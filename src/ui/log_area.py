"""
日志区域组件

提供系统日志显示和管理功能
"""

from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
from datetime import datetime


class LogArea(QFrame):
    """
    日志区域组件
    
    显示系统日志信息
    """
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_logging()
        
    def setup_ui(self):
        """
        设置日志区域界面
        """
        self.setFrameStyle(QFrame.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background-color: #1a202c;
                border-top: 1px solid #e2e8f0;
                border-radius: 8px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # 日志标题栏
        header_layout = QHBoxLayout()
        
        title = QLabel("系统日志")
        title.setFont(QFont("微软雅黑", 11, QFont.Bold))
        title.setStyleSheet("color: #e2e8f0; padding: 5px;")
        
        # 清空按钮
        clear_btn = QPushButton("清空日志")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a5568;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 10px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #718096;
            }
        """)
        clear_btn.clicked.connect(self.clear_logs)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(clear_btn)
        
        layout.addLayout(header_layout)
        
        # 日志文本区域
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 9))
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #2d3748;
                color: #e2e8f0;
                border: 1px solid #4a5568;
                border-radius: 6px;
                padding: 8px;
                selection-background-color: #667eea;
            }
        """)
        
        layout.addWidget(self.log_text)
        
        self.setLayout(layout)
        
    def setup_logging(self):
        """
        设置日志记录
        """
        # 添加一些示例日志
        self.add_log("INFO", "系统启动完成")
        self.add_log("INFO", "UI界面初始化完成")
        self.add_log("DEBUG", "等待用户操作...")
        
        # 设置定时器模拟日志更新
        self.log_timer = QTimer()
        self.log_timer.timeout.connect(self.update_logs)
        self.log_timer.start(5000)  # 每5秒更新一次
        
    def add_log(self, level, message):
        """
        添加日志信息
        
        Args:
            level (str): 日志级别
            message (str): 日志消息
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # 根据日志级别设置颜色
        color_map = {
            "INFO": "#48bb78",
            "DEBUG": "#90cdf4", 
            "WARNING": "#ed8936",
            "ERROR": "#f56565"
        }
        
        color = color_map.get(level, "#e2e8f0")
        
        log_entry = f'<span style="color: #a0aec0;">[{timestamp}]</span> <span style="color: {color}; font-weight: bold;">[{level}]</span> <span style="color: #e2e8f0;">{message}</span>'
        
        self.log_text.append(log_entry)
        
        # 自动滚动到底部
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
    def clear_logs(self):
        """
        清空日志
        """
        self.log_text.clear()
        self.add_log("INFO", "日志已清空")
        
    def update_logs(self):
        """
        更新日志（模拟）
        """
        import random
        messages = [
            ("INFO", "系统运行正常"),
            ("DEBUG", "检查设备连接状态"),
            ("INFO", "数据处理完成"),
            ("DEBUG", "内存使用率: 45%")
        ]
        
        level, message = random.choice(messages)
        self.add_log(level, message) 