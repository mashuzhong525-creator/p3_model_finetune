# -*- coding: utf-8 -*-
"""合并 LoRA 适配器到基座，输出合并后模型目录（FR-P3-2 产物）。"""

import argparse
from pathlib import Path

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="合并 PEFT LoRA 到基座")
    parser.add_argument("--model_path", required=True, help="基座模型目录")
    parser.add_argument("--adapter_path", required=True, help="LoRA adapter 目录")
    parser.add_argument("--output_dir", required=True, help="合并后模型输出目录")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    dtype = torch.bfloat16 if torch.cuda.is_available() and torch.cuda.is_bf16_supported() else torch.float32
    model = AutoModelForCausalLM.from_pretrained(args.model_path, trust_remote_code=True, torch_dtype=dtype)
    model = PeftModel.from_pretrained(model, args.adapter_path)
    model = model.merge_and_unload()

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(out, safe_serialization=True)
    tokenizer = AutoTokenizer.from_pretrained(args.model_path, trust_remote_code=True)
    tokenizer.save_pretrained(out)
    print(f"合并完成：{out}")


if __name__ == "__main__":
    main()
