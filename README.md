# P3 模型微调项目工作区

> 本目录用于 P3「知识库项目模型微调」（绑定 P1 知识库管理平台，绿建/双碳领域）的规格、过程与提示词文档。
> 与 `p1_knowledge_platform/`、`p2_attribution_analysis/`、`docs/` 相互独立，不冲突。

## 目录结构

```text
p3_model_finetune/
├── README.md                                  # 本文件：目录说明与状态
├── docs/
│   ├── 规格需求说明书-P3-知识库项目模型微调.md   # 主规格（PRD 基线）
│   ├── 产交流会议纪要.md                        # 过程记录：已确认决策 / 待确认项
│   └── 本地环境体检报告.md                      # 环境体检结论与证据
├── data/
│   ├── README.md                               # 数据说明与划分方式
│   ├── 素材语料库.md                            # 公开资料整理的检索片段（带来源）
│   ├── dataset_info.json                        # LLaMA-Factory 数据集注册
│   ├── split_train_val.py                       # 合并 + 9:1 划分脚本
│   ├── alpaca_术语适配_60.json                  # 术语适配（60 条）
│   ├── alpaca_忠实回答_75.json                  # 忠实回答（75 条）
│   ├── alpaca_多片段整合_45.json                # 多片段整合（45 条）
│   ├── alpaca_证据引用_60.json                  # 证据引用（60 条）
│   └── alpaca_拒答_60.json                      # 资料不足拒答（60 条）
└── prompts/
    ├── P1-C-RAG-ANSWER-输出契约.md             # 冻结契约摘录（训练数据 output 必须遵守）
    ├── 训练数据构建提示词.md                    # 五能力分层样本生成与校验提示词
    └── 评估提示词.md                            # 金标准与 M1~M4 评估提示词
```

## 状态

- 规格版本：v0.1（草稿）
- 已确认：技术栈主干=租用云 GPU 一天训练（AutoDL 按量，LoRA bf16 1.5B）+ 本地 Ollama 推理
- 已确认：基座 = Qwen2.5-1.5B-Instruct（2026-08-19 三次修订）；推理 = 本地 Ollama（OLLAMA_HOST=127.0.0.1:8100）；训练数据 = 300 条问答对
- 待确认：无（O1~O5 均已关闭）
- 待确认项详见 `docs/产交流会议纪要.md` 第 3 节

## 后续步骤

1. 确认开放问题 O1~O5（见产交流会议纪要）
2. 搭建独立训练环境（conda env + LLaMA-Factory + 模型下载）
3. 构建训练数据（≥300 条，五能力分层）
4. 租卡训练 → 量化回传 → 本地 Ollama 部署 → 评估对比（P1 线上不切换）

## 三步运行

1. 训练：`HOST=root@<云IP> bash train/upload_data.sh` → 云端 `bash train/prepare_data.sh` → `bash train/run_train.sh` → `bash train/export_quantize.sh` → scp 回本地
2. 部署：本地安装 Ollama（`OLLAMA_HOST=127.0.0.1:8100`），`ollama create finetuned-qwen -f deploy/Modelfile`
3. 评估：`python eval/eval_runner.py`（先配置 DEEPSEEK_* 环境变量）
