"""
Terraria Texture Extractor
Extracts tile and wall textures from Terraria's XNB files.

XNB decompression based on LzxDecoder from MonoGame (MS-PL/LGPL 2.1)
Original TExtract by Antag99 (MIT License): https://github.com/Antag99/TExtract
"""

import struct
import os
import sys
import winreg
from pathlib import Path
from PIL import Image
import io


def find_terraria_path():
    """Auto-detect Terraria installation directory."""
    # Common Steam paths
    steam_paths = [
        Path(os.environ.get("ProgramFiles(x86)", "C:/Program Files (x86)")) / "Steam",
        Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "Steam",
        Path("D:/SteamLibrary"),
        Path("E:/SteamLibrary"),
    ]
    
    # Try to get Steam path from registry
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam") as key:
            steam_path = Path(winreg.QueryValueEx(key, "SteamPath")[0])
            steam_paths.insert(0, steam_path)
    except:
        pass
    
    # Check each Steam path
    for steam in steam_paths:
        terraria = steam / "steamapps/common/Terraria"
        if terraria.exists():
            return terraria
        
        # Check library folders config
        libraryfolders = steam / "steamapps/libraryfolders.vdf"
        if libraryfolders.exists():
            try:
                content = libraryfolders.read_text()
                # Parse paths from libraryfolders.vdf
                import re
                for match in re.finditer(r'"path"\s+"([^"]+)"', content):
                    lib_path = Path(match.group(1).replace("\\\\", "/"))
                    terraria = lib_path / "steamapps/common/Terraria"
                    if terraria.exists():
                        return terraria
            except:
                pass
    
    # GOG install
    gog_path = Path(os.environ.get("ProgramFiles(x86)", "")) / "GOG Galaxy/Games/Terraria"
    if gog_path.exists():
        return gog_path
    
    return None


def read_7bit_int(data, offset):
    """Read .NET 7-bit encoded integer."""
    result = 0
    shift = 0
    while True:
        byte = data[offset]
        offset += 1
        result |= (byte & 0x7F) << shift
        if (byte & 0x80) == 0:
            break
        shift += 7
    return result, offset


