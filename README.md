# TPaint - Terraria Builder

A visual building tool for designing Terraria structures using actual game textures.

## Features

- **Block & Wall Layering** - Place blocks on top of walls (torches on walls, furniture in front of backgrounds)
- **Furniture Support** - Tables, chairs, chests, and other multi-tile objects
- **Auto-tiling** - Blocks automatically connect with the correct sprites
- **Fast Search** - Filter blocks, furniture, and walls by name or ID
- **Zoom & Pan** - Scroll to zoom, middle-click to pan
- **Export** - Save designs as PNG images
- **Auto-Setup** - Downloads TExtract and extracts textures from your Terraria installation

## Controls

| Key | Action |
|-----|--------|
| B | Block tool |
| W | Wall tool |
| E | Erase all |
| X | Erase block only |
| Z | Erase wall only |
| 1-5 | Brush sizes |
| C | Clear canvas |
| S | Save image |
| Scroll | Zoom |
| Middle-click | Pan |
| Right-click | Erase |

## Installation

---

### 🪟 Windows

#### Prerequisites
- **Python 3.8+** - Download from [python.org](https://www.python.org/downloads/)
- **Java Runtime** - Download from [Adoptium](https://adoptium.net/) (required for texture extraction)
- **Terraria** - Steam or GOG installation

#### Steps

1. **Clone or download the repository:**
   ```powershell
   git clone https://github.com/mharrington07/tpaint.git
   cd tpaint
   ```

2. **Install Python dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

3. **Run the app:**
   ```powershell
   python paint_app_main.py
   ```

4. **First run setup:**
   - The app will automatically download TExtract
   - It will find your Terraria installation (Steam/GOG)
   - Textures will be extracted to the `textures/` folder

#### Troubleshooting (Windows)
- If textures aren't found, run `python setup.py` manually
- Make sure Java is installed and in your PATH
- For GOG installations, the app checks `C:\Program Files (x86)\GOG Galaxy\Games\Terraria`

---

### 🐧 Linux

#### Prerequisites
- **Python 3.8+** with tkinter
- **Java Runtime** (OpenJDK)
- **Terraria** - Steam (native or Proton)

#### Steps

1. **Install system dependencies:**
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install python3 python3-pip python3-tk default-jre
   
   # Fedora
   sudo dnf install python3 python3-pip python3-tkinter java-latest-openjdk
   
   # Arch
   sudo pacman -S python python-pip tk jre-openjdk
   ```

2. **Clone the repository:**
   ```bash
   git clone https://github.com/mharrington07/tpaint.git
   cd tpaint
   ```

3. **Install Python packages:**
   ```bash
   pip3 install -r requirements.txt
   ```

4. **Run the app:**
   ```bash
   python3 paint_app_main.py
   ```

5. **Texture setup:**
   The app searches for Terraria in these locations:
   - `~/.steam/steam/steamapps/common/Terraria`
   - `~/.local/share/Steam/steamapps/common/Terraria`
   - Flatpak: `~/.var/app/com.valvesoftware.Steam/.steam/steam/steamapps/common/Terraria`

#### Troubleshooting (Linux)
- If auto-detection fails: `python3 setup.py`
- Or manually copy `Content/Images/Tiles_*.png` and `Wall_*.png` to `textures/`
- TExtract uses Java - ensure `java --version` works in terminal

---

## Requirements

| Dependency | Windows | Linux |
|------------|---------|-------|
| Python | 3.8+ from [python.org](https://www.python.org/downloads/) | `python3` via package manager |
| Pillow & NumPy | `pip install -r requirements.txt` | `pip3 install -r requirements.txt` |
| Java Runtime | [Adoptium](https://adoptium.net/) | `default-jre` / `jre-openjdk` |
| Terraria | Steam or GOG | Steam (native or Proton) |

## Credits

- **[TExtract](https://github.com/Antag99/TExtract)** by Antag99 (MIT License) - Texture extraction
- Terraria is property of Re-Logic
