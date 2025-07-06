#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
QML工作区域桥接模块

提供QML增强的工作区域组件，与现有PyQt6架构无缝集成
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from PySide6.QtCore import QObject, Signal, Slot, Property, QUrl
from PySide6.QtQuick import QQuickView
from PySide6.QtQuickWidgets import QQuickWidget
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtQml import qmlRegisterType

logger = logging.getLogger(__name__)


class QMLWorkAreaBridge(QObject):
    """
    QML工作区域桥接类
    
    负责Python与QML之间的数据传递和信号通信
    """
    
    # 信号定义
    contentChanged = Signal(str, 'QVariant', name='contentChanged')
    actionRequested = Signal(str, 'QVariant', name='actionRequested')
    modeChanged = Signal(str, name='modeChanged')
    
    def __init__(self):
        super().__init__()
        self._current_mode = "default"
        self._current_data = None
        
    @Property(str, notify=modeChanged)
    def currentMode(self):
        """当前显示模式"""
        return self._current_mode
        
    @currentMode.setter
    def currentMode(self, mode):
        if self._current_mode != mode:
            self._current_mode = mode
            self.modeChanged.emit(mode)
    
    @Slot(str, 'QVariant')
    def setContent(self, mode: str, data: Any):
        """设置工作区内容"""
        try:
            self._current_mode = mode
            self._current_data = data
            self.modeChanged.emit(mode)
            self.contentChanged.emit(mode, data)
            logger.info(f"工作区内容已切换到模式: {mode}")
        except Exception as e:
            logger.error(f"设置工作区内容失败: {e}")
    
    @Slot()
    def clearContent(self):
        """清空工作区内容"""
        try:
            self._current_mode = "default"
            self._current_data = None
            self.modeChanged.emit("default")
            self.contentChanged.emit("default", None)
            logger.info("工作区内容已清空")
        except Exception as e:
            logger.error(f"清空工作区内容失败: {e}")
    
    @Slot(str, 'QVariant')
    def onActionRequested(self, action: str, data: Any):
        """处理QML发出的操作请求"""
        try:
            logger.info(f"收到QML操作请求: {action}")
            self.actionRequested.emit(action, data)
        except Exception as e:
            logger.error(f"处理操作请求失败: {e}")
    
    @Slot('QVariant', result='QVariant')
    def processData(self, data: Any) -> Any:
        """处理数据格式转换"""
        try:
            if isinstance(data, dict):
                return data
            elif isinstance(data, str):
                try:
                    return json.loads(data)
                except json.JSONDecodeError:
                    return {"text": data}
            else:
                return {"value": data}
        except Exception as e:
            logger.error(f"数据处理失败: {e}")
            return {}


class QMLWorkArea(QWidget):
    """
    QML增强的工作区域组件
    
    集成QML界面到PyQt6 Widget系统中
    """
    
    # 信号定义
    content_changed = Signal(str, dict)  # 内容变化信号
    action_requested = Signal(str, dict)  # 操作请求信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.qml_bridge = None
        self.qml_widget = None
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        """设置用户界面"""
        try:
            layout = QVBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
            
            # 创建QML桥接对象
            self.qml_bridge = QMLWorkAreaBridge()
            
            # 注册QML类型
            qmlRegisterType(QMLWorkAreaBridge, "WorkAreaBridge", 1, 0, "WorkAreaBridge")
            
            # 创建QQuickWidget
            self.qml_widget = QQuickWidget()
            self.qml_widget.setResizeMode(QQuickWidget.SizeRootObjectToView)
            
            # 设置QML上下文属性
            self.qml_widget.rootContext().setContextProperty("workAreaBridge", self.qml_bridge)
            
            # 加载QML文件
            qml_file = Path(__file__).parent / "qml" / "WorkAreaEnhanced.qml"
            if qml_file.exists():
                self.qml_widget.setSource(QUrl.fromLocalFile(str(qml_file)))
                logger.info("QML工作区域加载成功")
            else:
                logger.error(f"QML文件不存在: {qml_file}")
                self.create_fallback_widget()
                
            layout.addWidget(self.qml_widget)
            self.setLayout(layout)
            
        except Exception as e:
            logger.error(f"QML工作区域初始化失败: {e}")
            self.create_fallback_widget()
    
    def create_fallback_widget(self):
        """创建备用Widget（当QML加载失败时）"""
        from PySide6.QtWidgets import QLabel
        from PySide6.QtCore import Qt
        
        fallback_label = QLabel("QML工作区域加载失败\n使用传统工作区域")
        fallback_label.setAlignment(Qt.AlignCenter)
        fallback_label.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 16px;
                background-color: #f5f5f5;
                padding: 50px;
                border-radius: 10px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.addWidget(fallback_label)
        self.setLayout(layout)
    
    def setup_connections(self):
        """设置信号连接"""
        if self.qml_bridge:
            self.qml_bridge.contentChanged.connect(self.on_content_changed)
            self.qml_bridge.actionRequested.connect(self.on_action_requested)
    
    def on_content_changed(self, mode: str, data):
        """处理内容变化"""
        try:
            data_dict = data if isinstance(data, dict) else {}
            self.content_changed.emit(mode, data_dict)
            logger.info(f"工作区内容变化: {mode}")
        except Exception as e:
            logger.error(f"处理内容变化失败: {e}")
    
    def on_action_requested(self, action: str, data):
        """处理操作请求"""
        try:
            data_dict = data if isinstance(data, dict) else {}
            self.action_requested.emit(action, data_dict)
            logger.info(f"工作区操作请求: {action}")
        except Exception as e:
            logger.error(f"处理操作请求失败: {e}")
    
    def set_content(self, mode: str, data: Optional[Dict[str, Any]] = None):
        """设置工作区内容"""
        if self.qml_bridge:
            self.qml_bridge.setContent(mode, data or {})
    
    def clear_content(self):
        """清空工作区内容"""
        if self.qml_bridge:
            self.qml_bridge.clearContent()
    
    def show_project_details(self, project_data: Dict[str, Any]):
        """显示项目详情"""
        self.set_content("project", project_data)
    
    def show_task_details(self, task_data: Dict[str, Any]):
        """显示任务详情"""
        self.set_content("task", task_data)
    
    def show_device_management(self, device_data: Dict[str, Any] = None):
        """显示设备管理"""
        self.set_content("device", device_data or {})
    
    def show_default_view(self):
        """显示默认视图"""
        self.set_content("default", {})


