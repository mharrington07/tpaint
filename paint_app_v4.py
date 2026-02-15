"""
Terraria Texture Paint App v4
All game tiles and walls included!
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np
from pathlib import Path
import re


TEXTURE_DIR = Path(__file__).parent / "textures"
TILE_SIZE = 16

# Import tile names and colors
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


# Block frame lookup - maps cardinal bitmask to (col, row) in 18px grid
TILE_FRAME_MAP = {
    0b0000: [(9, 3), (10, 3), (11, 3)],
    0b0001: [(6, 3), (7, 3), (8, 3)],
    0b0010: [(9, 0), (9, 1), (9, 2)],
    0b0100: [(6, 0), (7, 0), (8, 0)],
    0b1000: [(12, 0), (12, 1), (12, 2)],
    0b0101: [(5, 0), (5, 1), (5, 2)],
    0b1010: [(6, 4), (7, 4), (8, 4)],
    0b0011: [(0, 2), (1, 2), (2, 2)],
    0b0110: [(0, 0), (1, 0), (2, 0)],
    0b1100: [(3, 0), (4, 0), (3, 0)],
    0b1001: [(3, 2), (4, 2), (3, 2)],
    0b0111: [(0, 1), (1, 1), (2, 1)],
    0b1110: [(3, 1), (4, 1), (3, 1)],
    0b1101: [(0, 1), (1, 1), (2, 1)],
    0b1011: [(1, 2), (2, 2), (0, 2)],
    0b1111: [(1, 1), (2, 1), (3, 1)],
}


def scan_textures():
    """Scan texture folder for all available tiles and walls."""
    tiles = []
    walls = []
    
    for f in TEXTURE_DIR.iterdir():
        m = re.match(r'Tiles_(\d+)\.png', f.name)
        if m:
            tiles.append(int(m.group(1)))
        m = re.match(r'Wall_(\d+)\.png', f.name)
        if m:
            walls.append(int(m.group(1)))
    
    tiles.sort()
    walls.sort()
    return tiles, walls


class TileCache:
    """Cache for tile textures."""
    
    def __init__(self, tile_ids, wall_ids):
        self.tile_sheets = {}
        self.wall_sheets = {}
        self.frame_cache = {}
        self.tile_info = {}  # id -> (name, rgb)
        self.wall_info = {}
        
        self._load_sheets(tile_ids, wall_ids)
    
    def _load_sheets(self, tile_ids, wall_ids):
        print(f"Loading {len(tile_ids)} tile sheets...")
        for tid in tile_ids:
            path = TEXTURE_DIR / f"Tiles_{tid}.png"
            if path.exists():
                try:
                    self.tile_sheets[tid] = Image.open(path).convert('RGBA')
                    name = TILE_NAMES.get(tid, f"Tile {tid}")
                    rgb = TILE_COLORS.get(tid, (128, 128, 128))
                    self.tile_info[tid] = (name, rgb)
                except Exception as e:
                    pass
        
        print(f"Loading {len(wall_ids)} wall sheets...")
        for wid in wall_ids:
            path = TEXTURE_DIR / f"Wall_{wid}.png"
            if path.exists():
                try:
                    self.wall_sheets[wid] = Image.open(path).convert('RGBA')
                    name = WALL_NAMES.get(wid, f"Wall {wid}")
                    rgb = WALL_COLORS.get(wid, (80, 80, 80))
                    self.wall_info[wid] = (name, rgb)
                except:
                    pass
        
        print(f"Loaded {len(self.tile_sheets)} tiles, {len(self.wall_sheets)} walls")
    
    def get_tile_frame(self, tile_id: int, neighbors: dict) -> Image.Image:
        if tile_id not in self.tile_sheets:
            return None
        
        mask = 0
        if neighbors.get('n'): mask |= 1
        if neighbors.get('e'): mask |= 2
        if neighbors.get('s'): mask |= 4
        if neighbors.get('w'): mask |= 8
        
        frame_options = TILE_FRAME_MAP.get(mask, [(1, 1)])
        col, row = frame_options[0]
        
        cache_key = ('tile', tile_id, col, row)
        if cache_key not in self.frame_cache:
            sheet = self.tile_sheets[tile_id]
            w, h = sheet.size
            
            x = col * 18 + 1
            y = row * 18 + 1
            
            if x + 16 > w:
                x = 1
            if y + 16 > h:
                y = 1
            
            frame = sheet.crop((x, y, x + 16, y + 16))
            self.frame_cache[cache_key] = frame
        
        return self.frame_cache[cache_key]
    
    def get_wall_frame(self, wall_id: int, neighbors: dict) -> Image.Image:
        if wall_id not in self.wall_sheets:
            return None
        
        cache_key = ('wall_tile', wall_id)
        if cache_key not in self.frame_cache:
            sheet = self.wall_sheets[wall_id]
            w, h = sheet.size
            
            col, row = 9, 3
            frame_x = col * 36
            frame_y = row * 36
            
            if frame_x + 36 > w:
                frame_x = 0
            if frame_y + 36 > h:
                frame_y = 0
            
            x = frame_x + 2 + 8
            y = frame_y + 2 + 8
            
            if x + 16 > w:
                x = frame_x + 2
            if y + 16 > h:
                y = frame_y + 2
                
            frame = sheet.crop((x, y, x + 16, y + 16))
            
            arr = np.array(frame)
            if (arr[:,:,3] > 128).sum() < 128:
                x = frame_x + 2
                y = frame_y + 2
                frame = sheet.crop((x, y, x + 32, y + 32))
                frame = frame.resize((16, 16), Image.NEAREST)
            
            self.frame_cache[cache_key] = frame
        
        return self.frame_cache[cache_key]


class TerrariaPaintApp:
    """Paint app with ALL Terraria tiles and walls."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Terraria Paint - All Tiles!")
        
        self.grid_cols = 60
        self.grid_rows = 40
        
        self.grid = [[None for _ in range(self.grid_cols)] for _ in range(self.grid_rows)]
        
        self.current_tool = 'block'
        self.current_block_id = 30
        self.current_wall_id = 4
        
        # Scan and load all textures
        print("Scanning textures folder...")
        self.all_tile_ids, self.all_wall_ids = scan_textures()
        print(f"Found {len(self.all_tile_ids)} tiles, {len(self.all_wall_ids)} walls")
        
        print("Initializing texture cache...")
        self.cache = TileCache(self.all_tile_ids, self.all_wall_ids)
        
        self._photo_cache = {}
        self._palette_photos = {}
        
        # Search/filter
        self.tile_filter = ""
        self.wall_filter = ""
        
        self._build_ui()
        self._render_grid()
    
    def _build_ui(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel
        left_panel = ttk.Frame(main_frame, width=220)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        left_panel.pack_propagate(False)
        
        # Tools
        tool_frame = ttk.LabelFrame(left_panel, text="Tools")
        tool_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.tool_var = tk.StringVar(value='block')
        tools_row = ttk.Frame(tool_frame)
        tools_row.pack(fill=tk.X)
        ttk.Radiobutton(tools_row, text="Block", variable=self.tool_var,
                        value='block', command=self._on_tool_change).pack(side=tk.LEFT)
        ttk.Radiobutton(tools_row, text="Wall", variable=self.tool_var,
                        value='wall', command=self._on_tool_change).pack(side=tk.LEFT)
        ttk.Radiobutton(tools_row, text="Erase", variable=self.tool_var,
                        value='erase', command=self._on_tool_change).pack(side=tk.LEFT)
        
        # Brush size
        brush_row = ttk.Frame(tool_frame)
        brush_row.pack(fill=tk.X)
        ttk.Label(brush_row, text="Brush:").pack(side=tk.LEFT)
        self.brush_var = tk.IntVar(value=1)
        for size in [1, 2, 3, 5, 10]:
            ttk.Radiobutton(brush_row, text=str(size), variable=self.brush_var,
                           value=size).pack(side=tk.LEFT)
        
        # Block palette with search
        block_container = ttk.LabelFrame(left_panel, text=f"Blocks ({len(self.cache.tile_info)})")
        block_container.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        # Search box
        self.tile_search_var = tk.StringVar()
        self.tile_search_var.trace('w', lambda *args: self._filter_tiles())
        ttk.Entry(block_container, textvariable=self.tile_search_var).pack(fill=tk.X, padx=2, pady=2)
        
        # Scrollable tile list
        tile_scroll_frame = ttk.Frame(block_container)
        tile_scroll_frame.pack(fill=tk.BOTH, expand=True)
        
        self.tile_canvas = tk.Canvas(tile_scroll_frame, width=190, bg='#2a2a3a')
        tile_sb = ttk.Scrollbar(tile_scroll_frame, orient="vertical", command=self.tile_canvas.yview)
        self.tile_inner = ttk.Frame(self.tile_canvas)
        
        self.tile_canvas.configure(yscrollcommand=tile_sb.set)
        tile_sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.tile_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tile_canvas_window = self.tile_canvas.create_window((0, 0), window=self.tile_inner, anchor="nw")
        
        self.tile_canvas.bind('<Configure>', lambda e: self.tile_canvas.itemconfig(self.tile_canvas_window, width=e.width))
        self.tile_inner.bind('<Configure>', lambda e: self.tile_canvas.configure(scrollregion=self.tile_canvas.bbox("all")))
        
        # Mouse wheel scrolling
        self.tile_canvas.bind('<MouseWheel>', lambda e: self.tile_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        
        # Wall palette with search
        wall_container = ttk.LabelFrame(left_panel, text=f"Walls ({len(self.cache.wall_info)})")
        wall_container.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        self.wall_search_var = tk.StringVar()
        self.wall_search_var.trace('w', lambda *args: self._filter_walls())
        ttk.Entry(wall_container, textvariable=self.wall_search_var).pack(fill=tk.X, padx=2, pady=2)
        
        wall_scroll_frame = ttk.Frame(wall_container)
        wall_scroll_frame.pack(fill=tk.BOTH, expand=True)
        
        self.wall_canvas = tk.Canvas(wall_scroll_frame, width=190, bg='#2a2a3a')
        wall_sb = ttk.Scrollbar(wall_scroll_frame, orient="vertical", command=self.wall_canvas.yview)
        self.wall_inner = ttk.Frame(self.wall_canvas)
        
        self.wall_canvas.configure(yscrollcommand=wall_sb.set)
        wall_sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.wall_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.wall_canvas_window = self.wall_canvas.create_window((0, 0), window=self.wall_inner, anchor="nw")
        
        self.wall_canvas.bind('<Configure>', lambda e: self.wall_canvas.itemconfig(self.wall_canvas_window, width=e.width))
        self.wall_inner.bind('<Configure>', lambda e: self.wall_canvas.configure(scrollregion=self.wall_canvas.bbox("all")))
        self.wall_canvas.bind('<MouseWheel>', lambda e: self.wall_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        
        # Populate palettes
        self._populate_tile_palette()
        self._populate_wall_palette()
        
        # Actions
        action_frame = ttk.LabelFrame(left_panel, text="Actions")
        action_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(action_frame, text="Clear All", command=self._clear_grid).pack(fill=tk.X, pady=1)
        ttk.Button(action_frame, text="Save Image", command=self._save_image).pack(fill=tk.X, pady=1)
        
        # Canvas
        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        h_scroll = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL)
        v_scroll = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL)
        
        self.canvas = tk.Canvas(canvas_frame, 
                                width=900, height=640,
                                bg='#1a1a2e',
                                xscrollcommand=h_scroll.set,
                                yscrollcommand=v_scroll.set,
                                scrollregion=(0, 0, self.grid_cols * TILE_SIZE, 
                                             self.grid_rows * TILE_SIZE))
        
        h_scroll.config(command=self.canvas.xview)
        v_scroll.config(command=self.canvas.yview)
        
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.canvas.bind('<Button-1>', self._on_click)
        self.canvas.bind('<B1-Motion>', self._on_drag)
        self.canvas.bind('<Button-3>', self._on_right_click)
        self.canvas.bind('<B3-Motion>', self._on_right_drag)
        self.canvas.bind('<Motion>', self._on_mouse_move)
        self.canvas.bind('<Leave>', self._on_mouse_leave)
        
        # Cursor highlight
        self.cursor_highlight = None
        self.last_cursor_pos = (None, None)
        
        self.status_var = tk.StringVar(value="Ready - Left click to paint, Right click to erase | Search tiles by name!")
        ttk.Label(self.root, textvariable=self.status_var).pack(side=tk.BOTTOM, fill=tk.X)
    
    def _populate_tile_palette(self, filter_text=""):
        # Clear existing
        for widget in self.tile_inner.winfo_children():
            widget.destroy()
        
        filter_text = filter_text.lower()
        count = 0
        
        for tid in sorted(self.cache.tile_info.keys()):
            name, rgb = self.cache.tile_info[tid]
            
            if filter_text and filter_text not in name.lower() and filter_text not in str(tid):
                continue
            
            frame = ttk.Frame(self.tile_inner)
            frame.pack(fill=tk.X, pady=1, padx=2)
            
            # Color swatch
            color = f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'
            swatch = tk.Label(frame, width=2, bg=color)
            swatch.pack(side=tk.LEFT, padx=(0, 2))
            
            # Name button
            display_name = name[:18] if len(name) > 18 else name
            btn = tk.Button(frame, text=f"{tid}: {display_name}", 
                           anchor='w', width=22,
                           bg='#3a3a4a', fg='white',
                           activebackground='#5a5a6a',
                           command=lambda t=tid: self._select_block(t))
            btn.pack(side=tk.LEFT, fill=tk.X, expand=True)
            count += 1
        
        self.tile_inner.update_idletasks()
    
    def _populate_wall_palette(self, filter_text=""):
        for widget in self.wall_inner.winfo_children():
            widget.destroy()
        
        filter_text = filter_text.lower()
        
        for wid in sorted(self.cache.wall_info.keys()):
            name, rgb = self.cache.wall_info[wid]
            
            if filter_text and filter_text not in name.lower() and filter_text not in str(wid):
                continue
            
            frame = ttk.Frame(self.wall_inner)
            frame.pack(fill=tk.X, pady=1, padx=2)
            
            color = f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'
            swatch = tk.Label(frame, width=2, bg=color)
            swatch.pack(side=tk.LEFT, padx=(0, 2))
            
            display_name = name[:18] if len(name) > 18 else name
            btn = tk.Button(frame, text=f"{wid}: {display_name}",
                           anchor='w', width=22,
                           bg='#3a3a4a', fg='white',
                           activebackground='#5a5a6a',
                           command=lambda w=wid: self._select_wall(w))
            btn.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.wall_inner.update_idletasks()
    
    def _filter_tiles(self):
        self._populate_tile_palette(self.tile_search_var.get())
    
    def _filter_walls(self):
        self._populate_wall_palette(self.wall_search_var.get())
    
    def _on_tool_change(self):
        self.current_tool = self.tool_var.get()
        self.status_var.set(f"Tool: {self.current_tool.title()}")
    
    def _select_block(self, tile_id):
        self.current_block_id = tile_id
        self.tool_var.set('block')
        self.current_tool = 'block'
        name = self.cache.tile_info.get(tile_id, ("Unknown",))[0]
        self.status_var.set(f"Block: {tile_id} - {name}")
    
    def _select_wall(self, wall_id):
        self.current_wall_id = wall_id
        self.tool_var.set('wall')
        self.current_tool = 'wall'
        name = self.cache.wall_info.get(wall_id, ("Unknown",))[0]
        self.status_var.set(f"Wall: {wall_id} - {name}")
    
    def _get_cell(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        col = int(x // TILE_SIZE)
        row = int(y // TILE_SIZE)
        if 0 <= col < self.grid_cols and 0 <= row < self.grid_rows:
            return row, col
        return None, None
    
    def _on_click(self, event):
        row, col = self._get_cell(event)
        if row is not None:
            self._paint_area(row, col)
    
    def _on_drag(self, event):
        row, col = self._get_cell(event)
        if row is not None:
            self._paint_area(row, col)
    
    def _on_right_click(self, event):
        row, col = self._get_cell(event)
        if row is not None:
            self._erase_area(row, col)
    
    def _on_right_drag(self, event):
        row, col = self._get_cell(event)
        if row is not None:
            self._erase_area(row, col)
    
    def _on_mouse_move(self, event):
        """Update cursor highlight as mouse moves."""
        row, col = self._get_cell(event)
        
        if (row, col) != self.last_cursor_pos:
            self.last_cursor_pos = (row, col)
            self._update_cursor_highlight(row, col)
    
    def _on_mouse_leave(self, event):
        """Remove cursor highlight when mouse leaves canvas."""
        self.canvas.delete('cursor_highlight')
        self.last_cursor_pos = (None, None)
    
    def _update_cursor_highlight(self, center_row, center_col):
        """Draw cursor highlight showing brush area."""
        self.canvas.delete('cursor_highlight')
        
        if center_row is None:
            return
        
        brush = self.brush_var.get()
        half = brush // 2
        
        # Calculate brush area bounds
        start_row = center_row - half
        start_col = center_col - half
        end_row = start_row + brush
        end_col = start_col + brush
        
        # Clamp to grid
        start_row = max(0, start_row)
        start_col = max(0, start_col)
        end_row = min(self.grid_rows, end_row)
        end_col = min(self.grid_cols, end_col)
        
        x1 = start_col * TILE_SIZE
        y1 = start_row * TILE_SIZE
        x2 = end_col * TILE_SIZE
        y2 = end_row * TILE_SIZE
        
        # Choose highlight color based on tool
        if self.current_tool == 'erase':
            outline_color = '#ff4444'
            fill_color = '#ff444422'
        elif self.current_tool == 'wall':
            outline_color = '#44aaff'
            fill_color = '#44aaff22'
        else:  # block
            outline_color = '#44ff44'
            fill_color = '#44ff4422'
        
        # Draw highlight rectangle
        self.canvas.create_rectangle(
            x1, y1, x2, y2,
            outline=outline_color,
            width=2,
            tags='cursor_highlight'
        )
        
        # Draw individual cell outlines for larger brushes
        if brush > 1:
            for r in range(start_row, end_row):
                for c in range(start_col, end_col):
                    cx = c * TILE_SIZE
                    cy = r * TILE_SIZE
                    self.canvas.create_rectangle(
                        cx, cy, cx + TILE_SIZE, cy + TILE_SIZE,
                        outline=outline_color,
                        width=1,
                        stipple='gray50',
                        tags='cursor_highlight'
                    )

    def _paint_area(self, center_row, center_col):
        brush = self.brush_var.get()
        half = brush // 2
        
        affected = set()
        
        for dr in range(-half, brush - half):
            for dc in range(-half, brush - half):
                r, c = center_row + dr, center_col + dc
                if 0 <= r < self.grid_rows and 0 <= c < self.grid_cols:
                    if self.current_tool == 'erase':
                        self.grid[r][c] = None
                    elif self.current_tool == 'block':
                        self.grid[r][c] = ('block', self.current_block_id)
                    elif self.current_tool == 'wall':
                        self.grid[r][c] = ('wall', self.current_wall_id)
                    
                    for nr in range(r - 1, r + 2):
                        for nc in range(c - 1, c + 2):
                            if 0 <= nr < self.grid_rows and 0 <= nc < self.grid_cols:
                                affected.add((nr, nc))
        
        for r, c in affected:
            self._render_cell(r, c)
    
    def _erase_area(self, center_row, center_col):
        brush = self.brush_var.get()
        half = brush // 2
        
        affected = set()
        
        for dr in range(-half, brush - half):
            for dc in range(-half, brush - half):
                r, c = center_row + dr, center_col + dc
                if 0 <= r < self.grid_rows and 0 <= c < self.grid_cols:
                    self.grid[r][c] = None
                    for nr in range(r - 1, r + 2):
                        for nc in range(c - 1, c + 2):
                            if 0 <= nr < self.grid_rows and 0 <= nc < self.grid_cols:
                                affected.add((nr, nc))
        
        for r, c in affected:
            self._render_cell(r, c)
    
    def _get_neighbors(self, row, col, cell_type):
        def check(r, c):
            if 0 <= r < self.grid_rows and 0 <= c < self.grid_cols:
                cell = self.grid[r][c]
                if cell and cell[0] == cell_type:
                    return True
            return False
        
        return {
            'n':  check(row - 1, col),
            's':  check(row + 1, col),
            'e':  check(row, col + 1),
            'w':  check(row, col - 1),
            'ne': check(row - 1, col + 1),
            'nw': check(row - 1, col - 1),
            'se': check(row + 1, col + 1),
            'sw': check(row + 1, col - 1),
        }
    
    def _render_cell(self, row, col):
        x = col * TILE_SIZE
        y = row * TILE_SIZE
        
        self.canvas.delete(f'cell_{row}_{col}')
        
        cell = self.grid[row][col]
        
        if cell:
            cell_type, cell_id = cell
            neighbors = self._get_neighbors(row, col, cell_type)
            
            if cell_type == 'block':
                img = self.cache.get_tile_frame(cell_id, neighbors)
            else:
                img = self.cache.get_wall_frame(cell_id, neighbors)
            
            if img:
                photo = ImageTk.PhotoImage(img)
                self._photo_cache[(row, col)] = photo
                self.canvas.create_image(x, y, anchor=tk.NW, image=photo, tags=f'cell_{row}_{col}')
    
    def _render_grid(self):
        self.canvas.delete('all')
        self._photo_cache = {}
        
        self.canvas.create_rectangle(0, 0, self.grid_cols * TILE_SIZE,
                                     self.grid_rows * TILE_SIZE,
                                     fill='#1a1a2e', outline='')
        
        for row in range(self.grid_rows):
            for col in range(self.grid_cols):
                if self.grid[row][col]:
                    self._render_cell(row, col)
    
    def _clear_grid(self):
        self.grid = [[None for _ in range(self.grid_cols)] for _ in range(self.grid_rows)]
        self._render_grid()
        self.status_var.set("Grid cleared!")
    
    def _save_image(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        
        if filepath:
            img = Image.new('RGBA', (self.grid_cols * TILE_SIZE, self.grid_rows * TILE_SIZE),
                           (26, 26, 46, 255))
            
            for row in range(self.grid_rows):
                for col in range(self.grid_cols):
                    cell = self.grid[row][col]
                    if cell:
                        cell_type, cell_id = cell
                        neighbors = self._get_neighbors(row, col, cell_type)
                        
                        if cell_type == 'block':
                            tile_img = self.cache.get_tile_frame(cell_id, neighbors)
                        else:
                            tile_img = self.cache.get_wall_frame(cell_id, neighbors)
                        
                        if tile_img:
                            img.paste(tile_img, (col * TILE_SIZE, row * TILE_SIZE), tile_img)
            
            img.save(filepath)
            self.status_var.set(f"Saved: {filepath}")
            messagebox.showinfo("Saved", f"Image saved to {filepath}")


def main():
    root = tk.Tk()
    root.geometry("1300x750")
    app = TerrariaPaintApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
