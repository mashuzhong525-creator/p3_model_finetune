# P3 本地部署说明（存档：Ollama 备选）

> 主路径已改为 **WSL2 + vLLM**（`local_train/本地WSL2-vLLM部署手册.md`）；本文件为 Ollama 备选存档，不再作为主路径。

1. 安装 Ollama Windows：https://ollama.com/download
2. 设置系统环境变量 `OLLAMA_HOST=127.0.0.1:8100`，重启 Ollama
3. 将云端回传的 `qwen1.5b-q4_k_m.gguf`（约 1GB）放到 `D:\p3\models\`
4. 导入模型：`ollama create finetuned-qwen -f Modelfile`（FROM 指向本地 GGUF）
5. 验证：`curl http://127.0.0.1:8100/v1/models` → 返回 `finetuned-qwen`
6. 评估对比：`python ../eval/eval_runner.py`（配置 DEEPSEEK_* 环境变量）

P1 线上接入：本次不做（本地推理无法被云端 P1 直接访问）；如需接入，走内网穿透（frp/ngrok）或 GGUF 双部署到 4C4G。
