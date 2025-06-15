"""
左侧边栏组件

提供基于JSON格式的流程卡片显示，支持点击交互
"""

from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QScrollArea, QWidget, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QPainter, QPainterPath
from datetime import datetime
import json


class ProcessCard(QFrame):
    """
    流程卡片组件
    
    显示单个流程的信息，包括标题、运行状态和基本信息
    """
    
    # 定义信号
    card_clicked = Signal(dict)  # 卡片点击信号，传递流程数据
    
    def __init__(self, process_data):
        super().__init__()
        self.process_data = process_data
        self.is_hovered = False
        self.setup_ui()
        
    def setup_ui(self):
        """
        设置卡片界面
        """
        self.setFixedHeight(120)
        self.setCursor(Qt.PointingHandCursor)
        
        # 根据状态设置样式
        status = self.process_data.get('status', 'idle')
        status_colors = {
            'running': '#48bb78',    # 绿色 - 运行中
            'stopped': '#f56565',    # 红色 - 已停止
            'paused': '#ed8936',     # 橙色 - 暂停
            'idle': '#a0aec0',       # 灰色 - 空闲
            'error': '#e53e3e',      # 深红色 - 错误
            'completed': '#38b2ac'   # 青色 - 完成
        }
        
        self.status_color = status_colors.get(status, '#a0aec0')
        
        self.setStyleSheet(f"""
            ProcessCard {{
                background-color: white;
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                margin: 5px 2px;
            }}
            ProcessCard:hover {{
                border-color: #667eea;
                background-color: #f7fafc;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(8)
        
        # 标题和状态行
        self.create_header(layout)
        
        # 基本信息行
        self.create_info(layout)
        
        # 底部操作提示
        self.create_footer(layout)
        
        self.setLayout(layout)
        
    def create_header(self, parent_layout):
        """
        创建标题和状态行
        
        Args:
            parent_layout: 父布局
        """
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)
        
        # 流程标题
        title = QLabel(self.process_data.get('title', '未命名流程'))
        title.setFont(QFont("微软雅黑", 11, QFont.Bold))
        title.setStyleSheet("color: #2d3748;")
        title.setWordWrap(True)
        
        # 状态指示器
        status_widget = self.create_status_indicator()
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(status_widget)
        
        parent_layout.addLayout(header_layout)
        
    def create_status_indicator(self):
        """
        创建状态指示器
        
        Returns:
            QWidget: 状态指示器组件
        """
        status_widget = QWidget()
        status_widget.setFixedSize(80, 24)
        
        status_layout = QHBoxLayout()
        status_layout.setContentsMargins(8, 4, 8, 4)
        status_layout.setSpacing(4)
        
        # 状态点
        status_dot = QLabel("●")
        status_dot.setStyleSheet(f"color: {self.status_color}; font-size: 12px;")
        
        # 状态文本
        status_text = QLabel(self.get_status_text())
        status_text.setFont(QFont("微软雅黑", 9))
        status_text.setStyleSheet(f"color: {self.status_color};")
        
        status_layout.addWidget(status_dot)
        status_layout.addWidget(status_text)
        
        status_widget.setLayout(status_layout)
        status_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {self.status_color}20;
                border-radius: 12px;
                border: 1px solid {self.status_color}40;
            }}
        """)
        
        return status_widget
        
    def get_status_text(self):
        """
        获取状态文本
        
        Returns:
            str: 状态文本
        """
        status_map = {
            'running': '运行中',
            'stopped': '已停止',
            'paused': '暂停',
            'idle': '空闲',
            'error': '错误',
            'completed': '完成'
        }
        status = self.process_data.get('status', 'idle')
        return status_map.get(status, '未知')
        
    def create_info(self, parent_layout):
        """
        创建基本信息行
        
        Args:
            parent_layout: 父布局
        """
        info_layout = QHBoxLayout()
        info_layout.setSpacing(15)
        
        # 创建信息项
        info_items = []
        
        # 类型信息
        if 'type' in self.process_data:
            info_items.append(('类型', self.process_data['type']))
            
        # 进度信息
        if 'progress' in self.process_data:
            progress = self.process_data['progress']
            info_items.append(('进度', f"{progress}%"))
            
        # 时间信息
        if 'duration' in self.process_data:
            info_items.append(('耗时', self.process_data['duration']))
        elif 'start_time' in self.process_data:
            info_items.append(('开始', self.process_data['start_time']))
            
        # 显示前两个信息项
        for i, (key, value) in enumerate(info_items[:2]):
            if i > 0:
                # 添加分隔符
                separator = QLabel("•")
                separator.setStyleSheet("color: #cbd5e0; font-size: 10px;")
                info_layout.addWidget(separator)
                
            info_label = QLabel(f"{key}: {value}")
            info_label.setFont(QFont("微软雅黑", 9))
            info_label.setStyleSheet("color: #718096;")
            info_layout.addWidget(info_label)
            
        info_layout.addStretch()
        parent_layout.addLayout(info_layout)
        
    def create_footer(self, parent_layout):
        """
        创建底部操作提示
        
        Args:
            parent_layout: 父布局
        """
        footer_layout = QHBoxLayout()
        
        # 描述信息
        description = self.process_data.get('description', '')
        if description:
            desc_label = QLabel(description)
            desc_label.setFont(QFont("微软雅黑", 8))
            desc_label.setStyleSheet("color: #a0aec0;")
            desc_label.setWordWrap(True)
            footer_layout.addWidget(desc_label)
            
        footer_layout.addStretch()
        
        # 点击提示
        click_hint = QLabel("点击查看详情")
        click_hint.setFont(QFont("微软雅黑", 8))
        click_hint.setStyleSheet("color: #667eea;")
        footer_layout.addWidget(click_hint)
        
        parent_layout.addLayout(footer_layout)
        
    def mousePressEvent(self, event):
        """
        处理鼠标点击事件
        
        Args:
            event: 鼠标事件
        """
        if event.button() == Qt.LeftButton:
            self.card_clicked.emit(self.process_data)
        super().mousePressEvent(event)
        
    def enterEvent(self, event):
        """
        鼠标进入事件
        
        Args:
            event: 事件对象
        """
        self.is_hovered = True
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        """
        鼠标离开事件
        
        Args:
            event: 事件对象
        """
        self.is_hovered = False
        super().leaveEvent(event)


