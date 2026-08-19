"""S2 行为自测用 mock LLM：纯标准库，不调用外部 API。"""

import re


def mock_chat(prompt: str) -> str:
    """根据提示词中的检索片段返回固定格式答案，用于自测契约校验。"""
    question = prompt.rsplit("【用户问题】", 1)[-1].split("【回答】")[0].strip()
    ctx = prompt.split("【检索片段】", 1)[-1].split("【用户问题】")[0].strip()
    if not ctx:
        return "检索片段中未提供相关信息，无法回答该问题。资料不足，无法完整回答。"
    if "一星级" in question:
        return "一星级绿色建筑要求评价总得分达到60分。[证据1]"
    return f"依据片段内容回答如下：{ctx[:40]}……[证据1]"


def validate_output(item: dict, output: str) -> dict:
    ids = {int(m) for m in re.findall(r"\[证据(\d+)\]", item["input"])}
    out_ids = {int(m) for m in re.findall(r"\[证据(\d+)\]", output)}
    fake = out_ids - ids
    return {
        "m1_hit": len(fake) == 0 and (len(out_ids) > 0 or "资料不足" in output),
        "m2_compliant": bool(output.strip()),
        "m3_caution_ok": (not item.get("requires_caution")) or ("资料不足" in output or "未提及" in output),
        "fake_evidence": sorted(fake),
    }


if __name__ == "__main__":
    # 内置"伪造引用必被抓"自测用例
    item = {"instruction": "x", "input": "[证据1] a", "requires_caution": True}
    assert validate_output(item, "结论。[证据9]")["fake_evidence"] == [9], "伪造引用必须被抓"
    print("S2 mock 自测通过")
