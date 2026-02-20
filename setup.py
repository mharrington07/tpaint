"""
First-Run Setup for TPaint
Downloads and runs TExtract to extract Terraria textures.

TExtract by Antag99 (MIT License): https://github.com/Antag99/TExtract
"""

import os
import sys
import subprocess
import urllib.request
import shutil
import winreg
from pathlib import Path


TEXTRACT_URL = "http://bit.ly/2ieZZcs"  # Dropbox-hosted JAR via bit.ly
TEXTRACT_DIR = Path(__file__).parent / "tools"
TEXTRACT_JAR = TEXTRACT_DIR / "TExtract.jar"
TEXTURE_DIR = Path(__file__).parent / "textures"


def find_java():
    """Find Java executable."""
    # Check if java is in PATH
    java_cmd = shutil.which("java")
    if java_cmd:
        return java_cmd
    
    # Check common Windows paths
    java_paths = [
        Path(os.environ.get("JAVA_HOME", "")) / "bin" / "java.exe",
        Path(os.environ.get("ProgramFiles", "")) / "Java",
        Path(os.environ.get("ProgramFiles(x86)", "")) / "Java",
        Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Eclipse Adoptium",
    ]
    
    for base in java_paths:
        if base.exists():
            # Search for java.exe
            for java_exe in base.rglob("java.exe"):
                return str(java_exe)
    
    # Try registry
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\JavaSoft\Java Runtime Environment") as key:
            version = winreg.QueryValueEx(key, "CurrentVersion")[0]
            with winreg.OpenKey(key, version) as subkey:
                java_home = winreg.QueryValueEx(subkey, "JavaHome")[0]
                java_exe = Path(java_home) / "bin" / "java.exe"
                if java_exe.exists():
                    return str(java_exe)
    except:
        pass
    
    return None


def find_terraria():
    """Find Terraria installation."""
    steam_paths = [
        Path(os.environ.get("ProgramFiles(x86)", "C:/Program Files (x86)")) / "Steam",
        Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "Steam",
        Path("D:/SteamLibrary"),
        Path("E:/SteamLibrary"),
        Path("F:/SteamLibrary"),
    ]
    
    # Try registry for Steam path
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam") as key:
            steam_path = Path(winreg.QueryValueEx(key, "SteamPath")[0])
            steam_paths.insert(0, steam_path)
    except:
        pass
    
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
    
    # GOG
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
        print("\n[!] Java Runtime not found!")
        print("TExtract requires Java to extract Terraria's textures.")
        print()
        print("Please install Java from one of these sources:")
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
    import threading
    
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
        messagebox.showerror("TPaint Setup", 
            "Java Runtime not found!\n\n"
            "TExtract requires Java to extract Terraria's textures.\n\n"
            "Please install Java from:\n"
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
    
    # Result container
    result = {"success": False, "moved": 0, "error": ""}
    
    def update_progress(current, total, message):
        """Update progress bar from extraction callback."""
        def _update():
            if total > 0:
                pct = int(100 * current / total)
                progress_bar['value'] = pct
                percent_label.config(text=f"{pct}%")
            status_label.config(text=message)
            progress_win.update()
        progress_win.after(0, _update)
    
    def do_extraction():
        """Run extraction in background thread."""
        try:
            # Download TExtract
            progress_win.after(0, lambda: status_label.config(text="Downloading TExtract..."))
            if not download_textract():
                result["error"] = "Failed to download TExtract"
                return
            
            # Run TExtract
            temp_output = TEXTRACT_DIR / "extracted"
            success, message = run_textract(terraria, temp_output, progress_callback=update_progress)
            
            if not success:
                result["error"] = f"Extraction failed: {message}"
                return
            
            # Move tiles and walls
            progress_win.after(0, lambda: status_label.config(text="Organizing textures..."))
            moved = move_tiles_and_walls(temp_output, TEXTURE_DIR)
            
            # Cleanup
            try:
                shutil.rmtree(temp_output)
            except:
                pass
            
            result["success"] = True
            result["moved"] = moved
            
        except Exception as e:
            result["error"] = str(e)
    
    # Run extraction in thread
    thread = threading.Thread(target=do_extraction)
    thread.start()
    
    # Wait for thread while keeping GUI responsive
    while thread.is_alive():
        progress_win.update()
        progress_win.after(50)
    
    progress_win.destroy()
    
    if result["error"]:
        messagebox.showerror("TPaint Setup", result["error"])
        root.destroy()
        return False
    
    messagebox.showinfo("TPaint Setup", 
        f"Setup complete!\n\nExtracted {result['moved']} texture files.")
    
    root.destroy()
    return result["moved"] > 0


if __name__ == "__main__":
    # Console mode
    success = setup_textures()
    try:
        if not success:
            input("\nPress Enter to exit...")
    except:
        pass  # No stdin in windowed mode
    sys.exit(0 if success else 1)
