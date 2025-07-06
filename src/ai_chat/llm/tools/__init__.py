"""
工具套件模块
提供各种可用于Agent的工具函数
"""

from .math_tools import (
    add, subtract, multiply, divide, power, factorial,
    MATH_TOOLS
)

from .oscilloscope_tools import (
    set_channel, set_voltage_scale, set_time_scale, set_trigger,
    capture_waveform, measure_frequency, measure_amplitude,
    save_screenshot, reset_oscilloscope,
    OSCILLOSCOPE_TOOLS
)

from .tool_manager import (
    string_length, reverse_string, uppercase, lowercase,
    get_tools_by_name, get_tool_set, TOOL_SETS,
    TEXT_TOOLS, ALL_TOOLS
)

# 导出所有工具函数
__all__ = [
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