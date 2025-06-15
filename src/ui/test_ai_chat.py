"""
AI对话面板测试文件

用于测试AI对话面板的功能和界面
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from PySide6.QtWidgets import QApplication
from src.ui.ai_chat_panel import AIChatPanel


def main():
    """
    测试AI对话面板
    """
    app = QApplication(sys.argv)
    
    # 设置应用程序属性
    app.setApplicationName("AI Chat Panel Test")
    app.setApplicationVersion("1.0.0")
    
    # 创建AI对话面板
    chat_panel = AIChatPanel()
    
    # 设置窗口大小
    chat_panel.resize(400, 600)
    
    # 显示窗口
    chat_panel.show()
    
    # 运行应用程序
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 