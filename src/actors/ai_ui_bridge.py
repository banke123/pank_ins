#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI与UI通信桥接器

定义AI模块与UI模块之间的通信协议和消息格式。
提供统一的消息路由和处理机制。

@author: PankIns Team
@version: 1.0.0
"""

import logging
import pykka
from typing import Dict, Any, List, Optional, Callable
from enum import Enum
import time
import uuid


class MessageType(Enum):
    """消息类型枚举"""
    # AI查询相关
    AI_CHAT_QUERY = "ai_chat_query"           # 用户聊天查询
    AI_CHAT_RESPONSE = "ai_chat_response"     # AI聊天响应
    AI_ANALYSIS_REQUEST = "ai_analysis_request"  # 数据分析请求
    AI_ANALYSIS_RESULT = "ai_analysis_result"    # 分析结果
    AI_WORKFLOW_REQUEST = "ai_workflow_request"  # 工作流程生成请求
    AI_WORKFLOW_RESULT = "ai_workflow_result"    # 工作流程结果
    
    # UI更新相关
    UI_STATUS_UPDATE = "ui_status_update"     # UI状态更新
    UI_NOTIFICATION = "ui_notification"       # UI通知
    UI_PROGRESS_UPDATE = "ui_progress_update" # 进度更新
    UI_DATA_DISPLAY = "ui_data_display"       # 数据显示
    UI_LOG_MESSAGE = "ui_log_message"         # 日志消息
    
    # 系统控制
    SYSTEM_COMMAND = "system_command"         # 系统命令
    DEVICE_CONTROL = "device_control"         # 设备控制
    DATA_ACQUISITION = "data_acquisition"     # 数据采集


class AIMessage:
    """AI消息类"""
    
    def __init__(self, msg_type: MessageType, data: Dict[str, Any], 
                 sender: str = None, correlation_id: str = None):
        """
        初始化AI消息
        
        Args:
            msg_type (MessageType): 消息类型
            data (Dict[str, Any]): 消息数据
            sender (str): 发送者标识
            correlation_id (str): 关联ID，用于请求-响应配对
        """
        self.id = str(uuid.uuid4())
        self.type = msg_type
        self.data = data
        self.sender = sender or "unknown"
        self.correlation_id = correlation_id or self.id
        self.timestamp = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "id": self.id,
            "type": self.type.value,
            "data": self.data,
            "sender": self.sender,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AIMessage':
        """从字典创建消息"""
        msg = cls(
            msg_type=MessageType(data["type"]),
            data=data["data"],
            sender=data.get("sender"),
            correlation_id=data.get("correlation_id")
        )
        msg.id = data["id"]
        msg.timestamp = data["timestamp"]
        return msg


class AIUIBridge:
    """
    AI与UI通信桥接器
    
    管理AI Actor和UI Actor之间的消息路由和通信
    """
    
    def __init__(self):
        """初始化桥接器"""
        self.logger = logging.getLogger(__name__)
        self._ai_actor_ref: Optional[pykka.ActorRef] = None
        self._ui_actor_ref: Optional[pykka.ActorRef] = None
        self._pending_requests: Dict[str, Dict[str, Any]] = {}
        
        # 消息处理器映射
        self._message_handlers: Dict[MessageType, Callable] = {
            MessageType.AI_CHAT_QUERY: self._handle_ai_chat_query,
            MessageType.AI_ANALYSIS_REQUEST: self._handle_ai_analysis_request,
            MessageType.AI_WORKFLOW_REQUEST: self._handle_ai_workflow_request,
            MessageType.UI_STATUS_UPDATE: self._handle_ui_status_update,
            MessageType.UI_NOTIFICATION: self._handle_ui_notification,
        }
        
        self.logger.info("AI-UI桥接器初始化完成")
    
    def register_ai_actor(self, ai_actor_ref: pykka.ActorRef):
        """
        注册AI Actor
        
        Args:
            ai_actor_ref (pykka.ActorRef): AI Actor引用
        """
        self._ai_actor_ref = ai_actor_ref
        self.logger.info("AI Actor已注册到桥接器")
    
    def register_ui_actor(self, ui_actor_ref: pykka.ActorRef):
        """
        注册UI Actor
        
        Args:
            ui_actor_ref (pykka.ActorRef): UI Actor引用
        """
        self._ui_actor_ref = ui_actor_ref
        self.logger.info("UI Actor已注册到桥接器")
    
    def send_ai_query(self, query: str, context: Dict[str, Any] = None, 
                     callback: Callable = None) -> str:
        """
        发送AI查询
        
        Args:
            query (str): 查询内容
            context (Dict[str, Any]): 查询上下文
            callback (Callable): 响应回调函数
            
        Returns:
            str: 请求ID
        """
        if not self._ai_actor_ref:
            self.logger.error("AI Actor未注册")
            return None
        
        message = AIMessage(
            msg_type=MessageType.AI_CHAT_QUERY,
            data={
                "query": query,
                "context": context or {},
                "timestamp": time.time()
            },
            sender="ui"
        )
        
        # 记录待处理请求
        if callback:
            self._pending_requests[message.correlation_id] = {
                "callback": callback,
                "timestamp": time.time()
            }
        
        try:
            self._ai_actor_ref.tell(message.to_dict())
            self.logger.info(f"发送AI查询: {query[:50]}...")
            return message.correlation_id
        except Exception as e:
            self.logger.error(f"发送AI查询失败: {e}")
            return None
    
    def send_analysis_request(self, data: Dict[str, Any], analysis_type: str = "signal",
                            callback: Callable = None) -> str:
        """
        发送数据分析请求
        
        Args:
            data (Dict[str, Any]): 要分析的数据
            analysis_type (str): 分析类型
            callback (Callable): 响应回调函数
            
        Returns:
            str: 请求ID
        """
        if not self._ai_actor_ref:
            self.logger.error("AI Actor未注册")
            return None
        
        message = AIMessage(
            msg_type=MessageType.AI_ANALYSIS_REQUEST,
            data={
                "analysis_data": data,
                "analysis_type": analysis_type,
                "timestamp": time.time()
            },
            sender="ui"
        )
        
        # 记录待处理请求
        if callback:
            self._pending_requests[message.correlation_id] = {
                "callback": callback,
                "timestamp": time.time()
            }
        
        try:
            self._ai_actor_ref.tell(message.to_dict())
            self.logger.info(f"发送分析请求: {analysis_type}")
            return message.correlation_id
        except Exception as e:
            self.logger.error(f"发送分析请求失败: {e}")
            return None
    
    def send_workflow_request(self, objective: str, parameters: Dict[str, Any] = None,
                            callback: Callable = None) -> str:
        """
        发送工作流程生成请求
        
        Args:
            objective (str): 工作目标
            parameters (Dict[str, Any]): 参数
            callback (Callable): 响应回调函数
            
        Returns:
            str: 请求ID
        """
        if not self._ai_actor_ref:
            self.logger.error("AI Actor未注册")
            return None
        
        message = AIMessage(
            msg_type=MessageType.AI_WORKFLOW_REQUEST,
            data={
                "objective": objective,
                "parameters": parameters or {},
                "timestamp": time.time()
            },
            sender="ui"
        )
        
        # 记录待处理请求
        if callback:
            self._pending_requests[message.correlation_id] = {
                "callback": callback,
                "timestamp": time.time()
            }
        
        try:
            self._ai_actor_ref.tell(message.to_dict())
            self.logger.info(f"发送工作流程请求: {objective}")
            return message.correlation_id
        except Exception as e:
            self.logger.error(f"发送工作流程请求失败: {e}")
            return None
    
    def update_ui_status(self, status_type: str, value: Any):
        """
        更新UI状态
        
        Args:
            status_type (str): 状态类型
            value (Any): 状态值
        """
        if not self._ui_actor_ref:
            self.logger.error("UI Actor未注册")
            return
        
        message = AIMessage(
            msg_type=MessageType.UI_STATUS_UPDATE,
            data={
                "status_type": status_type,
                "value": value,
                "timestamp": time.time()
            },
            sender="ai"
        )
        
        try:
            self._ui_actor_ref.tell(message.to_dict())
            self.logger.debug(f"更新UI状态: {status_type} = {value}")
        except Exception as e:
            self.logger.error(f"更新UI状态失败: {e}")
    
    def send_ui_notification(self, title: str, message: str, level: str = "info"):
        """
        发送UI通知
        
        Args:
            title (str): 通知标题
            message (str): 通知内容
            level (str): 通知级别 (info, warning, error)
        """
        if not self._ui_actor_ref:
            self.logger.error("UI Actor未注册")
            return
        
        notification = AIMessage(
            msg_type=MessageType.UI_NOTIFICATION,
            data={
                "title": title,
                "message": message,
                "level": level,
                "timestamp": time.time()
            },
            sender="ai"
        )
        
        try:
            self._ui_actor_ref.tell(notification.to_dict())
            self.logger.info(f"发送UI通知: [{level}] {title}")
        except Exception as e:
            self.logger.error(f"发送UI通知失败: {e}")
    
    def handle_message(self, message_dict: Dict[str, Any]):
        """
        处理接收到的消息
        
        Args:
            message_dict (Dict[str, Any]): 消息字典
        """
        try:
            message = AIMessage.from_dict(message_dict)
            handler = self._message_handlers.get(message.type)
            
            if handler:
                handler(message)
            else:
                self.logger.warning(f"未知消息类型: {message.type.value}")
                
        except Exception as e:
            self.logger.error(f"处理消息失败: {e}")
    
    def _handle_ai_chat_query(self, message: AIMessage):
        """处理AI聊天查询"""
        # 这里可以添加查询预处理逻辑
        self.logger.debug(f"处理AI聊天查询: {message.data.get('query', '')[:50]}...")
    
    def _handle_ai_analysis_request(self, message: AIMessage):
        """处理AI分析请求"""
        self.logger.debug(f"处理AI分析请求: {message.data.get('analysis_type', 'unknown')}")
    
    def _handle_ai_workflow_request(self, message: AIMessage):
        """处理AI工作流程请求"""
        self.logger.debug(f"处理AI工作流程请求: {message.data.get('objective', 'unknown')}")
    
    def _handle_ui_status_update(self, message: AIMessage):
        """处理UI状态更新"""
        status_type = message.data.get('status_type')
        value = message.data.get('value')
        self.logger.debug(f"处理UI状态更新: {status_type} = {value}")
    
    def _handle_ui_notification(self, message: AIMessage):
        """处理UI通知"""
        title = message.data.get('title')
        level = message.data.get('level', 'info')
        self.logger.debug(f"处理UI通知: [{level}] {title}")
    
    def handle_response(self, response_dict: Dict[str, Any]):
        """
        处理响应消息
        
        Args:
            response_dict (Dict[str, Any]): 响应消息字典
        """
        try:
            correlation_id = response_dict.get("correlation_id")
            if not correlation_id:
                return
            
            # 查找待处理请求
            pending_request = self._pending_requests.get(correlation_id)
            if not pending_request:
                return
            
            # 调用回调函数
            callback = pending_request.get("callback")
            if callback:
                callback(response_dict)
            
            # 清理待处理请求
            del self._pending_requests[correlation_id]
            
        except Exception as e:
            self.logger.error(f"处理响应失败: {e}")
    
    def cleanup_expired_requests(self, timeout: float = 300.0):
        """
        清理过期的请求
        
        Args:
            timeout (float): 超时时间（秒）
        """
        current_time = time.time()
        expired_ids = []
        
        for request_id, request_info in self._pending_requests.items():
            if current_time - request_info["timestamp"] > timeout:
                expired_ids.append(request_id)
        
        for request_id in expired_ids:
            del self._pending_requests[request_id]
            self.logger.warning(f"清理过期请求: {request_id}")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取桥接器统计信息
        
        Returns:
            Dict[str, Any]: 统计信息
        """
        return {
            "ai_actor_registered": self._ai_actor_ref is not None,
            "ui_actor_registered": self._ui_actor_ref is not None,
            "pending_requests": len(self._pending_requests),
            "message_handlers": len(self._message_handlers)
        }


# 全局桥接器实例
_ai_ui_bridge = None


def get_ai_ui_bridge() -> AIUIBridge:
    """获取全局AI-UI桥接器实例"""
    global _ai_ui_bridge
    if _ai_ui_bridge is None:
        _ai_ui_bridge = AIUIBridge()
    return _ai_ui_bridge 