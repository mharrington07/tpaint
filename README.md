# TPaint - Terraria Builder

A visual building tool for designing Terraria structures using actual game textures.

## Features

- **Block & Wall Layering** - Place blocks on top of walls (torches on walls, furniture in front of backgrounds)
- **Furniture Support** - Tables, chairs, chests, and other multi-tile objects
- **Auto-tiling** - Blocks automatically connect with the correct sprites
- **Fast Search** - Filter blocks, furniture, and walls by name or ID
- **Zoom & Pan** - Scroll to zoom, middle-click to pan
- **Export** - Save designs as PNG images

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

2. Add Terraria textures to the `textures/` folder (Tiles_*.png and Wall_*.png files)

3. Run the app:
   ```bash
   python paint_app_main.py
   ```

## Textures

Extract textures from Terraria's Content folder. The app expects:
- `textures/Tiles_0.png`, `Tiles_1.png`, etc.
- `textures/Wall_0.png`, `Wall_1.png`, etc.

## Requirements

- Python 3.8+
- Pillow
- NumPy
- tkinter (included with Python)