class LzxDecoder:
    """
    LZX decompression for XNB files.
    Based on MonoGame's LzxDecoder (MS-PL/LGPL 2.1 dual license).
    Original C# by Ali Lortie, ported to Python.
    """
    
    MIN_MATCH = 2
    MAX_MATCH = 257
    NUM_CHARS = 256
    
    BLOCKTYPE_INVALID = 0
    BLOCKTYPE_VERBATIM = 1
    BLOCKTYPE_ALIGNED = 2
    BLOCKTYPE_UNCOMPRESSED = 3
    
    PRETREE_NUM_ELEMENTS = 20
    ALIGNED_NUM_ELEMENTS = 8
    NUM_PRIMARY_LENGTHS = 7
    NUM_SECONDARY_LENGTHS = 249
    
    PRETREE_MAXSYMBOLS = 20
    PRETREE_TABLEBITS = 6
    MAINTREE_MAXSYMBOLS = 656
    MAINTREE_TABLEBITS = 12
    LENGTH_MAXSYMBOLS = 250
    LENGTH_TABLEBITS = 12
    ALIGNED_MAXSYMBOLS = 8
    ALIGNED_TABLEBITS = 7
    LENTABLE_SAFETY = 64
    
    extra_bits = [0,0,0,0,1,1,2,2,3,3,4,4,5,5,6,6,7,7,8,8,9,9,10,10,11,11,12,12,13,13,14,14,15,15,16,16,17,17,17,17,17,17,17,17,17,17,17,17,17,17,17]
    position_base = [0,1,2,3,4,6,8,12,16,24,32,48,64,96,128,192,256,384,512,768,1024,1536,2048,3072,4096,6144,8192,12288,16384,24576,32768,49152,65536,98304,131072,196608,262144,393216,524288,655360,786432,917504,1048576,1179648,1310720,1441792,1572864,1703936,1835008,1966080,2097152]
    
    def __init__(self, window_bits):
        self.window_size = 1 << window_bits
        self.window = bytearray(self.window_size)
        self.window_posn = 0
        
        self.R0 = 1
        self.R1 = 1
        self.R2 = 1
        
        self.main_elements = self.NUM_CHARS + (window_bits << 3)
        
        self.header_read = False
        self.block_remaining = 0
        self.block_type = self.BLOCKTYPE_INVALID
        
        self.intel_filesize = 0
        self.intel_curpos = 0
        self.intel_started = False
        
        self.PRETREE_table = [0] * ((1 << self.PRETREE_TABLEBITS) + (self.PRETREE_MAXSYMBOLS << 1))
        self.PRETREE_len = [0] * (self.PRETREE_MAXSYMBOLS + self.LENTABLE_SAFETY)
        self.MAINTREE_table = [0] * ((1 << self.MAINTREE_TABLEBITS) + (self.MAINTREE_MAXSYMBOLS << 1))
        self.MAINTREE_len = [0] * (self.MAINTREE_MAXSYMBOLS + self.LENTABLE_SAFETY)
        self.LENGTH_table = [0] * ((1 << self.LENGTH_TABLEBITS) + (self.LENGTH_MAXSYMBOLS << 1))
        self.LENGTH_len = [0] * (self.LENGTH_MAXSYMBOLS + self.LENTABLE_SAFETY)
        self.ALIGNED_table = [0] * ((1 << self.ALIGNED_TABLEBITS) + (self.ALIGNED_MAXSYMBOLS << 1))
        self.ALIGNED_len = [0] * (self.ALIGNED_MAXSYMBOLS + self.LENTABLE_SAFETY)
        
        for i in range(self.MAINTREE_MAXSYMBOLS):
            self.MAINTREE_len[i] = 0
        for i in range(self.LENGTH_MAXSYMBOLS):
            self.LENGTH_len[i] = 0
    
    def decompress(self, indata, inlen, outdata, outlen):
        """Decompress LZX data."""
        bit_buf = 0
        bits_left = 0
        inpos = 0
        outpos = 0
        
        def ensure_bits(n):
            nonlocal bit_buf, bits_left, inpos
            while bits_left < n:
                if inpos + 1 < inlen:
                    b0, b1 = indata[inpos], indata[inpos + 1]
                    inpos += 2
                    bit_buf |= ((b1 << 8) | b0) << (16 - bits_left)
                    bits_left += 16
                else:
                    return False
            return True
        
        def peek_bits(n):
            return (bit_buf >> (32 - n)) & ((1 << n) - 1)
        
        def remove_bits(n):
            nonlocal bit_buf, bits_left
            bit_buf <<= n
            bit_buf &= 0xFFFFFFFF
            bits_left -= n
        
        def read_bits(n):
            nonlocal bit_buf, bits_left
            ensure_bits(n)
            val = peek_bits(n)
            remove_bits(n)
            return val
        
        # Read header if needed
        if not self.header_read:
            ensure_bits(1)
            if peek_bits(1) == 1:
                remove_bits(1)
                ensure_bits(16)
                i = peek_bits(16)
                remove_bits(16)
                ensure_bits(16)
                j = peek_bits(16)
                remove_bits(16)
                self.intel_filesize = (i << 16) | j
            else:
                remove_bits(1)
                self.intel_filesize = 0
            self.header_read = True
        
        togo = outlen
        while togo > 0:
            if self.block_remaining == 0:
                # Read block header
                ensure_bits(3)
                self.block_type = peek_bits(3)
                remove_bits(3)
                
                ensure_bits(16)
                i = peek_bits(16)
                remove_bits(16)
                ensure_bits(8)
                j = peek_bits(8)
                remove_bits(8)
                
                self.block_remaining = (i << 8) | j
                
                if self.block_type == self.BLOCKTYPE_ALIGNED:
                    for i in range(8):
                        ensure_bits(3)
                        self.ALIGNED_len[i] = peek_bits(3)
                        remove_bits(3)
                    self._make_decode_table(self.ALIGNED_MAXSYMBOLS, self.ALIGNED_TABLEBITS, 
                                           self.ALIGNED_len, self.ALIGNED_table)
                    # Fall through to verbatim
                
                if self.block_type in (self.BLOCKTYPE_VERBATIM, self.BLOCKTYPE_ALIGNED):
                    self._read_lengths(self.MAINTREE_len, 0, 256, 
                                      lambda n: read_bits(n), lambda n: peek_bits(n), lambda n: remove_bits(n), ensure_bits)
                    self._read_lengths(self.MAINTREE_len, 256, self.main_elements, 
                                      lambda n: read_bits(n), lambda n: peek_bits(n), lambda n: remove_bits(n), ensure_bits)
                    self._make_decode_table(self.MAINTREE_MAXSYMBOLS, self.MAINTREE_TABLEBITS,
                                           self.MAINTREE_len, self.MAINTREE_table)
                    
                    self._read_lengths(self.LENGTH_len, 0, self.NUM_SECONDARY_LENGTHS, 
                                      lambda n: read_bits(n), lambda n: peek_bits(n), lambda n: remove_bits(n), ensure_bits)
                    self._make_decode_table(self.LENGTH_MAXSYMBOLS, self.LENGTH_TABLEBITS,
                                           self.LENGTH_len, self.LENGTH_table)
                
                elif self.block_type == self.BLOCKTYPE_UNCOMPRESSED:
                    self.intel_started = True
                    if bits_left == 0:
                        ensure_bits(16)
                    bits_left = 0
                    bit_buf = 0
                    
                    if inpos + 12 > inlen:
                        return -1
                    
                    self.R0 = struct.unpack_from('<I', indata, inpos)[0]
                    inpos += 4
                    self.R1 = struct.unpack_from('<I', indata, inpos)[0]
                    inpos += 4
                    self.R2 = struct.unpack_from('<I', indata, inpos)[0]
                    inpos += 4
            
            this_run = min(self.block_remaining, togo)
            togo -= this_run
            self.block_remaining -= this_run
            window_posn = self.window_posn
            
            if self.block_type == self.BLOCKTYPE_UNCOMPRESSED:
                if inpos + this_run > inlen:
                    return -1
                self.window[window_posn:window_posn + this_run] = indata[inpos:inpos + this_run]
                inpos += this_run
                window_posn += this_run
            else:
                while this_run > 0:
                    ensure_bits(self.MAINTREE_TABLEBITS)
                    main_element = self.MAINTREE_table[peek_bits(self.MAINTREE_TABLEBITS)]
                    if main_element >= self.MAINTREE_MAXSYMBOLS:
                        remove_bits(self.MAINTREE_TABLEBITS)
                        repeat = 15
                        while main_element >= self.MAINTREE_MAXSYMBOLS:
                            ensure_bits(1)
                            main_element = self.MAINTREE_table[(main_element << 1) | peek_bits(1)]
                            remove_bits(1)
                            repeat -= 1
                            if repeat == 0:
                                break
                    else:
                        remove_bits(self.MAINTREE_len[main_element])
                    
                    if main_element < self.NUM_CHARS:
                        self.window[window_posn] = main_element
                        window_posn += 1
                        this_run -= 1
                    else:
                        main_element -= self.NUM_CHARS
                        match_length = main_element & self.NUM_PRIMARY_LENGTHS
                        
                        if match_length == self.NUM_PRIMARY_LENGTHS:
                            ensure_bits(self.LENGTH_TABLEBITS)
                            length_footer = self.LENGTH_table[peek_bits(self.LENGTH_TABLEBITS)]
                            if length_footer >= self.LENGTH_MAXSYMBOLS:
                                remove_bits(self.LENGTH_TABLEBITS)
                                repeat = 15
                                while length_footer >= self.LENGTH_MAXSYMBOLS:
                                    ensure_bits(1)
                                    length_footer = self.LENGTH_table[(length_footer << 1) | peek_bits(1)]
                                    remove_bits(1)
                                    repeat -= 1
                                    if repeat == 0:
                                        break
                            else:
                                remove_bits(self.LENGTH_len[length_footer])
                            match_length += length_footer
                        
                        match_length += self.MIN_MATCH
                        
                        match_offset = main_element >> 3
                        
                        if match_offset > 2:
                            if self.block_type == self.BLOCKTYPE_ALIGNED and self.extra_bits[match_offset] >= 3:
                                extra = self.extra_bits[match_offset] - 3
                                ensure_bits(extra)
                                verbatim_bits = peek_bits(extra) << 3
                                remove_bits(extra)
                                
                                ensure_bits(self.ALIGNED_TABLEBITS)
                                aligned_bits = self.ALIGNED_table[peek_bits(self.ALIGNED_TABLEBITS)]
                                if aligned_bits >= self.ALIGNED_MAXSYMBOLS:
                                    remove_bits(self.ALIGNED_TABLEBITS)
                                    repeat = 15
                                    while aligned_bits >= self.ALIGNED_MAXSYMBOLS:
                                        ensure_bits(1)
                                        aligned_bits = self.ALIGNED_table[(aligned_bits << 1) | peek_bits(1)]
                                        remove_bits(1)
                                        repeat -= 1
                                        if repeat == 0:
                                            break
                                else:
                                    remove_bits(self.ALIGNED_len[aligned_bits])
                                match_offset = self.position_base[match_offset] + verbatim_bits + aligned_bits - 2
                            elif self.extra_bits[match_offset] > 0:
                                extra = self.extra_bits[match_offset]
                                ensure_bits(extra)
                                verbatim_bits = peek_bits(extra)
                                remove_bits(extra)
                                match_offset = self.position_base[match_offset] + verbatim_bits - 2
                            else:
                                match_offset = 1
                            
                            self.R2 = self.R1
                            self.R1 = self.R0
                            self.R0 = match_offset
                        
                        elif match_offset == 0:
                            match_offset = self.R0
                        elif match_offset == 1:
                            match_offset = self.R1
                            self.R1 = self.R0
                            self.R0 = match_offset
                        else:  # match_offset == 2
                            match_offset = self.R2
                            self.R2 = self.R0
                            self.R0 = match_offset
                        
                        rundest = window_posn
                        runsrc = rundest - match_offset
                        
                        this_run -= match_length
                        
                        if runsrc < 0:
                            runsrc += self.window_size
                            copy_length = min(match_length, -runsrc)
                            for _ in range(copy_length):
                                self.window[rundest] = self.window[runsrc]
                                rundest += 1
                                runsrc += 1
                            match_length -= copy_length
                            runsrc -= self.window_size
                        
                        while match_length > 0:
                            self.window[rundest] = self.window[runsrc]
                            rundest += 1
                            runsrc += 1
                            match_length -= 1
                        
                        window_posn = rundest
            
            self.window_posn = window_posn
        
        outdata[:outlen] = self.window[0:outlen]
        return 0
    
    def _read_lengths(self, lens, first, last, read_bits, peek_bits, remove_bits, ensure_bits):
        """Read code lengths from bitstream."""
        ensure_bits(self.PRETREE_TABLEBITS)
        
        # Read pretree
        for i in range(self.PRETREE_NUM_ELEMENTS):
            ensure_bits(4)
            self.PRETREE_len[i] = peek_bits(4)
            remove_bits(4)
        
        self._make_decode_table(self.PRETREE_MAXSYMBOLS, self.PRETREE_TABLEBITS,
                               self.PRETREE_len, self.PRETREE_table)
        
        i = first
        while i < last:
            ensure_bits(self.PRETREE_TABLEBITS)
            z = self.PRETREE_table[peek_bits(self.PRETREE_TABLEBITS)]
            if z >= self.PRETREE_MAXSYMBOLS:
                remove_bits(self.PRETREE_TABLEBITS)
                repeat = 15
                while z >= self.PRETREE_MAXSYMBOLS:
                    ensure_bits(1)
                    z = self.PRETREE_table[(z << 1) | peek_bits(1)]
                    remove_bits(1)
                    repeat -= 1
                    if repeat == 0:
                        break
            else:
                remove_bits(self.PRETREE_len[z])
            
            if z == 17:
                ensure_bits(4)
                y = peek_bits(4)
                remove_bits(4)
                y += 4
                while y > 0 and i < last:
                    lens[i] = 0
                    i += 1
                    y -= 1
            elif z == 18:
                ensure_bits(5)
                y = peek_bits(5)
                remove_bits(5)
                y += 20
                while y > 0 and i < last:
                    lens[i] = 0
                    i += 1
                    y -= 1
            elif z == 19:
                ensure_bits(1)
                y = peek_bits(1)
                remove_bits(1)
                y += 4
                
                ensure_bits(self.PRETREE_TABLEBITS)
                z = self.PRETREE_table[peek_bits(self.PRETREE_TABLEBITS)]
                if z >= self.PRETREE_MAXSYMBOLS:
                    remove_bits(self.PRETREE_TABLEBITS)
                    repeat = 15
                    while z >= self.PRETREE_MAXSYMBOLS:
                        ensure_bits(1)
                        z = self.PRETREE_table[(z << 1) | peek_bits(1)]
                        remove_bits(1)
                        repeat -= 1
                        if repeat == 0:
                            break
                else:
                    remove_bits(self.PRETREE_len[z])
                
                z = (lens[i] - z + 17) % 17
                while y > 0 and i < last:
                    lens[i] = z
                    i += 1
                    y -= 1
            else:
                lens[i] = (lens[i] - z + 17) % 17
                i += 1
    
    def _make_decode_table(self, nsyms, nbits, length, table):
        """Build a decode table from code lengths."""
        pos = 0
        table_mask = 1 << nbits
        bit_mask = table_mask >> 1
        
        for bit_num in range(1, nbits + 1):
            for sym in range(nsyms):
                if length[sym] == bit_num:
                    leaf = pos
                    pos += bit_mask
                    if pos > table_mask:
                        return 1
                    fill = bit_mask
                    while fill > 0:
                        table[leaf] = sym
                        leaf += 1
                        fill -= 1
            bit_mask >>= 1
        
        if pos != table_mask:
            for sym in range(pos, table_mask):
                table[sym] = 0
            
            next_symbol = table_mask >> 1
            pos <<= 16
            table_mask <<= 16
            bit_mask = 1 << 15
            
            for bit_num in range(nbits + 1, 17):
                for sym in range(nsyms):
                    if length[sym] == bit_num:
                        leaf = pos >> 16
                        for i in range(bit_num - nbits):
                            if table[leaf] == 0:
                                table[next_symbol << 1] = 0
                                table[(next_symbol << 1) + 1] = 0
                                table[leaf] = next_symbol
                                next_symbol += 1
                            leaf = (table[leaf] << 1) + ((pos >> (15 - i)) & 1)
                        table[leaf] = sym
                        pos += bit_mask
                        if pos > table_mask:
                            return 1
                bit_mask >>= 1
        
        return 0


