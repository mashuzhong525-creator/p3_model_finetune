# -*- coding: utf-8 -*-
"""S1 静态校验：金标准 schema + 证据编号合法 + 统计（FR-P3-3）。"""

import json
import re
import sys
from pathlib import Path

GOLDEN = Path(__file__).parent / "golden_eval.json"
REQUIRED = {"id", "capability", "instruction", "input", "expected", "requires_caution", "note"}
EVIDENCE_RE = re.compile(r"\[证据(\d+)\]")


def main() -> int:
    items = json.loads(GOLDEN.read_text(encoding="utf-8"))
    errors: list[str] = []
    if len(items) < 50:
        errors.append(f"条数不足：{len(items)}")
    for item in items:
        missing = REQUIRED - set(item)
        if missing:
            errors.append(f"{item.get('id', '?')} 缺少字段 {sorted(missing)}")
            continue
        ids = {int(m) for m in EVIDENCE_RE.findall(item["input"])}
        out_ids = {int(m) for m in EVIDENCE_RE.findall(item["expected"])}
        if out_ids - ids:
            errors.append(f"{item['id']} 期望答案引用了不存在的证据 {sorted(out_ids - ids)}")
    caution = sum(1 for x in items if x.get("requires_caution"))
    if errors:
        for e in errors:
            print("FAIL:", e)
        return 1
    print(f"S1 通过：{len(items)} 条，requires_caution {caution} 条，证据编号全部合法")
    return 0


if __name__ == "__main__":
    sys.exit(main())
