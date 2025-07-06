"""
示波器控制工具
为Agent提供示波器操作功能
"""

import os
import sys
from langchain_core.tools import tool
import time
import random
from typing import Dict, Any

# 添加项目根目录到Python路径
current_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..', '..'))
sys.path.insert(0, project_root)

from src.utils.logger_config import get_logger

logger = get_logger(__name__)

# 模拟示波器状态
class OscilloscopeState:
    """示波器状态管理类"""
    def __init__(self):
        self.channels = {
            1: {"enabled": True, "voltage_scale": 1.0, "coupling": "DC", "probe": "1X"},
            2: {"enabled": False, "voltage_scale": 1.0, "coupling": "DC", "probe": "1X"},
            3: {"enabled": False, "voltage_scale": 1.0, "coupling": "DC", "probe": "1X"},
            4: {"enabled": False, "voltage_scale": 1.0, "coupling": "DC", "probe": "1X"}
        }
        self.time_scale = 1e-3  # 1ms/div
        self.trigger = {
            "source": "CH1",
            "level": 0.0,
            "slope": "RISING",
            "mode": "AUTO"
        }
        self.acquisition = {
            "mode": "NORMAL",
            "sample_rate": 1e9,  # 1GSa/s
            "memory_depth": 1000
        }
        self.measurements = {}
        
    def get_status(self) -> Dict[str, Any]:
        """获取示波器当前状态"""
        return {
            "channels": self.channels,
            "time_scale": self.time_scale,
            "trigger": self.trigger,
            "acquisition": self.acquisition
        }

# 全局示波器状态实例
oscilloscope = OscilloscopeState()

@tool
def set_channel(channel: int, enabled: bool = True, voltage_scale: float = 1.0, 
                coupling: str = "DC", probe: str = "1X") -> str:
    """
    设置示波器通道参数
    
    Args:
        channel: 通道号 (1-4)
        enabled: 是否启用通道
        voltage_scale: 电压刻度 (V/div)
        coupling: 耦合方式 ("DC", "AC", "GND")
        probe: 探头衰减比 ("1X", "10X", "100X")
        
    Returns:
        str: 设置结果描述
        
    Raises:
        ValueError: 当参数无效时抛出
    """
    if channel not in [1, 2, 3, 4]:
        raise ValueError("通道号必须在1-4之间")
    
    if coupling not in ["DC", "AC", "GND"]:
        raise ValueError("耦合方式必须是 DC、AC 或 GND")
    
    if probe not in ["1X", "10X", "100X"]:
        raise ValueError("探头衰减比必须是 1X、10X 或 100X")
    
    if voltage_scale <= 0:
        raise ValueError("电压刻度必须大于0")
    
    oscilloscope.channels[channel] = {
        "enabled": enabled,
        "voltage_scale": voltage_scale,
        "coupling": coupling,
        "probe": probe
    }
    
    status = "启用" if enabled else "禁用"
    result = f"通道{channel}已{status}，电压刻度: {voltage_scale}V/div，耦合: {coupling}，探头: {probe}"
    logger.debug(f"设置示波器通道: {result}")
    return result

@tool
def set_voltage_scale(channel: int, scale: float) -> str:
    """
    设置指定通道的电压刻度
    
    Args:
        channel: 通道号 (1-4)
        scale: 电压刻度 (V/div)
        
    Returns:
        str: 设置结果描述
    """
    if channel not in [1, 2, 3, 4]:
        raise ValueError("通道号必须在1-4之间")
    
    if scale <= 0:
        raise ValueError("电压刻度必须大于0")
    
    if channel not in oscilloscope.channels:
        oscilloscope.channels[channel] = {"enabled": True, "voltage_scale": scale, "coupling": "DC", "probe": "1X"}
    else:
        oscilloscope.channels[channel]["voltage_scale"] = scale
    
    result = f"通道{channel}电压刻度设置为 {scale}V/div"
    logger.debug(f"设置电压刻度: {result}")
    return result

@tool
def set_time_scale(scale: float) -> str:
    """
    设置时间刻度
    
    Args:
        scale: 时间刻度 (s/div)
        
    Returns:
        str: 设置结果描述
    """
    if scale <= 0:
        raise ValueError("时间刻度必须大于0")
    
    oscilloscope.time_scale = scale
    
    # 格式化时间单位显示
    if scale >= 1:
        unit = "s"
        value = scale
    elif scale >= 1e-3:
        unit = "ms"
        value = scale * 1000
    elif scale >= 1e-6:
        unit = "μs"
        value = scale * 1e6
    else:
        unit = "ns"
        value = scale * 1e9
    
    result = f"时间刻度设置为 {value:.2f}{unit}/div"
    logger.debug(f"设置时间刻度: {result}")
    return result

