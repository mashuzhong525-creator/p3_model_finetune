# P3 训练说明

- 环境：云 GPU（RTX 3090/4090，24GB），LLaMA-Factory（`pip install -e .`）
- 基座：Qwen/Qwen2.5-3B-Instruct（ModelScope 下载）
- 数据：`../data/train.json`（270）/ `val.json`（30），已注册为 `p3_train` / `p3_val`
- 一键管线（按顺序执行）：
  1. 本地：`HOST=root@<云IP> bash upload_data.sh`（上传数据与配置）
  2. 云端：`bash prepare_data.sh`（注册 p3_train/p3_val 并校验 270/30）
  3. 云端：`bash run_train.sh`（QLoRA 4bit，3 epochs，日志 train.log）
  4. 云端：`bash export_quantize.sh`（合并 + GGUF + Q4_K_M）
- 产出：`output/qwen3b-lora/`（adapter + trainer_log.jsonl）
- 量化：合并 → convert_hf_to_gguf → llama-quantize Q4_K_M（约 2GB）
