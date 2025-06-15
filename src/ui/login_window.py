"""
登录窗口模块

这个模块提供了一个现代化、简洁的登录界面
参考动漫风格设计，左右分栏布局
"""

import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QCheckBox, QFrame,
    QGraphicsDropShadowEffect, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Signal
from PySide6.QtGui import QFont, QPixmap, QPainter, QColor, QBrush, QLinearGradient


class LoginWindow(QWidget):
    """
    登录窗口类
    
    提供用户登录界面，采用左右分栏设计
    左侧为背景图区域，右侧为登录表单
    """
    
    # 定义信号
    login_success = Signal(str, str)  # 登录成功信号，传递用户名和密码
    login_failed = Signal(str)        # 登录失败信号，传递错误信息
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_animations()
        
    def setup_ui(self):
        """
        设置用户界面
        """
        # 设置窗口属性
        self.setWindowTitle("Pank Ins - 登录")
        self.setFixedSize(1000, 650)  # 更大的窗口尺寸
        self.setWindowFlags(Qt.FramelessWindowHint)  # 无边框窗口
        self.setAttribute(Qt.WA_TranslucentBackground)  # 透明背景
        
        # 创建主布局
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 创建主容器
        main_container = QFrame()
        main_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 15px;
            }
        """)
        
        # 创建主容器布局
        container_layout = QHBoxLayout()
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        
        # 创建左侧背景区域
        left_panel = self.create_left_panel()
        container_layout.addWidget(left_panel, 2)  # 占2/3空间
        
        # 创建右侧登录区域
        right_panel = self.create_right_panel()
        container_layout.addWidget(right_panel, 1)  # 占1/3空间
        
        main_container.setLayout(container_layout)
        main_layout.addWidget(main_container)
        self.setLayout(main_layout)
        
        # 添加阴影效果
        self.add_shadow_effect(main_container)
        
        # 添加窗口控制按钮到右上角
        self.create_floating_controls()
        
    def create_floating_controls(self):
        """
        创建浮动的窗口控制按钮（右上角）
        """
        # 最小化按钮
        self.minimize_btn = QPushButton("−", self)
        self.minimize_btn.setFixedSize(24, 24)
        self.minimize_btn.setFont(QFont("Arial", 12, QFont.Bold))
        self.minimize_btn.setCursor(Qt.PointingHandCursor)
        self.minimize_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.8);
                border: none;
                border-radius: 12px;
                color: #718096;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(226, 232, 240, 0.9);
                color: #4a5568;
            }
            QPushButton:pressed {
                background-color: rgba(203, 213, 224, 0.9);
            }
        """)
        self.minimize_btn.clicked.connect(self.showMinimized)
        
        # 关闭按钮
        self.close_btn = QPushButton("×", self)
        self.close_btn.setFixedSize(24, 24)
        self.close_btn.setFont(QFont("Arial", 14, QFont.Bold))
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.8);
                border: none;
                border-radius: 12px;
                color: #718096;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(254, 215, 215, 0.9);
                color: #e53e3e;
            }
            QPushButton:pressed {
                background-color: rgba(254, 178, 178, 0.9);
            }
        """)
        self.close_btn.clicked.connect(self.close)
        
        # 定位按钮到右上角
        self.position_floating_controls()
        
    def position_floating_controls(self):
        """
        定位浮动控制按钮到右上角
        """
        # 最小化按钮位置
        self.minimize_btn.move(self.width() - 60, 15)
        
        # 关闭按钮位置
        self.close_btn.move(self.width() - 30, 15)
        
    def resizeEvent(self, event):
        """
        窗口大小改变事件，重新定位控制按钮
        """
        super().resizeEvent(event)
        if hasattr(self, 'minimize_btn') and hasattr(self, 'close_btn'):
            self.position_floating_controls()
        
    def create_left_panel(self):
        """
        创建左侧背景面板
        
        Returns:
            QFrame: 左侧背景面板
        """
        left_panel = QFrame()
        left_panel.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #667eea, stop: 0.3 #764ba2, 
                    stop: 0.6 #f093fb, stop: 1 #f5576c);
                border-top-left-radius: 15px;
                border-bottom-left-radius: 15px;
                border-top-right-radius: 0px;
                border-bottom-right-radius: 0px;
            }
        """)
        
        # 创建左侧布局
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(40, 40, 40, 40)
        left_layout.setSpacing(20)
        
        # 添加背景图占位符
        bg_placeholder = self.create_background_placeholder()
        left_layout.addWidget(bg_placeholder)
        
        # 添加底部文字
        bottom_text = QLabel("AI 控制示波器系统")
        bottom_text.setAlignment(Qt.AlignCenter)
        bottom_text.setFont(QFont("微软雅黑", 16, QFont.Bold))
        bottom_text.setStyleSheet("""
            QLabel {
                color: white;
                background: rgba(255, 255, 255, 0.1);
                padding: 15px;
                border-radius: 10px;
                margin-top: 20px;
            }
        """)
        left_layout.addWidget(bottom_text)
        
        left_panel.setLayout(left_layout)
        return left_panel
        
    def create_background_placeholder(self):
        """
        创建背景图占位符
        
        Returns:
            QLabel: 背景图占位符
        """
        bg_label = QLabel()
        bg_label.setAlignment(Qt.AlignCenter)
        bg_label.setStyleSheet("""
            QLabel {
                background: rgba(255, 255, 255, 0.1);
                border: 2px dashed rgba(255, 255, 255, 0.3);
                border-radius: 15px;
                color: rgba(255, 255, 255, 0.8);
                font-size: 14px;
                font-weight: bold;
                min-height: 400px;
            }
        """)
        bg_label.setText("背景图片占位符\n\n可以在这里添加\n动漫风格的背景图片\n\n建议尺寸: 600x400")
        return bg_label
        
    def create_right_panel(self):
        """
        创建右侧登录面板
        
        Returns:
            QFrame: 右侧登录面板
        """
        right_panel = QFrame()
        right_panel.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border-top-right-radius: 15px;
                border-bottom-right-radius: 15px;
                border-top-left-radius: 0px;
                border-bottom-left-radius: 0px;
            }
        """)
        
        # 创建右侧布局
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(40, 40, 40, 40)
        right_layout.setSpacing(25)
        
        # 添加Logo和标题区域
        header_section = self.create_header_section()
        right_layout.addWidget(header_section)
        
        # 添加间距
        right_layout.addItem(QSpacerItem(20, 30, QSizePolicy.Minimum, QSizePolicy.Fixed))
        
        # 添加输入框区域
        input_section = self.create_input_section()
        right_layout.addWidget(input_section)
        
        # 添加记住密码和找回密码
        options_section = self.create_options_section()
        right_layout.addWidget(options_section)
        
        # 添加登录按钮
        login_button = self.create_login_button()
        right_layout.addWidget(login_button)
        
        # 添加底部间距
        right_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        right_panel.setLayout(right_layout)
        return right_panel
        
    def create_header_section(self):
        """
        创建头部区域（Logo + 标题）
        
        Returns:
            QWidget: 头部区域组件
        """
        header_widget = QWidget()
        header_layout = QVBoxLayout()
        header_layout.setSpacing(15)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Logo区域
        logo_container = QWidget()
        logo_layout = QHBoxLayout()
        logo_layout.setContentsMargins(0, 0, 0, 0)
        
        # Logo占位符
        logo_label = QLabel("P")
        logo_label.setFixedSize(60, 60)
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setFont(QFont("Arial", 24, QFont.Bold))
        logo_label.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #667eea, stop: 1 #764ba2);
                color: white;
                border-radius: 30px;
                font-weight: bold;
            }
        """)
        
        logo_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        logo_layout.addWidget(logo_label)
        logo_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        logo_container.setLayout(logo_layout)
        
        # 标题
        title_label = QLabel("欢迎使用 Pank Ins")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("微软雅黑", 20, QFont.Bold))
        title_label.setStyleSheet("""
            QLabel {
                color: #2d3748;
                margin: 10px 0;
            }
        """)
        
        # 副标题
        subtitle_label = QLabel("AI 智能示波器控制系统")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setFont(QFont("微软雅黑", 12))
        subtitle_label.setStyleSheet("""
            QLabel {
                color: #718096;
                margin-bottom: 10px;
            }
        """)
        
        header_layout.addWidget(logo_container)
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        header_widget.setLayout(header_layout)
        
        return header_widget
        
    def create_input_section(self):
        """
        创建输入框区域
        
        Returns:
            QWidget: 输入框区域组件
        """
        input_widget = QWidget()
        input_layout = QVBoxLayout()
        input_layout.setSpacing(20)
        
        # 用户名输入框
        self.username_input = self.create_input_field("用户名", "example@example.com")
        input_layout.addWidget(self.username_input)
        
        # 密码输入框
        self.password_input = self.create_input_field("密码", "请输入您的密码", is_password=True)
        input_layout.addWidget(self.password_input)
        
        input_widget.setLayout(input_layout)
        return input_widget
        
    def create_input_field(self, label_text, placeholder_text, is_password=False):
        """
        创建输入框字段
        
        Args:
            label_text (str): 标签文本
            placeholder_text (str): 占位符文本
            is_password (bool): 是否为密码输入框
            
        Returns:
            QWidget: 输入框字段组件
        """
        field_widget = QWidget()
        field_layout = QVBoxLayout()
        field_layout.setSpacing(8)
        field_layout.setContentsMargins(0, 0, 0, 0)
        
        # 标签
        label = QLabel(label_text)
        label.setFont(QFont("微软雅黑", 11, QFont.Medium))
        label.setStyleSheet("""
            QLabel {
                color: #4a5568;
                font-weight: 500;
            }
        """)
        field_layout.addWidget(label)
        
        # 输入框
        input_field = QLineEdit()
        input_field.setPlaceholderText(placeholder_text)
        input_field.setFont(QFont("微软雅黑", 11))
        input_field.setFixedHeight(45)
        
        if is_password:
            input_field.setEchoMode(QLineEdit.Password)
            
        input_field.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                padding: 12px 16px;
                background-color: #ffffff;
                color: #2d3748;
                font-size: 11px;
            }
            QLineEdit:focus {
                border-color: #667eea;
                outline: none;
                background-color: #f7fafc;
            }
            QLineEdit:hover {
                border-color: #cbd5e0;
            }
        """)
        
        field_layout.addWidget(input_field)
        field_widget.setLayout(field_layout)
        
        return field_widget
        
    def create_options_section(self):
        """
        创建选项区域（记住密码 + 找回密码）
        
        Returns:
            QWidget: 选项区域组件
        """
        options_widget = QWidget()
        options_layout = QHBoxLayout()
        options_layout.setContentsMargins(0, 0, 0, 0)
        
        # 记住密码复选框
        self.remember_checkbox = QCheckBox("记住密码")
        self.remember_checkbox.setFont(QFont("微软雅黑", 10))
        self.remember_checkbox.setStyleSheet("""
            QCheckBox {
                color: #4a5568;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid #e2e8f0;
                background-color: #ffffff;
            }
            QCheckBox::indicator:checked {
                background-color: #667eea;
                border-color: #667eea;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEwIDNMNC41IDguNUwyIDYiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+Cjwvc3ZnPgo=);
            }
            QCheckBox::indicator:hover {
                border-color: #cbd5e0;
            }
        """)
        
        # 找回密码链接
        forgot_password = QLabel('<a href="#" style="color: #667eea; text-decoration: none;">找回密码</a>')
        forgot_password.setFont(QFont("微软雅黑", 10))
        forgot_password.setStyleSheet("""
            QLabel {
                color: #667eea;
            }
            QLabel:hover {
                color: #5a67d8;
            }
        """)
        forgot_password.setCursor(Qt.PointingHandCursor)
        
        options_layout.addWidget(self.remember_checkbox)
        options_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        options_layout.addWidget(forgot_password)
        
        options_widget.setLayout(options_layout)
        return options_widget
        
    def create_login_button(self):
        """
        创建登录按钮
        
        Returns:
            QPushButton: 登录按钮
        """
        login_button = QPushButton("登录")
        login_button.setFixedHeight(50)
        login_button.setFont(QFont("微软雅黑", 13, QFont.Bold))
        login_button.setCursor(Qt.PointingHandCursor)
        
        login_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #667eea, stop: 1 #764ba2);
                color: white;
                border: none;
                border-radius: 25px;
                font-size: 13px;
                font-weight: bold;
                margin-top: 10px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #5a67d8, stop: 1 #6b46c1);
            }
            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #4c51bf, stop: 1 #553c9a);
            }
        """)
        
        # 连接登录事件
        login_button.clicked.connect(self.handle_login)
        
        return login_button
        
    def add_shadow_effect(self, widget):
        """
        添加阴影效果
        
        Args:
            widget: 要添加阴影的组件
        """
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 15)
        widget.setGraphicsEffect(shadow)
        
    def setup_animations(self):
        """
        设置动画效果
        """
        # 窗口淡入动画
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(400)
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.setEasingCurve(QEasingCurve.OutCubic)
        
    def show_with_animation(self):
        """
        带动画显示窗口
        """
        self.show()
        self.fade_animation.start()
        
    def handle_login(self):
        """
        处理登录逻辑
        """
        username = self.username_input.findChild(QLineEdit).text().strip()
        password = self.password_input.findChild(QLineEdit).text().strip()
        remember = self.remember_checkbox.isChecked()
        
        # 基本验证
        if not username:
            self.show_error("请输入用户名")
            return
            
        if not password:
            self.show_error("请输入密码")
            return
            
        # 这里可以添加实际的登录验证逻辑
        if self.validate_credentials(username, password):
            if remember:
                self.save_credentials(username, password)
            self.login_success.emit(username, password)
            self.close()
        else:
            self.login_failed.emit("用户名或密码错误")
            
    def validate_credentials(self, username, password):
        """
        验证用户凭证（演示用）
        
        Args:
            username (str): 用户名
            password (str): 密码
            
        Returns:
            bool: 验证结果
        """
        # 这里是演示代码，实际应该连接到真实的认证系统
        return len(username) >= 3 and len(password) >= 6
        
    def save_credentials(self, username, password):
        """
        保存用户凭证（如果选择了记住密码）
        
        Args:
            username (str): 用户名
            password (str): 密码
        """
        # 这里应该安全地保存凭证
        pass
        
    def show_error(self, message):
        """
        显示错误信息
        
        Args:
            message (str): 错误信息
        """
        print(f"登录错误: {message}")
        
    def mousePressEvent(self, event):
        """
        鼠标按下事件，用于拖拽窗口
        """
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
            
    def mouseMoveEvent(self, event):
        """
        鼠标移动事件，用于拖拽窗口
        """
        if event.buttons() == Qt.LeftButton and hasattr(self, 'drag_position'):
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()


# def main():
#     """
#     主函数，用于测试登录窗口
#     """
#     app = QApplication(sys.argv)
    
#     # 创建登录窗口
#     login_window = LoginWindow()
    
#     # 连接信号
#     login_window.login_success.connect(lambda u, p: print(f"登录成功: {u}"))
#     login_window.login_failed.connect(lambda e: print(f"登录失败: {e}"))
    
#     # 显示窗口
#     login_window.show_with_animation()
    
#     sys.exit(app.exec())


# if __name__ == "__main__":
#     main() 