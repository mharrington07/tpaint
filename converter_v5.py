"""
Terraria Texture Converter v5
Uses a curated, smaller palette for cleaner results.
Picks ONE representative block per color range.
"""

import sys
import os
from PIL import Image
import numpy as np
from pathlib import Path


TEXTURE_DIR = Path(__file__).parent / "textures"
TILE_SIZE = 16


# Curated palette with PRIORITY LEVELS
# Format: (tile_id, name, rgb, priority)
# Priority: Higher = more likely to be used when colors are similar
#   10 = FULL BLOCKS (wood, stone, brick) - ALWAYS prefer these
#    8 = Standard building blocks
#    6 = Earth/natural blocks  
#    4 = Specialty blocks (ores, gems)
#    2 = Rare/exotic blocks
#   10 = LIGHT SOURCES (fire) - high priority for bright colors
CURATED_PALETTE = [
    # === WOODS (browns) - HIGHEST PRIORITY ===
    (30,  "Wood",           (127, 92, 67),   10),   # Standard wood - PREFER THIS
    (321, "Boreal Wood",    (91, 72, 60),    10),   # Darker grayish brown
    (157, "Ebonwood",       (98, 88, 101),   10),   # Purple-tinted dark wood
    (158, "Rich Mahogany",  (114, 68, 66),   10),   # Reddish brown
    (311, "Palm Wood",      (88, 53, 28),    10),   # Very dark brown
    (208, "Shadewood",      (81, 85, 87),    10),   # Gray-purple wood
    
    # === STONE/BRICK (grays) - HIGH PRIORITY ===
    (1,   "Stone",          (103, 97, 92),   10),   # Standard gray
    (38,  "Gray Brick",     (101, 95, 91),    9),   # Similar gray
    (25,  "Ebonstone",      (60, 50, 70),    10),   # Dark purple stone
    (170, "Crimstone",      (80, 35, 40),     8),   # Red-brown stone
    
    # === DIRT/EARTH - MEDIUM-HIGH ===
    (0,   "Dirt",           (132, 95, 70),    8),   # Orange-brown
    (59,  "Mud",            (86, 68, 72),     7),   # Dark muddy brown
    
    # === BRICKS (colored) - HIGH PRIORITY ===
    (39,  "Red Brick",      (126, 77, 68),    9),   # Red brick
    (41,  "Blue Brick",     (50, 75, 150),    9),   # Blue dungeon brick
    (43,  "Green Brick",    (78, 87, 74),     9),   # Green brick
    (44,  "Pink Brick",     (170, 90, 140),   9),   # Pink brick
    (45,  "Gold Brick",     (108, 87, 36),    8),   # Gold-colored brick
    (47,  "Copper Brick",   (145, 80, 38),    8),   # Copper brick
    
    # === METALS/ORES - LOWER PRIORITY (specialty) ===
    (7,   "Copper Ore",     (138, 80, 48),    3),   # Orange copper
    (9,   "Silver Ore",     (180, 180, 185),  4),   # Bright silver
    (8,   "Gold Ore",       (180, 155, 45),   4),   # Yellow gold
    (6,   "Iron Ore",       (110, 100, 110),  3),   # Gray-brown iron
    (22,  "Demonite Ore",   (90, 70, 120),    3),   # Purple ore
    (203, "Crimtane Ore",   (106, 39, 35),    3),   # Blood red ore
    
    # === ICE/SNOW - HIGH for white/blue ===
    (147, "Snow Block",     (240, 245, 250), 10),   # White snow
    (161, "Ice Block",      (150, 200, 255),  9),   # Light blue ice
    
    # === SAND/DESERT ===
    (53,  "Sand",           (210, 190, 130),  8),   # Yellow sand
    
    # === GEMS - LOW PRIORITY (rare look) ===
    (63,  "Sapphire",       (50, 100, 200),   2),   # Blue gem
    (64,  "Ruby",           (200, 50, 80),    2),   # Red gem
    (65,  "Emerald",        (50, 180, 70),    2),   # Green gem
    (66,  "Topaz",          (200, 180, 50),   2),   # Yellow gem
    (67,  "Amethyst",       (150, 80, 200),   2),   # Purple gem
    (68,  "Diamond",        (220, 240, 255),  2),   # White/clear gem
    
    # === GEMSPARK (vibrant solid colors) - MEDIUM ===
    (255, "Amethyst Gemspark", (180, 70, 220),  6),   # Bright purple
    (256, "Topaz Gemspark",    (255, 180, 50),  6),   # Bright orange
    (257, "Sapphire Gemspark", (50, 120, 255),  6),   # Bright blue
    (258, "Emerald Gemspark",  (50, 255, 100),  6),   # Bright green
    (259, "Ruby Gemspark",     (255, 50, 80),   6),   # Bright red
    (260, "Diamond Gemspark",  (255, 255, 255), 6),   # Pure white
    (261, "Amber Gemspark",    (255, 200, 50),  6),   # Bright yellow
    
    # === FIRE/LIGHT (for torches) - HIGHEST for bright yellow/orange ===
    (343, "Living Demon Fire", (255, 210, 60), 10),   # Yellow flame - TORCHES!
    (336, "Living Fire",       (255, 140, 50), 10),   # Orange flame
    (340, "Living Cursed Fire",(100, 255, 50), 10),   # Green flame
    (342, "Ultrabright Fire",  (100, 250, 255),10),   # Cyan flame
    
    # === DARK BLOCKS ===
    (56,  "Obsidian",       (35, 30, 50),     8),   # Very dark purple
    (57,  "Hellstone",      (90, 30, 30),     6),   # Dark red
    
    # === NATURE ===
    (193, "Hive",           (180, 130, 40),   5),   # Yellow-orange hive
    (229, "Honey Block",    (255, 180, 50),   7),   # Golden honey
    
    # === MISC ===
    (51,  "Cobweb",         (220, 220, 220),  5),   # White webbing
    (127, "Glass",          (200, 220, 240),  4),   # Transparent blue-ish
]


