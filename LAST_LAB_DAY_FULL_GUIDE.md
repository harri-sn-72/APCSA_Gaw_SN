# LAST LAB DAY — Full Guide (Jul 15, 2026)

**You:** Harri  
**Machine:** Ubuntu lab PC + RTX 4090  
**Goal:** Ship polished live demo (UI + optional GPU heatmap), film video, backup everything  
**Already won:** live100 retrain + Hongfei tried it live @ ~99%  

Use this as the only checklist tomorrow morning.

---

## 0) Bring on USB / copy from laptop first

From `F:\UNC Charlotte Mentorship\mmWave Radar Data\lab_usb_bundle\`:

| Copy this | To Ubuntu |
|-----------|-----------|
| `ubuntu_harri_capture/ubuntu_live_display.py` | `~/harri_capture/` |
| `ubuntu_harri_capture/stream_live_pipeline.py` | `~/mmCLIP/demo_realtime/` |
| `mmap_heatmap/main_time_dop_read_all.py` | `~/mmCLIP/mmap_heatmap/` (**backup first**) |
| `ubuntu_harri_capture/bench_heatmap_device.sh` | `~/harri_capture/` (optional) |
| `FULL_DAY_RETRAIN_GUIDE.md` / this guide | Anywhere for reference |

```bash
# On Ubuntu after mounting USB (adjust path)
USB=/media/$USER/YOUR_USB/lab_usb_bundle

cp ~/mmCLIP/mmap_heatmap/main_time_dop_read_all.py \
   ~/mmCLIP/mmap_heatmap/main_time_dop_read_all.py.bak

cp "$USB/ubuntu_harri_capture/ubuntu_live_display.py" ~/harri_capture/
cp "$USB/ubuntu_harri_capture/stream_live_pipeline.py" ~/mmCLIP/demo_realtime/
cp "$USB/mmap_heatmap/main_time_dop_read_all.py" ~/mmCLIP/mmap_heatmap/
```

---

## 1) Morning power-on (15 min)

### Windows
1. mmWave Studio → load config → **Start stream**  
2. Confirm packets increasing  

### Ubuntu — env
```bash
conda activate mmCLIP
cd ~/mmCLIP
export CUDA_VISIBLE_DEVICES=0
export MMCLIP_7CLASS_CKPT=~/mmCLIP/src/linear_probe_7class_mmap_live100/best.pt
# If you promoted earlier:
# export MMCLIP_7CLASS_CKPT=~/mmCLIP/src/linear_probe_7class_mmap/best.pt

nvidia-smi
ls -lh "$MMCLIP_7CLASS_CKPT"
```

### Smoke (must pass before GPU games)
```bash
export MMCLIP_HEATMAP_DEVICE=cpu
python demo_realtime/live_infer.py \
  --bin data/jul9/jump1783621426.bin \
  --prefix smoke --hm-dir /tmp/smoke --out /tmp/smoke.json
python -c "import json;d=json.load(open('/tmp/smoke.json'));print(d['prediction'],d['confidence'],d.get('elapsed_s'))"
```
Expect **jump**, high confidence. Write down `elapsed_s` = **CPU baseline**.

---

## 2) Optional speedup — mmAP on GPU (20–40 min)

Your heatmap code now prefers CUDA. **Benchmark before trusting live.**

### 2a) Confirm the patched file prints the device
```bash
cd ~/mmCLIP
python -c "import mmap_heatmap.main_time_dop_read_all as m; print(m.gpu_device)"
# or just run live_infer and look for:
# [mmap_heatmap] device=cuda:0
```

### 2b) CPU vs CUDA timed compare
```bash
cd ~/mmCLIP
export MMCLIP_7CLASS_CKPT=~/mmCLIP/src/linear_probe_7class_mmap_live100/best.pt
BIN=data/jul9/jump1783621426.bin

export MMCLIP_HEATMAP_DEVICE=cpu
time python demo_realtime/live_infer.py \
  --bin "$BIN" --prefix bench_cpu --hm-dir /tmp/bench_cpu --out /tmp/bench_cpu.json
