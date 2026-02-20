"""
First-Run Setup for TPaint
Downloads and runs TExtract to extract Terraria textures.
Auto-downloads Java JRE if not found.

TExtract by Antag99 (MIT License): https://github.com/Antag99/TExtract
Java: Eclipse Temurin (Adoptium) - https://adoptium.net/
"""

import os
import sys
import subprocess
import urllib.request
import shutil
import platform
import zipfile
import tarfile
from pathlib import Path

# Windows-only import
if platform.system() == 'Windows':
    import winreg
else:
    winreg = None


TEXTRACT_URL = "http://bit.ly/2ieZZcs"  # Dropbox-hosted JAR via bit.ly
TEXTRACT_DIR = Path(__file__).parent / "tools"
TEXTRACT_JAR = TEXTRACT_DIR / "TExtract.jar"

# Adoptium (Eclipse Temurin) JRE 21 - portable versions
# Using GitHub releases API for latest LTS
JAVA_VERSION = "21"
JAVA_DIR = TEXTRACT_DIR / "jre"

# Direct download URLs for Adoptium JRE 21 (LTS)
if platform.system() == 'Windows':
    JAVA_URL = f"https://api.adoptium.net/v3/binary/latest/{JAVA_VERSION}/ga/windows/x64/jre/hotspot/normal/eclipse?project=jdk"
    JAVA_ARCHIVE = TEXTRACT_DIR / "jre.zip"
else:
    JAVA_URL = f"https://api.adoptium.net/v3/binary/latest/{JAVA_VERSION}/ga/linux/x64/jre/hotspot/normal/eclipse?project=jdk"
    JAVA_ARCHIVE = TEXTRACT_DIR / "jre.tar.gz"
TEXTURE_DIR = Path(__file__).parent / "textures"


def find_portable_java():
    """Find Java in our portable JRE directory."""
    if not JAVA_DIR.exists():
        return None
    
    is_windows = platform.system() == 'Windows'
    java_exe_name = "java.exe" if is_windows else "java"
    
    # Search for java executable in the JRE directory
    for java_exe in JAVA_DIR.rglob(java_exe_name):
        if java_exe.is_file() and "bin" in str(java_exe):
            return str(java_exe)
    
    return None


def download_java(progress_callback=None):
    """Download portable Java JRE from Adoptium."""
    # Check if already downloaded
    portable_java = find_portable_java()
    if portable_java:
        return portable_java
    
    TEXTRACT_DIR.mkdir(parents=True, exist_ok=True)
    
    is_windows = platform.system() == 'Windows'
    
    print("Downloading Java JRE (Eclipse Temurin)...")
    print("(This is required for texture extraction)")
    print(f"Version: JRE {JAVA_VERSION}")
    
    try:
        req = urllib.request.Request(JAVA_URL, headers={'User-Agent': 'Mozilla/5.0'})
        
        with urllib.request.urlopen(req) as response:
            total_size = int(response.headers.get('Content-Length', 0))
            downloaded = 0
            
            with open(JAVA_ARCHIVE, 'wb') as f:
                while True:
                    chunk = response.read(8192)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    if progress_callback and total_size > 0:
                        pct = int(downloaded * 100 / total_size)
                        progress_callback(downloaded, total_size, f"Downloading Java: {pct}%")
        
        print("Download complete. Extracting...")
        
        # Extract the archive
        JAVA_DIR.mkdir(parents=True, exist_ok=True)
        
        if is_windows:
            with zipfile.ZipFile(JAVA_ARCHIVE, 'r') as zf:
                zf.extractall(JAVA_DIR)
        else:
            with tarfile.open(JAVA_ARCHIVE, 'r:gz') as tf:
                tf.extractall(JAVA_DIR)
        
        # Clean up archive
        JAVA_ARCHIVE.unlink()
        
        print("Java JRE installed successfully!")
        
        # Find the java executable
        return find_portable_java()
        
    except Exception as e:
        print(f"Failed to download Java: {e}")
        if JAVA_ARCHIVE.exists():
            JAVA_ARCHIVE.unlink()
        return None