class LeftSidebar(QFrame):
    """
    左侧边栏组件
    
    基于JSON格式显示流程卡片列表
    """
    
    # 定义信号
    process_selected = Signal(dict)  # 流程选择信号
    
    def __init__(self):
        super().__init__()
        self.process_cards = []  # 存储卡片组件
        self.processes_data = []  # 存储流程数据
        self.setup_ui()
        self.load_default_processes()
        
    def setup_ui(self):
        """
        设置左侧边栏界面
        """
        self.setFrameStyle(QFrame.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border-right: 1px solid #e2e8f0;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 标题栏
        self.create_header(layout)
        
        # 流程卡片区域
        self.create_cards_area(layout)
        
        # 底部操作区域
        self.create_footer(layout)
        
        self.setLayout(layout)
        
    def create_header(self, parent_layout):
        """
        创建标题栏
        
        Args:
            parent_layout: 父布局
        """
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background-color: #667eea;
                border: none;
                border-bottom: 1px solid #5a67d8;
            }
        """)
        header.setFixedHeight(50)
        
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(20, 12, 20, 12)
        
        # 标题
        title = QLabel("🔄 流程管理")
        title.setFont(QFont("微软雅黑", 14, QFont.Bold))
        title.setStyleSheet("color: white;")
        
        # 流程数量
        self.count_label = QLabel("0 个流程")
        self.count_label.setFont(QFont("微软雅黑", 10))
        self.count_label.setStyleSheet("color: #e2e8f0;")
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.count_label)
        
        header.setLayout(header_layout)
        parent_layout.addWidget(header)
        
    def create_cards_area(self, parent_layout):
        """
        创建卡片显示区域
        
        Args:
            parent_layout: 父布局
        """
        # 滚动区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #f8fafc;
            }
            QScrollBar:vertical {
                background-color: #f1f5f9;
                width: 6px;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical {
                background-color: #cbd5e0;
                border-radius: 3px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #a0aec0;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # 卡片容器
        self.cards_container = QWidget()
        self.cards_layout = QVBoxLayout()
        self.cards_layout.setContentsMargins(10, 10, 10, 10)
        self.cards_layout.setSpacing(8)
        self.cards_layout.addStretch()  # 添加弹性空间
        
        self.cards_container.setLayout(self.cards_layout)
        self.scroll_area.setWidget(self.cards_container)
        
        parent_layout.addWidget(self.scroll_area)
        
    def create_footer(self, parent_layout):
        """
        创建底部操作区域
        
        Args:
            parent_layout: 父布局
        """
        footer = QFrame()
        footer.setStyleSheet("""
            QFrame {
                background-color: white;
                border-top: 1px solid #e2e8f0;
            }
        """)
        footer.setFixedHeight(60)
        
        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(15, 10, 15, 10)
        footer_layout.setSpacing(10)
        
        # 刷新按钮
        refresh_btn = QPushButton("🔄 刷新")
        refresh_btn.setFont(QFont("微软雅黑", 10))
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #667eea;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #5a67d8;
            }
            QPushButton:pressed {
                background-color: #4c51bf;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_processes)
        
        # 添加流程按钮
        add_btn = QPushButton("➕ 添加")
        add_btn.setFont(QFont("微软雅黑", 10))
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #48bb78;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #38a169;
            }
            QPushButton:pressed {
                background-color: #2f855a;
            }
        """)
        add_btn.clicked.connect(self.add_process)
        
        footer_layout.addWidget(refresh_btn)
        footer_layout.addWidget(add_btn)
        
        footer.setLayout(footer_layout)
        parent_layout.addWidget(footer)
        
    def load_processes_from_json(self, json_data):
        """
        从JSON数据加载流程
        
        Args:
            json_data (str or dict): JSON格式的流程数据
        """
        try:
            if isinstance(json_data, str):
                processes = json.loads(json_data)
            else:
                processes = json_data
                
            if isinstance(processes, dict) and 'processes' in processes:
                processes = processes['processes']
            elif not isinstance(processes, list):
                processes = [processes]
                
            self.processes_data = processes
            self.update_cards()
            
        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {e}")
        except Exception as e:
            print(f"加载流程数据错误: {e}")
            
    def load_default_processes(self):
        """
        加载默认的示例流程数据
        """
        default_processes = [
            {
                "id": "proc_001",
                "title": "示波器自动测试",
                "status": "running",
                "type": "自动化测试",
                "progress": 75,
                "duration": "00:05:23",
                "description": "正在执行信号完整性测试流程",
                "start_time": "14:30:15",
                "details": {
                    "test_type": "signal_integrity",
                    "device": "DSO-X 3024T",
                    "channels": [1, 2, 3]
                }
            },
            {
                "id": "proc_002", 
                "title": "波形数据分析",
                "status": "completed",
                "type": "数据分析",
                "progress": 100,
                "duration": "00:02:45",
                "description": "FFT频域分析已完成",
                "start_time": "14:25:30",
                "details": {
                    "analysis_type": "fft",
                    "sample_rate": "1GSa/s",
                    "data_points": 10000
                }
            },
            {
                "id": "proc_003",
                "title": "设备连接检查", 
                "status": "idle",
                "type": "系统检查",
                "description": "等待执行设备连接状态检查",
                "details": {
                    "check_type": "connectivity",
                    "devices": ["示波器", "信号发生器"]
                }
            },
            {
                "id": "proc_004",
                "title": "报告生成任务",
                "status": "paused",
                "type": "报告生成",
                "progress": 45,
                "duration": "00:01:20",
                "description": "测试报告生成已暂停",
                "start_time": "14:20:10",
                "details": {
                    "report_type": "test_summary",
                    "format": "PDF",
                    "pages": 12
                }
            },
            {
                "id": "proc_005",
                "title": "参数优化流程",
                "status": "error", 
                "type": "参数调优",
                "description": "参数优化过程中出现错误",
                "details": {
                    "error_code": "E001",
                    "error_msg": "设备通信超时"
                }
            }
        ]
        
        self.processes_data = default_processes
        self.update_cards()
        
    def update_cards(self):
        """
        更新卡片显示
        """
        # 清除现有卡片
        self.clear_cards()
        
        # 创建新卡片
        for process_data in self.processes_data:
            card = ProcessCard(process_data)
            card.card_clicked.connect(self.on_card_clicked)
            
            # 插入到布局中（在弹性空间之前）
            self.cards_layout.insertWidget(self.cards_layout.count() - 1, card)
            self.process_cards.append(card)
            
        # 更新计数
        self.count_label.setText(f"{len(self.processes_data)} 个流程")
        
    def clear_cards(self):
        """
        清除所有卡片
        """
        for card in self.process_cards:
            card.deleteLater()
        self.process_cards.clear()
        
    def on_card_clicked(self, process_data):
        """
        处理卡片点击事件
        
        Args:
            process_data (dict): 流程数据
        """
        print(f"选择流程: {process_data.get('title', '未知')}")
        self.process_selected.emit(process_data)
        
    def refresh_processes(self):
        """
        刷新流程列表
        """
        print("刷新流程列表")
        # 这里可以重新加载数据
        self.load_default_processes()
        
    def add_process(self):
        """
        添加新流程
        """
        print("添加新流程")
        # 这里可以打开添加流程的对话框
        
    def get_processes_data(self):
        """
        获取当前流程数据
        
        Returns:
            list: 流程数据列表
        """
        return self.processes_data.copy()
        
    def update_process_status(self, process_id, new_status):
        """
        更新指定流程的状态
        
        Args:
            process_id (str): 流程ID
            new_status (str): 新状态
        """
        for process_data in self.processes_data:
            if process_data.get('id') == process_id:
                process_data['status'] = new_status
                break
                
        # 重新更新卡片显示
        self.update_cards() 