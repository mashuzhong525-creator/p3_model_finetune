"""P3 训练数据合并与 9:1 划分脚本。

用法：python split_train_val.py
产出：train.json / val.json（固定随机种子 42）
"""

import json
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent
SEED = 42
RATIO = 0.9

FILES = [
    "alpaca_术语适配_60.json",
    "alpaca_忠实回答_75.json",
    "alpaca_多片段整合_45.json",
    "alpaca_证据引用_60.json",
    "alpaca_拒答_60.json",
]


def main() -> None:
    all_items: list[dict] = []
    for name in FILES:
        path = HERE / name
        items = json.loads(path.read_text(encoding="utf-8"))
        assert isinstance(items, list), name
        all_items.extend(items)
        print(f"{name}: {len(items)} 条")

    random.seed(SEED)
    random.shuffle(all_items)
    split = int(len(all_items) * RATIO)
    train, val = all_items[:split], all_items[split:]

    (HERE / "train.json").write_text(
        json.dumps(train, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (HERE / "val.json").write_text(
        json.dumps(val, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"总计 {len(all_items)} 条；train {len(train)} / val {len(val)}")


if __name__ == "__main__":
    main()

