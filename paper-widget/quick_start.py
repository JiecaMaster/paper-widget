#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
快速启动脚本 - 自动安装依赖并运行程序
"""

import subprocess
import sys
import os

def check_and_install_dependencies():
    """检查并安装依赖"""
    print("检查依赖包...")
    
    required_packages = [
        'requests',
        'arxiv',
        'beautifulsoup4',
        'lxml',
        'Pillow',
        'pystray'
    ]
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"  [已安装] {package}")
        except ImportError:
            print(f"  [安装中] {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    
    print("\n所有依赖已就绪！")

def main():
    print("=" * 50)
    print("  论文推送助手 - 快速启动")
    print("=" * 50)
    print()
    
    # 切换到脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # 检查并安装依赖
    check_and_install_dependencies()
    
    print("\n正在启动程序...")
    print("-" * 50)
    
    # 运行主程序
    import main as app_main
    app_main.main()

if __name__ == "__main__":
    main()