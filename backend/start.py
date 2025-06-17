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
                                       
    AI驱动的DevOps自动化平台
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
    req_file = BASE_DIR / "requirements.txt"
    
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

def run_migrations():
    """运行数据库迁移"""
    print("🔄 运行数据库迁移...")
    manage_py = BASE_DIR / "manage.py"
    
    if not manage_py.exists():
        print(f"❌ 找不到manage.py文件: {manage_py}")
        return False
    
    try:
        # 生成迁移文件
        subprocess.run(
            [sys.executable, str(manage_py), "makemigrations"],
            check=True
        )
        
        # 应用迁移
        subprocess.run(
            [sys.executable, str(manage_py), "migrate"],
            check=True
        )
        
        print("✅ 数据库迁移完成\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 数据库迁移失败: {e}")
        return False

def create_superuser():
    """创建超级用户（如果不存在）"""
    print("👤 检查超级用户...")
    manage_py = BASE_DIR / "manage.py"
    
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
    manage_py = BASE_DIR / "manage.py"
    
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
    print(f"🚀 启动开发服务器 (端口: {port})...")
    manage_py = BASE_DIR / "manage.py"
    
    # 打开浏览器
    if not no_browser:
        url = f"http://127.0.0.1:{port}/admin/"
        print(f"🌐 正在打开浏览器: {url}")
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

def start_frontend_dev_server(port=3000, no_browser=False):
    """启动前端开发服务器"""
    print(f"🚀 启动前端开发服务器 (端口: {port})...")
    frontend_dir = BASE_DIR / "frontend"
    
    if not frontend_dir.exists():
        print(f"❌ 找不到前端目录: {frontend_dir}")
        return False
    
    # 打开浏览器
    if not no_browser:
        url = f"http://127.0.0.1:{port}/"
        print(f"🌐 正在打开浏览器: {url}")
        webbrowser.open(url)
    
    # 启动前端服务器
    try:
        os.chdir(frontend_dir)
        subprocess.run(
            ["npm", "start", "--", f"--port={port}"],
            check=True
        )
    except KeyboardInterrupt:
        print("\n⛔ 前端服务器已停止")
    except subprocess.CalledProcessError as e:
        print(f"❌ 前端服务器启动失败: {e}")
        return False
    except FileNotFoundError:
        print("❌ 无法启动前端服务器，请确保已安装Node.js和npm")
        return False
    
    return True

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="ArtiOps启动脚本")
    parser.add_argument("--backend-port", type=int, default=8000, help="后端服务器端口 (默认: 8000)")
    parser.add_argument("--frontend-port", type=int, default=3000, help="前端服务器端口 (默认: 3000)")
    parser.add_argument("--no-browser", action="store_true", help="不自动打开浏览器")
    parser.add_argument("--skip-checks", action="store_true", help="跳过环境检查")
    parser.add_argument("--skip-migrations", action="store_true", help="跳过数据库迁移")
    parser.add_argument("--skip-requirements", action="store_true", help="跳过安装依赖")
    parser.add_argument("--frontend-only", action="store_true", help="仅启动前端服务器")
    parser.add_argument("--backend-only", action="store_true", help="仅启动后端服务器")
    args = parser.parse_args()
    
    print_banner()
    
    if not args.skip_checks:
        check_environment()
    
    if not args.skip_requirements:
        install_requirements()
    
    if not args.frontend_only and not args.skip_migrations:
        run_migrations()
        create_superuser()
        collect_static_files()
    
    if args.frontend_only:
        start_frontend_dev_server(port=args.frontend_port, no_browser=args.no_browser)
    elif args.backend_only:
        start_development_server(port=args.backend_port, no_browser=args.no_browser)
    else:
        # 默认情况下，仅启动后端服务器
        start_development_server(port=args.backend_port, no_browser=args.no_browser)

if __name__ == "__main__":
    main() 