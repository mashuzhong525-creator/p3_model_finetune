# -*- coding: utf-8 -*-
"""PEFT LoRA bf16 微调脚本（Qwen2.5-1.5B-Instruct，alpaca 格式，C-RAG-ANSWER 契约）。

与 LLaMA-Factory CLI 二选一；本脚本用于课程演示"微调代码"（FR-P3-2）。
用法示例（云端）：
  python train_peft.py \
    --model_path /root/autodl-tmp/models/Qwen2.5-1.5B-Instruct \
    --train_file /root/autodl-tmp/p3/data/train.json \
    --val_file /root/autodl-tmp/p3/data/val.json \
    --output_dir /root/autodl-tmp/p3/output/qwen1.5b-lora-peft
"""

import argparse
import json
from pathlib import Path

import torch
from datasets import Dataset
from peft import LoraConfig, get_peft_model
from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments


def build_prompt(instruction: str, context: str) -> str:
    """按 P1 C-RAG-ANSWER 契约组装提示词（对齐 prompts/P1-C-RAG-ANSWER-输出契约.md）。"""
    ctx = context if context else "（无检索片段）"
    return f"【检索片段】\n{ctx}\n\n【用户问题】\n{instruction}\n\n【回答】"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="P3 PEFT LoRA bf16 微调")
    parser.add_argument("--model_path", required=True, help="基座模型目录")
    parser.add_argument("--train_file", required=True, help="train.json（alpaca）")
    parser.add_argument("--val_file", required=True, help="val.json（alpaca）")
    parser.add_argument("--output_dir", required=True, help="adapter 输出目录")
    parser.add_argument("--max_length", type=int, default=1024)
    parser.add_argument("--per_device_train_batch_size", type=int, default=4)
    parser.add_argument("--per_device_eval_batch_size", type=int, default=4)
    parser.add_argument("--gradient_accumulation_steps", type=int, default=4)
    parser.add_argument("--learning_rate", type=float, default=1.0e-4)
    parser.add_argument("--num_train_epochs", type=float, default=3.0)
    parser.add_argument("--lora_r", type=int, default=16)
    parser.add_argument("--lora_alpha", type=int, default=32)
    parser.add_argument("--logging_steps", type=int, default=5)
    parser.add_argument("--save_steps", type=int, default=50)
    parser.add_argument("--eval_steps", type=int, default=50)
    return parser.parse_args()


def load_alpaca(path: str) -> list[dict]:
    items = json.loads(Path(path).read_text(encoding="utf-8"))
    for item in items:
        assert {"instruction", "input", "output"} <= set(item), item
    return items


def main() -> None:
    args = parse_args()
    torch.manual_seed(42)

    tokenizer = AutoTokenizer.from_pretrained(
        args.model_path, trust_remote_code=True, padding_side="left"
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        args.model_path,
        trust_remote_code=True,
        torch_dtype=torch.bfloat16 if torch.cuda.is_available() and torch.cuda.is_bf16_supported() else torch.float32,
    )
    lora_config = LoraConfig(
        r=args.lora_r,
        lora_alpha=args.lora_alpha,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    def tokenize_fn(examples: dict) -> dict:
        texts = [
            build_prompt(ins, ctx) + out + tokenizer.eos_token
            for ins, ctx, out in zip(examples["instruction"], examples["input"], examples["output"])
        ]
        enc = tokenizer(texts, truncation=True, max_length=args.max_length, padding=False)
        return {"input_ids": enc["input_ids"], "labels": enc["input_ids"], "attention_mask": enc["attention_mask"]}

    train_ds = Dataset.from_list(load_alpaca(args.train_file)).map(tokenize_fn, batched=True)
    val_ds = Dataset.from_list(load_alpaca(args.val_file)).map(tokenize_fn, batched=True)

    training_args = TrainingArguments(
        output_dir=args.output_dir,
        per_device_train_batch_size=args.per_device_train_batch_size,
        per_device_eval_batch_size=args.per_device_eval_batch_size,
        gradient_accumulation_steps=args.gradient_accumulation_steps,
        learning_rate=args.learning_rate,
        num_train_epochs=args.num_train_epochs,
        logging_steps=args.logging_steps,
        save_steps=args.save_steps,
        eval_steps=args.eval_steps,
        eval_strategy="steps",
        save_strategy="steps",
        save_total_limit=2,
        bf16=torch.cuda.is_available() and torch.cuda.is_bf16_supported(),
        fp16=False,
        remove_unused_columns=False,
        report_to="none",
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        greater_is_better=False,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        tokenizer=tokenizer,
    )
    trainer.train()
    trainer.save_model(args.output_dir)

    log_path = Path(args.output_dir) / "trainer_log.jsonl"
    with log_path.open("w", encoding="utf-8") as f:
        for entry in trainer.state.log_history:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"完成：adapter 与 trainer_log.jsonl 已写入 {args.output_dir}")


if __name__ == "__main__":
    main()