# WALL PALETTE - walls are darker, used for shadows/background
# Format: (wall_id, name, rgb, priority)
# Walls match similar colors but darker - placed when pixel is in "shadow"
WALL_PALETTE = [
    # === WOOD WALLS (dark browns) ===
    (4,   "Wood Wall",          (63, 46, 34),   10),   # Standard wood wall
    (27,  "Boreal Wood Wall",   (48, 39, 33),   10),   # Dark grayish
    (78,  "Palm Wood Wall",     (52, 32, 22),   10),   # Very dark brown
    (41,  "Ebonwood Wall",      (45, 42, 55),   10),   # Purple-dark
    (74,  "Shadewood Wall",     (50, 48, 55),   10),   # Gray-purple
    (149, "Rich Mahogany Wall", (55, 35, 30),   10),   # Dark reddish
    
    # === STONE/BRICK WALLS ===
    (1,   "Stone Wall",         (45, 45, 45),   10),   # Dark gray
    (5,   "Gray Brick Wall",    (49, 49, 49),    9),   # Similar dark gray
    (16,  "Dirt Wall",          (87, 63, 50),    8),   # Brown dirt
    (3,   "Ebonstone Wall",     (35, 30, 45),   10),   # Very dark purple
    (83,  "Crimstone Wall",     (50, 25, 28),    8),   # Dark red
    
    # === DUNGEON WALLS ===
    (7,   "Blue Brick Wall",    (30, 45, 90),    9),   # Dark blue
    (17,  "Obsidian Wall",      (28, 25, 35),    8),   # Very dark
    
    # === NATURE WALLS ===
    (63,  "Jungle Wall",        (25, 66, 38),    7),   # Dark green
    (15,  "Mud Wall",           (45, 38, 40),    7),   # Dark mud
    
    # === ICE/SNOW WALLS ===
    (40,  "Snow Wall",          (100, 105, 115), 9),   # Grayish white
    (73,  "Ice Wall",           (70, 95, 120),   8),   # Dark ice blue
    
    # === MISC WALLS ===
    (21,  "Pearlstone Wall",    (51, 85, 101),   6),   # Grayish blue
    (45,  "Disc Wall",          (40, 40, 45),    5),   # Dark metallic
]


