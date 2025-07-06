"""
JSON驱动的动态卡片渲染系统

支持通过JSON配置完全控制卡片的显示内容、样式、行为等
可以动态解析JSON并渲染对应的UI组件
"""

import json
from typing import Dict, List, Any, Optional
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QWidget, QProgressBar, QScrollArea, QGridLayout, QSizePolicy,
    QTextEdit, QSpacerItem
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QFont


class JsonDynamicCard(QFrame):
    """
    JSON驱动的动态卡片组件
    
    完全通过JSON配置控制卡片的显示内容和行为
    """
    
    # 信号定义
    card_clicked = Signal(dict)
    action_triggered = Signal(str, dict)  # 动作名称, 卡片数据
    content_changed = Signal(dict)
    
    def __init__(self, json_config: Dict[str, Any] = None):
        super().__init__()
        self.json_config = json_config or {}
        self.is_expanded = False
        self.dynamic_components = {}  # 存储动态组件引用
        
        if self.json_config:
            self.setup_from_json()
        
    def setup_from_json(self):
        """
        根据JSON配置设置卡片
        """
        # 解析基础配置
        self.card_id = self.json_config.get('id', 'unknown')
        self.card_type = self.json_config.get('type', 'default')
        
        # 设置卡片样式
        self.apply_card_style()
        
        # 创建布局
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(16, 16, 16, 16)
        self.main_layout.setSpacing(12)
        
        # 渲染内容区域
        self.render_content_sections()
        
        self.setLayout(self.main_layout)
        
        # 设置行为
        self.setup_behaviors()
        
    def apply_card_style(self):
        """
        应用卡片样式
        """
        style_config = self.json_config.get('style', {})
        
        # 基础样式
        background = style_config.get('background', '#ffffff')
        border = style_config.get('border', '2px solid #e2e8f0')
        border_radius = style_config.get('border_radius', 12)
        margin = style_config.get('margin', '8px 4px')
        
        # 悬停样式
        hover_config = style_config.get('hover', {})
        hover_border = hover_config.get('border', '2px solid #667eea')
        hover_background = hover_config.get('background', '#f7fafc')
        
        css_style = f"""
            JsonDynamicCard {{
                background: {background};
                border: {border};
                border-radius: {border_radius}px;
                margin: {margin};
            }}
            JsonDynamicCard:hover {{
                border: {hover_border};
                background: {hover_background};
            }}
        """
        
        self.setStyleSheet(css_style)
        self.setCursor(Qt.PointingHandCursor)
            
    def render_content_sections(self):
        """
        渲染内容区域
        """
        sections = self.json_config.get('content', [])
        
        for section_config in sections:
            section_widget = self.create_section(section_config)
            if section_widget:
                self.main_layout.addWidget(section_widget)
                
    def create_section(self, section_config: Dict) -> Optional[QWidget]:
        """
        创建单个内容区域
        """
        section_type = section_config.get('type')
        
        if section_type == 'header':
            return self.create_header_section(section_config)
        elif section_type == 'info_grid':
            return self.create_info_grid_section(section_config)
        elif section_type == 'progress':
            return self.create_progress_section(section_config)
        elif section_type == 'text':
            return self.create_text_section(section_config)
        elif section_type == 'actions':
            return self.create_actions_section(section_config)
        elif section_type == 'expandable':
            return self.create_expandable_section(section_config)
        elif section_type == 'custom_list':
            return self.create_custom_list_section(section_config)
        else:
            print(f"未知的区域类型: {section_type}")
            return None
            
    def create_header_section(self, config: Dict) -> QWidget:
        """
        创建头部区域
        """
        header_widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # 标题
        title_config = config.get('title', {})
        title_text = title_config.get('text', '无标题')
        title_label = QLabel(title_text)
        
        # 应用标题样式
        title_style = title_config.get('style', {})
        font_size = title_style.get('font_size', 12)
        color = title_style.get('color', '#2d3748')
        
        font = QFont("微软雅黑", font_size)
        font.setBold(True)
        title_label.setFont(font)
        title_label.setStyleSheet(f"color: {color};")
        title_label.setWordWrap(True)
            
        layout.addWidget(title_label)
        
        # 状态徽章
        if 'status' in config:
            status_widget = self.create_status_badge(config['status'])
            layout.addWidget(status_widget)
            
        # 图标
        if 'icon' in config:
            icon_widget = self.create_icon_widget(config['icon'])
            layout.addWidget(icon_widget)
            
        layout.addStretch()
        header_widget.setLayout(layout)
        return header_widget
        
    def create_status_badge(self, status_config: Dict) -> QWidget:
        """
        创建状态徽章
        """
        status_value = status_config.get('value', 'unknown')
        status_text = status_config.get('text', status_value)
        
        # 状态颜色映射
        status_colors = {
            'running': '#48bb78',
            'completed': '#38b2ac',
            'error': '#f56565',
            'planning': '#805ad5',
            'paused': '#ed8936'
        }
        
        color = status_colors.get(status_value, '#a0aec0')
        
        badge = QLabel(status_text)
        badge.setFont(QFont("微软雅黑", 9))
        badge.setAlignment(Qt.AlignCenter)
        badge.setStyleSheet(f"""
            QLabel {{
                background-color: {color};
                color: white;
                border-radius: 12px;
                padding: 4px 12px;
                font-weight: bold;
            }}
        """)
        
        # 存储引用用于动态更新
        badge_id = status_config.get('id', 'status_badge')
        self.dynamic_components[badge_id] = {
            'widget': badge,
            'type': 'status',
            'config': status_config
        }
        
        return badge
        
    def create_icon_widget(self, icon_config: Dict) -> QWidget:
        """
        创建图标组件
        """
        icon_text = icon_config.get('text', '📋')
        icon_label = QLabel(icon_text)
        icon_label.setFont(QFont("微软雅黑", icon_config.get('size', 16)))
        icon_label.setAlignment(Qt.AlignCenter)
        return icon_label
        
    def create_info_grid_section(self, config: Dict) -> QWidget:
        """
        创建信息网格区域
        """
        grid_widget = QWidget()
        layout = QGridLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(0, 0, 0, 0)
        
        items = config.get('items', [])
        columns = config.get('columns', 2)
        
        for i, item in enumerate(items):
            row = i // columns
            col = i % columns
            
            # 标签
            label_text = item.get('label', '')
            label = QLabel(f"{label_text}:")
            label.setFont(QFont("微软雅黑", 10, QFont.Bold))
            label.setStyleSheet("color: #4a5568;")
            
            # 值
            value_text = item.get('value', '')
            value = QLabel(str(value_text))
            value.setFont(QFont("微软雅黑", 10))
            value.setStyleSheet("color: #2d3748;")
            
            # 动态组件引用
            if 'id' in item:
                self.dynamic_components[item['id']] = {
                    'widget': value,
                    'type': 'text',
                    'config': item
                }
            
            layout.addWidget(label, row, col * 2)
            layout.addWidget(value, row, col * 2 + 1)
            
        grid_widget.setLayout(layout)
        
        # 应用网格样式
        grid_style = config.get('style', {})
        if grid_style:
            background = grid_style.get('background', '#f8fafc')
            border = grid_style.get('border', '1px solid #e2e8f0')
            border_radius = grid_style.get('border_radius', 8)
            padding = grid_style.get('padding', 15)
            
            grid_widget.setStyleSheet(f"""
                QWidget {{
                    background-color: {background};
                    border: {border};
                    border-radius: {border_radius}px;
                    padding: {padding}px;
                }}
            """)
            
        return grid_widget
        
    def create_progress_section(self, config: Dict) -> QWidget:
        """
        创建进度条区域
        """
        progress_widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # 进度文本
        if 'text' in config:
            progress_text = QLabel(config['text'])
            progress_text.setFont(QFont("微软雅黑", 9))
            progress_text.setStyleSheet("color: #6b7280;")
            layout.addWidget(progress_text)
            
        # 进度条
        progress_bar = QProgressBar()
        progress_bar.setFixedHeight(config.get('height', 6))
        progress_bar.setValue(config.get('value', 0))
        progress_bar.setMaximum(config.get('max', 100))
        
        # 进度条样式
        bar_color = config.get('color', '#3b82f6')
        progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                border-radius: 3px;
                background-color: #e5e7eb;
            }}
            QProgressBar::chunk {{
                background-color: {bar_color};
                border-radius: 3px;
            }}
        """)
        
        layout.addWidget(progress_bar)
        
        # 动态组件引用
        if 'id' in config:
            self.dynamic_components[config['id']] = {
                'widget': progress_bar,
                'type': 'progress',
                'config': config
            }
            
        progress_widget.setLayout(layout)
        return progress_widget
        
    def create_text_section(self, config: Dict) -> QWidget:
        """
        创建文本区域
        """
        text_content = config.get('content', '')
        
        if config.get('multiline', False):
            text_widget = QTextEdit()
            text_widget.setPlainText(text_content)
            text_widget.setReadOnly(True)
            text_widget.setFixedHeight(config.get('height', 80))
        else:
            text_widget = QLabel(text_content)
            text_widget.setWordWrap(config.get('word_wrap', True))
            
        # 应用文本样式
        style = config.get('style', {})
        font_size = style.get('font_size', 10)
        color = style.get('color', '#374151')
        
        font = QFont("微软雅黑", font_size)
        text_widget.setFont(font)
        text_widget.setStyleSheet(f"color: {color};")
        
        # 动态组件引用
        if 'id' in config:
            self.dynamic_components[config['id']] = {
                'widget': text_widget,
                'type': 'text',
                'config': config
            }
            
        return text_widget
        
    def create_actions_section(self, config: Dict) -> QWidget:
        """
        创建操作按钮区域
        """
        actions_widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        for action_config in config.get('buttons', []):
            button = self.create_action_button(action_config)
            layout.addWidget(button)
            
        # 添加弹性空间
        if config.get('align', 'left') == 'right':
            layout.insertStretch(0)
        elif config.get('align', 'left') == 'center':
            layout.insertStretch(0)
            layout.addStretch()
            
        actions_widget.setLayout(layout)
        return actions_widget
        
    def create_action_button(self, action_config: Dict) -> QPushButton:
        """
        创建操作按钮
        """
        button_text = action_config.get('text', '按钮')
        button = QPushButton(button_text)
        
        # 按钮样式
        button_type = action_config.get('style', 'primary')
        
        # 预定义按钮样式
        button_styles = {
            'primary': {'bg': '#3b82f6', 'hover': '#2563eb'},
            'secondary': {'bg': '#6b7280', 'hover': '#4b5563'},
            'success': {'bg': '#10b981', 'hover': '#059669'},
            'warning': {'bg': '#f59e0b', 'hover': '#d97706'},
            'danger': {'bg': '#ef4444', 'hover': '#dc2626'}
        }
        
        style = button_styles.get(button_type, button_styles['primary'])
        
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {style['bg']};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {style['hover']};
            }}
        """)
        
        # 连接点击事件
        action_name = action_config.get('action', 'unknown')
        button.clicked.connect(lambda: self.action_triggered.emit(action_name, self.json_config))
        
        return button
        
    def create_expandable_section(self, config: Dict) -> QWidget:
        """
        创建可展开区域
        """
        expandable_widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # 展开/收起按钮
        toggle_button = QPushButton(config.get('toggle_text', '▼ 展开详情'))
        toggle_button.clicked.connect(lambda: self.toggle_expandable_section(config['id']))
        layout.addWidget(toggle_button)
        
        # 可展开内容
        content_widget = QWidget()
        content_layout = QVBoxLayout()
        
        for section_config in config.get('content', []):
            section_widget = self.create_section(section_config)
            if section_widget:
                content_layout.addWidget(section_widget)
                
        content_widget.setLayout(content_layout)
        content_widget.hide()  # 初始隐藏
        
        layout.addWidget(content_widget)
        expandable_widget.setLayout(layout)
        
        # 存储引用
        self.dynamic_components[config['id']] = {
            'widget': content_widget,
            'button': toggle_button,
            'type': 'expandable',
            'config': config,
            'expanded': False
        }
        
        return expandable_widget
        
    def create_custom_list_section(self, config: Dict) -> QWidget:
        """
        创建自定义列表区域
        """
        list_widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # 列表标题
        if 'title' in config:
            title_label = QLabel(config['title'])
            title_label.setFont(QFont("微软雅黑", 10, QFont.Bold))
            title_label.setStyleSheet("color: #374151;")
            layout.addWidget(title_label)
            
        # 列表项
        for item_config in config.get('items', []):
            item_widget = self.create_list_item(item_config)
            layout.addWidget(item_widget)
            
        list_widget.setLayout(layout)
        return list_widget
        
    def create_list_item(self, item_config: Dict) -> QWidget:
        """
        创建列表项
        """
        item_widget = QFrame()
        layout = QHBoxLayout()
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(12)
        
        # 图标
        if 'icon' in item_config:
            icon_label = QLabel(item_config['icon'])
            icon_label.setFixedSize(20, 20)
            icon_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(icon_label)
            
        # 文本内容
        text_content = item_config.get('text', '')
        text_label = QLabel(text_content)
        text_label.setWordWrap(True)
        layout.addWidget(text_label)
        
        # 状态指示器
        if 'status' in item_config:
            status_text = item_config['status']
            status_label = QLabel(status_text)
            status_label.setStyleSheet("color: #6b7280; font-size: 9px;")
            layout.addWidget(status_label)
            
        layout.addStretch()
        item_widget.setLayout(layout)
        
        # 项目样式
        item_widget.setStyleSheet("""
            QFrame {
                background-color: #f9fafb;
                border: 1px solid #e5e7eb;
                border-radius: 6px;
            }
        """)
        
        return item_widget
        
    def setup_behaviors(self):
        """
        设置卡片行为
        """
        behaviors = self.json_config.get('behaviors', {})
        
        # 点击行为
        if behaviors.get('clickable', True):
            self.mousePressEvent = self.handle_card_click
            
    def handle_card_click(self, event):
        """
        处理卡片点击
        """
        if event.button() == Qt.LeftButton:
            self.card_clicked.emit(self.json_config)
            
    @Slot(str)
    def toggle_expandable_section(self, section_id: str):
        """
        切换可展开区域状态
        """
        if section_id in self.dynamic_components:
            component = self.dynamic_components[section_id]
            widget = component['widget']
            button = component['button']
            expanded = component['expanded']
            
            if expanded:
                widget.hide()
                button.setText(component['config'].get('toggle_text', '▼ 展开详情'))
                component['expanded'] = False
            else:
                widget.show()
                button.setText(component['config'].get('collapse_text', '▲ 收起详情'))
                component['expanded'] = True
                
    def update_from_json(self, new_config: Dict[str, Any]):
        """
        根据新的JSON配置更新卡片
        """
        self.json_config.update(new_config)
        
        # 更新动态组件
        updates = new_config.get('updates', {})
        for component_id, update_data in updates.items():
            if component_id in self.dynamic_components:
                self.update_component(component_id, update_data)
                
        # 发送内容变化信号
        self.content_changed.emit(self.json_config)
        
    def update_component(self, component_id: str, update_data: Dict):
        """
        更新特定组件
        """
        component = self.dynamic_components[component_id]
        widget = component['widget']
        component_type = component['type']
        
        if component_type == 'text':
            new_text = update_data.get('text', update_data.get('value', ''))
            if hasattr(widget, 'setText'):
                widget.setText(str(new_text))
            elif hasattr(widget, 'setPlainText'):
                widget.setPlainText(str(new_text))
                
        elif component_type == 'progress':
            if 'value' in update_data:
                widget.setValue(update_data['value'])
            if 'max' in update_data:
                widget.setMaximum(update_data['max'])
                
        elif component_type == 'status':
            if 'text' in update_data:
                widget.setText(update_data['text'])
            if 'color' in update_data:
                current_style = widget.styleSheet()
                new_style = current_style.replace(
                    widget.styleSheet().split('background-color: ')[1].split(';')[0],
                    update_data['color']
                )
                widget.setStyleSheet(new_style)

    def get_current_progress(self):
        """
        获取当前进度值
        """
        for component_id, component in self.dynamic_components.items():
            if component['type'] == 'progress':
                return component['widget'].value()
        return 0


