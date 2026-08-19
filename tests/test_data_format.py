"""P3 训练数据格式与 C-RAG-ANSWER 契约校验。"""

import json
import re
from pathlib import Path

DATA = Path(__file__).parent.parent / "data"
FILES = [
    "alpaca_术语适配_60.json",
    "alpaca_忠实回答_75.json",
    "alpaca_多片段整合_45.json",
    "alpaca_证据引用_60.json",
    "alpaca_拒答_60.json",
]
EVIDENCE_RE = re.compile(r"\[证据(\d+)\]")


def load_all():
    items = []
    for name in FILES:
        items.extend(json.loads((DATA / name).read_text(encoding="utf-8")))
    return items


def test_total_is_300():
    assert len(load_all()) == 300


def test_required_fields():
    for item in load_all():
        assert {"instruction", "input", "output"} <= set(item), item


def test_evidence_numbers_exist_in_input():
    for item in load_all():
        if not item["input"]:
            continue
        ids = {int(m) for m in EVIDENCE_RE.findall(item["input"])}
        out_ids = {int(m) for m in EVIDENCE_RE.findall(item["output"])}
        assert out_ids <= ids, item["instruction"]


def test_refusal_ends_with_standard_phrase():
    for item in load_all():
        if item["instruction"].startswith("资料不足") or not item["input"]:
            continue
        if "资料不足" in item["output"]:
            assert item["output"].strip().endswith("资料不足，无法完整回答。"), item["instruction"]


def test_empty_input_entries_are_refusals():
    for item in load_all():
        if item["input"] == "":
            assert "资料不足，无法完整回答" in item["output"], item["instruction"]