python -c "import json;d=json.load(open('/tmp/bench_cpu.json'));print('CPU',d.get('prediction'),d.get('confidence'),d.get('elapsed_s'))"

export MMCLIP_HEATMAP_DEVICE=cuda
time python demo_realtime/live_infer.py \
  --bin "$BIN" --prefix bench_gpu --hm-dir /tmp/bench_gpu --out /tmp/bench_gpu.json
python -c "import json;d=json.load(open('/tmp/bench_gpu.json'));print('GPU',d.get('prediction'),d.get('confidence'),d.get('elapsed_s'))"
```

### 2c) Decision table

| Result | Do this |
|--------|---------|
| GPU faster **and** still jump high conf | Keep `export MMCLIP_HEATMAP_DEVICE=cuda` all day |
| GPU similar / slower | `export MMCLIP_HEATMAP_DEVICE=cpu` |
| GPU wrong label / crash | Restore `.bak`, use CPU |

```bash
# Revert if needed
cp ~/mmCLIP/mmap_heatmap/main_time_dop_read_all.py.bak \
   ~/mmCLIP/mmap_heatmap/main_time_dop_read_all.py
export MMCLIP_HEATMAP_DEVICE=cpu
```

**Sticky note — add to `~/.bashrc` only if GPU wins:**
```bash
echo 'export MMCLIP_HEATMAP_DEVICE=cuda' >> ~/.bashrc
```

---

## 3) Live continuous demo (main event)

### Terminal 1 — capture (100 frames = live100 training length)
```bash
python3 ~/harri_capture/rolling_capture.py --out-dir ~/harri_capture --max-frames 100
```
Wait until `buffer=100`. Leave running.

### Terminal 2 — auto streaming classify
```bash
conda activate mmCLIP
cd ~/mmCLIP
export CUDA_VISIBLE_DEVICES=0
export MMCLIP_7CLASS_CKPT=~/mmCLIP/src/linear_probe_7class_mmap_live100/best.pt
export MMCLIP_HEATMAP_DEVICE=cuda   # or cpu from section 2

python demo_realtime/stream_live_pipeline.py --mode auto --min-interval 2 --stable-s 1.0
```

If labels thrash:
```bash
python demo_realtime/stream_live_pipeline.py --mode auto --min-interval 12 --stable-s 1.5
```

### Terminal 3 — terracotta UI
```bash
python3 ~/harri_capture/ubuntu_live_display.py --json ~/harri_capture/live_status.json
```

### Protocol (even in continuous mode)
- One action for a full processing cycle (~10–15s)  
- Hold still until label updates  
- Then next action  
- Partner FOV same as training helps; Hongfei already worked as unseen subject  

### Emergency: trigger mode
```bash
python demo_realtime/stream_live_pipeline.py --mode trigger
# Enter after each clean action
```

### Emergency: Friday-style one-shot
```bash
# T1 capture → action → Ctrl+C
python demo_realtime/live_infer.py \
  --bin ~/harri_capture/adc_direct_save.bin \
  --prefix oneshot --hm-dir /tmp/oneshot \
  --out ~/harri_capture/live_status.json
