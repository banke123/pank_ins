"""
工具套件模块（向后兼容）
从tools文件夹导入所有工具和工具集
"""

# 从新的工具文件夹导入所有内容
from .tools import *

# 保持向后兼容性，重新导出所有内容
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