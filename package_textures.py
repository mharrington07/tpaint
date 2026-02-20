"""
Package Terraria textures for distribution.
Creates textures.zip containing only the Tiles_*.png and Wall_*.png files
needed for TPaint.

Upload the resulting textures.zip to GitHub Releases.
"""

import zipfile
import os
from pathlib import Path

TEXTURE_DIR = Path(__file__).parent / "textures"
OUTPUT_FILE = Path(__file__).parent / "textures.zip"


def package_textures():
    """Create a zip archive of texture files."""
    
    # Find all tile and wall textures
    tiles = list(TEXTURE_DIR.glob("Tiles_*.png"))
    walls = list(TEXTURE_DIR.glob("Wall_*.png"))
    
    if not tiles:
        print("No tile textures found in textures/ folder!")
        print("Run setup.py first to extract textures from Terraria.")
        return False
    
    print(f"Found {len(tiles)} tiles and {len(walls)} walls")
    
    # Create zip file
    with zipfile.ZipFile(OUTPUT_FILE, 'w', zipfile.ZIP_DEFLATED) as zf:
        for f in tiles:
            # Store just the filename, not full path
            zf.write(f, f.name)
            
        for f in walls:
            zf.write(f, f.name)
    
    # Get file size
    size_mb = OUTPUT_FILE.stat().st_size / (1024 * 1024)
    
    print(f"\nCreated: {OUTPUT_FILE}")
    print(f"Size: {size_mb:.1f} MB")
    print(f"Files: {len(tiles) + len(walls)}")
    print()
    print("Upload this file to GitHub Releases:")
    print("  https://github.com/mharrington07/tpaint/releases")
    print()
    print("Tag suggestion: textures-v1.0")
    
    return True


if __name__ == "__main__":
    package_textures()
