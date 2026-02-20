"""
Extract icons from the user's spritesheet.
Better background removal and centered output.
"""

from PIL import Image
import numpy as np
from pathlib import Path

ICONS_DIR = Path(__file__).parent / "icons"
OUTPUT_SIZE = 32  # Final icon size


def remove_background(img):
    """Remove background by detecting the most common corner color."""
    data = np.array(img)
    
    # Sample corners to detect background color
    h, w = data.shape[:2]
    corners = [
        data[0, 0],           # top-left
        data[0, w-1],         # top-right
        data[h-1, 0],         # bottom-left
        data[h-1, w-1],       # bottom-right
    ]
    
    # Find most common corner color (likely background)
    from collections import Counter
    corner_tuples = [tuple(c) for c in corners]
    bg_color = Counter(corner_tuples).most_common(1)[0][0]
    
    # Make pixels matching background transparent
    # Allow some tolerance for anti-aliasing
    tolerance = 30
    bg = np.array(bg_color)
    
    # Calculate distance from background color
    diff = np.abs(data[:,:,:3].astype(int) - bg[:3].astype(int))
    mask = np.all(diff < tolerance, axis=2)
    
    # Set matching pixels to transparent
    data[mask, 3] = 0
    
    return Image.fromarray(data)


def center_and_resize(icon, target_size=OUTPUT_SIZE):
    """Center the icon content and resize to target, maintaining aspect ratio."""
    # Trim transparent edges
    bbox = icon.getbbox()
    if not bbox:
        # Fully transparent, return empty
        return Image.new('RGBA', (target_size, target_size), (0, 0, 0, 0))
    
    trimmed = icon.crop(bbox)
    tw, th = trimmed.size
    
    # Calculate scale to fit within target while maintaining aspect ratio
    # Leave some padding (use 85% of target size)
    usable = int(target_size * 0.85)
    scale = min(usable / tw, usable / th)
    
    # Scale the image (use LANCZOS for smooth scaling, NEAREST for pixel art)
    new_w = max(1, int(tw * scale))
    new_h = max(1, int(th * scale))
    scaled = trimmed.resize((new_w, new_h), Image.NEAREST)
    
    # Create centered output
    output = Image.new('RGBA', (target_size, target_size), (0, 0, 0, 0))
    x = (target_size - new_w) // 2
    y = (target_size - new_h) // 2
    output.paste(scaled, (x, y), scaled)
    
    return output


def extract_icons(spritesheet_path):
    """Extract 9 icons from a 3x3 grid spritesheet."""
    ICONS_DIR.mkdir(exist_ok=True)
    
    img = Image.open(spritesheet_path).convert('RGBA')
    
    # Assuming 3x3 grid
    cols, rows = 3, 3
    icon_w = img.width // cols
    icon_h = img.height // rows
    
    print(f"Spritesheet: {img.width}x{img.height}")
    print(f"Each icon cell: {icon_w}x{icon_h}")
    print(f"Output size: {OUTPUT_SIZE}x{OUTPUT_SIZE}")
    
    # Map grid positions to icon names
    # Row 0: circle, select, brush
    # Row 1: line, eraser, fill
    # Row 2: paint_bucket, palette, zoom
    icon_names = [
        ['circle', 'select', 'brush'],
        ['line', 'eraser', 'fill'],
        ['paint_bucket', 'palette', 'zoom']
    ]
    
    for row in range(rows):
        for col in range(cols):
            x = col * icon_w
            y = row * icon_h
            
            # Extract cell
            icon = img.crop((x, y, x + icon_w, y + icon_h))
            
            # Remove background
            icon = remove_background(icon)
            
            # Center and resize
            icon = center_and_resize(icon, OUTPUT_SIZE)
            
            name = icon_names[row][col]
            icon.save(ICONS_DIR / f"{name}.png")
            print(f"Saved {name}.png")
    
    # Create aliases for tool names
    # brush -> block, eraser -> erase, paint_bucket -> wall
    aliases = [
        ('brush.png', 'block.png'),
        ('eraser.png', 'erase.png'),
        ('paint_bucket.png', 'wall.png'),
    ]
    
    for src, dst in aliases:
        src_path = ICONS_DIR / src
        if src_path.exists():
            img = Image.open(src_path)
            img.save(ICONS_DIR / dst)
            print(f"Created alias: {dst}")
    
    print(f"\nDone! Icons extracted to: {ICONS_DIR}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        extract_icons(sys.argv[1])
    else:
        print("Usage: python extract_icons.py <spritesheet.png>")
        print("Looking for spritesheet in current directory...")
        
        # Try common names
        for name in ["icons.png", "spritesheet.png", "tools.png"]:
            p = Path(name)
            if p.exists():
                extract_icons(p)
                break
        else:
            print("No spritesheet found. Please provide path as argument.")
