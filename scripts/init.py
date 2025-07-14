#!/usr/bin/env python
"""uv项目初始化脚本"""

import subprocess
import sys
from pathlib import Path


def check_uv():
    """检查uv是否安装"""
    try:
        result = subprocess.run(
            ["uv", "--version"], check=True, capture_output=True, text=True
        )
        print(f"✅ 检测到 {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def setup_uv_environment():
    """设置uv虚拟环境和依赖"""
    print("正在初始化uv环境...")

    # 读取Python版本配置
    python_version = None
    python_version_file = Path(".python-version")
    if python_version_file.exists():
        python_version = python_version_file.read_text().strip()
        print(f"使用Python版本: {python_version}")

    try:
        # 创建虚拟环境（如果还没有）
        if not Path(".venv").exists():
            cmd = ["uv", "venv"]
            if python_version:
                cmd.extend(["--python", python_version])
            subprocess.run(cmd, check=True)
            print("✅ 虚拟环境创建完成")

        # 同步依赖（使用full-dev分组获得完整开发环境）
        subprocess.run(["uv", "sync", "--extra", "full-dev"], check=True)
        print("✅ 依赖安装完成")

        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 环境配置失败: {e}")
        return False


def main():
    """主函数"""
    print("🚀 初始化 My Python Project (uv环境)")

    # 检查是否在项目根目录
    if not Path("pyproject.toml").exists():
        print("❌ 请在项目根目录运行此脚本")
        sys.exit(1)

    # 检查uv
    if not check_uv():
        print("❌ 未找到uv命令")
        print("安装uv: https://docs.astral.sh/uv/getting-started/installation/")
        print("或使用: curl -LsSf https://astral.sh/uv/install.sh | sh")
        sys.exit(1)

    # 设置环境
    if not setup_uv_environment():
        sys.exit(1)

    print("\n🎉 uv环境初始化完成!")
    print("\n使用uv命令:")
    print("• uv run python your_script.py   # 在虚拟环境中运行Python")
    print("• uv add package_name            # 添加依赖")
    print("• uv remove package_name         # 移除依赖")
    print("• uv sync                        # 同步依赖")
    print("\n或激活虚拟环境:")
    print("• source .venv/bin/activate      # Linux/Mac")
    print("• .venv\\Scripts\\activate         # Windows")


if __name__ == "__main__":
    main()
