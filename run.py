#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI示波器控制系统启动脚本

提供环境检查、依赖验证和错误处理功能。

@author: PankIns Team
@version: 1.0.0
"""

import sys
import os
import subprocess
import importlib.util
from pathlib import Path
import argparse


def check_python_version():
    """
    检查Python版本
    """
    if sys.version_info < (3, 8):
        print("❌ 错误: 需要Python 3.8或更高版本")
        print(f"   当前版本: {sys.version}")
        return False
    
    print(f"✅ Python版本检查通过: {sys.version.split()[0]}")
    return True


def check_virtual_environment():
    """
    检查虚拟环境
    """
    venv_path = Path(".venv")
    if not venv_path.exists():
        print("⚠️  警告: 未检测到虚拟环境")
        print("   建议创建虚拟环境: python -m venv .venv")
        return False
    
    # 检查是否在虚拟环境中运行
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ 虚拟环境检查通过")
        return True
    else:
        print("⚠️  警告: 当前未激活虚拟环境")
        print("   请激活虚拟环境: .venv\\Scripts\\activate (Windows) 或 source .venv/bin/activate (Linux/Mac)")
        return False


def check_dependencies():
    """
    检查依赖库
    """
    required_packages = [
        ("PySide6", "PySide6"),
        ("qfluentwidgets", "qfluentwidgets"),
        ("pykka", "pykka"),
        ("numpy", "numpy"),
        ("matplotlib", "matplotlib"),
        ("langchain", "langchain")
    ]
    
    missing_packages = []
    
    for package_name, import_name in required_packages:
        try:
            spec = importlib.util.find_spec(import_name)
            if spec is None:
                missing_packages.append(package_name)
            else:
                print(f"✅ {package_name} 已安装")
        except ImportError:
            missing_packages.append(package_name)
    
    if missing_packages:
        print(f"❌ 缺少依赖库: {', '.join(missing_packages)}")
        print("   请运行: pip install -r requirements.txt")
        return False
    
    print("✅ 所有依赖库检查通过")
    return True


def check_project_structure():
    """
    检查项目结构
    """
    required_dirs = [
        "src",
        "src/actors",
        "src/core",
        "src/ui",
        "src/utils",
        "src/config",
        "logs",
        "config"
    ]
    
    required_files = [
        "main.py",
        "requirements.txt",
        "src/__init__.py",
        "src/actors/__init__.py",
        "src/core/__init__.py",
        "src/ui/__init__.py"
    ]
    
    missing_items = []
    
    # 检查目录
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            missing_items.append(f"目录: {dir_path}")
    
    # 检查文件
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_items.append(f"文件: {file_path}")
    
    if missing_items:
        print("❌ 项目结构不完整:")
        for item in missing_items:
            print(f"   缺少 {item}")
        return False
    
    print("✅ 项目结构检查通过")
    return True


def install_dependencies():
    """
    安装依赖库
    """
    print("🔄 正在安装依赖库...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ 依赖库安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖库安装失败: {e}")
        return False


def create_missing_directories():
    """
    创建缺失的目录
    """
    dirs_to_create = ["logs", "data", "config", "plugins"]
    
    for dir_name in dirs_to_create:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"✅ 创建目录: {dir_name}")


def run_application(args=None):
    """
    运行应用程序
    
    Args:
        args (list): 命令行参数列表
    """
    print("\n🚀 启动AI示波器控制系统...")
    print("=" * 50)
    
    try:
        # 如果有参数，临时修改sys.argv
        original_argv = sys.argv.copy()
        if args:
            sys.argv = [sys.argv[0]] + args
        
        try:
            # 导入并运行主程序
            from main import main
            return main()
        finally:
            # 恢复原始的sys.argv
            sys.argv = original_argv
            
    except KeyboardInterrupt:
        print("\n⏹️  用户中断程序")
        return 0
    except Exception as e:
        print(f"\n❌ 程序运行错误: {e}")
        import traceback
        traceback.print_exc()
        return 1


def main():
    """
    主函数
    """
    # 创建参数解析器
    parser = argparse.ArgumentParser(description="AI示波器控制系统启动脚本")
    parser.add_argument(
        "--skip-login", 
        action="store_true", 
        help="跳过登录直接启动主窗口"
    )
    parser.add_argument(
        "--mode",
        choices=["login", "main"],
        default="login",
        help="启动模式: login(登录窗口) 或 main(主窗口)"
    )
    parser.add_argument(
        "--skip-checks",
        action="store_true",
        help="跳过环境检查直接启动"
    )
    
    args = parser.parse_args()
    
    print("AI示波器控制系统 - 启动检查")
    print("=" * 40)
    
    # 如果指定跳过检查，直接启动
    if args.skip_checks:
        print("⚠️  跳过环境检查，直接启动应用程序")
        print("=" * 40)
        
        # 准备传递给main.py的参数
        main_args = []
        if args.skip_login:
            main_args.append("--skip-login")
        if args.mode:
            main_args.extend(["--mode", args.mode])
            
        return run_application(main_args)
    
    # 环境检查
    checks_passed = True
    
    # 1. Python版本检查
    if not check_python_version():
        checks_passed = False
    
    # 2. 虚拟环境检查（警告但不阻止）
    check_virtual_environment()
    
    # 3. 项目结构检查
    if not check_project_structure():
        print("\n🔧 尝试修复项目结构...")
        create_missing_directories()
    
    # 4. 依赖库检查
    if not check_dependencies():
        print("\n🔧 尝试安装依赖库...")
        if not install_dependencies():
            checks_passed = False
        else:
            # 重新检查依赖
            if not check_dependencies():
                checks_passed = False
    
    if not checks_passed:
        print("\n❌ 环境检查失败，请解决上述问题后重试")
        input("按回车键退出...")
        return 1
    
    print("\n✅ 所有检查通过，准备启动应用程序")
    print("=" * 40)
    
    # 准备传递给main.py的参数
    main_args = []
    if args.skip_login:
        main_args.append("--skip-login")
    if args.mode:
        main_args.extend(["--mode", args.mode])
    
    # 运行应用程序
    exit_code = run_application(main_args)
    
    if exit_code != 0:
        print("\n程序异常退出")
        input("按回车键退出...")
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main()) 