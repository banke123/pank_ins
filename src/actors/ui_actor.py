#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
UI Actor模块

负责管理UI界面和与其他Actor系统的通信桥梁

@author: PankIns Team
@version: 1.0.0
"""

import logging
from typing import Any, Dict, Optional
from PySide6.QtCore import QObject, Signal, QTimer
from PySide6.QtWidgets import QApplication
import pykka
from .base_actor import BaseActor


class UIActorSignals(QObject):
    """UI Actor的Qt信号类"""
    
    # 窗口控制信号
    show_main_window = Signal()
    close_main_window = Signal()
    
    # 状态更新信号
    status_update = Signal(str, dict)
    message_received = Signal(str)
    
    # 数据显示信号
    data_display = Signal(dict)
    log_message = Signal(str, str)  # level, message


class UIActor(BaseActor):
    """
    UI Actor类
    
    作为UI界面与Actor系统之间的通信桥梁
    管理主窗口的生命周期和消息传递
    """
    
    def __init__(self):
        super().__init__()
        self.main_window = None
        self.signals = UIActorSignals()
        self._setup_signals()
        
        # 存储其他Actor的引用
        self.registered_actors = {}
    
    def initialize(self):
        """初始化UI Actor"""
        self.logger.info("UI Actor初始化")
        # UI Actor的初始化在这里完成
        # 实际的窗口创建会在收到启动消息时进行
    
    def cleanup(self):
        """清理UI Actor"""
        self.logger.info("UI Actor清理")
        if self.main_window:
            self.main_window.close()
            self.main_window = None
        self.registered_actors.clear()
    
    def _setup_signals(self):
        """设置信号连接"""
        self.signals.show_main_window.connect(self._show_main_window)
        self.signals.close_main_window.connect(self._close_main_window)
        self.signals.log_message.connect(self._add_log_message)
    
    def handle_message(self, message) -> Any:
        """
        处理接收到的消息
        
        Args:
            message: 接收到的消息
            
        Returns:
            Any: 处理结果
        """
        try:
            if isinstance(message, dict):
                action = message.get('action')
                
                if action == 'start_main_window':
                    return self._handle_start_main_window(message)
                elif action == 'close_main_window':
                    return self._handle_close_main_window()
                elif action == 'show_status':
                    return self._handle_show_status(message.get('data', {}))
                elif action == 'show_message':
                    return self._handle_show_message(message.get('text', ''))
                elif action == 'add_log':
                    return self._handle_add_log(message.get('level', 'INFO'), message.get('text', ''))
                elif action == 'display_data':
                    return self._handle_display_data(message.get('data', {}))
                elif action == 'register_actor':
                    return self._handle_register_actor(message)
                elif action == 'forward_to_actor':
                    return self._handle_forward_to_actor(message)
                elif action == 'set_ai_actor_ref':
                    return self._handle_set_ai_actor_ref(message)
                elif action == 'ai_chat_update_stream':
                    # 处理AI Actor发来的流式更新
                    return self._handle_ai_chat_update_stream(message)
                elif action == 'ai_chat_send_message':
                    # 处理发送AI对话消息的请求
                    return self._handle_ai_chat_send_message(message)
                elif action == 'flow_card_update':
                    # 处理AI Actor发来的流程卡片更新
                    return self._handle_flow_card_update(message)
                else:
                    self.logger.warning(f"未知的消息类型: {action}")
                    return {"status": "error", "message": f"未知的消息类型: {action}"}
            else:
                self.logger.warning(f"无效的消息格式: {type(message)}")
                return {"status": "error", "message": "无效的消息格式"}
                
        except Exception as e:
            self.logger.error(f"消息处理异常: {e}", exc_info=True)
            return {"status": "error", "message": str(e)}
    
    def _handle_start_main_window(self, message) -> Dict[str, Any]:
        """处理启动主窗口的消息"""
        try:
            username = message.get('username', None)
            self.logger.info(f"启动主窗口，用户: {username}")
            
            # 通过信号启动主窗口（线程安全）
            self.signals.show_main_window.emit()
            
            # 如果有用户名，添加日志
            if username:
                self.signals.log_message.emit("INFO", f"用户 {username} 登录成功")
            
            return {"status": "ok", "message": "主窗口启动成功"}
            
        except Exception as e:
            self.logger.error(f"启动主窗口失败: {e}")
            return {"status": "error", "message": str(e)}
    
    def _handle_close_main_window(self) -> Dict[str, Any]:
        """处理关闭主窗口的消息"""
        try:
            self.logger.info("关闭主窗口")
            self.signals.close_main_window.emit()
            return {"status": "ok", "message": "主窗口关闭成功"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _handle_show_status(self, status_data) -> Dict[str, Any]:
        """处理显示状态的消息"""
        try:
            self.signals.status_update.emit("status_update", status_data)
            return {"status": "ok", "message": "状态更新成功"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _handle_show_message(self, text) -> Dict[str, Any]:
        """处理显示消息的消息"""
        try:
            self.signals.message_received.emit(text)
            return {"status": "ok", "message": "消息显示成功"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _handle_add_log(self, level, text) -> Dict[str, Any]:
        """处理添加日志的消息"""
        try:
            self.signals.log_message.emit(level, text)
            return {"status": "ok", "message": "日志添加成功"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _handle_display_data(self, data) -> Dict[str, Any]:
        """处理显示数据的消息"""
        try:
            self.signals.data_display.emit(data)
            return {"status": "ok", "message": "数据显示成功"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _handle_register_actor(self, message) -> Dict[str, Any]:
        """处理注册Actor的消息"""
        try:
            actor_name = message.get('actor_name')
            actor_ref = message.get('actor_ref')
            
            if actor_name and actor_ref:
                self.registered_actors[actor_name] = actor_ref
                self.logger.info(f"注册Actor: {actor_name}")
                
                # 如果主窗口已创建且是AI Actor，设置引用
                if actor_name == 'ai' and self.main_window:
                    self.main_window.set_ai_actor_ref(actor_ref)
                
                return {"status": "ok", "message": f"Actor {actor_name} 注册成功"}
            else:
                return {"status": "error", "message": "缺少actor_name或actor_ref"}
                
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _handle_forward_to_actor(self, message) -> Dict[str, Any]:
        """处理转发消息到其他Actor的请求"""
        try:
            target_actor = message.get('target_actor')
            forward_message = message.get('message')
            
            if target_actor in self.registered_actors:
                actor_ref = self.registered_actors[target_actor]
                
                # 根据消息类型选择发送方式
                if message.get('wait_response', False):
                    # 等待响应
                    timeout = message.get('timeout', 5.0)
                    result = actor_ref.ask(forward_message, timeout=timeout)
                    return {"status": "ok", "result": result}
                else:
                    # 不等待响应
                    actor_ref.tell(forward_message)
                    return {"status": "ok", "message": "消息已发送"}
            else:
                return {"status": "error", "message": f"Actor {target_actor} 未注册"}
                
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _handle_set_ai_actor_ref(self, message) -> Dict[str, Any]:
        """处理设置AI Actor引用的消息"""
        try:
            ai_actor_ref = message.get('ai_actor_ref')
            
            if ai_actor_ref:
                self.main_window.set_ai_actor_ref(ai_actor_ref)
                self.logger.info("AI Actor引用设置成功")
                return {"status": "ok", "message": "AI Actor引用设置成功"}
            else:
                return {"status": "error", "message": "缺少ai_actor_ref"}
                
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _handle_ai_chat_update_stream(self, message) -> Dict[str, Any]:
        """处理AI Actor发来的流式更新"""
        try:
            event_type = message.get('event_type')
            data = message.get('data')
            
            self.logger.info(f"收到流式更新 - 事件类型: {event_type}")
            
            # 🔥 修改：使用Qt信号确保在主线程中更新UI - 适配QML主窗口的画布布局
            if self.main_window:
                # 🔥 修改：使用直接调用方法而不是QMetaObject.invokeMethod
                from PySide6.QtCore import QTimer
                
                def call_in_main_thread():
                    """在主线程中执行UI更新"""
                    try:
                        if event_type == "START_STREAM":
                            # 🔥 直接调用方法
                            self.main_window.start_stream_response()
                            self.main_window.set_ai_chat_streaming_state(True)
                            
                        elif event_type == "STREAM_CHUNK":
                            # 🔥 直接调用方法
                            self.main_window.append_stream_chunk(data)
                            self.main_window.maintain_ai_chat_scroll_position()
                            
                        elif event_type == "END_STREAM":
                            # 🔥 直接调用方法
                            self.main_window.finish_stream_response()
                            self.main_window.set_ai_chat_streaming_state(False)
                            
                    except Exception as e:
                        self.logger.error(f"主线程UI更新失败: {e}")
                
                # 使用QTimer.singleShot确保在主线程中执行
                QTimer.singleShot(0, call_in_main_thread)
            
            return {"status": "ok", "message": "流式更新处理成功"}
            
        except Exception as e:
            self.logger.error(f"处理流式更新失败: {e}")
            return {"status": "error", "message": str(e)}
    
    def _handle_ai_chat_send_message(self, message) -> Dict[str, Any]:
        """处理发送AI对话消息的请求"""
        try:
            user_message = message.get('message', '')
            container_id = message.get('container_id', 'main_chat')
            
            if not user_message:
                return {"status": "error", "message": "消息文本为空"}
            
            self.logger.info(f"发送AI对话消息: {user_message}")
            
            # 转发给AI Actor处理
            if 'ai' in self.registered_actors:
                ai_actor_ref = self.registered_actors['ai']
                ai_message = {
                    'action': 'process_message_stream',
                    'container_id': container_id,
                    'content': user_message
                }
                ai_actor_ref.tell(ai_message)
                return {"status": "ok", "message": "消息已发送给AI Actor"}
            else:
                return {"status": "error", "message": "AI Actor未注册"}
                
        except Exception as e:
            self.logger.error(f"发送AI对话消息失败: {e}")
            return {"status": "error", "message": str(e)}
    
    def _handle_flow_card_update(self, message) -> Dict[str, Any]:
        """处理AI Actor发来的流程卡片更新"""
        try:
            event_type = message.get('event_type')
            data = message.get('data')
            
            self.logger.info(f"收到流程卡片更新 - 事件类型: {event_type}")
            
            # 适配QML主窗口的缓冲系统
            if self.main_window:
                if event_type == "UPDATE_PLAN":
                    # 更新Level3计划卡片
                    self.main_window.update_plan_buffer(data)
                elif event_type == "UPDATE_TASK":
                    # 更新Level2任务卡片
                    self.main_window.update_task_buffer(data)
            
            return {"status": "ok", "message": "流程卡片更新处理成功"}
            
        except Exception as e:
            self.logger.error(f"处理流程卡片更新失败: {e}")
            return {"status": "error", "message": str(e)}
    
    def _show_main_window(self):
        """显示主窗口（在主线程中执行）"""
        try:
            if not self.main_window:
                # 使用QML主窗口
                from src.ui.qml_main_window import QMLMainWindow
                self.main_window = QMLMainWindow()
                
                # 连接窗口关闭信号
                self.main_window.window_closed.connect(self._on_window_closed)
                
                # 设置UI Actor引用到QML主窗口
                self.main_window.set_ui_actor_ref(self.actor_ref)
                
                # 如果AI Actor已注册，设置引用
                if 'ai' in self.registered_actors:
                    self.main_window.set_ai_actor_ref(self.registered_actors['ai'])
            
            # 显示窗口并激活到前台
            self.main_window.show()
            self.main_window.raise_()
            self.main_window.activateWindow()
            
            self.logger.info("QML主窗口显示成功")
            
        except Exception as e:
            self.logger.error(f"显示QML主窗口失败: {e}")
    
    def _close_main_window(self):
        """关闭主窗口（在主线程中执行）"""
        try:
            if self.main_window:
                self.main_window.close()
                self.main_window = None
            self.logger.info("主窗口关闭成功")
        except Exception as e:
            self.logger.error(f"关闭主窗口失败: {e}")
    
    def _add_log_message(self, level, text):
        """添加日志消息（在主线程中执行）"""
        try:
            if self.main_window and hasattr(self.main_window, 'qml_bridge'):
                self.main_window.qml_bridge.add_log(level, text)
        except Exception as e:
            self.logger.error(f"添加日志消息失败: {e}")
    
    def _on_window_closed(self):
        """当窗口被关闭时的回调"""
        self.logger.info("主窗口被用户关闭")
        self.main_window = None
        
        # 🔥 重要：窗口关闭时停止所有Actor系统
        self.logger.info("🔄 开始清理Actor系统...")
        
        try:
            # 停止所有已注册的Actor
            for actor_name, actor_ref in self.registered_actors.items():
                try:
                    self.logger.info(f"🛑 停止 {actor_name} Actor...")
                    actor_ref.stop()
                    self.logger.info(f"✅ {actor_name} Actor已停止")
                except Exception as e:
                    self.logger.error(f"❌ 停止 {actor_name} Actor失败: {e}")
            
            # 清空注册的Actor列表
            self.registered_actors.clear()
            
            # 停止自己（UI Actor）
            self.logger.info("🛑 停止UI Actor...")
            
            # 使用QTimer延迟停止，确保日志记录完成
            from PySide6.QtCore import QTimer
            def delayed_shutdown():
                try:
                    # 停止整个pykka Actor系统
                    import pykka
                    pykka.ActorRegistry.stop_all()
                    self.logger.info("✅ 所有Actor已停止")
                    
                    # 退出QApplication
                    from PySide6.QtWidgets import QApplication
                    if QApplication.instance():
                        QApplication.instance().quit()
                        self.logger.info("✅ 应用程序已退出")
                        
                except Exception as e:
                    self.logger.error(f"❌ 延迟关闭过程中出错: {e}")
                    # 强制退出
                    import sys
                    sys.exit(0)
                    
            # 延迟500ms执行关闭，确保日志有时间写入
            QTimer.singleShot(500, delayed_shutdown)
            
        except Exception as e:
            self.logger.error(f"❌ 清理Actor系统失败: {e}")
            # 出现异常时强制退出
            import sys
            sys.exit(1)
    
    def get_main_window(self):
        """获取主窗口引用（用于直接访问）"""
        return self.main_window
    
    def get_registered_actors(self):
        """获取已注册的Actor列表"""
        return list(self.registered_actors.keys())
    
    def send_to_registered_actor(self, actor_name: str, message: dict, wait_response: bool = False, timeout: float = 5.0):
        """
        向已注册的Actor发送消息
        
        Args:
            actor_name (str): Actor名称
            message (dict): 消息内容
            wait_response (bool): 是否等待响应
            timeout (float): 超时时间
        """
        if actor_name in self.registered_actors:
            try:
                if wait_response:
                    return self.registered_actors[actor_name].ask(message, timeout=timeout)
                else:
                    self.registered_actors[actor_name].tell(message)
                    return True
            except Exception as e:
                self.logger.error(f"发送消息到 {actor_name} 失败: {e}")
                return False
        else:
            self.logger.warning(f"Actor {actor_name} 未注册")
            return False
