#!/usr/bin/env bash
set -euo pipefail
# 在云 GPU 服务器执行：注册 p3_train / p3_val 到 LLaMA-Factory
SRC="/root/autodl-tmp/p3/data"
DST="/root/autodl-tmp/LLaMA-Factory/data"
INFO="${DST}/dataset_info.json"

for n in train val; do
  cp "${SRC}/${n}.json" "${DST}/p3_${n}.json"
done

python - "${INFO}" <<'PY'
import json
import sys

path = sys.argv[1]
info = json.load(open(path, encoding="utf-8"))
info["p3_train"] = {"file_name": "p3_train.json", "formatting": "alpaca"}
info["p3_val"] = {"file_name": "p3_val.json", "formatting": "alpaca"}
with open(path, "w", encoding="utf-8") as f:
    json.dump(info, f, ensure_ascii=False, indent=2)
print("dataset_info 已注册：", sorted(k for k in info if k.startswith("p3_")))
PY

python - <<'PY'
import json
from pathlib import Path

p = Path("/root/autodl-tmp/LLaMA-Factory/data")
train = json.loads((p / "p3_train.json").read_text(encoding="utf-8"))
val = json.loads((p / "p3_val.json").read_text(encoding="utf-8"))
assert len(train) == 270 and len(val) == 30, (len(train), len(val))
print("校验通过：train 270 / val 30")
PY
