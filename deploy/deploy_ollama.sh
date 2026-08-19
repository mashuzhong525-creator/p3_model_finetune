#!/usr/bin/env bash
set -euo pipefail

export OLLAMA_HOST=0.0.0.0:8100
export OLLAMA_KEEP_ALIVE=10m

if ! command -v ollama >/dev/null 2>&1; then
  curl -fsSL https://ollama.com/install.sh | sh
fi

# 通过 systemd override 固定监听地址
mkdir -p /etc/systemd/system/ollama.service.d
cat > /etc/systemd/system/ollama.service.d/override.conf <<EOF
[Service]
Environment="OLLAMA_HOST=0.0.0.0:8100"
Environment="OLLAMA_KEEP_ALIVE=10m"
EOF
systemctl daemon-reload
systemctl restart ollama
