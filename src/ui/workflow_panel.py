#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
流程卡片面板组件

显示AI对话生成的流程卡片。

@author: PankIns Team
@version: 1.0.0
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QScrollArea, 
                            QLabel, QPushButton, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal


class WorkflowCard(QFrame):
    """
    流程卡片类
    
    显示单个流程步骤
    """
    
    clicked = pyqtSignal(str)  # 卡片点击信号
    
    def __init__(self, title: str, description: str, parent=None):
        """
        初始化流程卡片
        
        @param {str} title - 卡片标题
        @param {str} description - 卡片描述
        @param {QWidget} parent - 父窗口
        """
        super().__init__(parent)
        self.title = title
        
        self._init_ui(title, description)
        self._setup_style()
    
    def _init_ui(self, title: str, description: str):
        """
        初始化卡片UI
        
        @param {str} title - 卡片标题
        @param {str} description - 卡片描述
        """
        layout = QVBoxLayout(self)
        
        # 标题
        title_label = QLabel(title)
        title_label.setStyleSheet("font-weight: bold;")
        
        # 描述
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        
        layout.addWidget(title_label)
        layout.addWidget(desc_label)
    
    def _setup_style(self):
        """
        设置卡片样式
        """
        self.setStyleSheet("""
            WorkflowCard {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                margin: 4px;
            }
            WorkflowCard:hover {
                background-color: #f8f8f8;
                border-color: #ccc;
            }
        """)
    
    def mousePressEvent(self, event):
        """
        鼠标点击事件
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.title)
        super().mousePressEvent(event)


class WorkflowPanel(QWidget):
    """
    流程面板类
    
    管理和显示所有流程卡片
    """
    
    card_selected = pyqtSignal(str)  # 卡片选择信号
    
    def __init__(self, parent=None):
        """
        初始化流程面板
        
        @param {QWidget} parent - 父窗口
        """
        super().__init__(parent)
        self.cards = []  # 存储所有卡片
        
        self._init_ui()
    
    def _init_ui(self):
        """
        初始化面板UI
        """
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # 创建容器widget
        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        scroll.setWidget(self.container)
        layout.addWidget(scroll)
        
        # 设置样式
        self.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #f5f5f5;
            }
            QWidget#container {
                background-color: #f5f5f5;
            }
        """)
        self.container.setObjectName("container")
    
    def add_card(self, title: str, description: str):
        """
        添加新的流程卡片
        
        @param {str} title - 卡片标题
        @param {str} description - 卡片描述
        """
        card = WorkflowCard(title, description, self)
        card.clicked.connect(self._on_card_clicked)
        
        self.cards.append(card)
        self.container_layout.addWidget(card)
    
    def clear_cards(self):
        """
        清空所有卡片
        """
        for card in self.cards:
            card.deleteLater()
        self.cards.clear()
    
    def _on_card_clicked(self, title: str):
        """
        卡片点击处理
        
        @param {str} title - 被点击卡片的标题
        """
        self.card_selected.emit(title) 