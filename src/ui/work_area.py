"""
工作区域组件

主要的工作内容显示区域，可以显示示波器数据、AI控制界面、流程详情等
支持显示任务卡片网格布局
"""

from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, 
    QWidget, QGridLayout, QPushButton
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
import json

# 导入新的卡片组件
from src.ui.cards import TaskCard


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


class TaskCardsContainer(QWidget):
    """
    任务卡片容器组件
    
    在工作区显示多个任务卡片的网格布局
    """
    
    card_clicked = Signal(dict)  # 卡片点击信号
    
    def __init__(self, plan_project_data):
        super().__init__()
        self.plan_project_data = plan_project_data
        self.task_cards = []
        self.setup_ui()
        
    def setup_ui(self):
        """
        设置任务卡片容器界面
        """
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # 创建项目头部信息
        self.create_project_header(layout)
        
        # 创建任务卡片网格区域
        self.create_cards_grid(layout)
        
        self.setLayout(layout)
        
    def create_project_header(self, parent_layout):
        """创建项目头部信息"""
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 16px;
                padding: 20px;
            }
        """)
        
        header_layout = QVBoxLayout()
        header_layout.setContentsMargins(20, 16, 20, 16)
        header_layout.setSpacing(8)
        
        # 项目标题行
        title_layout = QHBoxLayout()
        title_layout.setSpacing(12)
        
        # 项目图标和标题
        icon_label = QLabel("🎯")
        icon_label.setFont(QFont("微软雅黑", 20))
        icon_label.setStyleSheet("color: white;")
        
        project_name = self.plan_project_data.get('project_name', '未命名项目')
        title_label = QLabel(project_name)
        title_label.setFont(QFont("微软雅黑", 18, QFont.Bold))
        title_label.setStyleSheet("color: white;")
        
        # 状态信息
        status = self.plan_project_data.get('status', 'planning')
        status_text = {
            'planning': '计划中', 'running': '执行中',
            'completed': '已完成', 'error': '错误'
        }.get(status, '未知')
        
        status_label = QLabel(f"状态: {status_text}")
        status_label.setFont(QFont("微软雅黑", 12))
        status_label.setStyleSheet("color: #e2e8f0;")
        
        title_layout.addWidget(icon_label)
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        title_layout.addWidget(status_label)
        
        # 项目描述
        description = self.plan_project_data.get('project_description', '')
        if description:
            desc_label = QLabel(description)
            desc_label.setFont(QFont("微软雅黑", 11))
            desc_label.setStyleSheet("color: #f7fafc;")
            desc_label.setWordWrap(True)
        else:
            desc_label = QLabel("点击下方任务卡片查看具体的信号测试流程")
            desc_label.setFont(QFont("微软雅黑", 11))
            desc_label.setStyleSheet("color: #cbd5e0;")
        
        # 任务统计
        total_tasks = len(self.plan_project_data.get('tasks', []))
        current_task = self.plan_project_data.get('current_task', 0)
        stats_label = QLabel(f"📊 总任务: {total_tasks} | 当前进度: {current_task}/{total_tasks}")
        stats_label.setFont(QFont("微软雅黑", 10))
        stats_label.setStyleSheet("color: #e2e8f0;")
        
        header_layout.addLayout(title_layout)
        header_layout.addWidget(desc_label)
        header_layout.addWidget(stats_label)
        
        header_frame.setLayout(header_layout)
        parent_layout.addWidget(header_frame)
        
    def create_cards_grid(self, parent_layout):
        """
        创建任务卡片网格
        
        Args:
            parent_layout: 父布局
        """
        grid_container = QFrame()
        grid_container.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            }
        """)
        
        grid_layout = QGridLayout()
        grid_layout.setSpacing(15)
        grid_layout.setContentsMargins(20, 20, 20, 20)
        
        # 获取任务列表
        tasks = self.plan_project_data.get('tasks', [])
        if not tasks:
            # 如果没有任务，显示提示信息
            no_tasks_label = QLabel("暂无任务")
            no_tasks_label.setAlignment(Qt.AlignCenter)
            no_tasks_label.setFont(QFont("微软雅黑", 14))
            no_tasks_label.setStyleSheet("color: #718096; padding: 40px;")
            grid_layout.addWidget(no_tasks_label, 0, 0)
        else:
            # 创建任务卡片
            row = 0
            col = 0
            max_cols = 2  # 每行最多2个卡片
            
            for task_index, task in enumerate(tasks):
                # 转换任务数据为任务卡片格式
                task_card_data = self.convert_task_to_task_card(task, task_index)
                
                # 创建任务卡片
                task_card = TaskCard(task_card_data)
                task_card.step_clicked.connect(self.on_card_clicked)
                
                # 添加到网格
                grid_layout.addWidget(task_card, row, col)
                self.task_cards.append(task_card)
                
                # 更新位置
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
        
        grid_container.setLayout(grid_layout)
        
        # 添加滚动支持
        scroll_area = QScrollArea()
        scroll_area.setWidget(grid_container)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        parent_layout.addWidget(scroll_area)
        
    def convert_task_to_task_card(self, task, task_index):
        """
        转换任务数据为任务卡片数据格式
        
        Args:
            task (dict): 原始任务数据
            task_index (int): 任务索引
            
        Returns:
            dict: 任务卡片数据
        """
        signal_type = task.get('signal_type', 'UART')
        
        # 根据信号类型和任务生成测试步骤
        test_steps = self.generate_test_steps(signal_type, task)
        
        # 确定任务状态
        current_task = self.plan_project_data.get('current_task', 0)
        if task_index < current_task:
            status = 'completed'
        elif task_index == current_task:
            status = 'running' if self.plan_project_data.get('status') == 'running' else 'paused'
        else:
            status = 'pending'
        
        task_card_data = {
            "card_type": "level2",
            "task_index": task_index,
            "title": task.get('task_name', f'{signal_type}任务{task_index + 1}'),
            "description": task.get('test_description', f'{signal_type}信号测试'),
            "signal_type": signal_type,
            "priority": task.get('priority', 'medium'),
            "estimated_time": task.get('estimated_time', '15分钟'),
            "status": status,
            "test_steps": test_steps,
            "result": self.get_task_result(task_index, status)
        }
        
        return task_card_data
        
    def generate_test_steps(self, signal_type, task):
        """根据信号类型生成测试步骤"""
        step_templates = {
            'I2C': [
                {'type': 'instruction', 'content': '设置示波器采样率为100MSa/s，触发方式为上升沿'},
                {'type': 'HCI', 'content': '请连接I2C信号线到通道1(SDA)和通道2(SCL)'},
                {'type': 'instruction', 'content': '开始I2C协议解码，设置解码参数'},
                {'type': 'measurement', 'content': '测量I2C时钟频率和数据完整性'},
                {'type': 'analysis', 'content': '分析I2C通信质量和协议合规性'}
            ],
            'SPI': [
                {'type': 'instruction', 'content': '配置SPI解码参数：CPOL=0, CPHA=0'},
                {'type': 'HCI', 'content': '连接SPI信号：MOSI、MISO、SCK、CS到对应通道'},
                {'type': 'measurement', 'content': '测量SPI时钟频率和数据传输速率'},
                {'type': 'analysis', 'content': '验证SPI数据完整性和时序关系'}
            ],
            'UART': [
                {'type': 'instruction', 'content': '设置UART解码：波特率115200，8N1'},
                {'type': 'HCI', 'content': '连接UART信号TX、RX到示波器通道'},
                {'type': 'measurement', 'content': '测量UART信号质量和波特率精度'},
                {'type': 'analysis', 'content': '检查数据传输错误率和信号完整性'}
            ],
            'PWM': [
                {'type': 'instruction', 'content': '设置PWM测量参数：频率和占空比'},
                {'type': 'HCI', 'content': '连接PWM输出信号到示波器通道1'},
                {'type': 'measurement', 'content': '测量PWM频率、占空比和上升/下降时间'},
                {'type': 'analysis', 'content': '分析PWM信号稳定性和精度'}
            ],
            'VIO': [
                {'type': 'instruction', 'content': '设置电压测量范围和触发电平'},
                {'type': 'HCI', 'content': '连接电源线到示波器差分探头'},
                {'type': 'measurement', 'content': '测量电源纹波、噪声和稳定性'},
                {'type': 'analysis', 'content': '分析电源质量和负载响应特性'}
            ]
        }
        
        # 获取对应信号类型的步骤模板
        steps = step_templates.get(signal_type, [
            {'type': 'instruction', 'content': f'设置{signal_type}信号测试参数'},
            {'type': 'HCI', 'content': f'连接{signal_type}信号到示波器'},
            {'type': 'measurement', 'content': f'测量{signal_type}信号特性'},
            {'type': 'analysis', 'content': f'分析{signal_type}测试结果'}
        ])
        
        return steps
        
    def get_task_result(self, task_index, status):
        """获取任务结果"""
        if status == 'completed':
            return f"任务{task_index + 1}已完成，测试通过"
        elif status == 'running':
            return f"正在执行任务{task_index + 1}..."
        else:
            return f"任务{task_index + 1}等待执行"
            
    def on_card_clicked(self, task_data):
        """
        处理任务卡片点击事件
        """
        self.card_clicked.emit(task_data)


