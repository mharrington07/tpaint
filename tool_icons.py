"""
Generate pixel-art tool icons for TPaint.
Terraria-inspired style with simple 24x24 icons.
"""

from PIL import Image, ImageDraw
from pathlib import Path


ICON_SIZE = 24
ICONS_DIR = Path(__file__).parent / "icons"


def create_icons():
    """Generate all tool icons."""
    ICONS_DIR.mkdir(exist_ok=True)
    
    icons = {
        'brush': create_brush_icon,
        'fill': create_fill_icon,
        'line': create_line_icon,
        'circle': create_circle_icon,
        'select': create_select_icon,
        'eraser': create_eraser_icon,
        'wall': create_wall_icon,
        'block': create_block_icon,
        'brush_1': lambda: create_brush_size_icon(1),
        'brush_2': lambda: create_brush_size_icon(2),
        'brush_3': lambda: create_brush_size_icon(3),
        'brush_5': lambda: create_brush_size_icon(5),
        'brush_10': lambda: create_brush_size_icon(10),
    }
    
    for name, func in icons.items():
        img = func()
        img.save(ICONS_DIR / f"{name}.png")
        print(f"Created {name}.png")
    
    print(f"Icons saved to {ICONS_DIR}")


def create_brush_icon():
    """Paintbrush icon."""
    img = Image.new('RGBA', (ICON_SIZE, ICON_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Handle (brown)
    draw.rectangle([16, 2, 22, 6], fill=(139, 90, 43))
    draw.rectangle([12, 6, 18, 10], fill=(139, 90, 43))
    
    # Bristles (gray/silver ferrule)
    draw.rectangle([8, 10, 14, 13], fill=(150, 150, 160))
    
    # Brush tip (blue paint)
    draw.polygon([(2, 22), (6, 14), (12, 14), (16, 22)], fill=(100, 149, 237))
    draw.polygon([(4, 20), (7, 14), (11, 14), (14, 20)], fill=(122, 166, 247))
    
    return img


def create_fill_icon():
    """Paint bucket fill icon."""
    img = Image.new('RGBA', (ICON_SIZE, ICON_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Bucket body (gray metal)
    draw.polygon([(4, 8), (8, 4), (20, 4), (20, 16), (8, 20), (4, 16)], fill=(120, 120, 130))
    draw.polygon([(6, 9), (9, 6), (18, 6), (18, 14), (9, 17), (6, 14)], fill=(160, 160, 170))
    
    # Paint pouring (blue)
    draw.polygon([(16, 8), (22, 14), (22, 22), (18, 22), (14, 16)], fill=(100, 149, 237))
    draw.polygon([(18, 10), (21, 14), (21, 20), (19, 20), (16, 15)], fill=(122, 166, 247))
    
    # Handle
    draw.arc([6, 0, 18, 10], 180, 0, fill=(80, 80, 90), width=2)
    
    return img


def create_line_icon():
    """Line tool icon with diagonal line."""
    img = Image.new('RGBA', (ICON_SIZE, ICON_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Diagonal line
    draw.line([(3, 21), (21, 3)], fill=(100, 149, 237), width=3)
    
    # Endpoints (darker)
    draw.ellipse([1, 19, 5, 23], fill=(70, 100, 200))
    draw.ellipse([19, 1, 23, 5], fill=(70, 100, 200))
    
    return img


def create_circle_icon():
    """Circle/ellipse tool icon."""
    img = Image.new('RGBA', (ICON_SIZE, ICON_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Circle outline
    draw.ellipse([2, 2, 22, 22], outline=(100, 149, 237), width=3)
    
    # Highlight
    draw.arc([4, 4, 12, 12], 200, 340, fill=(160, 190, 255), width=2)
    
    return img


def create_select_icon():
    """Selection/marquee tool icon."""
    img = Image.new('RGBA', (ICON_SIZE, ICON_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Dashed rectangle (marching ants style)
    dash_color = (255, 255, 255)
    gap_color = (100, 100, 100)
    
    # Top edge
    for x in range(3, 21, 4):
        draw.line([(x, 3), (x+2, 3)], fill=dash_color, width=2)
    # Bottom edge
    for x in range(3, 21, 4):
        draw.line([(x, 21), (x+2, 21)], fill=dash_color, width=2)
    # Left edge
    for y in range(3, 21, 4):
        draw.line([(3, y), (3, y+2)], fill=dash_color, width=2)
    # Right edge
    for y in range(3, 21, 4):
        draw.line([(21, y), (21, y+2)], fill=dash_color, width=2)
    
    # Corner handles
    for pos in [(2, 2), (20, 2), (2, 20), (20, 20)]:
        draw.rectangle([pos[0]-1, pos[1]-1, pos[0]+2, pos[1]+2], fill=(100, 149, 237))
    
    return img


def create_eraser_icon():
    """Eraser icon."""
    img = Image.new('RGBA', (ICON_SIZE, ICON_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Eraser body (pink/red)
    draw.polygon([(4, 20), (10, 8), (20, 8), (20, 16), (14, 20)], fill=(220, 100, 100))
    draw.polygon([(6, 19), (11, 10), (18, 10), (18, 15), (13, 19)], fill=(240, 140, 140))
    
    # Metal band
    draw.rectangle([10, 8, 12, 14], fill=(150, 150, 160))
    
    # Pencil end hint
    draw.polygon([(18, 4), (22, 8), (20, 10), (16, 8)], fill=(200, 180, 140))
    
    return img


def create_wall_icon():
    """Wall/background layer icon."""
    img = Image.new('RGBA', (ICON_SIZE, ICON_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Brick pattern (stone wall style)
    stone_dark = (80, 80, 90)
    stone_light = (110, 110, 120)
    
    # Background
    draw.rectangle([2, 2, 22, 22], fill=stone_dark)
    
    # Brick rows
    draw.rectangle([3, 3, 10, 7], fill=stone_light)
    draw.rectangle([12, 3, 21, 7], fill=stone_light)
    draw.rectangle([3, 9, 7, 13], fill=stone_light)
    draw.rectangle([9, 9, 17, 13], fill=stone_light)
    draw.rectangle([19, 9, 21, 13], fill=stone_light)
    draw.rectangle([3, 15, 13, 19], fill=stone_light)
    draw.rectangle([15, 15, 21, 19], fill=stone_light)
    
    return img


def create_block_icon():
    """Block/tile icon."""
    img = Image.new('RGBA', (ICON_SIZE, ICON_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 3D block (dirt/stone style)
    # Top face (lighter)
    draw.polygon([(4, 8), (12, 4), (20, 8), (12, 12)], fill=(130, 100, 70))
    
    # Left face (medium)
    draw.polygon([(4, 8), (12, 12), (12, 20), (4, 16)], fill=(100, 75, 50))
    
    # Right face (darker)
    draw.polygon([(12, 12), (20, 8), (20, 16), (12, 20)], fill=(80, 60, 40))
    
    # Highlight on top
    draw.polygon([(6, 8), (12, 5), (14, 6), (8, 9)], fill=(150, 120, 90))
    
    return img


def create_brush_size_icon(size):
    """Create brush size indicator icon."""
    img = Image.new('RGBA', (ICON_SIZE, ICON_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Background grid
    draw.rectangle([2, 2, 22, 22], fill=(40, 40, 50))
    
    # Size indicator (filled square proportional to size)
    if size == 1:
        draw.rectangle([10, 10, 14, 14], fill=(100, 149, 237))
    elif size == 2:
        draw.rectangle([8, 8, 16, 16], fill=(100, 149, 237))
    elif size == 3:
        draw.rectangle([6, 6, 18, 18], fill=(100, 149, 237))
    elif size == 5:
        draw.rectangle([4, 4, 20, 20], fill=(100, 149, 237))
    else:  # 10
        draw.rectangle([2, 2, 22, 22], fill=(100, 149, 237))
    
    # Size number
    # Simple pixel numbers
    if size <= 5:
        draw_number(draw, size, 9, 8)
    else:
        draw_small_number(draw, size, 5, 9)
    
    return img


def draw_number(draw, num, x, y):
    """Draw a small pixel number."""
    white = (255, 255, 255)
    black = (0, 0, 0)
    
    # Outline
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx or dy:
                draw_digit(draw, num, x+dx, y+dy, black)
    draw_digit(draw, num, x, y, white)


def draw_small_number(draw, num, x, y):
    """Draw two-digit number."""
    white = (255, 255, 255)
    black = (0, 0, 0)
    
    tens = num // 10
    ones = num % 10
    
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx or dy:
                draw_digit(draw, tens, x+dx, y+dy, black)
                draw_digit(draw, ones, x+6+dx, y+dy, black)
    draw_digit(draw, tens, x, y, white)
    draw_digit(draw, ones, x+6, y, white)


def draw_digit(draw, digit, x, y, color):
    """Draw a single 5x7 pixel digit."""
    digits = {
        1: [(2,0), (1,1), (2,1), (2,2), (2,3), (2,4), (0,5), (1,5), (2,5), (3,5), (4,5)],
        2: [(0,0), (1,0), (2,0), (3,0), (4,1), (3,2), (2,3), (1,4), (0,5), (1,5), (2,5), (3,5), (4,5)],
        3: [(0,0), (1,0), (2,0), (3,0), (4,1), (2,2), (3,2), (4,3), (0,4), (1,4), (2,4), (3,4)],
        5: [(0,0), (1,0), (2,0), (3,0), (4,0), (0,1), (0,2), (1,2), (2,2), (3,2), (4,3), (4,4), (0,5), (1,5), (2,5), (3,5)],
        0: [(1,0), (2,0), (3,0), (0,1), (4,1), (0,2), (4,2), (0,3), (4,3), (0,4), (4,4), (1,5), (2,5), (3,5)],
    }
    
    pixels = digits.get(digit, [])
    for px, py in pixels:
        draw.point((x + px, y + py), fill=color)


if __name__ == "__main__":
    create_icons()
    print("Done!")
