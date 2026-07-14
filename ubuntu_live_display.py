#!/usr/bin/env python3
"""
mmCLIP advanced live dashboard for Ubuntu.

Polls live_status.json and shows:
  - Large prediction + confidence
  - Per-class probability bars
  - TD / TR / TA heatmaps from hm_dir (when present)
  - Pass / latency / status (idle, processing, ready)

Deps: Python 3 + tkinter + numpy (usual). Pillow optional (better resize).

Usage:
  python3 ~/harri_capture/ubuntu_live_display.py
  python3 ~/harri_capture/ubuntu_live_display.py --json ~/harri_capture/live_status.json
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from tkinter import Canvas, Frame, Label, Tk, font as tkfont

import numpy as np

try:
    from PIL import Image, ImageTk

    HAS_PIL = True
except ImportError:
    HAS_PIL = False


# --- theme (instrumentation / warm amber, not purple-glass AI defaults) ---
BG = "#0e1114"
BG_PANEL = "#161b22"
BG_BAR = "#222a33"
FG = "#e8eef4"
FG_DIM = "#8b9aab"
ACCENT = "#f0a05a"
ACCENT_2 = "#5ec4b0"
WARN = "#e9c46a"
ERR = "#e76f51"
GRID = "#2a3440"

CLASS_ORDER = [
    "jump",
    "kick",
    "punch",
    "wave hand",
    "side walk",
    "stand still",
    "nodding head",
]


def _turbo_like(x: np.ndarray) -> np.ndarray:
    """Map [0,1] → RGB uint8 without matplotlib (approx. hot-scientific)."""
    x = np.clip(x, 0.0, 1.0)
    r = np.clip(1.5 * x - 0.1, 0, 1)
    g = np.clip(1.5 * np.sin(np.pi * x) ** 1.2, 0, 1)
    b = np.clip(1.4 * (1.0 - x) ** 0.7, 0, 1)
    # shift toward amber-cyan instrumentation look
    rgb = np.stack([0.55 * r + 0.45 * x, 0.35 * g + 0.4 * x, 0.7 * b + 0.15 * (1 - x)], axis=-1)
    return (255 * np.clip(rgb, 0, 1)).astype(np.uint8)


def load_heatmap_rgb(hm_dir: Path, stem: str, max_w: int = 420, max_h: int = 220) -> np.ndarray | None:
    candidates = [hm_dir / f"{stem}.npy", hm_dir / f"time_{stem}.npy"]
    if stem == "dop":
        candidates += [hm_dir / "time_dop.npy", hm_dir / "doppler.npy", hm_dir / "time_doppler.npy"]
    path = next((p for p in candidates if p.is_file()), None)
    if path is None:
        return None
    arr = np.load(path).astype(np.float32)
    if arr.ndim != 2 or arr.size == 0:
        return None
    # display time on x, feature on y (flip ud so low bins at bottom feel natural for TD)
    lo, hi = float(np.percentile(arr, 2)), float(np.percentile(arr, 98))
    if hi <= lo:
        lo, hi = float(arr.min()), float(arr.max())
    if hi <= lo:
        norm = np.zeros_like(arr)
    else:
        norm = (arr - lo) / (hi - lo)
    rgb = _turbo_like(norm)
    rgb = np.flipud(rgb)

    h, w = rgb.shape[:2]
    scale = min(max_w / max(w, 1), max_h / max(h, 1), 1.0)
    nh, nw = max(1, int(h * scale)), max(1, int(w * scale))
    if HAS_PIL:
        img = Image.fromarray(rgb, mode="RGB").resize((nw, nh), Image.BILINEAR)
        return np.asarray(img)
    # nearest-neighbor fallback
    ys = (np.linspace(0, h - 1, nh)).astype(int)
    xs = (np.linspace(0, w - 1, nw)).astype(int)
    return rgb[ys][:, xs]


def rgb_to_photo(root: Tk, rgb: np.ndarray):
    if HAS_PIL:
        return ImageTk.PhotoImage(Image.fromarray(rgb, mode="RGB"))
    h, w, _ = rgb.shape
    header = f"P6 {w} {h} 255\n".encode("ascii")
    return __import__("tkinter").PhotoImage(master=root, data=header + rgb.tobytes())


class ProbBars(Frame):
    def __init__(self, master, **kw):
        super().__init__(master, bg=BG_PANEL, **kw)
        self.canvas = Canvas(self, bg=BG_PANEL, highlightthickness=0, height=220)
        self.canvas.pack(fill="both", expand=True, padx=8, pady=8)
        self._probs: dict[str, float] = {}

    def set_probs(self, probs: dict, winner: str | None = None) -> None:
        self._probs = {k: float(v) for k, v in (probs or {}).items()}
        self.redraw(winner)

    def redraw(self, winner: str | None = None) -> None:
        c = self.canvas
        c.delete("all")
        c.update_idletasks()
        W = max(c.winfo_width(), 320)
        H = max(c.winfo_height(), 200)
        names = CLASS_ORDER
        rows = len(names)
        top, bottom, left, right = 8, 8, 110, 16
        usable_h = H - top - bottom
        usable_w = W - left - right
        row_h = usable_h / max(rows, 1)

        for i, name in enumerate(names):
            y0 = top + i * row_h
            y_mid = y0 + row_h * 0.5
            p = self._probs.get(name, 0.0)
            bar_w = max(2, int(usable_w * min(max(p, 0.0), 1.0)))
            color = ACCENT if (winner and name == winner) else ACCENT_2
            c.create_text(
                left - 8,
                y_mid,
                text=name,
                anchor="e",
                fill=FG if name == winner else FG_DIM,
                font=("Segoe UI", 10, "bold" if name == winner else "normal"),
            )
            c.create_rectangle(left, y_mid - 8, left + usable_w, y_mid + 8, fill=BG_BAR, outline=GRID)
            c.create_rectangle(left, y_mid - 8, left + bar_w, y_mid + 8, fill=color, outline="")
            c.create_text(
                left + usable_w + 4,
                y_mid,
                text=f"{100 * p:.0f}%",
                anchor="w",
                fill=FG_DIM,
                font=("Segoe UI", 9),
            )


class HeatmapPanel(Frame):
    def __init__(self, master, title: str, **kw):
        super().__init__(master, bg=BG_PANEL, **kw)
        Label(self, text=title, bg=BG_PANEL, fg=FG_DIM, font=("Segoe UI", 10, "bold")).pack(
            anchor="w", padx=10, pady=(8, 2)
        )
        self.lbl = Label(self, bg=BG_PANEL, fg=FG_DIM, text="No heatmap yet")
        self.lbl.pack(padx=10, pady=(0, 10))
        self._photo = None

    def set_image(self, rgb: np.ndarray | None, note: str = "") -> None:
        if rgb is None:
            self.lbl.config(image="", text=note or "Heatmap unavailable")
            self._photo = None
            return
        self._photo = rgb_to_photo(self.winfo_toplevel(), rgb)
        self.lbl.config(image=self._photo, text="")


class LiveDashboard:
    def __init__(self, json_path: Path, interval: float) -> None:
        self.json_path = json_path
        self.interval_ms = int(interval * 1000)
        self.last_mtime = 0.0
        self._pulse = 0

        self.root = Tk()
        self.root.title("mmCLIP Live Dashboard")
        self.root.configure(bg=BG)
        self.root.geometry("1280x820")
        self.root.minsize(1100, 700)

        title_font = tkfont.Font(family="Segoe UI", size=16, weight="bold")
        hero_font = tkfont.Font(family="Segoe UI", size=42, weight="bold")
        conf_font = tkfont.Font(family="Segoe UI", size=20)

        # header
        header = Frame(self.root, bg=BG)
        header.pack(fill="x", padx=20, pady=(16, 8))
        Label(header, text="mmCLIP", bg=BG, fg=ACCENT, font=title_font).pack(side="left")
        Label(
            header,
            text="  Activity Recognition  ·  Live Radar",
            bg=BG,
            fg=FG_DIM,
            font=("Segoe UI", 14),
        ).pack(side="left")
        self.clock_lbl = Label(header, text="", bg=BG, fg=FG_DIM, font=("Segoe UI", 11))
        self.clock_lbl.pack(side="right")

        self.status_lbl = Label(self.root, text="Waiting for live_status.json…", bg=BG, fg=FG_DIM)
        self.status_lbl.pack(anchor="w", padx=24)

        body = Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True, padx=16, pady=8)

        # left column — prediction
        left = Frame(body, bg=BG_PANEL, padx=16, pady=16)
        left.pack(side="left", fill="y", padx=(0, 10))

        Label(left, text="PREDICTION", bg=BG_PANEL, fg=FG_DIM, font=("Segoe UI", 10, "bold")).pack(
            anchor="w"
        )
        self.pred_lbl = Label(left, text="—", bg=BG_PANEL, fg=ACCENT, font=hero_font, wraplength=360)
        self.pred_lbl.pack(anchor="w", pady=(4, 8))
        self.conf_lbl = Label(left, text="", bg=BG_PANEL, fg=FG, font=conf_font)
        self.conf_lbl.pack(anchor="w")

        self.meta_lbl = Label(
            left, text="", bg=BG_PANEL, fg=FG_DIM, justify="left", font=("Segoe UI", 10)
        )
        self.meta_lbl.pack(anchor="w", pady=(16, 8))

        Label(left, text="CLASS SCORES", bg=BG_PANEL, fg=FG_DIM, font=("Segoe UI", 10, "bold")).pack(
            anchor="w", pady=(12, 0)
        )
        self.bars = ProbBars(left, width=380)
        self.bars.pack(fill="both", expand=True, pady=4)

        # right — heatmaps
        right = Frame(body, bg=BG)
        right.pack(side="left", fill="both", expand=True)

        Label(
            right,
            text="RADAR HEATMAPS  (Time–Doppler / Time–Range / Time–Angle)",
            bg=BG,
            fg=FG_DIM,
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w", pady=(0, 6))

        self.hm_dop = HeatmapPanel(right, "Time – Doppler")
        self.hm_dop.pack(fill="x", pady=4)
        self.hm_range = HeatmapPanel(right, "Time – Range")
        self.hm_range.pack(fill="x", pady=4)
        self.hm_angle = HeatmapPanel(right, "Time – Angle")
        self.hm_angle.pack(fill="x", pady=4)

        foot = Frame(self.root, bg=BG)
        foot.pack(fill="x", padx=20, pady=(4, 14))
        self.foot_lbl = Label(
            foot,
            text="Pipeline: rolling capture → mmAP → 7-class head  |  Local RTX 4090",
            bg=BG,
            fg=FG_DIM,
            font=("Segoe UI", 9),
        )
        self.foot_lbl.pack(anchor="w")

        self.root.after(self.interval_ms, self.poll)
        self.root.after(400, self._tick_clock)

    def _tick_clock(self) -> None:
        self.clock_lbl.config(text=time.strftime("%H:%M:%S"))
        self.root.after(400, self._tick_clock)

    def poll(self) -> None:
        try:
            if self.json_path.is_file():
                mtime = self.json_path.stat().st_mtime
                if mtime != self.last_mtime:
                    self.last_mtime = mtime
                    data = json.loads(self.json_path.read_text(encoding="utf-8"))
                    self.render(data)
                else:
                    # soft pulse while processing
                    status = ""
                    try:
                        status = json.loads(self.json_path.read_text(encoding="utf-8")).get(
                            "status", ""
                        )
                    except Exception:
                        pass
                    if str(status).lower() == "processing":
                        self._pulse = (self._pulse + 1) % 4
                        dots = "." * (self._pulse + 1)
                        self.pred_lbl.config(text=f"PROCESSING{dots}", fg=WARN)
            else:
                self.status_lbl.config(text=f"Waiting for {self.json_path} …")
        except Exception as exc:
            self.status_lbl.config(text=f"Error: {exc}", fg=ERR)

        self.root.after(self.interval_ms, self.poll)

    def render(self, data: dict) -> None:
        status = (data.get("status") or "").lower()
        pred = data.get("prediction") or "—"
        conf = data.get("confidence")
        elapsed = data.get("elapsed_s") or data.get("pipeline_elapsed_s")
        msg = data.get("message") or ""
        probs = data.get("probabilities") or {}
        shapes = data.get("shapes") or {}
        pass_n = data.get("pass")
        hm_dir = data.get("hm_dir")

        if data.get("error") or status == "error":
            self.status_lbl.config(text=f"Error: {data.get('error') or msg}", fg=ERR)
            self.pred_lbl.config(text="ERROR", fg=ERR)
            self.conf_lbl.config(text="")
            self.bars.set_probs({})
            return

        if status == "processing":
            self.status_lbl.config(text=msg or "Building heatmaps + classifying on RTX 4090…", fg=WARN)
            self.pred_lbl.config(text="PROCESSING…", fg=WARN)
            self.conf_lbl.config(text="Hold still — label updates when ready")
            return

        if status == "idle":
            self.status_lbl.config(text=msg or "Idle — ready for next action", fg=FG_DIM)
            self.pred_lbl.config(text="—", fg=ACCENT)
            self.conf_lbl.config(text="")
            self.bars.set_probs({})
            return

        self.status_lbl.config(text="Live result  ·  local RTX 4090", fg=ACCENT_2)
        self.pred_lbl.config(text=str(pred).upper(), fg=ACCENT)
        if conf is not None:
            self.conf_lbl.config(text=f"Confidence  {100 * float(conf):.1f}%")
        else:
            self.conf_lbl.config(text="")

        meta_lines = []
        if pass_n is not None:
            meta_lines.append(f"Pass  {pass_n}")
        if elapsed is not None:
            meta_lines.append(f"Latency  {elapsed}s")
        if shapes:
            meta_lines.append(
                "Shapes  "
                + ", ".join(f"{k}:{v}" for k, v in shapes.items())
            )
        if data.get("time_bins"):
            meta_lines.append(f"Time bins  {data['time_bins']}")
        if data.get("num_segments"):
            meta_lines.append(f"Segments  {data['num_segments']}")
        ckpt = data.get("ckpt")
        if ckpt:
            meta_lines.append(f"Ckpt  {Path(ckpt).name}")
        self.meta_lbl.config(text="\n".join(meta_lines))

        winner = str(pred).lower() if pred else None
        # normalize keys
        norm_probs = {}
        for k, v in probs.items():
            norm_probs[str(k).lower()] = float(v)
        self.bars.set_probs(norm_probs, winner=winner)

        # heatmaps
        if hm_dir:
            p = Path(hm_dir)
            if p.is_dir():
                self.hm_dop.set_image(load_heatmap_rgb(p, "dop"))
                self.hm_range.set_image(load_heatmap_rgb(p, "range"))
                self.hm_angle.set_image(load_heatmap_rgb(p, "angle"))
            else:
                self.hm_dop.set_image(None, f"hm_dir missing:\n{hm_dir}")
                self.hm_range.set_image(None, "")
                self.hm_angle.set_image(None, "")
        else:
            self.hm_dop.set_image(None, "No hm_dir in status JSON yet")
            self.hm_range.set_image(None, "")
            self.hm_angle.set_image(None, "")

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    p = argparse.ArgumentParser(description="mmCLIP advanced live dashboard")
    p.add_argument(
        "--json", type=Path, default=Path.home() / "harri_capture" / "live_status.json"
    )
    p.add_argument("--interval", type=float, default=0.35)
    args = p.parse_args()
    args.json.parent.mkdir(parents=True, exist_ok=True)
    LiveDashboard(args.json, args.interval).run()


if __name__ == "__main__":
    main()
