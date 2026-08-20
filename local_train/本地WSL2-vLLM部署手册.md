# P3 本地部署手册：WSL2 + vLLM（方案二，2026-08-19）

> 用途：在本地 Windows 上，通过 WSL2（Ubuntu）运行 vLLM，部署微调模型 `finetuned-qwen`，端口 8100（OpenAI 兼容）。
> 前提：微调已完成，云端产出 **bf16 合并模型目录**（HF safetensors 格式，约 3.2GB），并已回传本地。
> 环境：Windows 11 + NVIDIA 驱动（已装 610.74）+ WSL2 + RTX 5060 Laptop 8GB。

---

## 0. 确认 WSL2 可用

Windows PowerShell：

```powershell
wsl --status
wsl -l -v
```

预期：WSL 版本 2，存在 Ubuntu 发行版。若没有 Ubuntu，先安装：

```powershell
wsl --install -d Ubuntu
```

安装后设置 Linux 用户名/密码，重启终端。

## 1. 在 WSL 内检查 GPU 透传

进入 WSL：

```powershell
wsl
```

在 Ubuntu 内：

```bash
nvidia-smi
```

预期：显示 `RTX 5060 Laptop GPU`、约 8GB 显存（与 Windows 看到的同一张卡）。若看不到 GPU，先执行：

```bash
sudo apt update && sudo apt upgrade -y
```

并在 Windows 侧 `wsl --update` 后重启 WSL。

## 2. 安装 vLLM（自动脚本）

在 Ubuntu 内执行（脚本位置在 Windows 盘，通过 /mnt/d 访问）：

```bash
bash /mnt/d/mashu77/workspace/project1/p3_model_finetune/local_train/setup_wsl2_vllm.sh
```

脚本做的事：检查 GPU → 安装 uv → 创建 Python 3.12 虚拟环境 `~/.vllm-venv` → `uv pip install vllm`（清华源）。

预期末尾输出：

```text
vllm <版本号> | cuda_available True
安装完成：vllm 环境位于 /home/<用户>/.vllm-venv
```

## 3. 把 bf16 合并模型放进 WSL

模型在 Windows 的 `D:\p3\models\qwen1.5b-merged\`（若还没回传，先按《操作手册-P3-云端微调与本地部署.md》1.7/1.8 合并并 scp 回本地）。

在 Ubuntu 内：

```bash
mkdir -p ~/p3/models
cp -r /mnt/d/p3/models/qwen1.5b-merged ~/p3/models/
ls ~/p3/models/qwen1.5b-merged
```

预期：目录含 `config.json`、`model-*.safetensors`、`tokenizer.json`（合计约 3.2GB）。

> 建议拷进 WSL 文件系统（而不是直接读 /mnt/d），加载速度更快、避免 NTFS 性能损耗。

## 4. 启动 vLLM 服务

```bash
bash /mnt/d/mashu77/workspace/project1/p3_model_finetune/local_train/serve_vllm_wsl2.sh
```

等价命令（自动脚本实际执行）：

```bash
source ~/.vllm-venv/bin/activate
nohup vllm serve ~/p3/models/qwen1.5b-merged \
  --served-model-name finetuned-qwen \
  --port 8100 \
  --api-key sk-p3-demo \
  --max-model-len 4096 \
  --gpu-memory-utilization 0.85 \
  --dtype auto \
  > ~/vllm.log 2>&1 &
```

预期：约 20 秒后 `curl http://127.0.0.1:8100/v1/models` 返回模型列表（含 `finetuned-qwen`）。

## 5. 从 Windows 验证并演示

回到 Windows PowerShell（WSL2 会自动把 localhost 转发到 Windows）：

```powershell
curl.exe -s http://127.0.0.1:8100/v1/models
```

预期：返回 JSON，`data[].id` = `finetuned-qwen`。

本地问答演示：

```powershell
python D:\mashu77\workspace\project1\p3_model_finetune\eval\demo_chat.py --question "什么是绿色建筑？" --context "[证据1] 绿色建筑是在全寿命期内，节约资源、保护环境、减少污染，为人们提供健康、适用、高效的使用空间的高质量建筑。"
```

评估对比（微调前 DeepSeek vs 微调后 finetuned-qwen）：

```powershell
$env:DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
$env:DEEPSEEK_API_KEY = "<DeepSeekKey>"
$env:DEEPSEEK_MODEL = "deepseek-chat"
python D:\mashu77\workspace\project1\p3_model_finetune\eval\eval_runner.py
```

预期：输出两模型 M1~M4，生成 `eval\对比报告.json`。

## 6. 日常管理

| 操作 | 命令（Ubuntu 内） |
| --- | --- |
| 查看日志 | `tail -f ~/vllm.log` |
| 停止服务 | `pkill -f "vllm serve"` |
| 重启服务 | 再次执行第 4 步脚本 |
| 显存检查 | `nvidia-smi` |
| 开机自启（可选） | 将 serve 脚本加入 `~/.bashrc` 或 systemd（WSL 默认不自启，手动即可） |

## 7. 常见问题

| 现象 | 处理 |
| --- | --- |
| Windows 访问 8100 失败 | 确认 WSL 内 `curl http://127.0.0.1:8100/v1/models` 正常；WSL 版本需为 2；必要时 `wsl --shutdown` 后重进 |
| 显存不足（OOM） | 把 `--max-model-len` 降到 2048，或 `--gpu-memory-utilization` 降到 0.7；1.5B fp16 约 3.2GB，8GB 卡应够用 |
| `cuda_available False` | 驱动/WSL 未透传 GPU，按第 1 节处理 |
| 端口被占用 | `netstat -ano | findstr 8100`（Windows）或 `ss -ltnp | grep 8100`（WSL） |
| 想切回 Ollama（备选） | 见《操作手册-P3-云端微调与本地部署.md》第二部分（GGUF 流程保留） |

## 8. 与云端训练的关系

- 云端：只负责训练 + 导出 bf16 合并模型（`llamafactory-cli export` 或 `merge_peft.py`），完成后关机；
- 本地：本手册负责把合并模型跑起来（vLLM），供演示与评估；
- 两段共用契约：模型名 `finetuned-qwen`、端口 8100、OpenAI 兼容、API Key `sk-p3-demo`。
