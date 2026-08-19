#!/usr/bin/env bash
set -euo pipefail
# P3 一键训练：QLoRA 微调 Qwen2.5-3B-Instruct（云 GPU 服务器）
P3_DIR="/root/autodl-tmp/p3"
YAML="${P3_DIR}/qwen3b_lora.yaml"
LOG="${P3_DIR}/train.log"

echo "== 1/4 环境检查 =="
nvidia-smi | head -15
command -v llamafactory-cli >/dev/null || { echo "缺少 llamafactory-cli，请先 pip install -e ."; exit 1; }
test -f "${YAML}" || { echo "缺少训练配置 ${YAML}"; exit 1; }

echo "== 2/4 数据检查 =="
python - <<'PY'
import json
from pathlib import Path

p = Path("/root/autodl-tmp/p3/data")
for name in ("train.json", "val.json"):
    arr = json.loads((p / name).read_text(encoding="utf-8"))
    assert len(arr) > 0, name
    print(name, len(arr))
PY

echo "== 3/4 启动训练（后台，日志 train.log）=="
cd /root/autodl-tmp/LLaMA-Factory
nohup llamafactory-cli train "${YAML}" > "${LOG}" 2>&1 &
echo "训练 PID: $!"

echo "== 4/4 等待 30 秒确认 loss 开始下降 =="
sleep 30
tail -20 "${LOG}"
