# Build tool icons using .NET System.Drawing for better quality
# Also extracts game textures for tool icons
# Background removal and color matching to app theme

Add-Type -AssemblyName System.Drawing

$iconsDir = "$PWD\icons"
if (-not (Test-Path $iconsDir)) { New-Item -ItemType Directory -Path $iconsDir | Out-Null }

# App background color for matching
$appBgColor = [System.Drawing.Color]::FromArgb(255, 22, 27, 34)  # #161b22

function Remove-Background {
    param([System.Drawing.Bitmap]$img)
    
    # Sample corners to detect background
    $w = $img.Width
    $h = $img.Height
    $corners = @(
        $img.GetPixel(0, 0),
        $img.GetPixel($w - 1, 0),
        $img.GetPixel(0, $h - 1),
        $img.GetPixel($w - 1, $h - 1)
    )
    
    # Find most common corner color
    $colorCounts = @{}
    foreach ($c in $corners) {
        $key = "$($c.R),$($c.G),$($c.B),$($c.A)"
        if ($colorCounts.ContainsKey($key)) { $colorCounts[$key]++ }
        else { $colorCounts[$key] = 1 }
    }
    $bgKey = ($colorCounts.GetEnumerator() | Sort-Object Value -Descending | Select-Object -First 1).Key
    $bgParts = $bgKey -split ','
    $bgR = [int]$bgParts[0]; $bgG = [int]$bgParts[1]; $bgB = [int]$bgParts[2]; $bgA = [int]$bgParts[3]
    
    # Make background pixels transparent
    $tolerance = 40
    for ($y = 0; $y -lt $h; $y++) {
        for ($x = 0; $x -lt $w; $x++) {
            $pixel = $img.GetPixel($x, $y)
            $diffR = [Math]::Abs($pixel.R - $bgR)
            $diffG = [Math]::Abs($pixel.G - $bgG)
            $diffB = [Math]::Abs($pixel.B - $bgB)
            
            if ($diffR -lt $tolerance -and $diffG -lt $tolerance -and $diffB -lt $tolerance) {
                $img.SetPixel($x, $y, [System.Drawing.Color]::Transparent)
            }
        }
    }
    return $img
}

function Get-ContentBounds {
    param([System.Drawing.Bitmap]$img)
    
    $w = $img.Width; $h = $img.Height
    $minX = $w; $minY = $h; $maxX = 0; $maxY = 0
    
    for ($y = 0; $y -lt $h; $y++) {
        for ($x = 0; $x -lt $w; $x++) {
            $pixel = $img.GetPixel($x, $y)
            if ($pixel.A -gt 20) {
                if ($x -lt $minX) { $minX = $x }
                if ($y -lt $minY) { $minY = $y }
                if ($x -gt $maxX) { $maxX = $x }
                if ($y -gt $maxY) { $maxY = $y }
            }
        }
    }
    
    if ($maxX -le $minX -or $maxY -le $minY) {
        return @{ X = 0; Y = 0; W = $w; H = $h }
    }
    return @{ X = $minX; Y = $minY; W = $maxX - $minX + 1; H = $maxY - $minY + 1 }
}

