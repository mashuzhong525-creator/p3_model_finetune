"""P3 本地微调 · torch 自动安装脚本（Windows / RTX 5060）

作用：自动探测可用的 CUDA 版 torch 源，挑一个能连通的安装，并验证 GPU 可用。
用法：在 finetune 环境激活后执行：
    python local_train/install_torch.py
"""
import subprocess
import sys

# 依次尝试的 torch 源（CUDA 版本不同，能通即可；优先新版本）
SOURCES = [
    ("官方 cu128", "https://download.pytorch.org/whl/cu128"),
    ("清华 cu128", "https://mirrors.tuna.tsinghua.edu.cn/pytorch-wheels/cu128"),
    ("阿里 cu124", "https://mirrors.aliyun.com/pytorch-wheels/cu124"),
    ("阿里 cu126", "https://mirrors.aliyun.com/pytorch-wheels/cu126"),
]


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    print(f"\n>>> {' '.join(cmd)}", flush=True)
    return subprocess.run(cmd)


def main() -> int:
    print("=" * 60)
    print("探测可用的 PyTorch CUDA 源并安装（网络较慢请耐心等待）")
    print("=" * 60)

    # 先试官方源
    for name, url in SOURCES:
        print(f"\n--- 尝试源：{name} ---", flush=True)
        # 快速连通性探测：仅 pip index 查看版本，不下载大文件
        probe = run([sys.executable, "-m", "pip", "index", "versions", "torch",
                     "--index-url", url])
        if probe.returncode != 0:
            print(f"  [x] {name} 不可用，跳过", flush=True)
            continue

        # 源可用，正式安装 torch + torchvision
        install = run([sys.executable, "-m", "pip", "install",
                       "torch", "torchvision", "--index-url", url])
        if install.returncode != 0:
            print(f"  [x] {name} 安装失败，尝试下一个", flush=True)
            continue

        print(f"\n[v] 已用 {name} 安装成功，验证 GPU...", flush=True)
        verify = run([sys.executable, "-c",
                      "import torch; print('cuda', torch.cuda.is_available()); "
                      "print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'NO CUDA')"])
        if verify.returncode != 0 or "cuda True" not in verify.stdout:
            print("\n[!] torch 已装，但 GPU 未启用。请检查驱动/CUDA 版本。", flush=True)
            return 2
        print("\n[√] 一切就绪：CUDA 可用，GPU 已识别。", flush=True)
        return 0

    print("\n[x] 所有源都不可用。请检查网络，或手动安装 torch（见手册阶段 2）。", flush=True)
    return 1


if __name__ == "__main__":
    sys.exit(main())
