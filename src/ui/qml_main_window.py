#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
QML主窗口模块

基于PySide6 + QML技术栈实现现代化界面
- 4个主要区域：左侧树状图、中间工作区、下面log区、右边AI对话区
- Material Design 3 + Fluent Design融合风格
- 支持流式响应和缓冲系统
- 与UIActor集成，支持Actor间通信

@author: PankIns Team
@version: 1.0.0
"""

import os
import sys
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QMessageBox
from PySide6.QtCore import (
    QObject, Signal, Slot, QTimer, QUrl, QPropertyAnimation, 
    QEasingCurve, QParallelAnimationGroup, Qt, QThread, QMutex
)
from PySide6.QtGui import QGuiApplication, QIcon, QFont
from PySide6.QtQml import QmlElement, qmlRegisterType
from PySide6.QtQuick import QQuickView, QQuickItem
from PySide6.QtQuickWidgets import QQuickWidget
import pykka

logger = logging.getLogger(__name__)

# QML类型注册
QML_IMPORT_NAME = "PankIns.UI"
QML_IMPORT_MAJOR_VERSION = 1


@QmlElement
class QMLMainWindowBridge(QObject):
    """
    QML主窗口桥接器
    
    负责Python后端与QML前端的通信
    """
    
    # 信号定义
    messageReceived = Signal(str)
    streamStarted = Signal()
    streamChunkReceived = Signal(str)
    streamFinished = Signal()
    logMessageReceived = Signal(str, str)  # level, message
    planCardUpdated = Signal(str)  # JSON data
    taskCardUpdated = Signal(str)  # JSON data
    
    # 用户交互信号
    userMessageSent = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ai_actor_ref = None
        self.ui_actor_ref = None
        self.logger = logging.getLogger(__name__)
        
        # 流式响应状态
        self.stream_buffer = ""
        self.is_streaming = False
        
        # 缓冲系统
        self.plan_buffer = {}
        self.task_buffer = {}
        
        # 连接用户输入信号
        self.userMessageSent.connect(self.handle_user_message)
        
    def set_ai_actor_ref(self, ai_actor_ref):
        """设置AI Actor引用"""
        self.ai_actor_ref = ai_actor_ref
        self.logger.info("QML Bridge: AI Actor引用已设置")
        
    def set_ui_actor_ref(self, ui_actor_ref):
        """设置UI Actor引用"""
        self.ui_actor_ref = ui_actor_ref
        self.logger.info("QML Bridge: UI Actor引用已设置")
        
    @Slot(str)
    def handle_user_message(self, message: str):
        """
        处理用户消息输入
        
        Args:
            message (str): 用户输入的消息
        """
        try:
            self.logger.info(f"QML Bridge: 收到用户消息: {message}")
            
            # 通过UI Actor转发消息给AI Actor
            if self.ui_actor_ref:
                # 发送异步消息，不等待响应
                self.ui_actor_ref.tell({
                    'action': 'forward_to_actor',
                    'target_actor': 'ai',
                    'message': {
                        'action': 'process_message_stream',
                        'message': message,
                        'container_id': 'main_chat'
                    },
                    'wait_response': False
                })
            else:
                self.logger.error("QML Bridge: UI Actor引用未设置")
                
        except Exception as e:
            self.logger.error(f"QML Bridge: 处理用户消息失败: {e}")
    
    @Slot(str, str)
    def add_log(self, level: str, message: str):
        """
        添加日志消息
        
        Args:
            level (str): 日志级别
            message (str): 日志消息
        """
        self.logMessageReceived.emit(level, message)
    
    # 流式响应方法
    @Slot()
    def start_stream_response(self):
        """开始流式响应"""
        self.is_streaming = True
        self.stream_buffer = ""
        self.streamStarted.emit()
        
    @Slot(str)
    def append_stream_chunk(self, chunk: str):
        """追加流式响应片段"""
        if self.is_streaming:
            self.stream_buffer += chunk
            self.streamChunkReceived.emit(chunk)
            
    @Slot()
    def finish_stream_response(self):
        """完成流式响应"""
        self.is_streaming = False
        self.streamFinished.emit()
        
    # 缓冲系统方法
    def update_plan_buffer(self, plan_data: Dict[str, Any]):
        """更新计划缓冲区"""
        plan_id = plan_data.get('计划名', 'unknown')
        self.plan_buffer[plan_id] = plan_data
        self.planCardUpdated.emit(str(plan_data))
        
    def update_task_buffer(self, task_data: Dict[str, Any]):
        """更新任务缓冲区"""
        task_id = task_data.get('任务名', 'unknown')
        self.task_buffer[task_id] = task_data
        self.taskCardUpdated.emit(str(task_data))
        
    @Slot(result=str)
    def get_plan_cards(self) -> str:
        """获取计划卡片数据"""
        import json
        return json.dumps(list(self.plan_buffer.values()))
        
    @Slot(result=str)
    def get_task_cards(self) -> str:
        """获取任务卡片数据"""
        import json
        return json.dumps(list(self.task_buffer.values()))


class QMLMainWindow(QWidget):
    """
    QML主窗口类
    
    使用QQuickWidget嵌入QML内容，解决双窗口问题
    """
    
    # 信号定义
    window_closed = Signal()
    
    def __init__(self):
        super().__init__()
        self.qml_widget = None
        self.qml_bridge = None
        self.ai_actor_ref = None
        self.ui_actor_ref = None
        self.logger = logging.getLogger(__name__)
        self.setup_window()
        self.setup_qml_widget()
        
    def setup_window(self):
        """设置窗口属性"""
        self.setWindowTitle("Pank Ins - AI控制示波器系统")
        self.setWindowIcon(QIcon(":/icons/app_icon.png"))
        
        # 设置窗口大小和位置
        self.resize(1400, 900)
        self.setMinimumSize(1200, 800)
        
        # 窗口居中
        screen = QGuiApplication.primaryScreen()
        screen_geometry = screen.geometry()
        window_geometry = self.frameGeometry()
        window_geometry.moveCenter(screen_geometry.center())
        self.move(window_geometry.topLeft())
        
        # 设置窗口布局
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        
    def setup_qml_widget(self):
        """设置QML嵌入组件"""
        try:
            # 创建QML桥接器
            self.qml_bridge = QMLMainWindowBridge()
            
            # 注册QML类型
            qmlRegisterType(QMLMainWindowBridge, QML_IMPORT_NAME, QML_IMPORT_MAJOR_VERSION, 0, "MainWindowBridge")
            
            # 创建QQuickWidget
            self.qml_widget = QQuickWidget()
            self.qml_widget.setResizeMode(QQuickWidget.SizeRootObjectToView)
            
            # 设置QML上下文属性
            self.qml_widget.rootContext().setContextProperty("mainWindowBridge", self.qml_bridge)
            
            # 设置QML导入路径
            qml_dir = Path(__file__).parent / "qml"
            self.qml_widget.engine().addImportPath(str(qml_dir))
            
            # 创建主QML文件
            qml_file = qml_dir / "MainWindow.qml"
            if not qml_file.exists():
                self.create_modular_qml_file(qml_file)
            
            # 加载QML文件
            self.qml_widget.setSource(QUrl.fromLocalFile(str(qml_file)))
            
            # 检查是否加载成功
            if self.qml_widget.status() == QQuickWidget.Error:
                self.logger.error("QML加载失败")
                errors = self.qml_widget.errors()
                for error in errors:
                    self.logger.error(f"QML错误: {error.toString()}")
                # 创建备用界面
                self.create_fallback_ui()
            else:
                # 将QML widget添加到布局
                self.layout().addWidget(self.qml_widget)
                self.logger.info("QML界面加载成功")
                
        except Exception as e:
            self.logger.error(f"QML组件设置失败: {e}")
            # 创建备用界面
            self.create_fallback_ui()
            
    def create_modular_qml_file(self, qml_file: Path):
        """创建模块化的QML文件"""
        qml_file.parent.mkdir(parents=True, exist_ok=True)
        
        qml_content = '''
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Controls.Material 2.15
import "."

Rectangle {
    id: mainWindow
    
    Material.theme: Material.Dark
    Material.accent: Material.Blue
    
    color: Material.color(Material.Grey, Material.Shade950)
    
    // 主布局
    RowLayout {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 10
        
        // 左侧：工作流程树状图
        WorkflowTreeView {
            id: workflowTree
            Layout.fillHeight: true
            Layout.preferredWidth: 300
            Layout.minimumWidth: 250
            
            onItemClicked: function(itemData) {
                console.log("工作流项目点击:", itemData.name)
            }
            
            onItemDoubleClicked: function(itemData) {
                console.log("工作流项目双击:", itemData.name)
            }
        }
        
        // 中间：主工作区域
        ColumnLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 10
            
            // 上部分：主工作区
            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                color: Material.color(Material.Grey, Material.Shade900)
                radius: 8
                
                Column {
                    anchors.fill: parent
                    anchors.margins: 10
                    spacing: 10
                    
                    Label {
                        text: "主工作区域"
                        font.pixelSize: 18
                        font.bold: true
                        color: Material.color(Material.Blue)
                    }
                    
                    TabBar {
                        id: workAreaTabBar
                        width: parent.width
                        
                        TabButton {
                            text: "任务卡片"
                        }
                        TabButton {
                            text: "数据可视化"
                        }
                        TabButton {
                            text: "测试结果"
                        }
                    }
                    
                    StackLayout {
                        width: parent.width
                        height: parent.height - 80
                        currentIndex: workAreaTabBar.currentIndex
                        
                        // 任务卡片页面
                        Rectangle {
                            color: "transparent"
                            Label {
                                anchors.centerIn: parent
                                text: "任务卡片区域\\n(开发中)"
                                horizontalAlignment: Text.AlignHCenter
                                color: Material.color(Material.Grey)
                            }
                        }
                        
                        // 数据可视化页面
                        Rectangle {
                            color: "transparent"
                            Label {
                                anchors.centerIn: parent
                                text: "数据可视化区域\\n(开发中)"
                                horizontalAlignment: Text.AlignHCenter
                                color: Material.color(Material.Grey)
                            }
                        }
                        
                        // 测试结果页面
                        Rectangle {
                            color: "transparent"
                            Label {
                                anchors.centerIn: parent
                                text: "测试结果区域\\n(开发中)"
                                horizontalAlignment: Text.AlignHCenter
                                color: Material.color(Material.Grey)
                            }
                        }
                    }
                }
            }
            
            // 下部分：日志显示区
            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 200
                Layout.minimumHeight: 150
                color: Material.color(Material.Grey, Material.Shade900)
                radius: 8
                
                Column {
                    anchors.fill: parent
                    anchors.margins: 10
                    spacing: 10
                    
                    Label {
                        text: "系统日志"
                        font.pixelSize: 16
                        font.bold: true
                        color: Material.color(Material.Blue)
                    }
                    
                    ScrollView {
                        width: parent.width
                        height: parent.height - 40
                        
                        TextArea {
                            id: logArea
                            readOnly: true
                            wrapMode: TextArea.Wrap
                            color: Material.color(Material.Green)
                            font.family: "Consolas, Monaco, monospace"
                            font.pixelSize: 12
                            
                            // 连接到日志信号
                            Connections {
                                target: mainWindowBridge
                                function onLogMessageReceived(level, message) {
                                    var timestamp = new Date().toLocaleTimeString()
                                    logArea.append("[" + timestamp + "] " + level + ": " + message)
                                }
                            }
                        }
                    }
                }
            }
        }
        
        // 右侧：AI对话区域
        AIChatPanel {
            id: aiChatPanel
            Layout.fillHeight: true
            Layout.preferredWidth: 400
            Layout.minimumWidth: 350
            
            onMessageSent: function(message) {
                console.log("用户发送消息:", message)
                mainWindowBridge.userMessageSent(message)
            }
            
            // 连接流式响应信号
            Connections {
                target: mainWindowBridge
                function onStreamStarted() {
                    aiChatPanel.startStreamResponse()
                }
                function onStreamChunkReceived(chunk) {
                    aiChatPanel.appendStreamChunk(chunk)
                }
                function onStreamFinished() {
                    aiChatPanel.finishStreamResponse()
                }
            }
        }
    }
    
    // 初始化时添加欢迎日志
    Component.onCompleted: {
        logArea.append("[" + new Date().toLocaleTimeString() + "] INFO: 系统启动完成")
        logArea.append("[" + new Date().toLocaleTimeString() + "] INFO: 所有模块加载成功")
    }
}
'''
        
        with open(qml_file, 'w', encoding='utf-8') as f:
            f.write(qml_content)
        
        self.logger.info(f"创建模块化QML文件: {qml_file}")
    
    def create_fallback_ui(self):
        """创建备用界面"""
        self.logger.info("创建备用界面")
        
        # 创建基本的PyQt界面作为备用
        from PySide6.QtWidgets import QLabel, QTextEdit, QLineEdit, QPushButton, QHBoxLayout
        
        # 标题
        title = QLabel("Pank Ins - AI控制示波器系统")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px;")
        self.layout().addWidget(title)
        
        # 简单的聊天区域
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.layout().addWidget(self.chat_area)
        
        # 输入区域
        input_layout = QHBoxLayout()
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("输入消息...")
        send_button = QPushButton("发送")
        
        input_layout.addWidget(self.message_input)
        input_layout.addWidget(send_button)
        self.layout().addLayout(input_layout)
        
        # 连接信号
        self.message_input.returnPressed.connect(self.send_message)
        send_button.clicked.connect(self.send_message)
        
    @Slot()
    def send_message(self):
        """发送消息（备用界面）"""
        message = self.message_input.text().strip()
        if message:
            self.chat_area.append(f"👤 用户: {message}")
            if self.qml_bridge:
                self.qml_bridge.handle_user_message(message)
            self.message_input.clear()
    
    def set_ai_actor_ref(self, ai_actor_ref):
        """设置AI Actor引用"""
        self.ai_actor_ref = ai_actor_ref
        if self.qml_bridge:
            self.qml_bridge.set_ai_actor_ref(ai_actor_ref)
        self.logger.info("QML主窗口: AI Actor引用已设置")
    
    def set_ui_actor_ref(self, ui_actor_ref):
        """设置UI Actor引用"""
        self.ui_actor_ref = ui_actor_ref
        if self.qml_bridge:
            self.qml_bridge.set_ui_actor_ref(ui_actor_ref)
        self.logger.info("QML主窗口: UI Actor引用已设置")
    
    # 流式响应方法
    @Slot()
    def start_stream_response(self):
        """开始流式响应"""
        if self.qml_bridge:
            self.qml_bridge.start_stream_response()
            
    @Slot(str)
    def append_stream_chunk(self, chunk: str):
        """追加流式响应片段"""
        if self.qml_bridge:
            self.qml_bridge.append_stream_chunk(chunk)
            
    @Slot()
    def finish_stream_response(self):
        """完成流式响应"""
        if self.qml_bridge:
            self.qml_bridge.finish_stream_response()
            
    # 🔥 新增：AI聊天画布流式状态管理方法
    def get_ai_chat_panel(self) -> Optional[QObject]:
        """获取AI聊天面板组件的引用"""
        try:
            if self.qml_widget and self.qml_widget.rootObject():
                # 🔥 修改：使用递归查找AI聊天面板
                root_object = self.qml_widget.rootObject()
                
                # 方法1：通过objectName查找
                ai_chat_panel = root_object.findChild(QObject, "aiChatPanel")
                if ai_chat_panel:
                    return ai_chat_panel
                
                # 方法2：通过QML ID查找（使用property方式）
                try:
                    ai_chat_panel = root_object.property("aiChatPanel")
                    if ai_chat_panel:
                        return ai_chat_panel
                except:
                    pass
                
                # 方法3：递归查找所有子组件
                def find_object_by_name(obj, name):
                    if obj and hasattr(obj, 'objectName') and obj.objectName() == name:
                        return obj
                    if hasattr(obj, 'children'):
                        for child in obj.children():
                            result = find_object_by_name(child, name)
                            if result:
                                return result
                    return None
                
                ai_chat_panel = find_object_by_name(root_object, "aiChatPanel")
                if ai_chat_panel:
                    return ai_chat_panel
                
                # 🔥 新增：尝试直接调用QML方法而不是查找组件
                self.logger.debug("尝试直接调用QML方法而不是查找组件")
                
        except Exception as e:
            self.logger.error(f"获取AI聊天面板失败: {e}")
        return None
    
    # 🔥 修改：改为直接调用QML方法的方式
    @Slot(bool)
    def set_ai_chat_streaming_state(self, streaming: bool):
        """设置AI聊天画布的流式响应状态"""
        try:
            if self.qml_widget and self.qml_widget.rootObject():
                # 🔥 修改：直接调用根对象的方法
                root_object = self.qml_widget.rootObject()
                from PySide6.QtCore import QMetaObject, Qt
                
                # 🔥 修复：使用直接参数传递而不是QVariant
                success = QMetaObject.invokeMethod(
                    root_object,
                    "setAiChatStreamingState",
                    Qt.QueuedConnection,
                    streaming
                )
                
                if success:
                    self.logger.debug(f"✅ 设置AI聊天画布流式状态成功: {streaming}")
                else:
                    self.logger.debug(f"⚠️ 设置AI聊天画布流式状态失败，尝试查找组件方式")
                    
                    # 备选方案：查找AI聊天面板组件
                    ai_chat_panel = self.get_ai_chat_panel()
                    if ai_chat_panel:
                        QMetaObject.invokeMethod(
                            ai_chat_panel,
                            "setStreamingState",
                            Qt.QueuedConnection,
                            streaming
                        )
                        self.logger.debug(f"✅ 通过组件查找设置流式状态成功: {streaming}")
                    else:
                        self.logger.warning("❌ 未找到AI聊天面板组件")
                        
        except Exception as e:
            self.logger.error(f"设置AI聊天画布流式状态失败: {e}")
            
    @Slot()
    def maintain_ai_chat_scroll_position(self):
        """维持AI聊天画布的当前滚动位置"""
        try:
            if self.qml_widget and self.qml_widget.rootObject():
                # 🔥 修改：直接调用根对象的方法
                root_object = self.qml_widget.rootObject()
                from PySide6.QtCore import QMetaObject, Qt
                
                # 尝试直接调用QML中的方法
                success = QMetaObject.invokeMethod(
                    root_object,
                    "maintainAiChatScrollPosition",
                    Qt.QueuedConnection
                )
                
                if success:
                    self.logger.debug("✅ 维持AI聊天画布滚动位置成功")
                else:
                    # 备选方案：查找AI聊天面板组件
                    ai_chat_panel = self.get_ai_chat_panel()
                    if ai_chat_panel:
                        QMetaObject.invokeMethod(
                            ai_chat_panel,
                            "maintainScrollPosition",
                            Qt.QueuedConnection
                        )
                        self.logger.debug("✅ 通过组件查找维持滚动位置成功")
                    else:
                        self.logger.debug("⚠️ 未找到AI聊天面板组件，跳过滚动位置维持")
                        
        except Exception as e:
            self.logger.error(f"维持AI聊天画布滚动位置失败: {e}")
            
    @Slot()
    def scroll_ai_chat_to_bottom(self):
        """手动滚动AI聊天画布到底部"""
        try:
            if self.qml_widget and self.qml_widget.rootObject():
                # 🔥 修改：直接调用根对象的方法
                root_object = self.qml_widget.rootObject()
                from PySide6.QtCore import QMetaObject, Qt
                
                # 尝试直接调用QML中的方法
                success = QMetaObject.invokeMethod(
                    root_object,
                    "scrollAiChatToBottom",
                    Qt.QueuedConnection
                )
                
                if success:
                    self.logger.debug("✅ 手动滚动AI聊天画布到底部成功")
                else:
                    # 备选方案：查找AI聊天面板组件
                    ai_chat_panel = self.get_ai_chat_panel()
                    if ai_chat_panel:
                        QMetaObject.invokeMethod(
                            ai_chat_panel,
                            "scrollToBottom",
                            Qt.QueuedConnection
                        )
                        self.logger.debug("✅ 通过组件查找滚动到底部成功")
                    else:
                        self.logger.debug("⚠️ 未找到AI聊天面板组件，跳过滚动到底部")
                        
        except Exception as e:
            self.logger.error(f"手动滚动AI聊天画布到底部失败: {e}")
            
    # 🔥 新增：AI聊天画布相关的辅助方法
    def get_ai_chat_panel(self) -> Optional[QObject]:
        """获取AI聊天面板组件的引用"""
        try:
            if self.qml_widget and self.qml_widget.rootObject():
                # 🔥 修改：使用递归查找AI聊天面板
                root_object = self.qml_widget.rootObject()
                
                # 方法1：通过objectName查找
                ai_chat_panel = root_object.findChild(QObject, "aiChatPanel")
                if ai_chat_panel:
                    return ai_chat_panel
                
                # 方法2：通过QML ID查找（使用property方式）
                try:
                    ai_chat_panel = root_object.property("aiChatPanel")
                    if ai_chat_panel:
                        return ai_chat_panel
                except:
                    pass
                
                # 方法3：递归查找所有子组件
                def find_object_by_name(obj, name):
                    if obj and hasattr(obj, 'objectName') and obj.objectName() == name:
                        return obj
                    if hasattr(obj, 'children'):
                        for child in obj.children():
                            result = find_object_by_name(child, name)
                            if result:
                                return result
                    return None
                
                ai_chat_panel = find_object_by_name(root_object, "aiChatPanel")
                if ai_chat_panel:
                    return ai_chat_panel
                
                # 🔥 新增：尝试直接调用QML方法而不是查找组件
                self.logger.debug("尝试直接调用QML方法而不是查找组件")
                
        except Exception as e:
            self.logger.error(f"获取AI聊天面板失败: {e}")
        return None
    
    # 🔥 重新添加：缓冲系统方法
    def update_plan_buffer(self, plan_data: Dict[str, Any]):
        """更新计划缓冲区"""
        if self.qml_bridge:
            self.qml_bridge.update_plan_buffer(plan_data)
            
    def update_task_buffer(self, task_data: Dict[str, Any]):
        """更新任务缓冲区"""
        if self.qml_bridge:
            self.qml_bridge.update_task_buffer(task_data)
     
    def closeEvent(self, event):
        """窗口关闭事件"""
        self.logger.info("QML主窗口正在关闭...")
        self.window_closed.emit()
        event.accept()
        
    def show(self):
        """显示窗口"""
        super().show()
        self.logger.info("QML主窗口已显示")
        
        # 设置窗口到屏幕中央
        screen = QGuiApplication.primaryScreen()
        if screen:
            screen_geometry = screen.availableGeometry()
            self.move(
                (screen_geometry.width() - self.width()) // 2,
                (screen_geometry.height() - self.height()) // 2
            )


def main():
    """主程序入口（用于测试）"""
    import sys
    
    app = QApplication(sys.argv)
    app.setApplicationName("Pank Ins")
    app.setApplicationVersion("2.0.0")
    
    window = QMLMainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 