def extract_xnb(xnb_path, output_path=None):
    """
    Extract a texture from a Terraria XNB file.
    Returns PIL Image or None on failure.
    """
    with open(xnb_path, 'rb') as f:
        data = f.read()
    
    if data[:3] != b'XNB':
        return None
    
    version = data[4]
    flags = data[5]
    file_size = struct.unpack('<I', data[6:10])[0]
    compressed = (flags & 0x80) != 0
    
    offset = 10
    
    if compressed:
        decompressed_size = struct.unpack('<I', data[10:14])[0]
        offset = 14
        
        # Decompress using LZX
        decoder = LzxDecoder(16)  # Window bits for Terraria
        decompressed = bytearray(decompressed_size)
        
        remaining = decompressed_size
        outpos = 0
        
        while remaining > 0:
            # Read block header
            hi = data[offset]
            offset += 1
            lo = data[offset]
            offset += 1
            
            block_size = (hi << 8) | lo
            frame_size = 0x8000
            
            if hi == 0xFF:
                hi = lo
                lo = data[offset]
                offset += 1
                frame_size = (hi << 8) | lo
                hi = data[offset]
                offset += 1
                lo = data[offset]
                offset += 1
                block_size = (hi << 8) | lo
            
            if block_size == 0 or frame_size == 0:
                break
            
            block_data = data[offset:offset + block_size]
            offset += block_size
            
            temp = bytearray(frame_size)
            ret = decoder.decompress(block_data, block_size, temp, frame_size)
            if ret != 0:
                return None
            
            copy_size = min(frame_size, remaining)
            decompressed[outpos:outpos + copy_size] = temp[:copy_size]
            outpos += copy_size
            remaining -= copy_size
        
        data = bytes(decompressed)
        offset = 0
    
    # Read type readers count
    type_count, offset = read_7bit_int(data, offset)
    
    # Skip type reader definitions
    for _ in range(type_count):
        name_len, offset = read_7bit_int(data, offset)
        offset += name_len + 4  # Skip string + version
    
    # Skip shared resources
    shared_count, offset = read_7bit_int(data, offset)
    
    # Read primary asset type
    type_id, offset = read_7bit_int(data, offset)
    if type_id == 0:
        return None
    
    # Read Texture2D
    surface_format = struct.unpack('<I', data[offset:offset+4])[0]
    offset += 4
    width = struct.unpack('<I', data[offset:offset+4])[0]
    offset += 4
    height = struct.unpack('<I', data[offset:offset+4])[0]
    offset += 4
    mip_count = struct.unpack('<I', data[offset:offset+4])[0]
    offset += 4
    data_size = struct.unpack('<I', data[offset:offset+4])[0]
    offset += 4
    
    pixel_data = data[offset:offset + data_size]
    
    if surface_format == 0 and len(pixel_data) >= width * height * 4:
        img = Image.frombytes('RGBA', (width, height), pixel_data[:width*height*4])
        if output_path:
            img.save(output_path)
        return img
    
    return None


