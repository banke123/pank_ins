#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
基础Actor模块

提供Actor的基础功能和接口，基于pykka框架。

@author: PankIns Team
@version: 1.0.0
"""

import logging
import pykka
from typing import Any, Dict, Optional
from abc import ABC, abstractmethod


class BaseActor(pykka.ThreadingActor, ABC):
    """
    基础Actor类
    
    所有Actor的基类，基于pykka.ThreadingActor，提供消息处理、生命周期管理等基础功能
    """
    
    def __init__(self):
        """
        初始化基础Actor
        """
        super().__init__()
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
        self._is_initialized = False
        self._status = "stopped"
        
        self.logger.info(f"{self.__class__.__name__} Actor创建")
    
    def on_start(self):
        """
        Actor启动时调用
        """
        try:
            self.logger.info(f"{self.__class__.__name__} Actor启动中...")
            self._status = "starting"
            
            # 调用子类的初始化方法
            self.initialize()
            
            self._is_initialized = True
            self._status = "running"
            self.logger.info(f"{self.__class__.__name__} Actor启动完成")
            
        except Exception as e:
            self.logger.error(f"{self.__class__.__name__} Actor启动失败: {e}", exc_info=True)
            self._status = "error"
            raise
    
    def on_stop(self):
        """
        Actor停止时调用
        """
        try:
            self.logger.info(f"{self.__class__.__name__} Actor停止中...")
            self._status = "stopping"
            
            # 调用子类的清理方法
            self.cleanup()
            
            self._status = "stopped"
            self.logger.info(f"{self.__class__.__name__} Actor已停止")
            
        except Exception as e:
            self.logger.error(f"{self.__class__.__name__} Actor停止失败: {e}", exc_info=True)
    
    def on_failure(self, exception_type, exception_value, traceback):
        """
        Actor失败时调用
        
        Args:
            exception_type: 异常类型
            exception_value: 异常值
            traceback: 异常追踪
        """
        self.logger.error(
            f"{self.__class__.__name__} Actor发生异常: {exception_type.__name__}: {exception_value}",
            exc_info=(exception_type, exception_value, traceback)
        )
        self._status = "error"
    
    def on_receive(self, message):
        """
        接收消息的通用处理
        
        Args:
            message: 接收到的消息
            
        Returns:
            Any: 处理结果
        """
        try:
            if not self._is_initialized:
                self.logger.warning(f"Actor未初始化，忽略消息: {message}")
                return {"status": "error", "message": "Actor未初始化"}
            
            # 处理通用消息
            if isinstance(message, dict):
                action = message.get('action')
                
                if action == 'get_status':
                    return self.get_status()
                elif action == 'ping':
                    return {"status": "ok", "message": "pong"}
                elif action == 'stop':
                    self.stop()
                    return {"status": "ok", "message": "stopping"}
            
            # 委托给子类处理
            return self.handle_message(message)
            
        except Exception as e:
            self.logger.error(f"消息处理失败: {e}", exc_info=True)
            return {"status": "error", "message": str(e)}
    
    @abstractmethod
    def initialize(self):
        """
        子类实现的初始化方法
        """
        pass
    
    @abstractmethod
    def cleanup(self):
        """
        子类实现的清理方法
        """
        pass
    
    @abstractmethod
    def handle_message(self, message) -> Any:
        """
        子类实现的消息处理方法
        
        Args:
            message: 接收到的消息
            
        Returns:
            Any: 处理结果
        """
        pass
    
    def get_status(self) -> Dict[str, Any]:
        """
        获取Actor状态
        
        Returns:
            Dict[str, Any]: Actor状态信息
        """
        return {
            "actor_name": self.__class__.__name__,
            "status": self._status,
            "initialized": self._is_initialized,
            "actor_urn": str(self.actor_urn) if hasattr(self, 'actor_urn') else None
        }
    
    def send_to_actor(self, actor_ref: pykka.ActorRef, message: Any, timeout: float = 5.0) -> Optional[Any]:
        """
        向其他Actor发送消息
        
        Args:
            actor_ref: 目标Actor引用
            message: 发送的消息
            timeout: 超时时间（秒）
            
        Returns:
            Optional[Any]: 响应结果
        """
        try:
            future = actor_ref.ask(message, timeout=timeout)
            return future.get()
        except Exception as e:
            self.logger.error(f"发送消息失败: {e}")
            return None
    
    def tell_actor(self, actor_ref: pykka.ActorRef, message: Any):
        """
        向其他Actor发送单向消息（不等待响应）
        
        Args:
            actor_ref: 目标Actor引用
            message: 发送的消息
        """
        try:
            actor_ref.tell(message)
        except Exception as e:
            self.logger.error(f"发送单向消息失败: {e}")
    
    def broadcast_message(self, actor_refs: list, message: Any):
        """
        向多个Actor广播消息
        
        Args:
            actor_refs: Actor引用列表
            message: 广播的消息
        """
        for actor_ref in actor_refs:
            try:
                actor_ref.tell(message)
            except Exception as e:
                self.logger.error(f"广播消息失败: {e}") 