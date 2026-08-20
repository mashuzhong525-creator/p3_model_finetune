param(
  [string]$EnvName = "finetune"
)
# Local fine-tune env setup: conda env + CUDA PyTorch + train deps
$ErrorActionPreference = "Stop"

Write-Output "== 1/3 Install CUDA PyTorch (about 2.5GB download) =="
conda run -n $EnvName pip install torch --index-url https://download.pytorch.org/whl/cu130
if ($LASTEXITCODE -ne 0) { throw "torch install failed" }

Write-Output "== 2/3 Install train deps =="
conda run -n $EnvName pip install transformers peft datasets accelerate sentencepiece pyyaml
if ($LASTEXITCODE -ne 0) { throw "deps install failed" }

Write-Output "== 3/3 Verify GPU =="
conda run -n $EnvName python -c 'import torch; assert torch.cuda.is_available(); p = torch.cuda.get_device_properties(0); print(torch.cuda.get_device_name(0), round(p.total_memory / 1024**3, 2), "GB")'
if ($LASTEXITCODE -ne 0) { throw "GPU verify failed" }

Write-Output "DONE: local train env ready (env: $EnvName)"
