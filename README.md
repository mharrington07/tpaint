# TPaint - Terraria Builder

A visual building tool for designing Terraria structures using actual game textures.

## Features

- **Block & Wall Layering** - Place blocks on top of walls (torches on walls, furniture in front of backgrounds)
- **Furniture Support** - Tables, chairs, chests, and other multi-tile objects
- **Auto-tiling** - Blocks automatically connect with the correct sprites
- **Fast Search** - Filter blocks, furniture, and walls by name or ID
- **Zoom & Pan** - Scroll to zoom, middle-click to pan
- **Export** - Save designs as PNG images
- **Auto-Extract** - Automatically extracts textures from your Terraria installation on first run

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

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the app:
   ```bash
   python paint_app_main.py
   ```

3. On first run, the app will automatically find your Terraria installation and extract the needed textures.

## Textures

The app automatically extracts textures from Terraria on first run. It looks for:
- Steam installation (Windows)
- GOG installation

If auto-detection fails, you'll be prompted to enter your Terraria path manually.

You can also manually run the extractor:
```bash
python texture_extractor.py
```

## Requirements

- Python 3.8+
- Pillow
- NumPy
- tkinter (included with Python)
- **Terraria** (Steam or GOG installation)

## Credits

- **Texture Extraction** based on [TExtract](https://github.com/Antag99/TExtract) by Antag99 (MIT License)
- LZX decompression based on MonoGame's LzxDecoder (MS-PL/LGPL 2.1)
- Terraria is property of Re-Logic
