"""
文件名: start.py
功能描述: 一键启动脚本，同时启动后端和前端服务
作者: ZT
日期: 2026/6/16
"""

import subprocess
import sys
import signal
from pathlib import Path

# 项目根目录
PROJECT_DIR = Path(__file__).parent
FRONTEND_DIR = PROJECT_DIR / "frontend"


def start_backend():
    """启动后端服务"""
    print("正在启动后端服务...")
    process = subprocess.Popen(
        [sys.executable, "main.py"],
        cwd=PROJECT_DIR,
        shell=True
    )
    return process


def start_frontend():
    """启动前端服务"""
    print("正在启动前端服务...")
    process = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=FRONTEND_DIR,
        shell=True
    )
    return process


def main():
    """主函数"""
    print("=" * 60)
    print("🍅 TomatoAI - 番茄病虫害智能诊断")
    print("=" * 60)

    # 启动后端
    backend_process = start_backend()

    # 启动前端
    frontend_process = start_frontend()

    print("\n" + "=" * 60)
    print("✅ 启动成功！")
    print("=" * 60)
    print("\n📍 访问地址:")
    print("   前端页面: http://localhost:3000")
    print("   后端 API: http://localhost:8000")
    print("   API 文档: http://localhost:8000/docs")
    print("\n💡 按 Ctrl+C 停止服务")
    print("=" * 60)

    # 处理退出信号
    def signal_handler(sig, frame):
        print("\n正在停止服务...")
        backend_process.terminate()
        frontend_process.terminate()
        backend_process.wait()
        frontend_process.wait()
        print("服务已停止！")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # 等待进程结束
    try:
        frontend_process.wait()
    except KeyboardInterrupt:
        signal_handler(None, None)


if __name__ == "__main__":
    main()