def extract_tile_frame(path: Path, tile_id: int) -> Image.Image:
    """
    Extract the SOLID CENTER portion of a tile that tiles seamlessly.
    We sample a small area from the center of a middle tile frame
    and tile it to create a uniform look.
    """
    try:
        img = Image.open(path).convert('RGBA')
        w, h = img.size
        
        # Terraria tiles are in 18x18 grid (16x16 + 2px border)
        # Frame positions: edge pieces around outside, solid center pieces inside
        # Best solid frame is usually around (54, 36) or (72, 54)
        
        if w >= 90 and h >= 72:
            # Get a deep center frame - this is usually a solid fill tile
            # Position (4,3) in the 18px grid = (72, 54)
            frame_x = 72 + 1  # Skip 1px border
            frame_y = 54 + 1
            tile_img = img.crop((frame_x, frame_y, frame_x + 16, frame_y + 16))
        elif w >= 72 and h >= 54:
            # Frame at (3,2) = (54, 36)
            frame_x = 54 + 1
            frame_y = 36 + 1
            tile_img = img.crop((frame_x, frame_y, frame_x + 16, frame_y + 16))
        elif w >= 54 and h >= 36:
            # Frame at (2,1) = (36, 18)
            frame_x = 36 + 1
            frame_y = 18 + 1
            tile_img = img.crop((frame_x, frame_y, frame_x + 16, frame_y + 16))
        elif w >= 36 and h >= 36:
            tile_img = img.crop((19, 19, 35, 35))
        elif w >= 18 and h >= 18:
            tile_img = img.crop((1, 1, 17, 17))
        elif w == 16 and h == 16:
            tile_img = img
        else:
            tile_img = img.crop((0, 0, min(16, w), min(16, h)))
            if tile_img.size != (16, 16):
                tile_img = tile_img.resize((16, 16), Image.NEAREST)
        
        return tile_img
    except Exception as e:
        print(f"Error loading tile {tile_id}: {e}")
        return None


def extract_wall_frame(path: Path, wall_id: int) -> Image.Image:
    """
    Extract a SOLID CENTER portion of a wall that tiles seamlessly.
    Wall textures are 36x36 grid (32x32 + 4px padding).
    """
    try:
        img = Image.open(path).convert('RGBA')
        w, h = img.size
        
        # Walls are in 36x36 grid - we want a deep center frame
        # that doesn't have edge/corner markings
        if w >= 180 and h >= 108:
            # Deep center: position (4,2) = (144, 72)
            wall_img = img.crop((144 + 2, 72 + 2, 144 + 2 + 32, 72 + 2 + 32))
        elif w >= 144 and h >= 72:
            # Center: position (3,1) = (108, 36)
            wall_img = img.crop((108 + 2, 36 + 2, 108 + 2 + 32, 36 + 2 + 32))
        elif w >= 108 and h >= 72:
            wall_img = img.crop((72 + 2, 36 + 2, 72 + 2 + 32, 36 + 2 + 32))
        elif w >= 72 and h >= 36:
            wall_img = img.crop((36 + 2, 2, 36 + 2 + 32, 34))
        elif w >= 36 and h >= 36:
            wall_img = img.crop((2, 2, 34, 34))
        else:
            wall_img = img.crop((0, 0, min(32, w), min(32, h)))
        
        # Scale to 16x16 to match tile size
        wall_img = wall_img.resize((16, 16), Image.NEAREST)
        return wall_img
    except Exception as e:
        print(f"Error loading wall {wall_id}: {e}")
        return None


