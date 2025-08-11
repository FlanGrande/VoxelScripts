import argparse
import struct
import sys
from collections import OrderedDict
from PIL import Image


def _chunk(name: str, content: bytes, children: bytes = b"") -> bytes:
    return struct.pack("<4sii", name.encode("ascii"), len(content), len(children)) + content + children


def _save_vox(path: str, size_xyz: tuple[int, int, int], voxels: list[tuple[int, int, int, int]], palette: list[tuple[int, int, int, int]]):
    size_chunk = _chunk("SIZE", struct.pack("<iii", *size_xyz))
    xyzi_body = struct.pack("<i", len(voxels)) + b"".join(struct.pack("<BBBB", *v) for v in voxels)
    xyzi_chunk = _chunk("XYZI", xyzi_body)
    pal = [(0, 0, 0, 0)] + palette[:]
    if len(pal) < 256:
        pal += [(0, 0, 0, 0)] * (256 - len(pal))
    else:
        pal = pal[:256]
    rgba_body = b"".join(struct.pack("<BBBB", *rgba) for rgba in pal[:256])
    rgba_chunk = _chunk("RGBA", rgba_body)
    children = size_chunk + xyzi_chunk + rgba_chunk
    with open(path, "wb") as f:
        f.write(b"VOX " + struct.pack("<i", 150))
        f.write(struct.pack("<4sii", b"MAIN", 0, len(children)))
        f.write(children)


def slice_to_vox(src: str, out: str):
    img = Image.open(src).convert("RGBA")
    w, h = img.size
    if h != 64 or w % 64 != 0:
        print("Image must be 64px tall and width multiple of 64.", file=sys.stderr)
        sys.exit(1)
    cells = w // 64
    px = img.load()

    colors: list[tuple[int, int, int, int]] = []
    cmap: "OrderedDict[tuple[int, int, int, int], int]" = OrderedDict()
    voxels: list[tuple[int, int, int, int]] = []

    for d in range(cells):
        ox = d * 64
        for y in range(64):
            for x in range(64):
                r, g, b, a = px[ox + x, y]
                if a == 0:
                    continue
                color = (r, g, b, a)
                if color not in cmap:
                    if len(colors) >= 254:
                        print("More than 254 colors detected (palette index 0 is reserved).", file=sys.stderr)
                        sys.exit(1)
                    cmap[color] = len(colors)
                    colors.append(color)
                idx = cmap[color] + 2
                voxels.append((x, 63 - y, d, idx))

    _save_vox(out, (64, 64, cells), voxels, colors)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input", help="Path to sliced PNG")
    ap.add_argument("-o", "--output", help="Output .vox path", default=None)
    args = ap.parse_args()
    out = args.output or (args.input.rsplit(".", 1)[0] + ".vox")
    slice_to_vox(args.input, out)
    print(out)


if __name__ == "__main__":
    main()
