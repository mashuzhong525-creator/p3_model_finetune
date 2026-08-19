#!/usr/bin/env bash
set -euo pipefail
# P3 合并 LoRA + 转换 GGUF + Q4_K_M 量化（云 GPU 服务器）
MODEL="/root/autodl-tmp/models/Qwen2.5-3B-Instruct"
ADAPTER="/root/autodl-tmp/p3/output/qwen3b-lora"
MERGED="/root/autodl-tmp/p3/output/qwen3b-merged"
OUT="/root/autodl-tmp/p3/output"
LLAMA_CPP="/root/autodl-tmp/llama.cpp"

test -f "${ADAPTER}/adapter_model.safetensors" || { echo "缺少 adapter 权重：${ADAPTER}"; exit 1; }

echo "== 1/3 合并 LoRA 到基座 =="
cd /root/autodl-tmp/LLaMA-Factory
llamafactory-cli export \
  --model_name_or_path "${MODEL}" \
  --adapter_name_or_path "${ADAPTER}" \
  --template qwen \
  --finetuning_type lora \
  --export_dir "${MERGED}" \
  --export_size 4 \
  --export_legacy_format false

echo "== 2/3 转换 GGUF (f16) =="
test -d "${LLAMA_CPP}" || git clone https://github.com/ggerganov/llama.cpp "${LLAMA_CPP}"
cd "${LLAMA_CPP}"
if [ ! -f build/bin/llama-quantize ]; then
  cmake -B build -DCMAKE_BUILD_TYPE=Release
  cmake --build build -j --target llama-quantize
fi
python convert_hf_to_gguf.py "${MERGED}" --outfile "${OUT}/qwen3b-f16.gguf" --outtype f16

echo "== 3/3 量化 Q4_K_M =="
./build/bin/llama-quantize "${OUT}/qwen3b-f16.gguf" "${OUT}/qwen3b-q4_k_m.gguf" Q4_K_M
ls -lh "${OUT}/qwen3b-q4_k_m.gguf"
echo "完成：请 scp 到 4C4G 服务器的 /opt/p3/models/"
