#!/usr/bin/env python3
"""Build train/val CSV for new100 mmap folders (5 clips/class, *_05 = val).

Usage (Ubuntu, after heatmaps exist):
  python3 build_new100_manifest.py \
    --mmap-root ~/harri_capture/new100/mmap \
    --out-dir ~/mmCLIP/data/splits
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

# class_id matches your 7-class mmap training
CLASS_MAP = {
    "jump": 1,
    "kick": 8,
    "punch": 41,
    "wave_hand": 10,
    "side_walk": 31,
    "stand_still": 15,
    "nodding_head": 52,
}

CLASS_NAME = {
    "jump": "jump",
    "kick": "kick",
    "punch": "punch",
    "wave_hand": "wave hand",
    "side_walk": "side walk",
    "stand_still": "stand still",
    "nodding_head": "nodding head",
}


def parse_stem(stem: str) -> tuple[str, str] | None:
    # e.g. jump_01_17839..._mmap  OR jump_01_mmap
    s = stem
    if s.endswith("_mmap"):
        s = s[: -len("_mmap")]
    for key in CLASS_MAP:
        if s.startswith(key + "_"):
            rest = s[len(key) + 1 :]
            # rest like 01 or 01_1783...
            num = rest.split("_")[0]
            return key, num
    return None


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--mmap-root", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, required=True)
    args = p.parse_args()

    rows = []
    for folder in sorted(args.mmap_root.iterdir()):
        if not folder.is_dir():
            continue
        if not (folder / "time_dop.npy").is_file():
            print(f"[skip] no time_dop.npy in {folder.name}")
            continue
        parsed = parse_stem(folder.name)
        if not parsed:
            print(f"[skip] cannot parse class from {folder.name}")
            continue
        key, num = parsed
        split = "val" if num == "05" else "train"
        rows.append(
            {
                "trial_folder": str(folder.resolve()),
                "class_id": CLASS_MAP[key],
                "class_name": CLASS_NAME[key],
                "split": split,
            }
        )

    args.out_dir.mkdir(parents=True, exist_ok=True)
    all_csv = args.out_dir / "new100_mmap_manifest.csv"
    train_csv = args.out_dir / "new100_train.csv"
    val_csv = args.out_dir / "new100_val.csv"

    fields = ["trial_folder", "class_id", "class_name", "split"]
    with all_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    train_rows = [r for r in rows if r["split"] == "train"]
    val_rows = [r for r in rows if r["split"] == "val"]
    for path, subset in ((train_csv, train_rows), (val_csv, val_rows)):
        with path.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(subset)

    print(f"wrote {all_csv} ({len(rows)} rows)")
    print(f"train={len(train_rows)} val={len(val_rows)}")
    from collections import Counter

    print("per-class:", Counter(r["class_name"] for r in rows))


if __name__ == "__main__":
    main()
