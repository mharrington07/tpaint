"""
Analyze Terraria textures pixel-by-pixel to determine accurate color tags.
Run this once to generate tile_tags.json for the paint app.
"""

import json
from pathlib import Path
from PIL import Image
from collections import Counter
import re

TEXTURE_DIR = Path(__file__).parent / "textures"
OUTPUT_FILE = Path(__file__).parent / "tile_tags.json"

# Import names
try:
    from terraria_names import TILE_NAMES, WALL_NAMES
except ImportError:
    TILE_NAMES = {}
    WALL_NAMES = {}

# Furniture definitions
FURNITURE_NAMES = {
    4: "Torch", 33: "Candle", 49: "Water Candle", 372: "Peace Candle",
    14: "Table", 469: "Table", 15: "Chair", 79: "Bed", 18: "Workbench",
    77: "Hellforge", 133: "Adamantite Forge", 134: "Mythril Anvil",
    10: "Wooden Door", 11: "Open Door", 21: "Chest", 467: "Chest",
    29: "Piggy Bank", 97: "Bookcase", 105: "Statue", 101: "Bookcase",
    42: "Hanging Lantern", 91: "Banner", 87: "Grand Piano", 93: "Grandfather Clock",
    88: "Dresser", 89: "Bench", 102: "Throne", 172: "Sink", 380: "Toilet",
    92: "Lamp Post",
}

# Color definitions - HSV-based for better accuracy
COLOR_RANGES = {
    # Color name: (hue_min, hue_max, sat_min, sat_max, val_min, val_max)
    # Hue is 0-360, sat and val are 0-100
    'red': [(0, 15, 30, 100, 30, 100), (345, 360, 30, 100, 30, 100)],
    'orange': [(15, 45, 30, 100, 30, 100)],
    'yellow': [(45, 70, 30, 100, 40, 100)],
    'lime': [(70, 90, 30, 100, 40, 100)],
    'green': [(90, 150, 20, 100, 20, 100)],
    'teal': [(150, 180, 20, 100, 20, 100)],
    'cyan': [(180, 200, 20, 100, 30, 100)],
    'blue': [(200, 250, 20, 100, 20, 100)],
    'purple': [(250, 290, 20, 100, 20, 100)],
    'magenta': [(290, 330, 20, 100, 30, 100)],
    'pink': [(330, 345, 20, 80, 50, 100)],
    'brown': [(15, 45, 30, 80, 15, 60)],
    'tan': [(25, 50, 15, 50, 40, 80)],
    'gold': [(40, 55, 50, 100, 50, 100)],
    'silver': [(0, 360, 0, 15, 50, 85)],
    'gray': [(0, 360, 0, 20, 25, 70)],
    'black': [(0, 360, 0, 100, 0, 25)],
    'white': [(0, 360, 0, 20, 80, 100)],
}

