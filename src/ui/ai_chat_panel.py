"""
AI对话面板组件

提供与AI助手的对话界面，支持消息发送、接收和显示，支持Markdown格式
"""

from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, 
    QLineEdit, QPushButton, QScrollArea, QWidget, QPlainTextEdit
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QTextCursor, QKeySequence
from datetime import datetime
import markdown


class MessageWidget(QFrame):
    """
    单条消息组件，支持Markdown渲染
    """
    
    def __init__(self, message, is_user=True, timestamp=None):
        super().__init__()
        self.message = message
        self.is_user = is_user
        self.timestamp = timestamp or datetime.now()
        self.setup_ui()
        
    def setup_ui(self):
        """
        设置消息界面
        """
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(5)
        
        # 消息头部（时间和发送者）
        header_layout = QHBoxLayout()
        
        sender_label = QLabel("您" if self.is_user else "AI助手")
        sender_label.setFont(QFont("微软雅黑", 9, QFont.Bold))
        sender_label.setStyleSheet(f"""
            QLabel {{
                color: {'#667eea' if self.is_user else '#48bb78'};
                padding: 2px 0;
            }}
        """)
        
        time_label = QLabel(self.timestamp.strftime("%H:%M:%S"))
        time_label.setFont(QFont("微软雅黑", 8))
        time_label.setStyleSheet("color: #a0aec0;")
        
        if self.is_user:
            header_layout.addStretch()
            header_layout.addWidget(time_label)
            header_layout.addWidget(sender_label)
        else:
            header_layout.addWidget(sender_label)
            header_layout.addWidget(time_label)
            header_layout.addStretch()
            
        layout.addLayout(header_layout)
        
        # 消息内容 - 支持Markdown和文本选择
        if self.is_user:
            # 用户消息使用QLabel，支持文本选择
            message_label = QLabel(self.message)
            message_label.setWordWrap(True)
            message_label.setFont(QFont("微软雅黑", 10))
            message_label.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
            message_label.setStyleSheet("""
                QLabel {
                    background-color: #667eea;
                    color: white;
                    padding: 12px 16px;
                    border-radius: 18px;
                    border-bottom-right-radius: 4px;
                    max-width: 300px;
                }
                QLabel::selection {
                    background-color: rgba(255, 255, 255, 0.3);
                }
            """)
            message_label.setAlignment(Qt.AlignRight)
        else:
            # AI消息使用QLabel支持HTML渲染和文本选择
            message_label = QLabel()
            message_label.setWordWrap(True)
            message_label.setFont(QFont("微软雅黑", 10))
            message_label.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
            
            # 将Markdown转换为HTML
            html_content = markdown.markdown(self.message, extensions=['codehilite', 'fenced_code', 'tables'])
            message_label.setText(html_content)
            message_label.setTextFormat(Qt.RichText)
            
            # 设置样式
            message_label.setStyleSheet("""
                QLabel {
                    background-color: #f7fafc;
                    color: #2d3748;
                    padding: 12px 16px;
                    border-radius: 18px;
                    border-bottom-left-radius: 4px;
                    border: 1px solid #e2e8f0;
                    max-width: 350px;
                }
                QLabel::selection {
                    background-color: #667eea;
                    color: white;
                }
            """)
            message_label.setAlignment(Qt.AlignLeft)
            
        # 消息对齐
        message_layout = QHBoxLayout()
        if self.is_user:
            message_layout.addStretch()
            message_layout.addWidget(message_label)
        else:
            message_layout.addWidget(message_label)
            message_layout.addStretch()
            
        layout.addLayout(message_layout)
        self.setLayout(layout)


