#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
工作区面板组件

包含波形显示和日志窗口。

@author: PankIns Team
@version: 1.0.0
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QSplitter,
                            QTextEdit, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal


class WaveformDisplay(QFrame):
    """
    波形显示区域
    
    显示示波器采集的波形数据
    """
    
    def __init__(self, parent=None):
        """
        初始化波形显示区域
        
        @param {QWidget} parent - 父窗口
        """
        super().__init__(parent)
        self._init_ui()
    
    def _init_ui(self):
        """
        初始化UI
        """
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 这里后续会集成matplotlib的Figure
        self.setStyleSheet("""
            WaveformDisplay {
                background-color: black;
                border: none;
            }
        """)
        
        # 设置最小尺寸
        self.setMinimumSize(400, 300)


class LogWindow(QTextEdit):
    """
    日志窗口
    
    显示系统日志信息
    """
    
    def __init__(self, parent=None):
        """
        初始化日志窗口
        
        @param {QWidget} parent - 父窗口
        """
        super().__init__(parent)
        self._init_ui()
    
    def _init_ui(self):
        """
        初始化UI
        """
        self.setReadOnly(True)
        self.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        
        # 设置字体和样式
        self.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 9pt;
                border: none;
            }
        """)
    
    def append_log(self, message: str, level: str = "INFO"):
        """
        添加日志消息
        
        @param {str} message - 日志消息
        @param {str} level - 日志级别
        """
        # 根据日志级别设置颜色
        color = {
            "DEBUG": "#6A9955",
            "INFO": "#d4d4d4",
            "WARNING": "#DCDCAA",
            "ERROR": "#F14C4C",
            "CRITICAL": "#FF0000"
        }.get(level.upper(), "#d4d4d4")
        
        # 格式化日志消息
        formatted_msg = f'<span style="color: {color};">[{level}] {message}</span>'
        self.append(formatted_msg)


class WorkspacePanel(QWidget):
    """
    工作区面板
    
    包含波形显示和日志窗口
    """
    
    def __init__(self, parent=None):
        """
        初始化工作区面板
        
        @param {QWidget} parent - 父窗口
        """
        super().__init__(parent)
        self._init_ui()
    
    def _init_ui(self):
        """
        初始化UI
        """
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 创建垂直分割器
        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.setHandleWidth(1)
        splitter.setStyleSheet("""
            QSplitter::handle:vertical {
                background: #E0E0E0;
                height: 1px;
                margin: 0px;
            }
        """)
        
        # 波形显示区域
        self.waveform_display = WaveformDisplay()
        splitter.addWidget(self.waveform_display)
        
        # 日志窗口
        self.log_window = LogWindow()
        splitter.addWidget(self.log_window)
        
        # 设置分割器比例
        splitter.setSizes([500, 120])  # 波形显示更大，日志窗口固定较小高度
        
        layout.addWidget(splitter)
    
    def append_log(self, message: str, level: str = "INFO"):
        """
        添加日志消息
        
        @param {str} message - 日志消息
        @param {str} level - 日志级别
        """
        self.log_window.append_log(message, level)
    
    def clear_log(self):
        """
        清空日志窗口
        """
        self.log_window.clear() 