```

---

## 4) Film the video (Hongfei asked)

1. Phone or simple screen recorder on Ubuntu  
2. Show **UI** (prediction + bars + heatmaps)  
3. Capture person doing 2–3 actions (stand still, nodding, jump)  
4. Optional: show Terminal 2 `elapsed_s` once for latency story  
5. 30–60 s clip is enough  

Save to USB / laptop before you leave.

---

## 5) Backup before you leave lab (do not skip)

```bash
mkdir -p ~/harri_backup_last_day
cp -a ~/mmCLIP/src/linear_probe_7class_mmap_live100 ~/harri_backup_last_day/
cp -a ~/mmCLIP/src/linear_probe_7class_mmap/best.pt ~/harri_backup_last_day/best_mmap_main.pt 2>/dev/null || true
cp ~/harri_capture/live_status.json ~/harri_backup_last_day/ 2>/dev/null || true
# copy a couple good bins if space
ls ~/harri_capture/new100/bins | head
```

Also copy to USB:
- `best.pt` (live100)  
- this guide  
- video  
- `poster_figures/` from laptop if not already  

From laptop (poster figs already generated):
`Hongfei_7class_results/poster_figures/`

---

## 6) Harvey CUDA tools — what to say (don’t derail the day)

You pulled `cci-csgpu3:/data/swap/tools` → laptop `harvey_accel_tools_full/`.

| Fact | Detail |
|------|--------|
| What it is | SMPL → CUDA **sim** signal → GPU heatmaps |
| What your demo uses | Real `.bin` → **mmAP** → 7-class head |
| Drop-in? | **No** (different heatmap layout + would need retrain) |
| Real speedup you *can* try | GPU for **mmAP** (section 2) — same math, different device |

**Talk track for Hongfei:**  
> “I reviewed Harvey’s accelerated sim heatmap stack. For live radar I’m keeping mmAP for train/serve match; I enabled CUDA on the existing mmAP FFT path as the low-risk speedup.”

Full notes: `harvey_accel_tools_full/HARVEY_FULL_WALKTHROUGH.md`

---

## 7) UI notes (what you should see)

Light terracotta theme:
- Sand background, terracotta prediction text  
- Class bars **sorted by confidence** (highest on top)  
- No “ranked by confidence” caption  
- Scientific (original) heatmap colors  

If UI file missing / crash:
```bash
# minimal fallback text viewer if you still have it
python3 ~/harri_capture/ubuntu_live_viewer.py --json ~/harri_capture/live_status.json
```

---

## 8) Checkpoint paths (don’t mix)

| Checkpoint | Use |
|------------|-----|
| `src/linear_probe_7class_mmap_live100/best.pt` | **Preferred live** (35 new clips @ ~100 frames) |
| `src/linear_probe_7class_mmap/best.pt` | Older jul9 mmap head (backup) |
| `src/linear_probe_7class/best.pt` | hm_dra offline only — **not** live mmAP |

Live capture frames: **`--max-frames 100`** with live100 head.

---

## 9) Full command cheat sheet (copy to sticky note)

```bash
conda activate mmCLIP && cd ~/mmCLIP
export CUDA_VISIBLE_DEVICES=0
export MMCLIP_7CLASS_CKPT=~/mmCLIP/src/linear_probe_7class_mmap_live100/best.pt
export MMCLIP_HEATMAP_DEVICE=cuda   # or cpu

# T1
python3 ~/harri_capture/rolling_capture.py --out-dir ~/harri_capture --max-frames 100

# T2
python demo_realtime/stream_live_pipeline.py --mode auto --min-interval 2 --stable-s 1.0

# T3
python3 ~/harri_capture/ubuntu_live_display.py --json ~/harri_capture/live_status.json
```

---

## 10) Day timeline

| Time | Task |
|------|------|
| 0:00–0:15 | Studio + smoke (CPU) |
| 0:15–0:45 | GPU vs CPU bench → pick device |
| 0:45–1:30 | Continuous live + UI polish check |
| 1:30–2:00 | Film video |
| 2:00–2:30 | Show Hongfei / chat Harvey mmAP-GPU |
| last 20 min | Backups to USB |

---

## 11) Success = leave with

- [ ] Continuous live demo working  
- [ ] Updated UI on the lab monitor  
- [ ] GPU heatmap either faster or consciously left on CPU  
- [ ] Short demo video  
- [ ] `best.pt` + notes backed up off the lab PC  

---

## 12) If everything is on fire

1. `MMCLIP_HEATMAP_DEVICE=cpu`  
2. One-shot `live_infer` (no stream loop)  
3. Old display / text viewer  
4. csgpu1 hybrid (scp bin → remote infer → JSON back) — last resort  

You already proved the science with Hongfei. Tomorrow is polish, film, and backup.
