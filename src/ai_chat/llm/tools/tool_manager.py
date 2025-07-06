"""
工具管理器
提供工具集管理和工具获取功能
"""

import os
import sys
from typing import List, Dict, Any

# 添加项目根目录到Python路径
current_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..', '..'))
sys.path.insert(0, project_root)

from src.utils.logger_config import get_logger
from langchain_core.tools import tool
from .math_tools import MATH_TOOLS
from .oscilloscope_tools import OSCILLOSCOPE_TOOLS

logger = get_logger(__name__)

# 文本处理工具套件
@tool
def string_length(text: str) -> int:
    """
    计算字符串长度
    
    Args:
        text: 输入字符串
        
    Returns:
        int: 字符串长度
    """
    result = len(text)
    logger.debug(f"计算字符串长度: '{text}' = {result}")
    return result

@tool
def reverse_string(text: str) -> str:
    """
    反转字符串
    
    Args:
        text: 输入字符串
        
    Returns:
        str: 反转后的字符串
    """
    result = text[::-1]
    logger.debug(f"反转字符串: '{text}' -> '{result}'")
    return result

@tool
def uppercase(text: str) -> str:
    """
    转换为大写
    
    Args:
        text: 输入字符串
        
    Returns:
        str: 大写字符串
    """
    result = text.upper()
    logger.debug(f"转换大写: '{text}' -> '{result}'")
    return result

@tool
def lowercase(text: str) -> str:
    """
    转换为小写
    
    Args:
        text: 输入字符串
        
    Returns:
        str: 小写字符串
    """
    result = text.lower()
    logger.debug(f"转换小写: '{text}' -> '{result}'")
    return result

# 文本工具集合
TEXT_TOOLS = [string_length, reverse_string, uppercase, lowercase]

# 所有工具集合
ALL_TOOLS = MATH_TOOLS + OSCILLOSCOPE_TOOLS + TEXT_TOOLS

# 工具集合字典，方便按名称获取
TOOL_SETS = {
    "math": MATH_TOOLS,
    "oscilloscope": OSCILLOSCOPE_TOOLS,
    "text": TEXT_TOOLS,
    "all": ALL_TOOLS
}

def get_tools_by_name(tool_names: list) -> list:
    """
    根据工具名称获取工具列表
    
    Args:
        tool_names: 工具名称列表
        
    Returns:
        list: 工具对象列表
        
    Raises:
        ValueError: 当工具名称不存在时抛出
    """
    # 创建工具名称到工具对象的映射
    tool_map = {tool.name: tool for tool in ALL_TOOLS}
    
    tools = []
    for name in tool_names:
        if name not in tool_map:
            available_tools = list(tool_map.keys())
            raise ValueError(f"工具 '{name}' 不存在。可用工具: {available_tools}")
        tools.append(tool_map[name])
    
    logger.debug(f"获取工具: {tool_names}")
    return tools

def get_tool_set(set_name: str) -> list:
    """
    根据工具集名称获取工具列表
    
    Args:
        set_name: 工具集名称 ("math", "oscilloscope", "text", "all")
        
    Returns:
        list: 工具对象列表
        
    Raises:
        ValueError: 当工具集名称不存在时抛出
    """
    if set_name not in TOOL_SETS:
        available_sets = list(TOOL_SETS.keys())
        raise ValueError(f"工具集 '{set_name}' 不存在。可用工具集: {available_sets}")
    
    tools = TOOL_SETS[set_name]
    logger.debug(f"获取工具集 '{set_name}': {[tool.name for tool in tools]}")
    return tools 