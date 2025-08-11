# VoxelScripts: Slice PNG to MagicaVoxel

A small Python CLI to convert a sliced sprite sheet into a MagicaVoxel `.vox` model. The image must be 64 px tall and its width must be a multiple of 64. Each 64×64 tile (left → right) becomes a layer along Z, producing a 64×64×N volume.

## Requirements
- Python 3.9+
- Pillow

Install:
```bash
pip install pillow
```

## Script
- File: `slice_to_vox.py`
- Input: sliced PNG (RGBA recommended)
- Output: `.vox` with embedded palette

## Usage
```bash
python slice_to_vox.py /path/to/sliced.png -o out.vox
```
Example:
```bash
python slice_to_vox.py \
  "/run/media/Flan/Big E/Proyectos/Tools/VoxelScripts/motocross_slice.png" \
  -o "/run/media/Flan/Big E/Proyectos/Tools/VoxelScripts/motocross_slice.vox"
```
If `-o` is omitted, the output path is the input path with `.vox` extension.

## How it works
- Calculates number of cells: `cells = width // 64`.
- Iterates tiles left→right; for each tile, stacks non‑transparent pixels as the layer at depth `d`.
- Top of the image is mapped to the top (Y is flipped so the model appears upright in MagicaVoxel).

## Palette
- Extracts unique colors from all non‑transparent pixels, preserving encounter order.
- Writes the palette into the `.vox` RGBA chunk.
- Palette index 0 is a dummy placeholder (transparent/black). Actual colors occupy indices 1..K in the RGBA palette.
- Voxel color indices start at 2 so the first real color aligns to palette slot 1. Index 1 is never used.
- Up to 254 unique colors are supported (plus the dummy at 0). If exceeded, the script exits with an error.

## Image constraints
- Height must be exactly 64 px.
- Width must be a multiple of 64 px.
- Transparent pixels (alpha == 0) are ignored.

## Notes
- If the palette appears off, ensure your PNG uses straight (not premultiplied) alpha and consistent color management.
- MagicaVoxel does not use per‑color alpha for voxel visibility; empty voxels come from transparent pixels in the input.
