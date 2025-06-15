"""
主窗口测试文件

用于测试主窗口的各个组件和功能
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from PySide6.QtWidgets import QApplication
from src.ui.main_window import MainWindow


def main():
    """
    测试主窗口
    """
    app = QApplication(sys.argv)
    
    # 设置应用程序属性
    app.setApplicationName("Pank Ins")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Pank Ins Team")
    
    # 创建主窗口
    main_window = MainWindow()
    
    # 显示窗口
    main_window.show()
    
    # 运行应用程序
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 