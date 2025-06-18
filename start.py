#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ArtiOps 系统启动脚本
用于初始化系统和启动开发服务器
"""

import os
import sys
import subprocess
import time
import argparse
import webbrowser
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def print_banner():
    """打印启动横幅"""
    print("\n" + "=" * 80)
    print("""
    █████╗ ██████╗ ████████╗██╗ ██████╗ ██████╗ ███████╗
   ██╔══██╗██╔══██╗╚══██╔══╝██║██╔═══██╗██╔══██╗██╔════╝
   ███████║██████╔╝   ██║   ██║██║   ██║██████╔╝███████╗
   ██╔══██║██╔══██╗   ██║   ██║██║   ██║██╔═══╝ ╚════██║
   ██║  ██║██║  ██║   ██║   ██║╚██████╔╝██║     ███████║
   ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝ ╚═════╝ ╚═╝     ╚══════╝
                                       
    AI驱动的DevOps自动化平台 - 后端API服务
    """)
    print("=" * 80 + "\n")

def check_environment():
    """检查环境依赖"""
    print("📋 检查环境依赖...")
    
    # 检查Python版本
    py_version = sys.version.split()[0]
    print(f"✅ Python版本: {py_version}")
    
    # 检查pip是否可用
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      check=True, capture_output=True, text=True)
        print("✅ pip已安装")
    except subprocess.CalledProcessError:
        print("❌ pip未安装或不可用")
        sys.exit(1)
    
    # 检查虚拟环境
    in_venv = sys.prefix != sys.base_prefix
    if in_venv:
        print(f"✅ 在虚拟环境中运行: {sys.prefix}")
    else:
        print("⚠️ 未在虚拟环境中运行，建议使用虚拟环境")
    
    # 检查数据库连接
    try:
        # 这里可以添加数据库连接检查代码
        print("✅ 数据库连接检查 (跳过)")
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
    
    print("✅ 环境检查完成\n")

def install_requirements():
    """安装项目依赖"""
    print("📦 安装项目依赖...")
    backend_dir = BASE_DIR
    req_file = backend_dir / "requirements.txt"
    
    if not req_file.exists():
        print(f"❌ 找不到依赖文件: {req_file}")
        return False
    
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", str(req_file)],
            check=True
        )
        print("✅ 依赖安装完成\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖安装失败: {e}")
        return False

def create_superuser():
    """创建超级用户（如果不存在）"""
    print("👤 检查超级用户...")
    backend_dir = BASE_DIR
    manage_py = backend_dir / "manage.py"
    
    try:
        # 检查是否已存在超级用户
        result = subprocess.run(
            [sys.executable, str(manage_py), "shell", "-c", 
             "from django.contrib.auth import get_user_model; print(get_user_model().objects.filter(is_superuser=True).exists())"],
            check=True, capture_output=True, text=True
        )
        
        if result.stdout.strip() == "True":
            print("✅ 超级用户已存在\n")
            return True
        
        # 提示创建超级用户
        print("⚠️ 未找到超级用户，请创建一个:")
        subprocess.run(
            [sys.executable, str(manage_py), "createsuperuser"],
            check=True
        )
        
        print("✅ 超级用户创建完成\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 超级用户检查/创建失败: {e}")
        return False

def collect_static_files():
    """收集静态文件"""
    print("📂 收集静态文件...")
    backend_dir = BASE_DIR
    manage_py = backend_dir / "manage.py"
    
    try:
        subprocess.run(
            [sys.executable, str(manage_py), "collectstatic", "--noinput"],
            check=True
        )
        print("✅ 静态文件收集完成\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 静态文件收集失败: {e}")
        return False

def start_development_server(port=8000, no_browser=False):
    """启动开发服务器"""
    print(f"🚀 启动API开发服务器 (端口: {port})...")
    backend_dir = BASE_DIR
    manage_py = backend_dir / "manage.py"
    
    # 设置环境变量，确保 Python 能找到正确的包路径
    os.environ['PYTHONPATH'] = str(BASE_DIR)
    
    # 打开浏览器
    if not no_browser:
        url = f"http://127.0.0.1:{port}/swagger/"
        print(f"🌐 正在打开API文档: {url}")
        webbrowser.open(url)
    
    # 启动服务器
    try:
        subprocess.run(
            [sys.executable, str(manage_py), "runserver", f"0.0.0.0:{port}"],
            check=True
        )
    except KeyboardInterrupt:
        print("\n⛔ 服务器已停止")
    except subprocess.CalledProcessError as e:
        print(f"❌ 服务器启动失败: {e}")
        return False
    
    return True

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="ArtiOps API服务启动脚本")
    parser.add_argument("--port", type=int, default=8000, help="API服务器端口 (默认: 8000)")
    parser.add_argument("--no-browser", action="store_true", help="不自动打开浏览器")
    parser.add_argument("--skip-checks", action="store_true", help="跳过环境检查")
    parser.add_argument("--skip-requirements", action="store_true", help="跳过安装依赖")
    args = parser.parse_args()
    
    print_banner()
    
    if not args.skip_checks:
        check_environment()
    
    if not args.skip_requirements:
        install_requirements()
    
    collect_static_files()
    # 不再执行数据库迁移和系统初始化
    
    start_development_server(port=args.port, no_browser=args.no_browser)

if __name__ == "__main__":
    main() 