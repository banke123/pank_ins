"""
卡片组件模块

提供不同类型的流程卡片组件，包括任务卡片和计划卡片
支持美观的界面设计和交互功能
"""

from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QWidget, QProgressBar, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve, QRect
from PySide6.QtGui import QFont, QPainter, QPainterPath, QColor, QLinearGradient


class BaseCard(QFrame):
    """
    基础卡片类
    
    提供通用的卡片外观和动画效果
    """
    
    card_clicked = Signal(dict)
    
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.is_hovered = False
        self.setup_base_style()
        
    def setup_base_style(self):
        """设置基础样式"""
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
            BaseCard {
                background-color: white;
                border-radius: 16px;
                border: 2px solid #e2e8f0;
            }
        """)
        
    def update_display(self):
        """
        更新显示内容的基础方法
        子类应该重写此方法来实现具体的更新逻辑
        """
        pass
        
    def enterEvent(self, event):
        """鼠标进入事件"""
        self.is_hovered = True
        # 禁用悬停动画效果，只展开不放大
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        """鼠标离开事件"""
        self.is_hovered = False
        # 禁用悬停动画效果，只展开不放大
        super().leaveEvent(event)
        
    def mousePressEvent(self, event):
        """处理点击事件"""
        if event.button() == Qt.LeftButton:
            self.card_clicked.emit(self.data)
        super().mousePressEvent(event)


class TaskCard(BaseCard):
    """
    任务卡片 - 信号测试流程卡片
    
    显示在工作区，展示具体的信号测试步骤和进度
    """
    
    step_clicked = Signal(dict, int)
    
    def __init__(self, task_data):
        super().__init__(task_data)
        self.task_data = task_data
        self.setup_ui()
        
    def update_display(self):
        """
        更新任务卡片显示内容
        """
        # 更新数据引用
        self.data = self.task_data
        
        # 重新设置样式和主题色
        status = self.task_data.get('status', 'running')
        self.theme_colors = self.get_theme_colors(status)
        
        # 重新创建界面
        self.setup_ui()
        
    def setup_ui(self):
        """设置任务卡片界面"""
        # 移除固定高度，让卡片自适应内容
        # self.setFixedHeight(220)
        self.setMinimumHeight(220)  # 设置最小高度
        
        # 根据状态设置主题色
        status = self.task_data.get('status', 'running')
        self.theme_colors = self.get_theme_colors(status)
        
        self.setStyleSheet(f"""
            TaskCard {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 white, stop:1 {self.theme_colors['bg_gradient']});
                border: 2px solid {self.theme_colors['border']};
                border-left: 6px solid {self.theme_colors['accent']};
                border-radius: 16px;
                margin: 12px 8px;
            }}
            TaskCard:hover {{
                border-color: {self.theme_colors['accent']};
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(28, 24, 28, 24)  # 进一步增加边距
        layout.setSpacing(18)  # 增加间距
        
        # 创建各个区域
        self.create_header(layout)
        self.create_signal_info(layout)
        self.create_progress_section(layout)
        self.create_current_step(layout)
        self.create_action_buttons(layout)
        
        self.setLayout(layout)
        
    def get_theme_colors(self, status):
        """根据状态获取主题色"""
        color_schemes = {
            'running': {
                'accent': '#3b82f6',
                'border': '#dbeafe',
                'bg_gradient': '#f0f9ff',
                'text': '#1e40af'
            },
            'completed': {
                'accent': '#10b981',
                'border': '#d1fae5',
                'bg_gradient': '#f0fdf4',
                'text': '#059669'
            },
            'error': {
                'accent': '#ef4444',
                'border': '#fecaca',
                'bg_gradient': '#fef2f2',
                'text': '#dc2626'
            },
            'paused': {
                'accent': '#f59e0b',
                'border': '#fed7aa',
                'bg_gradient': '#fffbeb',
                'text': '#d97706'
            }
        }
        return color_schemes.get(status, color_schemes['running'])
        
    def create_header(self, parent_layout):
        """创建头部区域"""
        header_layout = QHBoxLayout()
        header_layout.setSpacing(16)  # 增加头部元素间距
        
        # 信号类型图标和标题
        icon_widget = QLabel()
        icon_widget.setFixedSize(48, 48)
        signal_type = self.task_data.get('signal_type', '未知')
        icon_widget.setText(self.get_signal_icon(signal_type))
        icon_widget.setAlignment(Qt.AlignCenter)
        icon_widget.setStyleSheet(f"""
            QLabel {{
                background-color: {self.theme_colors['accent']};
                color: white;
                border-radius: 24px;
                font-size: 20px;
                font-weight: bold;
            }}
        """)
        
        # 标题区域
        title_layout = QVBoxLayout()
        title_layout.setSpacing(4)
        
        title = QLabel(f"{signal_type} 信号测试")
        title.setFont(QFont("微软雅黑", 13, QFont.Bold))
        title.setStyleSheet(f"color: {self.theme_colors['text']};")
        
        subtitle = QLabel(f"计划 #{self.task_data.get('plan_num', 0)}")
        subtitle.setFont(QFont("微软雅黑", 10))
        subtitle.setStyleSheet("color: #6b7280;")
        
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        
        # 状态标签
        status_label = self.create_status_badge()
        
        header_layout.addWidget(icon_widget)
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        header_layout.addWidget(status_label)
        
        parent_layout.addLayout(header_layout)
        
    def get_signal_icon(self, signal_type):
        """获取信号类型图标"""
        icons = {
            'I2C': '🔧', 'SPI': '⚡', 'UART': '📡',
            'PWM': '〰️', 'CLOCK': '⏰', 'VIO': '🔋'
        }
        return icons.get(signal_type, '📊')
        
    def create_status_badge(self):
        """创建状态徽章"""
        status = self.task_data.get('status', 'running')
        status_text = {'running': '执行中', 'completed': '已完成', 
                      'error': '错误', 'paused': '暂停'}.get(status, '未知')
        
        badge = QLabel(f"● {status_text}")
        badge.setFont(QFont("微软雅黑", 9, QFont.Bold))
        badge.setAlignment(Qt.AlignCenter)
        badge.setFixedSize(80, 28)
        badge.setStyleSheet(f"""
            QLabel {{
                background-color: {self.theme_colors['accent']};
                color: white;
                border-radius: 14px;
                padding: 4px 12px;
            }}
        """)
        
        return badge
        
    def create_signal_info(self, parent_layout):
        """创建信号信息区域"""
        info_layout = QHBoxLayout()
        info_layout.setSpacing(20)  # 增加信息项间距
        
        # 步骤信息
        steps = self.task_data.get('steps', [])
        total_steps = len(steps)
        current_step = self.task_data.get('current_step', 0)
        
        steps_info = QLabel(f"📋 {total_steps} 个步骤")
        steps_info.setFont(QFont("微软雅黑", 10))
        steps_info.setStyleSheet("color: #4b5563;")
        
        # 进度信息
        progress_info = QLabel(f"🎯 {current_step}/{total_steps}")
        progress_info.setFont(QFont("微软雅黑", 10))
        progress_info.setStyleSheet("color: #4b5563;")
        
        info_layout.addWidget(steps_info)
        info_layout.addWidget(progress_info)
        info_layout.addStretch()
        
        parent_layout.addLayout(info_layout)
        
    def create_progress_section(self, parent_layout):
        """创建进度区域"""
        progress_layout = QVBoxLayout()
        progress_layout.setSpacing(10)  # 增加进度区域内部间距
        
        # 进度条
        progress_bar = QProgressBar()
        current_step = self.task_data.get('current_step', 0)
        total_steps = len(self.task_data.get('steps', []))
        
        if total_steps > 0:
            progress_value = int((current_step / total_steps) * 100)
        else:
            progress_value = 0
            
        progress_bar.setValue(progress_value)
        progress_bar.setFixedHeight(8)
        progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                background-color: #f3f4f6;
                border-radius: 4px;
            }}
            QProgressBar::chunk {{
                background-color: {self.theme_colors['accent']};
                border-radius: 4px;
            }}
        """)
        
        # 步骤点
        dots_layout = QHBoxLayout()
        dots_layout.setSpacing(6)
        
        for i in range(total_steps):
            dot = QLabel("●")
            if i < current_step:
                dot.setStyleSheet("color: #10b981; font-size: 12px;")  # 已完成
            elif i == current_step:
                dot.setStyleSheet(f"color: {self.theme_colors['accent']}; font-size: 16px;")  # 当前
            else:
                dot.setStyleSheet("color: #e5e7eb; font-size: 12px;")  # 未开始
            dots_layout.addWidget(dot)
            
        dots_layout.addStretch()
        
        progress_layout.addWidget(progress_bar)
        progress_layout.addLayout(dots_layout)
        
        parent_layout.addLayout(progress_layout)
        
    def create_current_step(self, parent_layout):
        """创建当前步骤区域"""
        steps = self.task_data.get('steps', [])
        current_step = self.task_data.get('current_step', 0)
        
        if steps and current_step < len(steps):
            step_data = steps[current_step]
            step_type = step_data.get('type', '')
            step_content = step_data.get('content', '')
            
            step_layout = QHBoxLayout()
            step_layout.setContentsMargins(16, 12, 16, 12)  # 增加步骤内边距
            step_layout.setSpacing(16)  # 增加步骤内部间距
            
            # 步骤类型图标
            type_icon = {'instruction': '⚡', 'HCI': '👤', 
                        'measurement': '📊', 'analysis': '🔍'}.get(step_type, '📋')
            
            icon_label = QLabel(type_icon)
            icon_label.setFixedSize(32, 32)
            icon_label.setAlignment(Qt.AlignCenter)
            icon_label.setStyleSheet(f"""
                QLabel {{
                    background-color: {self.theme_colors['bg_gradient']};
                    border: 2px solid {self.theme_colors['accent']};
                    border-radius: 16px;
                    font-size: 14px;
                }}
            """)
            
            # 步骤内容
            content_label = QLabel(step_content[:60] + "..." if len(step_content) > 60 else step_content)
            content_label.setFont(QFont("微软雅黑", 10))
            content_label.setStyleSheet("color: #374151;")
            content_label.setWordWrap(True)
            
            step_layout.addWidget(icon_label)
            step_layout.addWidget(content_label)
            step_layout.addStretch()
            
            parent_layout.addLayout(step_layout)
            
    def create_action_buttons(self, parent_layout):
        """创建操作按钮区域"""
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        
        # 详情按钮
        detail_btn = QPushButton("📋 查看详情")
        detail_btn.setFont(QFont("微软雅黑", 9))
        detail_btn.setFixedHeight(32)
        detail_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.theme_colors['accent']};
                color: white;
                border: none;
                border-radius: 16px;
                padding: 6px 16px;
            }}
            QPushButton:hover {{
                background-color: {self.theme_colors['text']};
            }}
        """)
        
        # 控制按钮
        status = self.task_data.get('status', 'running')
        if status == 'running':
            control_btn = QPushButton("⏸️ 暂停")
        elif status == 'paused':
            control_btn = QPushButton("▶️ 继续")
        elif status == 'completed':
            control_btn = QPushButton("🔄 重新执行")
        else:
            control_btn = QPushButton("▶️ 开始")
            
        control_btn.setFont(QFont("微软雅黑", 9))
        control_btn.setFixedHeight(32)
        control_btn.setStyleSheet("""
            QPushButton {
                background-color: #f3f4f6;
                color: #374151;
                border: 1px solid #d1d5db;
                border-radius: 16px;
                padding: 6px 16px;
            }
            QPushButton:hover {
                background-color: #e5e7eb;
            }
        """)
        
        button_layout.addStretch()
        button_layout.addWidget(detail_btn)
        button_layout.addWidget(control_btn)
        
        parent_layout.addLayout(button_layout)


