#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
现代化主界面窗口

采用现代化设计风格的主界面，包含：
- 左侧导航栏：功能模块导航
- 中间主工作区：AI对话、测试卡片、数据可视化
- 右侧信息面板：系统状态、日志、任务列表
- 顶部工具栏：快捷操作按钮
- 底部状态栏：系统信息显示

设计特色：
- 现代化扁平设计风格
- 流畅的动画效果
- 响应式布局
- 主题切换支持
- 模块化组件设计
"""

import sys
import logging
from typing import Optional, Dict, Any
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QFrame, QSplitter, QScrollArea,
    QStackedWidget, QToolBar, QStatusBar, QMenuBar,
    QSpacerItem, QSizePolicy, QTabWidget, QTextEdit,
    QProgressBar, QListWidget, QListWidgetItem
)
from PySide6.QtCore import (
    Qt, Signal, QTimer, QPropertyAnimation, QEasingCurve,
    QParallelAnimationGroup, QSequentialAnimationGroup, Slot
)
from PySide6.QtGui import (
    QFont, QIcon, QPalette, QColor, QAction, QPixmap,
    QPainter, QLinearGradient, QBrush
)

logger = logging.getLogger(__name__)


class ModernSidebar(QFrame):
    """现代化侧边栏组件"""
    
    # 信号定义
    module_selected = Signal(str)  # 模块选择信号
    
    def __init__(self):
        super().__init__()
        self.current_module = "ai_chat"
        self.setup_ui()
        self.setup_style()
        
    def setup_ui(self):
        """设置界面"""
        self.setObjectName("sidebar")
        self.setFixedWidth(280)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 30, 20, 30)
        layout.setSpacing(15)
        
        # Logo区域
        logo_widget = self.create_logo_widget()
        layout.addWidget(logo_widget)
        
        # 分隔线
        separator = QFrame()
        separator.setObjectName("separator")
        separator.setFrameShape(QFrame.HLine)
        separator.setFixedHeight(1)
        layout.addWidget(separator)
        
        # 导航菜单
        nav_widget = self.create_navigation_widget()
        layout.addWidget(nav_widget)
        
        # 弹簧
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # 用户信息
        user_widget = self.create_user_widget()
        layout.addWidget(user_widget)
        
        self.setLayout(layout)
        
    def create_logo_widget(self) -> QWidget:
        """创建Logo区域"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # 主标题
        title = QLabel("Pank Ins")
        title.setObjectName("logo_title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # 副标题
        subtitle = QLabel("AI 示波器控制系统")
        subtitle.setObjectName("logo_subtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)
        
        widget.setLayout(layout)
        return widget
        
    def create_navigation_widget(self) -> QWidget:
        """创建导航菜单"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(8)
        
        # 导航项配置
        nav_items = [
            ("ai_chat", "🤖", "AI 对话", "与AI助手进行智能对话"),
            ("test_cards", "📋", "测试卡片", "管理和执行测试计划"),
            ("data_analysis", "📊", "数据分析", "查看测试数据和图表"),
            ("device_control", "🔧", "设备控制", "控制示波器和测试设备"),
            ("timeline", "⏱️", "时序图", "查看和分析时序数据"),
            ("logs", "📝", "日志记录", "查看系统日志和历史"),
            ("settings", "⚙️", "系统设置", "配置系统参数和选项")
        ]
        
        self.nav_buttons = {}
        for module_id, icon, title, desc in nav_items:
            btn = self.create_nav_button(module_id, icon, title, desc)
            self.nav_buttons[module_id] = btn
            layout.addWidget(btn)
            
        # 设置默认选中
        self.nav_buttons[self.current_module].setProperty("selected", True)
        
        widget.setLayout(layout)
        return widget
        
    def create_nav_button(self, module_id: str, icon: str, title: str, desc: str) -> QPushButton:
        """创建导航按钮"""
        btn = QPushButton()
        btn.setObjectName("nav_button")
        btn.setFixedHeight(60)
        btn.setCursor(Qt.PointingHandCursor)
        
        # 按钮布局
        layout = QHBoxLayout()
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(15)
        
        # 图标
        icon_label = QLabel(icon)
        icon_label.setObjectName("nav_icon")
        icon_label.setFixedSize(24, 24)
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)
        
        # 文字区域
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        
        title_label = QLabel(title)
        title_label.setObjectName("nav_title")
        text_layout.addWidget(title_label)
        
        desc_label = QLabel(desc)
        desc_label.setObjectName("nav_desc")
        text_layout.addWidget(desc_label)
        
        layout.addLayout(text_layout)
        
        # 创建容器widget来包含布局
        container = QWidget()
        container.setLayout(layout)
        
        # 按钮布局
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.addWidget(container)
        btn.setLayout(btn_layout)
        
        # 连接点击事件
        btn.clicked.connect(lambda: self.select_module(module_id))
        
        return btn
        
    def create_user_widget(self) -> QWidget:
        """创建用户信息区域"""
        widget = QFrame()
        widget.setObjectName("user_widget")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # 用户头像和信息
        user_layout = QHBoxLayout()
        user_layout.setSpacing(10)
        
        # 头像
        avatar = QLabel("👤")
        avatar.setObjectName("user_avatar")
        avatar.setFixedSize(40, 40)
        avatar.setAlignment(Qt.AlignCenter)
        user_layout.addWidget(avatar)
        
        # 用户信息
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        
        name_label = QLabel("测试用户")
        name_label.setObjectName("user_name")
        info_layout.addWidget(name_label)
        
        status_label = QLabel("在线")
        status_label.setObjectName("user_status")
        info_layout.addWidget(status_label)
        
        user_layout.addLayout(info_layout)
        layout.addLayout(user_layout)
        
        widget.setLayout(layout)
        return widget
        
    def select_module(self, module_id: str):
        """选择模块"""
        if module_id == self.current_module:
            return
            
        # 更新按钮状态
        if self.current_module in self.nav_buttons:
            self.nav_buttons[self.current_module].setProperty("selected", False)
            
        self.current_module = module_id
        self.nav_buttons[module_id].setProperty("selected", True)
        
        # 刷新样式
        for btn in self.nav_buttons.values():
            btn.style().unpolish(btn)
            btn.style().polish(btn)
            
        # 发送信号
        self.module_selected.emit(module_id)
        logger.info(f"选择模块: {module_id}")
        
    def setup_style(self):
        """设置样式"""
        self.setStyleSheet("""
        /* 侧边栏主容器 */
        #sidebar {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #1e293b, stop:1 #0f172a);
            border-right: 2px solid #334155;
        }
        
        /* Logo标题 */
        #logo_title {
            font-size: 24px;
            font-weight: bold;
            color: #f1f5f9;
            margin-bottom: 5px;
        }
        
        #logo_subtitle {
            font-size: 12px;
            color: #94a3b8;
        }
        
        /* 分隔线 */
        #separator {
            background: #334155;
            margin: 10px 0;
        }
        
        /* 导航按钮 */
        #nav_button {
            background: transparent;
            border: none;
            border-radius: 12px;
            margin: 2px 0;
        }
        
        #nav_button:hover {
            background: rgba(59, 130, 246, 0.1);
        }
        
        #nav_button[selected="true"] {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #3b82f6, stop:1 #1d4ed8);
        }
        
        #nav_icon {
            font-size: 16px;
            color: #cbd5e1;
        }
        
        #nav_button[selected="true"] #nav_icon {
            color: white;
        }
        
        #nav_title {
            font-size: 14px;
            font-weight: 500;
            color: #e2e8f0;
        }
        
        #nav_button[selected="true"] #nav_title {
            color: white;
            font-weight: bold;
        }
        
        #nav_desc {
            font-size: 11px;
            color: #64748b;
        }
        
        #nav_button[selected="true"] #nav_desc {
            color: rgba(255, 255, 255, 0.8);
        }
        
        /* 用户信息 */
        #user_widget {
            background: rgba(51, 65, 85, 0.3);
            border: 1px solid #475569;
            border-radius: 12px;
        }
        
        #user_avatar {
            background: #475569;
            border-radius: 20px;
            font-size: 18px;
            color: #cbd5e1;
        }
        
        #user_name {
            font-size: 14px;
            font-weight: 500;
            color: #f1f5f9;
        }
        
        #user_status {
            font-size: 11px;
            color: #10b981;
        }
        """)


class ModernWorkArea(QFrame):
    """现代化工作区域"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_style()
        
    def setup_ui(self):
        """设置界面"""
        self.setObjectName("work_area")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # 工作区标题栏
        header = self.create_header()
        layout.addWidget(header)
        
        # 主内容区域
        self.content_stack = QStackedWidget()
        self.content_stack.setObjectName("content_stack")
        
        # 创建各个模块页面
        self.create_module_pages()
        
        layout.addWidget(self.content_stack)
        self.setLayout(layout)
        
    def create_header(self) -> QWidget:
        """创建标题栏"""
        header = QFrame()
        header.setObjectName("work_header")
        header.setFixedHeight(80)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(20)
        
        # 标题区域
        title_layout = QVBoxLayout()
        title_layout.setSpacing(5)
        
        self.page_title = QLabel("AI 对话助手")
        self.page_title.setObjectName("page_title")
        title_layout.addWidget(self.page_title)
        
        self.page_subtitle = QLabel("与AI助手进行智能对话，获取测试建议和技术支持")
        self.page_subtitle.setObjectName("page_subtitle")
        title_layout.addWidget(self.page_subtitle)
        
        layout.addLayout(title_layout)
        
        # 弹簧
        layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        
        # 操作按钮
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(10)
        
        refresh_btn = QPushButton("🔄 刷新")
        refresh_btn.setObjectName("action_button")
        actions_layout.addWidget(refresh_btn)
        
        settings_btn = QPushButton("⚙️ 设置")
        settings_btn.setObjectName("action_button")
        actions_layout.addWidget(settings_btn)
        
        layout.addLayout(actions_layout)
        header.setLayout(layout)
        
        return header
        
    def create_module_pages(self):
        """创建模块页面"""
        # AI对话页面
        ai_chat_page = self.create_ai_chat_page()
        self.content_stack.addWidget(ai_chat_page)
        
        # 测试卡片页面
        test_cards_page = self.create_test_cards_page()
        self.content_stack.addWidget(test_cards_page)
        
        # 数据分析页面
        data_analysis_page = self.create_data_analysis_page()
        self.content_stack.addWidget(data_analysis_page)
        
        # 设备控制页面
        device_control_page = self.create_device_control_page()
        self.content_stack.addWidget(device_control_page)
        
        # 时序图页面
        timeline_page = self.create_timeline_page()
        self.content_stack.addWidget(timeline_page)
        
        # 日志页面
        logs_page = self.create_logs_page()
        self.content_stack.addWidget(logs_page)
        
        # 设置页面
        settings_page = self.create_settings_page()
        self.content_stack.addWidget(settings_page)
        
    def create_ai_chat_page(self) -> QWidget:
        """创建AI对话页面"""
        page = QWidget()
        layout = QVBoxLayout()
        
        # 临时内容
        content = QLabel("🤖 AI对话模块\n\n这里将显示AI对话界面")
        content.setObjectName("page_content")
        content.setAlignment(Qt.AlignCenter)
        content.setStyleSheet("""
            #page_content {
                font-size: 16px;
                color: #64748b;
                background: #f8fafc;
                border-radius: 12px;
                padding: 40px;
                border: 2px dashed #cbd5e1;
            }
        """)
        
        layout.addWidget(content)
        page.setLayout(layout)
        return page
        
    def create_test_cards_page(self) -> QWidget:
        """创建测试卡片页面"""
        page = QWidget()
        layout = QVBoxLayout()
        
        content = QLabel("📋 测试卡片模块\n\n这里将显示测试计划和执行卡片")
        content.setObjectName("page_content")
        content.setAlignment(Qt.AlignCenter)
        content.setStyleSheet("""
            #page_content {
                font-size: 16px;
                color: #64748b;
                background: #f8fafc;
                border-radius: 12px;
                padding: 40px;
                border: 2px dashed #cbd5e1;
            }
        """)
        
        layout.addWidget(content)
        page.setLayout(layout)
        return page
        
    def create_data_analysis_page(self) -> QWidget:
        """创建数据分析页面"""
        page = QWidget()
        layout = QVBoxLayout()
        
        content = QLabel("📊 数据分析模块\n\n这里将显示测试数据的图表和分析结果")
        content.setObjectName("page_content")
        content.setAlignment(Qt.AlignCenter)
        content.setStyleSheet("""
            #page_content {
                font-size: 16px;
                color: #64748b;
                background: #f8fafc;
                border-radius: 12px;
                padding: 40px;
                border: 2px dashed #cbd5e1;
            }
        """)
        
        layout.addWidget(content)
        page.setLayout(layout)
        return page
        
    def create_device_control_page(self) -> QWidget:
        """创建设备控制页面"""
        page = QWidget()
        layout = QVBoxLayout()
        
        content = QLabel("🔧 设备控制模块\n\n这里将显示示波器和其他测试设备的控制界面")
        content.setObjectName("page_content")
        content.setAlignment(Qt.AlignCenter)
        content.setStyleSheet("""
            #page_content {
                font-size: 16px;
                color: #64748b;
                background: #f8fafc;
                border-radius: 12px;
                padding: 40px;
                border: 2px dashed #cbd5e1;
            }
        """)
        
        layout.addWidget(content)
        page.setLayout(layout)
        return page
        
    def create_timeline_page(self) -> QWidget:
        """创建时序图页面"""
        page = QWidget()
        layout = QVBoxLayout()
        
        content = QLabel("⏱️ 时序图模块\n\n这里将显示时序数据的可视化图表")
        content.setObjectName("page_content")
        content.setAlignment(Qt.AlignCenter)
        content.setStyleSheet("""
            #page_content {
                font-size: 16px;
                color: #64748b;
                background: #f8fafc;
                border-radius: 12px;
                padding: 40px;
                border: 2px dashed #cbd5e1;
            }
        """)
        
        layout.addWidget(content)
        page.setLayout(layout)
        return page
        
    def create_logs_page(self) -> QWidget:
        """创建日志页面"""
        page = QWidget()
        layout = QVBoxLayout()
        
        content = QLabel("📝 日志记录模块\n\n这里将显示系统运行日志和历史记录")
        content.setObjectName("page_content")
        content.setAlignment(Qt.AlignCenter)
        content.setStyleSheet("""
            #page_content {
                font-size: 16px;
                color: #64748b;
                background: #f8fafc;
                border-radius: 12px;
                padding: 40px;
                border: 2px dashed #cbd5e1;
            }
        """)
        
        layout.addWidget(content)
        page.setLayout(layout)
        return page
        
    def create_settings_page(self) -> QWidget:
        """创建设置页面"""
        page = QWidget()
        layout = QVBoxLayout()
        
        content = QLabel("⚙️ 系统设置模块\n\n这里将显示系统配置和参数设置")
        content.setObjectName("page_content")
        content.setAlignment(Qt.AlignCenter)
        content.setStyleSheet("""
            #page_content {
                font-size: 16px;
                color: #64748b;
                background: #f8fafc;
                border-radius: 12px;
                padding: 40px;
                border: 2px dashed #cbd5e1;
            }
        """)
        
        layout.addWidget(content)
        page.setLayout(layout)
        return page
        
    def switch_page(self, module_id: str):
        """切换页面"""
        page_mapping = {
            "ai_chat": (0, "AI 对话助手", "与AI助手进行智能对话，获取测试建议和技术支持"),
            "test_cards": (1, "测试卡片管理", "管理和执行各种测试计划和任务"),
            "data_analysis": (2, "数据分析中心", "查看和分析测试数据，生成报告图表"),
            "device_control": (3, "设备控制台", "控制示波器和其他测试设备"),
            "timeline": (4, "时序图分析", "查看和分析时序数据的可视化图表"),
            "logs": (5, "日志记录中心", "查看系统运行日志和历史操作记录"),
            "settings": (6, "系统设置", "配置系统参数和个人偏好设置")
        }
        
        if module_id in page_mapping:
            page_index, title, subtitle = page_mapping[module_id]
            self.content_stack.setCurrentIndex(page_index)
            self.page_title.setText(title)
            self.page_subtitle.setText(subtitle)
            logger.info(f"切换到页面: {title}")
        
    def setup_style(self):
        """设置样式"""
        self.setStyleSheet("""
        /* 工作区主容器 */
        #work_area {
            background: white;
            border-radius: 0;
        }
        
        /* 工作区标题栏 */
        #work_header {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #ffffff, stop:1 #f8fafc);
            border-bottom: 1px solid #e2e8f0;
            border-radius: 12px;
        }
        
        #page_title {
            font-size: 24px;
            font-weight: bold;
            color: #1e293b;
        }
        
        #page_subtitle {
            font-size: 14px;
            color: #64748b;
        }
        
        #action_button {
            background: #f1f5f9;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 8px 16px;
            font-size: 13px;
            color: #475569;
        }
        
        #action_button:hover {
            background: #e2e8f0;
            border-color: #cbd5e1;
        }
        
        /* 内容堆栈 */
        #content_stack {
            background: transparent;
        }
        """)


