"""
    llm 种类，基于base_model.py
    1. 基础聊天模型
    2. 工具调用模型
    3. 多模态模型
    4. 思考型模型
"""

import os
import sys
from typing import Optional, List, Dict, Any

# 添加项目根目录到Python路径
current_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
sys.path.insert(0, project_root)

from .base_model import BaseLLM
from src.utils.logger_config import get_logger

logger = get_logger(__name__)



class ChatLLM(BaseLLM):
    """
    基础聊天模型
    """
    def __init__(self, model_name: str, api_key: Optional[str] = None, api_url: Optional[str] = None, 
                 temperature: float = 0.5, max_tokens: int = 1000, system_prompt: Optional[str] = None):
        super().__init__(model_name, api_key, api_url, temperature, max_tokens, system_prompt)
        logger.debug(f"初始化聊天模型{self.model_name}")

    def chat_get_response(self, query: List[Dict[str, Any]]) -> str:
        """
        获取模型响应（非流式，返回字符串）
        
        Args:
            query: 包含历史对话的消息列表
            
        Returns:
            str: 模型响应内容
        """
        try:
            response = self.get_response(query)
            logger.debug(f"模型响应: {response}")
            return response
        except Exception as e:
            logger.error(f"发生错误: {e}")
            return "发生错误: " + str(e)

    def chat_get_response_stream(self, query: List[Dict[str, Any]]):
        """
        获取模型响应（流式，生成器）
        
        Args:
            query: 包含历史对话的消息列表
            
        Yields:
            str: 模型响应内容分片
        """
        try:
            for chunk in self.get_response_stream(query):
                if chunk:
                    logger.debug(chunk)
                    yield chunk
        except Exception as e:
            logger.error(f"发生错误: {e}")
            yield "发生错误: " + str(e)
    
