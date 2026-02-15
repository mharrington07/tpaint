"""
Terraria Texture Mapping
Maps block/wall IDs to their actual texture filenames from the game.

Terraria texture naming:
- Tiles_X.png = Block tiles (X = tile ID)
- Wall_X.png = Wall tiles (X = wall ID)
- Item_X.png = Item sprites
- NPC_X.png = NPCs
- Projectile_X.png = Projectiles

We ONLY use Tiles_ and Wall_ for building.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class TileInfo:
    """Complete info for a Terraria tile."""
    id: int
    name: str
    texture_file: str  # e.g., "Tiles_0.png"
    rgb: tuple[int, int, int]  # Average color for matching
    category: str
    width: int = 1  # Tile width in blocks (most are 1x1)
    height: int = 1  # Tile height in blocks
    is_solid: bool = True
    is_furniture: bool = False


@dataclass
class WallInfo:
    """Complete info for a Terraria wall."""
    id: int
    name: str
    texture_file: str  # e.g., "Wall_1.png"
    rgb: tuple[int, int, int]
    category: str


# =============================================================================
# TILES (Blocks) - Maps to Tiles_X.png
# =============================================================================

TILES = [
    # -------------------------------------------------------------------------
    # NATURAL BLOCKS
    # -------------------------------------------------------------------------
    TileInfo(0, "Dirt", "Tiles_0.png", (151, 107, 75), "soil"),
    TileInfo(1, "Stone", "Tiles_1.png", (128, 128, 128), "stone"),
    TileInfo(2, "Grass", "Tiles_2.png", (28, 200, 94), "grass"),
    TileInfo(23, "Corrupt Grass", "Tiles_23.png", (141, 98, 195), "grass"),
    TileInfo(25, "Ebonstone", "Tiles_25.png", (98, 95, 167), "stone"),
    TileInfo(40, "Clay", "Tiles_40.png", (146, 81, 68), "soil"),
    TileInfo(53, "Sand", "Tiles_53.png", (219, 197, 135), "soil"),
    TileInfo(56, "Obsidian", "Tiles_56.png", (65, 52, 76), "stone"),
    TileInfo(57, "Ash", "Tiles_57.png", (44, 41, 50), "soil"),
    TileInfo(58, "Hellstone", "Tiles_58.png", (102, 34, 34), "stone"),
    TileInfo(59, "Mud", "Tiles_59.png", (92, 68, 73), "soil"),
    TileInfo(60, "Jungle Grass", "Tiles_60.png", (143, 215, 29), "grass"),
    TileInfo(70, "Mushroom Grass", "Tiles_70.png", (93, 127, 255), "grass"),
    TileInfo(75, "Meteorite", "Tiles_75.png", (105, 74, 202), "stone"),
    TileInfo(109, "Hallowed Grass", "Tiles_109.png", (78, 193, 227), "grass"),
    TileInfo(112, "Ebonsand", "Tiles_112.png", (122, 116, 163), "soil"),
    TileInfo(116, "Pearlsand", "Tiles_116.png", (230, 178, 211), "soil"),
    TileInfo(117, "Pearlstone", "Tiles_117.png", (181, 146, 173), "stone"),
    TileInfo(123, "Silt", "Tiles_123.png", (108, 100, 115), "soil"),
    TileInfo(147, "Ice", "Tiles_147.png", (147, 197, 234), "ice"),
    TileInfo(161, "Sandstone", "Tiles_161.png", (171, 142, 91), "stone"),
    TileInfo(163, "Purple Ice", "Tiles_163.png", (140, 100, 182), "ice"),
    TileInfo(164, "Pink Ice", "Tiles_164.png", (215, 165, 203), "ice"),
    TileInfo(199, "Crimson Grass", "Tiles_199.png", (182, 50, 51), "grass"),
    TileInfo(200, "Red Ice", "Tiles_200.png", (180, 82, 82), "ice"),
    TileInfo(203, "Crimstone", "Tiles_203.png", (140, 56, 56), "stone"),
    TileInfo(224, "Slush", "Tiles_224.png", (170, 188, 197), "soil"),
    TileInfo(234, "Crimsand", "Tiles_234.png", (213, 92, 77), "soil"),
    TileInfo(367, "Marble", "Tiles_367.png", (211, 207, 201), "stone"),
    TileInfo(368, "Granite", "Tiles_368.png", (50, 46, 104), "stone"),
    
    # -------------------------------------------------------------------------
    # ORES
    # -------------------------------------------------------------------------
    TileInfo(6, "Iron Ore", "Tiles_6.png", (135, 114, 95), "ore"),
    TileInfo(7, "Copper Ore", "Tiles_7.png", (150, 100, 50), "ore"),
    TileInfo(8, "Gold Ore", "Tiles_8.png", (185, 164, 23), "ore"),
    TileInfo(9, "Silver Ore", "Tiles_9.png", (185, 194, 195), "ore"),
    TileInfo(22, "Demonite Ore", "Tiles_22.png", (98, 95, 167), "ore"),
    TileInfo(107, "Cobalt Ore", "Tiles_107.png", (33, 105, 163), "ore"),
    TileInfo(108, "Mythril Ore", "Tiles_108.png", (130, 186, 130), "ore"),
    TileInfo(111, "Adamantite Ore", "Tiles_111.png", (221, 85, 125), "ore"),
    TileInfo(166, "Tin Ore", "Tiles_166.png", (152, 137, 106), "ore"),
    TileInfo(167, "Lead Ore", "Tiles_167.png", (83, 98, 113), "ore"),
    TileInfo(168, "Tungsten Ore", "Tiles_168.png", (95, 137, 81), "ore"),
    TileInfo(169, "Platinum Ore", "Tiles_169.png", (155, 175, 195), "ore"),
    TileInfo(204, "Crimtane Ore", "Tiles_204.png", (175, 55, 55), "ore"),
    TileInfo(211, "Chlorophyte Ore", "Tiles_211.png", (79, 178, 56), "ore"),
    TileInfo(221, "Palladium Ore", "Tiles_221.png", (228, 95, 43), "ore"),
    TileInfo(222, "Orichalcum Ore", "Tiles_222.png", (186, 50, 188), "ore"),
    TileInfo(223, "Titanium Ore", "Tiles_223.png", (139, 141, 145), "ore"),
    
    # -------------------------------------------------------------------------
    # WOOD TYPES
    # -------------------------------------------------------------------------
    TileInfo(30, "Wood", "Tiles_30.png", (168, 121, 72), "wood"),
    TileInfo(157, "Ebonwood", "Tiles_157.png", (113, 99, 133), "wood"),
    TileInfo(158, "Shadewood", "Tiles_158.png", (82, 62, 95), "wood"),
    TileInfo(159, "Pearlwood", "Tiles_159.png", (173, 154, 122), "wood"),
    TileInfo(191, "Living Wood", "Tiles_191.png", (137, 97, 57), "wood"),
    TileInfo(192, "Living Leaf", "Tiles_192.png", (80, 140, 50), "wood"),
    TileInfo(208, "Cactus", "Tiles_208.png", (87, 112, 24), "wood"),
    TileInfo(311, "Boreal Wood", "Tiles_311.png", (151, 132, 115), "wood"),
    TileInfo(322, "Palm Wood", "Tiles_322.png", (183, 165, 117), "wood"),
    TileInfo(383, "Rich Mahogany", "Tiles_383.png", (107, 50, 46), "wood"),
    TileInfo(188, "Dynasty Wood", "Tiles_188.png", (185, 125, 70), "wood"),
    TileInfo(431, "Spooky Wood", "Tiles_431.png", (60, 47, 70), "wood"),
    
    # -------------------------------------------------------------------------
    # BRICKS
    # -------------------------------------------------------------------------
    TileInfo(38, "Gray Brick", "Tiles_38.png", (90, 90, 90), "brick"),
    TileInfo(39, "Red Brick", "Tiles_39.png", (150, 60, 60), "brick"),
    TileInfo(41, "Blue Brick", "Tiles_41.png", (43, 53, 121), "brick"),
    TileInfo(43, "Green Brick", "Tiles_43.png", (40, 77, 52), "brick"),
    TileInfo(44, "Pink Brick", "Tiles_44.png", (122, 46, 82), "brick"),
    TileInfo(45, "Gold Brick", "Tiles_45.png", (176, 157, 35), "brick"),
    TileInfo(46, "Silver Brick", "Tiles_46.png", (178, 183, 187), "brick"),
    TileInfo(47, "Copper Brick", "Tiles_47.png", (173, 106, 60), "brick"),
    TileInfo(54, "Obsidian Brick", "Tiles_54.png", (25, 23, 54), "brick"),
    TileInfo(118, "Pearlstone Brick", "Tiles_118.png", (140, 130, 145), "brick"),
    TileInfo(119, "Iridescent Brick", "Tiles_119.png", (90, 100, 80), "brick"),
    TileInfo(120, "Mudstone Brick", "Tiles_120.png", (73, 57, 49), "brick"),
    TileInfo(121, "Cobalt Brick", "Tiles_121.png", (53, 78, 117), "brick"),
    TileInfo(122, "Mythril Brick", "Tiles_122.png", (84, 130, 100), "brick"),
    TileInfo(140, "Demonite Brick", "Tiles_140.png", (77, 69, 105), "brick"),
    TileInfo(144, "Hellstone Brick", "Tiles_144.png", (102, 46, 38), "brick"),
    TileInfo(175, "Sunplate", "Tiles_175.png", (225, 195, 130), "brick"),
    TileInfo(196, "Sandstone Brick", "Tiles_196.png", (163, 143, 92), "brick"),
    TileInfo(226, "Lihzahrd Brick", "Tiles_226.png", (76, 57, 10), "brick"),
    TileInfo(267, "Stone Slab", "Tiles_267.png", (130, 130, 130), "brick"),
    TileInfo(273, "Snow Brick", "Tiles_273.png", (210, 220, 230), "brick"),
    TileInfo(369, "Marble Block", "Tiles_369.png", (200, 195, 190), "brick"),
    TileInfo(370, "Granite Block", "Tiles_370.png", (55, 50, 90), "brick"),
    
    # -------------------------------------------------------------------------
    # ICE & SNOW
    # -------------------------------------------------------------------------
    TileInfo(127, "Snow", "Tiles_127.png", (224, 231, 240), "ice"),
    TileInfo(148, "Ice Brick", "Tiles_148.png", (130, 180, 220), "ice"),
    
    # -------------------------------------------------------------------------
    # GEMS (embedded in stone)
    # -------------------------------------------------------------------------
    TileInfo(63, "Sapphire Stone", "Tiles_63.png", (45, 68, 168), "gem"),
    TileInfo(64, "Ruby Stone", "Tiles_64.png", (166, 24, 44), "gem"),
    TileInfo(65, "Emerald Stone", "Tiles_65.png", (8, 143, 59), "gem"),
    TileInfo(66, "Topaz Stone", "Tiles_66.png", (182, 161, 55), "gem"),
    TileInfo(67, "Amethyst Stone", "Tiles_67.png", (153, 72, 189), "gem"),
    TileInfo(68, "Diamond Stone", "Tiles_68.png", (93, 186, 192), "gem"),
    
    # -------------------------------------------------------------------------
    # GEMSPARK BLOCKS
    # -------------------------------------------------------------------------
    TileInfo(259, "Amber Gemspark", "Tiles_259.png", (255, 180, 50), "gemspark"),
    TileInfo(260, "Diamond Gemspark", "Tiles_260.png", (220, 255, 255), "gemspark"),
    TileInfo(261, "Offline Diamond Gemspark", "Tiles_261.png", (150, 180, 180), "gemspark"),
    TileInfo(262, "Amethyst Gemspark", "Tiles_262.png", (200, 100, 255), "gemspark"),
    TileInfo(263, "Topaz Gemspark", "Tiles_263.png", (255, 220, 80), "gemspark"),
    TileInfo(264, "Sapphire Gemspark", "Tiles_264.png", (80, 120, 255), "gemspark"),
    TileInfo(265, "Emerald Gemspark", "Tiles_265.png", (80, 255, 100), "gemspark"),
    TileInfo(266, "Ruby Gemspark", "Tiles_266.png", (255, 80, 80), "gemspark"),
    
    # -------------------------------------------------------------------------
    # GLASS
    # -------------------------------------------------------------------------
    TileInfo(51, "Glass", "Tiles_51.png", (175, 210, 240), "glass"),
    TileInfo(328, "Waterfall Block", "Tiles_328.png", (100, 150, 255), "glass"),
    TileInfo(329, "Lavafall Block", "Tiles_329.png", (255, 120, 40), "glass"),
    
    # -------------------------------------------------------------------------
    # HIVE & HONEY
    # -------------------------------------------------------------------------
    TileInfo(225, "Hive", "Tiles_225.png", (226, 148, 36), "hive"),
    TileInfo(229, "Honey Block", "Tiles_229.png", (239, 176, 46), "hive"),
    TileInfo(230, "Crispy Honey", "Tiles_230.png", (200, 150, 30), "hive"),
    
    # -------------------------------------------------------------------------
    # SPECIAL BLOCKS
    # -------------------------------------------------------------------------
    TileInfo(76, "Bone Block", "Tiles_76.png", (210, 200, 180), "special"),
    TileInfo(179, "Flesh Block", "Tiles_179.png", (140, 50, 60), "special"),
    TileInfo(180, "Lesion Block", "Tiles_180.png", (100, 60, 80), "special"),
    TileInfo(189, "Cloud", "Tiles_189.png", (255, 255, 255), "special"),
    TileInfo(190, "Rain Cloud", "Tiles_190.png", (150, 150, 180), "special"),
    TileInfo(209, "Pumpkin", "Tiles_209.png", (225, 125, 25), "special"),
    TileInfo(210, "Hay", "Tiles_210.png", (170, 150, 80), "special"),
    TileInfo(379, "Silk", "Tiles_379.png", (245, 240, 235), "special"),
    
    # -------------------------------------------------------------------------
    # FURNITURE (multi-tile objects - for reference)
    # -------------------------------------------------------------------------
    TileInfo(10, "Closed Door", "Tiles_10.png", (140, 100, 70), "furniture", width=1, height=3, is_solid=False, is_furniture=True),
    TileInfo(11, "Open Door", "Tiles_11.png", (140, 100, 70), "furniture", width=2, height=3, is_solid=False, is_furniture=True),
    TileInfo(13, "Bottle", "Tiles_13.png", (200, 200, 220), "furniture", width=1, height=1, is_solid=False, is_furniture=True),
    TileInfo(14, "Table", "Tiles_14.png", (150, 110, 70), "furniture", width=3, height=2, is_solid=False, is_furniture=True),
    TileInfo(15, "Chair", "Tiles_15.png", (150, 110, 70), "furniture", width=1, height=2, is_solid=False, is_furniture=True),
    TileInfo(17, "Furnace", "Tiles_17.png", (120, 100, 100), "furniture", width=3, height=2, is_solid=False, is_furniture=True),
    TileInfo(18, "Workbench", "Tiles_18.png", (160, 120, 80), "furniture", width=2, height=1, is_solid=False, is_furniture=True),
    TileInfo(19, "Platform", "Tiles_19.png", (150, 110, 70), "platform", width=1, height=1, is_solid=False),
    TileInfo(21, "Chest", "Tiles_21.png", (160, 120, 80), "furniture", width=2, height=2, is_solid=False, is_furniture=True),
    TileInfo(26, "Altar", "Tiles_26.png", (100, 80, 100), "furniture", width=3, height=2, is_solid=False, is_furniture=True),
    TileInfo(27, "Sunflower", "Tiles_27.png", (230, 200, 50), "furniture", width=2, height=4, is_solid=False, is_furniture=True),
    TileInfo(33, "Candle", "Tiles_33.png", (200, 180, 140), "furniture", width=1, height=1, is_solid=False, is_furniture=True),
    TileInfo(34, "Chandelier", "Tiles_34.png", (180, 160, 120), "furniture", width=3, height=3, is_solid=False, is_furniture=True),
    TileInfo(35, "Jack O Lantern", "Tiles_35.png", (220, 140, 30), "furniture", width=2, height=2, is_solid=False, is_furniture=True),
    TileInfo(42, "Chain", "Tiles_42.png", (150, 150, 150), "furniture", width=1, height=1, is_solid=False, is_furniture=True),
    TileInfo(48, "Spike", "Tiles_48.png", (128, 128, 128), "hazard", width=1, height=1, is_solid=False),
    TileInfo(49, "Web", "Tiles_49.png", (220, 220, 220), "special", width=1, height=1, is_solid=False),
    TileInfo(50, "Torch", "Tiles_50.png", (255, 200, 100), "furniture", width=1, height=1, is_solid=False, is_furniture=True),
    TileInfo(77, "Skull Lantern", "Tiles_77.png", (200, 190, 170), "furniture", width=1, height=2, is_solid=False, is_furniture=True),
    TileInfo(79, "Bed", "Tiles_79.png", (160, 80, 80), "furniture", width=4, height=2, is_solid=False, is_furniture=True),
    TileInfo(85, "Tombstone", "Tiles_85.png", (130, 130, 130), "furniture", width=2, height=2, is_solid=False, is_furniture=True),
    TileInfo(86, "Loom", "Tiles_86.png", (160, 120, 80), "furniture", width=3, height=2, is_solid=False, is_furniture=True),
    TileInfo(87, "Piano", "Tiles_87.png", (50, 50, 50), "furniture", width=3, height=2, is_solid=False, is_furniture=True),
    TileInfo(88, "Dresser", "Tiles_88.png", (140, 100, 60), "furniture", width=3, height=2, is_solid=False, is_furniture=True),
    TileInfo(89, "Bench", "Tiles_89.png", (140, 100, 60), "furniture", width=3, height=1, is_solid=False, is_furniture=True),
    TileInfo(90, "Bathtub", "Tiles_90.png", (200, 200, 220), "furniture", width=4, height=2, is_solid=False, is_furniture=True),
    TileInfo(91, "Banner", "Tiles_91.png", (180, 50, 50), "furniture", width=1, height=3, is_solid=False, is_furniture=True),
    TileInfo(92, "Lamp Post", "Tiles_92.png", (100, 100, 100), "furniture", width=1, height=6, is_solid=False, is_furniture=True),
    TileInfo(93, "Tiki Torch", "Tiles_93.png", (150, 100, 50), "furniture", width=1, height=3, is_solid=False, is_furniture=True),
    TileInfo(94, "Keg", "Tiles_94.png", (120, 80, 50), "furniture", width=2, height=2, is_solid=False, is_furniture=True),
    TileInfo(95, "Chinese Lantern", "Tiles_95.png", (200, 50, 50), "furniture", width=2, height=2, is_solid=False, is_furniture=True),
    TileInfo(96, "Cooking Pot", "Tiles_96.png", (80, 80, 80), "furniture", width=2, height=2, is_solid=False, is_furniture=True),
    TileInfo(97, "Safe", "Tiles_97.png", (100, 100, 100), "furniture", width=2, height=2, is_solid=False, is_furniture=True),
    TileInfo(98, "Skull Candle", "Tiles_98.png", (200, 180, 150), "furniture", width=2, height=2, is_solid=False, is_furniture=True),
    TileInfo(100, "Book", "Tiles_100.png", (140, 100, 50), "furniture", width=1, height=1, is_solid=False, is_furniture=True),
    TileInfo(101, "Bookshelf", "Tiles_101.png", (140, 100, 50), "furniture", width=3, height=4, is_solid=False, is_furniture=True),
    TileInfo(102, "Throne", "Tiles_102.png", (180, 140, 50), "furniture", width=3, height=4, is_solid=False, is_furniture=True),
    TileInfo(103, "Bowl", "Tiles_103.png", (160, 120, 80), "furniture", width=2, height=1, is_solid=False, is_furniture=True),
    TileInfo(104, "Grandfather Clock", "Tiles_104.png", (140, 100, 60), "furniture", width=2, height=5, is_solid=False, is_furniture=True),
    TileInfo(105, "Statue", "Tiles_105.png", (128, 128, 128), "furniture", width=2, height=3, is_solid=False, is_furniture=True),
    TileInfo(106, "Sawmill", "Tiles_106.png", (140, 100, 60), "furniture", width=3, height=3, is_solid=False, is_furniture=True),
    TileInfo(114, "Anvil", "Tiles_114.png", (128, 128, 128), "furniture", width=2, height=1, is_solid=False, is_furniture=True),
    TileInfo(125, "Crystal Ball", "Tiles_125.png", (200, 100, 200), "furniture", width=2, height=2, is_solid=False, is_furniture=True),
    TileInfo(128, "Mannequin", "Tiles_128.png", (150, 100, 80), "furniture", width=2, height=3, is_solid=False, is_furniture=True),
    TileInfo(132, "Lever", "Tiles_132.png", (100, 100, 100), "furniture", width=2, height=2, is_solid=False, is_furniture=True),
    TileInfo(133, "Switch", "Tiles_133.png", (100, 100, 100), "furniture", width=1, height=1, is_solid=False, is_furniture=True),
    TileInfo(134, "Pressure Plate", "Tiles_134.png", (120, 120, 120), "furniture", width=1, height=1, is_solid=False, is_furniture=True),
    TileInfo(135, "Timer", "Tiles_135.png", (100, 100, 100), "furniture", width=1, height=1, is_solid=False, is_furniture=True),
    TileInfo(172, "Sink", "Tiles_172.png", (180, 180, 200), "furniture", width=2, height=2, is_solid=False, is_furniture=True),
    TileInfo(173, "Cannon", "Tiles_173.png", (80, 80, 80), "furniture", width=4, height=2, is_solid=False, is_furniture=True),
    TileInfo(174, "Land Mine", "Tiles_174.png", (100, 80, 80), "hazard", width=1, height=1, is_solid=False),
    TileInfo(207, "Water Fountain", "Tiles_207.png", (128, 128, 180), "furniture", width=2, height=4, is_solid=False, is_furniture=True),
    TileInfo(215, "Campfire", "Tiles_215.png", (255, 150, 50), "furniture", width=3, height=2, is_solid=False, is_furniture=True),
    TileInfo(235, "Teleporter", "Tiles_235.png", (200, 150, 50), "furniture", width=3, height=1, is_solid=False, is_furniture=True),
    TileInfo(240, "Painting", "Tiles_240.png", (150, 120, 80), "furniture", width=3, height=3, is_solid=False, is_furniture=True),
]


# =============================================================================
# WALLS - Maps to Wall_X.png
# =============================================================================

WALLS = [
    WallInfo(1, "Stone Wall", "Wall_1.png", (65, 65, 65), "natural"),
    WallInfo(2, "Dirt Wall Unsafe", "Wall_2.png", (88, 61, 46), "natural"),
    WallInfo(3, "Ebonstone Wall Unsafe", "Wall_3.png", (60, 55, 90), "natural"),
    WallInfo(4, "Wood Wall", "Wall_4.png", (102, 75, 37), "crafted"),
    WallInfo(5, "Gray Brick Wall", "Wall_5.png", (52, 52, 52), "crafted"),
    WallInfo(6, "Red Brick Wall", "Wall_6.png", (90, 40, 40), "crafted"),
    WallInfo(7, "Blue Brick Wall Unsafe", "Wall_7.png", (27, 31, 74), "dungeon"),
    WallInfo(8, "Green Brick Wall Unsafe", "Wall_8.png", (27, 47, 36), "dungeon"),
    WallInfo(9, "Pink Brick Wall Unsafe", "Wall_9.png", (74, 27, 51), "dungeon"),
    WallInfo(10, "Gold Brick Wall", "Wall_10.png", (100, 90, 25), "crafted"),
    WallInfo(11, "Silver Brick Wall", "Wall_11.png", (100, 105, 110), "crafted"),
    WallInfo(12, "Copper Brick Wall", "Wall_12.png", (95, 60, 35), "crafted"),
    WallInfo(13, "Hellstone Brick Wall Unsafe", "Wall_13.png", (60, 30, 25), "hell"),
    WallInfo(14, "Obsidian Brick Wall", "Wall_14.png", (20, 18, 35), "crafted"),
    WallInfo(15, "Mud Wall Unsafe", "Wall_15.png", (56, 40, 43), "natural"),
    WallInfo(16, "Dirt Wall", "Wall_16.png", (88, 61, 46), "crafted"),
    WallInfo(17, "Blue Brick Wall", "Wall_17.png", (27, 31, 74), "crafted"),
    WallInfo(18, "Green Brick Wall", "Wall_18.png", (27, 47, 36), "crafted"),
    WallInfo(19, "Pink Brick Wall", "Wall_19.png", (74, 27, 51), "crafted"),
    WallInfo(20, "Obsidian Back Wall Unsafe", "Wall_20.png", (15, 13, 25), "natural"),
    WallInfo(21, "Glass Wall", "Wall_21.png", (140, 170, 200), "crafted"),
    WallInfo(22, "Pearlstone Wall", "Wall_22.png", (100, 85, 95), "crafted"),
    WallInfo(23, "Iridescent Brick Wall", "Wall_23.png", (55, 60, 50), "crafted"),
    WallInfo(24, "Mudstone Brick Wall", "Wall_24.png", (45, 35, 30), "crafted"),
    WallInfo(25, "Cobalt Brick Wall", "Wall_25.png", (35, 50, 75), "crafted"),
    WallInfo(26, "Mythril Brick Wall", "Wall_26.png", (55, 80, 65), "crafted"),
    WallInfo(27, "Planked Wall", "Wall_27.png", (85, 60, 30), "crafted"),
    WallInfo(28, "Pearlstone Brick Wall", "Wall_28.png", (85, 80, 90), "crafted"),
    WallInfo(29, "Candy Cane Wall", "Wall_29.png", (180, 50, 50), "crafted"),
    WallInfo(30, "Green Candy Cane Wall", "Wall_30.png", (50, 180, 50), "crafted"),
    WallInfo(31, "Snow Brick Wall", "Wall_31.png", (140, 150, 160), "crafted"),
    WallInfo(32, "Adamantite Beam Wall", "Wall_32.png", (95, 40, 55), "crafted"),
    WallInfo(33, "Demonite Brick Wall", "Wall_33.png", (50, 45, 65), "crafted"),
    WallInfo(34, "Sandstone Brick Wall", "Wall_34.png", (100, 88, 55), "crafted"),
    WallInfo(35, "Ebonstone Brick Wall", "Wall_35.png", (55, 50, 80), "crafted"),
    WallInfo(36, "Red Stucco Wall", "Wall_36.png", (130, 70, 55), "crafted"),
    WallInfo(37, "Yellow Stucco Wall", "Wall_37.png", (140, 130, 80), "crafted"),
    WallInfo(38, "Green Stucco Wall", "Wall_38.png", (70, 110, 60), "crafted"),
    WallInfo(39, "Gray Stucco Wall", "Wall_39.png", (95, 95, 95), "crafted"),
    WallInfo(40, "Ebonwood Wall", "Wall_40.png", (65, 55, 75), "crafted"),
    WallInfo(41, "Rich Mahogany Wall", "Wall_41.png", (65, 30, 28), "crafted"),
    WallInfo(42, "Pearlwood Wall", "Wall_42.png", (105, 95, 75), "crafted"),
    TileInfo(43, "Rainbow Brick Wall", "Wall_43.png", (200, 150, 200), "crafted"),
    WallInfo(44, "Tin Brick Wall", "Wall_44.png", (90, 85, 75), "crafted"),
    WallInfo(45, "Tungsten Brick Wall", "Wall_45.png", (60, 70, 55), "crafted"),
    WallInfo(46, "Platinum Brick Wall", "Wall_46.png", (100, 100, 105), "crafted"),
    WallInfo(59, "Living Wood Wall", "Wall_59.png", (79, 57, 30), "crafted"),
    WallInfo(60, "Living Leaf Wall", "Wall_60.png", (35, 75, 25), "crafted"),
    WallInfo(62, "Hive Wall", "Wall_62.png", (130, 85, 22), "natural"),
    WallInfo(63, "Lihzahrd Brick Wall Unsafe", "Wall_63.png", (50, 40, 8), "temple"),
    WallInfo(64, "Slime Block Wall", "Wall_64.png", (55, 90, 200), "crafted"),
    WallInfo(65, "Bone Block Wall", "Wall_65.png", (130, 125, 110), "crafted"),
    WallInfo(66, "Flesh Block Wall", "Wall_66.png", (85, 35, 40), "crafted"),
    WallInfo(67, "Sunplate Wall", "Wall_67.png", (140, 120, 80), "crafted"),
    WallInfo(68, "Shadewood Wall", "Wall_68.png", (50, 38, 55), "crafted"),
    WallInfo(69, "Spooky Wood Wall", "Wall_69.png", (35, 28, 42), "crafted"),
    WallInfo(78, "Granite Wall", "Wall_78.png", (30, 28, 60), "natural"),
    WallInfo(79, "Marble Wall", "Wall_79.png", (130, 125, 120), "natural"),
    WallInfo(82, "Boreal Wood Wall", "Wall_82.png", (90, 80, 70), "crafted"),
    WallInfo(83, "Palm Wood Wall", "Wall_83.png", (110, 100, 70), "crafted"),
]


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_all_tiles() -> list[TileInfo]:
    """Get all tiles (blocks)."""
    return TILES.copy()


def get_solid_tiles() -> list[TileInfo]:
    """Get only solid 1x1 tiles (for image conversion)."""
    return [t for t in TILES if t.is_solid and t.width == 1 and t.height == 1]


def get_all_walls() -> list[WallInfo]:
    """Get all walls."""
    return WALLS.copy()


def get_tile_by_id(tile_id: int) -> Optional[TileInfo]:
    """Find tile by ID."""
    for tile in TILES:
        if tile.id == tile_id:
            return tile
    return None


def get_wall_by_id(wall_id: int) -> Optional[WallInfo]:
    """Find wall by ID."""
    for wall in WALLS:
        if wall.id == wall_id:
            return wall
    return None


def list_all_texture_files() -> list[str]:
    """List all texture files needed for tiles and walls."""
    files = set()
    for tile in TILES:
        files.add(tile.texture_file)
    for wall in WALLS:
        files.add(wall.texture_file)
    return sorted(files)


if __name__ == "__main__":
    print("Terraria Texture Mapping")
    print("=" * 50)
    print(f"\nTiles: {len(TILES)}")
    print(f"Solid 1x1 tiles: {len(get_solid_tiles())}")
    print(f"Walls: {len(WALLS)}")
    print(f"\nTotal texture files needed: {len(list_all_texture_files())}")
    
    print("\nTile categories:")
    categories = set(t.category for t in TILES)
    for cat in sorted(categories):
        count = len([t for t in TILES if t.category == cat])
        print(f"  {cat}: {count}")
    
    print("\nSample texture mappings:")
    for tile in TILES[:10]:
        print(f"  {tile.id}: {tile.name} -> {tile.texture_file}")