def find_java():
    """Find Java executable."""
    # First check our portable JRE
    portable_java = find_portable_java()
    if portable_java:
        return portable_java
    
    # Check if java is in PATH
    java_cmd = shutil.which("java")
    if java_cmd:
        return java_cmd
    
    is_windows = platform.system() == 'Windows'
    java_exe_name = "java.exe" if is_windows else "java"
    
    if is_windows:
        # Check common Windows paths
        java_paths = [
            Path(os.environ.get("JAVA_HOME", "")) / "bin" / java_exe_name,
            Path(os.environ.get("ProgramFiles", "")) / "Java",
            Path(os.environ.get("ProgramFiles(x86)", "")) / "Java",
            Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Eclipse Adoptium",
        ]
        
        for base in java_paths:
            if base.exists():
                for java_exe in base.rglob(java_exe_name):
                    return str(java_exe)
        
        # Try registry
        try:
            if winreg:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\JavaSoft\Java Runtime Environment") as key:
                    version = winreg.QueryValueEx(key, "CurrentVersion")[0]
                    with winreg.OpenKey(key, version) as subkey:
                        java_home = winreg.QueryValueEx(subkey, "JavaHome")[0]
                        java_exe = Path(java_home) / "bin" / java_exe_name
                        if java_exe.exists():
                            return str(java_exe)
        except:
            pass
    else:
        # Linux/macOS paths
        java_paths = [
            Path(os.environ.get("JAVA_HOME", "")) / "bin" / "java",
            Path("/usr/bin/java"),
            Path("/usr/lib/jvm"),
            Path("/opt/java"),
            Path.home() / ".sdkman" / "candidates" / "java",
        ]
        
        for base in java_paths:
            if base.is_file():
                return str(base)
            if base.is_dir():
                for java_exe in base.rglob("java"):
                    if java_exe.is_file() and "bin" in str(java_exe):
                        return str(java_exe)
    
    return None


def find_terraria():
    """Find Terraria installation."""
    is_windows = platform.system() == 'Windows'
    
    if is_windows:
        steam_paths = [
            Path(os.environ.get("ProgramFiles(x86)", "C:/Program Files (x86)")) / "Steam",
            Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "Steam",
            Path("D:/SteamLibrary"),
            Path("E:/SteamLibrary"),
            Path("F:/SteamLibrary"),
        ]
        
        # Try registry for Steam path
        try:
            if winreg:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam") as key:
                    steam_path = Path(winreg.QueryValueEx(key, "SteamPath")[0])
                    steam_paths.insert(0, steam_path)
        except:
            pass
    else:
        # Linux/macOS Steam paths
        home = Path.home()
        steam_paths = [
            home / ".steam" / "steam",
            home / ".steam" / "debian-installation",
            home / ".local" / "share" / "Steam",
            Path("/opt/steam"),
            # Flatpak Steam
            home / ".var" / "app" / "com.valvesoftware.Steam" / ".steam" / "steam",
            # macOS
            home / "Library" / "Application Support" / "Steam",
        ]
    
    for steam in steam_paths:
        terraria = steam / "steamapps/common/Terraria"
        if terraria.exists():
            return terraria
        
        # Check library folders
        libraryfolders = steam / "steamapps/libraryfolders.vdf"
        if libraryfolders.exists():
            try:
                import re
                content = libraryfolders.read_text()
                for match in re.finditer(r'"path"\s+"([^"]+)"', content):
                    lib_path = Path(match.group(1).replace("\\\\", "/"))
                    terraria = lib_path / "steamapps/common/Terraria"
                    if terraria.exists():
                        return terraria
            except:
                pass
    
    # GOG (Windows only)
    if is_windows:
        gog_path = Path(os.environ.get("ProgramFiles(x86)", "")) / "GOG Galaxy/Games/Terraria"
        if gog_path.exists():
            return gog_path
    
    return None


