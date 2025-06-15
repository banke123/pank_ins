#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
UI Actor模块

处理用户界面相关的消息和状态更新。

@author: PankIns Team
@version: 1.0.0
"""

import logging
from typing import Dict, Any
from .base_actor import BaseActor


class UIMessage:
    """UI消息类型定义"""
    UPDATE_STATUS = "update_status"
    SHOW_NOTIFICATION = "show_notification"
    UPDATE_WAVEFORM = "update_waveform"
    ADD_LOG = "add_log"
    UPDATE_PROGRESS = "update_progress"


class UIActor(BaseActor):
    """
    UI Actor类
    
    负责处理用户界面相关的消息和状态更新
    """
    
    def __init__(self):
        """
        初始化UI Actor
        """
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.ui_state = {
            "device_connected": False,
            "acquiring": False,
            "ai_online": True,
            "current_workflow": None
        }
    
    def on_start(self):
        """
        Actor启动时的初始化
        """
        super().on_start()
        self.logger.info("UI Actor启动完成")
    
    def on_receive(self, message):
        """
        处理接收到的消息
        
        @param {dict} message - 接收到的消息
        """
        try:
            msg_type = message.get("type")
            data = message.get("data", {})
            
            if msg_type == UIMessage.UPDATE_STATUS:
                self._handle_status_update(data)
            elif msg_type == UIMessage.SHOW_NOTIFICATION:
                self._handle_notification(data)
            elif msg_type == UIMessage.UPDATE_WAVEFORM:
                self._handle_waveform_update(data)
            elif msg_type == UIMessage.ADD_LOG:
                self._handle_log_message(data)
            elif msg_type == UIMessage.UPDATE_PROGRESS:
                self._handle_progress_update(data)
            else:
                self.logger.warning(f"未知的UI消息类型: {msg_type}")
                
        except Exception as e:
            self.logger.error(f"处理UI消息时发生错误: {e}")
    
    def _handle_status_update(self, data: Dict[str, Any]):
        """
        处理状态更新
        
        @param {dict} data - 状态数据
        """
        status_type = data.get("status_type")
        value = data.get("value")
        
        if status_type == "device_connection":
            self.ui_state["device_connected"] = value
            self.logger.info(f"设备连接状态更新: {value}")
        elif status_type == "data_acquisition":
            self.ui_state["acquiring"] = value
            self.logger.info(f"数据采集状态更新: {value}")
        elif status_type == "ai_status":
            self.ui_state["ai_online"] = value
            self.logger.info(f"AI状态更新: {value}")
        elif status_type == "workflow":
            self.ui_state["current_workflow"] = value
            self.logger.info(f"当前工作流程: {value}")
        
        # 通知其他Actor状态变化
        self._broadcast_status_change(status_type, value)
    
    def _handle_notification(self, data: Dict[str, Any]):
        """
        处理通知消息
        
        @param {dict} data - 通知数据
        """
        title = data.get("title", "通知")
        message = data.get("message", "")
        level = data.get("level", "info")
        
        self.logger.info(f"显示通知: [{level}] {title} - {message}")
        
        # 这里可以发送消息给主窗口显示通知
        # 实际实现中可以通过信号槽机制与UI通信
    
    def _handle_waveform_update(self, data: Dict[str, Any]):
        """
        处理波形数据更新
        
        @param {dict} data - 波形数据
        """
        time_data = data.get("time_data")
        signal_data = data.get("signal_data")
        
        if time_data is not None and signal_data is not None:
            self.logger.info(f"更新波形数据: {len(time_data)}个采样点")
            # 这里可以发送消息给波形显示组件
        else:
            self.logger.warning("波形数据不完整")
    
    def _handle_log_message(self, data: Dict[str, Any]):
        """
        处理日志消息
        
        @param {dict} data - 日志数据
        """
        message = data.get("message", "")
        level = data.get("level", "INFO")
        source = data.get("source", "System")
        
        # 记录到日志系统
        if level == "ERROR":
            self.logger.error(f"[{source}] {message}")
        elif level == "WARNING":
            self.logger.warning(f"[{source}] {message}")
        elif level == "DEBUG":
            self.logger.debug(f"[{source}] {message}")
        else:
            self.logger.info(f"[{source}] {message}")
    
    def _handle_progress_update(self, data: Dict[str, Any]):
        """
        处理进度更新
        
        @param {dict} data - 进度数据
        """
        task_id = data.get("task_id")
        progress = data.get("progress", 0)
        status = data.get("status", "running")
        
        self.logger.info(f"任务 {task_id} 进度更新: {progress}% ({status})")
    
    def _broadcast_status_change(self, status_type: str, value: Any):
        """
        广播状态变化给其他Actor
        
        @param {str} status_type - 状态类型
        @param {Any} value - 状态值
        """
        broadcast_message = {
            "type": "status_changed",
            "data": {
                "status_type": status_type,
                "value": value,
                "source": "ui_actor"
            }
        }
        
        # 发送给系统管理器，由其转发给其他Actor
        self.send_to_system_manager(broadcast_message)
    
    def get_ui_state(self) -> Dict[str, Any]:
        """
        获取当前UI状态
        
        @returns {dict} UI状态字典
        """
        return self.ui_state.copy()
    
    def update_device_status(self, connected: bool):
        """
        更新设备连接状态
        
        @param {bool} connected - 是否已连接
        """
        self._handle_status_update({
            "status_type": "device_connection",
            "value": connected
        })
    
    def update_acquisition_status(self, acquiring: bool):
        """
        更新数据采集状态
        
        @param {bool} acquiring - 是否正在采集
        """
        self._handle_status_update({
            "status_type": "data_acquisition",
            "value": acquiring
        })
    
    def show_notification(self, title: str, message: str, level: str = "info"):
        """
        显示通知
        
        @param {str} title - 通知标题
        @param {str} message - 通知消息
        @param {str} level - 通知级别
        """
        self._handle_notification({
            "title": title,
            "message": message,
            "level": level
        })
    
    def add_log(self, message: str, level: str = "INFO", source: str = "System"):
        """
        添加日志消息
        
        @param {str} message - 日志消息
        @param {str} level - 日志级别
        @param {str} source - 消息来源
        """
        self._handle_log_message({
            "message": message,
            "level": level,
            "source": source
        }) 