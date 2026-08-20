param(
  [Parameter(Mandatory = $true)]
  [string]$LlamaFactoryData
)
# 本地数据注册（LLaMA-Factory CLI 路径用）：把 train/val 复制到 LLaMA-Factory/data 并注册 p3_train / p3_val
$ErrorActionPreference = "Stop"
$src = Join-Path $PSScriptRoot "..\data"

Copy-Item -LiteralPath (Join-Path $src "train.json") -Destination (Join-Path $LlamaFactoryData "p3_train.json") -Force
Copy-Item -LiteralPath (Join-Path $src "val.json") -Destination (Join-Path $LlamaFactoryData "p3_val.json") -Force

$infoPath = Join-Path $LlamaFactoryData "dataset_info.json"
$info = Get-Content -LiteralPath $infoPath -Raw -Encoding UTF8 | ConvertFrom-Json
$info.p3_train = @{ file_name = "p3_train.json"; formatting = "alpaca" }
$info.p3_val = @{ file_name = "p3_val.json"; formatting = "alpaca" }
$info | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $infoPath -Encoding UTF8

Write-Output "已注册 p3_train / p3_val -> $LlamaFactoryData"