def extract_tiles_and_walls(terraria_path, output_dir, progress_callback=None):
    """
    Extract all Tiles_*.xnb and Wall_*.xnb from Terraria.
    
    Args:
        terraria_path: Path to Terraria installation
        output_dir: Where to save the PNGs
        progress_callback: Optional function(current, total, filename)
    
    Returns:
        (extracted_count, failed_count)
    """
    content_dir = Path(terraria_path) / "Content" / "Images"
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Find all tile and wall XNB files
    patterns = ["Tiles_*.xnb", "Wall_*.xnb"]
    xnb_files = []
    for pattern in patterns:
        xnb_files.extend(content_dir.glob(pattern))
    
    extracted = 0
    failed = 0
    total = len(xnb_files)
    
    for i, xnb_file in enumerate(xnb_files):
        output_file = output_dir / f"{xnb_file.stem}.png"
        
        if progress_callback:
            progress_callback(i + 1, total, xnb_file.name)
        
        try:
            img = extract_xnb(str(xnb_file), str(output_file))
            if img:
                extracted += 1
            else:
                failed += 1
        except Exception as e:
            failed += 1
    
    return extracted, failed


def setup_textures(output_dir=None):
    """
    Main entry point - auto-detect Terraria and extract textures.
    Called on first run or when textures are missing.
    """
    if output_dir is None:
        output_dir = Path(__file__).parent / "textures"
    
    output_dir = Path(output_dir)
    
    # Check if textures already exist
    existing_tiles = list(output_dir.glob("Tiles_*.png"))
    existing_walls = list(output_dir.glob("Wall_*.png"))
    
    if len(existing_tiles) > 700 and len(existing_walls) > 300:
        print(f"Textures already present: {len(existing_tiles)} tiles, {len(existing_walls)} walls")
        return True
    
    # Find Terraria
    print("Searching for Terraria installation...")
    terraria_path = find_terraria_path()
    
    if not terraria_path:
        print("\nCould not find Terraria installation!")
        print("Please enter the path to your Terraria folder:")
        print("(e.g., C:\\Program Files (x86)\\Steam\\steamapps\\common\\Terraria)")
        user_path = input("> ").strip().strip('"')
        
        if not user_path or not Path(user_path).exists():
            print("Invalid path. Please install Terraria from Steam or GOG first.")
            return False
        
        terraria_path = Path(user_path)
    
    content_path = terraria_path / "Content" / "Images"
    if not content_path.exists():
        print(f"Content folder not found at: {content_path}")
        return False
    
    print(f"Found Terraria at: {terraria_path}")
    print(f"Extracting textures to: {output_dir}")
    print()
    
    def progress(current, total, filename):
        bar_width = 40
        filled = int(bar_width * current / total)
        bar = '=' * filled + '-' * (bar_width - filled)
        print(f"\r[{bar}] {current}/{total} - {filename}", end='', flush=True)
    
    extracted, failed = extract_tiles_and_walls(terraria_path, output_dir, progress)
    
    print()
    print(f"\nExtraction complete!")
    print(f"  Extracted: {extracted}")
    print(f"  Failed: {failed}")
    
    return extracted > 0


if __name__ == "__main__":
    print("=" * 60)
    print("Terraria Texture Extractor")
    print("Based on TExtract by Antag99 (MIT License)")
    print("https://github.com/Antag99/TExtract")
    print("=" * 60)
    print()
    
    if len(sys.argv) > 1:
        # Command line mode
        output = sys.argv[2] if len(sys.argv) > 2 else "textures"
        img = extract_xnb(sys.argv[1])
        if img:
            print(f"Extracted: {sys.argv[1]}")
        else:
            print(f"Failed: {sys.argv[1]}")
    else:
        setup_textures()