class PlanCard(BaseCard):
    """
    计划卡片 - 测试计划流程卡片
    
    显示在左侧边栏，支持展开显示任务内容
    """
    
    task_selected = Signal(dict, int)
    
    def __init__(self, plan_data):
        super().__init__(plan_data)
        self.plan_data = plan_data
        self.project_data = plan_data  # 添加project_data别名保持兼容性
        self.is_expanded = False  # 是否展开状态
        self.task_widgets = []     # 存储任务步骤组件
        self.setup_ui()
        
    def update_display(self):
        """
        更新计划卡片显示内容
        当项目数据发生变化时调用此方法来刷新界面
        """
        # 注意：这里的self.project_data是从外部传入的更新后的数据
        # 更新内部数据引用
        self.plan_data = self.project_data
        self.data = self.project_data
        
        # 清除当前界面
        if hasattr(self, 'main_layout') and self.main_layout:
            while self.main_layout.count():
                child = self.main_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
        
        # 清除任务组件
        self.clear_task_widgets()
        
        # 重新设置样式和主题色
        status = self.plan_data.get('status', 'planning')
        self.theme_colors = self.get_theme_colors(status)
        
        # 重新创建界面
        self.setup_ui()
        
        print(f"卡片界面已更新: {self.plan_data.get('project_name', '未知')}")
        
    def clear_task_widgets(self):
        """
        清除任务步骤组件
        """
        for widget in self.task_widgets:
            widget.setParent(None)
            widget.deleteLater()
        self.task_widgets.clear()
        
    def setup_ui(self):
        """设置计划卡片界面"""
        # 设置卡片最大宽度，防止被内容撑开
        self.setMaximumWidth(330)  # 稍小于侧边栏宽度360
        
        # 根据状态设置主题色
        status = self.plan_data.get('status', 'planning')
        self.theme_colors = self.get_theme_colors(status)
        
        self.setStyleSheet(f"""
            PlanCard {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 white, stop:1 {self.theme_colors['bg_gradient']});
                border: 2px solid {self.theme_colors['border']};
                border-left: 5px solid {self.theme_colors['accent']};
                border-radius: 12px;
                margin: 8px 6px;
            }}
            PlanCard:hover {{
                border-color: {self.theme_colors['accent']};
            }}
        """)
        
        # 主布局
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(20, 20, 20, 20)  # 减少内边距
        self.main_layout.setSpacing(16)  # 减少内部间距
        
        # 创建固定显示的头部区域
        self.create_header(self.main_layout)
        self.create_plan_info(self.main_layout)
        self.create_progress_indicator(self.main_layout)
        
        # 创建可展开的任务内容区域（初始隐藏）
        self.create_expandable_content()
        
        self.setLayout(self.main_layout)
        
    def create_expandable_content(self):
        """创建可展开的任务内容区域"""
        # 分隔线
        self.separator = QFrame()
        self.separator.setFrameShape(QFrame.HLine)
        self.separator.setFrameShadow(QFrame.Sunken)
        self.separator.setStyleSheet(f"color: {self.theme_colors['border']};")
        self.separator.hide()
        
        # 任务步骤容器
        self.task_container = QWidget()
        self.task_container.setMaximumWidth(290)  # 设置容器最大宽度
        self.task_layout = QVBoxLayout()
        self.task_layout.setContentsMargins(0, 8, 0, 0)  # 减少顶部边距
        self.task_layout.setSpacing(8)  # 减少步骤间距
        
        # 标题
        self.task_title = QLabel("📋 测试任务详情")
        self.task_title.setFont(QFont("微软雅黑", 10, QFont.Bold))
        self.task_title.setStyleSheet(f"color: {self.theme_colors['text']};")
        self.task_layout.addWidget(self.task_title)
        
        # 创建任务步骤列表
        self.create_task_steps()
        
        self.task_container.setLayout(self.task_layout)
        self.task_container.hide()
        
        # 添加到主布局
        self.main_layout.addWidget(self.separator)
        self.main_layout.addWidget(self.task_container)
        self.main_layout.addStretch()
        
    def create_task_steps(self):
        """创建任务步骤列表"""
        tasks = self.plan_data.get('tasks', [])
        current_task = self.plan_data.get('current_task', 0)
        
        for i, task in enumerate(tasks):
            step_widget = self.create_task_step_widget(task, i, i <= current_task)
            self.task_layout.addWidget(step_widget)
            self.task_widgets.append(step_widget)
            
    def create_task_step_widget(self, task_data, step_index, is_active):
        """创建单个任务步骤组件"""
        step_widget = QFrame()
        step_widget.setMinimumHeight(70)  # 减少最小高度
        step_widget.setMaximumWidth(290)  # 设置最大宽度，防止撑开
        
        # 正确设置QSizePolicy
        step_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        
        # 根据状态设置样式
        if step_index < self.plan_data.get('current_task', 0):
            # 已完成
            bg_color = "#f0fdf4"
            border_color = "#10b981"
            text_color = "#059669"
            status_text = "已完成"
            status_icon = "✅"
        elif step_index == self.plan_data.get('current_task', 0):
            # 进行中
            bg_color = "#f0f9ff"
            border_color = "#3b82f6"
            text_color = "#2563eb"
            status_text = "进行中"
            status_icon = "🔄"
        else:
            # 待执行
            bg_color = "#f9fafb"
            border_color = "#d1d5db"
            text_color = "#6b7280"
            status_text = "待执行"
            status_icon = "⏳"
            
        step_widget.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: 8px;
                margin: 2px 0px;
            }}
            QFrame:hover {{
                border-color: {self.theme_colors['accent']};
                background-color: {self.theme_colors['bg_gradient']};
            }}
        """)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(12, 10, 12, 10)  # 减少步骤内边距
        layout.setSpacing(12)  # 减少步骤内部间距
        
        # 步骤编号
        step_num = QLabel(f"{step_index + 1}")
        step_num.setFixedSize(20, 20)  # 减少编号大小
        step_num.setAlignment(Qt.AlignCenter)
        step_num.setFont(QFont("微软雅黑", 9, QFont.Bold))
        step_num.setStyleSheet(f"""
            QLabel {{
                background-color: {border_color};
                color: white;
                border-radius: 10px;
                font-weight: bold;
            }}
        """)
        
        # 步骤信息
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)  # 减少步骤信息内部间距
        
        # 任务名称 - 限制长度并启用换行
        task_name_text = task_data.get('task_name', f'任务 {step_index + 1}')
        if len(task_name_text) > 25:
            task_name_text = task_name_text[:25] + "..."
        task_name = QLabel(task_name_text)
        task_name.setFont(QFont("微软雅黑", 9, QFont.Bold))
        task_name.setStyleSheet(f"color: {text_color};")
        task_name.setWordWrap(True)
        task_name.setMaximumWidth(180)  # 限制名称宽度
        
        # 任务描述 - 限制长度并启用换行
        desc_text = task_data.get('test_description', '')
        if len(desc_text) > 40:
            desc_text = desc_text[:40] + "..."
        task_desc = QLabel(desc_text)
        task_desc.setFont(QFont("微软雅黑", 8))
        task_desc.setStyleSheet(f"color: {text_color};")
        task_desc.setWordWrap(True)
        task_desc.setMaximumWidth(180)  # 限制描述宽度
        
        info_layout.addWidget(task_name)
        info_layout.addWidget(task_desc)
        
        # 状态和时间
        status_layout = QVBoxLayout()
        status_layout.setSpacing(2)  # 减少状态区域间距
        
        # 状态
        status_label = QLabel(f"{status_icon}")
        status_label.setFont(QFont("微软雅黑", 8))
        status_label.setStyleSheet(f"color: {text_color};")
        status_label.setAlignment(Qt.AlignCenter)
        
        # 预计时间 - 简化显示
        time_text = task_data.get('estimated_time', '未知')
        # 确保time_text是字符串类型
        if not isinstance(time_text, str):
            time_text = str(time_text) if time_text is not None else '未知'
        if len(time_text) > 8:
            time_text = time_text[:8]
        time_label = QLabel(time_text)
        time_label.setFont(QFont("微软雅黑", 7))
        time_label.setStyleSheet(f"color: {text_color};")
        time_label.setAlignment(Qt.AlignCenter)
        
        status_layout.addWidget(status_label)
        status_layout.addWidget(time_label)
        status_layout.addStretch()
        
        layout.addWidget(step_num)
        layout.addLayout(info_layout, 1)
        layout.addLayout(status_layout)
        
        step_widget.setLayout(layout)
        
        # 添加点击事件
        step_widget.mousePressEvent = lambda event, idx=step_index: self.on_step_clicked(idx)
        step_widget.setCursor(Qt.PointingHandCursor)
        
        return step_widget
        
    def on_step_clicked(self, step_index):
        """处理步骤点击事件"""
        print(f"任务 {step_index + 1} 被点击")
        self.task_selected.emit(self.plan_data, step_index)
        
    def toggle_expansion(self):
        """切换展开/收起状态"""
        self.is_expanded = not self.is_expanded
        
        if self.is_expanded:
            # 展开
            self.separator.show()
            self.task_container.show()
        else:
            # 收起
            self.separator.hide()
            self.task_container.hide()
            
        # 更新展开指示器
        self.update_expand_indicator()
        
        # 触发布局更新
        self.updateGeometry()
        if self.parent():
            self.parent().updateGeometry()
        
    def mousePressEvent(self, event):
        """处理卡片点击事件"""
        if event.button() == Qt.LeftButton:
            # 发送卡片点击信号，让父组件处理
            self.card_clicked.emit(self.plan_data)
            
            # 点击后展开/收起卡片
            self.toggle_expansion()
        super().mousePressEvent(event)
        
    def get_theme_colors(self, status):
        """根据状态获取主题色"""
        color_schemes = {
            'planning': {
                'accent': '#8b5cf6',
                'border': '#e9d5ff',
                'bg_gradient': '#faf5ff',
                'text': '#7c3aed'
            },
            'running': {
                'accent': '#3b82f6',
                'border': '#dbeafe',
                'bg_gradient': '#f0f9ff',
                'text': '#2563eb'
            },
            'completed': {
                'accent': '#10b981',
                'border': '#d1fae5',
                'bg_gradient': '#f0fdf4',
                'text': '#059669'
            },
            'error': {
                'accent': '#ef4444',
                'border': '#fecaca',
                'bg_gradient': '#fef2f2',
                'text': '#dc2626'
            }
        }
        return color_schemes.get(status, color_schemes['planning'])
        
    def create_header(self, parent_layout):
        """创建头部区域"""
        header_layout = QHBoxLayout()
        header_layout.setSpacing(16)  # 增加头部元素间距
        
        # 展开/收起指示器
        self.expand_indicator = QLabel("▶")
        self.expand_indicator.setFont(QFont("微软雅黑", 10))
        self.expand_indicator.setFixedSize(16, 16)
        self.expand_indicator.setAlignment(Qt.AlignCenter)
        self.expand_indicator.setStyleSheet(f"color: {self.theme_colors['accent']};")
        
        # 计划名称
        plan_name = QLabel(self.plan_data.get('project_name', '未命名计划'))
        plan_name.setFont(QFont("微软雅黑", 12, QFont.Bold))
        plan_name.setStyleSheet(f"color: {self.theme_colors['text']};")
        plan_name.setWordWrap(True)
        
        # 状态徽章
        status_badge = self.create_status_badge()
        
        header_layout.addWidget(self.expand_indicator)
        header_layout.addWidget(plan_name, 1)
        header_layout.addWidget(status_badge)
        
        parent_layout.addLayout(header_layout)
        
    def create_status_badge(self):
        """创建状态徽章"""
        status = self.plan_data.get('status', 'planning')
        status_map = {
            'planning': '📋 计划中',
            'running': '🔄 进行中', 
            'completed': '✅ 已完成',
            'error': '❌ 错误'
        }
        
        badge = QLabel(status_map.get(status, '❓ 未知'))
        badge.setFont(QFont("微软雅黑", 9))
        badge.setFixedHeight(24)
        badge.setAlignment(Qt.AlignCenter)
        badge.setStyleSheet(f"""
            QLabel {{
                background-color: {self.theme_colors['accent']};
                color: white;
                border-radius: 12px;
                padding: 4px 12px;
            }}
        """)
        
        return badge
        
    def create_plan_info(self, parent_layout):
        """创建计划信息区域"""
        info_layout = QHBoxLayout()
        info_layout.setSpacing(20)  # 增加信息项间距
        
        # 任务数量
        total_tasks = self.plan_data.get('total_tasks', 0)
        current_task = self.plan_data.get('current_task', 0)
        
        tasks_info = QLabel(f"📝 {total_tasks} 个任务")
        tasks_info.setFont(QFont("微软雅黑", 10))
        tasks_info.setStyleSheet("color: #6b7280;")
        
        # 预计时间
        estimated_time = self.plan_data.get('estimated_total_time', '未知')
        time_info = QLabel(f"⏱️ {estimated_time}")
        time_info.setFont(QFont("微软雅黑", 10))
        time_info.setStyleSheet("color: #6b7280;")
        
        info_layout.addWidget(tasks_info)
        info_layout.addWidget(time_info)
        info_layout.addStretch()
        
        parent_layout.addLayout(info_layout)
        
    def create_progress_indicator(self, parent_layout):
        """创建进度指示器"""
        progress_layout = QVBoxLayout()
        progress_layout.setSpacing(10)  # 增加进度区域内部间距
        
        # 进度文本
        current_task = self.plan_data.get('current_task', 0)
        total_tasks = self.plan_data.get('total_tasks', 1)
        progress_text = QLabel(f"进度: {current_task}/{total_tasks}")
        progress_text.setFont(QFont("微软雅黑", 9))
        progress_text.setStyleSheet("color: #6b7280;")
        
        # 进度条
        progress_bar = QFrame()
        progress_bar.setFixedHeight(6)
        progress_value = (current_task / total_tasks * 100) if total_tasks > 0 else 0
        progress_bar.setStyleSheet(f"""
            QFrame {{
                background-color: #e5e7eb;
                border-radius: 3px;
            }}
        """)
        
        # 在进度条上添加已完成部分的样式
        if progress_value > 0:
            progress_inner = QFrame(progress_bar)
            progress_inner.setFixedHeight(6)
            progress_inner.setFixedWidth(int(progress_bar.width() * progress_value / 100))
            progress_inner.setStyleSheet(f"""
                QFrame {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 {self.theme_colors['accent']}, 
                        stop:1 {self.theme_colors['text']});
                    border-radius: 3px;
                }}
            """)
        
        progress_layout.addWidget(progress_text)
        progress_layout.addWidget(progress_bar)
        
        parent_layout.addLayout(progress_layout)
        
    def update_expand_indicator(self):
        """更新展开指示器"""
        if hasattr(self, 'expand_indicator'):
            if self.is_expanded:
                self.expand_indicator.setText("▼")
            else:
                self.expand_indicator.setText("▶") 