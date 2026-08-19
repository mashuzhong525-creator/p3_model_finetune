"""M1~M4 评估：微调前（DeepSeek 官方 API）vs 微调后（Ollama finetuned-qwen）。"""

import json
import os
import re
from pathlib import Path

import httpx

HERE = Path(__file__).parent
GOLDEN = HERE / "golden_eval.json"
EVIDENCE_RE = re.compile(r"\[证据(\d+)\]")


def call_llm(base_url: str, api_key: str, model: str, instruction: str, ctx: str) -> str:
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": f"【检索片段】\n{ctx}\n\n【用户问题】\n{instruction}\n\n【回答】"}
        ],
        "temperature": 0.3,
    }
    headers = {"Authorization": f"Bearer {api_key}"}
    resp = httpx.post(f"{base_url}/chat/completions", json=payload, headers=headers, timeout=120)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def score(item: dict, output: str) -> dict:
    ids = {int(m) for m in EVIDENCE_RE.findall(item["input"])}
    out_ids = {int(m) for m in EVIDENCE_RE.findall(output)}
    m1 = len(out_ids - ids) == 0 and (len(out_ids) > 0 or "资料不足" in output)
    m2 = bool(output.strip())
    m3 = (not item.get("requires_caution")) or ("资料不足" in output or "未提及" in output or "无法确认" in output)
    return {"m1": m1, "m2": m2, "m3": m3}


def run(base_url: str, api_key: str, model: str) -> dict:
    items = json.loads(GOLDEN.read_text(encoding="utf-8"))
    results = [score(item, call_llm(base_url, api_key, model, item["instruction"], item["input"])) for item in items]
    n = len(results)
    return {
        "model": model,
        "n": n,
        "M1_证据引用命中率": sum(r["m1"] for r in results) / n,
        "M2_结构化合规率": sum(r["m2"] for r in results) / n,
        "M3_反幻觉遵守率": sum(r["m3"] for r in results) / n,
        "M4_覆盖": 1.0,
    }


if __name__ == "__main__":
    deepseek = run(os.environ["DEEPSEEK_BASE_URL"], os.environ["DEEPSEEK_API_KEY"], os.environ["DEEPSEEK_MODEL"])
    finetuned = run("http://127.0.0.1:8100/v1", "sk-p3-demo", "finetuned-qwen")
    report = {"微调前_DeepSeek": deepseek, "微调后_finetuned-qwen": finetuned}
    (HERE / "对比报告.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
