# Spec 文档（模块级）：P3 知识库项目模型微调

> 版本：v0.1 ｜ 日期：2026-08-19 ｜ 范围：P3 全链路（数据→训练→评估→部署→P1 集成→交付）
> 上游文档：`规格需求说明书-P3-知识库项目模型微调.md`、`2026-08-19-P3-环境搭建与训练实施方案.md`
> 说明：本 Spec 定义各模块的职责、边界与接口；实现以实施方案为准，契约以本文第 7 节为准。

---

## 1. 模块总览

```text
┌────────────┐     ┌────────────┐     ┌────────────┐     ┌──────────────┐
│ M1 数据模块 │ ──▶ │ M2 训练模块 │ ──▶ │ M4 部署模块 │ ──▶ │ M5 P1 集成   │
│ data/      │     │ train/     │     │ deploy/    │     │ .env.prod    │
└────────────┘     └────────────┘     └────────────┘     └──────────────┘
       │                  │                   ▲
       ▼                  ▼                   │
┌────────────┐     ┌────────────┐     ┌────────────┐
│ M3 评估模块 │ ◀── │ 产物/日志   │     │ 金标准/报告 │
│ eval/      │     │            │     │            │
└────────────┘     └────────────┘     └────────────┘

M6 文档与交付模块：docs/ + README + 交付清单，贯穿以上全部模块
```

| 模块 | 职责 | 关键目录/文件 |
| --- | --- | --- |
| M1 数据模块 | 语料、300 条 alpaca 数据、9:1 划分、格式契约校验 | `data/`、`tests/test_data_format.py` |
| M2 训练模块 | LoRA bf16 训练配置与执行说明（本地） | `train/qwen1.5b_lora.yaml`、`train/*.ps1`、`train/README.md` |
| M3 评估模块 | 金标准、M1~M4 评估、S1/S2/S3 | `eval/` |
| M4 部署模块 | 本地 WSL2 vLLM 服务、HF bf16 模型、OpenAI 兼容接口 | `deploy/`、`local_train/` |
| M5 P1 集成模块 | 本地演示与评估（P1 线上不切换） | `eval/`、`deploy/README.md` |
| M6 文档与交付模块 | 规格/纪要/计划/清单、截图 | `docs/`、`README.md` |

---

## 2. M1 数据模块

### 2.1 职责

- 维护训练语料与 300 条 alpaca 问答对（五能力分层）；
- 提供 9:1 train/val 划分与 LLaMA-Factory 数据集注册；
- 校验数据满足 P1 C-RAG-ANSWER 输出契约。

### 2.2 边界

- 输入：`素材语料库.md`（S/D/C 片段）、`../prompts/训练数据构建提示词.md`
- 输出：5 个分层 JSON、`train.json`（270）/`val.json`（30）、`dataset_info.json`
- 不包含：模型训练、评估、部署（见 M2/M3/M4）

### 2.3 文件与接口

| 文件 | 说明 |
| --- | --- |
| `data/alpaca_{层}_{数}.json` | alpaca 数据集，条目结构见 2.4 |
| `data/train.json` / `val.json` | `split_train_val.py` 的产物 |
| `data/dataset_info.json` | LLaMA-Factory 注册（p3_train/p3_val 在云侧追加） |
| `data/split_train_val.py` | `main()`：合并 5 个文件 → shuffle(seed=42) → 9:1 写出 |
| `tests/test_data_format.py` | 5 个测试：总数 300 / 字段 / 证据编号合法 / 拒答收尾 / 空 input 必拒答 |

### 2.4 条目结构（契约）

```json
{
  "instruction": "用户问题",
  "input": "[证据N] 检索片段…（可空；空=无召回）",
  "output": "标准答案（关键结论后标注 [证据N]；拒答以「资料不足，无法完整回答。」收尾）"
}
```

### 2.5 验收

- `python -m pytest tests/test_data_format.py -v` → 5 passed
- 五层条数 = 60/75/45/60/60，合计 300；train/val = 270/30

---

## 3. M2 训练模块

### 3.1 职责

- 在云 GPU（租卡一天）以 LoRA bf16 微调 Qwen2.5-1.5B-Instruct；
- 产出训练日志、loss 曲线数据、LoRA 适配器权重。

### 3.2 边界

- 输入：`data/train.json`、`data/val.json`（注册为 p3_train/p3_val）、基座模型目录
- 输出：`output/qwen1.5b-lora/`（`adapter_config.json`、`adapter_model.safetensors`、`trainer_log.jsonl`）
- 环境：云 GPU（AutoDL 按量，≥24GB 显存），LLaMA-Factory（`pip install -e .`）

### 3.3 管线脚本（`train/`）