function Extract-Icon {
    param(
        [System.Drawing.Bitmap]$src,
        [int]$x, [int]$y, [int]$w, [int]$h,
        [string]$outPath,
        [int]$targetSize = 32
    )
    
    # Crop the region
    $rect = [System.Drawing.Rectangle]::new($x, $y, $w, $h)
    $cropped = $src.Clone($rect, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
    
    # Remove background
    $cropped = Remove-Background -img $cropped
    
    # Find content bounds
    $bounds = Get-ContentBounds -img $cropped
    
    # Get content region
    $contentRect = [System.Drawing.Rectangle]::new($bounds.X, $bounds.Y, $bounds.W, $bounds.H)
    $content = $cropped.Clone($contentRect, $cropped.PixelFormat)
    
    # Scale to fit 80% of target size
    $usable = [int]($targetSize * 0.80)
    $scale = [Math]::Min($usable / $bounds.W, $usable / $bounds.H)
    $newW = [Math]::Max(1, [int]($bounds.W * $scale))
    $newH = [Math]::Max(1, [int]($bounds.H * $scale))
    
    # Create output with transparency
    $output = New-Object System.Drawing.Bitmap($targetSize, $targetSize, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
    $g = [System.Drawing.Graphics]::FromImage($output)
    $g.Clear([System.Drawing.Color]::Transparent)
    $g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::NearestNeighbor
    $g.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::Half
    
    # Center in output
    $destX = [int](($targetSize - $newW) / 2)
    $destY = [int](($targetSize - $newH) / 2)
    $g.DrawImage($content, $destX, $destY, $newW, $newH)
    $g.Dispose()
    
    $output.Save($outPath, [System.Drawing.Imaging.ImageFormat]::Png)
    $cropped.Dispose()
    $content.Dispose()
    $output.Dispose()
    Write-Host "Saved: $(Split-Path $outPath -Leaf)"
}

function Extract-GameTexture {
    param(
        [string]$srcPath,
        [int]$x, [int]$y, [int]$w, [int]$h,
        [string]$outPath,
        [int]$targetSize = 32
    )
    
    $src = [System.Drawing.Image]::FromFile($srcPath)
    $bitmap = New-Object System.Drawing.Bitmap($src)
    $src.Dispose()
    
    # Crop
    $rect = [System.Drawing.Rectangle]::new($x, $y, $w, $h)
    $cropped = $bitmap.Clone($rect, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
    $bitmap.Dispose()
    
    # Create output centered
    $output = New-Object System.Drawing.Bitmap($targetSize, $targetSize, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
    $g = [System.Drawing.Graphics]::FromImage($output)
    $g.Clear([System.Drawing.Color]::Transparent)
    $g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::NearestNeighbor
    $g.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::Half
    
    # Scale and center
    $scale = [Math]::Min(($targetSize * 0.9) / $w, ($targetSize * 0.9) / $h)
    $newW = [Math]::Max(1, [int]($w * $scale))
    $newH = [Math]::Max(1, [int]($h * $scale))
    $destX = [int](($targetSize - $newW) / 2)
    $destY = [int](($targetSize - $newH) / 2)
    $g.DrawImage($cropped, $destX, $destY, $newW, $newH)
    $g.Dispose()
    
    $output.Save($outPath, [System.Drawing.Imaging.ImageFormat]::Png)
    $cropped.Dispose()
    $output.Dispose()
    Write-Host "Saved: $(Split-Path $outPath -Leaf)"
}

# Extract from icons2.png (3x3 grid)
Write-Host "`n=== Extracting from icons2.png ==="
$icons2 = [System.Drawing.Image]::FromFile("$PWD\icons2.png")
$bitmap2 = New-Object System.Drawing.Bitmap($icons2)
$icons2.Dispose()

$cellW = [int]($bitmap2.Width / 3)
$cellH = [int]($bitmap2.Height / 3)

# Grid layout: Row 0: circle, select, brush | Row 1: line, eraser, fill | Row 2: paint_bucket, palette, zoom
$iconNames = @(
    @("circle", "select", "brush"),
    @("line", "erase", "fill"),
    @("paint_bucket", "palette", "zoom")
)

for ($row = 0; $row -lt 3; $row++) {
    for ($col = 0; $col -lt 3; $col++) {
        $name = $iconNames[$row][$col]
        $x = $col * $cellW
        $y = $row * $cellH
        Extract-Icon -src $bitmap2 -x $x -y $y -w $cellW -h $cellH -outPath "$iconsDir\$name.png"
    }
}
$bitmap2.Dispose()

# Extract game textures for block/wall tools
Write-Host "`n=== Extracting game textures ==="

# Stone block (Tiles_1) - solid center frame
Extract-GameTexture -srcPath "$PWD\textures\Tiles_1.png" -x 19 -y 19 -w 16 -h 16 -outPath "$iconsDir\block.png"

# Wood wall (Wall_4) - center 16x16 from a good frame
Extract-GameTexture -srcPath "$PWD\textures\Wall_4.png" -x 334 -y 118 -w 16 -h 16 -outPath "$iconsDir\wall.png"

Write-Host "`n=== Done! Icons saved to: $iconsDir ==="