# 演示数据生成器
class DemoDataGenerator:
    """演示数据生成器"""
    
    @staticmethod
    def create_sample_project() -> Dict[str, Any]:
        """创建示例项目数据"""
        return {
            "id": "proj_001",
            "title": "I2C协议测试项目",
            "description": "完整的I2C通信协议测试，包括时钟信号、数据信号和协议解码验证",
            "status": "running",
            "progress": 65,
            "created_time": "2025-06-28 10:30:00",
            "estimated_duration": "45分钟",
            "tasks": [
                {
                    "id": "task_001",
                    "name": "I2C时钟信号测试",
                    "description": "测试I2C时钟线(SCL)的信号质量和频率",
                    "status": "completed",
                    "progress": 100,
                    "duration": "12分钟"
                },
                {
                    "id": "task_002", 
                    "name": "I2C数据信号测试",
                    "description": "测试I2C数据线(SDA)的信号完整性",
                    "status": "running",
                    "progress": 75,
                    "duration": "15分钟"
                },
                {
                    "id": "task_003",
                    "name": "I2C协议解码验证", 
                    "description": "验证I2C协议的起始、停止、应答等信号",
                    "status": "pending",
                    "progress": 0,
                    "duration": "18分钟"
                }
            ]
        }
    
    @staticmethod
    def create_sample_task() -> Dict[str, Any]:
        """创建示例任务数据"""
        return {
            "id": "task_002",
            "name": "I2C数据信号测试",
            "description": "测试I2C数据线(SDA)的信号完整性",
            "status": "running",
            "progress": 75,
            "steps": [
                {
                    "id": "step_001",
                    "name": "设置示波器参数",
                    "status": "completed",
                    "description": "配置采样率、触发条件等"
                },
                {
                    "id": "step_002", 
                    "name": "连接测试信号",
                    "status": "completed",
                    "description": "连接I2C数据线到示波器通道"
                },
                {
                    "id": "step_003",
                    "name": "执行信号测量",
                    "status": "running",
                    "description": "实时测量数据线信号质量"
                },
                {
                    "id": "step_004",
                    "name": "分析测试结果",
                    "status": "pending", 
                    "description": "分析信号完整性和噪声水平"
                }
            ],
            "measurements": {
                "voltage_high": "3.3V",
                "voltage_low": "0.1V", 
                "rise_time": "2.5μs",
                "fall_time": "1.8μs",
                "noise_level": "15mV"
            }
        }


if __name__ == "__main__":
    """测试QML工作区域"""
    import sys
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # 创建QML工作区域
    work_area = QMLWorkArea()
    work_area.setWindowTitle("QML工作区域测试")
    work_area.resize(1000, 700)
    
    # 连接信号
    def on_content_changed(mode, data):
        print(f"内容变化: {mode} -> {data}")
    
    def on_action_requested(action, data):
        print(f"操作请求: {action} -> {data}")
        
        # 演示响应操作
        if action == "start_test":
            work_area.show_task_details(DemoDataGenerator.create_sample_task())
        elif action == "view_report":
            print("查看报告功能（演示）")
        elif action == "select_task":
            work_area.show_task_details(DemoDataGenerator.create_sample_task())
    
    work_area.content_changed.connect(on_content_changed)
    work_area.action_requested.connect(on_action_requested)
    
    # 显示窗口
    work_area.show()
    
    # 延迟显示项目详情（演示）
    from PySide6.QtCore import QTimer
    def show_demo_project():
        work_area.show_project_details(DemoDataGenerator.create_sample_project())
    
    QTimer.singleShot(2000, show_demo_project)
    
    sys.exit(app.exec()) 