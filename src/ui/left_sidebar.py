"""
左侧边栏组件

提供基于JSON格式的流程卡片显示，支持点击交互
"""

from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QScrollArea, QWidget, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QTimer, Slot
from PySide6.QtGui import QFont, QPainter, QPainterPath
from datetime import datetime
import json

# 导入新的卡片组件
from src.ui.cards import PlanCard, TaskCard
# 导入数据管理器
from src.utils.project_data_manager import get_project_manager


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
            'completed': '#38b2ac',  # 青色 - 完成
            'planning': '#805ad5'    # 紫色 - 计划中
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
            'completed': '完成',
            'planning': '计划中'
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
    
    显示计划卡片列表，使用动态数据管理，支持流程卡片缓冲机制
    """
    
    # 定义信号
    plan_card_clicked = Signal(dict)  # 计划卡片点击信号
    
    def __init__(self):
        super().__init__()
        self.plan_cards = []  # 存储计划卡片组件
        self.project_manager = get_project_manager()  # 获取数据管理器实例
        
        # 流程卡片缓冲区
        self.card_buffer = {
            "current_plan_id": None,  # 当前缓冲的计划ID
            "plan_data": None,        # Level3计划数据
            "task_data": None,        # Level2任务数据
            "temp_plan_counter": 0    # 临时计划计数器
        }
        
        self.setup_ui()
        self.connect_signals()  # 连接信号槽
        self.load_initial_data()  # 加载初始数据
        
    def setup_ui(self):
        """
        设置左侧边栏界面
        """
        self.setFixedWidth(360)  # 增加侧边栏宽度
        self.setFrameStyle(QFrame.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            }
        """)
        
        # 主布局
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 创建头部
        self.create_header(layout)
        
        # 创建卡片滚动区域
        self.create_cards_area(layout)
        
        self.setLayout(layout)
        
    def create_header(self, parent_layout):
        """
        创建头部区域
        
        Args:
            parent_layout: 父布局
        """
        header_frame = QFrame()
        header_frame.setFixedHeight(120)  # 增加高度以容纳按钮
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 0px;
                border-bottom: 1px solid #e2e8f0;
            }
        """)
        
        header_layout = QVBoxLayout()
        header_layout.setContentsMargins(24, 18, 24, 18)
        header_layout.setSpacing(8)
        
        # 标题行
        title_layout = QHBoxLayout()
        
        # 标题
        title = QLabel("测试计划")
        title.setFont(QFont("微软雅黑", 16, QFont.Bold))
        title.setStyleSheet("color: white;")
        
        # 计数标签
        self.count_label = QLabel("0 个计划")
        self.count_label.setFont(QFont("微软雅黑", 10))
        self.count_label.setStyleSheet("color: #e2e8f0;")
        
        title_layout.addWidget(title)
        title_layout.addStretch()
        title_layout.addWidget(self.count_label)
        
        # 模式切换按钮组
        mode_layout = QHBoxLayout()
        mode_layout.setSpacing(8)
        
        # 普通模式按钮
        self.normal_mode_btn = QPushButton("普通")
        self.normal_mode_btn.setFixedSize(60, 28)
        self.normal_mode_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #667eea;
                border: 1px solid #ffffff;
                border-radius: 14px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #f0f4ff;
            }
            QPushButton:pressed {
                background-color: #e0e8ff;
            }
        """)
        self.normal_mode_btn.clicked.connect(self.switch_to_normal_mode)
        
        # JSON模式按钮
        self.json_mode_btn = QPushButton("JSON")
        self.json_mode_btn.setFixedSize(60, 28)
        self.json_mode_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.3);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.5);
                border-radius: 14px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.4);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.2);
            }
        """)
        self.json_mode_btn.clicked.connect(self.switch_to_json_mode)
        
        # QML模式按钮
        self.qml_mode_btn = QPushButton("QML")
        self.qml_mode_btn.setFixedSize(60, 28)
        self.qml_mode_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.3);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.5);
                border-radius: 14px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.4);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.2);
            }
        """)
        self.qml_mode_btn.clicked.connect(self.switch_to_qml_mode)
        
        mode_layout.addWidget(self.normal_mode_btn)
        mode_layout.addWidget(self.json_mode_btn)
        mode_layout.addWidget(self.qml_mode_btn)
        mode_layout.addStretch()
        
        header_layout.addLayout(title_layout)
        header_layout.addLayout(mode_layout)
        
        header_frame.setLayout(header_layout)
        parent_layout.addWidget(header_frame)
        
        # 设置初始模式
        self.current_mode = 'normal'
        self.update_mode_buttons()
        
    def create_cards_area(self, parent_layout):
        """
        创建卡片滚动区域
        
        Args:
            parent_layout: 父布局
        """
        # 创建滚动区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)  # 让内容自适应大小
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setFrameStyle(QFrame.NoFrame)
        
        # 卡片容器
        self.cards_widget = QWidget()
        self.cards_layout = QVBoxLayout()
        self.cards_layout.setContentsMargins(20, 24, 20, 24)  # 保持边距
        self.cards_layout.setSpacing(16)  # 适中的卡片间距
        self.cards_layout.setAlignment(Qt.AlignTop)  # 确保卡片靠顶对齐
        # 移除addStretch，让卡片自然排列
        self.cards_widget.setLayout(self.cards_layout)
        
        self.scroll_area.setWidget(self.cards_widget)
        
        parent_layout.addWidget(self.scroll_area)
        
    def connect_signals(self):
        """
        连接信号槽
        """
        # 连接数据管理器的信号
        self.project_manager.plan_added.connect(self.on_project_added)
        self.project_manager.plan_removed.connect(self.on_project_removed)
        self.project_manager.plan_updated.connect(self.on_project_updated)
        self.project_manager.plans_cleared.connect(self.on_projects_cleared)
        
    def load_initial_data(self):
        """
        加载初始数据（不加载示例数据，只显示缓冲区内容）
        """
        # 只从数据管理器获取现有数据并更新界面（不添加示例数据）
        self.refresh_all_cards()
        
    def refresh_all_cards(self):
        """
        刷新所有卡片显示
        """
        # 清除现有卡片
        self.clear_cards()
        
        # 从数据管理器获取所有项目
        projects = self.project_manager.get_all_projects()
        
        # 创建新的计划卡片
        for project_data in projects:
            plan_card = PlanCard(project_data)
            plan_card.card_clicked.connect(self.on_plan_card_clicked)
            
            self.cards_layout.addWidget(plan_card)
            self.plan_cards.append(plan_card)
            
        # 更新计数
        self.update_count_label()
        
    def clear_cards(self):
        """
        清除所有卡片
        """
        for card in self.plan_cards:
            card.setParent(None)
            card.deleteLater()
        self.plan_cards.clear()
        
    def update_count_label(self):
        """
        更新计划计数标签
        """
        count = self.project_manager.get_project_count()
        self.count_label.setText(f"{count} 个计划")
        
    # 数据管理器信号槽处理方法
    def on_project_added(self, project_data):
        """
        处理项目添加信号
        
        Args:
            project_data (dict): 新添加的项目数据
        """
        print(f"新计划已添加: {project_data.get('project_name', '未知计划')}")
        # 创建新卡片
        plan_card = PlanCard(project_data)
        plan_card.card_clicked.connect(self.on_plan_card_clicked)
        
        self.cards_layout.addWidget(plan_card)
        self.plan_cards.append(plan_card)
        
        # 更新计数
        self.update_count_label()
        
    def on_project_removed(self, project_id):
        """
        处理项目移除信号
        
        Args:
            project_id (str): 被移除的项目ID
        """
        print(f"计划已移除: {project_id}")
        # 找到并移除对应的卡片
        for i, card in enumerate(self.plan_cards):
            if card.project_data.get('project_id') == project_id:
                card.setParent(None)
                card.deleteLater()
                self.plan_cards.pop(i)
                break
                
        # 更新计数
        self.update_count_label()
        
    def on_project_updated(self, project_data):
        """
        处理项目更新信号
        
        Args:
            project_data (dict): 更新后的项目数据
        """
        project_id = project_data.get('project_id')
        print(f"计划已更新: {project_data.get('project_name', '未知计划')} (ID: {project_id})")
        
        # 找到并更新对应的卡片
        for card in self.plan_cards:
            if card.project_data.get('project_id') == project_id:
                # 更新卡片数据并重新创建界面
                card.project_data = project_data
                card.update_display()  # 需要在PlanCard中添加此方法
                break
                
    def on_projects_cleared(self):
        """
        处理项目清空信号
        """
        print("所有计划已清空")
        self.clear_cards()
        self.update_count_label()
        
    def on_plan_card_clicked(self, project_data):
        """
        处理计划卡片点击事件
        
        Args:
            project_data (dict): 项目数据
        """
        print(f"计划卡片被点击: {project_data.get('project_name', '未知计划')}")
        self.plan_card_clicked.emit(project_data)
        
    # 向外提供的API方法（保持兼容性）
    def add_project(self, project_data):
        """
        添加新项目（通过数据管理器）
        
        Args:
            project_data (dict): 项目数据
        """
        return self.project_manager.add_project(project_data)
        
    def remove_project(self, project_id):
        """
        移除项目（通过数据管理器）
        
        Args:
            project_id (str): 项目ID
        """
        return self.project_manager.remove_project(project_id)
        
    def update_project_status(self, project_id, new_status):
        """
        更新项目状态（通过数据管理器）
        
        Args:
            project_id (str): 项目ID
            new_status (str): 新状态
        """
        return self.project_manager.update_project_status(project_id, new_status)
        
    def get_project_manager(self):
        """
        获取数据管理器实例，供外部使用
        
        Returns:
            ProjectDataManager: 数据管理器实例
        """
        return self.project_manager 

    @Slot("PyQt_PyObject")
    def update_plan_buffer(self, plan_data):
        """
        更新Level3计划缓冲区（简化版本）
        
        Args:
            plan_data (dict): Level3计划数据
        """
        try:
            plan_id = plan_data.get('plan_id', 'unknown')
            project_name = plan_data.get('project_name', '未知计划')
            print(f"收到Level3计划更新: {project_name} (ID: {plan_id})")
            
            # 转换为项目格式
            project_data = self.convert_plan_to_project(plan_data)
            project_id = project_data.get('project_id')
            
            # 检查是否已存在相同项目
            existing_project = None
            for project in self.project_manager.get_all_projects():
                if project.get('project_id') == project_id:
                    existing_project = project
                    break
            
            if existing_project:
                # 更新现有项目
                self.project_manager.update_project(project_id, project_data)
                print(f"更新现有Level3计划: {project_name}")
            else:
                # 添加新项目
                self.project_manager.add_project(project_data)
                print(f"添加新Level3计划: {project_name}")
                
        except Exception as e:
            print(f"更新计划缓冲失败: {e}")
    
    @Slot("PyQt_PyObject")
    def update_task_buffer(self, task_data):
        """
        更新Level2任务缓冲区（简化版本）
        
        Args:
            task_data (dict): Level2任务数据
        """
        try:
            plan_id = task_data.get('plan_id', 'unknown')
            task_name = task_data.get('task_name', '未知任务')
            print(f"收到Level2任务更新: {task_name} (计划ID: {plan_id})")
            
            # 查找是否有对应的Level3计划
            project_id = f"plan_{plan_id}"
            existing_project = None
            
            for project in self.project_manager.get_all_projects():
                if project.get('project_id') == project_id:
                    existing_project = project
                    break
            
            if existing_project:
                # 有对应的Level3计划，更新任务状态
                print(f"找到对应计划，更新任务状态")
                self.update_existing_plan_task(existing_project, task_data)
            else:
                # 没有对应的Level3计划，创建临时计划
                print(f"未找到对应计划，创建临时计划")
                self.create_temp_plan_for_task(task_data)
                
        except Exception as e:
            print(f"更新任务缓冲失败: {e}")
    
    def update_existing_plan_task(self, project_data, task_data):
        """
        更新现有计划中的任务状态
        
        Args:
            project_data (dict): 现有项目数据
            task_data (dict): Level2任务数据
        """
        task_name = task_data.get('task_name', '未知任务')
        current_step = task_data.get('current_step', 0)
        total_steps = task_data.get('total_steps', 0)
        status = task_data.get('status', 'running')
        
        # 更新项目状态
        project_data['status'] = status
        project_data['current_task'] = current_step
        
        # 查找并更新对应的任务
        tasks = project_data.get('tasks', [])
        task_found = False
        
        for task in tasks:
            if task.get('task_name') == task_name:
                task['test_description'] = f"当前步骤: {current_step}/{total_steps}"
                task_found = True
                break
        
        if not task_found:
            # 添加新任务
            new_task = {
                "task_name": task_name,
                "signal_type": "未知",
                "priority": "medium",
                "estimated_time": "未知",
                "test_description": f"当前步骤: {current_step}/{total_steps}"
            }
            tasks.append(new_task)
            project_data['total_tasks'] = len(tasks)
        
        # 更新项目管理器
        self.project_manager.update_project(project_data.get('project_id'), project_data)
    
    def create_temp_plan_for_task(self, task_data):
        """
        为Level2任务创建临时Level3计划
        
        Args:
            task_data (dict): Level2任务数据
        """
        self.card_buffer["temp_plan_counter"] += 1
        plan_id = task_data.get('plan_id', 'unknown')
        task_name = task_data.get('task_name', '未知任务')
        
        # 创建临时计划数据
        temp_plan_data = {
                "card_type": "level3",
            "plan_id": plan_id,
            "project_name": f"临时计划_{self.card_buffer['temp_plan_counter']}: {task_name}",
            "total_tasks": 1,
            "current_task": 0,
            "status": task_data.get('status', 'running'),
            "estimated_total_time": "未知",
            "tasks": [{
                "task_name": task_name,
                "task_type": "signal_test",
                "task_description": f"步骤总数: {task_data.get('total_steps', 0)}",
                "execution_status": f"当前步骤: {task_data.get('current_step', 0)}/{task_data.get('total_steps', 0)}",
                "estimated_time": "未知"
            }]
        }
        
        # 更新缓冲区
        self.card_buffer["current_plan_id"] = plan_id
        self.card_buffer["plan_data"] = temp_plan_data
        self.card_buffer["task_data"] = task_data
        
        # 转换为项目格式并添加
        project_data = self.convert_plan_to_project(temp_plan_data)
        self.project_manager.add_project(project_data)
        
        print(f"创建临时计划: {temp_plan_data['project_name']}")
    
    def convert_plan_to_project(self, plan_data):
        """
        将Level3计划数据转换为项目格式
        
        Args:
            plan_data (dict): Level3计划数据
            
        Returns:
            dict: 项目格式数据
        """
        tasks = []
        for task in plan_data.get('tasks', []):
            tasks.append({
                "task_name": task.get('任务名', '未知任务'),
                "signal_type": "未知",  # 可以从任务描述中推断
                "priority": "medium",   # 默认优先级
                "estimated_time": task.get('预估时间', '未知'),
                "test_description": task.get('任务描述', '')
            })
        
        return {
            "card_type": "level3",
            "project_id": f"plan_{plan_data.get('plan_id', 'unknown')}",
            "project_name": plan_data.get('project_name', '未知计划'),
            "project_description": f"基于计划ID {plan_data.get('plan_id')} 的测试计划",
            "status": plan_data.get('status', 'planning'),
                "plan_num": 1,
            "current_task": plan_data.get('current_task', 0),
            "total_tasks": plan_data.get('total_tasks', 0),
            "estimated_total_time": plan_data.get('estimated_total_time', '未知'),
            "tasks": tasks
        }

    @Slot("PyQt_PyObject")
    def load_cards_from_json(self, json_data):
        """
        从JSON数据加载流程卡片
        
        Args:
            json_data: JSON格式的卡片数据
        """
        try:
            # 检查是否有JSON卡片容器
            if not hasattr(self, 'json_card_container'):
                from src.ui.json_card_renderer import JsonCardContainer
                self.json_card_container = JsonCardContainer()
                # 替换原有的卡片区域
                self.cards_layout.addWidget(self.json_card_container)
                # 连接信号
                self.json_card_container.card_selected.connect(self.on_json_card_selected)
                self.json_card_container.action_requested.connect(self.on_json_card_action)
                
            # 加载卡片数据
            self.json_card_container.load_cards_from_json(json_data)
            print(f"JSON卡片已加载: {self.json_card_container.get_card_count()} 个卡片")
            
        except Exception as e:
            print(f"加载JSON卡片失败: {e}")
    
    @Slot("PyQt_PyObject")
    def update_json_card(self, card_id, update_data):
        """
        更新特定的JSON卡片
        
        Args:
            card_id (str): 卡片ID
            update_data (dict): 更新数据
        """
        try:
            if hasattr(self, 'json_card_container'):
                self.json_card_container.update_card(card_id, update_data)
                print(f"JSON卡片已更新: {card_id}")
        except Exception as e:
            print(f"更新JSON卡片失败: {e}")
    
    @Slot(dict)
    def on_json_card_selected(self, card_data):
        """
        处理JSON卡片选择事件
        
        Args:
            card_data (dict): 选中的卡片数据
        """
        print(f"JSON卡片被选择: {card_data.get('title', '未知卡片')}")
        # 发送计划卡片点击信号
        self.plan_card_clicked.emit(card_data)
    
    @Slot(str, dict)
    def on_json_card_action(self, action_name, card_data):
        """
        处理JSON卡片动作事件
        
        Args:
            action_name (str): 动作名称
            card_data (dict): 卡片数据
        """
        print(f"JSON卡片动作: {action_name} - {card_data.get('title', '未知卡片')}")
        # 可以根据动作类型执行不同操作
        if action_name == 'execute':
            # 执行卡片任务
            pass
        elif action_name == 'pause':
            # 暂停任务
            pass
        elif action_name == 'stop':
            # 停止任务
            pass
    
    def convert_level3_to_json_card(self, plan_data):
        """
        将Level3计划数据转换为JSON卡片格式
        
        Args:
            plan_data (dict): Level3计划数据
            
        Returns:
            dict: JSON卡片配置
        """
        plan_id = plan_data.get('plan_id', 'unknown')
        project_name = plan_data.get('project_name', '未知计划')
        status = plan_data.get('status', 'planning')
        total_tasks = plan_data.get('total_tasks', 0)
        current_task = plan_data.get('current_task', 0)
        
        # 构建任务列表
        task_items = []
        for i, task in enumerate(plan_data.get('tasks', [])):
            task_name = task.get('任务名', f'任务{i+1}')
            task_status = '✓' if i < current_task else '○'
            task_items.append({
                'icon': task_status,
                'text': task_name,
                'status': '已完成' if i < current_task else '待执行'
            })
        
        # 进度百分比
        progress = int((current_task / total_tasks * 100)) if total_tasks > 0 else 0
        
        return {
            'id': f'level3_{plan_id}',
            'type': 'level3_plan',
            'content': [
                {
                    'type': 'header',
                    'title': {
                        'text': project_name,
                        'style': {'font_size': 14, 'color': '#2d3748'}
                    },
                    'status': {
                        'value': status,
                        'text': self.get_status_text_zh(status),
                        'id': 'plan_status'
                    },
                    'icon': {'text': '📋', 'size': 16}
                },
                {
                    'type': 'info_grid',
                    'columns': 2,
                    'items': [
                        {'label': '计划ID', 'value': plan_id, 'id': 'plan_id'},
                        {'label': '总任务数', 'value': f'{total_tasks}个', 'id': 'total_tasks'},
                        {'label': '当前进度', 'value': f'{current_task}/{total_tasks}', 'id': 'current_progress'},
                        {'label': '预计时间', 'value': plan_data.get('estimated_total_time', '未知'), 'id': 'estimated_time'}
                    ],
                    'style': {
                        'background': '#f8fafc',
                        'border': '1px solid #e2e8f0',
                        'border_radius': 8,
                        'padding': 12
                    }
                },
                {
                    'type': 'progress',
                    'text': f'完成进度: {progress}%',
                    'value': progress,
                    'max': 100,
                    'color': '#3b82f6',
                    'id': 'progress_bar'
                },
                {
                    'type': 'expandable',
                    'id': 'task_details',
                    'toggle_text': '▼ 展开任务列表',
                    'collapse_text': '▲ 收起任务列表',
                    'content': [
                        {
                            'type': 'custom_list',
                            'title': '任务详情',
                            'items': task_items
                    }
                ]
            },
            {
                    'type': 'actions',
                    'align': 'right',
                    'buttons': [
                        {
                            'text': '查看详情',
                            'type': 'primary',
                            'action': 'view_details'
                        }
                    ]
                }
            ],
            'style': {
                'width': 'auto',
                'min_size': {'width': 280},
                'background': '#ffffff',
                'border': '2px solid #e2e8f0',
                'border_radius': 12,
                'margin': '8px 4px',
                'hover': {
                    'border': '2px solid #667eea',
                    'background': '#f7fafc'
                }
            },
            'behaviors': {
                'clickable': True,
                'hoverable': True
            }
        }
    
    def convert_level2_to_json_card(self, task_data):
        """
        将Level2任务数据转换为JSON卡片格式
        
        Args:
            task_data (dict): Level2任务数据
            
        Returns:
            dict: JSON卡片配置
        """
        plan_id = task_data.get('plan_id', 'unknown')
        task_name = task_data.get('task_name', '未知任务')
        status = task_data.get('status', 'running')
        current_step = task_data.get('current_step', 0)
        total_steps = task_data.get('total_steps', 0)
        
        # 进度百分比
        progress = int((current_step / total_steps * 100)) if total_steps > 0 else 0
        
        return {
            'id': f'level2_{plan_id}',
            'type': 'level2_task',
            'content': [
                {
                    'type': 'header',
                    'title': {
                        'text': task_name,
                        'style': {'font_size': 13, 'color': '#2d3748'}
                    },
                    'status': {
                        'value': status,
                        'text': self.get_status_text_zh(status),
                        'id': 'task_status'
                    },
                    'icon': {'text': '⚡', 'size': 16}
                },
                {
                    'type': 'info_grid',
                    'columns': 2,
                    'items': [
                        {'label': '计划ID', 'value': plan_id, 'id': 'task_plan_id'},
                        {'label': '当前步骤', 'value': f'{current_step}/{total_steps}', 'id': 'step_progress'}
                    ],
                    'style': {
                        'background': '#fef5e7',
                        'border': '1px solid #f7c948',
                        'border_radius': 8,
                        'padding': 12
                    }
                },
                {
                    'type': 'progress',
                    'text': f'执行进度: {progress}%',
                    'value': progress,
                    'max': 100,
                    'color': '#f59e0b',
                    'id': 'task_progress_bar'
                },
                {
                    'type': 'text',
                    'id': 'task_description',
                    'content': f'正在执行第 {current_step} 步，共 {total_steps} 步',
                    'style': {'font_size': 10, 'color': '#6b7280'},
                    'word_wrap': True
                },
                {
                    'type': 'actions',
                    'align': 'right',
                    'buttons': [
                        {
                            'text': '查看执行',
                            'type': 'secondary',
                            'action': 'view_execution'
                        }
                    ]
                }
            ],
            'style': {
                'width': 'auto',
                'min_size': {'width': 280},
                'background': '#fffbeb',
                'border': '2px solid #f59e0b',
                'border_radius': 12,
                'margin': '8px 4px',
                'hover': {
                    'border': '2px solid #d97706',
                    'background': '#fef3c7'
                }
            },
            'behaviors': {
                'clickable': True,
                'hoverable': True
            }
        }
    
    def get_status_text_zh(self, status):
        """
        获取状态的中文文本
        
        Args:
            status (str): 英文状态
            
        Returns:
            str: 中文状态文本
        """
        status_map = {
            'running': '运行中',
            'completed': '已完成',
            'planning': '计划中',
            'paused': '已暂停',
            'error': '错误',
            'stopped': '已停止',
            'idle': '空闲'
        }
        return status_map.get(status, status)
    
    @Slot("PyQt_PyObject")
    def update_plan_buffer_json(self, plan_data):
        """
        使用JSON卡片更新Level3计划缓冲区
        
        Args:
            plan_data (dict): Level3计划数据
        """
        try:
            print(f"收到Level3计划(JSON模式): {plan_data.get('project_name', '未知计划')}")
            
            # 转换为JSON卡片格式
            json_card_config = self.convert_level3_to_json_card(plan_data)
            
            # 创建包含单个卡片的数据
            json_data = {
                'cards': [json_card_config]
            }
            
            # 加载到JSON卡片容器
            self.load_cards_from_json(json_data)
            
        except Exception as e:
            print(f"JSON模式更新计划缓冲失败: {e}")
    
    @Slot("PyQt_PyObject")
    def update_task_buffer_json(self, task_data):
        """
        使用JSON卡片更新Level2任务缓冲区
        
        Args:
            task_data (dict): Level2任务数据
        """
        try:
            print(f"收到Level2任务(JSON模式): {task_data.get('task_name', '未知任务')}")
            
            # 转换为JSON卡片格式
            json_card_config = self.convert_level2_to_json_card(task_data)
            
            # 检查是否已有对应的Level3计划卡片
            plan_id = task_data.get('plan_id', 'unknown')
            level3_card_id = f'level3_{plan_id}'
            
            if hasattr(self, 'json_card_container') and level3_card_id in self.json_card_container.cards:
                # 更新对应的Level3卡片
                update_data = {
                    'updates': {
                        'task_status': {'text': self.get_status_text_zh(task_data.get('status', 'running'))},
                        'current_progress': {'value': f"{task_data.get('current_step', 0)}/{task_data.get('total_steps', 0)}"},
                        'progress_bar': {'value': int((task_data.get('current_step', 0) / task_data.get('total_steps', 1) * 100))}
                    }
                }
                self.update_json_card(level3_card_id, update_data)
            else:
                # 创建新的Level2任务卡片
                json_data = {
                    'cards': [json_card_config]
                }
                self.load_cards_from_json(json_data)
                
        except Exception as e:
            print(f"JSON模式更新任务缓冲失败: {e}")
    
    def switch_to_json_mode(self):
        """
        切换到JSON卡片模式
        """
        try:
            # 隐藏原有的卡片区域
            if hasattr(self, 'scroll_area'):
                self.scroll_area.hide()
            
            # 隐藏QML卡片容器
            if hasattr(self, 'qml_card_container'):
                self.qml_card_container.hide()
            
            # 创建JSON卡片容器
            if not hasattr(self, 'json_card_container'):
                from src.ui.json_card_renderer import JsonCardContainer
                self.json_card_container = JsonCardContainer()
                self.cards_layout.addWidget(self.json_card_container)
                # 连接信号
                self.json_card_container.card_selected.connect(self.on_json_card_selected)
                self.json_card_container.action_requested.connect(self.on_json_card_action)
            else:
                self.json_card_container.show()
                
            # 更新模式状态
            self.current_mode = 'json'
            self.update_mode_buttons()
            print("已切换到JSON卡片模式")
            
        except Exception as e:
            print(f"切换到JSON模式失败: {e}")

    def switch_to_normal_mode(self):
        """
        切换到普通卡片模式
        """
        try:
            # 隐藏JSON卡片容器
            if hasattr(self, 'json_card_container'):
                self.json_card_container.hide()
            
            # 隐藏QML卡片容器
            if hasattr(self, 'qml_card_container'):
                self.qml_card_container.hide()
            
            # 显示原有的卡片区域
            if hasattr(self, 'scroll_area'):
                self.scroll_area.show()
                
            # 更新模式状态
            self.current_mode = 'normal'
            self.update_mode_buttons()
            print("已切换到普通卡片模式")
            
        except Exception as e:
            print(f"切换到普通模式失败: {e}")

    def switch_to_qml_mode(self):
        """
        切换到QML卡片模式
        """
        try:
            # 隐藏原有的卡片区域
            if hasattr(self, 'scroll_area'):
                self.scroll_area.hide()
            
            # 隐藏JSON卡片容器
            if hasattr(self, 'json_card_container'):
                self.json_card_container.hide()
            
            # 创建QML卡片容器
            if not hasattr(self, 'qml_card_container'):
                self.create_qml_card_container()
            else:
                self.qml_card_container.show()
            
            # 更新模式状态
            self.current_mode = 'qml'
            self.update_mode_buttons()
            print("已切换到QML卡片模式")
            
        except Exception as e:
            print(f"切换到QML模式失败: {e}")

    def create_qml_card_container(self):
        """
        创建QML卡片容器
        """
        try:
            from PySide6.QtQuickWidgets import QQuickWidget
            from PySide6.QtQml import qmlRegisterType
            from src.ui.qml_card_system import CardSystemBridge
            
            # 注册QML类型
            qmlRegisterType(CardSystemBridge, "CardSystem", 1, 0, "CardSystemBridge")
            
            # 创建QML Widget
            self.qml_card_container = QQuickWidget()
            self.qml_card_container.setResizeMode(QQuickWidget.SizeRootObjectToView)
            
            # 创建桥接对象
            self.qml_bridge = CardSystemBridge()
            
            # 设置QML上下文属性
            self.qml_card_container.rootContext().setContextProperty("cardBridge", self.qml_bridge)
            
            # 设置QML源文件路径
            from pathlib import Path
            qml_file = Path(__file__).parent / "qml" / "CardContainer.qml"
            self.qml_card_container.setSource(f"file:///{qml_file}")
            
            # 连接信号
            self.qml_bridge.cardAdded.connect(self.on_qml_card_added)
            self.qml_bridge.cardUpdated.connect(self.on_qml_card_updated)
            self.qml_bridge.cardRemoved.connect(self.on_qml_card_removed)
            self.qml_bridge.systemCleared.connect(self.on_qml_system_cleared)
            
            # 添加到布局
            self.cards_layout.addWidget(self.qml_card_container)
            
            print("QML卡片容器创建成功")
            
        except Exception as e:
            print(f"创建QML卡片容器失败: {e}")
            import traceback
            traceback.print_exc()

    def on_qml_card_added(self, card_data_str):
        """
        处理QML卡片添加事件
        
        Args:
            card_data_str (str): JSON格式的卡片数据
        """
        try:
            import json
            card_data = json.loads(card_data_str)
            print(f"QML卡片已添加: {card_data.get('id', '未知ID')}")
        except Exception as e:
            print(f"处理QML卡片添加失败: {e}")

    def on_qml_card_updated(self, card_data_str):
        """
        处理QML卡片更新事件
        
        Args:
            card_data_str (str): JSON格式的卡片数据
        """
        try:
            import json
            card_data = json.loads(card_data_str)
            print(f"QML卡片已更新: {card_data.get('id', '未知ID')}")
        except Exception as e:
            print(f"处理QML卡片更新失败: {e}")

    def on_qml_card_removed(self, card_id):
        """
        处理QML卡片移除事件
        
        Args:
            card_id (str): 卡片ID
        """
        print(f"QML卡片已移除: {card_id}")

    def on_qml_system_cleared(self):
        """
        处理QML系统清空事件
        """
        print("QML卡片系统已清空")

    @Slot("PyQt_PyObject")
    def update_plan_buffer_qml(self, plan_data):
        """
        使用QML卡片更新Level3计划缓冲区
        
        Args:
            plan_data (dict): Level3计划数据
        """
        try:
            print(f"收到Level3计划(QML模式): {plan_data.get('project_name', '未知计划')}")
            
            # 确保QML容器已创建
            if not hasattr(self, 'qml_card_container'):
                self.create_qml_card_container()
            
            # 转换为QML卡片格式
            qml_card_data = self.convert_level3_to_qml_card(plan_data)
            
            # 发送数据到QML
            import json
            card_data_str = json.dumps(qml_card_data, ensure_ascii=False)
            
            if hasattr(self, 'qml_bridge'):
                # 通过桥接对象添加卡片
                self.qml_bridge.addLevel3Plan()
                print("Level3计划已发送到QML系统")
            
        except Exception as e:
            print(f"QML模式更新计划缓冲失败: {e}")
            import traceback
            traceback.print_exc()

    @Slot("PyQt_PyObject")  
    def update_task_buffer_qml(self, task_data):
        """
        使用QML卡片更新Level2任务缓冲区
        
        Args:
            task_data (dict): Level2任务数据
        """
        try:
            print(f"收到Level2任务(QML模式): {task_data.get('task_name', '未知任务')}")
            
            # 确保QML容器已创建
            if not hasattr(self, 'qml_card_container'):
                self.create_qml_card_container()
            
            # 转换为QML卡片格式
            qml_card_data = self.convert_level2_to_qml_card(task_data)
            
            # 发送数据到QML
            import json
            card_data_str = json.dumps(qml_card_data, ensure_ascii=False)
            
            if hasattr(self, 'qml_bridge'):
                # 通过桥接对象添加任务
                plan_id = task_data.get('plan_id', 'unknown')
                self.qml_bridge.addLevel2Task(plan_id)
                print("Level2任务已发送到QML系统")
            
        except Exception as e:
            print(f"QML模式更新任务缓冲失败: {e}")
            import traceback
            traceback.print_exc()

    def convert_level3_to_qml_card(self, plan_data):
        """
        将Level3计划数据转换为QML卡片格式
        
        Args:
            plan_data (dict): Level3计划数据
            
        Returns:
            dict: QML卡片数据
        """
        plan_id = plan_data.get('plan_id', 'unknown')
        project_name = plan_data.get('project_name', '未知计划')
        status = plan_data.get('status', 'planning')
        total_tasks = plan_data.get('total_tasks', 0)
        current_task = plan_data.get('current_task', 0)
        
        # 进度百分比
        progress = int((current_task / total_tasks * 100)) if total_tasks > 0 else 0
        
        return {
            'id': f'level3_{plan_id}',
            'type': 'level3',
            'Json A样式': {
                '计划计数': 0,
                '计划名称': project_name,
                '任务总数': total_tasks,
                '计划状态': status,
                '当前任务': current_task,
                '进度百分比': progress,
                '预计总时间': plan_data.get('estimated_total_time', '未知'),
                '开始时间': plan_data.get('start_time', ''),
                '任务列表': plan_data.get('tasks', [])
            }
        }

    def convert_level2_to_qml_card(self, task_data):
        """
        将Level2任务数据转换为QML卡片格式
        
        Args:
            task_data (dict): Level2任务数据
            
        Returns:
            dict: QML卡片数据
        """
        plan_id = task_data.get('plan_id', 'unknown')
        task_name = task_data.get('task_name', '未知任务')
        status = task_data.get('status', 'running')
        current_step = task_data.get('current_step', 0)
        total_steps = task_data.get('total_steps', 0)
        
        # 进度百分比
        progress = int((current_step / total_steps * 100)) if total_steps > 0 else 0
        
        return {
            'id': f'level2_{plan_id}',
            'type': 'level2',
            'Json B样式': {
                '计划计数': 0,
                '任务名': task_name,
                '步骤总数': total_steps,
                '当前步骤': current_step,
                '任务状态': status,
                '进度百分比': progress,
                '每个步骤具体内容': task_data.get('steps', []),
                '最终结果': task_data.get('result', '')
            }
        }

    def get_qml_bridge(self):
        """
        获取QML桥接对象
        
        Returns:
            CardSystemBridge: QML桥接对象，如果不存在则返回None
        """
        return getattr(self, 'qml_bridge', None)

    def add_level3_plan_to_qml(self, plan_data):
        """
        向QML系统添加Level3计划
        
        Args:
            plan_data (dict): Level3计划数据
        """
        try:
            if hasattr(self, 'qml_bridge'):
                self.qml_bridge.addLevel3Plan()
                print(f"Level3计划已添加到QML: {plan_data.get('project_name', '未知计划')}")
            else:
                print("QML桥接对象不存在，无法添加计划")
        except Exception as e:
            print(f"添加Level3计划到QML失败: {e}")

    def add_level2_task_to_qml(self, task_data):
        """
        向QML系统添加Level2任务
        
        Args:
            task_data (dict): Level2任务数据
        """
        try:
            if hasattr(self, 'qml_bridge'):
                plan_id = task_data.get('plan_id', 'unknown')
                self.qml_bridge.addLevel2Task(plan_id)
                print(f"Level2任务已添加到QML: {task_data.get('task_name', '未知任务')}")
            else:
                print("QML桥接对象不存在，无法添加任务")
        except Exception as e:
            print(f"添加Level2任务到QML失败: {e}")

    def clear_qml_cards(self):
        """
        清空QML卡片系统
        """
        try:
            if hasattr(self, 'qml_bridge'):
                self.qml_bridge.clearAllCards()
                print("QML卡片系统已清空")
            else:
                print("QML桥接对象不存在，无法清空")
        except Exception as e:
            print(f"清空QML卡片失败: {e}")

    def execute_qml_card(self, card_id=None):
        """
        执行QML卡片任务
        
        Args:
            card_id (str, optional): 卡片ID，如果为None则执行当前任务
        """
        try:
            if hasattr(self, 'qml_bridge'):
                self.qml_bridge.executeCard()
                print(f"QML卡片任务已执行: {card_id or '当前任务'}")
            else:
                print("QML桥接对象不存在，无法执行任务")
        except Exception as e:
            print(f"执行QML卡片任务失败: {e}")

    def update_mode_buttons(self):
        """
        更新模式按钮的状态
        """
        self.normal_mode_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #667eea;
                border: 1px solid #ffffff;
                border-radius: 14px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #f0f4ff;
            }
            QPushButton:pressed {
                background-color: #e0e8ff;
            }
        """)
        self.json_mode_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.3);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.5);
                border-radius: 14px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.4);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.2);
            }
        """)
        self.qml_mode_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.3);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.5);
                border-radius: 14px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.4);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.2);
            }
        """)

        if self.current_mode == 'normal':
            self.normal_mode_btn.setStyleSheet("""
                QPushButton {
                    background-color: #ffffff;
                    color: #667eea;
                    border: 1px solid #ffffff;
                    border-radius: 14px;
                    font-size: 11px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #f0f4ff;
                }
                QPushButton:pressed {
                    background-color: #e0e8ff;
                }
            """)
        elif self.current_mode == 'json':
            self.json_mode_btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(255, 255, 255, 0.3);
                    color: white;
                    border: 1px solid rgba(255, 255, 255, 0.5);
                    border-radius: 14px;
                    font-size: 11px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.4);
                }
                QPushButton:pressed {
                    background-color: rgba(255, 255, 255, 0.2);
                }
            """)
        elif self.current_mode == 'qml':
            self.qml_mode_btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(255, 255, 255, 0.3);
                    color: white;
                    border: 1px solid rgba(255, 255, 255, 0.5);
                    border-radius: 14px;
                    font-size: 11px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.4);
                }
                QPushButton:pressed {
                    background-color: rgba(255, 255, 255, 0.2);
                }
            """) 