class AIChatPanel(QFrame):
    """
    AI对话面板组件
    
    提供完整的AI对话界面，支持Markdown格式
    """
    
    # 定义信号
    message_sent = Signal(str)  # 消息发送信号
    
    def __init__(self):
        super().__init__()
        self.messages = []  # 存储消息历史
        self.setup_ui()
        self.add_welcome_message()
        
    def setup_ui(self):
        """
        设置AI对话面板界面
        """
        self.setFrameStyle(QFrame.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-left: 1px solid #e2e8f0;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 标题栏（简化版，移除状态）
        self.create_header(layout)
        
        # 消息显示区域
        self.create_message_area(layout)
        
        # 输入区域
        self.create_input_area(layout)
        
        self.setLayout(layout)
        
    def create_header(self, parent_layout):
        """
        创建简化的标题栏
        
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
        
        # AI助手标题
        title = QLabel("🤖 AI智能助手")
        title.setFont(QFont("微软雅黑", 14, QFont.Bold))
        title.setStyleSheet("color: white;")
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        header.setLayout(header_layout)
        parent_layout.addWidget(header)
        
    def create_message_area(self, parent_layout):
        """
        创建消息显示区域
        
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
                background-color: #fafafa;
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
        
        # 消息容器
        self.message_container = QWidget()
        self.message_layout = QVBoxLayout()
        self.message_layout.setContentsMargins(10, 10, 10, 10)
        self.message_layout.setSpacing(10)
        self.message_layout.addStretch()  # 添加弹性空间，使消息从底部开始
        
        self.message_container.setLayout(self.message_layout)
        self.scroll_area.setWidget(self.message_container)
        
        parent_layout.addWidget(self.scroll_area)
        
    def create_input_area(self, parent_layout):
        """
        创建输入区域，支持多行输入
        
        Args:
            parent_layout: 父布局
        """
        input_frame = QFrame()
        input_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-top: 1px solid #e2e8f0;
            }
        """)
        input_frame.setFixedHeight(120)  # 增加高度以容纳多行输入
        
        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(15, 15, 15, 15)
        input_layout.setSpacing(10)
        
        # 多行输入框
        self.input_field = QPlainTextEdit()
        self.input_field.setPlaceholderText("输入您的问题...\n(Ctrl+Enter 发送，Enter 换行)")
        self.input_field.setFont(QFont("微软雅黑", 11))
        self.input_field.setMaximumHeight(80)
        self.input_field.setStyleSheet("""
            QPlainTextEdit {
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                padding: 10px 15px;
                background-color: #f8fafc;
                font-size: 11px;
                line-height: 1.4;
            }
            QPlainTextEdit:focus {
                border-color: #667eea;
                background-color: white;
            }
        """)
        
        # 连接键盘事件
        self.input_field.keyPressEvent = self.handle_key_press
        
        # 发送按钮
        self.send_button = QPushButton("发送")
        self.send_button.setFont(QFont("微软雅黑", 10, QFont.Bold))
        self.send_button.setFixedSize(70, 50)
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #667eea;
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #5a67d8;
            }
            QPushButton:pressed {
                background-color: #4c51bf;
            }
            QPushButton:disabled {
                background-color: #a0aec0;
            }
        """)
        
        # 连接信号
        self.send_button.clicked.connect(self.send_message)
        
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_button)
        
        input_frame.setLayout(input_layout)
        parent_layout.addWidget(input_frame)
        
    def handle_key_press(self, event):
        """
        处理键盘按键事件
        
        Args:
            event: 键盘事件
        """
        # Ctrl+Enter 发送消息
        if event.key() == Qt.Key_Return and event.modifiers() == Qt.ControlModifier:
            self.send_message()
        # Enter 换行（默认行为）
        else:
            QPlainTextEdit.keyPressEvent(self.input_field, event)
        
    def add_welcome_message(self):
        """
        添加欢迎消息，使用Markdown格式
        """
        welcome_text = """您好！我是AI智能助手，可以帮助您：

## 主要功能
- **控制示波器设备** - 远程操作和配置
- **分析波形数据** - 智能数据处理
- **解答技术问题** - 专业技术支持  
- **生成测试报告** - 自动化报告生成

### 支持格式
我支持 **Markdown** 格式显示，包括：
- `代码块`
- **粗体文字**
- *斜体文字*
- 列表和表格

### 使用提示
- **Enter** 键换行
- **Ctrl+Enter** 发送消息
- 可以**选中复制**对话内容

请告诉我您需要什么帮助？"""
        self.add_message(welcome_text, is_user=False)
        
    def add_message(self, message, is_user=True):
        """
        添加消息到对话中
        
        Args:
            message (str): 消息内容
            is_user (bool): 是否为用户消息
        """
        # 创建消息组件
        message_widget = MessageWidget(message, is_user)
        
        # 插入到消息布局中（在弹性空间之前）
        self.message_layout.insertWidget(self.message_layout.count() - 1, message_widget)
        
        # 滚动到底部 - 确保始终显示最新消息
        QTimer.singleShot(50, self.scroll_to_bottom)
        
        # 存储消息
        self.messages.append({
            'message': message,
            'is_user': is_user,
            'timestamp': datetime.now()
        })
        
    def scroll_to_bottom(self):
        """
        滚动到底部 - 确保始终显示最新消息
        """
        scrollbar = self.scroll_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
    def send_message(self):
        """
        发送消息
        """
        message = self.input_field.toPlainText().strip()
        if not message:
            return
            
        # 添加用户消息
        self.add_message(message, is_user=True)
        
        # 清空输入框
        self.input_field.clear()
        
        # 发送信号
        self.message_sent.emit(message)
        
        # 模拟AI回复（延迟1秒）
        QTimer.singleShot(1000, lambda: self.simulate_ai_response(message))
        
    def simulate_ai_response(self, user_message):
        """
        模拟AI回复，支持Markdown格式
        
        Args:
            user_message (str): 用户消息
        """
        # 增强的回复逻辑，支持Markdown
        responses = {
            "你好": """您好！很高兴为您服务。

## 我可以帮助您：
- 🔧 **设备控制** - 示波器操作和配置
- 📊 **数据分析** - 波形数据处理
- 🛠️ **技术支持** - 专业问题解答
- 📋 **报告生成** - 自动化测试报告

有什么可以帮助您的吗？""",
            
            "示波器": """## 示波器控制功能

我可以帮助您进行以下操作：

### 基本控制
- **连接设备** - 建立通信连接
- **参数设置** - 配置采样率、触发等
- **数据采集** - 实时波形捕获

### 高级功能  
- **自动测量** - 频率、幅值、相位等
- **波形分析** - FFT、滤波、统计分析
- **数据导出** - 支持多种格式

请告诉我您需要进行什么具体操作？""",
            
            "测试": """## 测试功能说明

### 支持的测试类型：
1. **信号完整性测试**
   - 上升时间测量
   - 过冲/下冲分析
   - 眼图测试

2. **频域分析**
   - 频谱分析
   - 谐波失真测试
   - 噪声分析

3. **自动化测试**
   ```python
   # 示例代码
   def run_test():
       scope.connect()
       scope.set_trigger()
       data = scope.capture()
       return analyze(data)
   ```

请描述您的具体测试需求。""",
            
            "帮助": """# AI助手帮助文档

## 🚀 快速开始
我是您的专业AI助手，专门为示波器控制和测试而设计。

## 📋 主要功能

### 设备控制
- **连接管理** - 自动检测和连接设备
- **参数配置** - 智能参数推荐
- **实时监控** - 设备状态实时显示

### 数据分析  
- **波形处理** - 滤波、平滑、去噪
- **测量计算** - 自动测量各种参数
- **统计分析** - 数据统计和趋势分析

### 报告生成
- **自动报告** - 一键生成测试报告
- **图表生成** - 专业图表和波形图
- **数据导出** - 支持Excel、PDF等格式

## 💡 使用技巧
- 使用 **关键词** 快速获取帮助
- 支持 `代码块` 和 **格式化文本**
- 可以询问具体的技术问题
- **选中文本** 可以复制内容

## ⌨️ 快捷键
- **Enter** - 换行
- **Ctrl+Enter** - 发送消息
- **鼠标选择** - 选中复制文本

有任何问题都可以随时询问我！"""
        }
        
        # 查找匹配的回复
        ai_response = None
        for keyword, response in responses.items():
            if keyword in user_message:
                ai_response = response
                break
                
        if not ai_response:
            ai_response = f"""我理解您说的是：「**{user_message}**」

## 🤔 需要更多信息
我正在学习如何更好地回答这个问题。

### 建议：
- 请您 **详细描述** 具体需求
- 可以使用 `关键词` 如：示波器、测试、帮助等
- 我会根据您的问题提供 **专业建议**

### 常用功能：
- 设备控制和配置
- 数据分析和处理  
- 测试流程指导
- 技术问题解答

### 💡 提示
您可以**选中并复制**这些文字内容，也可以使用**多行输入**发送长文本。

我会尽力帮助您！"""
            
        # 添加AI回复
        self.add_message(ai_response, is_user=False)
        
    def clear_chat(self):
        """
        清空聊天记录
        """
        # 清除所有消息组件
        while self.message_layout.count() > 1:  # 保留弹性空间
            child = self.message_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        # 清空消息历史
        self.messages.clear()
        
        # 重新添加欢迎消息
        self.add_welcome_message()
        
    def get_chat_history(self):
        """
        获取聊天历史
        
        Returns:
            list: 聊天历史列表
        """
        return self.messages.copy() 