"""P3 本地微调 · 冒烟验证脚本

作用：在正式训练前，用很小的步数快速验证整条训练链路能跑通：
  - 模型能加载（Qwen2.5-1.5B-Instruct）
  - GPU 可用、能前向/反向/更新
  - loss 能下降、checkpoint 能保存
用法（在 finetune 环境激活后）：
    python local_train/smoke_test.py [--steps 5] [--out 临时输出目录]
"""
import argparse
import os

import torch
from peft import LoraConfig, get_peft_model
from transformers import AutoModelForCausalLM, AutoTokenizer


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=r"D:\ai_models\Qwen2.5-1.5B-Instruct")
    parser.add_argument("--steps", type=int, default=5)
    parser.add_argument("--out", default=r"D:\mashu77\workspace\project1\p3_model_finetune\train\smoke_out")
    args = parser.parse_args()

    assert torch.cuda.is_available(), "CUDA 不可用！请先回手册阶段 2 确认 GPU 环境。"
    print(f"[OK] GPU: {torch.cuda.get_device_name(0)} "
          f"{round(torch.cuda.get_device_properties(0).total_memory/1024**3,2)} GB")

    print(f"[*] 加载模型 from {args.model} ...")
    model = AutoModelForCausalLM.from_pretrained(
        args.model, torch_dtype=torch.bfloat16, device_map="cuda", use_cache=False)
    tok = AutoTokenizer.from_pretrained(args.model)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token

    # 冻结全部基座参数，只训练 LoRA（与正式训练 train_peft.py 同一链路，防止 8GB 显存 OOM）
    for p in model.parameters():
        p.requires_grad_(False)
    model = get_peft_model(
        model,
        LoraConfig(
            r=8,
            lora_alpha=16,
            target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
            lora_dropout=0.05,
            bias="none",
            task_type="CAUSAL_LM",
        ),
    )
    model.print_trainable_parameters()

    optimizer = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=1e-4)

    model.train()
    for step in range(args.steps):
        text = "【检索片段】\n绿色建筑是在全寿命期内节约资源、保护环境、减少污染的建筑。\n\n【用户问题】\n什么是绿色建筑？\n\n【回答】一星级绿色建筑要求评价总得分达到60分。"
        enc = tok(text, return_tensors="pt").to("cuda")
        out = model(input_ids=enc["input_ids"], labels=enc["input_ids"])
        loss = out.loss
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        print(f"  step {step}: loss={loss.item():.4f} | "
              f"显存 {round(torch.cuda.memory_allocated()/1024**3,2)}GB")

    if not os.path.isdir(args.out):
        os.makedirs(args.out, exist_ok=True)
    model.save_pretrained(args.out)
    print(f"[OK] 冒烟通过：链路可跑通，LoRA adapter 已保存到 {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