| 文件 | 说明 |
| --- | --- |
| `upload_data.sh` | 本地→云上传 train/val 与 yaml（`HOST=root@<云IP> bash upload_data.sh`） |
| `run_train_local.ps1` | 本地一键训练（GPU/数据检查 + train_peft.py，Windows） |
| `train_peft.py` / `merge_peft.py` | PEFT LoRA 训练主代码 / 合并（课程演示代码） |
| `prepare_data.sh` / `run_train.sh`（可选） | 云端租卡训练备选（存档） |
| `export_quantize.sh` | 合并 LoRA → GGUF(f16) → Q4_K_M 量化（产物约 1GB） |
| `train_peft.py` | PEFT LoRA bf16 训练脚本（课程演示代码，与 LLaMA-Factory CLI 二选一） |
| `merge_peft.py` | 合并 LoRA adapter 到基座，输出合并模型目录 |

### 3.4 配置接口（`train/qwen1.5b_lora.yaml`）

| 配置项 | 值 | 说明 |
| --- | --- | --- |
| `model_name_or_path` | `D:/ai_models/Qwen2.5-1.5B-Instruct` | 基座（本地） |
| `stage` / `finetuning_type` | `sft` / `lora` | 监督微调 + LoRA |
| `lora_rank` / `lora_alpha` / `lora_target` | 16 / 32 / all | LoRA 超参 |
| ~~`quantization_bit`~~ | —（LoRA bf16） | 无需 QLoRA |
| `dataset` / `val_dataset` | p3_train / p3_val | LLaMA-Factory 注册名 |
| `max_length` | 1024 | 序列上限 |
| `per_device_train_batch_size` / `gradient_accumulation_steps` | 4 / 4 | 等效 batch=16 |
| `learning_rate` / `num_train_epochs` / `lr_scheduler_type` | 1e-4 / 3.0 / cosine | 训练超参 |
| `output_dir` | `D:/mashu77/workspace/project1/p3_model_finetune/train/output/qwen1.5b-lora` | 产物目录（本地） |

### 3.5 调用

```bash
python train_peft.py ...（或 `.\run_train_local.ps1`；LLaMA-Factory CLI 用 qwen1.5b_lora_local.yaml）
```

### 3.6 验收

- 日志出现 `trainable params` 且 loss 逐步下降；
- `trainer_log.jsonl` 含 `current_steps` 与 `loss` 字段；
- 产物含 adapter 权重（约 10~30MB 量级）。

---

## 4. M3 评估模块

### 4.1 职责

- 提供金标准评估集（50 条）与 M1~M4 四指标评估；
- 实现 S1 静态校验、S2 mock 自测、S3 实机评估三级验证。

### 4.2 边界

- 输入：`golden_eval.json`、微调前模型（DeepSeek API）、微调后模型（vLLM `finetuned-qwen`）
- 输出：`对比报告.json`（两模型的 M1~M4）
- 不包含：训练、部署

### 4.3 文件与接口

| 文件 | 关键接口 |
| --- | --- |
| `eval/golden_eval.json` | 50 条；字段见 4.4；`requires_caution` 10 条 |
| `eval/run_s1.py` | S1 静态校验：schema + 证据编号 + caution 统计（`python run_s1.py`） |
| `eval/demo_chat.py` | 本地问答演示：调用 vLLM OpenAI 兼容端点（`--question` / `--context`） |
| `eval/mock_llm.py` | `mock_chat(prompt) -> str`；`validate_output(item, output) -> dict`；`__main__` 内置伪造引用自测 |
| `eval/eval_runner.py` | `call_llm(base_url, api_key, model, instruction, ctx) -> str`；`score(item, output) -> dict`；`run(base_url, api_key, model) -> dict`；`__main__` 对比 DeepSeek vs finetuned-qwen 并写报告 |
| `eval/README.md` | 运行说明与纪律（S3 未跑须标注「未经实机」） |

### 4.4 金标准结构

```json
{
  "id": "G001",
  "capability": "术语适配|忠实回答|多片段整合|证据引用|资料不足拒答",
  "instruction": "问题",
  "input": "[证据N] 片段",
  "expected": "期望答案",
  "requires_caution": false,
  "note": "考察点说明"
}
```

### 4.5 指标口径

- M1 证据引用命中率 ≥95%：`[证据N]` 必须存在于 input 编号集且内容一致；
- M2 结构化合规率 100%：字段齐全、非空；拒答类含「资料不足，无法完整回答」；
- M3 反幻觉遵守率 ≥80%：`requires_caution=true` 样本输出含「资料不足/未提及/无法确认」等限定；
- M4 覆盖 100%：金标准全量跑完。

### 4.6 分级验证

