#!/usr/bin/env bash
set -euo pipefail
# 启动 vLLM 服务（WSL2 内执行）；Windows 通过 http://127.0.0.1:8100/v1 访问
MODEL_DIR="${1:-$HOME/p3/models/qwen1.5b-merged}"
export PATH="$HOME/.local/bin:$PATH"

# WSL 中 nvidia-smi 默认在 /usr/lib/wsl/lib，未进 PATH 时补上
if ! command -v nvidia-smi >/dev/null 2>&1 && [ -x /usr/lib/wsl/lib/nvidia-smi ]; then
  export PATH="/usr/lib/wsl/lib:$PATH"
fi

source "$HOME/.vllm-venv/bin/activate"

test -f "$MODEL_DIR/config.json" || { echo "模型目录缺少 config.json：$MODEL_DIR"; exit 1; }

nohup vllm serve "$MODEL_DIR" \
  --served-model-name finetuned-qwen \
  --port 8100 \
  --api-key sk-p3-demo \
  --max-model-len 4096 \
  --gpu-memory-utilization 0.85 \
  --dtype auto \
  > "$HOME/vllm.log" 2>&1 &

echo "vLLM 已后台启动（PID $!），日志 $HOME/vllm.log"
sleep 20
if curl -s http://127.0.0.1:8100/v1/models; then
  echo ""
  echo "服务正常：Windows 访问 http://127.0.0.1:8100/v1"
else
  echo "服务未就绪，日志如下："
  tail -20 "$HOME/vllm.log"
fi
