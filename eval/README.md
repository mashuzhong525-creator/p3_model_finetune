# P3 评估说明

- 金标准：`golden_eval.json`（50 条，五能力分层，含 `requires_caution`）
- S1 静态校验：`python run_s1.py`（schema + 引用编号合法性 + caution 统计）
- S2 行为自测：`python mock_llm.py`（纯标准库，内置"伪造引用必被抓"用例）
- S3 实机评估：`python eval_runner.py`（需配置 `DEEPSEEK_*` 环境变量；微调模型走 `http://127.0.0.1:8100/v1`）
- 输出：`对比报告.json`（微调前 DeepSeek vs 微调后 finetuned-qwen 的 M1~M4）
- 纪律：S3 人工抽检 20% 未完成时须标注「未经实机」
- 本地演示：`python demo_chat.py --question "什么是绿色建筑？" --context "[证据1] 绿色建筑是在全寿命期内节约资源、保护环境的高质量建筑。"`