- S1：schema + 引用编号合法（命令行校验）
- S2：`python eval/mock_llm.py`（纯标准库，伪造引用必被抓）
- S3：`eval_runner.py` + 人工抽检 20%，如实标注

### 4.7 验收

- S2 输出 `S2 mock 自测通过`；
- S3 产出 `对比报告.json`，含两模型四指标与抽样说明。

---

## 5. M4 部署模块

### 5.1 职责

- 在本地 WSL2（Ubuntu）用 vLLM 提供 OpenAI 兼容端点；
- 托管微调模型 GGUF（Q4_K_M）。

### 5.2 边界

- 输入：`qwen1.5b-q4_k_m.gguf`（约 1GB，来自云端量化回传）
- 输出：`http://127.0.0.1:8100/v1/*` OpenAI 兼容接口
- 环境：本地 WSL2（Ubuntu）+ RTX 5060 8GB（Ollama CPU/GPU 为备选）

### 5.3 文件与接口

| 文件 | 说明 |
| --- | --- |
| `deploy/Modelfile` | `FROM D:\p3\models\qwen1.5b-q4_k_m.gguf`；`temperature 0.3`；`num_ctx 2048` |
| `deploy/README.md` | 本地部署说明（安装、OLLAMA_HOST、导入、验证） |

### 5.4 对外接口（契约，冻结）

| 接口 | 请求 | 响应关键字段 |
| --- | --- | --- |
| `GET /v1/models` | — | `data[].id` = `finetuned-qwen` |
| `POST /v1/chat/completions` | OpenAI messages，`stream=false` | `choices[0].message.content`、`usage` |

鉴权：`Authorization: Bearer <key>`（P1 配置 `LLM_API_KEY`）。

### 5.5 降级与风险

- 本地资源：1.5B Q4 约 1GB，GPU 或 CPU 均可跑；资源紧张时 `num_ctx` 降至 1024；
- 模型加载：vLLM 常驻并受 `--gpu-memory-utilization` 控制显存占用；Ollama 备选按需加载。

### 5.6 验收

- `curl http://127.0.0.1:8100/v1/models` 返回 `finetuned-qwen`；
- chat/completions 返回可解析内容（GPU/CPU 均可）。

---

## 6. M5 P1 集成模块

### 6.1 职责

- 本地加载微调模型 `finetuned-qwen` 并验证 OpenAI 兼容端点；
- 支撑本地问答演示与 eval_runner 四指标对比（P1 线上不切换）。

### 6.2 接口（env 映射，冻结）

| P1 配置 | 微调接入值 |
| --- | --- |
| `LLM_API_KEY` | `sk-p3-demo`（与 vLLM `--api-key` 一致） |
| `LLM_BASE_URL` | `http://127.0.0.1:8100/v1`（本地演示用） |
| `LLM_MODEL` | `finetuned-qwen` |

### 6.3 本地演示流程

1. WSL2 内 `bash local_train/setup_wsl2_vllm.sh` 安装 vLLM；
2. `bash local_train/serve_vllm_wsl2.sh` 启动 `vllm serve --port 8100`；
3. 验证：`curl http://127.0.0.1:8100/v1/models` → `finetuned-qwen`；
4. 对比：`eval_runner.py`（DeepSeek ↔ finetuned-qwen）产出四指标报告。

### 6.4 验收

- 本地 `/v1/models` 返回 `finetuned-qwen`；
- 本地问答演示与对比报告产出。

---

## 7. 跨模块契约（冻结，变更需 P1+P3 协同评审）

| 契约 | 值 |
| --- | --- |
| 推理端口 | `8100`（本地 vLLM `--port 8100`，WSL2） |
| 服务模型名 | `finetuned-qwen` |
| 数据输出契约 | P1 `c_rag_answer.prompt` 六条规则（见 `prompts/P1-C-RAG-ANSWER-输出契约.md`） |
| 向量维度 | 切换 BGE-M3 需清 `data/vectors` 重新导入（本方案沿用现状） |

---

## 8. 验收口径对照

| 规格验收项 | 归属模块 | 状态 |
| --- | --- | --- |
| 300 条数据 + 格式校验 | M1 | ✅ 已完成（pytest 5 passed） |
| 真实训练 + 日志/loss/权重 | M2 | ⏳ 待本地执行（RTX 5060 8GB） |
| 金标准 50 条 + M1~M4 + S1/S2/S3 | M3 | ✅ S1/S2 完成；⏳ S3 待部署后执行 |
| vLLM 8100 + /v1/models | M4 | ⏳ 待本地执行（WSL2） |
| 本地演示 + 对比报告 | M5 | ⏳ 待本地执行（P1 线上不切换） |
| 截图与 README | M6 | ⏳ 待各模块完成后补齐 |
