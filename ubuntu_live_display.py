#!/usr/bin/env python3
"""
mmCLIP live dashboard — light terracotta theme, dynamic class rankings.

Polls live_status.json:
  - Large prediction + confidence
  - Class bars sorted by confidence (highest → lowest)
  - TD / TR / TA heatmaps when hm_dir is present
  - Idle / processing / ready status

Usage:
  python3 ubuntu_live_display.py
  python3 ubuntu_live_display.py --json ~/harri_capture/live_status.json
  python3 ubuntu_live_display.py --json demo_live_status.json   # local preview
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


# --- light terracotta theme (matches warm presentation deck: cream + clay) ---
BG = "#F4EFE8"           # soft warm sand
BG_PANEL = "#FFFDF9"     # near-white panel
BG_BAR_TRACK = "#E8DFD4"
FG = "#2C241C"           # deep brown
FG_DIM = "#7A6A5C"
ACCENT = "#C45C3E"       # terracotta
ACCENT_SOFT = "#D4785C"
ACCENT_2 = "#8B5E3C"     # warm brown secondary
WARN = "#C9A227"
ERR = "#B33A3A"
GRID = "#E0D5C8"
WINNER_FILL = "#C45C3E"
BAR_FILL = "#D4A28A"

CLASS_FALLBACK = [
    "jump",
    "kick",
    "punch",
    "wave hand",
    "side walk",
    "stand still",
    "nodding head",
]


def _scientific_cmap(x: np.ndarray) -> np.ndarray:
    """Original scientific-ish heatmap colors (blue → cyan → yellow → red)."""
    x = np.clip(x, 0.0, 1.0)
    r = np.clip(1.5 * x - 0.1, 0, 1)
    g = np.clip(1.5 * np.sin(np.pi * x) ** 1.2, 0, 1)
    b = np.clip(1.4 * (1.0 - x) ** 0.7, 0, 1)
    rgb = np.stack(
        [0.55 * r + 0.45 * x, 0.35 * g + 0.4 * x, 0.7 * b + 0.15 * (1 - x)],
        axis=-1,
    )
    return (255 * np.clip(rgb, 0, 1)).astype(np.uint8)


def load_heatmap_rgb(hm_dir: Path, stem: str, max_w: int = 400, max_h: int = 160) -> np.ndarray | None:
    candidates = [hm_dir / f"{stem}.npy", hm_dir / f"time_{stem}.npy"]
    if stem == "dop":
        candidates += [hm_dir / "time_dop.npy", hm_dir / "doppler.npy", hm_dir / "time_doppler.npy"]
    path = next((p for p in candidates if p.is_file()), None)
    if path is None:
        return None
    arr = np.load(path).astype(np.float32)
    if arr.ndim != 2 or arr.size == 0:
        return None
    lo, hi = float(np.percentile(arr, 2)), float(np.percentile(arr, 98))
    if hi <= lo:
        lo, hi = float(arr.min()), float(arr.max())
    norm = np.zeros_like(arr) if hi <= lo else (arr - lo) / (hi - lo)
    rgb = np.flipud(_scientific_cmap(norm))
    h, w = rgb.shape[:2]
    scale = min(max_w / max(w, 1), max_h / max(h, 1), 1.0)
    nh, nw = max(1, int(h * scale)), max(1, int(w * scale))
    if HAS_PIL:
        return np.asarray(Image.fromarray(rgb, mode="RGB").resize((nw, nh), Image.BILINEAR))
    ys = (np.linspace(0, h - 1, nh)).astype(int)
    xs = (np.linspace(0, w - 1, nw)).astype(int)
    return rgb[ys][:, xs]


def rgb_to_photo(root: Tk, rgb: np.ndarray):
    if HAS_PIL:
        return ImageTk.PhotoImage(Image.fromarray(rgb, mode="RGB"))
    h, w, _ = rgb.shape
    header = f"P6 {w} {h} 255\n".encode("ascii")
    return __import__("tkinter").PhotoImage(master=root, data=header + rgb.tobytes())


def _pretty_class(name: str) -> str:
    return "Wave Hand" if name == "wave hand" else name.title()


class ProbBars(Frame):
    """Probability bars sorted dynamically: highest confidence first.

    Layout per row (no overlapping):
        1  Stand Still                         95%
           [====================............]
    """

    def __init__(self, master, **kw):
        super().__init__(master, bg=BG_PANEL, **kw)
        self.canvas = Canvas(self, bg=BG_PANEL, highlightthickness=0, height=320)
        self.canvas.pack(fill="both", expand=True, padx=4, pady=4)
        self.canvas.bind("<Configure>", lambda _e: self.redraw(self._winner))
        self._probs: dict[str, float] = {}
        self._winner: str | None = None

    def set_probs(self, probs: dict, winner: str | None = None) -> None:
        self._probs = {str(k).lower(): float(v) for k, v in (probs or {}).items()}
        self._winner = winner.lower() if winner else None
        self.redraw(self._winner)

    def redraw(self, winner: str | None = None) -> None:
        c = self.canvas
        c.delete("all")
        c.update_idletasks()
        W = max(c.winfo_width(), 360)
        H = max(c.winfo_height(), 300)

        if self._probs:
            ranked = sorted(self._probs.items(), key=lambda kv: -kv[1])
        else:
            ranked = [(n, 0.0) for n in CLASS_FALLBACK]

        pad_x = 12
        top = 4
        bottom = 4
        usable_h = H - top - bottom
        row_h = usable_h / max(len(ranked), 1)
        bar_left = pad_x + 28
        bar_right = W - pad_x - 8
        bar_w_max = max(40, bar_right - bar_left)

        for i, (name, p) in enumerate(ranked):
            y0 = top + i * row_h
            y_label = y0 + row_h * 0.32
            y_bar = y0 + row_h * 0.68
            is_win = winner is not None and name == winner.lower()
            fill = WINNER_FILL if is_win else BAR_FILL
            label_color = FG if is_win else FG_DIM
            weight = "bold" if is_win else "normal"
            pct = f"{100 * p:.0f}%"

            c.create_text(
                pad_x + 10,
                y_label,
                text=str(i + 1),
                anchor="center",
                fill=ACCENT if is_win else FG_DIM,
                font=("Segoe UI", 11, "bold"),
            )
            c.create_text(
                bar_left,
                y_label,
                text=_pretty_class(name),
                anchor="w",
                fill=label_color,
                font=("Segoe UI", 11, weight),
            )
            c.create_text(
                bar_right,
                y_label,
                text=pct,
                anchor="e",
                fill=FG if is_win else FG_DIM,
                font=("Segoe UI", 11, weight),
            )
            c.create_rectangle(
                bar_left,
                y_bar - 7,
                bar_left + bar_w_max,
                y_bar + 7,
                fill=BG_BAR_TRACK,
                outline="",
            )
            filled = max(4, int(bar_w_max * min(max(p, 0.0), 1.0)))
            c.create_rectangle(
                bar_left,
                y_bar - 7,
                bar_left + filled,
                y_bar + 7,
                fill=fill,
                outline="",
            )


class HeatmapPanel(Frame):
    def __init__(self, master, title: str, **kw):
        super().__init__(master, bg=BG_PANEL, **kw)
        Label(
            self,
            text=title,
            bg=BG_PANEL,
            fg=FG_DIM,
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w", padx=14, pady=(12, 4))
        self.lbl = Label(self, bg=BG_PANEL, fg=FG_DIM, text="Waiting for heatmaps…")
        self.lbl.pack(padx=14, pady=(0, 12))
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
        self.root.title("mmCLIP Live · Activity Recognition")
        self.root.configure(bg=BG)
        self.root.geometry("1280x840")
        self.root.minsize(1080, 720)

        hero_font = tkfont.Font(family="Georgia", size=40, weight="bold")
        title_font = tkfont.Font(family="Segoe UI", size=13, weight="bold")
        conf_font = tkfont.Font(family="Segoe UI", size=18)

        # top bar
        header = Frame(self.root, bg=BG)
        header.pack(fill="x", padx=28, pady=(18, 6))
        Label(header, text="mmCLIP", bg=BG, fg=ACCENT, font=("Georgia", 22, "bold")).pack(
            side="left"
        )
        Label(
            header,
            text="  Live activity recognition",
            bg=BG,
            fg=FG_DIM,
            font=("Segoe UI", 13),
        ).pack(side="left", pady=(6, 0))
        self.clock_lbl = Label(header, text="", bg=BG, fg=FG_DIM, font=("Segoe UI", 11))
        self.clock_lbl.pack(side="right", pady=(6, 0))

        self.status_lbl = Label(
            self.root,
            text="Waiting for results…",
            bg=BG,
            fg=FG_DIM,
            font=("Segoe UI", 11),
        )
        self.status_lbl.pack(anchor="w", padx=32, pady=(0, 8))

        body = Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True, padx=24, pady=4)

        # left card
        left = Frame(body, bg=BG_PANEL, highlightbackground=GRID, highlightthickness=1)
        left.pack(side="left", fill="y", padx=(0, 14))
        left_inner = Frame(left, bg=BG_PANEL)
        left_inner.pack(fill="both", expand=True, padx=22, pady=20)

        Label(
            left_inner,
            text="CURRENT PREDICTION",
            bg=BG_PANEL,
            fg=FG_DIM,
            font=title_font,
        ).pack(anchor="w")
        self.pred_lbl = Label(
            left_inner,
            text="—",
            bg=BG_PANEL,
            fg=ACCENT,
            font=hero_font,
            wraplength=380,
            justify="left",
        )
        self.pred_lbl.pack(anchor="w", pady=(6, 4))
        self.conf_lbl = Label(left_inner, text="", bg=BG_PANEL, fg=FG, font=conf_font)
        self.conf_lbl.pack(anchor="w")

        self.meta_lbl = Label(
            left_inner,
            text="",
            bg=BG_PANEL,
            fg=FG_DIM,
            justify="left",
            font=("Segoe UI", 10),
        )
        self.meta_lbl.pack(anchor="w", pady=(14, 8))

        self.bars = ProbBars(left_inner, width=400)
        self.bars.pack(fill="both", expand=True, pady=(16, 0))

        # right heatmaps
        right = Frame(body, bg=BG)
        right.pack(side="left", fill="both", expand=True)
        Label(
            right,
            text="RADAR HEATMAPS",
            bg=BG,
            fg=FG_DIM,
            font=title_font,
        ).pack(anchor="w", pady=(0, 2))
        Label(
            right,
            text="Time–Doppler  ·  Time–Range  ·  Time–Angle",
            bg=BG,
            fg=FG_DIM,
            font=("Segoe UI", 9),
        ).pack(anchor="w", pady=(0, 8))

        self.hm_dop = HeatmapPanel(right, "Time – Doppler")
        self.hm_dop.pack(fill="x", pady=5)
        self.hm_dop.configure(highlightbackground=GRID, highlightthickness=1)
        self.hm_range = HeatmapPanel(right, "Time – Range")
        self.hm_range.pack(fill="x", pady=5)
        self.hm_range.configure(highlightbackground=GRID, highlightthickness=1)
        self.hm_angle = HeatmapPanel(right, "Time – Angle")
        self.hm_angle.pack(fill="x", pady=5)
        self.hm_angle.configure(highlightbackground=GRID, highlightthickness=1)

        foot = Frame(self.root, bg=BG)
        foot.pack(fill="x", padx=28, pady=(6, 16))
        self.foot_lbl = Label(
            foot,
            text="Live radar  →  mmAP heatmaps  →  mmCLIP 7-class head  ·  Local RTX 4090",
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
                    try:
                        status = json.loads(self.json_path.read_text(encoding="utf-8")).get(
                            "status", ""
                        )
                    except Exception:
                        status = ""
                    if str(status).lower() == "processing":
                        self._pulse = (self._pulse + 1) % 4
                        self.pred_lbl.config(
                            text="Processing" + "." * (self._pulse + 1), fg=WARN
                        )
            else:
                self.status_lbl.config(text=f"Waiting for {self.json_path.name}…")
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
            self.status_lbl.config(text=f"Something went wrong: {data.get('error') or msg}", fg=ERR)
            self.pred_lbl.config(text="Error", fg=ERR)
            self.conf_lbl.config(text="")
            self.bars.set_probs({})
            return

        if status == "processing":
            self.status_lbl.config(
                text=msg or "Building heatmaps and classifying… hang tight",
                fg=WARN,
            )
            self.pred_lbl.config(text="Processing…", fg=WARN)
            self.conf_lbl.config(text="Keep the same action until this finishes")
            return

        if status == "idle":
            self.status_lbl.config(text=msg or "Ready — do an action when you’re set", fg=FG_DIM)
            self.pred_lbl.config(text="—", fg=ACCENT)
            self.conf_lbl.config(text="")
            self.bars.set_probs({})
            return

        self.status_lbl.config(text="Live update from local RTX 4090", fg=ACCENT_2)
        pretty = str(pred).replace("_", " ").title()
        self.pred_lbl.config(text=pretty, fg=ACCENT)
        if conf is not None:
            self.conf_lbl.config(text=f"{100 * float(conf):.1f}% confidence")
        else:
            self.conf_lbl.config(text="")

        meta = []
        if pass_n is not None:
            meta.append(f"Pass {pass_n}")
        if elapsed is not None:
            meta.append(f"{elapsed}s processing")
        if data.get("time_bins"):
            meta.append(f"{data['time_bins']} time bins")
        if data.get("num_segments"):
            meta.append(f"{data['num_segments']} segments")
        if shapes:
            meta.append(" · ".join(f"{k} {v}" for k, v in shapes.items()))
        self.meta_lbl.config(text="\n".join(meta))

        winner = str(pred).lower().strip()
        self.bars.set_probs(probs, winner=winner)

        if hm_dir and Path(hm_dir).is_dir():
            p = Path(hm_dir)
            self.hm_dop.set_image(load_heatmap_rgb(p, "dop"))
            self.hm_range.set_image(load_heatmap_rgb(p, "range"))
            self.hm_angle.set_image(load_heatmap_rgb(p, "angle"))
        else:
            self.hm_dop.set_image(None, "Heatmaps appear after the next inference")
            self.hm_range.set_image(None, "")
            self.hm_angle.set_image(None, "")

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    p = argparse.ArgumentParser(description="mmCLIP terracotta live dashboard")
    p.add_argument(
        "--json",
        type=Path,
        default=Path.home() / "harri_capture" / "live_status.json",
    )
    p.add_argument("--interval", type=float, default=0.35)
    args = p.parse_args()
    args.json.parent.mkdir(parents=True, exist_ok=True)
    LiveDashboard(args.json, args.interval).run()


if __name__ == "__main__":
    main()
