"""
大模型调用接口

此模块定义了与大语言模型交互的基础抽象类和相关数据模型。
具体的模型实现（如聊天、推理、带工具调用、多模态）将继承此基类并实现其抽象方法。

基类提供通用功能：
1. 记忆管理：对话历史的存储和检索
2. 消息处理：消息的格式化和验证
3. 会话功能：会话的创建、更新和删除
4. 错误处理：统一的错误处理机制
5. 重试机制：请求失败时的重试策略

相关的配置和错误类定义在 config.py 和 errors.py 中。

使用示例：
    >>> from ai_chat.llm import ModelConfig, BaseLLM
    >>> config = ModelConfig(model_name="ernie-3.5-8k")
    >>> llm = BaseLLM.create(config)
    >>> response = llm.get_response("你好")
"""
import os
import sys
from langchain_openai import ChatOpenAI
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union, Type
from datetime import datetime
import time
from pydantic import BaseModel, Field

# 添加项目根目录到Python路径
current_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
sys.path.insert(0, project_root)

from src.utils.logger_config import get_logger
from .errors import LLMError, ToolNotFoundError
from src.ai_chat.utils.error_codes import ErrorCode

# 获取logger
logger = get_logger(__name__)

def _system_message(content: str):
    """
    构造系统消息
    """
    return {"role": "system", "content": content}

class BaseLLM(ABC):
    """
    大语言模型基础抽象类
    
    提供所有LLM实现的通用功能和抽象接口。
    """
    
    def __init__(self, model_name: str, api_key: Optional[str] = None, api_url: Optional[str] = None, 
                 temperature: float = 0.5, max_tokens: int = 1000, system_prompt: Optional[str] = None):
        """
        初始化大语言模型基类
        
        Args:
            model_name: 模型名称
            api_key: API密钥
            api_url: API URL
            temperature: 温度
            max_tokens: 最大token数
            system_prompt: 系统提示词
        """
        try:
            self.model_name: str = model_name
            self.api_key: Optional[str] = api_key or os.getenv("QIANFAN_API_KEY")
            self.api_url: Optional[str] = api_url or os.getenv("QIANFAN_API_URL")
            self.temperature: float = temperature
            self.max_tokens: int = max_tokens
            self.system_prompt: Optional[str] = system_prompt
            self.llm = ChatOpenAI(
                model=self.model_name,
                api_key=self.api_key,
                base_url=self.api_url,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stream_usage=True
            )
            
            logger.debug(f"初始化基础模型: {self.model_name}，系统提示词: {system_prompt}")
            
        except Exception as e:
            logger.error(f"初始化模型失败: {e}")
            raise LLMError(ErrorCode.INIT_ERROR, f"初始化模型失败: {str(e)}")

    def _prepare_messages(self, query: Union[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """
        准备发送给模型的消息列表
        
        Args:
            query: 用户输入 (字符串或消息列表)
            
        Returns:
            List[Dict[str, Any]]: 完整的消息列表（系统提示词 + 历史对话）
        """
        messages = []
        
        # 如果有系统提示词，添加到最前面
        if self.system_prompt:
            messages.append(_system_message(self.system_prompt))
            
        # 处理输入消息
        if isinstance(query, str):
            messages.append({"role": "user", "content": query})
        elif isinstance(query, list):
            messages.extend(query)
            
        return messages
    
    def get_response(self, query: Union[str, List[Dict[str, Any]]], **kwargs) -> str:
        """
        获取模型响应（非流式，返回字符串）
        Args:
            query: 用户输入 (字符串或消息列表)
            **kwargs: 其他模型调用参数
        Returns:
            str: 模型响应内容
        Raises:
            LLMError: 调用模型失败时抛出
        """
        try:
            messages_to_send = self._prepare_messages(query)
            logger.debug(f"发送给模型的完整消息: {messages_to_send}")
            
            response = self.llm.invoke(messages_to_send)
            logger.debug(response)
            logger.debug(response.usage_metadata)
            if response.additional_kwargs != {'refusal': None}:
                return response.additional_kwargs
            else:
                return response.content
        except LLMError as e:
            logger.error(f"获取模型响应失败: {e}")
            raise
        except Exception as e:
            logger.error(f"获取模型响应失败，发生未知错误: {e}")
            raise LLMError(ErrorCode.MODEL_ERROR, f"获取模型响应失败: {str(e)}", details=e)

    def get_response_stream(self, query: Union[str, List[Dict[str, Any]]], **kwargs):
        """
        获取模型响应（流式，生成器）
        Args:
            query: 用户输入 (字符串或消息列表)
            **kwargs: 其他模型调用参数
        Yields:
            str: 模型响应内容分片
        Raises:
            LLMError: 调用模型失败时抛出
        """
        try:
            messages_to_send = self._prepare_messages(query)
            logger.debug(f"发送给模型的完整消息: {messages_to_send}")
            
            for chunk in self.llm.stream(messages_to_send):
                # logger.debug(chunk)
                if chunk.content != "":
                    yield chunk.content
                elif chunk.additional_kwargs != {'refusal': None}:
                    yield chunk.additional_kwargs
                else:
                    logger.debug(f"响应完成，token使用情况：{chunk.usage_metadata}")

        except LLMError as e:
            logger.error(f"获取模型响应失败: {e}")
            raise
        except Exception as e:
            logger.error(f"获取模型响应失败，发生未知错误: {e}")
            raise LLMError(ErrorCode.MODEL_ERROR, f"获取模型响应失败: {str(e)}", details=e)