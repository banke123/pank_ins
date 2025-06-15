"""
UI模块

这个模块包含了Pank Ins项目的所有用户界面组件
使用PySide6框架开发，提供现代化的用户界面

主要组件:
- LoginWindow: 登录窗口
- MainWindow: 主窗口
- LeftSidebar: 左侧边栏
- WorkArea: 工作区域
- AIChatPanel: AI对话面板
- LogArea: 日志区域
- AppLauncher: 应用启动器
"""

from .login_window import LoginWindow
from .main_window import MainWindow
from .left_sidebar import LeftSidebar
from .work_area import WorkArea
from .ai_chat_panel import AIChatPanel
from .log_area import LogArea
from .app_launcher import AppLauncher

__all__ = [
    'LoginWindow',
    'MainWindow', 
    'LeftSidebar',
    'WorkArea',
    'AIChatPanel',
    'LogArea',
    'AppLauncher'
]

__version__ = '1.0.0'
__author__ = 'Pank Ins Team' 