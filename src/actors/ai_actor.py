#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI Actor模块

使用pykka框架实现的AI聊天处理器，集成LevelBaseChain功能。
支持多用户对话管理和智能难度识别。

@author: PankIns Team
@version: 1.0.0
"""

import os
import sys
import pykka
from typing import Dict, Any, Optional

# 添加项目根目录到Python路径
current_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
sys.path.insert(0, project_root)

from src.utils.logger_config import get_logger
# 🔥 修改：使用真正的chain而不是测试版本
from src.ai_chat.chain.level_base_chain import LevelBaseChain

logger = get_logger(__name__)


class AIActor(pykka.ThreadingActor):
    """
    AI处理Actor
    
    提供智能对话处理功能，支持：
    - 多用户对话管理
    - 4个难度级别的智能识别和处理
    - 历史记录管理
    - 异步消息处理
    - 流式响应显示
    """
    
    def __init__(self):
        super().__init__()
        self.chain = None
        self.active_containers = set()
        self._chain_initialized = False
        self.ui_actor_ref = None  # UI Actor引用
        self.main_window_ref = None  # 主窗口引用（用于直接调用）
        
    def on_start(self):
        """Actor启动时初始化"""
        try:
            logger.info("AI Actor 正在启动...")
            logger.info("AI Actor 启动成功")
        except Exception as e:
            logger.error(f"AI Actor 启动失败: {e}")
            raise
    
    def _ensure_chain_initialized(self):
        """确保 chain 已初始化"""
        if not self._chain_initialized:
            try:
                # 🔥 修改：使用真正的LevelBaseChain
                
                def stream_callback(event_type, data):
                    """流式回调函数"""
                    logger.debug(f"流式回调: {event_type} - {data}")
                    try:
                        # 🔧 修复：解析AI响应中的JSON格式
                        processed_data = self._process_stream_data(event_type, data)
                        
                        # 发送流式更新给UI Actor
                        if self.ui_actor_ref:
                            self.ui_actor_ref.tell({
                                'action': 'ai_chat_update_stream',
                                'event_type': event_type,
                                'data': processed_data
                            })
                            logger.debug(f"已发送流式更新: {event_type}")
                    except Exception as e:
                        logger.error(f"流式回调处理错误: {e}")
                
                # 创建LevelBaseChain实例
                self.chain = LevelBaseChain(
                    stream_callback=stream_callback,
                    flow_card_update=None  # 暂时不实现
                )
                
                self._chain_initialized = True
                logger.info("🚀 真正的LevelBaseChain 初始化完成")
                
            except Exception as e:
                logger.error(f"LevelBaseChain 初始化失败: {e}")
                logger.error(f"错误详情: {type(e).__name__}: {str(e)}")
                import traceback
                logger.error(f"错误堆栈:\n{traceback.format_exc()}")
                
    def _process_stream_data(self, event_type, data):
        """处理流式数据，解析JSON格式的AI响应"""
        try:
            if event_type == "STREAM_CHUNK" and data:
                # 尝试解析JSON格式的响应
                import json
                try:
                    json_data = json.loads(data)
                    if isinstance(json_data, dict) and 'content' in json_data:
                        return json_data['content']
                except json.JSONDecodeError:
                    # 如果不是JSON，直接返回原始数据
                    pass
            return data
        except Exception as e:
            logger.error(f"处理流式数据时出错: {e}")
            return data
    
    def on_stop(self):
        """Actor停止时清理资源"""
        logger.info("AI Actor 正在停止...")
        self.active_containers.clear()
        logger.info("AI Actor 已停止")
    
    def on_receive(self, message):
        """接收并处理消息"""
        try:
            if not isinstance(message, dict):
                logger.warning(f"收到非字典格式消息: {type(message)}")
                return {"status": "error", "message": "消息格式错误"}
            
            action = message.get('action')
            
            if action == 'get_status':
                return {
                    "status": "running", 
                    "actor_type": "AIActor",
                    "chain_initialized": self._chain_initialized,
                    "chain_type": "真正的LevelBaseChain"  # 添加chain类型标识
                }
            
            elif action == 'set_ui_actor_ref':
                self.ui_actor_ref = message.get('ui_actor_ref')
                logger.info("AI Actor已设置UI Actor引用")
                return {"status": "success", "message": "UI Actor引用已设置"}
            
            elif action == 'set_main_window_ref':
                self.main_window_ref = message.get('main_window_ref')
                logger.info("AI Actor已设置主窗口引用")
                # 重新初始化chain以使用新的回调
                self._chain_initialized = False
                self._ensure_chain_initialized()
                return {"status": "success", "message": "主窗口引用已设置"}
            
            elif action == 'process_message':
                self._ensure_chain_initialized()
                return self._handle_process_message(message)
                
            elif action == 'process_message_stream':
                self._ensure_chain_initialized()
                return self._handle_process_message_stream(message)
            
            elif action == 'get_history':
                self._ensure_chain_initialized()
                return self._handle_get_history(message)
            
            elif action == 'clear_history':
                self._ensure_chain_initialized()
                return self._handle_clear_history(message)
            
            else:
                logger.warning(f"收到未知消息类型: {action}")
                return {"status": "error", "message": f"未知消息类型: {action}"}
                
        except Exception as e:
            logger.error(f"处理消息时发生错误: {e}")
            return {"status": "error", "message": str(e)}
    
    def _handle_process_message(self, message: dict) -> Dict[str, Any]:
        """处理用户消息"""
        try:
            container_id = message.get('container_id', 'default')
            content = message.get('content', '')
            
            logger.info(f"🤖 处理用户消息 - 容器ID: {container_id}, 内容: {content[:50]}...")
            
            # 添加到活跃容器列表
            self.active_containers.add(container_id)
            
            # 使用真正的LevelBaseChain处理消息
            response = self.chain.process_message(container_id, content)
            
            logger.info(f"✅ 消息处理完成 - 容器ID: {container_id}")
            logger.debug(f"AI响应: {response[:100]}...")
            
            return {
                "status": "success",
                "container_id": container_id,
                "response": response
            }
            
        except Exception as e:
            logger.error(f"处理用户消息失败: {e}")
            import traceback
            logger.error(f"错误详情:\n{traceback.format_exc()}")
            return {
                "status": "error",
                "container_id": message.get('container_id', 'default'),
                "message": str(e)
            }
    
    def _handle_process_message_stream(self, message: dict) -> Dict[str, Any]:
        """处理流式响应消息"""
        try:
            container_id = message.get('container_id', 'default')
            content = message.get('content', '')
            
            logger.info(f"处理流式响应消息 - 容器ID: {container_id}, 内容: {content[:50]}...")
            
            # 添加到活跃容器列表
            self.active_containers.add(container_id)
            
            # 使用LevelBaseChain处理消息（流式回调会自动调用）
            response = self.chain.process_message(container_id, content)
            
            logger.info(f"流式响应处理完成 - 容器ID: {container_id}")
            
            return {
                "status": "success",
                "container_id": container_id,
                "response": response
            }
            
        except Exception as e:
            logger.error(f"处理流式响应消息失败: {e}")
            return {
                "status": "error",
                "container_id": message.get('container_id', 'default'),
                "message": str(e)
            }
    
    def _handle_get_history(self, message: dict) -> Dict[str, Any]:
        """获取对话历史"""
        try:
            container_id = message.get('container_id', 'default')
            history = self.chain.get_history(container_id)
            
            return {
                "status": "success",
                "container_id": container_id,
                "history": history
            }
            
        except Exception as e:
            logger.error(f"获取历史记录失败: {e}")
            return {
                "status": "error",
                "container_id": message.get('container_id', 'default'),
                "message": str(e)
            }
    
    def _handle_clear_history(self, message: dict) -> Dict[str, Any]:
        """清空对话历史"""
        try:
            container_id = message.get('container_id', 'default')
            success = self.chain.clear_history(container_id)
            
            return {
                "status": "success" if success else "error",
                "container_id": container_id,
                "cleared": success
            }
            
        except Exception as e:
            logger.error(f"清空历史记录失败: {e}")
            return {
                "status": "error",
                "container_id": message.get('container_id', 'default'),
                "message": str(e)
            }


class AIActorManager:
    """AI Actor管理器"""
    
    def __init__(self):
        self.actor_ref = None
        
    def start(self):
        """启动AI Actor"""
        try:
            if self.actor_ref is None:
                self.actor_ref = AIActor.start()
                logger.info("AI Actor Manager 启动成功")
            return True
        except Exception as e:
            logger.error(f"启动AI Actor失败: {e}")
            return False
    
    def stop(self):
        """停止AI Actor"""
        try:
            if self.actor_ref:
                self.actor_ref.stop()
                self.actor_ref = None
                logger.info("AI Actor Manager 已停止")
        except Exception as e:
            logger.error(f"停止AI Actor失败: {e}")
    
    def send_message(self, message: dict) -> Any:
        """发送消息到Actor"""
        if self.actor_ref is None:
            raise RuntimeError("AI Actor 未启动")
        
        return self.actor_ref.ask(message)
    
    def process_user_message(self, container_id: str, content: str) -> Dict[str, Any]:
        """处理用户消息的便捷方法"""
        message = {
            "action": "process_message",
            "container_id": container_id,
            "content": content
        }
        return self.send_message(message)
    
    def process_user_message_stream(self, container_id: str, content: str) -> Dict[str, Any]:
        """处理用户消息的便捷方法（流式）"""
        message = {
            "action": "process_message_stream",
            "container_id": container_id,
            "content": content
        }
        return self.send_message(message)
    
    def get_history(self, container_id: str) -> Dict[str, Any]:
        """获取历史记录的便捷方法"""
        message = {
            "action": "get_history",
            "container_id": container_id
        }
        return self.send_message(message)
    
    def clear_history(self, container_id: str) -> Dict[str, Any]:
        """清空历史记录的便捷方法"""
        message = {
            "action": "clear_history",
            "container_id": container_id
        }
        return self.send_message(message)


# 全局AI Actor管理器实例
ai_manager = AIActorManager()


def get_ai_manager() -> AIActorManager:
    """获取AI Actor管理器实例"""
    return ai_manager
