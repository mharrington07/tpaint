"""
Terraria Texture Paint App
Clean UI with tabs, hotkeys, fast search, furniture support, and wall+block layering.
Blocks can be placed on top of walls (torches on walls, tables in front of walls, etc.)
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np
from pathlib import Path
import re
import os


TEXTURE_DIR = Path(__file__).parent / "textures"
TILE_SIZE = 16

# Import data
try:
    from terraria_names import TILE_NAMES, WALL_NAMES
except ImportError:
    TILE_NAMES = {}
    WALL_NAMES = {}

try:
    from tile_colors import TILE_COLORS, WALL_COLORS
except ImportError:
    TILE_COLORS = {}
    WALL_COLORS = {}


# Block frame lookup
TILE_FRAME_MAP = {
    0b0000: [(9, 3)], 0b0001: [(6, 3)], 0b0010: [(9, 0)], 0b0100: [(6, 0)],
    0b1000: [(12, 0)], 0b0101: [(5, 0)], 0b1010: [(6, 4)], 0b0011: [(0, 2)],
    0b0110: [(0, 0)], 0b1100: [(3, 0)], 0b1001: [(3, 2)], 0b0111: [(0, 1)],
    0b1110: [(3, 1)], 0b1101: [(0, 1)], 0b1011: [(1, 2)], 0b1111: [(1, 1)],
}

# Furniture definitions: tile_id -> (name, tile_width, tile_height, frame_pixel_w, frame_pixel_h)
# These are multi-tile objects that don't auto-tile
FURNITURE = {
    # Torches (all variants)
    4: ("Torch", 1, 1, 22, 22),
    
    # Candles
    33: ("Candle", 1, 1, 18, 20),
    49: ("Water Candle", 1, 2, 18, 36),
    
    # Lanterns & Lights
    42: ("Lantern", 1, 2, 18, 36),
    93: ("Tiki Torch", 1, 3, 18, 54),
    100: ("Candelabra", 2, 2, 36, 36),
    34: ("Chandelier", 3, 3, 54, 54),
    35: ("Silver Chandelier", 3, 3, 54, 54),
    36: ("Gold Chandelier", 3, 3, 54, 54),
    
    # Tables (all wood types share same base tile with variants in sheet)
    14: ("Table", 3, 2, 54, 36),
    
    # Workbenches
    18: ("Workbench", 2, 1, 36, 18),
    
    # Chairs (all variants in single sheet)
    15: ("Chair", 1, 2, 18, 40),
    497: ("Chair", 1, 2, 18, 40),
    
    # Doors
    10: ("Closed Door", 1, 3, 18, 54),
    11: ("Open Door", 2, 3, 36, 54),
    
    # Chests (main chest tile has ALL variants)
    21: ("Chest", 2, 2, 36, 36),
    441: ("Chest", 2, 2, 36, 36),
    467: ("Chest", 2, 2, 36, 38),
    468: ("Chest", 2, 2, 36, 38),
    
    # Dressers
    88: ("Dresser", 3, 2, 54, 36),
    
    # Beds (all variants)
    79: ("Bed", 4, 2, 72, 36),
    
    # Benches
    89: ("Bench", 3, 2, 54, 36),
    
    # Bathtubs
    90: ("Bathtub", 4, 2, 72, 36),
    
    # Pianos
    87: ("Piano", 3, 2, 54, 36),
    
    # Bookcases
    101: ("Bookcase", 3, 4, 54, 72),
    
    # Grandfather Clocks
    104: ("Grandfather Clock", 2, 5, 36, 90),
    
    # Thrones
    102: ("Throne", 3, 4, 52, 70),
    
    # Statues
    105: ("Statue", 2, 3, 36, 54),
    
    # Furnaces
    17: ("Furnace", 3, 2, 54, 36),
    77: ("Hellforge", 3, 2, 54, 36),
    133: ("Adamantite Forge", 3, 2, 54, 36),
    
    # Anvils
    16: ("Anvil", 2, 1, 36, 18),
    134: ("Mythril Anvil", 2, 1, 36, 18),
    
    # Crafting stations
    86: ("Loom", 3, 2, 54, 36),
    94: ("Keg", 2, 2, 36, 36),
    96: ("Cooking Pot", 2, 2, 36, 36),
    106: ("Sawmill", 3, 3, 54, 54),
    228: ("Dye Vat", 3, 2, 54, 36),
    243: ("Imbuing Station", 2, 2, 36, 36),
    247: ("Autohammer", 3, 2, 54, 36),
    
    # Storage
    29: ("Piggy Bank", 2, 1, 36, 18),
    97: ("Safe", 2, 2, 36, 36),
    
    # Decorative
    13: ("Bottle", 1, 1, 18, 18),
    28: ("Pot", 2, 2, 36, 36),
    50: ("Books", 3, 1, 54, 18),
    55: ("Sign", 2, 2, 36, 36),
    85: ("Tombstone", 2, 2, 36, 36),
    103: ("Bowl", 1, 1, 18, 18),
    125: ("Crystal Ball", 2, 2, 36, 36),
    126: ("Disco Ball", 2, 2, 36, 36),
    128: ("Mannequin", 2, 3, 36, 54),
    139: ("Music Box", 2, 2, 36, 36),
    207: ("Water Fountain", 2, 4, 36, 72),
    215: ("Campfire", 3, 2, 54, 36),
    217: ("Firework Fountain", 2, 2, 36, 36),
    244: ("Bubble Machine", 2, 2, 36, 36),
    
    # Cages
    219: ("Bunny Cage", 3, 3, 54, 54),
    220: ("Squirrel Cage", 3, 3, 54, 54),
    
    # Misc
    132: ("Lever", 1, 1, 18, 18),
    209: ("Cannon", 3, 2, 54, 36),
    
    # Paintings & Banners (various sizes)
    240: ("Painting 3x3", 3, 3, 54, 54),
    245: ("Banner", 1, 3, 18, 54),
    
    # Sinks
    172: ("Sink", 2, 2, 36, 36),
    
    # Toilet
    380: ("Toilet", 1, 2, 18, 36),
    
    # Sofas (various wood)
    # 89 is already Bench above
    
    # Lamp posts
    92: ("Lamp Post", 1, 6, 18, 108),
}


def scan_textures():
    tiles, walls = [], []
    for f in TEXTURE_DIR.iterdir():
        if m := re.match(r'Tiles_(\d+)\.png', f.name):
            tiles.append(int(m.group(1)))
        elif m := re.match(r'Wall_(\d+)\.png', f.name):
            walls.append(int(m.group(1)))
    return sorted(tiles), sorted(walls)


class TileCache:
    def __init__(self, tile_ids, wall_ids):
        self.sheets = {}
        self.cache = {}
        self.tile_info = {}
        self.wall_info = {}
        self.furniture_info = {}
        self._load(tile_ids, wall_ids)
    
    def _load(self, tile_ids, wall_ids):
        for tid in tile_ids:
            path = TEXTURE_DIR / f"Tiles_{tid}.png"
            if path.exists():
                try:
                    self.sheets[('t', tid)] = Image.open(path).convert('RGBA')
                    if tid in FURNITURE:
                        name = FURNITURE[tid][0]
                        self.furniture_info[tid] = (name, TILE_COLORS.get(tid, (128,128,128)))
                    else:
                        name = TILE_NAMES.get(tid, f"Tile {tid}")
                        self.tile_info[tid] = (name, TILE_COLORS.get(tid, (128,128,128)))
                except: pass
        
        for wid in wall_ids:
            path = TEXTURE_DIR / f"Wall_{wid}.png"
            if path.exists():
                try:
                    self.sheets[('w', wid)] = Image.open(path).convert('RGBA')
                    name = WALL_NAMES.get(wid, f"Wall {wid}")
                    self.wall_info[wid] = (name, WALL_COLORS.get(wid, (80,80,80)))
                except: pass
        
        print(f"Loaded {len(self.tile_info)} blocks, {len(self.furniture_info)} furniture, {len(self.wall_info)} walls")
    
    def get_block(self, tid, neighbors):
        if ('t', tid) not in self.sheets:
            return None
        if tid in FURNITURE:
            return self.get_furniture(tid)
        
        # Convert bool to int for bitmask
        n = 1 if neighbors.get('n') else 0
        e = 1 if neighbors.get('e') else 0
        s = 1 if neighbors.get('s') else 0
        w = 1 if neighbors.get('w') else 0
        mask = (n << 0) | (e << 1) | (s << 2) | (w << 3)
        
        col, row = TILE_FRAME_MAP.get(mask, [(1,1)])[0]
        
        key = ('b', tid, col, row)
        if key not in self.cache:
            sheet = self.sheets[('t', tid)]
            sw, sh = sheet.size
            x, y = col * 18 + 1, row * 18 + 1
            if x + 16 > sw: x = 1
            if y + 16 > sh: y = 1
            self.cache[key] = sheet.crop((x, y, x+16, y+16))
        return self.cache[key]
    
    def get_furniture(self, tid):
        key = ('f', tid)
        if key not in self.cache:
            sheet = self.sheets.get(('t', tid))
            if not sheet:
                return None
            info = FURNITURE.get(tid)
            if info:
                _, tw, th, fw, fh = info
                # Extract first frame, scale to fit grid size
                frame = sheet.crop((0, 0, min(fw, sheet.width), min(fh, sheet.height)))
                # Scale to tile grid size
                target_w, target_h = tw * 16, th * 16
                frame = frame.resize((target_w, target_h), Image.NEAREST)
                self.cache[key] = frame
            else:
                self.cache[key] = sheet.crop((0, 0, 16, 16))
        return self.cache[key]
    
    def get_wall(self, wid, neighbors=None):
        key = ('w', wid, 'tile')
        if key not in self.cache:
            sheet = self.sheets.get(('w', wid))
            if not sheet:
                return None
            w, h = sheet.size
            # Use solid center frame
            fx, fy = 9 * 36, 3 * 36
            if fx + 36 > w: fx = 0
            if fy + 36 > h: fy = 0
            x, y = fx + 10, fy + 10
            if x + 16 > w: x = fx + 2
            if y + 16 > h: y = fy + 2
            frame = sheet.crop((x, y, x+16, y+16))
            if np.array(frame)[:,:,3].sum() < 128 * 256:
                frame = sheet.crop((fx+2, fy+2, fx+34, fy+34)).resize((16,16), Image.NEAREST)
            self.cache[key] = frame
        return self.cache[key]


class TerrariaPaint:
    def __init__(self, root):
        self.root = root
        self.root.title("TPaint - Terraria Builder")
        self.root.configure(bg='#1e1e2e')
        
        # Grid - now uses layered cells: {'wall': wall_id or None, 'block': block_data or None}
        # block_data can be ('block', tile_id) or ('furn', tile_id, fx, fy)
        self.cols, self.rows = 64, 40
        self.grid = [[{'wall': None, 'block': None} for _ in range(self.cols)] for _ in range(self.rows)]
        
        # State
        self.tool = 'block'
        self.layer = 'block'  # 'block' or 'wall' - what layer the current tool affects
        self.block_id = 30
        self.wall_id = 4
        self.brush = 1
        self.photos = {}
        self.search_job = None
        self.zoom = 1.0  # Zoom level (0.25 to 4.0)
        
        # Tool state for line/circle/select
        self.tool_start = None  # (row, col) for line/circle start
        self.tool_preview = []  # Preview points
        self.fill_shape = False  # Fill shapes or outline only
        self.selection = None  # {'r1', 'c1', 'r2', 'c2'} or None
        self.clipboard = None  # Grid data for paste
        
        # Move tool state
        self.moving = False  # Whether currently moving a selection
        self.move_start = None  # (row, col) where move started
        self.move_data = None  # Grid data being moved
        
        # Undo/Redo system
        self.undo_stack = []  # List of grid states
        self.redo_stack = []  # List of grid states for redo
        self.max_undo = 50  # Maximum undo steps
        
        # Reference image
        self.reference_image = None  # PIL Image
        self.reference_photo = None  # PhotoImage for display
        self.reference_opacity = 0.5
        self.show_reference = False
        
        # Project state
        self.project_path = None  # Current .tpaint file path
        
        # Load tool icons
        self._load_icons()
        
        # Load textures
        print("Loading textures...")
        tile_ids, wall_ids = scan_textures()
        self.cache = TileCache(tile_ids, wall_ids)
        
        self._build_ui()
        self._bind_keys()
        self._render()
    
    def _load_icons(self):
        """Load tool icons from icons folder."""
        from pathlib import Path
        self.icons = {}
        icons_dir = Path(__file__).parent / "icons"
        
        # Tool names that match icon filenames directly
        tool_icons = ['block', 'wall', 'fill', 'line', 'circle', 'rect', 'select', 'erase', 'eyedropper']
        
        for tool_name in tool_icons:
            path = icons_dir / f"{tool_name}.png"
            if path.exists():
                img = Image.open(path).convert('RGBA')
                # Resize if needed
                if img.width != 32 or img.height != 32:
                    img = img.resize((32, 32), Image.NEAREST)
                self.icons[tool_name] = ImageTk.PhotoImage(img)
    
    def _build_ui(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Modern dark theme colors - sleeker palette
        bg_dark = '#0d1117'     # GitHub dark
        bg_mid = '#161b22'       # Card background
        bg_light = '#21262d'     # Elevated elements
        bg_hover = '#30363d'     # Hover state
        accent = '#58a6ff'       # Primary accent (blue)
        accent_dim = '#388bfd'   # Accent hover
        accent_glow = '#1f6feb'  # Selection glow
        text = '#e6edf3'         # Primary text
        text_dim = '#7d8590'     # Secondary text
        border = '#30363d'       # Borders
        success = '#3fb950'      # Green accent
        
        # Configure styles with rounded feel
        style.configure('TFrame', background=bg_dark)
        style.configure('TLabel', background=bg_dark, foreground=text, font=('Segoe UI', 9))
        style.configure('TLabelframe', background=bg_mid, foreground=text, borderwidth=2, relief='flat')
        style.configure('TLabelframe.Label', background=bg_mid, foreground=accent, font=('Segoe UI', 10, 'bold'))
        style.configure('TNotebook', background=bg_dark, borderwidth=0, padding=4)
        style.configure('TNotebook.Tab', background=bg_light, foreground=text_dim, padding=[16, 8], font=('Segoe UI', 9, 'bold'))
        style.map('TNotebook.Tab', background=[('selected', bg_mid)], foreground=[('selected', text)])
        style.configure('TButton', background=bg_light, foreground=text, font=('Segoe UI', 9, 'bold'), padding=[12, 6], borderwidth=0)
        style.map('TButton', background=[('active', accent_dim), ('pressed', accent_glow)])
        style.configure('TRadiobutton', background=bg_dark, foreground=text, font=('Segoe UI', 9))
        style.map('TRadiobutton', background=[('active', bg_dark)])
        style.configure('TEntry', fieldbackground=bg_light, foreground=text, insertcolor=text, borderwidth=0, padding=6)
        style.configure('TSpinbox', fieldbackground=bg_light, foreground=text, arrowcolor=text, borderwidth=0, padding=4)
        style.configure('TScrollbar', background=bg_light, troughcolor=bg_dark, arrowcolor=text, borderwidth=0)
        style.map('TScrollbar', background=[('active', bg_hover)])
        style.configure('TCheckbutton', background=bg_dark, foreground=text, font=('Segoe UI', 9))
        style.map('TCheckbutton', background=[('active', bg_dark)])
        
        self.root.configure(bg=bg_dark)
        self.colors = {'bg_dark': bg_dark, 'bg_mid': bg_mid, 'bg_light': bg_light, 
                       'bg_hover': bg_hover, 'accent': accent, 'accent_dim': accent_dim,
                       'text': text, 'text_dim': text_dim, 'border': border}
        
        main = ttk.Frame(self.root)
        main.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        
        # Left panel
        left = ttk.Frame(main, width=320)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0,12))
        left.pack_propagate(False)
        
        # Tools - Modern card-style toolbar
        tools_card = tk.Frame(left, bg=bg_mid, highlightbackground=border, highlightthickness=1)
        tools_card.pack(fill=tk.X, pady=(0,12))
        
        # Tools header
        tools_header = tk.Frame(tools_card, bg=bg_mid)
        tools_header.pack(fill=tk.X, padx=12, pady=(12,8))
        tk.Label(tools_header, text="Tools", bg=bg_mid, fg=accent, font=('Segoe UI', 11, 'bold')).pack(side=tk.LEFT)
        
        # Drawing tools row with modern buttons
        tool_row1 = tk.Frame(tools_card, bg=bg_mid)
        tool_row1.pack(fill=tk.X, pady=(0,12), padx=12)
        
        self.tool_var = tk.StringVar(value='block')
        self.tool_buttons = {}
        
        tool_defs = [
            ('block', 'Block [B]', 'block'),
            ('wall', 'Wall [W]', 'wall'),
            ('erase', 'Eraser [E]', 'erase'),
            ('fill', 'Fill [F]', 'fill'),
            ('line', 'Line [L]', 'line'),
            ('circle', 'Circle [O]', 'circle'),
            ('rect', 'Rectangle [R]', 'rect'),
            ('select', 'Select [M]', 'select'),
            ('eyedropper', 'Pick Tile [I]', 'eyedropper'),
        ]
        
        for icon_name, tooltip, tool_val in tool_defs:
            # Modern rounded-feel button with padding
            btn_frame = tk.Frame(tool_row1, bg=bg_mid)
            btn_frame.pack(side=tk.LEFT, padx=3)
            
            btn = tk.Button(btn_frame, 
                           image=self.icons.get(icon_name),
                           bg=bg_light, activebackground=accent_dim,
                           relief='flat', bd=0, 
                           padx=8, pady=8,
                           cursor='hand2',
                           command=lambda t=tool_val: self._set_tool(t))
            btn.pack(padx=1, pady=1)
            
            # Hover effects
            btn.bind('<Enter>', lambda e, b=btn: b.config(bg=bg_hover))
            btn.bind('<Leave>', lambda e, b=btn, t=tool_val: b.config(bg=accent if t == self.tool else bg_light))
            
            self.tool_buttons[tool_val] = btn
            self._create_tooltip(btn, tooltip)
        
        # Layer selection (modern toggle buttons)
        layer_row = tk.Frame(tools_card, bg=bg_mid)
        layer_row.pack(fill=tk.X, pady=(0,8), padx=12)
        
        tk.Label(layer_row, text="Layer:", bg=bg_mid, fg=text_dim, font=('Segoe UI', 9)).pack(side=tk.LEFT, padx=(0,8))
        self.layer_var = tk.StringVar(value='block')
        for txt, val in [("Block", "block"), ("Wall", "wall")]:
            rb = tk.Radiobutton(layer_row, text=txt, variable=self.layer_var, value=val,
                               bg=bg_light, fg=text, selectcolor=accent_glow, activebackground=bg_hover,
                               indicatoron=0, padx=12, pady=4, relief='flat', cursor='hand2',
                               command=self._layer_changed)
            rb.pack(side=tk.LEFT, padx=2)
        
        # Shape options row
        shape_row = tk.Frame(tools_card, bg=bg_mid)
        shape_row.pack(fill=tk.X, pady=(0,12), padx=12)
        
        self.fill_var = tk.BooleanVar(value=False)
        fill_cb = tk.Checkbutton(shape_row, text="Fill Shapes", variable=self.fill_var,
                      bg=bg_mid, fg=text, selectcolor=accent_glow, activebackground=bg_mid,
                      cursor='hand2',
                      command=lambda: setattr(self, 'fill_shape', self.fill_var.get()))
        fill_cb.pack(side=tk.LEFT)
        
        # Brush size card
        brush_card = tk.Frame(left, bg=bg_mid, highlightbackground=border, highlightthickness=1)
        brush_card.pack(fill=tk.X, pady=(0,12))
        
        brush_header = tk.Frame(brush_card, bg=bg_mid)
        brush_header.pack(fill=tk.X, padx=12, pady=(12,6))
        tk.Label(brush_header, text="Brush Size", bg=bg_mid, fg=accent, font=('Segoe UI', 11, 'bold')).pack(side=tk.LEFT)
        
        self.brush_var = tk.IntVar(value=1)
        self.brush_label = tk.Label(brush_header, text="1x1", bg=bg_mid, fg=text, 
                                    font=('Segoe UI', 10, 'bold'))
        self.brush_label.pack(side=tk.RIGHT)
        
        brush_row = tk.Frame(brush_card, bg=bg_mid)
        brush_row.pack(fill=tk.X, pady=(0,12), padx=12)
        
        # Modern slider
        self.brush_slider = tk.Scale(brush_row, from_=1, to=20, orient=tk.HORIZONTAL,
                                     variable=self.brush_var, command=self._brush_slider_changed,
                                     bg=bg_mid, fg=text, troughcolor=bg_light, 
                                     activebackground=accent, highlightthickness=0,
                                     sliderrelief='flat', length=260, showvalue=0,
                                     sliderlength=20)
        self.brush_slider.pack(fill=tk.X)
        
        # Grid Size card
        size_card = tk.Frame(left, bg=bg_mid, highlightbackground=border, highlightthickness=1)
        size_card.pack(fill=tk.X, pady=(0,12))
        
        size_header = tk.Frame(size_card, bg=bg_mid)
        size_header.pack(fill=tk.X, padx=12, pady=(12,8))
        tk.Label(size_header, text="Grid Size", bg=bg_mid, fg=accent, font=('Segoe UI', 11, 'bold')).pack(side=tk.LEFT)
        
        size_frame = tk.Frame(size_card, bg=bg_mid)
        size_frame.pack(fill=tk.X)
        
        size_row = tk.Frame(size_frame, bg=bg_mid)
        size_row.pack(fill=tk.X, pady=(0,12), padx=12)
        tk.Label(size_row, text="W:", bg=bg_mid, fg=text_dim, font=('Segoe UI', 9)).pack(side=tk.LEFT)
        self.width_var = tk.StringVar(value=str(self.cols))
        w_entry = tk.Entry(size_row, textvariable=self.width_var, width=6, bg=bg_light, fg=text,
                          insertbackground=text, relief='flat', font=('Segoe UI', 10))
        w_entry.pack(side=tk.LEFT, padx=(4,16))
        tk.Label(size_row, text="H:", bg=bg_mid, fg=text_dim, font=('Segoe UI', 9)).pack(side=tk.LEFT)
        self.height_var = tk.StringVar(value=str(self.rows))
        h_entry = tk.Entry(size_row, textvariable=self.height_var, width=6, bg=bg_light, fg=text,
                          insertbackground=text, relief='flat', font=('Segoe UI', 10))
        h_entry.pack(side=tk.LEFT, padx=(4,16))
        apply_btn = tk.Button(size_row, text="Apply", command=self._resize_grid,
                             bg=accent, fg='#ffffff', activebackground=accent_dim,
                             relief='flat', padx=12, pady=2, cursor='hand2', font=('Segoe UI', 9, 'bold'))
        apply_btn.pack(side=tk.LEFT)
        
        # Notebook tabs
        notebook = ttk.Notebook(left)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0,8))
        
        # Blocks tab
        block_frame = ttk.Frame(notebook)
        notebook.add(block_frame, text=f"  Blocks ({len(self.cache.tile_info)})  ")
        
        self.block_search = tk.StringVar()
        self.block_search.trace_add('write', lambda *a: self._search_delayed('block'))
        search_entry = ttk.Entry(block_frame, textvariable=self.block_search, font=('Segoe UI', 10))
        search_entry.pack(fill=tk.X, padx=4, pady=6)
        search_entry.insert(0, '')
        
        self.block_list = self._create_list(block_frame)
        self._populate_blocks()
        
        # Furniture tab
        furn_frame = ttk.Frame(notebook)
        notebook.add(furn_frame, text=f"  Furniture ({len(self.cache.furniture_info)})  ")
        
        self.furn_search = tk.StringVar()
        self.furn_search.trace_add('write', lambda *a: self._search_delayed('furniture'))
        ttk.Entry(furn_frame, textvariable=self.furn_search, font=('Segoe UI', 10)).pack(fill=tk.X, padx=4, pady=6)
        
        self.furn_list = self._create_list(furn_frame)
        self._populate_furniture()
        
        # Walls tab
        wall_frame = ttk.Frame(notebook)
        notebook.add(wall_frame, text=f"  Walls ({len(self.cache.wall_info)})  ")
        
        self.wall_search = tk.StringVar()
        self.wall_search.trace_add('write', lambda *a: self._search_delayed('wall'))
        ttk.Entry(wall_frame, textvariable=self.wall_search, font=('Segoe UI', 10)).pack(fill=tk.X, padx=4, pady=6)
        
        self.wall_list = self._create_list(wall_frame)
        self._populate_walls()
        
        # Action buttons - modern card style
        actions = tk.Frame(left, bg=bg_dark)
        actions.pack(fill=tk.X, pady=(8,0))
        
        clear_btn = tk.Button(actions, text="Clear [C]", command=self._clear,
                             bg=bg_light, fg=text, activebackground=bg_hover,
                             relief='flat', padx=16, pady=8, cursor='hand2',
                             font=('Segoe UI', 9, 'bold'))
        clear_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0,6))
        
        save_btn = tk.Button(actions, text="Save [S]", command=self._save,
                            bg=accent, fg='#ffffff', activebackground=accent_dim,
                            relief='flat', padx=16, pady=8, cursor='hand2',
                            font=('Segoe UI', 9, 'bold'))
        save_btn.pack(side=tk.LEFT, expand=True, fill=tk.X)
        
        # Canvas area with subtle border
        canvas_frame = tk.Frame(main, bg=border, highlightbackground=border, highlightthickness=1)
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        xscroll = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL)
        yscroll = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL)
        
        self.canvas = tk.Canvas(canvas_frame, bg='#010409', highlightthickness=0,
                               xscrollcommand=xscroll.set, yscrollcommand=yscroll.set,
                               scrollregion=(0, 0, self.cols*TILE_SIZE, self.rows*TILE_SIZE))
        
        xscroll.config(command=self.canvas.xview)
        yscroll.config(command=self.canvas.yview)
        
        yscroll.pack(side=tk.RIGHT, fill=tk.Y)
        xscroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.canvas.bind('<Button-1>', self._click)
        self.canvas.bind('<B1-Motion>', self._drag)
        self.canvas.bind('<ButtonRelease-1>', self._release)
        self.canvas.bind('<Button-3>', self._right_click)
        self.canvas.bind('<B3-Motion>', self._right_drag)
        self.canvas.bind('<Motion>', self._hover)
        self.canvas.bind('<Leave>', lambda e: self.canvas.delete('cursor'))
        
        # Middle-click pan
        self.canvas.bind('<Button-2>', self._pan_start)
        self.canvas.bind('<B2-Motion>', self._pan_move)
        self.canvas.bind('<ButtonRelease-2>', self._pan_end)
        self._pan_data = None
        
        # Scroll wheel zoom
        self.canvas.bind('<MouseWheel>', self._zoom)
        
        # Status bar
        status_frame = tk.Frame(self.root, bg=bg_mid, height=28)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        status_frame.pack_propagate(False)
        
        self.status = tk.StringVar(value="Ready • Ctrl+Z/Y=Undo/Redo • Ctrl+S/O=Save/Open • Ctrl+N=New • B/W/E/F/L/O/R/M/I=Tools")
        tk.Label(status_frame, textvariable=self.status, bg=bg_mid, fg=text_dim, 
                font=('Segoe UI', 9), anchor='w', padx=10).pack(fill=tk.BOTH, expand=True)
    
    def _create_list(self, parent):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True)
        
        bg = self.colors['bg_mid']
        canvas = tk.Canvas(frame, bg=bg, highlightthickness=0, bd=0)
        scroll = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
        inner = tk.Frame(canvas, bg=bg)
        
        canvas.configure(yscrollcommand=scroll.set)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        win = canvas.create_window((0,0), window=inner, anchor='nw')
        canvas.bind('<Configure>', lambda e: canvas.itemconfig(win, width=e.width))
        inner.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.bind('<MouseWheel>', lambda e: canvas.yview_scroll(-1*(e.delta//120), 'units'))
        inner.bind('<MouseWheel>', lambda e: canvas.yview_scroll(-1*(e.delta//120), 'units'))
        
        return {'canvas': canvas, 'inner': inner, 'photos': []}
    
    def _populate_blocks(self, filter_text=""):
        self._populate_list(self.block_list, self.cache.tile_info, filter_text, 'block')
    
    def _populate_furniture(self, filter_text=""):
        self._populate_list(self.furn_list, self.cache.furniture_info, filter_text, 'furniture')
    
    def _populate_walls(self, filter_text=""):
        self._populate_list(self.wall_list, self.cache.wall_info, filter_text, 'wall')
    
    def _populate_list(self, lst, data, filter_text, item_type):
        inner = lst['inner']
        for w in inner.winfo_children():
            w.destroy()
        lst['photos'].clear()
        
        filter_text = filter_text.lower()
        bg_mid = self.colors['bg_mid']
        bg_light = self.colors['bg_light']
        text = self.colors['text']
        accent = self.colors['accent']
        
        for tid in sorted(data.keys()):
            name, rgb = data[tid]
            if filter_text and filter_text not in name.lower() and filter_text not in str(tid):
                continue
            
            row = tk.Frame(inner, bg=bg_mid)
            row.pack(fill=tk.X, pady=1, padx=4)
            
            # Texture preview (24x24)
            preview_frame = tk.Frame(row, bg=bg_mid, width=28, height=28)
            preview_frame.pack(side=tk.LEFT, padx=(0,6))
            preview_frame.pack_propagate(False)
            
            # Try to get actual texture
            preview_img = None
            try:
                if item_type == 'wall':
                    tile = self.cache.get_wall(tid)
                elif item_type == 'furniture':
                    tile = self.cache.get_furniture(tid)
                else:
                    # For blocks, get center tile (all neighbors)
                    tile = self.cache.get_block(tid, {'n': True, 'e': True, 's': True, 'w': True})
                
                if tile:
                    # Scale to 24x24
                    tw, th = tile.size
                    scale = min(24 / tw, 24 / th)
                    new_w = max(1, int(tw * scale))
                    new_h = max(1, int(th * scale))
                    scaled = tile.resize((new_w, new_h), Image.NEAREST)
                    
                    # Center on 24x24 canvas
                    preview = Image.new('RGBA', (24, 24), (0, 0, 0, 0))
                    x = (24 - new_w) // 2
                    y = (24 - new_h) // 2
                    preview.paste(scaled, (x, y), scaled)
                    preview_img = ImageTk.PhotoImage(preview)
            except:
                pass
            
            if preview_img:
                lst['photos'].append(preview_img)  # Keep reference
                lbl = tk.Label(preview_frame, image=preview_img, bg=bg_mid)
                lbl.pack(expand=True)
            else:
                # Fallback to color swatch
                color = f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'
                swatch = tk.Frame(preview_frame, bg=color, width=20, height=20)
                swatch.pack(expand=True, pady=2)
            
            # Name button
            display = f"{tid}: {name[:22]}"
            btn = tk.Button(row, text=display, anchor='w',
                           bg=bg_mid, fg=text, activebackground=accent, activeforeground='#ffffff',
                           bd=0, padx=8, pady=4, font=('Segoe UI', 9),
                           cursor='hand2',
                           command=lambda t=tid, it=item_type: self._select_item(t, it))
            btn.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            # Hover effects
            def on_enter(e, b=btn): b.config(bg=bg_light)
            def on_leave(e, b=btn): b.config(bg=bg_mid)
            btn.bind('<Enter>', on_enter)
            btn.bind('<Leave>', on_leave)
            
            # Bind mousewheel
            btn.bind('<MouseWheel>', lambda e, c=lst['canvas']: c.yview_scroll(-1*(e.delta//120), 'units'))
            preview_frame.bind('<MouseWheel>', lambda e, c=lst['canvas']: c.yview_scroll(-1*(e.delta//120), 'units'))
            row.bind('<MouseWheel>', lambda e, c=lst['canvas']: c.yview_scroll(-1*(e.delta//120), 'units'))
        
        inner.update_idletasks()
    
    def _select_item(self, tid, item_type):
        if item_type == 'wall':
            self.wall_id = tid
            self.tool_var.set('wall')
            self.tool = 'wall'
            name = self.cache.wall_info.get(tid, ("Unknown",))[0]
            self.status.set(f"Wall: {tid} - {name}")
        else:
            self.block_id = tid
            self.tool_var.set('block')
            self.tool = 'block'
            if tid in self.cache.furniture_info:
                name = self.cache.furniture_info[tid][0]
            else:
                name = self.cache.tile_info.get(tid, ("Unknown",))[0]
            self.status.set(f"Block: {tid} - {name}")
    
    def _search_delayed(self, tab):
        if self.search_job:
            self.root.after_cancel(self.search_job)
        self.search_job = self.root.after(150, lambda: self._do_search(tab))
    
    def _do_search(self, tab):
        if tab == 'block':
            self._populate_blocks(self.block_search.get())
        elif tab == 'furniture':
            self._populate_furniture(self.furn_search.get())
        elif tab == 'wall':
            self._populate_walls(self.wall_search.get())
    
    def _create_tooltip(self, widget, text):
        """Create a hover tooltip for a widget."""
        def show(e):
            tooltip = tk.Toplevel(widget)
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{e.x_root+10}+{e.y_root+10}")
            tk.Label(tooltip, text=text, bg='#161b22', fg='#e6edf3', 
                    font=('Segoe UI', 9), padx=8, pady=4, relief='flat', bd=0,
                    highlightbackground='#30363d', highlightthickness=1).pack()
            widget._tooltip = tooltip
        def hide(e):
            if hasattr(widget, '_tooltip'):
                widget._tooltip.destroy()
        widget.bind('<Enter>', show)
        widget.bind('<Leave>', hide)
    
    def _layer_changed(self):
        """Handle layer radio button change."""
        self.layer = self.layer_var.get()
    
    def _update_tool_buttons(self):
        """Update tool button appearances to show selection."""
        bg_light = self.colors['bg_light']
        accent = self.colors['accent']
        for tool, btn in self.tool_buttons.items():
            if tool == self.tool:
                btn.config(bg=accent)
            else:
                btn.config(bg=bg_light)
    
    def _bind_keys(self):
        self.root.bind('b', lambda e: self._set_tool('block'))
        self.root.bind('w', lambda e: self._set_tool('wall'))
        self.root.bind('e', lambda e: self._set_tool('erase'))
        self.root.bind('f', lambda e: self._set_tool('fill'))
        self.root.bind('l', lambda e: self._set_tool('line'))
        self.root.bind('o', lambda e: self._set_tool('circle'))
        self.root.bind('r', lambda e: self._set_tool('rect'))
        self.root.bind('m', lambda e: self._set_tool('select'))
        self.root.bind('i', lambda e: self._set_tool('eyedropper'))
        self.root.bind('1', lambda e: self._set_brush(1))
        self.root.bind('2', lambda e: self._set_brush(2))
        self.root.bind('3', lambda e: self._set_brush(3))
        self.root.bind('4', lambda e: self._set_brush(5))
        self.root.bind('5', lambda e: self._set_brush(10))
        self.root.bind('c', lambda e: self._clear())
        self.root.bind('s', lambda e: self._save())
        self.root.bind('<Escape>', lambda e: self._cancel_tool())
        self.root.bind('<Control-c>', lambda e: self._copy_selection())
        self.root.bind('<Control-v>', lambda e: self._paste_selection())
        self.root.bind('<Delete>', lambda e: self._delete_selection())
        # Undo/Redo
        self.root.bind('<Control-z>', lambda e: self._undo())
        self.root.bind('<Control-y>', lambda e: self._redo())
        self.root.bind('<Control-Z>', lambda e: self._undo())
        self.root.bind('<Control-Y>', lambda e: self._redo())
        # Project file operations
        self.root.bind('<Control-s>', lambda e: self._save_project())
        self.root.bind('<Control-S>', lambda e: self._save_project())
        self.root.bind('<Control-o>', lambda e: self._load_project())
        self.root.bind('<Control-O>', lambda e: self._load_project())
        self.root.bind('<Control-n>', lambda e: self._new_canvas())
        self.root.bind('<Control-N>', lambda e: self._new_canvas())
    
    def _cancel_tool(self):
        """Cancel current tool operation."""
        # If moving, restore the data to original position
        if self.moving and self.move_data and self.selection:
            sel = self.selection
            for ri, row_data in enumerate(self.move_data):
                for ci, cell_data in enumerate(row_data):
                    r, c = sel['r1'] + ri, sel['c1'] + ci
                    if 0 <= r < self.rows and 0 <= c < self.cols:
                        self.grid[r][c] = cell_data.copy()
                        self._render_cell(r, c)
        
        self.tool_start = None
        self.tool_preview = []
        self.selection = None
        self.moving = False
        self.move_start = None
        self.move_data = None
        self.canvas.delete('tool_preview')
        self.canvas.delete('selection')
        self.canvas.delete('move_preview')
        self.status.set("Cancelled")
    
    def _set_tool(self, tool):
        self.tool = tool
        self.tool_var.set(tool)
        self.tool_start = None
        self.tool_preview = []
        self.canvas.delete('tool_preview')
        
        # Set layer based on tool
        if tool == 'block':
            self.layer = 'block'
            self.layer_var.set('block')
        elif tool == 'wall':
            self.layer = 'wall'
            self.layer_var.set('wall')
        
        tool_names = {
            'block': 'Block',
            'wall': 'Wall',
            'erase': 'Eraser',
            'fill': 'Fill',
            'line': 'Line',
            'circle': 'Circle',
            'select': 'Select'
        }
        self.status.set(f"Tool: {tool_names.get(tool, tool.title())}")
        self._update_tool_buttons()
    
    def _set_brush(self, size):
        self.brush = size
        self.brush_var.set(size)
        self.status.set(f"Brush: {size}x{size}")
        self._update_tool_buttons()
    
    def _tool_changed(self):
        self.tool = self.tool_var.get()
        self._update_tool_buttons()
    
    def _brush_changed(self):
        self.brush = self.brush_var.get()
        self._update_tool_buttons()
    
    def _brush_slider_changed(self, value):
        """Handle brush size slider change."""
        size = int(float(value))
        self.brush = size
        self.brush_label.config(text=f"{size}x{size}")
        self.status.set(f"Brush: {size}x{size}")
    
    def _resize_grid(self):
        """Resize the grid, preserving existing content."""
        try:
            new_cols = int(self.width_var.get())
            new_rows = int(self.height_var.get())
        except ValueError:
            self.status.set("Invalid size!")
            return
        
        new_cols = max(1, min(10000, new_cols))
        new_rows = max(1, min(10000, new_rows))
        
        # Create new grid and copy existing data
        new_grid = [[{'wall': None, 'block': None} for _ in range(new_cols)] for _ in range(new_rows)]
        for r in range(min(self.rows, new_rows)):
            for c in range(min(self.cols, new_cols)):
                new_grid[r][c] = self.grid[r][c].copy()
        
        self.cols, self.rows = new_cols, new_rows
        self.grid = new_grid
        scaled_size = int(TILE_SIZE * self.zoom)
        self.canvas.config(scrollregion=(0, 0, self.cols*scaled_size, self.rows*scaled_size))
        self._render()
        self.status.set(f"Resized to {new_cols}x{new_rows}")
    
    def _pan_start(self, e):
        """Start middle-click pan."""
        self._pan_data = (e.x, e.y)
        self.canvas.config(cursor='fleur')
    
    def _pan_move(self, e):
        """Handle middle-click pan drag."""
        if self._pan_data:
            dx = e.x - self._pan_data[0]
            dy = e.y - self._pan_data[1]
            self._pan_data = (e.x, e.y)
            
            # Get current scroll position and canvas size
            x1, x2 = self.canvas.xview()
            y1, y2 = self.canvas.yview()
            
            # Calculate scroll region size
            scaled_size = int(TILE_SIZE * self.zoom)
            total_w = self.cols * scaled_size
            total_h = self.rows * scaled_size
            
            # Sensitivity factor (0.3 = 30% of normal speed)
            sensitivity = 0.3
            
            # Convert pixel delta to fraction of scroll region
            if total_w > 0:
                frac_x = (dx * sensitivity) / total_w
                new_x = max(0, min(1 - (x2 - x1), x1 - frac_x))
                self.canvas.xview_moveto(new_x)
            
            if total_h > 0:
                frac_y = (dy * sensitivity) / total_h
                new_y = max(0, min(1 - (y2 - y1), y1 - frac_y))
                self.canvas.yview_moveto(new_y)
    
    def _pan_end(self, e):
        """End middle-click pan."""
        self._pan_data = None
        self.canvas.config(cursor='')
    
    def _zoom(self, e):
        """Handle scroll wheel zoom."""
        # Get mouse position in canvas coords before zoom
        cx = self.canvas.canvasx(e.x)
        cy = self.canvas.canvasy(e.y)
        
        old_zoom = self.zoom
        
        # Zoom in/out
        if e.delta > 0:
            self.zoom = min(4.0, self.zoom * 1.2)
        else:
            self.zoom = max(0.25, self.zoom / 1.2)
        
        # Update scroll region
        scaled_size = int(TILE_SIZE * self.zoom)
        self.canvas.config(scrollregion=(0, 0, self.cols * scaled_size, self.rows * scaled_size))
        
        # Re-render at new zoom
        self._render()
        
        # Try to keep mouse position centered on same grid location
        new_cx = cx * (self.zoom / old_zoom)
        new_cy = cy * (self.zoom / old_zoom)
        
        # Scroll to keep position under mouse
        self.canvas.xview_moveto((new_cx - e.x) / (self.cols * scaled_size))
        self.canvas.yview_moveto((new_cy - e.y) / (self.rows * scaled_size))
        
        self.status.set(f"Zoom: {int(self.zoom * 100)}%")

    def _get_cell(self, event):
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        scaled_size = int(TILE_SIZE * self.zoom)
        col, row = int(x // scaled_size), int(y // scaled_size)
        if 0 <= col < self.cols and 0 <= row < self.rows:
            return row, col
        return None, None
    
    def _click(self, e):
        r, c = self._get_cell(e)
        if r is None:
            return
        
        if self.tool in ('block', 'wall', 'erase'):
            self._save_undo()  # Save before painting
            self._paint(r, c)
            self._draw_cursor(r, c)
        elif self.tool == 'fill':
            self._save_undo()  # Save before fill
            self._flood_fill(r, c)
        elif self.tool == 'eyedropper':
            self._eyedropper(r, c)
        elif self.tool in ('line', 'circle', 'rect'):
            if self.tool_start is None:
                self.tool_start = (r, c)
                self.status.set(f"Click second point for {self.tool}")
            else:
                self._save_undo()  # Save before completing shape
                self._complete_shape(r, c)
        elif self.tool == 'select':
            # Check if clicking inside existing selection to move it
            if self.selection and self._point_in_selection(r, c):
                self._start_move(r, c)
            elif self.tool_start is None and not self.moving:
                # Clear previous selection when starting a new one
                self.canvas.delete('selection')
                self.selection = None
                self.tool_start = (r, c)
                self.status.set("Drag to select area")
            elif not self.moving:
                self._complete_selection(r, c)
    
    def _drag(self, e):
        r, c = self._get_cell(e)
        if r is None:
            return
        
        if self.tool in ('block', 'wall', 'erase'):
            self._paint(r, c)
            self._draw_cursor(r, c)
        elif self.tool == 'select' and self.moving:
            self._preview_move(r, c)
        elif self.tool in ('line', 'circle', 'rect', 'select') and self.tool_start:
            self._preview_shape(r, c)
    
    def _release(self, e):
        """Handle mouse button release for drag-based tools."""
        r, c = self._get_cell(e)
        if r is None:
            return
        
        if self.tool in ('line', 'circle', 'rect') and self.tool_start:
            self._save_undo()  # Save before completing shape
            self._complete_shape(r, c)
        elif self.tool == 'select' and self.moving:
            self._save_undo()  # Save before completing move
            self._complete_move(r, c)
        elif self.tool == 'select' and self.tool_start:
            self._complete_selection(r, c)
    
    def _right_click(self, e):
        r, c = self._get_cell(e)
        if r is not None:
            self._erase(r, c)
            self._draw_cursor(r, c)
    
    def _right_drag(self, e):
        r, c = self._get_cell(e)
        if r is not None:
            self._erase(r, c)
            self._draw_cursor(r, c)
    
    def _hover(self, e):
        r, c = self._get_cell(e)
        if r is not None:
            self._draw_cursor(r, c)
    
    def _get_furniture_origin(self, row, col, tid):
        """Get top-left position for centered furniture placement."""
        if tid not in FURNITURE:
            return row, col
        info = FURNITURE[tid]
        tw, th = info[1], info[2]
        # Center the furniture on cursor
        origin_r = row - th // 2
        origin_c = col - tw // 2
        return origin_r, origin_c
    
    def _can_place_furniture(self, row, col, tid):
        """Check if furniture can be placed without overlapping other blocks."""
        if tid not in FURNITURE:
            # For regular blocks, allow placement (blocks can go on walls)
            return True
        info = FURNITURE[tid]
        tw, th = info[1], info[2]
        origin_r, origin_c = self._get_furniture_origin(row, col, tid)
        
        for fr in range(th):
            for fc in range(tw):
                nr, nc = origin_r + fr, origin_c + fc
                if not (0 <= nr < self.rows and 0 <= nc < self.cols):
                    return False
                # Check only the block layer - walls are OK to have underneath
                if self.grid[nr][nc]['block'] is not None:
                    return False
        return True
    
    def _draw_cursor(self, row, col):
        self.canvas.delete('cursor')
        self.canvas.delete('preview')
        
        scaled_size = int(TILE_SIZE * self.zoom)
        
        # For furniture, show ghost preview centered on cursor
        if self.tool == 'block' and self.block_id in FURNITURE:
            info = FURNITURE[self.block_id]
            tw, th = info[1], info[2]
            origin_r, origin_c = self._get_furniture_origin(row, col, self.block_id)
            
            # Check if placement is valid
            can_place = self._can_place_furniture(row, col, self.block_id)
            outline_color = '#00ff00' if can_place else '#ff0000'
            
            # Draw outline for each cell the furniture will occupy
            for fr in range(th):
                for fc in range(tw):
                    nr, nc = origin_r + fr, origin_c + fc
                    if 0 <= nr < self.rows and 0 <= nc < self.cols:
                        x, y = nc * scaled_size, nr * scaled_size
                        self.canvas.create_rectangle(x, y, x+scaled_size, y+scaled_size,
                                                    outline=outline_color, width=2, tags='cursor')
            
            # Draw semi-transparent preview image
            preview_img = self.cache.get_furniture(self.block_id)
            if preview_img:
                # Create semi-transparent version
                preview = preview_img.copy()
                alpha = preview.split()[3]
                alpha = alpha.point(lambda p: p * 0.5)  # 50% opacity
                preview.putalpha(alpha)
                if self.zoom != 1.0:
                    new_size = (int(preview.width * self.zoom), int(preview.height * self.zoom))
                    preview = preview.resize(new_size, Image.NEAREST)
                photo = ImageTk.PhotoImage(preview)
                self.photos['preview'] = photo
                px, py = origin_c * scaled_size, origin_r * scaled_size
                self.canvas.create_image(px, py, anchor=tk.NW, image=photo, tags='preview')
        
        elif self.tool == 'block':
            # Show ghost preview for regular blocks too
            half = self.brush // 2
            for dr in range(-half, self.brush - half):
                for dc in range(-half, self.brush - half):
                    r, c = row + dr, col + dc
                    if 0 <= r < self.rows and 0 <= c < self.cols:
                        x, y = c * scaled_size, r * scaled_size
                        # Draw green outline
                        self.canvas.create_rectangle(x, y, x+scaled_size, y+scaled_size,
                                                    outline='#00ff00', width=1, tags='cursor')
                        # Draw preview tile
                        preview_img = self.cache.get_block(self.block_id, {'n': False, 's': False, 'e': False, 'w': False})
                        if preview_img:
                            preview = preview_img.copy()
                            alpha = preview.split()[3]
                            alpha = alpha.point(lambda p: int(p * 0.5))
                            preview.putalpha(alpha)
                            if self.zoom != 1.0:
                                new_size = (int(preview.width * self.zoom), int(preview.height * self.zoom))
                                preview = preview.resize(new_size, Image.NEAREST)
                            photo = ImageTk.PhotoImage(preview)
                            self.photos[('preview', r, c)] = photo
                            self.canvas.create_image(x, y, anchor=tk.NW, image=photo, tags='preview')
        
        elif self.tool == 'wall':
            # Show ghost preview for walls
            half = self.brush // 2
            for dr in range(-half, self.brush - half):
                for dc in range(-half, self.brush - half):
                    r, c = row + dr, col + dc
                    if 0 <= r < self.rows and 0 <= c < self.cols:
                        x, y = c * scaled_size, r * scaled_size
                        self.canvas.create_rectangle(x, y, x+scaled_size, y+scaled_size,
                                                    outline='#4488ff', width=1, tags='cursor')
                        preview_img = self.cache.get_wall(self.wall_id)
                        if preview_img:
                            preview = preview_img.copy()
                            alpha = preview.split()[3]
                            alpha = alpha.point(lambda p: int(p * 0.5))
                            preview.putalpha(alpha)
                            if self.zoom != 1.0:
                                new_size = (int(preview.width * self.zoom), int(preview.height * self.zoom))
                                preview = preview.resize(new_size, Image.NEAREST)
                            photo = ImageTk.PhotoImage(preview)
                            self.photos[('preview', r, c)] = photo
                            self.canvas.create_image(x, y, anchor=tk.NW, image=photo, tags='preview')
        
        else:
            # Erase cursor - color depends on erase type
            if self.tool == 'erase_block':
                outline_color = '#ff8844'  # Orange for block erase
            elif self.tool == 'erase_wall':
                outline_color = '#8844ff'  # Purple for wall erase
            else:
                outline_color = '#ff4444'  # Red for full erase
            
            half = self.brush // 2
            for dr in range(-half, self.brush - half):
                for dc in range(-half, self.brush - half):
                    r, c = row + dr, col + dc
                    if 0 <= r < self.rows and 0 <= c < self.cols:
                        x, y = c * scaled_size, r * scaled_size
                        self.canvas.create_rectangle(x+1, y+1, x+scaled_size-1, y+scaled_size-1,
                                                    outline=outline_color, width=1, tags='cursor')
    
    def _paint(self, row, col):
        half = self.brush // 2
        affected = set()
        
        # Handle erase tools in paint
        if self.tool in ('erase', 'erase_block', 'erase_wall'):
            self._erase(row, col)
            return
        
        # For furniture, only place once (not per brush cell) and check overlap
        if self.tool == 'block' and self.block_id in FURNITURE:
            if not self._can_place_furniture(row, col, self.block_id):
                return  # Can't place here - blocked by another block (walls are OK)
            
            info = FURNITURE[self.block_id]
            tw, th = info[1], info[2]
            origin_r, origin_c = self._get_furniture_origin(row, col, self.block_id)
            
            for fr in range(th):
                for fc in range(tw):
                    nr, nc = origin_r + fr, origin_c + fc
                    if 0 <= nr < self.rows and 0 <= nc < self.cols:
                        # Place furniture in block layer, keep wall layer intact
                        self.grid[nr][nc]['block'] = ('furn', self.block_id, fc, fr)
                        affected.add((nr, nc))
            
            for r, c in affected:
                self._render_cell(r, c)
            return
        
        # Normal block/wall painting
        for dr in range(-half, self.brush - half):
            for dc in range(-half, self.brush - half):
                r, c = row + dr, col + dc
                if 0 <= r < self.rows and 0 <= c < self.cols:
                    if self.tool == 'block':
                        # Blocks go in block layer, wall layer stays intact
                        self.grid[r][c]['block'] = ('block', self.block_id)
                    elif self.tool == 'wall':
                        # Walls go in wall layer, block layer stays intact
                        self.grid[r][c]['wall'] = self.wall_id
                    
                    for nr in range(r-1, r+2):
                        for nc in range(c-1, c+2):
                            if 0 <= nr < self.rows and 0 <= nc < self.cols:
                                affected.add((nr, nc))
        
        for r, c in affected:
            self._render_cell(r, c)
    
    def _erase(self, row, col):
        half = self.brush // 2
        affected = set()
        
        for dr in range(-half, self.brush - half):
            for dc in range(-half, self.brush - half):
                r, c = row + dr, col + dc
                if 0 <= r < self.rows and 0 <= c < self.cols:
                    if self.tool == 'erase':
                        # Erase both layers
                        self.grid[r][c]['wall'] = None
                        self.grid[r][c]['block'] = None
                    elif self.tool == 'erase_block':
                        # Erase only block layer
                        self.grid[r][c]['block'] = None
                    elif self.tool == 'erase_wall':
                        # Erase only wall layer
                        self.grid[r][c]['wall'] = None
                    
                    for nr in range(r-1, r+2):
                        for nc in range(c-1, c+2):
                            if 0 <= nr < self.rows and 0 <= nc < self.cols:
                                affected.add((nr, nc))
        
        for r, c in affected:
            self._render_cell(r, c)
    
    def _flood_fill(self, row, col):
        """Flood fill tool - fills connected area with same tile."""
        # Get target cell value
        cell = self.grid[row][col]
        
        if self.layer == 'block':
            target = cell['block']
            # Fill with current block
            fill_value = ('block', self.block_id) if self.block_id not in FURNITURE else None
        else:
            target = cell['wall']
            fill_value = self.wall_id
        
        if fill_value is None:
            self.status.set("Cannot flood fill with furniture")
            return
        
        # BFS flood fill
        visited = set()
        queue = [(row, col)]
        affected = set()
        
        while queue and len(visited) < 10000:  # Limit to prevent hanging
            r, c = queue.pop(0)
            if (r, c) in visited:
                continue
            if not (0 <= r < self.rows and 0 <= c < self.cols):
                continue
            
            cell = self.grid[r][c]
            current = cell['block'] if self.layer == 'block' else cell['wall']
            
            if current != target:
                continue
            
            visited.add((r, c))
            
            # Fill this cell
            if self.layer == 'block':
                self.grid[r][c]['block'] = fill_value
            else:
                self.grid[r][c]['wall'] = fill_value
            
            affected.add((r, c))
            
            # Add neighbors
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                queue.append((r + dr, c + dc))
        
        # Re-render affected cells and neighbors
        to_render = set()
        for r, c in affected:
            for dr in range(-1, 2):
                for dc in range(-1, 2):
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < self.rows and 0 <= nc < self.cols:
                        to_render.add((nr, nc))
        
        for r, c in to_render:
            self._render_cell(r, c)
        
        self.status.set(f"Filled {len(affected)} cells")
    
    def _preview_shape(self, end_row, end_col):
        """Show preview of line or circle being drawn."""
        self.canvas.delete('tool_preview')
        
        if not self.tool_start:
            return
        
        start_r, start_c = self.tool_start
        scaled_size = int(TILE_SIZE * self.zoom)
        
        if self.tool == 'line':
            points = self._get_line_points(start_r, start_c, end_row, end_col)
        elif self.tool == 'circle':
            points = self._get_circle_points(start_r, start_c, end_row, end_col)
        elif self.tool == 'rect':
            points = self._get_rect_points(start_r, start_c, end_row, end_col)
        elif self.tool == 'select':
            # Draw selection rectangle
            r1, r2 = min(start_r, end_row), max(start_r, end_row)
            c1, c2 = min(start_c, end_col), max(start_c, end_col)
            x1, y1 = c1 * scaled_size, r1 * scaled_size
            x2, y2 = (c2 + 1) * scaled_size, (r2 + 1) * scaled_size
            self.canvas.create_rectangle(x1, y1, x2, y2, 
                                         outline='#7aa2f7', width=2, 
                                         dash=(4, 4), tags='tool_preview')
            return
        else:
            return
        
        # Draw preview points
        for r, c in points:
            if 0 <= r < self.rows and 0 <= c < self.cols:
                x, y = c * scaled_size, r * scaled_size
                self.canvas.create_rectangle(x, y, x + scaled_size, y + scaled_size,
                                            outline='#7aa2f7', width=1, tags='tool_preview')
    
    def _complete_shape(self, end_row, end_col):
        """Complete drawing a line or circle."""
        if not self.tool_start:
            return
        
        start_r, start_c = self.tool_start
        
        if self.tool == 'line':
            points = self._get_line_points(start_r, start_c, end_row, end_col)
        elif self.tool == 'circle':
            points = self._get_circle_points(start_r, start_c, end_row, end_col)
        elif self.tool == 'rect':
            points = self._get_rect_points(start_r, start_c, end_row, end_col)
        else:
            points = []
        
        # Apply points to grid
        affected = set()
        for r, c in points:
            if 0 <= r < self.rows and 0 <= c < self.cols:
                if self.layer == 'block':
                    if self.block_id not in FURNITURE:
                        self.grid[r][c]['block'] = ('block', self.block_id)
                else:
                    self.grid[r][c]['wall'] = self.wall_id
                affected.add((r, c))
        
        # Re-render
        to_render = set()
        for r, c in affected:
            for dr in range(-1, 2):
                for dc in range(-1, 2):
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < self.rows and 0 <= nc < self.cols:
                        to_render.add((nr, nc))
        
        for r, c in to_render:
            self._render_cell(r, c)
        
        # Reset tool state
        self.tool_start = None
        self.canvas.delete('tool_preview')
        self.status.set(f"Drew {self.tool} with {len(affected)} cells")
    
    def _get_line_points(self, r1, c1, r2, c2):
        """Get points along a line using Bresenham's algorithm."""
        points = []
        
        dr = abs(r2 - r1)
        dc = abs(c2 - c1)
        sr = 1 if r1 < r2 else -1
        sc = 1 if c1 < c2 else -1
        err = dc - dr
        
        r, c = r1, c1
        
        while True:
            points.append((r, c))
            
            if r == r2 and c == c2:
                break
            
            e2 = 2 * err
            if e2 > -dr:
                err -= dr
                c += sc
            if e2 < dc:
                err += dc
                r += sr
        
        # If fill_shape is True, fill the line with brush width
        if self.fill_shape and self.brush > 1:
            expanded = set()
            half = self.brush // 2
            for r, c in points:
                for dr in range(-half, self.brush - half):
                    for dc in range(-half, self.brush - half):
                        expanded.add((r + dr, c + dc))
            return list(expanded)
        
        return points
    
    def _get_circle_points(self, r1, c1, r2, c2):
        """Get points for a circle/ellipse."""
        # Calculate center and radii
        center_r = (r1 + r2) // 2
        center_c = (c1 + c2) // 2
        radius_r = abs(r2 - r1) // 2
        radius_c = abs(c2 - c1) // 2
        
        if radius_r == 0 and radius_c == 0:
            return [(center_r, center_c)]
        
        points = set()
        
        # Midpoint ellipse algorithm
        if radius_r == 0:
            radius_r = 1
        if radius_c == 0:
            radius_c = 1
        
        # Draw ellipse outline
        for angle in range(360):
            import math
            rad = math.radians(angle)
            pr = int(center_r + radius_r * math.sin(rad))
            pc = int(center_c + radius_c * math.cos(rad))
            points.add((pr, pc))
        
        # If fill_shape, fill the interior
        if self.fill_shape:
            filled = set()
            for r in range(center_r - radius_r, center_r + radius_r + 1):
                for c in range(center_c - radius_c, center_c + radius_c + 1):
                    # Check if point is inside ellipse
                    if radius_r > 0 and radius_c > 0:
                        dr = (r - center_r) / radius_r
                        dc = (c - center_c) / radius_c
                        if dr * dr + dc * dc <= 1:
                            filled.add((r, c))
            return list(filled)
        
        return list(points)
    
    def _complete_selection(self, end_row, end_col):
        """Complete a selection rectangle."""
        if not self.tool_start:
            return
        
        start_r, start_c = self.tool_start
        r1, r2 = min(start_r, end_row), max(start_r, end_row)
        c1, c2 = min(start_c, end_col), max(start_c, end_col)
        
        self.selection = {'r1': r1, 'c1': c1, 'r2': r2, 'c2': c2}
        self.tool_start = None
        self.canvas.delete('tool_preview')
        
        # Draw persistent selection rectangle
        scaled_size = int(TILE_SIZE * self.zoom)
        x1, y1 = c1 * scaled_size, r1 * scaled_size
        x2, y2 = (c2 + 1) * scaled_size, (r2 + 1) * scaled_size
        self.canvas.create_rectangle(x1, y1, x2, y2, 
                                     outline='#7aa2f7', width=2,
                                     dash=(4, 4), tags='selection')
        
        width = c2 - c1 + 1
        height = r2 - r1 + 1
        self.status.set(f"Selected {width}x{height} area (Drag inside to move, Ctrl+C/V, Del)")
    
    def _copy_selection(self):
        """Copy selected area to clipboard."""
        if not self.selection:
            self.status.set("No selection to copy")
            return
        
        sel = self.selection
        self.clipboard = []
        
        for r in range(sel['r1'], sel['r2'] + 1):
            row_data = []
            for c in range(sel['c1'], sel['c2'] + 1):
                row_data.append(self.grid[r][c].copy())
            self.clipboard.append(row_data)
        
        self.status.set(f"Copied {sel['r2']-sel['r1']+1}x{sel['c2']-sel['c1']+1} area")
    
    def _paste_selection(self):
        """Paste clipboard at current selection or cursor."""
        if not self.clipboard:
            self.status.set("Nothing to paste")
            return
        
        # Paste at selection origin or (0, 0)
        start_r = self.selection['r1'] if self.selection else 0
        start_c = self.selection['c1'] if self.selection else 0
        
        affected = set()
        for dr, row_data in enumerate(self.clipboard):
            for dc, cell_data in enumerate(row_data):
                r, c = start_r + dr, start_c + dc
                if 0 <= r < self.rows and 0 <= c < self.cols:
                    self.grid[r][c] = cell_data.copy()
                    affected.add((r, c))
        
        # Re-render
        to_render = set()
        for r, c in affected:
            for dr in range(-1, 2):
                for dc in range(-1, 2):
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < self.rows and 0 <= nc < self.cols:
                        to_render.add((nr, nc))
        
        for r, c in to_render:
            self._render_cell(r, c)
        
        self.status.set(f"Pasted {len(self.clipboard)}x{len(self.clipboard[0])} area")
    
    def _delete_selection(self):
        """Delete selected area."""
        if not self.selection:
            self.status.set("No selection to delete")
            return
        
        sel = self.selection
        affected = set()
        
        for r in range(sel['r1'], sel['r2'] + 1):
            for c in range(sel['c1'], sel['c2'] + 1):
                self.grid[r][c] = {'wall': None, 'block': None}
                affected.add((r, c))
        
        # Re-render
        for r, c in affected:
            self._render_cell(r, c)
        
        self.canvas.delete('selection')
        self.selection = None
        self.status.set(f"Deleted selection")
    
    def _point_in_selection(self, row, col):
        """Check if a point is inside the current selection."""
        if not self.selection:
            return False
        sel = self.selection
        return sel['r1'] <= row <= sel['r2'] and sel['c1'] <= col <= sel['c2']
    
    def _start_move(self, row, col):
        """Start moving the selected area."""
        if not self.selection:
            return
        
        sel = self.selection
        self.moving = True
        self.move_start = (row, col)
        
        # Copy the selected data
        self.move_data = []
        for r in range(sel['r1'], sel['r2'] + 1):
            row_data = []
            for c in range(sel['c1'], sel['c2'] + 1):
                row_data.append(self.grid[r][c].copy())
            self.move_data.append(row_data)
        
        # Clear the original area
        for r in range(sel['r1'], sel['r2'] + 1):
            for c in range(sel['c1'], sel['c2'] + 1):
                self.grid[r][c] = {'wall': None, 'block': None}
                self._render_cell(r, c)
        
        self.status.set("Drag to move selection")
    
    def _preview_move(self, row, col):
        """Preview where the selection will be moved to."""
        if not self.moving or not self.move_start or not self.selection or not self.move_data:
            return
        
        self.canvas.delete('move_preview')
        self.canvas.delete('selection')
        
        # Calculate offset
        start_r, start_c = self.move_start
        dr = row - start_r
        dc = col - start_c
        
        sel = self.selection
        new_r1 = sel['r1'] + dr
        new_c1 = sel['c1'] + dc
        new_r2 = sel['r2'] + dr
        new_c2 = sel['c2'] + dc
        
        scaled_size = int(TILE_SIZE * self.zoom)
        
        # Draw the actual blocks being moved as a preview
        for ri, row_data in enumerate(self.move_data):
            for ci, cell_data in enumerate(row_data):
                r, c = new_r1 + ri, new_c1 + ci
                if 0 <= r < self.rows and 0 <= c < self.cols:
                    x, y = c * scaled_size, r * scaled_size
                    
                    # Get wall image
                    wall_img = None
                    if cell_data['wall']:
                        wall_img = self.cache.get_wall(cell_data['wall'])
                    
                    # Get block image
                    block_img = None
                    if cell_data['block']:
                        if cell_data['block'][0] == 'block':
                            block_img = self.cache.get_block(cell_data['block'][1], {'n': False, 's': False, 'e': False, 'w': False})
                        elif cell_data['block'][0] == 'furn' and cell_data['block'][2] == 0 and cell_data['block'][3] == 0:
                            block_img = self.cache.get_furniture(cell_data['block'][1])
                    
                    # Composite and render
                    if wall_img or block_img:
                        if wall_img and block_img:
                            img = self._composite_layers(wall_img, block_img)
                        elif wall_img:
                            img = wall_img
                        else:
                            img = block_img
                        
                        # Make semi-transparent
                        if img:
                            img = img.copy()
                            if img.mode != 'RGBA':
                                img = img.convert('RGBA')
                            alpha = img.split()[3]
                            alpha = alpha.point(lambda p: int(p * 0.7))
                            img.putalpha(alpha)
                            
                            if self.zoom != 1.0:
                                new_size = (int(img.width * self.zoom), int(img.height * self.zoom))
                                img = img.resize(new_size, Image.NEAREST)
                            
                            photo = ImageTk.PhotoImage(img)
                            self.photos[('move_preview', ri, ci)] = photo
                            self.canvas.create_image(x, y, anchor=tk.NW, image=photo, tags='move_preview')
        
        # Draw outline rectangle
        x1 = new_c1 * scaled_size
        y1 = new_r1 * scaled_size
        x2 = (new_c2 + 1) * scaled_size
        y2 = (new_r2 + 1) * scaled_size
        
        self.canvas.create_rectangle(x1, y1, x2, y2,
                                     outline='#f7768e', width=2,
                                     dash=(4, 4), tags='move_preview')
    
    def _complete_move(self, row, col):
        """Complete moving the selection."""
        if not self.moving or not self.move_start or not self.selection or not self.move_data:
            self.moving = False
            return
        
        # Calculate offset
        start_r, start_c = self.move_start
        dr = row - start_r
        dc = col - start_c
        
        sel = self.selection
        new_r1 = sel['r1'] + dr
        new_c1 = sel['c1'] + dc
        
        # Place the data at new position
        affected = set()
        for ri, row_data in enumerate(self.move_data):
            for ci, cell_data in enumerate(row_data):
                r, c = new_r1 + ri, new_c1 + ci
                if 0 <= r < self.rows and 0 <= c < self.cols:
                    self.grid[r][c] = cell_data.copy()
                    affected.add((r, c))
        
        # Re-render affected cells and neighbors
        to_render = set()
        for r, c in affected:
            for ddr in range(-1, 2):
                for ddc in range(-1, 2):
                    nr, nc = r + ddr, c + ddc
                    if 0 <= nr < self.rows and 0 <= nc < self.cols:
                        to_render.add((nr, nc))
        
        for r, c in to_render:
            self._render_cell(r, c)
        
        # Update selection to new position
        self.selection = {
            'r1': new_r1, 'c1': new_c1,
            'r2': new_r1 + len(self.move_data) - 1,
            'c2': new_c1 + len(self.move_data[0]) - 1
        }
        
        # Draw new selection rectangle
        self.canvas.delete('move_preview')
        scaled_size = int(TILE_SIZE * self.zoom)
        x1 = self.selection['c1'] * scaled_size
        y1 = self.selection['r1'] * scaled_size
        x2 = (self.selection['c2'] + 1) * scaled_size
        y2 = (self.selection['r2'] + 1) * scaled_size
        self.canvas.create_rectangle(x1, y1, x2, y2,
                                     outline='#7aa2f7', width=2,
                                     dash=(4, 4), tags='selection')
        
        # Reset move state
        self.moving = False
        self.move_start = None
        self.move_data = None
        
        self.status.set(f"Moved selection by ({dc}, {dr})")
    
    def _get_neighbors(self, row, col, layer):
        """Get neighbors for auto-tiling. layer is 'block' or 'wall'."""
        def check(r, c):
            if 0 <= r < self.rows and 0 <= c < self.cols:
                if layer == 'block':
                    cell = self.grid[r][c]['block']
                    return cell is not None and cell[0] == 'block'
                elif layer == 'wall':
                    return self.grid[r][c]['wall'] is not None
            return False
        return {'n': check(row-1, col), 's': check(row+1, col),
                'e': check(row, col+1), 'w': check(row, col-1)}
    
    def _composite_on_bg(self, img):
        """Composite an image onto solid background to remove transparency."""
        bg = Image.new('RGB', img.size, (17, 17, 27))  # Match canvas bg #11111b
        if img.mode == 'RGBA':
            bg.paste(img, (0, 0), img)
        else:
            bg.paste(img, (0, 0))
        return bg
    
    def _composite_layers(self, wall_img, block_img):
        """Composite block image on top of wall image."""
        if wall_img is None:
            return block_img
        if block_img is None:
            return wall_img
        
        # Start with wall as base
        result = wall_img.copy()
        if result.mode != 'RGBA':
            result = result.convert('RGBA')
        
        # Paste block on top
        if block_img.mode == 'RGBA':
            result.paste(block_img, (0, 0), block_img)
        else:
            result.paste(block_img, (0, 0))
        
        return result
    
    def _render_cell(self, row, col):
        scaled_size = int(TILE_SIZE * self.zoom)
        x, y = col * scaled_size, row * scaled_size
        self.canvas.delete(f'c_{row}_{col}')
        
        cell = self.grid[row][col]
        wall_id = cell['wall']
        block_data = cell['block']
        
        if not wall_id and not block_data:
            return
        
        # Get wall image
        wall_img = None
        if wall_id:
            wall_img = self.cache.get_wall(wall_id)
        
        # Get block/furniture image
        block_img = None
        if block_data:
            if block_data[0] == 'block':
                neighbors = self._get_neighbors(row, col, 'block')
                block_img = self.cache.get_block(block_data[1], neighbors)
            elif block_data[0] == 'furn':
                tid, fx, fy = block_data[1], block_data[2], block_data[3]
                if fx == 0 and fy == 0:
                    # Render full furniture from top-left
                    furn_img = self.cache.get_furniture(tid)
                    if furn_img:
                        # Handle wall underneath furniture
                        if wall_img:
                            # Create composite with wall as background for entire furniture
                            info = FURNITURE.get(tid)
                            if info:
                                tw, th = info[1], info[2]
                                # Create background from walls under entire furniture
                                bg = Image.new('RGBA', (tw * 16, th * 16), (17, 17, 27, 255))
                                for fr in range(th):
                                    for fc in range(tw):
                                        nr, nc = row + fr, col + fc
                                        if 0 <= nr < self.rows and 0 <= nc < self.cols:
                                            wcell = self.grid[nr][nc]['wall']
                                            if wcell:
                                                wtile = self.cache.get_wall(wcell)
                                                if wtile:
                                                    bg.paste(wtile, (fc * 16, fr * 16), wtile)
                                # Composite furniture on top of wall background
                                bg.paste(furn_img, (0, 0), furn_img)
                                img = bg
                            else:
                                img = furn_img
                        else:
                            img = self._composite_on_bg(furn_img)
                        
                        # Scale for zoom
                        if self.zoom != 1.0:
                            new_size = (int(img.width * self.zoom), int(img.height * self.zoom))
                            img = img.resize(new_size, Image.NEAREST)
                        photo = ImageTk.PhotoImage(img)
                        self.photos[(row, col)] = photo
                        self.canvas.create_image(x, y, anchor=tk.NW, image=photo, tags=f'c_{row}_{col}')
                        return
                else:
                    # Non-origin furniture cell - don't render (origin handles it)
                    # But we may need to render the wall underneath
                    if wall_img:
                        img = self._composite_on_bg(wall_img)
                        if self.zoom != 1.0:
                            new_size = (int(img.width * self.zoom), int(img.height * self.zoom))
                            img = img.resize(new_size, Image.NEAREST)
                        photo = ImageTk.PhotoImage(img)
                        self.photos[(row, col)] = photo
                        self.canvas.create_image(x, y, anchor=tk.NW, image=photo, tags=f'c_{row}_{col}')
                    return
        
        # Composite wall and block
        if wall_img and block_img:
            img = self._composite_layers(wall_img, block_img)
        elif wall_img:
            img = wall_img
        elif block_img:
            img = block_img
        else:
            return
        
        # Composite onto solid background
        img = self._composite_on_bg(img)
        
        # Scale for zoom
        if self.zoom != 1.0:
            new_size = (int(img.width * self.zoom), int(img.height * self.zoom))
            img = img.resize(new_size, Image.NEAREST)
        
        photo = ImageTk.PhotoImage(img)
        self.photos[(row, col)] = photo
        self.canvas.create_image(x, y, anchor=tk.NW, image=photo, tags=f'c_{row}_{col}')
    
    def _render(self):
        self.canvas.delete('all')
        self.photos.clear()
        
        scaled_size = int(TILE_SIZE * self.zoom)
        w, h = self.cols * scaled_size, self.rows * scaled_size
        
        # Update scroll region
        self.canvas.config(scrollregion=(0, 0, w, h))
        
        # Draw background - darker for contrast
        self.canvas.create_rectangle(0, 0, w, h, fill='#11111b', outline='', tags='bg')
        
        # Draw subtle grid lines
        grid_color = '#1e1e2e'
        for r in range(self.rows + 1):
            y = r * scaled_size
            self.canvas.create_line(0, y, w, y, fill=grid_color, tags='grid')
        for c in range(self.cols + 1):
            x = c * scaled_size
            self.canvas.create_line(x, 0, x, h, fill=grid_color, tags='grid')
        
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.grid[r][c]
                if cell['wall'] or cell['block']:
                    self._render_cell(r, c)
    
    # =========== UNDO/REDO SYSTEM ===========
    
    def _save_undo(self):
        """Save current grid state to undo stack."""
        # Deep copy the grid
        state = [[cell.copy() for cell in row] for row in self.grid]
        self.undo_stack.append(state)
        
        # Limit stack size
        if len(self.undo_stack) > self.max_undo:
            self.undo_stack.pop(0)
        
        # Clear redo stack on new action
        self.redo_stack.clear()
    
    def _undo(self):
        """Undo last action."""
        if not self.undo_stack:
            self.status.set("Nothing to undo")
            return
        
        # Save current state to redo
        current = [[cell.copy() for cell in row] for row in self.grid]
        self.redo_stack.append(current)
        
        # Restore previous state
        self.grid = self.undo_stack.pop()
        self._render()
        self.status.set(f"Undo ({len(self.undo_stack)} left)")
    
    def _redo(self):
        """Redo last undone action."""
        if not self.redo_stack:
            self.status.set("Nothing to redo")
            return
        
        # Save current to undo
        current = [[cell.copy() for cell in row] for row in self.grid]
        self.undo_stack.append(current)
        
        # Restore redo state
        self.grid = self.redo_stack.pop()
        self._render()
        self.status.set(f"Redo ({len(self.redo_stack)} left)")
    
    # =========== PROJECT SAVE/LOAD ===========
    
    def _save_project(self):
        """Save project to .tpaint file."""
        import json
        
        path = filedialog.asksaveasfilename(
            defaultextension=".tpaint",
            filetypes=[("TPaint Project", "*.tpaint"), ("All Files", "*.*")],
            initialfile=os.path.basename(self.project_path) if self.project_path else "untitled.tpaint"
        )
        
        if not path:
            return
        
        # Build project data
        project = {
            'version': '1.0',
            'cols': self.cols,
            'rows': self.rows,
            'grid': []
        }
        
        # Serialize grid - only non-empty cells to save space
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.grid[r][c]
                if cell['wall'] or cell['block']:
                    entry = {'r': r, 'c': c}
                    if cell['wall']:
                        entry['wall'] = cell['wall']
                    if cell['block']:
                        entry['block'] = list(cell['block'])  # Convert tuple to list for JSON
                    project['grid'].append(entry)
        
        try:
            with open(path, 'w') as f:
                json.dump(project, f)
            self.project_path = path
            self.status.set(f"Project saved: {os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save project:\n{e}")
    
    def _load_project(self):
        """Load project from .tpaint file."""
        import json
        
        path = filedialog.askopenfilename(
            filetypes=[("TPaint Project", "*.tpaint"), ("All Files", "*.*")]
        )
        
        if not path:
            return
        
        try:
            with open(path, 'r') as f:
                project = json.load(f)
            
            # Save undo before loading
            self._save_undo()
            
            # Resize if needed
            new_cols = project.get('cols', 64)
            new_rows = project.get('rows', 40)
            
            if new_cols != self.cols or new_rows != self.rows:
                self.cols, self.rows = new_cols, new_rows
                self.grid = [[{'wall': None, 'block': None} for _ in range(self.cols)] for _ in range(self.rows)]
            else:
                # Clear existing grid
                for r in range(self.rows):
                    for c in range(self.cols):
                        self.grid[r][c] = {'wall': None, 'block': None}
            
            # Load grid data
            for entry in project.get('grid', []):
                r, c = entry['r'], entry['c']
                if 0 <= r < self.rows and 0 <= c < self.cols:
                    if 'wall' in entry:
                        self.grid[r][c]['wall'] = entry['wall']
                    if 'block' in entry:
                        self.grid[r][c]['block'] = tuple(entry['block'])
            
            self.project_path = path
            self._render()
            self.status.set(f"Loaded: {os.path.basename(path)}")
            
        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load project:\n{e}")
    
    def _new_canvas(self):
        """Create new canvas with custom size."""
        # Create dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("New Canvas")
        dialog.geometry("300x180")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - 300) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - 180) // 2
        dialog.geometry(f"+{x}+{y}")
        
        bg = self.colors['bg_mid']
        fg = self.colors['text']
        dialog.configure(bg=bg)
        
        tk.Label(dialog, text="Canvas Size", font=('Segoe UI', 12, 'bold'), bg=bg, fg=fg).pack(pady=10)
        
        size_frame = tk.Frame(dialog, bg=bg)
        size_frame.pack(pady=10)
        
        tk.Label(size_frame, text="Width:", bg=bg, fg=fg).grid(row=0, column=0, padx=5, pady=5)
        width_var = tk.StringVar(value=str(self.cols))
        width_entry = ttk.Entry(size_frame, textvariable=width_var, width=10)
        width_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(size_frame, text="Height:", bg=bg, fg=fg).grid(row=1, column=0, padx=5, pady=5)
        height_var = tk.StringVar(value=str(self.rows))
        height_entry = ttk.Entry(size_frame, textvariable=height_var, width=10)
        height_entry.grid(row=1, column=1, padx=5, pady=5)
        
        def create():
            try:
                new_cols = int(width_var.get())
                new_rows = int(height_var.get())
                if new_cols < 1 or new_rows < 1 or new_cols > 500 or new_rows > 500:
                    messagebox.showerror("Invalid Size", "Size must be between 1 and 500")
                    return
                
                self._save_undo()
                self.cols, self.rows = new_cols, new_rows
                self.grid = [[{'wall': None, 'block': None} for _ in range(self.cols)] for _ in range(self.rows)]
                self.project_path = None
                self._render()
                self.status.set(f"New canvas: {new_cols}x{new_rows}")
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter valid numbers")
        
        btn_frame = tk.Frame(dialog, bg=bg)
        btn_frame.pack(pady=15)
        
        tk.Button(btn_frame, text="Create", command=create,
                 bg=self.colors['accent'], fg='white', padx=20, pady=5).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Cancel", command=dialog.destroy,
                 bg=self.colors['bg_light'], fg=fg, padx=20, pady=5).pack(side=tk.LEFT, padx=5)
    
    def _import_reference(self):
        """Import an image as a background reference."""
        path = filedialog.askopenfilename(
            filetypes=[("Images", "*.png *.jpg *.jpeg *.gif *.bmp"), ("All Files", "*.*")]
        )
        
        if not path:
            return
        
        try:
            img = Image.open(path).convert('RGBA')
            
            # Scale to fit canvas
            canvas_w = self.cols * TILE_SIZE
            canvas_h = self.rows * TILE_SIZE
            
            # Maintain aspect ratio
            scale = min(canvas_w / img.width, canvas_h / img.height)
            new_w = int(img.width * scale)
            new_h = int(img.height * scale)
            
            self.reference_image = img.resize((new_w, new_h), Image.LANCZOS)
            self.show_reference = True
            self._render()
            self.status.set(f"Reference loaded: {os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to load image:\n{e}")
    
    def _toggle_reference(self):
        """Toggle reference image visibility."""
        if self.reference_image:
            self.show_reference = not self.show_reference
            self._render()
            self.status.set(f"Reference {'shown' if self.show_reference else 'hidden'}")
        else:
            self.status.set("No reference image loaded")
    
    # =========== EYEDROPPER TOOL ===========
    
    def _eyedropper(self, row, col):
        """Pick tile/wall from canvas at position."""
        if 0 <= row < self.rows and 0 <= col < self.cols:
            cell = self.grid[row][col]
            
            # Check block layer first
            if cell['block']:
                block_data = cell['block']
                if block_data[0] == 'block':
                    self.block_id = block_data[1]
                    name = self.cache.tile_info.get(self.block_id, {}).get('name', f'Tile {self.block_id}')
                    self.status.set(f"Picked block: {name}")
                    self._set_tool('block')
                elif block_data[0] == 'furn':
                    self.block_id = block_data[1]
                    name = self.cache.furniture_info.get(self.block_id, {}).get('name', f'Furniture {self.block_id}')
                    self.status.set(f"Picked furniture: {name}")
                    self._set_tool('block')
                return
            
            # Otherwise check wall layer
            if cell['wall']:
                self.wall_id = cell['wall']
                name = self.cache.wall_info.get(self.wall_id, {}).get('name', f'Wall {self.wall_id}')
                self.status.set(f"Picked wall: {name}")
                self._set_tool('wall')
                return
            
            self.status.set("Empty cell - nothing to pick")
    
    # =========== RECTANGLE TOOL ===========
    
    def _get_rect_points(self, r1, c1, r2, c2):
        """Get all points for a rectangle (outline or filled)."""
        points = []
        min_r, max_r = min(r1, r2), max(r1, r2)
        min_c, max_c = min(c1, c2), max(c1, c2)
        
        if self.fill_shape:
            # Filled rectangle
            for r in range(min_r, max_r + 1):
                for c in range(min_c, max_c + 1):
                    points.append((r, c))
        else:
            # Outline only
            for c in range(min_c, max_c + 1):
                points.append((min_r, c))
                points.append((max_r, c))
            for r in range(min_r + 1, max_r):
                points.append((r, min_c))
                points.append((r, max_c))
        
        return points
    
    def _clear(self):
        self._save_undo()  # Save before clearing
        self.grid = [[{'wall': None, 'block': None} for _ in range(self.cols)] for _ in range(self.rows)]
        self._render()
        self.status.set("Cleared!")
    
    def _save(self):
        """Export dialog with format options."""
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("PNG Image", "*.png"),
                ("TPaint Project", "*.tpaint"),
                ("TEdit Schematic", "*.TEditSch"),
            ]
        )
        if not path:
            return
        
        ext = os.path.splitext(path)[1].lower()
        
        if ext == '.tpaint':
            self._export_tpaint(path)
        elif ext == '.teditsch':
            self._export_tedit(path)
        else:  # Default to PNG
            self._export_png(path)
    
    def _export_png(self, path):
        """Export as PNG image."""
        img = Image.new('RGBA', (self.cols*TILE_SIZE, self.rows*TILE_SIZE), (10,10,26,255))
        
        # First pass: render all walls
        for r in range(self.rows):
            for c in range(self.cols):
                wall_id = self.grid[r][c]['wall']
                if wall_id:
                    tile = self.cache.get_wall(wall_id)
                    if tile:
                        img.paste(tile, (c*TILE_SIZE, r*TILE_SIZE), tile)
        
        # Second pass: render all blocks/furniture on top
        for r in range(self.rows):
            for c in range(self.cols):
                block_data = self.grid[r][c]['block']
                if block_data:
                    tile = None
                    if block_data[0] == 'block':
                        neighbors = self._get_neighbors(r, c, 'block')
                        tile = self.cache.get_block(block_data[1], neighbors)
                    elif block_data[0] == 'furn' and block_data[2] == 0 and block_data[3] == 0:
                        tile = self.cache.get_furniture(block_data[1])
                    
                    if tile:
                        img.paste(tile, (c*TILE_SIZE, r*TILE_SIZE), tile)
        
        img.save(path)
        self.status.set(f"Exported PNG: {os.path.basename(path)}")
        messagebox.showinfo("Export", "PNG image saved!")
    
    def _export_tpaint(self, path):
        """Export as TPaint project file."""
        import json
        
        project = {
            'version': '1.0',
            'cols': self.cols,
            'rows': self.rows,
            'grid': []
        }
        
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.grid[r][c]
                if cell['wall'] or cell['block']:
                    entry = {'r': r, 'c': c}
                    if cell['wall']:
                        entry['wall'] = cell['wall']
                    if cell['block']:
                        entry['block'] = list(cell['block'])
                    project['grid'].append(entry)
        
        try:
            with open(path, 'w') as f:
                json.dump(project, f)
            self.project_path = path
            self.status.set(f"Saved project: {os.path.basename(path)}")
            messagebox.showinfo("Export", "TPaint project saved!")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to save: {e}")
    
    def _export_tedit(self, path):
        """Export as TEdit schematic (.TEditSch) file."""
        import json
        
        # TEdit schematic format (JSON-based)
        # Reference: https://github.com/TEdit/Terraria-Map-Editor
        schematic = {
            'Name': os.path.splitext(os.path.basename(path))[0],
            'Version': 1,
            'Width': self.cols,
            'Height': self.rows,
            'Tiles': [],
            'Chests': [],
            'Signs': []
        }
        
        # Build tile array (TEdit format: array of rows, each row is array of tile objects)
        for r in range(self.rows):
            row_data = []
            for c in range(self.cols):
                cell = self.grid[r][c]
                tile_obj = {}
                
                # Wall
                if cell['wall']:
                    tile_obj['Wall'] = cell['wall']
                
                # Block/Tile
                if cell['block']:
                    block_data = cell['block']
                    if block_data[0] == 'block':
                        tile_obj['IsActive'] = True
                        tile_obj['Type'] = block_data[1]
                    elif block_data[0] == 'furn':
                        tile_obj['IsActive'] = True
                        tile_obj['Type'] = block_data[1]
                        # Frame coordinates for furniture
                        tile_obj['U'] = block_data[2] * TILE_SIZE
                        tile_obj['V'] = block_data[3] * TILE_SIZE
                
                row_data.append(tile_obj if tile_obj else None)
            schematic['Tiles'].append(row_data)
        
        try:
            with open(path, 'w') as f:
                json.dump(schematic, f, indent=2)
            self.status.set(f"Exported TEdit: {os.path.basename(path)}")
            messagebox.showinfo("Export", "TEdit schematic saved!\n\nImport in TEdit via:\nFile → Import → Schematic")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to save: {e}")


def check_textures():
    """Check if textures exist, run setup if missing."""
    tiles = list(TEXTURE_DIR.glob("Tiles_*.png"))
    walls = list(TEXTURE_DIR.glob("Wall_*.png"))
    
    if len(tiles) < 100 or len(walls) < 100:
        try:
            from setup import setup_textures_gui
            if not setup_textures_gui():
                return False
        except ImportError:
            messagebox.showerror("Setup Error", 
                "setup.py not found.\n\nPlease place Terraria textures in the textures folder.")
            return False
    return True


def main():
    # Check for textures on startup
    if not check_textures():
        # Show error in GUI since we may not have console
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("TPaint", 
            "Cannot start without textures.\n\nPlease run setup.py or place Terraria textures in the textures folder.")
        root.destroy()
        return
    
    root = tk.Tk()
    root.geometry("1400x800")
    app = TerrariaPaint(root)
    root.mainloop()


if __name__ == "__main__":
    main()
