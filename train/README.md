# P3 训练说明（v3：租卡一天，训练云端、推理本地）

- 本地微调（Windows，RTX 5060 8GB）：见 `本地微调-代码与参数.md`（代码 + 参数 + 步骤）
- 环境：云 GPU（AutoDL 按量，RTX 3090/4090 皆可），LLaMA-Factory（`pip install -e .`）
- 基座：Qwen/Qwen2.5-1.5B-Instruct（ModelScope 下载）
- 数据：`../data/train.json`（270）/ `val.json`（30），注册为 `p3_train` / `p3_val`
- 方式：**LoRA bf16**（不需要 QLoRA / bitsandbytes）
- 一键管线（按顺序执行）：
  1. 本地：`HOST=root@<云IP> bash upload_data.sh`（上传数据与配置）
  2. 云端：`bash prepare_data.sh`（注册 p3_train/p3_val 并校验 270/30）
  3. 云端：`bash run_train.sh`（LoRA bf16，3 epochs，约 20-40 分钟，日志 train.log）
  4. 云端：`bash export_quantize.sh`（合并 + GGUF + Q4_K_M，产物约 1GB）
  5. 回传：`scp root@<云IP>:/root/autodl-tmp/p3/output/qwen1.5b-q4_k_m.gguf D:\p3\models\`
- 备选（课程演示代码，与 LLaMA-Factory CLI 二选一）：
  - `python train_peft.py --model_path <基座> --train_file ../data/train.json --val_file ../data/val.json --output_dir output/qwen1.5b-lora-peft`
  - `python merge_peft.py --model_path <基座> --adapter_path output/qwen1.5b-lora-peft --output_dir output/qwen1.5b-merged-peft`
- 本地推理：Windows 安装 Ollama，`ollama create finetuned-qwen -f ../deploy/Modelfile`（FROM 本地 GGUF 路径）
- 产出：云端 `output/qwen1.5b-lora/`（adapter + trainer_log.jsonl）；回传 `qwen1.5b-q4_k_m.gguf`