class TerrariaConverterV5:
    """Converter with curated palette for clean results. Supports blocks AND walls."""
    
    def __init__(self, texture_dir: Path = TEXTURE_DIR):
        self.texture_dir = texture_dir
        self.tiles = []
        self.walls = []
        self._load_tiles()
        self._load_walls()
        
    def _load_tiles(self):
        """Load curated tiles with priority levels."""
        print(f"Loading {len(CURATED_PALETTE)} curated tiles...")
        
        loaded = 0
        for tile_id, name, rgb, priority in CURATED_PALETTE:
            path = self.texture_dir / f"Tiles_{tile_id}.png"
            if path.exists():
                texture = extract_tile_frame(path, tile_id)
                if texture:
                    # Also create a solid color version for uniform look
                    solid = Image.new('RGBA', (16, 16), (*rgb, 255))
                    self.tiles.append({
                        'id': tile_id,
                        'name': name,
                        'color': rgb,
                        'priority': priority,
                        'texture': texture,
                        'solid': solid
                    })
                    loaded += 1
        
        print(f"Loaded {loaded} tiles")
        
        # Build arrays for fast matching
        self.tile_colors = np.array([t['color'] for t in self.tiles], dtype=np.float32)
        self.tile_colors_lab = self._rgb_to_lab(self.tile_colors)
        self.tile_priorities = np.array([t['priority'] for t in self.tiles], dtype=np.float32)
    
    def _load_walls(self):
        """Load wall textures."""
        print(f"Loading {len(WALL_PALETTE)} wall textures...")
        
        loaded = 0
        for wall_id, name, rgb, priority in WALL_PALETTE:
            path = self.texture_dir / f"Wall_{wall_id}.png"
            if path.exists():
                texture = extract_wall_frame(path, wall_id)
                if texture:
                    # Also create solid color version
                    solid = Image.new('RGBA', (16, 16), (*rgb, 255))
                    self.walls.append({
                        'id': wall_id,
                        'name': name,
                        'color': rgb,
                        'priority': priority,
                        'texture': texture,
                        'solid': solid
                    })
                    loaded += 1
        
        print(f"Loaded {loaded} walls")
        
        # Build arrays for fast wall matching
        self.wall_colors = np.array([w['color'] for w in self.walls], dtype=np.float32)
        self.wall_colors_lab = self._rgb_to_lab(self.wall_colors)
        self.wall_priorities = np.array([w['priority'] for w in self.walls], dtype=np.float32)
    
    def _rgb_to_lab(self, rgb: np.ndarray) -> np.ndarray:
        """Convert RGB to LAB."""
        if len(rgb.shape) == 1:
            rgb = rgb.reshape(1, -1)
            
        rgb_norm = rgb.astype(np.float32) / 255.0
        
        mask = rgb_norm > 0.04045
        rgb_linear = np.where(mask, ((rgb_norm + 0.055) / 1.055) ** 2.4, rgb_norm / 12.92)
        
        matrix = np.array([
            [0.4124564, 0.3575761, 0.1804375],
            [0.2126729, 0.7151522, 0.0721750],
            [0.0193339, 0.1191920, 0.9503041]
        ])
        
        xyz = rgb_linear @ matrix.T
        xyz[:, 0] /= 0.95047
        xyz[:, 1] /= 1.00000
        xyz[:, 2] /= 1.08883
        
        epsilon = 0.008856
        kappa = 903.3
        
        mask = xyz > epsilon
        f = np.where(mask, xyz ** (1/3), (kappa * xyz + 16) / 116)
        
        lab = np.zeros_like(xyz)
        lab[:, 0] = 116 * f[:, 1] - 16
        lab[:, 1] = 500 * (f[:, 0] - f[:, 1])
        lab[:, 2] = 200 * (f[:, 1] - f[:, 2])
        
        return lab
    
    def convert(
        self,
        input_path: str,
        output_path: str = None,
        tile_size: int = 8,
        brightness_threshold: int = 15,
        wall_threshold: int = 45,  # Below this brightness = use walls (shadows only)
        smooth: bool = True  # Use solid colors for uniform merged look
    ) -> dict:
        """
        Convert image to Terraria with blocks AND walls.
        
        Brightness detection:
        - Very dark (< brightness_threshold): skip (true background)
        - Dark shadows (< wall_threshold): use WALLS (interior shadows)
        - Normal/Bright (>= wall_threshold): use BLOCKS (main structure)
        
        Args:
            smooth: If True, use solid colors for a uniform "merged" look.
                    If False, use actual Terraria textures.
        """
        print(f"\nConverting: {input_path}")
        print(f"Mode: {'SMOOTH (solid colors)' if smooth else 'TEXTURED'}")
        image = Image.open(input_path)
        
        # Handle alpha
        has_alpha = image.mode == 'RGBA'
        if has_alpha:
            img_array = np.array(image)
            rgb = img_array[:, :, :3].astype(np.float32)
            alpha = img_array[:, :, 3]
        else:
            rgb = np.array(image.convert('RGB')).astype(np.float32)
            alpha = None
        
        height, width = rgb.shape[:2]
        rows = height // tile_size
        cols = width // tile_size
        print(f"Grid: {cols}x{rows} tiles ({rows * cols:,} total)")
        
        # Downsample
        rgb = rgb[:rows * tile_size, :cols * tile_size]
        rgb = rgb.reshape(rows, tile_size, cols, tile_size, 3).mean(axis=(1, 3))
        
        if alpha is not None:
            alpha = alpha[:rows * tile_size, :cols * tile_size]
            alpha = alpha.reshape(rows, tile_size, cols, tile_size).mean(axis=(1, 3))
        
        # Calculate brightness for each cell
        brightness = rgb.mean(axis=2)
        
        # Match BLOCKS (for bright areas)
        pixels = rgb.reshape(-1, 3)
        pixels_lab = self._rgb_to_lab(pixels)
        
        diff = pixels_lab[:, np.newaxis, :] - self.tile_colors_lab[np.newaxis, :, :]
        distances = np.sqrt(np.sum(diff ** 2, axis=2))
        priority_bonus = self.tile_priorities * 1.5
        adjusted_distances = distances - priority_bonus[np.newaxis, :]
        closest_tile_idx = np.argmin(adjusted_distances, axis=1).reshape(rows, cols)
        
        # Match WALLS (for dark/shadow areas)
        wall_diff = pixels_lab[:, np.newaxis, :] - self.wall_colors_lab[np.newaxis, :, :]
        wall_distances = np.sqrt(np.sum(wall_diff ** 2, axis=2))
        wall_priority_bonus = self.wall_priorities * 1.5
        wall_adjusted_distances = wall_distances - wall_priority_bonus[np.newaxis, :]
        closest_wall_idx = np.argmin(wall_adjusted_distances, axis=1).reshape(rows, cols)
        
        # Render
        mode_str = "smooth solid colors" if smooth else "textures"
        print(f"Rendering with {mode_str} (blocks + walls)...")
        output = Image.new("RGBA", (cols * TILE_SIZE, rows * TILE_SIZE), (0, 0, 0, 0))
        
        block_usage = {}
        wall_usage = {}
        
        for row in range(rows):
            for col in range(cols):
                # Skip transparent
                if alpha is not None and alpha[row, col] < 128:
                    continue
                
                pixel_brightness = brightness[row, col]
                
                # Skip very dark (true background)
                if pixel_brightness < brightness_threshold:
                    continue
                
                # Decide: wall or block based on brightness
                if pixel_brightness < wall_threshold:
                    # DARK = use wall
                    wall = self.walls[closest_wall_idx[row, col]]
                    tex = wall['solid'] if smooth else wall['texture']
                    output.paste(tex, (col * TILE_SIZE, row * TILE_SIZE), tex)
                    name = wall['name']
                    wall_usage[name] = wall_usage.get(name, 0) + 1
                else:
                    # BRIGHT = use block
                    tile = self.tiles[closest_tile_idx[row, col]]
                    tex = tile['solid'] if smooth else tile['texture']
                    output.paste(tex, (col * TILE_SIZE, row * TILE_SIZE), tex)
                    name = tile['name']
                    block_usage[name] = block_usage.get(name, 0) + 1
        
        if output_path:
            final = Image.new("RGB", output.size, (0, 0, 0))
            final.paste(output, mask=output.split()[3])
            final.save(output_path, quality=95)
            print(f"Saved: {output_path}")
        
        return {'blocks': block_usage, 'walls': wall_usage}
    
    def print_shopping_list(self, usage: dict):
        """Print shopping list for blocks and walls."""
        block_usage = usage.get('blocks', {})
        wall_usage = usage.get('walls', {})
        
        print("\n" + "=" * 60)
        print("TERRARIA SHOPPING LIST")
        print("=" * 60)
        
        if block_usage:
            print("\n--- BLOCKS ---")
            block_total = 0
            for name, count in sorted(block_usage.items(), key=lambda x: -x[1]):
                print(f"  {name:25}: {count:>6,}")
                block_total += count
            print(f"  {'SUBTOTAL':25}: {block_total:>6,} ({len(block_usage)} types)")
        
        if wall_usage:
            print("\n--- WALLS ---")
            wall_total = 0
            for name, count in sorted(wall_usage.items(), key=lambda x: -x[1]):
                print(f"  {name:25}: {count:>6,}")
                wall_total += count
            print(f"  {'SUBTOTAL':25}: {wall_total:>6,} ({len(wall_usage)} types)")
        
        grand_total = sum(block_usage.values()) + sum(wall_usage.values())
        unique_total = len(block_usage) + len(wall_usage)
        
        print(f"\n{'=' * 60}")
        print(f"GRAND TOTAL: {grand_total:,} tiles | {unique_total} unique types")
        print("=" * 60)


def main():
    if len(sys.argv) < 2:
        print("Terraria Texture Converter v5 (Curated Palette)")
        print("=" * 50)
        print("\nUsage: python converter_v5.py <input> [output] [tile_size] [smooth]")
        print("\nArguments:")
        print("  input     - Input image path")
        print("  output    - Output path (default: terraria_curated.png)")
        print("  tile_size - Input pixels per tile (default: 8)")
        print("  smooth    - 1=solid colors (uniform), 0=textures (default: 1)")
        print("\nExample:")
        print("  python converter_v5.py myimage.png output.png 8 1")
        sys.exit(0)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "terraria_curated.png"
    tile_size = int(sys.argv[3]) if len(sys.argv) > 3 else 8
    smooth = bool(int(sys.argv[4])) if len(sys.argv) > 4 else True  # Default to smooth
    
    converter = TerrariaConverterV5()
    usage = converter.convert(input_path, output_path, tile_size=tile_size, smooth=smooth)
    converter.print_shopping_list(usage)


if __name__ == "__main__":
    main()
