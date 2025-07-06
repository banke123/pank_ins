#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
现代化登录窗口模块

采用新拟态设计风格 (Neumorphism) + Material Design 3
- 左右分栏布局：左侧为品牌展示区，右侧为登录表单
- 流畅的动画效果和微交互
- 支持主题切换
- 现代化的视觉设计
"""

import sys
import logging
from typing import Optional
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QCheckBox, QFrame,
    QGraphicsDropShadowEffect, QSpacerItem, QSizePolicy,
    QProgressBar, QComboBox
)
from PySide6.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve, Signal, QTimer,
    QParallelAnimationGroup, QSequentialAnimationGroup, Slot, QRect
)
from PySide6.QtGui import (
    QFont, QPixmap, QPainter, QColor, QBrush, QLinearGradient,
    QRadialGradient, QFontMetrics, QIcon, QPalette
)

logger = logging.getLogger(__name__)


class ModernLoginWindow(QWidget):
    """
    现代化登录窗口
    
    特色功能：
    - 新拟态设计风格
    - 流畅的动画效果
    - 左右分栏布局
    - 主题切换支持
    - 记住密码功能
    - 自动登录选项
    """
    
    # 信号定义
    login_success = Signal(str, str)  # 用户名, 密码
    login_failed = Signal(str)        # 错误信息
    theme_changed = Signal(str)       # 主题名称
    
    def __init__(self):
        super().__init__()
        
        # 初始化属性
        self.current_theme = "dark"
        self.drag_position = None
        self.is_logging_in = False
        
        # 自动登录相关
        self.auto_login_timer = QTimer()
        self.auto_login_countdown = 3  # 3秒倒计时
        self.countdown_timer = QTimer()  # 用于倒计时显示的定时器
        
        # 动画组
        self.entrance_animation = None
        self.login_animation = None
        
        self.setup_window()
        self.setup_ui()
        self.setup_animations()
        self.apply_theme()
        
        # 确保界面正确显示
        self.main_container.setVisible(True)
        self.repaint()
        
        # 设置自动登录定时器
        self.setup_auto_login()
        
        logger.info("现代化登录窗口初始化完成")
    
    def setup_window(self):
        """设置窗口属性"""
        self.setWindowTitle("Pank Ins - AI示波器控制系统")
        
        # 直接使用最小尺寸
        self.setMinimumSize(800, 600)
        self.resize(800, 700)  # 直接设置为最小尺寸
        self.setWindowFlags(Qt.FramelessWindowHint)
        
        # 设置窗口背景透明
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        
        # 获取屏幕分辨率，居中显示
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - 800) // 2
        y = (screen.height() - 600) // 2
        self.move(x, y)
    
    def setup_ui(self):
        """设置用户界面"""
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)  # 移除外边距
        main_layout.setSpacing(0)
        
        # 主容器
        self.main_container = QFrame()
        self.main_container.setObjectName("main_container")
        
        # 容器布局
        container_layout = QHBoxLayout()
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        
        # 左侧品牌展示区
        left_panel = self.create_brand_panel()
        left_panel.setMinimumWidth(480)  # 设置最小宽度
        container_layout.addWidget(left_panel, 3)  # 60%
        
        # 右侧登录表单区
        right_panel = self.create_login_panel()
        right_panel.setMinimumWidth(320)  # 设置最小宽度
        container_layout.addWidget(right_panel, 2)  # 40%
        
        self.main_container.setLayout(container_layout)
        
        # 添加到主布局
        main_layout.addWidget(self.main_container)
        self.setLayout(main_layout)
        
        # 创建窗口控制按钮
        self.create_window_controls()
    
    def create_brand_panel(self) -> QFrame:
        """创建左侧空白面板"""
        panel = QFrame()
        panel.setObjectName("brand_panel")
        
        # 简单的空白布局
        layout = QVBoxLayout()
        layout.setContentsMargins(60, 80, 60, 80)
        layout.setSpacing(40)
        
        # 添加一个占位标签（可选，用于调试）
        placeholder_label = QLabel("")
        placeholder_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(placeholder_label)
        
        panel.setLayout(layout)
        return panel
    
    def create_login_panel(self) -> QFrame:
        """创建登录表单面板"""
        panel = QFrame()
        panel.setObjectName("login_panel")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(50, 60, 50, 60)
        layout.setSpacing(30)
        
        # 顶部空间
        top_spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(top_spacer)
        
        # 登录标题
        login_title = QLabel("自动登录")
        login_title.setObjectName("login_title")
        login_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(login_title)
        
        # 登录副标题
        login_subtitle = QLabel("系统将在3秒后自动登录")
        login_subtitle.setObjectName("login_subtitle")
        login_subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(login_subtitle)
        
        # 表单区域
        form_widget = self.create_login_form()
        layout.addWidget(form_widget)
        
        # 选项区域
        options_widget = self.create_login_options()
        layout.addWidget(options_widget)
        
        # 登录按钮
        self.login_button = self.create_login_button()
        layout.addWidget(self.login_button)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("login_progress")
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # 主题切换
        theme_widget = self.create_theme_selector()
        layout.addWidget(theme_widget)
        
        # 底部空间
        bottom_spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(bottom_spacer)
        
        panel.setLayout(layout)
        return panel
    
    def create_login_form(self) -> QWidget:
        """创建登录表单"""
        form_widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # 用户名输入
        self.username_input = self.create_input_field("👤", "用户名", "自动登录，无需输入")
        # 设置默认值并禁用
        username_line_edit = self.username_input.findChild(QLineEdit)
        username_line_edit.setText("admin")
        username_line_edit.setEnabled(False)
        layout.addWidget(self.username_input)
        
        # 密码输入
        self.password_input = self.create_input_field("🔒", "密码", "自动登录，无需输入", is_password=True)
        # 设置默认值并禁用
        password_line_edit = self.password_input.findChild(QLineEdit)
        password_line_edit.setText("admin123")
        password_line_edit.setEnabled(False)
        layout.addWidget(self.password_input)
        
        form_widget.setLayout(layout)
        return form_widget
    
    def create_input_field(self, icon: str, label: str, placeholder: str, is_password: bool = False) -> QFrame:
        """创建输入字段"""
        field = QFrame()
        field.setObjectName("input_field")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # 标签
        label_widget = QLabel(f"{icon} {label}")
        label_widget.setObjectName("input_label")
        layout.addWidget(label_widget)
        
        # 输入框 - 改为相对高度
        input_widget = QLineEdit()
        input_widget.setObjectName("input_widget")
        input_widget.setPlaceholderText(placeholder)
        # 移除固定高度，改为最小高度
        input_widget.setMinimumHeight(40)
        input_widget.setMaximumHeight(60)
        
        if is_password:
            input_widget.setEchoMode(QLineEdit.Password)
        
        layout.addWidget(input_widget)
        field.setLayout(layout)
        
        return field
    
    def create_login_options(self) -> QWidget:
        """创建登录选项"""
        options_widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 记住密码
        self.remember_checkbox = QCheckBox("记住密码")
        self.remember_checkbox.setObjectName("remember_checkbox")
        self.remember_checkbox.setEnabled(False)  # 禁用，因为是自动登录
        self.remember_checkbox.setChecked(True)   # 默认选中
        layout.addWidget(self.remember_checkbox)
        
        # 弹簧
        layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        
        # 自动登录
        self.auto_login_checkbox = QCheckBox("自动登录")
        self.auto_login_checkbox.setObjectName("auto_login_checkbox")
        self.auto_login_checkbox.setEnabled(False)  # 禁用，因为已经是自动登录
        self.auto_login_checkbox.setChecked(True)    # 默认选中
        layout.addWidget(self.auto_login_checkbox)
        
        options_widget.setLayout(layout)
        return options_widget
    
    def create_login_button(self) -> QPushButton:
        """创建登录按钮"""
        button = QPushButton("自动登录中... 3s")
        button.setObjectName("login_button")
        # 改为相对高度
        button.setMinimumHeight(40)
        button.setMaximumHeight(60)
        button.setCursor(Qt.PointingHandCursor)
        button.setEnabled(False)  # 禁用手动点击，因为是自动登录
        button.clicked.connect(self.handle_login)
        return button
    
    def create_theme_selector(self) -> QWidget:
        """创建主题选择器"""
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 主题标签
        theme_label = QLabel("主题:")
        theme_label.setObjectName("theme_label")
        layout.addWidget(theme_label)
        
        # 主题下拉框
        self.theme_combo = QComboBox()
        self.theme_combo.setObjectName("theme_combo")
        self.theme_combo.addItems(["深色主题", "浅色主题", "蓝色主题"])
        self.theme_combo.setCurrentText("深色主题")
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        layout.addWidget(self.theme_combo)
        
        # 弹簧
        layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        
        widget.setLayout(layout)
        return widget
    
    def create_window_controls(self):
        """创建窗口控制按钮"""
        # 最小化按钮
        self.minimize_btn = QPushButton("−")
        self.minimize_btn.setObjectName("window_control_btn")
        self.minimize_btn.setFixedSize(30, 30)
        self.minimize_btn.setCursor(Qt.PointingHandCursor)
        self.minimize_btn.clicked.connect(self.showMinimized)
        self.minimize_btn.setParent(self)
        
        # 关闭按钮
        self.close_btn = QPushButton("×")
        self.close_btn.setObjectName("window_control_btn")
        self.close_btn.setFixedSize(30, 30)
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.clicked.connect(self.close)
        self.close_btn.setParent(self)
        
        # 定位按钮
        self.position_window_controls()
    
    def position_window_controls(self):
        """定位窗口控制按钮"""
        if hasattr(self, 'minimize_btn') and hasattr(self, 'close_btn'):
            # 修正按钮位置，考虑边距
            self.minimize_btn.move(self.width() - 70, 10)
            self.close_btn.move(self.width() - 35, 10)
    
    def setup_animations(self):
        """设置动画"""
        # 入场动画
        self.entrance_animation = QParallelAnimationGroup()
        
        # 主容器淡入
        self.fade_in = QPropertyAnimation(self, b"windowOpacity")  # 改为整个窗口的透明度
        self.fade_in.setDuration(600)  # 缩短动画时间
        self.fade_in.setStartValue(0.0)
        self.fade_in.setEndValue(1.0)
        self.fade_in.setEasingCurve(QEasingCurve.OutCubic)
        
        # 主容器缩放
        self.scale_in = QPropertyAnimation(self, b"geometry")  # 改为整个窗口的缩放
        self.scale_in.setDuration(600)  # 缩短动画时间
        self.scale_in.setEasingCurve(QEasingCurve.OutBack)
        
        self.entrance_animation.addAnimation(self.fade_in)
        self.entrance_animation.addAnimation(self.scale_in)
    
    def show_with_animation(self):
        """带动画显示窗口"""
        # 先正常显示，确保布局正确
        self.show()
        self.repaint()
        
        # 如果需要动画效果，可以启用下面的代码
        # 暂时禁用动画，确保界面能正常显示
        return
        
        # 设置初始状态
        center_x = self.x() + self.width() // 2
        center_y = self.y() + self.height() // 2
        small_width = int(self.width() * 0.95)  # 进一步减少缩放程度
        small_height = int(self.height() * 0.95)
        
        start_rect = QRect(
            center_x - small_width // 2,
            center_y - small_height // 2,
            small_width,
            small_height
        )
        
        end_rect = QRect(self.x(), self.y(), self.width(), self.height())
        
        self.scale_in.setStartValue(start_rect)
        self.scale_in.setEndValue(end_rect)
        
        # 开始动画
        self.entrance_animation.start()
    
    def apply_theme(self):
        """应用主题"""
        themes = {
            "深色主题": self.get_dark_theme(),
            "浅色主题": self.get_light_theme(),
            "蓝色主题": self.get_blue_theme()
        }
        
        theme_name = self.theme_combo.currentText() if hasattr(self, 'theme_combo') else "深色主题"
        stylesheet = themes.get(theme_name, themes["深色主题"])
        
        self.setStyleSheet(stylesheet)
        logger.info(f"应用主题: {theme_name}")
    
    def get_dark_theme(self) -> str:
        """获取深色主题样式"""
        return """
        /* 主窗口背景 - 透明 */
        ModernLoginWindow {
            background: transparent;
        }
        
        /* 主容器 - 透明背景，保留边框 */
        #main_container {
            background: transparent;
            border-radius: 20px;
            border: 1px solid #334155;
        }
        
        /* 左侧面板 - 透明背景 */
        #brand_panel {
            background: transparent;
            border-top-left-radius: 20px;
            border-bottom-left-radius: 20px;
        }
        
        /* 登录面板 */
        #login_panel {
            background: #475569;
            border-top-right-radius: 20px;
            border-bottom-right-radius: 20px;
            border: 2px solid #64748B;
            min-width: 320px;
        }
        
        #login_title {
            font-size: 32px;
            font-weight: bold;
            color: #F1F5F9;
            margin-bottom: 10px;
        }
        
        #login_subtitle {
            font-size: 16px;
            color: #CBD5E1;
            margin-bottom: 30px;
        }
        
        #input_field {
            background: transparent;
        }
        
        #input_label {
            font-size: 14px;
            font-weight: 500;
            color: #CBD5E1;
        }
        
        #input_widget {
            background: #334155;
            border: 2px solid #475569;
            border-radius: 12px;
            padding: 0 15px;
            font-size: 16px;
            color: #F1F5F9;
        }
        
        #input_widget:focus {
            border-color: #6366F1;
            background: #475569;
        }
        
        #input_widget:disabled {
            background: #1E293B;
            border-color: #374151;
            color: #6B7280;
        }
        
        #remember_checkbox, #auto_login_checkbox {
            color: #CBD5E1;
            font-size: 14px;
        }
        
        #login_button {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #6366F1, stop:1 #8B5CF6);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 16px;
            font-weight: bold;
        }
        
        #login_button:hover {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #4F46E5, stop:1 #7C3AED);
        }
        
        #login_button:pressed {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #4338CA, stop:1 #6D28D9);
        }
        
        #login_button:disabled {
            background: #374151;
            color: #6B7280;
        }
        
        #login_progress {
            border: none;
            border-radius: 6px;
            background: #334155;
        }
        
        #login_progress::chunk {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #6366F1, stop:1 #8B5CF6);
            border-radius: 6px;
        }
        
        #theme_label {
            color: #CBD5E1;
            font-size: 14px;
        }
        
        #theme_combo {
            background: #334155;
            border: 1px solid #475569;
            border-radius: 8px;
            padding: 5px 10px;
            color: #F1F5F9;
            min-width: 120px;
        }
        
        #theme_combo::drop-down {
            border: none;
        }
        
        #theme_combo::down-arrow {
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid #CBD5E1;
        }
        
        #window_control_btn {
            background: rgba(255, 255, 255, 0.1);
            border: none;
            border-radius: 15px;
            color: rgba(255, 255, 255, 0.8);
            font-size: 16px;
            font-weight: bold;
        }
        
        #window_control_btn:hover {
            background: rgba(255, 255, 255, 0.2);
            color: white;
        }
        """
    
    def get_light_theme(self) -> str:
        """获取浅色主题样式"""
        return """
        /* 主窗口背景 - 透明 */
        ModernLoginWindow {
            background: transparent;
        }
        
        /* 主容器 - 透明背景，保留边框 */
        #main_container {
            background: transparent;
            border-radius: 20px;
            border: 1px solid #E5E7EB;
        }
        
        /* 左侧面板 - 透明背景 */
        #brand_panel {
            background: transparent;
            border-top-left-radius: 20px;
            border-bottom-left-radius: 20px;
        }
        
        /* 登录面板 */
        #login_panel {
            background: #FFFFFF;
            border-top-right-radius: 20px;
            border-bottom-right-radius: 20px;
            border: 2px solid #E5E7EB;
            min-width: 320px;
        }
        
        #login_title {
            font-size: 32px;
            font-weight: bold;
            color: #1F2937;
            margin-bottom: 10px;
        }
        
        #login_subtitle {
            font-size: 16px;
            color: #6B7280;
            margin-bottom: 30px;
        }
        
        #input_field {
            background: transparent;
        }
        
        #input_label {
            font-size: 14px;
            font-weight: 500;
            color: #374151;
        }
        
        #input_widget {
            background: #F9FAFB;
            border: 2px solid #E5E7EB;
            border-radius: 12px;
            padding: 0 15px;
            font-size: 16px;
            color: #1F2937;
        }
        
        #input_widget:focus {
            border-color: #6366F1;
            background: #FFFFFF;
        }
        
        #input_widget:disabled {
            background: #1E293B;
            border-color: #374151;
            color: #6B7280;
        }
        
        #remember_checkbox, #auto_login_checkbox {
            color: #374151;
            font-size: 14px;
        }
        
        #login_button {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #6366F1, stop:1 #8B5CF6);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 16px;
            font-weight: bold;
        }
        
        #login_button:hover {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #4F46E5, stop:1 #7C3AED);
        }
        
        #login_button:pressed {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #4338CA, stop:1 #6D28D9);
        }
        
        #login_button:disabled {
            background: #374151;
            color: #6B7280;
        }
        
        #login_progress {
            border: none;
            border-radius: 6px;
            background: #E5E7EB;
        }
        
        #login_progress::chunk {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #6366F1, stop:1 #8B5CF6);
            border-radius: 6px;
        }
        
        #theme_label {
            color: #374151;
            font-size: 14px;
        }
        
        #theme_combo {
            background: #F9FAFB;
            border: 1px solid #E5E7EB;
            border-radius: 8px;
            padding: 5px 10px;
            color: #1F2937;
            min-width: 120px;
        }
        
        #theme_combo::drop-down {
            border: none;
        }
        
        #theme_combo::down-arrow {
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid #6B7280;
        }
        
        #window_control_btn {
            background: rgba(0, 0, 0, 0.1);
            border: none;
            border-radius: 15px;
            color: rgba(0, 0, 0, 0.6);
            font-size: 16px;
            font-weight: bold;
        }
        
        #window_control_btn:hover {
            background: rgba(0, 0, 0, 0.2);
            color: rgba(0, 0, 0, 0.8);
        }
        """
    
    def get_blue_theme(self) -> str:
        """获取蓝色主题样式"""
        return """
        /* 主窗口背景 - 透明 */
        ModernLoginWindow {
            background: transparent;
        }
        
        /* 主容器 - 透明背景，保留边框 */
        #main_container {
            background: transparent;
            border-radius: 20px;
            border: 1px solid #7DD3FC;
        }
        
        /* 左侧面板 - 透明背景 */
        #brand_panel {
            background: transparent;
            border-top-left-radius: 20px;
            border-bottom-left-radius: 20px;
        }
        
        /* 登录面板 */
        #login_panel {
            background: #FFFFFF;
            border-top-right-radius: 20px;
            border-bottom-right-radius: 20px;
            border: 2px solid #7DD3FC;
            min-width: 320px;
        }
        
        #login_title {
            font-size: 32px;
            font-weight: bold;
            color: #0C4A6E;
            margin-bottom: 10px;
        }
        
        #login_subtitle {
            font-size: 16px;
            color: #0369A1;
            margin-bottom: 30px;
        }
        
        #input_field {
            background: transparent;
        }
        
        #input_label {
            font-size: 14px;
            font-weight: 500;
            color: #0369A1;
        }
        
        #input_widget {
            background: #F0F9FF;
            border: 2px solid #BAE6FD;
            border-radius: 12px;
            padding: 0 15px;
            font-size: 16px;
            color: #0C4A6E;
        }
        
        #input_widget:focus {
            border-color: #0EA5E9;
            background: #FFFFFF;
        }
        
        #input_widget:disabled {
            background: #1E293B;
            border-color: #374151;
            color: #6B7280;
        }
        
        #remember_checkbox, #auto_login_checkbox {
            color: #0369A1;
            font-size: 14px;
        }
        
        #login_button {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #0EA5E9, stop:1 #0284C7);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 16px;
            font-weight: bold;
        }
        
        #login_button:hover {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #0284C7, stop:1 #0369A1);
        }
        
        #login_button:pressed {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #0369A1, stop:1 #075985);
        }
        
        #login_button:disabled {
            background: #374151;
            color: #6B7280;
        }
        
        #login_progress {
            border: none;
            border-radius: 6px;
            background: #BAE6FD;
        }
        
        #login_progress::chunk {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #0EA5E9, stop:1 #0284C7);
            border-radius: 6px;
        }
        
        #theme_label {
            color: #0369A1;
            font-size: 14px;
        }
        
        #theme_combo {
            background: #F0F9FF;
            border: 1px solid #BAE6FD;
            border-radius: 8px;
            padding: 5px 10px;
            color: #0C4A6E;
            min-width: 120px;
        }
        
        #theme_combo::drop-down {
            border: none;
        }
        
        #theme_combo::down-arrow {
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid #0369A1;
        }
        
        #window_control_btn {
            background: rgba(255, 255, 255, 0.1);
            border: none;
            border-radius: 15px;
            color: rgba(255, 255, 255, 0.8);
            font-size: 16px;
            font-weight: bold;
        }
        
        #window_control_btn:hover {
            background: rgba(255, 255, 255, 0.2);
            color: white;
        }
        """
    
    @Slot(str)
    def on_theme_changed(self, theme_name: str):
        """主题切换事件"""
        self.current_theme = theme_name
        self.apply_theme()
        self.theme_changed.emit(theme_name)
    
    @Slot()
    def handle_login(self):
        """处理登录"""
        if self.is_logging_in:
            return
        
        # 获取输入值
        username = self.username_input.findChild(QLineEdit).text().strip()
        password = self.password_input.findChild(QLineEdit).text().strip()
        
        # 验证输入
        if not username:
            self.show_error("请输入用户名")
            return
        
        if not password:
            self.show_error("请输入密码")
            return
        
        # 开始登录过程
        self.start_login_animation()
        
        # 模拟登录验证
        QTimer.singleShot(2000, lambda: self.complete_login(username, password))
    
    def start_login_animation(self):
        """开始登录动画"""
        self.is_logging_in = True
        self.login_button.setText("正在登录...")
        self.login_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 无限进度条
    
    def complete_login(self, username: str, password: str):
        """完成登录"""
        # 停止倒计时定时器
        if hasattr(self, 'countdown_timer') and self.countdown_timer.isActive():
            self.countdown_timer.stop()
            
        # 简单验证（实际项目中应该连接到认证服务）
        if self.validate_credentials(username, password):
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(100)
            
            # 保存凭据
            if self.remember_checkbox.isChecked():
                self.save_credentials(username, password)
            
            QTimer.singleShot(500, lambda: self.login_success.emit(username, password))
        else:
            self.show_error("用户名或密码错误")
            self.reset_login_state()
    
    def validate_credentials(self, username: str, password: str) -> bool:
        """验证凭据 - 暂时跳过验证，直接通过"""
        # 暂时跳过验证，所有用户都能登录
        logger.info(f"跳过验证，用户 {username} 直接登录成功")
        return True
    
    def save_credentials(self, username: str, password: str):
        """保存凭据"""
        # 实际项目中应该加密保存
        logger.info(f"保存用户凭据: {username}")
    
    def show_error(self, message: str):
        """显示错误信息"""
        # 这里可以添加错误提示动画
        logger.error(f"登录错误: {message}")
        self.login_failed.emit(message)
    
    def reset_login_state(self):
        """重置登录状态"""
        self.is_logging_in = False
        self.login_button.setText("自动登录中... 3s")
        self.login_button.setEnabled(False)
        self.progress_bar.setVisible(False)
    
    def resizeEvent(self, event):
        """窗口大小改变事件"""
        super().resizeEvent(event)
        self.position_window_controls()
    
    def mousePressEvent(self, event):
        """鼠标按下事件 - 支持拖拽窗口"""
        if event.button() == Qt.LeftButton:
            # 检查是否点击在窗口控制按钮上
            if hasattr(self, 'minimize_btn') and hasattr(self, 'close_btn'):
                min_btn_rect = self.minimize_btn.geometry()
                close_btn_rect = self.close_btn.geometry()
                click_pos = event.position().toPoint()
                
                # 如果点击在按钮区域，不处理拖动
                if (min_btn_rect.contains(click_pos) or 
                    close_btn_rect.contains(click_pos)):
                    return
            
            # 检查是否点击在输入框或按钮等交互元素上
            widget_at_pos = self.childAt(event.position().toPoint())
            if widget_at_pos and (isinstance(widget_at_pos, (QLineEdit, QPushButton, QCheckBox, QComboBox)) or
                                  widget_at_pos.objectName() in ['input_widget', 'login_button', 'remember_checkbox', 
                                                                'auto_login_checkbox', 'theme_combo']):
                return
            
            # 只在空白区域或标题区域允许拖动
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件 - 拖拽窗口"""
        if (event.buttons() == Qt.LeftButton and 
            hasattr(self, 'drag_position') and 
            self.drag_position is not None):
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
    
    def closeEvent(self, event):
        """关闭事件"""
        # 停止所有定时器
        if hasattr(self, 'countdown_timer') and self.countdown_timer.isActive():
            self.countdown_timer.stop()
        if hasattr(self, 'auto_login_timer') and self.auto_login_timer.isActive():
            self.auto_login_timer.stop()
        
        logger.info("登录窗口关闭")
        event.accept()

    def setup_auto_login(self):
        """设置自动登录定时器"""
        # 更新登录按钮显示倒计时
        self.update_countdown_display()
        # 启动1秒间隔的定时器用于更新倒计时显示
        self.countdown_timer.timeout.connect(self.update_countdown_display)
        self.countdown_timer.start(1000)
    
    def update_countdown_display(self):
        """更新倒计时显示"""
        if self.auto_login_countdown > 0:
            self.login_button.setText(f"自动登录中... {self.auto_login_countdown}s")
            self.auto_login_countdown -= 1
        else:
            # 倒计时结束，执行自动登录
            self.countdown_timer.stop()
            self.handle_auto_login()
    
    @Slot()
    def handle_auto_login(self):
        """处理自动登录 - 直接登录，无需输入验证"""
        logger.info("开始自动登录...")
        
        # 使用默认用户信息
        default_username = "admin"
        default_password = "admin123"
        
        # 开始登录过程
        self.start_login_animation()
        
        # 直接完成登录
        QTimer.singleShot(1000, lambda: self.complete_login(default_username, default_password))


def main():
    """测试函数"""
    app = QApplication(sys.argv)
    
    # 设置应用属性
    app.setApplicationName("Pank Ins")
    app.setApplicationVersion("1.0.0")
    
    # 创建登录窗口
    login_window = ModernLoginWindow()
    
    # 连接信号
    login_window.login_success.connect(
        lambda u, p: print(f"登录成功: {u}")
    )
    login_window.login_failed.connect(
        lambda msg: print(f"登录失败: {msg}")
    )
    
    # 显示窗口
    login_window.show_with_animation()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 