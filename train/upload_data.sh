#!/usr/bin/env bash
set -euo pipefail
# 本地执行：上传数据与训练配置到云 GPU（租卡一天方案）
# 用法：HOST=root@<云IP> bash upload_data.sh
HOST="${HOST:?请设置 HOST，例如 HOST=root@1.2.3.4}"
PORT="${PORT:-22}"
HERE="$(cd "$(dirname "$0")" && pwd)"

ssh -p "${PORT}" "${HOST}" "mkdir -p /root/autodl-tmp/p3/data"
scp -P "${PORT}" "${HERE}/../data/train.json" "${HERE}/../data/val.json" "${HOST}:/root/autodl-tmp/p3/data/"
scp -P "${PORT}" "${HERE}/qwen1.5b_lora.yaml" "${HOST}:/root/autodl-tmp/p3/"
echo "上传完成"
