#!/usr/bin/env python3
"""Batch: new100 .bin files → mmAP heatmap folders.

Usage (Ubuntu, conda mmCLIP):
  cd ~/mmCLIP
  python ~/harri_capture/batch_bins_to_mmap.py \
    --bin-dir ~/harri_capture/new100/bins \
    --out-dir ~/harri_capture/new100/mmap
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--bin-dir", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, required=True)
    p.add_argument("--mmclip-root", type=Path, default=Path.home() / "mmCLIP")
    p.add_argument("--noise", action="store_true")
    args = p.parse_args()

    gen = args.mmclip_root / "generate_mmap_heatmaps.py"
    if not gen.is_file():
        print(f"ERROR: missing {gen}", file=sys.stderr)
        sys.exit(1)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    bins = sorted(args.bin_dir.glob("*.bin"))
    if not bins:
        print(f"ERROR: no .bin in {args.bin_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"[batch] {len(bins)} bins → {args.out_dir}")
    ok = 0
    for bin_path in bins:
        # jump_01_1783....bin → prefix jump_01_1783....
        prefix = bin_path.stem
        print(f"\n==== {prefix} ====")
        target = args.mmclip_root / f"{prefix}.bin"
        shutil.copy2(bin_path, target)
        cmd = [sys.executable, str(gen), prefix]
        if not args.noise:
            cmd.append("--no-noise")
        proc = subprocess.run(cmd, cwd=str(args.mmclip_root))
        if proc.returncode != 0:
            print(f"[batch] FAILED {prefix}", file=sys.stderr)
            continue

        # find folder with npy
        candidates = [
            args.mmclip_root / f"{prefix}_mmap",
            args.mmclip_root / prefix,
            args.mmclip_root / "data" / f"{prefix}_mmap",
        ]
        found = None
        for c in candidates:
            if c.is_dir() and (c / "time_dop.npy").is_file():
                found = c
                break
        if found is None:
            hits = list(args.mmclip_root.glob(f"**/{prefix}*/time_dop.npy"))
            if hits:
                found = hits[0].parent
        if found is None:
            print(f"[batch] heatmaps not found for {prefix}", file=sys.stderr)
            continue

        dest = args.out_dir / f"{prefix}_mmap"
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(found, dest)
        print(f"[batch] ok → {dest}")
        ok += 1

    print(f"\n[batch] done {ok}/{len(bins)}")


if __name__ == "__main__":
    main()
