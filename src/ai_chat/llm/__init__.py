"""
LLM模块
提供大语言模型调用和智能Agent功能
"""

from .llm import ChatLLM
from .agent import UniversalAgent, MathAgent, OscilloscopeAgent
from .base_model import BaseLLM
from .errors import LLMError, AuthenticationError, RateLimitError, ModelError, ConnectionError, ToolNotFoundError
from .chain import test_chain, LLMResponse

# 从工具模块导入所有工具和工具集
from .tools import (
    # 数学工具
    add, subtract, multiply, divide, power, factorial,
    
    # 示波器工具
    set_channel, set_voltage_scale, set_time_scale, set_trigger,
    capture_waveform, measure_frequency, measure_amplitude,
    save_screenshot, reset_oscilloscope,
    
    # 文本工具
    string_length, reverse_string, uppercase, lowercase,
    
    # 工具集
    MATH_TOOLS, OSCILLOSCOPE_TOOLS, TEXT_TOOLS, ALL_TOOLS, TOOL_SETS,
    
    # 工具管理函数
    get_tools_by_name, get_tool_set
)

__all__ = [
    # 基础模型
    "BaseLLM",
    "ChatLLM",
    
    # Agent类
    "UniversalAgent",
    "MathAgent", 
    "OscilloscopeAgent",
    
    # Chain类
    "test_chain",
    "LLMResponse",
    
    # 错误类
    "LLMError",
    "AuthenticationError", 
    "RateLimitError",
    "ModelError",
    "ConnectionError",
    "ToolNotFoundError",
    
    # 数学工具
    "add", "subtract", "multiply", "divide", "power", "factorial",
    
    # 示波器工具
    "set_channel", "set_voltage_scale", "set_time_scale", "set_trigger",
    "capture_waveform", "measure_frequency", "measure_amplitude",
    "save_screenshot", "reset_oscilloscope",
    
    # 文本工具
    "string_length", "reverse_string", "uppercase", "lowercase",
    
    # 工具集
    "MATH_TOOLS", "OSCILLOSCOPE_TOOLS", "TEXT_TOOLS", "ALL_TOOLS", "TOOL_SETS",
    
    # 工具管理函数
    "get_tools_by_name", "get_tool_set"
] 