class WorkArea(QFrame):
    """
    中间工作区组件
    
    主要的工作内容显示区域
    """
    
    # 定义信号
    process_action_requested = Signal(str, dict)  # 流程操作请求信号
    task_card_clicked = Signal(dict)  # 任务卡片点击信号
    
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
        显示默认的空白内容
        """
        # 先清空现有内容，但不递归调用
        if hasattr(self, 'current_content') and self.current_content:
            self.scroll_area.setWidget(None)
            self.current_content = None
        
        # 创建默认内容容器
        default_widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(80, 100, 80, 100)  # 进一步增加边距
        layout.setSpacing(50)  # 增加间距
        
        # 欢迎区域
        welcome_frame = QFrame()
        welcome_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #f8faff, stop:1 #e6f3ff);
                border: 2px solid #e0e7ff;
                border-radius: 24px;
                padding: 40px;
            }
        """)
        
        welcome_layout = QVBoxLayout()
        welcome_layout.setSpacing(30)  # 增加内部间距
        welcome_layout.setAlignment(Qt.AlignCenter)
        
        # 主标题
        main_title = QLabel("🎯 AI 示波器控制系统")
        main_title.setFont(QFont("微软雅黑", 28, QFont.Bold))
        main_title.setStyleSheet("""
            QLabel {
                color: #4338ca;
                text-align: center;
                margin: 10px 0;
            }
        """)
        main_title.setAlignment(Qt.AlignCenter)
        
        # 副标题
        subtitle = QLabel("点击左侧项目卡片展开测试步骤，开始您的测试流程")
        subtitle.setFont(QFont("微软雅黑", 16))
        subtitle.setStyleSheet("""
            QLabel {
                color: #6366f1;
                text-align: center;
                margin: 5px 0;
            }
        """)
        subtitle.setAlignment(Qt.AlignCenter)
        
        # 功能说明
        features_layout = QHBoxLayout()
        features_layout.setSpacing(40)  # 增加功能项之间的间距
        features_layout.setAlignment(Qt.AlignCenter)
        
        features = [
            ("📊", "智能测试", "AI驱动的自动化测试流程"),
            ("🔧", "多协议支持", "支持I2C、SPI、UART等协议"),
            ("📈", "实时分析", "实时数据采集和分析")
        ]
        
        for icon, title, desc in features:
            feature_widget = QWidget()
            feature_layout = QVBoxLayout()
            feature_layout.setAlignment(Qt.AlignCenter)
            feature_layout.setSpacing(15)  # 增加功能项内部间距
            
            # 图标
            icon_label = QLabel(icon)
            icon_label.setFont(QFont("微软雅黑", 32))
            icon_label.setAlignment(Qt.AlignCenter)
            icon_label.setStyleSheet("color: #8b5cf6; margin: 5px;")
            
            # 标题
            title_label = QLabel(title)
            title_label.setFont(QFont("微软雅黑", 14, QFont.Bold))
            title_label.setAlignment(Qt.AlignCenter)
            title_label.setStyleSheet("color: #374151; margin: 3px;")
            
            # 描述
            desc_label = QLabel(desc)
            desc_label.setFont(QFont("微软雅黑", 11))
            desc_label.setAlignment(Qt.AlignCenter)
            desc_label.setStyleSheet("color: #6b7280; margin: 3px;")
            desc_label.setWordWrap(True)
            
            feature_layout.addWidget(icon_label)
            feature_layout.addWidget(title_label)
            feature_layout.addWidget(desc_label)
            
            feature_widget.setLayout(feature_layout)
            features_layout.addWidget(feature_widget)
        
        # 操作提示
        tip_label = QLabel("💡 提示：点击左侧项目流程卡片，展开查看详细的测试步骤")
        tip_label.setFont(QFont("微软雅黑", 12))
        tip_label.setStyleSheet("""
            QLabel {
                color: #059669;
                background-color: #f0fdf4;
                border: 1px solid #bbf7d0;
                border-radius: 12px;
                padding: 15px 20px;
                text-align: center;
            }
        """)
        tip_label.setAlignment(Qt.AlignCenter)
        
        # 添加所有组件到布局
        welcome_layout.addWidget(main_title)
        welcome_layout.addWidget(subtitle)
        welcome_layout.addSpacing(25)  # 增加间距
        welcome_layout.addLayout(features_layout)
        welcome_layout.addSpacing(25)  # 增加间距
        welcome_layout.addWidget(tip_label)
        
        welcome_frame.setLayout(welcome_layout)
        
        # 添加弹性空间
        layout.addStretch(1)
        layout.addWidget(welcome_frame)
        layout.addStretch(2)
        
        default_widget.setLayout(layout)
        self.set_content(default_widget)
        
    def show_plan_project_tasks(self, plan_project_data):
        """
        显示计划任务
        
        Args:
            plan_project_data (dict): 计划数据
        """
        # 创建任务卡片容器
        task_container = TaskCardsContainer(plan_project_data)
        task_container.card_clicked.connect(self.on_task_card_clicked)
        
        # 设置为当前内容
        self.set_content(task_container)
        
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
        
    def on_task_card_clicked(self, task_data):
        """
        处理任务卡片点击事件
        """
        self.task_card_clicked.emit(task_data)
        
    def on_process_action(self, action, process_data):
        """
        处理流程操作请求
        
        Args:
            action (str): 操作类型
            process_data (dict): 流程数据
        """
        print(f"工作区接收到流程操作: {action}")
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
        if hasattr(self, 'current_content') and self.current_content:
            self.scroll_area.setWidget(None)
            self.current_content = None 