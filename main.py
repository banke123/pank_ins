#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI示波器控制系统主程序

主要功能：
1. 初始化系统
2. 启动Actor系统
3. 启动UI界面
4. 系统清理和退出

@author: PankIns Team
@version: 1.0.0
"""

import sys
import logging
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from src.ui import MainWindow
from src.core import SystemManager
from src.utils import setup_logging


def main():
    """
    主程序入口
    """
    # 设置高DPI支持 - 必须在QApplication创建之前
    import os
    os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '1'
    os.environ['QT_SCALE_FACTOR'] = '1'
    
    # 设置日志
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("启动AI示波器控制系统")
    
    # 创建应用程序
    app = QApplication(sys.argv)
    
    # Windows特有的DPI设置
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)  # 设置DPI感知
    except:
        pass  # 如果失败则忽略
    
    # 设置默认字体 - 针对Windows优化
    font = QFont()
    if sys.platform == "win32":
        font.setFamily("Microsoft YaHei UI")  # Windows上更清晰的字体
        font.setPointSize(9)
        font.setWeight(QFont.Weight.Normal)
        font.setHintingPreference(QFont.HintingPreference.PreferDefaultHinting)
    else:
        font.setFamily("Microsoft YaHei")
        font.setPointSize(9)
    
    app.setFont(font)
    
    # 创建系统管理器
    system_manager = SystemManager()
    
    # 创建主窗口
    window = MainWindow(system_manager)
    window.show()
    
    # 运行应用程序
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 