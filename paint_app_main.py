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
        self.block_id = 30
        self.wall_id = 4
        self.brush = 1
        self.photos = {}
        self.search_job = None
        self.zoom = 1.0  # Zoom level (0.25 to 4.0)
        
        # Load textures
        print("Loading textures...")
        tile_ids, wall_ids = scan_textures()
        self.cache = TileCache(tile_ids, wall_ids)
        
        self._build_ui()
        self._bind_keys()
        self._render()
    
    def _build_ui(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Modern dark theme colors
        bg_dark = '#1a1b26'
        bg_mid = '#24283b'
        bg_light = '#414868'
        accent = '#7aa2f7'
        accent_dim = '#3d59a1'
        text = '#c0caf5'
        text_dim = '#565f89'
        
        # Configure styles
        style.configure('TFrame', background=bg_dark)
        style.configure('TLabel', background=bg_dark, foreground=text, font=('Segoe UI', 9))
        style.configure('TLabelframe', background=bg_dark, foreground=text)
        style.configure('TLabelframe.Label', background=bg_dark, foreground=accent, font=('Segoe UI', 9, 'bold'))
        style.configure('TNotebook', background=bg_dark, borderwidth=0)
        style.configure('TNotebook.Tab', background=bg_mid, foreground=text, padding=[12, 6], font=('Segoe UI', 9))
        style.map('TNotebook.Tab', background=[('selected', accent_dim)], foreground=[('selected', '#ffffff')])
        style.configure('TButton', background=bg_light, foreground=text, font=('Segoe UI', 9), padding=[8, 4])
        style.map('TButton', background=[('active', accent)])
        style.configure('TRadiobutton', background=bg_dark, foreground=text, font=('Segoe UI', 9))
        style.map('TRadiobutton', background=[('active', bg_dark)])
        style.configure('TEntry', fieldbackground=bg_mid, foreground=text, insertcolor=text)
        style.configure('TSpinbox', fieldbackground=bg_mid, foreground=text, arrowcolor=text)
        style.configure('TScrollbar', background=bg_mid, troughcolor=bg_dark, arrowcolor=text)
        style.map('TScrollbar', background=[('active', bg_light)])
        
        self.root.configure(bg=bg_dark)
        self.colors = {'bg_dark': bg_dark, 'bg_mid': bg_mid, 'bg_light': bg_light, 
                       'accent': accent, 'text': text, 'text_dim': text_dim}
        
        main = ttk.Frame(self.root)
        main.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        
        # Left panel
        left = ttk.Frame(main, width=280)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0,8))
        left.pack_propagate(False)
        
        # Grid Size - compact row
        size_frame = ttk.LabelFrame(left, text="Grid Size")
        size_frame.pack(fill=tk.X, pady=(0,8))
        
        size_row = ttk.Frame(size_frame)
        size_row.pack(fill=tk.X, pady=6, padx=8)
        ttk.Label(size_row, text="W:").pack(side=tk.LEFT)
        self.width_var = tk.StringVar(value=str(self.cols))
        ttk.Spinbox(size_row, from_=1, to=10000, width=6, textvariable=self.width_var).pack(side=tk.LEFT, padx=(2,12))
        ttk.Label(size_row, text="H:").pack(side=tk.LEFT)
        self.height_var = tk.StringVar(value=str(self.rows))
        ttk.Spinbox(size_row, from_=1, to=10000, width=6, textvariable=self.height_var).pack(side=tk.LEFT, padx=(2,12))
        ttk.Button(size_row, text="Apply", command=self._resize_grid).pack(side=tk.LEFT)
        
        # Tools - horizontal buttons with Erase Block and Erase Wall options
        tools = ttk.LabelFrame(left, text="Tools")
        tools.pack(fill=tk.X, pady=(0,8))
        
        row1 = ttk.Frame(tools)
        row1.pack(fill=tk.X, pady=6, padx=8)
        self.tool_var = tk.StringVar(value='block')
        for text, val, key in [("Block", "block", "B"), ("Wall", "wall", "W")]:
            btn = ttk.Radiobutton(row1, text=f"{text} [{key}]", variable=self.tool_var, value=val,
                           command=self._tool_changed)
            btn.pack(side=tk.LEFT, padx=4)
        
        row2 = ttk.Frame(tools)
        row2.pack(fill=tk.X, pady=(0, 6), padx=8)
        for text, val, key in [("Erase Block", "erase_block", "X"), ("Erase Wall", "erase_wall", "Z"), ("Erase All", "erase", "E")]:
            btn = ttk.Radiobutton(row2, text=f"{text} [{key}]", variable=self.tool_var, value=val,
                           command=self._tool_changed)
            btn.pack(side=tk.LEFT, padx=4)
        
        # Brush sizes
        brush_frame = ttk.LabelFrame(left, text="Brush Size")
        brush_frame.pack(fill=tk.X, pady=(0,8))
        
        row = ttk.Frame(brush_frame)
        row.pack(fill=tk.X, pady=6, padx=8)
        self.brush_var = tk.IntVar(value=1)
        for i, size in enumerate([1, 2, 3, 5, 10], 1):
            ttk.Radiobutton(row, text=f"{size}x{size}", variable=self.brush_var, value=size,
                           command=self._brush_changed).pack(side=tk.LEFT, padx=4)
        
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
        
        # Action buttons
        actions = ttk.Frame(left)
        actions.pack(fill=tk.X)
        ttk.Button(actions, text="Clear [C]", command=self._clear).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0,4))
        ttk.Button(actions, text="Save [S]", command=self._save).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(4,0))
        
        # Canvas area
        canvas_frame = ttk.Frame(main)
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        xscroll = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL)
        yscroll = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL)
        
        self.canvas = tk.Canvas(canvas_frame, bg='#0f0f14', highlightthickness=0,
                               xscrollcommand=xscroll.set, yscrollcommand=yscroll.set,
                               scrollregion=(0, 0, self.cols*TILE_SIZE, self.rows*TILE_SIZE))
        
        xscroll.config(command=self.canvas.xview)
        yscroll.config(command=self.canvas.yview)
        
        yscroll.pack(side=tk.RIGHT, fill=tk.Y)
        xscroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.canvas.bind('<Button-1>', self._click)
        self.canvas.bind('<B1-Motion>', self._drag)
        self.canvas.bind('<Button-3>', self._right_click)
        self.canvas.bind('<B3-Motion>', self._right_drag)
        self.canvas.bind('<Motion>', self._hover)
        self.canvas.bind('<Leave>', lambda e: self.canvas.delete('cursor'))
        
        # Middle-click pan
        self.canvas.bind('<Button-2>', self._pan_start)
        self.canvas.bind('<B2-Motion>', self._pan_move)
        self._pan_data = None
        
        # Scroll wheel zoom
        self.canvas.bind('<MouseWheel>', self._zoom)
        
        # Status bar
        status_frame = tk.Frame(self.root, bg=bg_mid, height=28)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        status_frame.pack_propagate(False)
        
        self.status = tk.StringVar(value="Ready • Scroll=Zoom • Middle-click=Pan • B/W/E/X/Z=Tools • 1-5=Brush • C=Clear • S=Save")
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
            
            # Color swatch with padding
            color = f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'
            swatch = tk.Frame(row, bg=color, width=20, height=24)
            swatch.pack(side=tk.LEFT, padx=(0,6))
            swatch.pack_propagate(False)
            
            # Name button
            display = f"{tid}: {name[:24]}"
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
            swatch.bind('<MouseWheel>', lambda e, c=lst['canvas']: c.yview_scroll(-1*(e.delta//120), 'units'))
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
    
    def _bind_keys(self):
        self.root.bind('b', lambda e: self._set_tool('block'))
        self.root.bind('w', lambda e: self._set_tool('wall'))
        self.root.bind('e', lambda e: self._set_tool('erase'))
        self.root.bind('x', lambda e: self._set_tool('erase_block'))
        self.root.bind('z', lambda e: self._set_tool('erase_wall'))
        self.root.bind('1', lambda e: self._set_brush(1))
        self.root.bind('2', lambda e: self._set_brush(2))
        self.root.bind('3', lambda e: self._set_brush(3))
        self.root.bind('4', lambda e: self._set_brush(5))
        self.root.bind('5', lambda e: self._set_brush(10))
        self.root.bind('c', lambda e: self._clear())
        self.root.bind('s', lambda e: self._save())
    
    def _set_tool(self, tool):
        self.tool = tool
        self.tool_var.set(tool)
        tool_names = {
            'block': 'Block',
            'wall': 'Wall',
            'erase': 'Erase All',
            'erase_block': 'Erase Block',
            'erase_wall': 'Erase Wall'
        }
        self.status.set(f"Tool: {tool_names.get(tool, tool.title())}")
    
    def _set_brush(self, size):
        self.brush = size
        self.brush_var.set(size)
        self.status.set(f"Brush: {size}x{size}")
    
    def _tool_changed(self):
        self.tool = self.tool_var.get()
    
    def _brush_changed(self):
        self.brush = self.brush_var.get()
    
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
            dx = self._pan_data[0] - e.x
            dy = self._pan_data[1] - e.y
            self._pan_data = (e.x, e.y)
            # Scroll by pixel delta
            self.canvas.xview_scroll(dx, 'units')
            self.canvas.yview_scroll(dy, 'units')
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
        if r is not None:
            self._paint(r, c)
            self._draw_cursor(r, c)
    
    def _drag(self, e):
        r, c = self._get_cell(e)
        if r is not None:
            self._paint(r, c)
            self._draw_cursor(r, c)
    
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
    
    def _clear(self):
        self.grid = [[{'wall': None, 'block': None} for _ in range(self.cols)] for _ in range(self.rows)]
        self._render()
        self.status.set("Cleared!")
    
    def _save(self):
        path = filedialog.asksaveasfilename(defaultextension=".png",
                                            filetypes=[("PNG", "*.png")])
        if path:
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
            self.status.set(f"Saved: {path}")
            messagebox.showinfo("Saved", f"Image saved!")


def main():
    root = tk.Tk()
    root.geometry("1400x800")
    app = TerrariaPaint(root)
    root.mainloop()


if __name__ == "__main__":
    main()
