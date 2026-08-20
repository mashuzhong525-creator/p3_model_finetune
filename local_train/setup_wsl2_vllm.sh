#!/usr/bin/env bash
set -euo pipefail
# 本地 WSL2 部署 vLLM：环境安装（在 Ubuntu 内执行）

# WSL 中 nvidia-smi 默认在 /usr/lib/wsl/lib，未进 PATH 时补上
if ! command -v nvidia-smi >/dev/null 2>&1 && [ -x /usr/lib/wsl/lib/nvidia-smi ]; then
  export PATH="/usr/lib/wsl/lib:$PATH"
fi

echo "== 1/3 检查 GPU 透传 =="
if ! nvidia-smi >/dev/null 2>&1; then
  echo "WSL 中看不到 GPU：请先确认 Windows 驱动为 WSL 提供 CUDA 支持（本机 NVIDIA 驱动即可），并确保 WSL 已更新："
  echo "  wsl --update"
  echo "  sudo apt update && sudo apt upgrade -y"
  exit 1
fi
nvidia-smi | head -15

echo "== 2/3 安装 uv 并创建 vllm 虚拟环境 =="
command -v uv >/dev/null 2>&1 || curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
cd "$HOME"
uv venv --python 3.12 .vllm-venv
source .vllm-venv/bin/activate
uv pip install vllm -i https://pypi.tuna.tsinghua.edu.cn/simple

echo "== 3/3 验证 =="
python -c "import vllm, torch; print('vllm', vllm.__version__, '| cuda_available', torch.cuda.is_available())"
echo "安装完成：vllm 环境位于 $HOME/.vllm-venv"