# Category keywords
CATEGORY_KEYWORDS = {
    'chair': ['chair', 'throne', 'seat', 'stool'],
    'table': ['table', 'desk', 'workbench', 'counter'],
    'bed': ['bed', 'mattress'],
    'door': ['door', 'gate', 'portal'],
    'chest': ['chest', 'safe', 'barrel', 'crate', 'storage'],
    'light': ['torch', 'lamp', 'lantern', 'candle', 'chandelier', 'light', 'candelabra', 'firefly'],
    'decoration': ['statue', 'trophy', 'banner', 'painting', 'vase', 'bottle', 'bowl', 'pot', 'clock', 'fountain'],
    'plant': ['plant', 'flower', 'herb', 'tree', 'sapling', 'mushroom', 'vine', 'grass', 'moss', 'coral', 'seaweed', 'cactus', 'sunflower', 'rose'],
    'crystal': ['crystal', 'gem', 'gemspark', 'diamond', 'ruby', 'sapphire', 'emerald', 'amethyst', 'topaz'],
    'ore': ['ore', 'vein'],
    'brick': ['brick', 'stone', 'block', 'tile', 'slab'],
    'wood': ['wood', 'plank', 'lumber', 'mahogany', 'ebonwood', 'shadewood', 'pearlwood', 'boreal', 'palm'],
    'metal': ['iron', 'copper', 'silver', 'gold', 'platinum', 'cobalt', 'mythril', 'adamantite', 'titanium', 'chlorophyte', 'luminite', 'lead', 'tin', 'tungsten'],
    'glass': ['glass', 'window', 'stained'],
    'platform': ['platform', 'scaffold'],
    'bookshelf': ['bookcase', 'bookshelf', 'book'],
    'piano': ['piano', 'organ'],
    'dresser': ['dresser', 'wardrobe', 'cabinet'],
    'clock': ['clock', 'grandfather'],
    'bath': ['bathtub', 'sink', 'toilet'],
    'cooking': ['cooking pot', 'cauldron', 'furnace', 'forge', 'oven', 'campfire', 'fireplace', 'hellforge'],
    'crafting': ['anvil', 'loom', 'sawmill', 'extractinator', 'solidifier'],
    'dungeon': ['dungeon', 'spike', 'bone', 'skull'],
    'jungle': ['jungle', 'hive', 'honey', 'bee', 'lihzahrd'],
    'corruption': ['corruption', 'demonite', 'ebonstone', 'shadow', 'corrupt', 'demon'],
    'crimson': ['crimson', 'crimtane', 'flesh', 'tissue', 'blood'],
    'hallow': ['hallow', 'pearlstone', 'crystal', 'unicorn', 'holy', 'rainbow'],
    'snow': ['snow', 'ice', 'frozen', 'boreal', 'frost'],
    'desert': ['sand', 'sandstone', 'desert', 'pyramid', 'pharaoh'],
    'ocean': ['coral', 'shell', 'ocean', 'beach', 'palm'],
    'space': ['meteor', 'lunar', 'martian', 'nebula', 'solar', 'stardust', 'vortex'],
}


def rgb_to_hsv(r, g, b):
    """Convert RGB (0-255) to HSV (H: 0-360, S: 0-100, V: 0-100)."""
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    max_c = max(r, g, b)
    min_c = min(r, g, b)
    diff = max_c - min_c
    
    # Value
    v = max_c * 100
    
    # Saturation
    if max_c == 0:
        s = 0
    else:
        s = (diff / max_c) * 100
    
    # Hue
    if diff == 0:
        h = 0
    elif max_c == r:
        h = (60 * ((g - b) / diff) + 360) % 360
    elif max_c == g:
        h = (60 * ((b - r) / diff) + 120) % 360
    else:
        h = (60 * ((r - g) / diff) + 240) % 360
    
    return h, s, v


def get_color_from_hsv(h, s, v):
    """Determine color name(s) from HSV values."""
    colors = []
    
    for color_name, ranges in COLOR_RANGES.items():
        for h_min, h_max, s_min, s_max, v_min, v_max in ranges:
            if h_min <= h <= h_max and s_min <= s <= s_max and v_min <= v <= v_max:
                colors.append(color_name)
                break
    
    return colors


def analyze_image_colors(img):
    """Analyze an image and return dominant colors with percentages."""
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    # Sample pixels for speed - resize large images
    w, h = img.size
    if w * h > 10000:
        # Downsample to ~100x100 max
        scale = min(100 / w, 100 / h, 1.0)
        if scale < 1.0:
            img = img.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.NEAREST)
    
    pixels = list(img.getdata())
    color_counts = Counter()
    total_opaque = 0
    
    for pixel in pixels:
        if len(pixel) < 4:
            r, g, b = pixel[:3]
            a = 255
        else:
            r, g, b, a = pixel
        
        # Skip transparent pixels
        if a < 128:
            continue
        
        total_opaque += 1
        h, s, v = rgb_to_hsv(r, g, b)
        colors = get_color_from_hsv(h, s, v)
        
        for color in colors:
            color_counts[color] += 1
    
    if total_opaque == 0:
        return []
    
    # Return colors that make up at least 10% of opaque pixels
    significant_colors = []
    for color, count in color_counts.most_common():
        percentage = (count / total_opaque) * 100
        if percentage >= 10:
            significant_colors.append(color)
        if len(significant_colors) >= 3:  # Max 3 color tags
            break
    
    return significant_colors