class ModernInfoPanel(QFrame):
    """现代化信息面板"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_style()
        
    def setup_ui(self):
        """设置界面"""
        self.setObjectName("info_panel")
        self.setFixedWidth(320)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 30, 20, 30)
        layout.setSpacing(20)
        
        # 系统状态卡片
        status_card = self.create_status_card()
        layout.addWidget(status_card)
        
        # 任务列表卡片
        tasks_card = self.create_tasks_card()
        layout.addWidget(tasks_card)
        
        # 实时日志卡片
        logs_card = self.create_logs_card()
        layout.addWidget(logs_card)
        
        self.setLayout(layout)
        
    def create_status_card(self) -> QWidget:
        """创建系统状态卡片"""
        card = QFrame()
        card.setObjectName("info_card")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(15)
        
        # 卡片标题
        title = QLabel("系统状态")
        title.setObjectName("card_title")
        layout.addWidget(title)
        
        # 状态指标
        status_layout = QVBoxLayout()
        status_layout.setSpacing(10)
        
        # CPU使用率
        cpu_layout = QHBoxLayout()
        cpu_label = QLabel("CPU 使用率")
        cpu_label.setObjectName("status_label")
        cpu_progress = QProgressBar()
        cpu_progress.setObjectName("status_progress")
        cpu_progress.setValue(25)
        cpu_layout.addWidget(cpu_label)
        cpu_layout.addWidget(cpu_progress)
        status_layout.addLayout(cpu_layout)
        
        # 内存使用率
        memory_layout = QHBoxLayout()
        memory_label = QLabel("内存使用率")
        memory_label.setObjectName("status_label")
        memory_progress = QProgressBar()
        memory_progress.setObjectName("status_progress")
        memory_progress.setValue(45)
        memory_layout.addWidget(memory_label)
        memory_layout.addWidget(memory_progress)
        status_layout.addLayout(memory_layout)
        
        # 活跃任务数
        tasks_info = QLabel("活跃任务: 3")
        tasks_info.setObjectName("status_info")
        status_layout.addWidget(tasks_info)
        
        layout.addLayout(status_layout)
        card.setLayout(layout)
        
        return card
        
    def create_tasks_card(self) -> QWidget:
        """创建任务列表卡片"""
        card = QFrame()
        card.setObjectName("info_card")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(15)
        
        # 卡片标题
        title = QLabel("最近任务")
        title.setObjectName("card_title")
        layout.addWidget(title)
        
        # 任务列表
        tasks_list = QListWidget()
        tasks_list.setObjectName("tasks_list")
        
        # 添加示例任务
        task_items = [
            "I2C协议测试 - 进行中",
            "电源纹波测试 - 已完成",
            "SPI通信验证 - 排队中"
        ]
        
        for task in task_items:
            item = QListWidgetItem(task)
            tasks_list.addItem(item)
            
        layout.addWidget(tasks_list)
        card.setLayout(layout)
        
        return card
        
    def create_logs_card(self) -> QWidget:
        """创建实时日志卡片"""
        card = QFrame()
        card.setObjectName("info_card")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(15)
        
        # 卡片标题
        title = QLabel("实时日志")
        title.setObjectName("card_title")
        layout.addWidget(title)
        
        # 日志显示
        self.logs_display = QTextEdit()
        self.logs_display.setObjectName("logs_display")
        self.logs_display.setReadOnly(True)
        self.logs_display.setMaximumHeight(150)
        
        # 添加示例日志
        sample_logs = [
            "[INFO] 系统启动完成",
            "[INFO] AI Actor 已连接",
            "[INFO] 设备检测中...",
            "[SUCCESS] 示波器连接成功"
        ]
        
        for log in sample_logs:
            self.logs_display.append(log)
            
        layout.addWidget(self.logs_display)
        card.setLayout(layout)
        
        return card
        
    def setup_style(self):
        """设置样式"""
        self.setStyleSheet("""
        /* 信息面板主容器 */
        #info_panel {
            background: #f8fafc;
            border-left: 1px solid #e2e8f0;
        }
        
        /* 信息卡片 */
        #info_card {
            background: white;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            margin-bottom: 10px;
        }
        
        #card_title {
            font-size: 16px;
            font-weight: bold;
            color: #1e293b;
            margin-bottom: 10px;
        }
        
        #status_label {
            font-size: 12px;
            color: #64748b;
            min-width: 80px;
        }
        
        #status_progress {
            border: none;
            border-radius: 4px;
            background: #e2e8f0;
            height: 6px;
        }
        
        #status_progress::chunk {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #3b82f6, stop:1 #1d4ed8);
            border-radius: 4px;
        }
        
        #status_info {
            font-size: 13px;
            color: #475569;
            background: #f1f5f9;
            padding: 8px;
            border-radius: 6px;
        }
        
        #tasks_list {
            border: none;
            background: transparent;
            font-size: 12px;
        }
        
        #tasks_list::item {
            padding: 8px;
            border-bottom: 1px solid #f1f5f9;
            color: #475569;
        }
        
        #tasks_list::item:hover {
            background: #f1f5f9;
        }
        
        #logs_display {
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            background: #f8fafc;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 11px;
            color: #475569;
        }
        """)


class ModernMainWindow(QMainWindow):
    """
    现代化主界面窗口
    
    特色功能：
    - 现代化三栏布局设计
    - 模块化导航系统
    - 响应式工作区域
    - 实时信息面板
    - 主题切换支持
    """
    
    # 信号定义
    window_closed = Signal()
    module_changed = Signal(str)
    
    def __init__(self):
        super().__init__()
        
        # 初始化属性
        self.ai_actor_ref = None
        self.current_module = "ai_chat"
        
        self.setup_window()
        self.setup_ui()
        self.setup_connections()
        self.setup_style()
        
        logger.info("现代化主界面窗口初始化完成")
        
    def setup_window(self):
        """设置窗口属性"""
        self.setWindowTitle("Pank Ins - AI控制示波器系统")
        self.setMinimumSize(1400, 900)
        self.resize(1600, 1000)
        
        # 居中显示
        from PySide6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
        
    def setup_ui(self):
        """设置用户界面"""
        # 创建菜单栏
        self.create_menu_bar()
        
        # 创建状态栏
        self.create_status_bar()
        
        # 主工作区域
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 左侧边栏
        self.sidebar = ModernSidebar()
        main_layout.addWidget(self.sidebar)
        
        # 中间工作区
        self.work_area = ModernWorkArea()
        main_layout.addWidget(self.work_area)
        
        # 右侧信息面板
        self.info_panel = ModernInfoPanel()
        main_layout.addWidget(self.info_panel)
        
        central_widget.setLayout(main_layout)
        
    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件")
        file_menu.addAction("新建项目", self.new_project)
        file_menu.addAction("打开项目", self.open_project)
        file_menu.addSeparator()
        file_menu.addAction("退出", self.close)
        
        # 编辑菜单
        edit_menu = menubar.addMenu("编辑")
        edit_menu.addAction("设置", self.open_settings)
        
        # 视图菜单
        view_menu = menubar.addMenu("视图")
        view_menu.addAction("重置布局", self.reset_layout)
        
        # 工具菜单
        tools_menu = menubar.addMenu("工具")
        tools_menu.addAction("设备管理器", self.open_device_manager)
        tools_menu.addAction("插件管理器", self.open_plugin_manager)
        
        # 帮助菜单
        help_menu = menubar.addMenu("帮助")
        help_menu.addAction("关于", self.show_about)
        
    def create_status_bar(self):
        """创建状态栏"""
        status_bar = self.statusBar()
        status_bar.showMessage("就绪")
        
        # 右侧状态信息
        self.status_label = QLabel("AI Actor: 已连接")
        status_bar.addPermanentWidget(self.status_label)
        
    def setup_connections(self):
        """设置信号连接"""
        # 侧边栏模块选择
        self.sidebar.module_selected.connect(self.on_module_selected)
        
    def setup_style(self):
        """设置窗口样式"""
        self.setStyleSheet("""
        QMainWindow {
            background: #ffffff;
        }
        
        QMenuBar {
            background: #f8fafc;
            border-bottom: 1px solid #e2e8f0;
            font-size: 14px;
            padding: 5px;
        }
        
        QMenuBar::item {
            padding: 8px 12px;
            border-radius: 4px;
        }
        
        QMenuBar::item:selected {
            background: #e2e8f0;
        }
        
        QStatusBar {
            background: #f8fafc;
            border-top: 1px solid #e2e8f0;
            font-size: 12px;
        }
        """)
        
    @Slot(str)
    def on_module_selected(self, module_id: str):
        """模块选择处理"""
        self.current_module = module_id
        self.work_area.switch_page(module_id)
        self.module_changed.emit(module_id)
        
        # 更新状态栏
        module_names = {
            "ai_chat": "AI对话",
            "test_cards": "测试卡片",
            "data_analysis": "数据分析",
            "device_control": "设备控制",
            "timeline": "时序图",
            "logs": "日志记录",
            "settings": "系统设置"
        }
        
        module_name = module_names.get(module_id, "未知模块")
        self.statusBar().showMessage(f"当前模块: {module_name}")
        
    def set_ai_actor_ref(self, ai_actor_ref):
        """设置AI Actor引用"""
        self.ai_actor_ref = ai_actor_ref
        self.status_label.setText("AI Actor: 已连接")
        logger.info("AI Actor引用已设置")
        
    def closeEvent(self, event):
        """关闭事件"""
        self.window_closed.emit()
        event.accept()
        logger.info("现代化主界面窗口关闭")
        
    # 菜单动作槽函数
    def new_project(self):
        """新建项目"""
        logger.info("新建项目")
        
    def open_project(self):
        """打开项目"""
        logger.info("打开项目")
        
    def open_settings(self):
        """打开设置"""
        self.sidebar.select_module("settings")
        
    def reset_layout(self):
        """重置布局"""
        logger.info("重置布局")
        
    def open_device_manager(self):
        """打开设备管理器"""
        logger.info("打开设备管理器")
        
    def open_plugin_manager(self):
        """打开插件管理器"""
        logger.info("打开插件管理器")
        
    def show_about(self):
        """显示关于"""
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.about(self, "关于", "Pank Ins AI控制示波器系统\n版本 2.0.0")


def main():
    """测试函数"""
    import sys
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # 创建主窗口
    window = ModernMainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 