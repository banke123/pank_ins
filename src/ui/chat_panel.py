#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI对话面板组件

实现类似Cursor的AI对话界面。

@author: PankIns Team
@version: 1.0.0
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                            QTextEdit, QPushButton, QFrame, QScrollArea, QLabel)
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QTimer
from PyQt6.QtGui import QFont, QTextCursor, QPainter, QPainterPath, QColor


class MessageBubble(QFrame):
    """
    消息气泡组件
    
    显示单条对话消息，采用气泡式设计
    """
    
    def __init__(self, message: str, is_user: bool = False, parent=None):
        """
        初始化消息气泡
        
        @param {str} message - 消息内容
        @param {bool} is_user - 是否为用户消息
        @param {QWidget} parent - 父窗口
        """
        super().__init__(parent)
        self.is_user = is_user
        self.setFixedWidth(280)  # 限制气泡宽度
        self._init_ui(message)
    
    def _init_ui(self, message: str):
        """
        初始化UI
        
        @param {str} message - 消息内容
        """
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 创建气泡容器
        bubble_container = QFrame()
        bubble_layout = QVBoxLayout(bubble_container)
        bubble_layout.setContentsMargins(16, 12, 16, 12)
        
        # 消息文本
        text_label = QLabel(message)
        text_label.setWordWrap(True)
        text_label.setFont(QFont("Microsoft YaHei UI", 9))
        text_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        text_label.setStyleSheet("""
            QLabel {
                background: transparent;
                line-height: 1.4;
                font-family: 'Microsoft YaHei UI', 'Microsoft YaHei', sans-serif;
            }
        """)
        
        bubble_layout.addWidget(text_label)
        
        # 设置气泡样式
        if self.is_user:
            bubble_container.setStyleSheet("""
                QFrame {
                    background: #4A90E2;
                    border-radius: 2px;
                    margin: 3px 0px 3px 40px;
                    border: none;
                }
                QLabel {
                    color: white;
                    background: transparent;
                }
            """)
        else:
            bubble_container.setStyleSheet("""
                QFrame {
                    background: #F5F5F5;
                    border-radius: 2px;
                    margin: 3px 40px 3px 0px;
                    border: none;
                }
                QLabel {
                    color: #333333;
                    background: transparent;
                }
            """)
        
        layout.addWidget(bubble_container)


