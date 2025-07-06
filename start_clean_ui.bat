@echo off
echo ================================================
echo        Pank Ins - 清理后的UI测试
echo ================================================
echo.

cd /d "%~dp0"

echo 当前目录: %CD%
echo.

echo 激活虚拟环境...
call .venv\Scripts\activate.bat

echo.
echo 启动清理后的QML UI界面...
echo.

python test_clean_ui.py

echo.
echo 测试结束，按任意键退出...
pause > nul 