def download_textract():
    """Download TExtract.jar if not present."""
    if TEXTRACT_JAR.exists():
        return True
    
    TEXTRACT_DIR.mkdir(parents=True, exist_ok=True)
    
    print("Downloading TExtract...")
    print("(TExtract by Antag99, MIT License)")
    print(f"URL: {TEXTRACT_URL}")
    
    try:
        # Use Request with User-Agent for bit.ly redirect
        req = urllib.request.Request(TEXTRACT_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            with open(TEXTRACT_JAR, 'wb') as f:
                f.write(response.read())
        print("Download complete!")
        return True
    except Exception as e:
        print(f"Download failed: {e}")
        return False


def run_textract(terraria_path, output_dir, progress_callback=None):
    """Run TExtract in command-line mode."""
    java = find_java()
    if not java:
        return False, "Java not found"
    
    content_dir = Path(terraria_path) / "Content" / "Images"
    if not content_dir.exists():
        return False, f"Content/Images folder not found: {content_dir}"
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Get all Tiles_*.xnb and Wall_*.xnb files
    tiles = list(content_dir.glob("Tiles_*.xnb"))
    walls = list(content_dir.glob("Wall_*.xnb"))
    all_files = tiles + walls
    
    if not all_files:
        return False, f"No Tiles_*.xnb or Wall_*.xnb files found in {content_dir}"
    
    total = len(all_files)
    extracted = 0
    
    if progress_callback:
        progress_callback(0, total, "Starting extraction...")
    
    # TExtract CLI: java -jar TExtract.jar --outputDirectory path [files...]
    # Process in batches to avoid command line length limits
    batch_size = 50
    
    for i in range(0, len(all_files), batch_size):
        batch = all_files[i:i + batch_size]
        
        cmd = [java, "-jar", str(TEXTRACT_JAR), "--outputDirectory", str(output_dir)]
        cmd.extend(str(f) for f in batch)
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            extracted += len(batch)
            
            if progress_callback:
                progress_callback(extracted, total, f"Extracted {extracted}/{total} textures...")
                
        except subprocess.TimeoutExpired:
            return False, f"Extraction timed out at file {extracted}"
        except Exception as e:
            return False, str(e)
    
    if progress_callback:
        progress_callback(total, total, "Extraction complete!")
    
    return True, f"Extracted {extracted} files"


def move_tiles_and_walls(extracted_dir, texture_dir):
    """Move only Tiles_*.png and Wall_*.png to the texture folder."""
    extracted_dir = Path(extracted_dir)
    texture_dir = Path(texture_dir)
    texture_dir.mkdir(parents=True, exist_ok=True)
    
    # TExtract outputs to: output_dir/Images/
    images_dir = extracted_dir / "Images"
    if not images_dir.exists():
        images_dir = extracted_dir  # Might be flat
    
    moved = 0
    for pattern in ["Tiles_*.png", "Wall_*.png"]:
        for f in images_dir.glob(pattern):
            dest = texture_dir / f.name
            shutil.copy2(f, dest)
            moved += 1
    
    return moved


def setup_textures():
    """Main setup function - call this on first run."""
    print("=" * 60)
    print("TPaint - First Run Setup")
    print("=" * 60)
    print()
    
    # Check if textures already exist
    existing_tiles = list(TEXTURE_DIR.glob("Tiles_*.png"))
    existing_walls = list(TEXTURE_DIR.glob("Wall_*.png"))
    
    if len(existing_tiles) > 700 and len(existing_walls) > 300:
        print(f"Textures already present: {len(existing_tiles)} tiles, {len(existing_walls)} walls")
        return True
    
    # Check for Java
    print("Checking for Java...")
    java = find_java()
    if not java:
        print("\n[!] Java Runtime not found. Downloading portable JRE...")
        java = download_java()
        if not java:
            print("\n[!] Failed to download Java automatically!")
            print("Please install Java manually from one of these sources:")
            print("  - https://adoptium.net/ (Recommended)")
            print("  - https://www.oracle.com/java/technologies/downloads/")
            print()
            print("After installing Java, run this setup again.")
            return False
    
    print(f"Found Java: {java}")
    print()
    
    # Find Terraria
    print("Searching for Terraria...")
    terraria = find_terraria()
    
    if not terraria:
        print("\nCould not find Terraria installation.")
        print("Please enter the path to your Terraria folder:")
        print("(e.g., C:\\Program Files (x86)\\Steam\\steamapps\\common\\Terraria)")
        user_path = input("> ").strip().strip('"')
        
        if not user_path or not Path(user_path).exists():
            print("Invalid path.")
            return False
        terraria = Path(user_path)
    
    print(f"Found Terraria: {terraria}")
    print()
    
    # Download TExtract
    if not download_textract():
        print("Failed to download TExtract.")
        return False
    print()
    
    # Run TExtract
    temp_output = TEXTRACT_DIR / "extracted"
    success, message = run_textract(terraria, temp_output)
    
    if not success:
        print(f"Extraction failed: {message}")
        return False
    
    print()
    
    # Move tiles and walls to textures folder
    print("Organizing textures...")
    moved = move_tiles_and_walls(temp_output, TEXTURE_DIR)
    print(f"Moved {moved} texture files to {TEXTURE_DIR}")
    
    # Cleanup temp files
    try:
        shutil.rmtree(temp_output)
    except:
        pass
    
    print()
    print("=" * 60)
    print("Setup complete! You can now run TPaint.")
    print("=" * 60)
    
    return True


def setup_textures_gui():
    """GUI-based setup for windowed mode."""
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog
    
    # Check if textures already exist
    existing_tiles = list(TEXTURE_DIR.glob("Tiles_*.png"))
    existing_walls = list(TEXTURE_DIR.glob("Wall_*.png"))
    
    if len(existing_tiles) > 700 and len(existing_walls) > 300:
        return True
    
    root = tk.Tk()
    root.withdraw()
    
    # Check for Java
    java = find_java()
    if not java:
        # Show downloading dialog
        download_win = tk.Toplevel(root)
        download_win.title("TPaint Setup")
        download_win.geometry("400x120")
        download_win.resizable(False, False)
        download_win.protocol("WM_DELETE_WINDOW", lambda: None)
        
        download_win.update_idletasks()
        x = (download_win.winfo_screenwidth() - 400) // 2
        y = (download_win.winfo_screenheight() - 120) // 2
        download_win.geometry(f"400x120+{x}+{y}")
        
        tk.Label(download_win, text="Downloading Java JRE...", font=("Arial", 12, "bold")).pack(pady=10)
        java_status = tk.Label(download_win, text="This may take a moment...")
        java_status.pack(pady=5)
        java_progress = ttk.Progressbar(download_win, length=350, mode='determinate')
        java_progress.pack(pady=10)
        
        def java_progress_callback(current, total, msg):
            if total > 0:
                java_progress['value'] = int(current * 100 / total)
            java_status.config(text=msg)
            download_win.update()
        
        download_win.update()
        java = download_java(java_progress_callback)
        download_win.destroy()
        
        if not java:
            messagebox.showerror("TPaint Setup", 
                "Failed to download Java automatically!\n\n"
                "Please install Java manually from:\n"
                "https://adoptium.net/\n\n"
                "Then restart TPaint.")
            root.destroy()
            return False
    
    # Find Terraria
    terraria = find_terraria()
    
    if not terraria:
        messagebox.showinfo("TPaint Setup", 
            "Could not auto-detect Terraria installation.\n\n"
            "Please select your Terraria folder in the next dialog.")
        
        terraria = filedialog.askdirectory(
            title="Select Terraria Installation Folder",
            initialdir="C:/Program Files (x86)/Steam/steamapps/common"
        )
        
        if not terraria or not Path(terraria).exists():
            messagebox.showerror("TPaint Setup", "No valid Terraria path selected.")
            root.destroy()
            return False
        terraria = Path(terraria)
    
    # Create progress window
    progress_win = tk.Toplevel(root)
    progress_win.title("TPaint Setup")
    progress_win.geometry("400x150")
    progress_win.resizable(False, False)
    progress_win.protocol("WM_DELETE_WINDOW", lambda: None)  # Disable close
    
    # Center the window
    progress_win.update_idletasks()
    x = (progress_win.winfo_screenwidth() - 400) // 2
    y = (progress_win.winfo_screenheight() - 150) // 2
    progress_win.geometry(f"400x150+{x}+{y}")
    
    tk.Label(progress_win, text="Extracting Terraria Textures...", font=("Arial", 12, "bold")).pack(pady=10)
    
    status_label = tk.Label(progress_win, text="Downloading TExtract...")
    status_label.pack(pady=5)
    
    progress_bar = ttk.Progressbar(progress_win, length=350, mode='determinate')
    progress_bar.pack(pady=10)
    
    percent_label = tk.Label(progress_win, text="0%")
    percent_label.pack()
    
    progress_win.deiconify()
    progress_win.update()
    
    def update_progress(current, total, message):
        """Update progress bar - called from main thread."""
        if total > 0:
            pct = int(100 * current / total)
            progress_bar['value'] = pct
            percent_label.config(text=f"{pct}%")
        status_label.config(text=message)
        progress_win.update()
    
    # Download TExtract
    update_progress(0, 100, "Downloading TExtract...")
    if not download_textract():
        progress_win.destroy()
        messagebox.showerror("TPaint Setup", "Failed to download TExtract.")
        root.destroy()
        return False
    
    # Run TExtract (synchronous with progress updates)
    temp_output = TEXTRACT_DIR / "extracted"
    success, message = run_textract(terraria, temp_output, progress_callback=update_progress)
    
    if not success:
        progress_win.destroy()
        messagebox.showerror("TPaint Setup", f"Extraction failed:\n{message}")
        root.destroy()
        return False
    
    # Move tiles and walls
    update_progress(100, 100, "Organizing textures...")
    moved = move_tiles_and_walls(temp_output, TEXTURE_DIR)
    
    # Cleanup
    try:
        shutil.rmtree(temp_output)
    except:
        pass
    
    progress_win.destroy()
    
    messagebox.showinfo("TPaint Setup", 
        f"Setup complete!\n\nExtracted {moved} texture files.")
    
    root.destroy()
    return moved > 0


if __name__ == "__main__":
    # Console mode
    success = setup_textures()
    try:
        if not success:
            input("\nPress Enter to exit...")
    except:
        pass  # No stdin in windowed mode
    sys.exit(0 if success else 1)