class TypingIndicator(QFrame):
    """
    打字指示器组件
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(40)
        self._init_ui()
        self._setup_animation()
    
    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 8, 20, 8)
        
        # AI头像指示
        avatar = QLabel("🤖")
        avatar.setFont(QFont("Segoe UI Emoji", 12))
        layout.addWidget(avatar)
        
        # 打字点动画
        self.dots_label = QLabel("AI正在思考")
        self.dots_label.setFont(QFont("Microsoft YaHei UI", 9))
        self.dots_label.setStyleSheet("color: #6C757D; font-family: 'Microsoft YaHei UI', 'Microsoft YaHei', sans-serif;")
        layout.addWidget(self.dots_label)
        
        layout.addStretch()
        
        self.setStyleSheet("""
            QFrame {
                background: #F5F5F5;
                border-radius: 2px;
                margin: 3px 40px 3px 0px;
                border: none;
            }
        """)
    
    def _setup_animation(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self._animate_dots)
        self.dot_count = 0
    
    def start_animation(self):
        self.timer.start(500)
        self.show()
    
    def stop_animation(self):
        self.timer.stop()
        self.hide()
    
    def _animate_dots(self):
        self.dot_count = (self.dot_count + 1) % 4
        dots = "." * self.dot_count
        self.dots_label.setText(f"AI正在思考{dots}")


class ModernInputWidget(QFrame):
    """
    现代化输入组件
    """
    
    message_sent = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
    
    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)
        
        # 输入框容器
        input_container = QFrame()
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(16, 8, 16, 8)
        
        # 输入框
        self.input_edit = QTextEdit()
        self.input_edit.setPlaceholderText("输入您的问题...")
        self.input_edit.setMaximumHeight(80)
        self.input_edit.setMinimumHeight(40)
        self.input_edit.setFont(QFont("Microsoft YaHei UI", 9))
        self.input_edit.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.input_edit.setStyleSheet("""
            QTextEdit {
                background: transparent;
                border: none;
                color: #212529;
                selection-background-color: #4A90E2;
                font-family: 'Microsoft YaHei UI', 'Microsoft YaHei', sans-serif;
            }
        """)
        
        input_layout.addWidget(self.input_edit)
        
        # 输入框容器样式
        input_container.setStyleSheet("""
            QFrame {
                background: #FFFFFF;
                border: 1px solid #D0D0D0;
                border-radius: 2px;
            }
            QFrame:focus-within {
                border-color: #4A90E2;
            }
        """)
        
        # 发送按钮
        self.send_button = QPushButton("发送")
        self.send_button.setFixedSize(80, 40)
        self.send_button.setFont(QFont("Microsoft YaHei UI", 9, QFont.Weight.Normal))
        self.send_button.setStyleSheet("""
            QPushButton {
                background: #4A90E2;
                color: white;
                border: none;
                border-radius: 2px;
                font-weight: normal;
                font-family: 'Microsoft YaHei UI', 'Microsoft YaHei', sans-serif;
            }
            QPushButton:hover {
                background: #357ABD;
            }
            QPushButton:pressed {
                background: #2E6DA4;
            }
            QPushButton:disabled {
                background: #CCCCCC;
            }
        """)
        
        layout.addWidget(input_container, stretch=1)
        layout.addWidget(self.send_button)
        
        # 连接信号
        self.send_button.clicked.connect(self._send_message)
        self.input_edit.textChanged.connect(self._on_text_changed)
        
        # 设置容器样式
        self.setStyleSheet("""
            ModernInputWidget {
                background: #F8F8F8;
                border-top: 1px solid #E0E0E0;
            }
        """)
    
    def _send_message(self):
        message = self.input_edit.toPlainText().strip()
        if message:
            self.message_sent.emit(message)
            self.input_edit.clear()
    
    def _on_text_changed(self):
        # 自动调整输入框高度
        doc_height = self.input_edit.document().size().height()
        new_height = min(max(int(doc_height) + 16, 40), 80)
        self.input_edit.setFixedHeight(new_height)
        
        # 根据是否有内容启用/禁用发送按钮
        has_text = bool(self.input_edit.toPlainText().strip())
        self.send_button.setEnabled(has_text)


class ChatPanel(QWidget):
    """
    AI对话面板
    
    现代化的AI对话界面
    """
    
    message_sent = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 标题栏
        header = QFrame()
        header.setFixedHeight(32)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(12, 0, 12, 0)
        
        title_label = QLabel("AI助手")
        title_label.setFont(QFont("Microsoft YaHei UI", 8, QFont.Weight.Normal))
        title_label.setStyleSheet("color: #333333; font-family: 'Microsoft YaHei UI', 'Microsoft YaHei', sans-serif;")
        
        status_label = QLabel("● 在线")
        status_label.setFont(QFont("Microsoft YaHei UI", 7))
        status_label.setStyleSheet("color: #28A745; font-family: 'Microsoft YaHei UI', 'Microsoft YaHei', sans-serif;")
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(status_label)
        
        header.setStyleSheet("""
            QFrame {
                background: #F0F0F0;
                border: none;
            }
        """)
        
        # 对话历史区域
        self.history_area = QWidget()
        self.history_layout = QVBoxLayout(self.history_area)
        self.history_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.history_layout.setSpacing(8)
        self.history_layout.setContentsMargins(16, 16, 16, 16)
        
        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidget(self.history_area)
        scroll.setWidgetResizable(True)
        scroll.setFrameStyle(QFrame.Shape.NoFrame)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        scroll.setStyleSheet("""
            QScrollArea {
                background: #FFFFFF;
                border: none;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: rgba(0, 0, 0, 0.2);
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(0, 0, 0, 0.3);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # 打字指示器
        self.typing_indicator = TypingIndicator()
        self.typing_indicator.hide()
        
        # 输入组件
        self.input_widget = ModernInputWidget()
        self.input_widget.message_sent.connect(self._on_message_sent)
        
        # 添加到主布局
        layout.addWidget(header)
        layout.addWidget(scroll, stretch=1)
        layout.addWidget(self.typing_indicator)
        layout.addWidget(self.input_widget)
        
        # 设置整体样式
        self.setStyleSheet("""
            ChatPanel {
                background: #FFFFFF;
                border: none;
            }
        """)
        
        # 添加欢迎消息
        self.add_message("您好！我是您的AI示波器助手，我可以帮助您分析波形、设置参数和解释测量结果。有什么可以帮助您的吗？", False)
    
    def _on_message_sent(self, message: str):
        """处理消息发送"""
        self.add_message(message, True)
        self.message_sent.emit(message)
        
        # 显示打字指示器
        self.typing_indicator.start_animation()
        
        # 模拟AI回复（实际应用中这里会调用AI接口）
        QTimer.singleShot(2000, self._simulate_ai_response)
    
    def _simulate_ai_response(self):
        """模拟AI回复"""
        self.typing_indicator.stop_animation()
        responses = [
            "我理解您的问题。让我为您分析一下...",
            "根据您提供的信息，我建议您检查以下几个方面：",
            "这是一个很好的问题！让我为您详细解释一下相关的原理。",
            "我已经收到您的请求，正在为您生成相应的测试流程。"
        ]
        import random
        response = random.choice(responses)
        self.add_message(response, False)
    
    def add_message(self, message: str, is_user: bool = False):
        """
        添加新消息
        
        @param {str} message - 消息内容
        @param {bool} is_user - 是否为用户消息
        """
        bubble = MessageBubble(message, is_user, self)
        
        # 消息对齐
        container = QWidget()
        container_layout = QHBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        
        if is_user:
            container_layout.addStretch()
            container_layout.addWidget(bubble)
        else:
            container_layout.addWidget(bubble)
            container_layout.addStretch()
        
        self.history_layout.addWidget(container)
        
        # 滚动到底部
        QTimer.singleShot(50, self._scroll_to_bottom)
    
    def _scroll_to_bottom(self):
        """滚动到底部"""
        scroll = self.findChild(QScrollArea)
        if scroll:
            scroll.verticalScrollBar().setValue(scroll.verticalScrollBar().maximum())
    
    def clear_history(self):
        """清空对话历史"""
        while self.history_layout.count():
            item = self.history_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater() 