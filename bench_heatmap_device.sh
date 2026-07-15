#!/usr/bin/env bash
# Benchmark mmAP heatmap device: CPU vs CUDA on one .bin via live_infer.
# Run on Ubuntu 4090 inside ~/mmCLIP with conda mmCLIP active.
set -euo pipefail
BIN="${1:-data/jul9/jump1783621426.bin}"
CKPT="${MMCLIP_7CLASS_CKPT:-src/linear_probe_7class_mmap_live100/best.pt}"

echo "BIN=$BIN"
echo "CKPT=$CKPT"

run_one () {
  local dev="$1"
  local out="/tmp/bench_${dev}.json"
  export MMCLIP_HEATMAP_DEVICE="$dev"
  export CUDA_VISIBLE_DEVICES=0
  export MMCLIP_7CLASS_CKPT="$CKPT"
  echo ""
  echo "===== MMCLIP_HEATMAP_DEVICE=$dev ====="
  /usr/bin/time -f "WALL %e s" python demo_realtime/live_infer.py \
    --bin "$BIN" \
    --prefix "bench_${dev}" \
    --hm-dir "/tmp/bench_${dev}_hm" \
    --out "$out"
  python -c "import json;d=json.load(open('$out'));print('pred',d.get('prediction'),'conf',d.get('confidence'),'elapsed',d.get('elapsed_s'))"
}

run_one cpu
run_one cuda
echo ""
echo "Done. Compare WALL / elapsed_s above."
