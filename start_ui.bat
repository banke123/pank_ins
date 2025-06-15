@echo off
chcp 65001 >nul
title Pank Ins - AI 控制示波器系统

echo.
echo ========================================
echo    Pank Ins - AI 控制示波器系统
echo ========================================
echo.

echo 选择启动模式:
echo [1] 完整启动 (登录窗口 + 主窗口)
echo [2] 直接启动主窗口 (跳过登录)
echo [3] 仅启动登录窗口
echo [4] 测试AI对话面板
echo [5] 退出
echo.

set /p choice=请输入选择 (1-5): 

if "%choice%"=="1" (
    echo.
    echo 启动完整应用程序...
    python src\ui\app_launcher.py --mode login
) else if "%choice%"=="2" (
    echo.
    echo 直接启动主窗口...
    python src\ui\app_launcher.py --mode main
) else if "%choice%"=="3" (
    echo.
    echo 启动登录窗口...
    python src\ui\test_login.py
) else if "%choice%"=="4" (
    echo.
    echo 测试AI对话面板...
    python src\ui\test_ai_chat.py
) else if "%choice%"=="5" (
    echo.
    echo 退出程序...
    exit /b 0
) else (
    echo.
    echo 无效选择，请重新运行脚本
    pause
    exit /b 1
)

if errorlevel 1 (
    echo.
    echo 程序运行出错，请检查Python环境和依赖库
    echo 可以尝试运行: pip install -r requirements.txt
    pause
)

echo.
echo 程序已退出
pause 