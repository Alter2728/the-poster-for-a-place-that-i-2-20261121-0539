"""Copy the pre-rendered entry.png to the make.fun output directory.

Stdlib only. Reads MAKEFUN_OUTPUT_DIR (default /output), creates it if
needed, and copies entry.png from beside this file to <dir>/entry.png.
entry.png is rendered by draw.py (PIL) and committed beside this file.
The output is deterministic: copying the committed entry.png byte-for-byte
means every run produces exactly the same file, with no rendering variance.
"""
import os
import shutil
from pathlib import Path


def main():
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    src = Path(__file__).resolve().parent / "entry.png"
    dst = out_dir / "entry.png"
    shutil.copyfile(src, dst)
    print(f"copied {src} -> {dst}")


if __name__ == "__main__":
    main()
