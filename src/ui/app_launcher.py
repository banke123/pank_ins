"""
应用启动器

提供统一的应用程序启动入口
可以选择启动登录窗口或直接启动主窗口
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from PySide6.QtWidgets import QApplication
from src.ui.login_window import LoginWindow
from src.ui.main_window import MainWindow


class AppLauncher:
    """
    应用启动器类
    
    管理应用程序的启动流程
    """
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.setup_app()
        
        self.login_window = None
        self.main_window = None
        
    def setup_app(self):
        """
        设置应用程序属性
        """
        self.app.setApplicationName("Pank Ins")
        self.app.setApplicationVersion("1.0.0")
        self.app.setOrganizationName("Pank Ins Team")
        self.app.setApplicationDisplayName("AI 控制示波器系统")
        
    def start_with_login(self):
        """
        从登录窗口开始启动应用
        """
        self.login_window = LoginWindow()
        
        # 连接登录成功信号
        self.login_window.login_success.connect(self.on_login_success)
        self.login_window.login_failed.connect(self.on_login_failed)
        
        # 显示登录窗口
        self.login_window.show_with_animation()
        
        return self.app.exec()
        
    def start_main_directly(self):
        """
        直接启动主窗口（跳过登录）
        """
        self.main_window = MainWindow()
        self.main_window.show()
        
        return self.app.exec()
        
    def on_login_success(self, username, password):
        """
        登录成功处理
        
        Args:
            username (str): 用户名
            password (str): 密码
        """
        print(f"用户 {username} 登录成功")
        
        # 关闭登录窗口
        if self.login_window:
            self.login_window.close()
            
        # 启动主窗口
        self.main_window = MainWindow()
        
        # 在状态栏显示当前用户
        self.main_window.statusBar().showMessage(f"当前用户: {username}")
        
        # 在日志中记录登录信息
        self.main_window.log_area.add_log("INFO", f"用户 {username} 登录成功")
        
        self.main_window.show()
        
    def on_login_failed(self, error_message):
        """
        登录失败处理
        
        Args:
            error_message (str): 错误信息
        """
        print(f"登录失败: {error_message}")


def main():
    """
    主函数
    """
    import argparse
    
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description="Pank Ins - AI 控制示波器系统")
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
    
    args = parser.parse_args()
    
    # 创建启动器
    launcher = AppLauncher()
    
    # 根据参数选择启动方式
    if args.skip_login or args.mode == "main":
        print("直接启动主窗口...")
        return launcher.start_main_directly()
    else:
        print("启动登录窗口...")
        return launcher.start_with_login()


if __name__ == "__main__":
    sys.exit(main()) 