class JsonCardContainer(QFrame):
    """
    JSON卡片容器
    
    管理多个JSON驱动的卡片
    """
    
    card_selected = Signal(dict)
    action_requested = Signal(str, dict)
    
    def __init__(self):
        super().__init__()
        self.cards = {}  # 存储卡片引用
        self.setup_ui()
        
    def setup_ui(self):
        """
        设置容器界面
        """
        # 滚动区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # 卡片容器
        self.cards_widget = QWidget()
        self.cards_layout = QVBoxLayout()
        self.cards_layout.setContentsMargins(8, 8, 8, 8)
        self.cards_layout.setSpacing(12)
        self.cards_layout.addStretch()  # 底部弹性空间
        
        self.cards_widget.setLayout(self.cards_layout)
        self.scroll_area.setWidget(self.cards_widget)
        
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.scroll_area)
        
        self.setLayout(main_layout)
        
    def load_cards_from_json(self, json_data: Any):
        """
        从JSON数据加载卡片
        """
        try:
            # 处理不同格式的JSON数据
            if isinstance(json_data, str):
                data = json.loads(json_data)
            else:
                data = json_data
                
            # 清除现有卡片
            self.clear_all_cards()
            
            # 解析卡片数据
            cards_data = []
            if isinstance(data, list):
                cards_data = data
            elif isinstance(data, dict):
                if 'cards' in data:
                    cards_data = data['cards']
                elif 'processes' in data:
                    cards_data = data['processes']
                else:
                    cards_data = [data]  # 单个卡片
                    
            # 创建卡片
            for card_config in cards_data:
                self.add_card_from_json(card_config)
                
        except Exception as e:
            print(f"加载JSON卡片数据失败: {e}")
            
    def add_card_from_json(self, card_config: Dict[str, Any]):
        """
        从JSON配置添加新卡片
        """
        card = JsonDynamicCard(card_config)
        card.card_clicked.connect(self.card_selected.emit)
        card.action_triggered.connect(self.action_requested.emit)
        
        # 插入到底部弹性空间之前
        self.cards_layout.insertWidget(self.cards_layout.count() - 1, card)
        
        # 存储卡片引用
        card_id = card_config.get('id', f'card_{len(self.cards)}')
        self.cards[card_id] = card
        
    def update_card(self, card_id: str, update_config: Dict[str, Any]):
        """
        更新指定卡片
        """
        if card_id in self.cards:
            self.cards[card_id].update_from_json(update_config)
            
    def remove_card(self, card_id: str):
        """
        移除指定卡片
        """
        if card_id in self.cards:
            card = self.cards[card_id]
            card.setParent(None)
            card.deleteLater()
            del self.cards[card_id]
            
    def clear_all_cards(self):
        """
        清除所有卡片
        """
        for card_id in list(self.cards.keys()):
            self.remove_card(card_id)
            
    def get_card_count(self) -> int:
        """
        获取卡片数量
        """
        return len(self.cards)
        
    def get_all_cards(self) -> Dict[str, JsonDynamicCard]:
        """
        获取所有卡片
        """
        return self.cards.copy() 