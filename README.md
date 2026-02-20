# TPaint - Terraria Builder

A visual building tool for designing Terraria structures using actual game textures.

**No Terraria required!** - Texture pack available for download if you don't own the game.

## Features

- **Block & Wall Layering** - Place blocks on top of walls (torches on walls, furniture in front of backgrounds)
- **Furniture Support** - Tables, chairs, chests, and other multi-tile objects
- **Auto-tiling** - Blocks automatically connect with the correct sprites
- **Drawing Tools** - Line, Circle, Rectangle, Fill, Selection with move
- **Undo/Redo** - Full history support (Ctrl+Z/Y)
- **Project Files** - Save and load .tpaint projects
- **Eyedropper** - Pick tiles directly from canvas
- **Fast Search** - Filter blocks, furniture, and walls by name or ID
- **Zoom & Pan** - Scroll to zoom, middle-click to pan
- **Export** - Save as PNG image, TPaint project, or TEdit schematic (.TEditSch)
- **Auto-Setup** - Downloads textures automatically

## Controls

| Key | Action |
|-----|--------|
| B | Block tool |
| W | Wall tool |
| E | Erase all |
| F | Fill tool |
| L | Line tool |
| O | Circle tool |
| R | Rectangle tool |
| M | Selection tool |
| I | Eyedropper (pick tile) |
| 1-5 | Brush sizes |
| C | Clear canvas |
| S | Export (PNG/TPaint/TEdit) |
| Ctrl+Z | Undo |
| Ctrl+Y | Redo |
| Ctrl+S | Save project |
| Ctrl+O | Open project |
| Ctrl+N | New canvas |
| Ctrl+C/V | Copy/Paste selection |
| Scroll | Zoom |
| Middle-click | Pan |
| Right-click | Erase |

## Installation

---

### 🪟 Windows

#### Using the Executable (Recommended)
1. Download `TPaint.exe` from the [Releases](https://github.com/mharrington07/tpaint/releases) page
2. Run `TPaint.exe`
3. On first run, the app will:
   - Find your Terraria installation, **or** download texture pack if not installed
   - Auto-download Java JRE if needed (only for Terraria extraction)
   - Extract textures automatically

#### From Source
1. **Prerequisites:** Python 3.8+ from [python.org](https://www.python.org/downloads/)
2. Clone and install:
   ```powershell
   git clone https://github.com/mharrington07/tpaint.git
   cd tpaint
   pip install -r requirements.txt
   python paint_app_main.py
   ```

> **Note:** Java is auto-downloaded if not found - no manual installation required!

#### Troubleshooting (Windows)
- If textures aren't found, run `python setup.py` manually
- For GOG installations, the app checks `C:\Program Files (x86)\GOG Galaxy\Games\Terraria`

---

### 🐧 Linux

#### Using the Executable (Recommended)
1. Download `TPaint` from the [Releases](https://github.com/mharrington07/tpaint/releases) page
2. Make it executable: `chmod +x TPaint`
3. Run: `./TPaint`
4. On first run:
   - Finds your Terraria installation, **or** downloads texture pack if not installed
   - Auto-downloads Java JRE if needed (only for Terraria extraction)

#### From Source
Prerequisites: Python 3.8+ with tkinter, Terraria (Steam)

> **Note:** Java is auto-downloaded if not found - no manual installation required!

#### Steps

1. **Install system dependencies:**
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install python3 python3-pip python3-tk
   
   # Fedora
   sudo dnf install python3 python3-pip python3-tkinter
   
   # Arch
   sudo pacman -S python python-pip tk
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
| Java Runtime | Auto-downloaded | Auto-downloaded |
| Terraria | Steam or GOG | Steam (native or Proton) |

## Credits

- **[TExtract](https://github.com/Antag99/TExtract)** by Antag99 (MIT License) - Texture extraction
- Terraria is property of Re-Logic
