"""
工作区域组件

主要的工作内容显示区域，可以显示示波器数据、AI控制界面、流程详情等
"""

from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, 
    QWidget, QGridLayout, QPushButton
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
import json


class ProcessDetailWidget(QWidget):
    """
    流程详情显示组件
    """
    
    # 定义信号
    action_requested = Signal(str, dict)  # 操作请求信号
    
    def __init__(self, process_data):
        super().__init__()
        self.process_data = process_data
        self.setup_ui()
        
    def setup_ui(self):
        """
        设置流程详情界面
        """
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        
        # 流程标题区域
        self.create_header(layout)
        
        # 流程信息区域
        self.create_info_section(layout)
        
        # 流程详细信息
        self.create_details_section(layout)
        
        # 操作按钮区域
        self.create_actions_section(layout)
        
        self.setLayout(layout)
        
    def create_header(self, parent_layout):
        """
        创建标题区域
        
        Args:
            parent_layout: 父布局
        """
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #667eea;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(20, 15, 20, 15)
        
        # 流程标题
        title = QLabel(self.process_data.get('title', '未命名流程'))
        title.setFont(QFont("微软雅黑", 18, QFont.Bold))
        title.setStyleSheet("color: white;")
        
        # 状态指示器
        status_widget = self.create_status_badge()
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(status_widget)
        
        header_frame.setLayout(header_layout)
        parent_layout.addWidget(header_frame)
        
    def create_status_badge(self):
        """
        创建状态徽章
        
        Returns:
            QWidget: 状态徽章组件
        """
        status = self.process_data.get('status', 'idle')
        status_colors = {
            'running': '#48bb78',
            'stopped': '#f56565', 
            'paused': '#ed8936',
            'idle': '#a0aec0',
            'error': '#e53e3e',
            'completed': '#38b2ac'
        }
        
        status_texts = {
            'running': '运行中',
            'stopped': '已停止',
            'paused': '暂停',
            'idle': '空闲',
            'error': '错误',
            'completed': '完成'
        }
        
        color = status_colors.get(status, '#a0aec0')
        text = status_texts.get(status, '未知')
        
        badge = QLabel(f"● {text}")
        badge.setFont(QFont("微软雅黑", 12, QFont.Bold))
        badge.setStyleSheet(f"""
            QLabel {{
                background-color: {color};
                color: white;
                padding: 8px 16px;
                border-radius: 20px;
                font-size: 12px;
            }}
        """)
        
        return badge
        
    def create_info_section(self, parent_layout):
        """
        创建信息区域
        
        Args:
            parent_layout: 父布局
        """
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        
        info_layout = QGridLayout()
        info_layout.setSpacing(15)
        
        # 基本信息项
        info_items = [
            ("流程ID", self.process_data.get('id', 'N/A')),
            ("类型", self.process_data.get('type', 'N/A')),
            ("状态", self.get_status_text()),
            ("进度", f"{self.process_data.get('progress', 0)}%" if 'progress' in self.process_data else 'N/A'),
            ("开始时间", self.process_data.get('start_time', 'N/A')),
            ("耗时", self.process_data.get('duration', 'N/A')),
        ]
        
        row = 0
        col = 0
        for label_text, value_text in info_items:
            # 标签
            label = QLabel(f"{label_text}:")
            label.setFont(QFont("微软雅黑", 10, QFont.Bold))
            label.setStyleSheet("color: #4a5568;")
            
            # 值
            value = QLabel(str(value_text))
            value.setFont(QFont("微软雅黑", 10))
            value.setStyleSheet("color: #2d3748;")
            
            info_layout.addWidget(label, row, col * 2)
            info_layout.addWidget(value, row, col * 2 + 1)
            
            col += 1
            if col >= 2:  # 每行显示2组信息
                col = 0
                row += 1
                
        info_frame.setLayout(info_layout)
        parent_layout.addWidget(info_frame)
        
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
        
    def create_details_section(self, parent_layout):
        """
        创建详细信息区域
        
        Args:
            parent_layout: 父布局
        """
        details_frame = QFrame()
        details_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        
        details_layout = QVBoxLayout()
        
        # 描述信息
        description = self.process_data.get('description', '')
        if description:
            desc_label = QLabel("描述:")
            desc_label.setFont(QFont("微软雅黑", 12, QFont.Bold))
            desc_label.setStyleSheet("color: #2d3748; margin-bottom: 5px;")
            
            desc_content = QLabel(description)
            desc_content.setFont(QFont("微软雅黑", 11))
            desc_content.setStyleSheet("color: #4a5568; padding: 10px; background-color: #f7fafc; border-radius: 6px;")
            desc_content.setWordWrap(True)
            
            details_layout.addWidget(desc_label)
            details_layout.addWidget(desc_content)
            details_layout.addSpacing(15)
            
        # 详细配置信息
        details = self.process_data.get('details', {})
        if details:
            config_label = QLabel("详细配置:")
            config_label.setFont(QFont("微软雅黑", 12, QFont.Bold))
            config_label.setStyleSheet("color: #2d3748; margin-bottom: 5px;")
            
            # 格式化JSON显示
            config_text = json.dumps(details, indent=2, ensure_ascii=False)
            config_content = QLabel(config_text)
            config_content.setFont(QFont("Consolas", 10))
            config_content.setStyleSheet("""
                QLabel {
                    color: #2d3748;
                    background-color: #f1f5f9;
                    padding: 15px;
                    border-radius: 6px;
                    border: 1px solid #e2e8f0;
                }
            """)
            config_content.setWordWrap(True)
            config_content.setTextInteractionFlags(Qt.TextSelectableByMouse)
            
            details_layout.addWidget(config_label)
            details_layout.addWidget(config_content)
            
        details_frame.setLayout(details_layout)
        parent_layout.addWidget(details_frame)
        
    def create_actions_section(self, parent_layout):
        """
        创建操作按钮区域
        
        Args:
            parent_layout: 父布局
        """
        actions_frame = QFrame()
        actions_frame.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(10)
        
        # 根据状态显示不同的操作按钮
        status = self.process_data.get('status', 'idle')
        
        if status == 'running':
            # 运行中：暂停、停止
            pause_btn = self.create_action_button("⏸️ 暂停", "pause", "#ed8936")
            stop_btn = self.create_action_button("⏹️ 停止", "stop", "#f56565")
            actions_layout.addWidget(pause_btn)
            actions_layout.addWidget(stop_btn)
            
        elif status == 'paused':
            # 暂停：继续、停止
            resume_btn = self.create_action_button("▶️ 继续", "resume", "#48bb78")
            stop_btn = self.create_action_button("⏹️ 停止", "stop", "#f56565")
            actions_layout.addWidget(resume_btn)
            actions_layout.addWidget(stop_btn)
            
        elif status in ['idle', 'stopped', 'error']:
            # 空闲/停止/错误：启动
            start_btn = self.create_action_button("▶️ 启动", "start", "#48bb78")
            actions_layout.addWidget(start_btn)
            
        elif status == 'completed':
            # 完成：重新运行
            restart_btn = self.create_action_button("🔄 重新运行", "restart", "#667eea")
            actions_layout.addWidget(restart_btn)
            
        # 通用操作按钮
        actions_layout.addStretch()
        edit_btn = self.create_action_button("✏️ 编辑", "edit", "#667eea")
        delete_btn = self.create_action_button("🗑️ 删除", "delete", "#e53e3e")
        
        actions_layout.addWidget(edit_btn)
        actions_layout.addWidget(delete_btn)
        
        actions_frame.setLayout(actions_layout)
        parent_layout.addWidget(actions_frame)
        
    def create_action_button(self, text, action, color):
        """
        创建操作按钮
        
        Args:
            text (str): 按钮文本
            action (str): 操作类型
            color (str): 按钮颜色
            
        Returns:
            QPushButton: 操作按钮
        """
        button = QPushButton(text)
        button.setFont(QFont("微软雅黑", 10))
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {color}dd;
            }}
            QPushButton:pressed {{
                background-color: {color}bb;
            }}
        """)
        
        # 连接点击事件
        button.clicked.connect(lambda: self.action_requested.emit(action, self.process_data))
        
        return button


class WorkArea(QFrame):
    """
    中间工作区组件
    
    主要的工作内容显示区域
    """
    
    # 定义信号
    process_action_requested = Signal(str, dict)  # 流程操作请求信号
    
    def __init__(self):
        super().__init__()
        self.current_content = None
        self.setup_ui()
        
    def setup_ui(self):
        """
        设置工作区界面
        """
        self.setFrameStyle(QFrame.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            }
        """)
        
        # 创建滚动区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: white;
            }
            QScrollBar:vertical {
                background-color: #f1f5f9;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: #cbd5e0;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #a0aec0;
            }
        """)
        
        # 默认内容
        self.show_default_content()
        
        # 设置布局
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.scroll_area)
        self.setLayout(layout)
        
    def show_default_content(self):
        """
        显示默认内容
        """
        default_widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 工作区标题
        title = QLabel("工作区域")
        title.setFont(QFont("微软雅黑", 16, QFont.Bold))
        title.setStyleSheet("""
            QLabel {
                color: #2d3748;
                padding: 15px;
                background-color: #f8fafc;
                border-radius: 8px;
                border: 1px solid #e2e8f0;
            }
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # 内容区域
        content_area = QLabel("这里是主要的工作内容区域\n\n可以显示:\n• 流程详情和控制\n• AI控制界面\n• 示波器数据\n• 插件内容\n• 设备状态等\n\n点击左侧流程卡片查看详情")
        content_area.setFont(QFont("微软雅黑", 12))
        content_area.setStyleSheet("""
            QLabel {
                color: #718096;
                background-color: #f7fafc;
                padding: 30px;
                border-radius: 8px;
                border: 2px dashed #e2e8f0;
                line-height: 1.6;
            }
        """)
        content_area.setAlignment(Qt.AlignCenter)
        layout.addWidget(content_area)
        
        default_widget.setLayout(layout)
        self.scroll_area.setWidget(default_widget)
        self.current_content = default_widget
        
    def show_process_details(self, process_data):
        """
        显示流程详情
        
        Args:
            process_data (dict): 流程数据
        """
        # 创建流程详情组件
        detail_widget = ProcessDetailWidget(process_data)
        detail_widget.action_requested.connect(self.on_process_action)
        
        # 设置到滚动区域
        self.scroll_area.setWidget(detail_widget)
        self.current_content = detail_widget
        
    def on_process_action(self, action, process_data):
        """
        处理流程操作请求
        
        Args:
            action (str): 操作类型
            process_data (dict): 流程数据
        """
        print(f"流程操作: {action}, 流程: {process_data.get('title', '未知')}")
        self.process_action_requested.emit(action, process_data)
        
    def set_content(self, widget):
        """
        设置工作区内容
        
        Args:
            widget: 要显示的组件
        """
        self.scroll_area.setWidget(widget)
        self.current_content = widget
        
    def clear_content(self):
        """
        清空工作区内容
        """
        self.show_default_content() 