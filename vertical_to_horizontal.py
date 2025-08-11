import argparse
import os
import sys
from PIL import Image


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input", help="Path to vertical sliced PNG (width=64, height multiple of 64)")
    ap.add_argument("-o", "--output", help="Output PNG path", default=None)
    args = ap.parse_args()

    img = Image.open(args.input)
    w, h = img.size
    if w != 64 or h % 64 != 0:
        print("Input must be vertical strip of 64x64 tiles (width=64, height multiple of 64).", file=sys.stderr)
        sys.exit(1)

    n = h // 64
    out_img = Image.new(img.mode, (n * 64, 64))

    for i in range(n):
        src_i = n - 1 - i
        tile = img.crop((0, src_i * 64, 64, (src_i + 1) * 64))
        out_img.paste(tile, (i * 64, 0))

    out_path = args.output or (os.path.splitext(args.input)[0] + "_h.png")
    out_img.save(out_path)
    print(out_path)


if __name__ == "__main__":
    main()
