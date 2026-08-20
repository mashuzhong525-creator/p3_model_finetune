# -*- coding: utf-8 -*-
"""本地问答演示：调用 Ollama OpenAI 兼容端点（C-RAG-ANSWER 提示词格式，FR-P3-4）。"""

import argparse

import httpx


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="本地 Ollama 问答演示")
    parser.add_argument("--question", required=True, help="用户问题")
    parser.add_argument("--context", default="", help="检索片段（[证据N] 格式，可空）")
    parser.add_argument("--base_url", default="http://127.0.0.1:8100/v1")
    parser.add_argument("--api_key", default="sk-p3-demo")
    parser.add_argument("--model", default="finetuned-qwen")
    parser.add_argument("--temperature", type=float, default=0.3)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ctx = args.context if args.context else "（无检索片段）"
    content = f"【检索片段】\n{ctx}\n\n【用户问题】\n{args.question}\n\n【回答】"
    payload = {
        "model": args.model,
        "messages": [{"role": "user", "content": content}],
        "temperature": args.temperature,
    }
    headers = {"Authorization": f"Bearer {args.api_key}"}
    resp = httpx.post(
        f"{args.base_url}/chat/completions", json=payload, headers=headers, timeout=120
    )
    resp.raise_for_status()
    answer = resp.json()["choices"][0]["message"]["content"]
    print(f"问题：{args.question}\n\n回答：\n{answer}")


if __name__ == "__main__":
    main()
