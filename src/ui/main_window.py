#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
主窗口模块

AI示波器控制系统的主用户界面。

@author: PankIns Team
@version: 1.0.0
"""

import logging
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QSplitter, QFrame, QLabel
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QIcon, QFont

from .toolbar import ToolBar
from .workflow_panel import WorkflowPanel
from .workspace_panel import WorkspacePanel
from .chat_panel import ChatPanel


class ModernSplitter(QSplitter):
    """现代化分割器"""
    
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.setHandleWidth(1)
        self.setStyleSheet("""
            QSplitter::handle {
                background: #E0E0E0;
                margin: 0px;
            }
            QSplitter::handle:hover {
                background: #4A90E2;
            }
            QSplitter::handle:pressed {
                background: #357ABD;
            }
        """)


class MainWindow(QMainWindow):
    """
    主窗口类
    
    提供AI示波器控制系统的主用户界面
    """
    
    # 信号定义
    status_updated = pyqtSignal(str)
    data_received = pyqtSignal(dict)
    
    def __init__(self, system_manager):
        """
        初始化主窗口
        
        @param {SystemManager} system_manager - 系统管理器实例
        """
        super().__init__()
        self.system_manager = system_manager
        self.logger = logging.getLogger(__name__)
        
        # 窗口属性
        self.setWindowTitle("AI示波器控制系统 v1.0.0")
        self.setGeometry(100, 100, 1600, 900)
        self.setMinimumSize(1200, 700)
        
        # 设置窗口样式
        self._setup_window_style()
        
        # 初始化UI
        self._init_ui()
        self._setup_connections()
        
        self.logger.info("主窗口初始化完成")
    
    def _setup_window_style(self):
        """设置窗口样式"""
        self.setStyleSheet("""
            QMainWindow {
                background: #F5F5F5;
                color: #333333;
                font-family: 'Microsoft YaHei UI', 'Microsoft YaHei', 'Segoe UI', sans-serif;
                font-size: 9pt;
                font-weight: normal;
            }
            
            QMainWindow::separator {
                background: #E0E0E0;
                width: 1px;
                height: 1px;
            }
            
            QStatusBar {
                background: #FFFFFF;
                border-top: 1px solid #E0E0E0;
                color: #666666;
                font-size: 9pt;
                font-family: 'Microsoft YaHei UI', 'Microsoft YaHei', sans-serif;
                padding: 2px 8px;
            }
            
            QLabel {
                font-family: 'Microsoft YaHei UI', 'Microsoft YaHei', 'Segoe UI', sans-serif;
                font-weight: normal;
            }
            
            QTextEdit {
                font-family: 'Microsoft YaHei UI', 'Microsoft YaHei', 'Segoe UI', sans-serif;
                font-weight: normal;
            }
            
            QPushButton {
                font-family: 'Microsoft YaHei UI', 'Microsoft YaHei', 'Segoe UI', sans-serif;
                font-weight: normal;
            }
        """)
    
    def _init_ui(self):
        """
        初始化用户界面
        """
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)
        
        # 工具栏
        self.toolbar = ToolBar(self)
        self.addToolBar(self.toolbar)
        
        # 创建主要内容区域
        content_frame = QFrame()
        content_frame.setStyleSheet("""
            QFrame {
                background: #F5F5F5;
                border: none;
            }
        """)
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(4, 4, 4, 4)
        content_layout.setSpacing(4)
        
        # 创建水平分割器
        splitter = ModernSplitter(Qt.Orientation.Horizontal)
        
        # 流程卡片面板
        self.workflow_panel = WorkflowPanel()
        workflow_container = self._create_panel_container("流程管理", self.workflow_panel)
        splitter.addWidget(workflow_container)
        
        # 工作区面板
        self.workspace_panel = WorkspacePanel()
        workspace_container = self._create_panel_container("工作区", self.workspace_panel)
        splitter.addWidget(workspace_container)
        
        # AI对话面板
        self.chat_panel = ChatPanel()
        splitter.addWidget(self.chat_panel)
        
        # 设置分割器比例 - 调整为更合理的比例
        splitter.setSizes([220, 900, 380])  # 流程图更小，工作区更大，对话区适中
        
        content_layout.addWidget(splitter)
        main_layout.addWidget(content_frame)
        
        # 状态栏
        self.statusBar().showMessage("就绪")
        self.statusBar().setFont(QFont("Microsoft YaHei", 9))
    
    def _create_panel_container(self, title: str, widget: QWidget) -> QFrame:
        """
        创建面板容器
        
        @param {str} title - 面板标题
        @param {QWidget} widget - 面板内容
        @returns {QFrame} 容器框架
        """
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background: #FFFFFF;
                border: none;
            }
        """)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 标题栏
        header = QFrame()
        header.setFixedHeight(32)
        header.setStyleSheet("""
            QFrame {
                background: #F0F0F0;
                border-bottom: 1px solid #E0E0E0;
            }
        """)
        
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(10, 0, 10, 0)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Microsoft YaHei", 8, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #555555; background: transparent;")
        header_layout.addWidget(title_label)
        
        # 内容区域
        content_container = QFrame()
        content_container.setStyleSheet("""
            QFrame {
                background: transparent;
                border: none;
            }
        """)
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.addWidget(widget)
        
        layout.addWidget(header)
        layout.addWidget(content_container)
        
        return container
    
    def _setup_connections(self):
        """
        设置信号连接
        """
        # 工具栏连接
        self.toolbar.connect_action.triggered.connect(self._on_connect_clicked)
        self.toolbar.acquire_action.triggered.connect(self._on_acquire_clicked)
        self.toolbar.save_action.triggered.connect(self._on_save_clicked)
        self.toolbar.export_action.triggered.connect(self._on_export_clicked)
        self.toolbar.settings_action.triggered.connect(self._on_settings_clicked)
        
        # 流程卡片连接
        self.workflow_panel.card_selected.connect(self._on_workflow_card_selected)
        
        # AI对话连接
        self.chat_panel.message_sent.connect(self._on_chat_message_sent)
        
        # 信号连接
        self.status_updated.connect(self._on_status_updated)
        self.data_received.connect(self._on_data_received)
    
    def _on_connect_clicked(self, checked):
        """
        连接按钮点击处理
        """
        if checked:
            self.logger.info("连接设备")
            self.workspace_panel.append_log("正在连接设备...", "INFO")
            self.statusBar().showMessage("正在连接设备...")
            # 模拟连接成功
            self.toolbar.update_device_status(True)
            self.statusBar().showMessage("设备已连接")
        else:
            self.logger.info("断开设备")
            self.workspace_panel.append_log("设备已断开", "INFO")
            self.toolbar.update_device_status(False)
            self.statusBar().showMessage("设备已断开")
    
    def _on_acquire_clicked(self, checked):
        """
        采集按钮点击处理
        """
        if checked:
            self.logger.info("开始数据采集")
            self.workspace_panel.append_log("开始数据采集...", "INFO")
            self.toolbar.acquire_action.setText("停止采集")
            self.statusBar().showMessage("正在采集数据...")
        else:
            self.logger.info("停止数据采集")
            self.workspace_panel.append_log("数据采集已停止", "INFO")
            self.toolbar.acquire_action.setText("开始采集")
            self.statusBar().showMessage("数据采集已停止")
    
    def _on_save_clicked(self):
        """
        保存按钮点击处理
        """
        self.logger.info("保存数据")
        self.workspace_panel.append_log("正在保存数据...", "INFO")
        self.statusBar().showMessage("正在保存数据...")
    
    def _on_export_clicked(self):
        """
        导出按钮点击处理
        """
        self.logger.info("导出报告")
        self.workspace_panel.append_log("正在导出报告...", "INFO")
        self.statusBar().showMessage("正在导出报告...")
    
    def _on_settings_clicked(self):
        """
        设置按钮点击处理
        """
        self.logger.info("打开设置")
        self.workspace_panel.append_log("打开设置对话框", "INFO")
        self.statusBar().showMessage("设置已打开")
    
    def _on_workflow_card_selected(self, title):
        """
        流程卡片选择处理
        
        @param {str} title - 选中的卡片标题
        """
        self.logger.info(f"选中流程卡片: {title}")
        self.workspace_panel.append_log(f"执行流程: {title}", "INFO")
        self.statusBar().showMessage(f"正在执行: {title}")
    
    def _on_chat_message_sent(self, message):
        """
        聊天消息发送处理
        
        @param {str} message - 发送的消息
        """
        self.logger.info("发送AI消息")
        self.statusBar().showMessage("AI正在处理您的请求...")
        # 这里会调用系统管理器处理AI消息
    
    def _on_status_updated(self, status):
        """
        状态更新处理
        
        @param {str} status - 状态信息
        """
        self.workspace_panel.append_log(status, "INFO")
        self.statusBar().showMessage(status)
    
    def _on_data_received(self, data):
        """
        数据接收处理
        
        @param {dict} data - 接收到的数据
        """
        self.logger.info(f"接收到数据: {data}")
        self.workspace_panel.append_log("接收到新数据", "INFO")
        self.statusBar().showMessage("接收到新数据")
    
    def closeEvent(self, event):
        """
        窗口关闭事件
        """
        self.logger.info("关闭主窗口")
        # 这里可以添加关闭确认对话框
        event.accept() 