param(
  [string]$ModelPath = "D:\ai_models\Qwen2.5-1.5B-Instruct",
  [string]$TrainFile = (Join-Path $PSScriptRoot "..\data\train.json"),
  [string]$ValFile = (Join-Path $PSScriptRoot "..\data\val.json"),
  [string]$OutputDir = (Join-Path $PSScriptRoot "output\qwen1.5b-lora")
)
# 本地微调（PEFT LoRA bf16）：GPU 检查 → 数据检查 → 训练
$ErrorActionPreference = "Stop"

Write-Output "== 1/3 GPU 检查 =="
python -c "import torch; assert torch.cuda.is_available(); print(torch.cuda.get_device_name(0), round(torch.cuda.get_device_properties(0).total_memory/1024**3,2), 'GB')"

Write-Output "== 2/3 数据检查 =="
$train = Get-Content -LiteralPath $TrainFile -Raw -Encoding UTF8 | ConvertFrom-Json
$val = Get-Content -LiteralPath $ValFile -Raw -Encoding UTF8 | ConvertFrom-Json
if ($train.Count -ne 270 -or $val.Count -ne 30) { throw "数据条数不符：train=$($train.Count) val=$($val.Count)" }
Write-Output "train 270 / val 30 OK"

Write-Output "== 3/3 启动训练（日志输出到终端）=="
python (Join-Path $PSScriptRoot "train_peft.py") `
  --model_path $ModelPath `
  --train_file $TrainFile `
  --val_file $ValFile `
  --output_dir $OutputDir `
  --max_length 1024 `
  --per_device_train_batch_size 4 `
  --gradient_accumulation_steps 4 `
  --learning_rate 1.0e-4 `
  --num_train_epochs 3.0 `
  --lora_r 16 `
  --lora_alpha 32 `
  --logging_steps 5 `
  --save_steps 50 `
  --eval_steps 50

Write-Output "训练完成，adapter 已保存到 $OutputDir"