@tool
def set_trigger(source: str = "CH1", level: float = 0.0, slope: str = "RISING", mode: str = "AUTO") -> str:
    """
    设置触发参数
    
    Args:
        source: 触发源 ("CH1", "CH2", "CH3", "CH4", "EXT")
        level: 触发电平 (V)
        slope: 触发边沿 ("RISING", "FALLING")
        mode: 触发模式 ("AUTO", "NORMAL", "SINGLE")
        
    Returns:
        str: 设置结果描述
    """
    valid_sources = ["CH1", "CH2", "CH3", "CH4", "EXT"]
    if source not in valid_sources:
        raise ValueError(f"触发源必须是: {', '.join(valid_sources)}")
    
    if slope not in ["RISING", "FALLING"]:
        raise ValueError("触发边沿必须是 RISING 或 FALLING")
    
    if mode not in ["AUTO", "NORMAL", "SINGLE"]:
        raise ValueError("触发模式必须是 AUTO、NORMAL 或 SINGLE")
    
    oscilloscope.trigger = {
        "source": source,
        "level": level,
        "slope": slope,
        "mode": mode
    }
    
    result = f"触发设置: 源={source}, 电平={level}V, 边沿={slope}, 模式={mode}"
    logger.debug(f"设置触发: {result}")
    return result

@tool
def capture_waveform(channel: int = 1) -> str:
    """
    捕获指定通道的波形数据
    
    Args:
        channel: 通道号 (1-4)
        
    Returns:
        str: 捕获结果描述
    """
    if channel not in [1, 2, 3, 4]:
        raise ValueError("通道号必须在1-4之间")
    
    if not oscilloscope.channels.get(channel, {}).get("enabled", False):
        raise ValueError(f"通道{channel}未启用，无法捕获波形")
    
    # 模拟捕获过程
    time.sleep(0.1)  # 模拟捕获延时
    
    # 生成模拟波形数据
    sample_count = oscilloscope.acquisition["memory_depth"]
    frequency = random.uniform(100000, 400000)  # 100-400kHz
    amplitude = random.uniform(1.8, 3.6)     # 1.8-3.6V
    
    result = f"通道{channel}波形捕获完成: 采样点数={sample_count}, 估计频率={frequency:.1f}Hz, 估计幅度={amplitude:.2f}V"
    logger.debug(f"捕获波形: {result}")
    return result

@tool
def measure_frequency(channel: int = 1) -> str:
    """
    测量指定通道的频率
    
    Args:
        channel: 通道号 (1-4)
        
    Returns:
        str: 频率测量结果
    """
    if channel not in [1, 2, 3, 4]:
        raise ValueError("通道号必须在1-4之间")
    
    if not oscilloscope.channels.get(channel, {}).get("enabled", False):
        raise ValueError(f"通道{channel}未启用，无法测量频率")
    
    # 模拟频率测量
    # frequency = random.uniform(100000, 400000)  # 100kHz - 400kHz
    frequency = 100000
    
    # 格式化频率单位
    if frequency >= 1000000:
        unit = "MHz"
        value = frequency / 1000000
    elif frequency >= 1000:
        unit = "kHz"
        value = frequency / 1000
    else:
        unit = "Hz"
        value = frequency
    
    result = f"通道{channel}频率测量: {value:.3f}{unit}"
    logger.debug(f"测量频率: {result}")
    return result

@tool
def measure_amplitude(channel: int = 1) -> str:
    """
    测量指定通道的幅度
    
    Args:
        channel: 通道号 (1-4)
        
    Returns:
        str: 幅度测量结果
    """
    if channel not in [1, 2, 3, 4]:
        raise ValueError("通道号必须在1-4之间")
    
    if not oscilloscope.channels.get(channel, {}).get("enabled", False):
        raise ValueError(f"通道{channel}未启用，无法测量幅度")
    
    # 模拟幅度测量
    vpp = random.uniform(3.0, 3.6)    # 峰峰值
    vrms = random.uniform(0.5, 3)          # 有效值
    vmax = random.uniform(3.0, 3.6)                     # 最大值
    vmin = random.uniform(0, 0.5)                   # 最小值
    
    result = f"通道{channel}幅度测量: Vpp={vpp:.3f}V, Vrms={vrms:.3f}V, Vmax={vmax:.3f}V, Vmin={vmin:.3f}V"
    logger.debug(f"测量幅度: {result}")
    return result

@tool
def save_screenshot(filename: str = "oscilloscope_screen.png") -> str:
    """
    保存示波器屏幕截图
    
    Args:
        filename: 保存的文件名
        
    Returns:
        str: 保存结果描述
    """
    if not filename.endswith(('.png', '.jpg', '.bmp')):
        filename += '.png'
    
    # 模拟保存过程
    time.sleep(0.2)
    
    result = f"屏幕截图已保存为: {filename}"
    logger.debug(f"保存截图: {result}")
    return result

@tool
def reset_oscilloscope() -> str:
    """
    重置示波器到默认设置
    
    Returns:
        str: 重置结果描述
    """
    global oscilloscope
    oscilloscope = OscilloscopeState()
    
    result = "示波器已重置到默认设置"
    logger.debug(f"重置示波器: {result}")
    return result

# 示波器工具集合
OSCILLOSCOPE_TOOLS = [
    set_channel, set_voltage_scale, set_time_scale, set_trigger,
    capture_waveform, measure_frequency, measure_amplitude,
    save_screenshot, reset_oscilloscope
] 