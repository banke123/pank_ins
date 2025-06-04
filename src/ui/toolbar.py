#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
工具栏组件

提供主窗口的工具栏功能。

@author: PankIns Team
@version: 1.0.0
"""

from PyQt6.QtWidgets import QToolBar, QWidget, QHBoxLayout, QLabel, QSizePolicy
from PyQt6.QtGui import QIcon, QAction, QFont
from PyQt6.QtCore import Qt


class ToolBar(QToolBar):
    """
    工具栏类
    
    提供主要的工具按钮和操作
    """
    
    def __init__(self, parent=None):
        """
        初始化工具栏
        
        @param {QWidget} parent - 父窗口
        """
        super().__init__(parent)
        self.setMovable(False)  # 固定工具栏
        self.setFloatable(False)
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        
        self._init_actions()
        self._setup_toolbar()
    
    def _init_actions(self):
        """
        初始化工具栏动作
        """
        # 连接/断开设备
        self.connect_action = QAction("🔌 连接设备", self)
        self.connect_action.setCheckable(True)
        self.connect_action.setToolTip("连接或断开示波器设备")
        
        # 开始/停止采集
        self.acquire_action = QAction("▶️ 开始采集", self)
        self.acquire_action.setCheckable(True)
        self.acquire_action.setEnabled(False)  # 初始禁用
        self.acquire_action.setToolTip("开始或停止数据采集")
        
        # 保存数据
        self.save_action = QAction("💾 保存数据", self)
        self.save_action.setEnabled(False)  # 初始禁用
        self.save_action.setToolTip("保存采集的数据")
        
        # 导出报告
        self.export_action = QAction("📊 导出报告", self)
        self.export_action.setToolTip("导出分析报告")
        
        # 设置
        self.settings_action = QAction("⚙️ 设置", self)
        self.settings_action.setToolTip("打开系统设置")
    
    def _setup_toolbar(self):
        """
        设置工具栏布局
        """
        # 设置工具栏高度
        self.setFixedHeight(50)
        
        # 添加动作
        self.addAction(self.connect_action)
        self.addAction(self.acquire_action)
        self.addSeparator()
        self.addAction(self.save_action)
        self.addAction(self.export_action)
        self.addSeparator()
        self.addAction(self.settings_action)
        
        # 添加弹性空间
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.addWidget(spacer)
        
        # 添加状态指示器
        self.status_label = QLabel("● 离线")
        self.status_label.setFont(QFont("Microsoft YaHei UI", 8))
        self.status_label.setStyleSheet("""
            QLabel {
                color: #DC3545;
                background: #FFEBEE;
                padding: 3px 8px;
                border-radius: 2px;
                margin: 4px;
                border: 1px solid #FFCDD2;
                font-family: 'Microsoft YaHei UI', 'Microsoft YaHei', sans-serif;
            }
        """)
        self.addWidget(self.status_label)
        
        # 设置工具栏样式
        self.setStyleSheet("""
            QToolBar {
                background: #FFFFFF;
                border: none;
                border-bottom: 1px solid #D0D0D0;
                spacing: 4px;
                padding: 3px 10px;
            }
            
            QToolBar QToolButton {
                background: #F5F5F5;
                border: 1px solid #D0D0D0;
                border-radius: 2px;
                padding: 4px 10px;
                margin: 1px;
                font-family: 'Microsoft YaHei UI', 'Microsoft YaHei', 'Segoe UI', sans-serif;
                font-size: 8pt;
                font-weight: normal;
                color: #333333;
                min-width: 70px;
                text-align: left;
            }
            
            QToolBar QToolButton:hover {
                background: #E8F2FF;
                border-color: #4A90E2;
                color: #2E5A87;
            }
            
            QToolBar QToolButton:pressed {
                background: #D6E8FF;
                border-color: #357ABD;
            }
            
            QToolBar QToolButton:checked {
                background: #4A90E2;
                border-color: #357ABD;
                color: white;
            }
            
            QToolBar QToolButton:disabled {
                background: #F0F0F0;
                border-color: #E0E0E0;
                color: #999999;
            }
            
            QToolBar::separator {
                background: #D0D0D0;
                width: 1px;
                margin: 6px 3px;
            }
        """)
    
    def update_device_status(self, connected: bool):
        """
        更新设备状态
        
        @param {bool} connected - 设备是否连接
        """
        self.connect_action.setChecked(connected)
        self.acquire_action.setEnabled(connected)
        self.save_action.setEnabled(connected)
        
        if connected:
            self.connect_action.setText("🔌 断开设备")
            self.status_label.setText("● 在线")
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #28A745;
                    background: #E8F5E8;
                    padding: 3px 8px;
                    border-radius: 2px;
                    margin: 4px;
                    border: 1px solid #C3E6CB;
                    font-family: 'Microsoft YaHei UI', 'Microsoft YaHei', sans-serif;
                }
            """)
        else:
            self.connect_action.setText("🔌 连接设备")
            self.acquire_action.setChecked(False)
            self.acquire_action.setText("▶️ 开始采集")
            self.status_label.setText("● 离线")
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #DC3545;
                    background: #FFEBEE;
                    padding: 3px 8px;
                    border-radius: 2px;
                    margin: 4px;
                    border: 1px solid #FFCDD2;
                    font-family: 'Microsoft YaHei UI', 'Microsoft YaHei', sans-serif;
                }
            """) 