#!/usr/bin/env python3
"""Streaming-friendly local inference for Ubuntu RTX 4090.

Improves the Friday/Monday live loop without changing mmAP math:
  - Snapshots the .bin before inference so rolling capture can keep running
  - Waits until the bin is stable (debounce) so mid-write windows aren't classified
  - Unique heatmap prefix per pass (no live_capture_mmap stomping)
  - Writes status=processing so the display feels live during the ~12s wait
  - Optional --mode trigger: press Enter after one clean action (best for video)

Usage (on Ubuntu, from ~/mmCLIP):
  export MMCLIP_7CLASS_CKPT=~/mmCLIP/src/linear_probe_7class_mmap/best.pt
  python demo_realtime/stream_live_pipeline.py --mode trigger
  python demo_realtime/stream_live_pipeline.py --mode auto --min-interval 20 --stable-s 1.5
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

MMCLIP_ROOT = Path(__file__).resolve().parents[1]
LIVE_INFER = Path(__file__).resolve().parent / "live_infer.py"
DEFAULT_BIN = Path.home() / "harri_capture" / "adc_direct_save.bin"
DEFAULT_STATUS = Path.home() / "harri_capture" / "live_status.json"
SNAP_DIR = Path.home() / "harri_capture" / "stream_snaps"


def file_sig(path: Path) -> tuple[int, int] | None:
    try:
        st = path.stat()
        return int(st.st_mtime_ns), int(st.st_size)
    except FileNotFoundError:
        return None


def write_status(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    os.replace(tmp, path)


def wait_stable(bin_path: Path, stable_s: float, poll: float) -> tuple[int, int] | None:
    """Return signature once mtime/size stop changing for stable_s seconds."""
    last = file_sig(bin_path)
    if last is None:
        return None
    changed_at = time.time()
    while True:
        time.sleep(poll)
        cur = file_sig(bin_path)
        if cur is None:
            return None
        if cur != last:
            last = cur
            changed_at = time.time()
            continue
        if time.time() - changed_at >= stable_s:
            return cur


def run_infer(
    bin_path: Path,
    out_path: Path,
    prefix: str,
    hm_dir: Path,
    noise: bool,
) -> tuple[int, dict | None, float]:
    cmd = [
        sys.executable,
        str(LIVE_INFER),
        "--bin",
        str(bin_path),
        "--out",
        str(out_path),
        "--prefix",
        prefix,
        "--hm-dir",
        str(hm_dir),
    ]
    if noise:
        cmd.append("--noise")
    t0 = time.time()
    proc = subprocess.run(
        cmd,
        cwd=str(MMCLIP_ROOT),
        capture_output=True,
        text=True,
        env={**os.environ, "CUDA_VISIBLE_DEVICES": os.environ.get("CUDA_VISIBLE_DEVICES", "0")},
    )
    elapsed = time.time() - t0
    payload = None
    if out_path.is_file():
        try:
            payload = json.loads(out_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    if proc.returncode != 0 and proc.stderr:
        print(proc.stderr[-2000:], file=sys.stderr)
    return proc.returncode, payload, elapsed


def classify_once(
    src_bin: Path,
    status_path: Path,
    pass_n: int,
    noise: bool,
) -> None:
    SNAP_DIR.mkdir(parents=True, exist_ok=True)
    snap = SNAP_DIR / f"pass_{pass_n:04d}.bin"
    shutil.copy2(src_bin, snap)

    prefix = f"stream_pass_{pass_n:04d}"
    hm_dir = SNAP_DIR / f"hm_{pass_n:04d}"

    write_status(
        status_path,
        {
            "status": "processing",
            "pass": pass_n,
            "prediction": "…",
            "confidence": None,
            "message": f"Pass {pass_n}: building heatmaps + classifying (~10–15s)",
            "timestamp": time.time(),
            "bin_path": str(snap),
        },
    )
    print(f"[stream] pass={pass_n} snapped {snap.name} ({snap.stat().st_size / 1e6:.1f} MB)")
    print(f"[stream] pass={pass_n} inferring…")

    code, payload, elapsed = run_infer(snap, status_path, prefix, hm_dir, noise)

    if code == 0 and payload and not payload.get("error"):
        payload["status"] = "ready"
        payload["pass"] = pass_n
        payload["pipeline_elapsed_s"] = round(elapsed, 2)
        write_status(status_path, payload)
        pred = payload.get("prediction", "?")
        conf = payload.get("confidence")
        conf_s = f" ({100 * float(conf):.1f}%)" if conf is not None else ""
        print(f"[stream] pass={pass_n} ok in {elapsed:.1f}s -> {pred}{conf_s}")
    else:
        err = {
            "status": "error",
            "pass": pass_n,
            "prediction": "ERROR",
            "error": (payload or {}).get("error") or f"live_infer exit {code}",
            "elapsed_s": round(elapsed, 2),
            "timestamp": time.time(),
        }
        write_status(status_path, err)
        print(f"[stream] pass={pass_n} FAILED in {elapsed:.1f}s", file=sys.stderr)


def main() -> None:
    p = argparse.ArgumentParser(description="Streaming local 4090 inference")
    p.add_argument("--bin", type=Path, default=DEFAULT_BIN)
    p.add_argument("--out", type=Path, default=DEFAULT_STATUS)
    p.add_argument(
        "--mode",
        choices=("trigger", "auto"),
        default="trigger",
        help="trigger=Enter after one action (best accuracy/video); auto=debounce+interval",
    )
    p.add_argument("--interval", type=float, default=0.5, help="Poll sleep in auto mode")
    p.add_argument("--min-interval", type=float, default=20.0, help="Min seconds between auto passes")
    p.add_argument(
        "--stable-s",
        type=float,
        default=1.5,
        help="Bin must stop changing this long before auto classify",
    )
    p.add_argument("--noise", action="store_true")
    args = p.parse_args()

    ckpt = os.environ.get(
        "MMCLIP_7CLASS_CKPT",
        str(MMCLIP_ROOT / "src" / "linear_probe_7class_mmap" / "best.pt"),
    )
    print(f"[stream] mode={args.mode}")
    print(f"[stream] bin={args.bin}")
    print(f"[stream] status -> {args.out}")
    print(f"[stream] ckpt -> {ckpt}")
    if not LIVE_INFER.is_file():
        print(f"ERROR: missing {LIVE_INFER}", file=sys.stderr)
        sys.exit(1)

    write_status(
        args.out,
        {
            "status": "idle",
            "prediction": "—",
            "message": "Waiting — do one action, then classify",
            "timestamp": time.time(),
        },
    )

    pass_n = 0

    if args.mode == "trigger":
        print("[stream] Press Enter to classify current window (Ctrl+C to quit).")
        print("[stream] Protocol: still 2s → ONE action 12–15s → freeze → Enter")
        while True:
            try:
                input()
            except EOFError:
                break
            if not args.bin.is_file():
                print(f"[stream] missing {args.bin}", file=sys.stderr)
                continue
            # brief stability so we don't copy mid-flush
            sig = wait_stable(args.bin, max(0.3, args.stable_s * 0.5), 0.2)
            if sig is None:
                print("[stream] bin disappeared", file=sys.stderr)
                continue
            pass_n += 1
            classify_once(args.bin, args.out, pass_n, args.noise)
        return

    # auto mode
    print(
        f"[stream] auto: stable_s={args.stable_s}s, min_interval={args.min_interval}s"
    )
    last_sig: tuple[int, int] | None = None
    last_done = 0.0
    while True:
        if not args.bin.is_file():
            print(f"[stream] waiting for {args.bin.name}…")
            time.sleep(args.interval)
            continue
        if time.time() - last_done < args.min_interval:
            time.sleep(args.interval)
            continue
        sig = wait_stable(args.bin, args.stable_s, args.interval)
        if sig is None or sig == last_sig:
            time.sleep(args.interval)
            continue
        last_sig = sig
        pass_n += 1
        classify_once(args.bin, args.out, pass_n, args.noise)
        last_done = time.time()


if __name__ == "__main__":
    main()
