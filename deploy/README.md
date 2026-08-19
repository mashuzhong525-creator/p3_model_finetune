# P3 部署与 P1 切换说明

- 4C4G 安装 Ollama，`OLLAMA_HOST=0.0.0.0:8100`（systemd override，见 `deploy_ollama.sh`）
- 模型：`ollama create finetuned-qwen -f Modelfile`（GGUF Q4_K_M 约 2GB）
- 验证：`curl http://127.0.0.1:8100/v1/models`
- P1 切换：`deploy/.env.prod` 配置 `LLM_BASE_URL=http://127.0.0.1:8100/v1`、`LLM_MODEL=finetuned-qwen`、`LLM_API_KEY=sk-p3-demo`，重启 `kb-app`，SSE 流尾 `model` 事件显示模型名
- 切回：恢复 `.env.prod.bak-*` 或注释 `LLM_*` 回退 legacy `DEEPSEEK_*`
