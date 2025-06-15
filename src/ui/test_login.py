"""
登录窗口测试脚本

用于测试和演示登录窗口的功能
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from PySide6.QtWidgets import QApplication
from ui.login_window import LoginWindow


def test_login_window():
    """
    测试登录窗口
    """
    app = QApplication(sys.argv)
    
    # 创建登录窗口
    login_window = LoginWindow()
    
    # 连接信号处理
    def on_login_success(username, password):
        print(f"登录成功！用户名: {username}")
        # 这里可以打开主窗口或其他操作
        
    def on_login_failed(error_message):
        print(f"登录失败: {error_message}")
    
    # 连接信号
    login_window.login_success.connect(on_login_success)
    login_window.login_failed.connect(on_login_failed)
    
    # 显示窗口（带动画效果）
    login_window.show_with_animation()
    
    # 运行应用
    sys.exit(app.exec())


if __name__ == "__main__":
    test_login_window() 