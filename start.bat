@echo off
chcp 65001 >nul
title AI示波器控制系统

echo.
echo ========================================
echo    AI示波器控制系统 启动脚本
echo ========================================
echo.

:: 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到Python，请先安装Python 3.8+
    echo    下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: 检查虚拟环境
if not exist ".venv" (
    echo ⚠️  警告: 未找到虚拟环境
    echo 🔧 正在创建虚拟环境...
    python -m venv .venv
    if errorlevel 1 (
        echo ❌ 虚拟环境创建失败
        pause
        exit /b 1
    )
    echo ✅ 虚拟环境创建成功
)

:: 激活虚拟环境
echo 🔄 激活虚拟环境...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ 虚拟环境激活失败
    pause
    exit /b 1
)

:: 检查并安装依赖
echo 🔄 检查依赖库...
pip show PySide6 >nul 2>&1
if errorlevel 1 (
    echo 🔧 正在安装依赖库...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ 依赖库安装失败
        pause
        exit /b 1
    )
    echo ✅ 依赖库安装完成
)

:: 显示启动选项菜单
echo.
echo ========================================
echo    请选择启动模式:
echo ========================================
echo    1. 标准启动 (登录窗口)
echo    2. 直接启动主窗口 (跳过登录)
echo    3. 快速启动 (跳过检查和登录)
echo    4. 开发模式 (跳过检查，显示登录)
echo ========================================
echo.

set /p choice="请输入选项 (1-4，默认为1): "

:: 设置默认值
if "%choice%"=="" set choice=1

:: 根据选择运行不同模式
if "%choice%"=="1" (
    echo 🚀 标准启动模式...
    python run.py
) else if "%choice%"=="2" (
    echo 🚀 直接启动主窗口...
    python run.py --skip-login
) else if "%choice%"=="3" (
    echo 🚀 快速启动模式...
    python run.py --skip-checks --skip-login
) else if "%choice%"=="4" (
    echo 🚀 开发模式启动...
    python run.py --skip-checks
) else (
    echo ❌ 无效选项，使用标准启动模式
    python run.py
)

:: 程序结束后暂停
echo.
echo 程序已退出
pause 