def extract_category_tags(name):
    """Extract category tags from item name."""
    tags = set()
    name_lower = name.lower()
    
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in name_lower:
                tags.add(category)
                break
    
    return list(tags)


def analyze_all_textures():
    """Analyze all textures and generate tags."""
    print("Analyzing textures...")
    
    results = {
        'blocks': {},
        'walls': {},
        'furniture': {}
    }
    
    # Analyze tiles (blocks and furniture)
    tile_files = sorted(TEXTURE_DIR.glob("Tiles_*.png"))
    for i, path in enumerate(tile_files):
        match = re.match(r'Tiles_(\d+)\.png', path.name)
        if not match:
            continue
        
        tid = int(match.group(1))
        
        # Get name
        if tid in FURNITURE_NAMES:
            name = FURNITURE_NAMES[tid]
            item_type = 'furniture'
        else:
            name = TILE_NAMES.get(tid, f"Tile {tid}")
            item_type = 'blocks'
        
        try:
            img = Image.open(path)
            color_tags = analyze_image_colors(img)
            category_tags = extract_category_tags(name)
            
            all_tags = list(set(color_tags + category_tags))
            
            results[item_type][str(tid)] = {
                'name': name,
                'colors': color_tags,
                'categories': category_tags,
                'tags': all_tags
            }
            
            if (i + 1) % 50 == 0:
                print(f"  Processed {i + 1}/{len(tile_files)} tiles...")
                
        except Exception as e:
            print(f"  Error processing {path.name}: {e}")
    
    # Analyze walls
    wall_files = sorted(TEXTURE_DIR.glob("Wall_*.png"))
    for i, path in enumerate(wall_files):
        match = re.match(r'Wall_(\d+)\.png', path.name)
        if not match:
            continue
        
        wid = int(match.group(1))
        name = WALL_NAMES.get(wid, f"Wall {wid}")
        
        try:
            img = Image.open(path)
            color_tags = analyze_image_colors(img)
            category_tags = extract_category_tags(name)
            
            all_tags = list(set(color_tags + category_tags))
            
            results['walls'][str(wid)] = {
                'name': name,
                'colors': color_tags,
                'categories': category_tags,
                'tags': all_tags
            }
            
            if (i + 1) % 50 == 0:
                print(f"  Processed {i + 1}/{len(wall_files)} walls...")
                
        except Exception as e:
            print(f"  Error processing {path.name}: {e}")
    
    return results


def main():
    print("=" * 50)
    print("Terraria Texture Color Analyzer")
    print("=" * 50)
    
    if not TEXTURE_DIR.exists():
        print(f"Error: Texture directory not found: {TEXTURE_DIR}")
        return
    
    results = analyze_all_textures()
    
    # Stats
    total_blocks = len(results['blocks'])
    total_furniture = len(results['furniture'])
    total_walls = len(results['walls'])
    
    print(f"\nAnalysis complete!")
    print(f"  Blocks: {total_blocks}")
    print(f"  Furniture: {total_furniture}")
    print(f"  Walls: {total_walls}")
    
    # Save to JSON
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nSaved to: {OUTPUT_FILE}")
    
    # Show some examples
    print("\nSample color detections:")
    samples = list(results['blocks'].items())[:5]
    for tid, data in samples:
        print(f"  {tid}: {data['name']} -> {data['colors']}")


if __name__ == "__main__":
    main()
