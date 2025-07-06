"""
全面的示波器仪器控制工具套件
提供示波器仪器的完整模拟控制功能，包括各种高级测量
"""

from langchain_core.tools import tool
from src.utils.logger_config import get_logger
import time
import random
import math
from typing import Dict, Any, List, Tuple
from enum import Enum

logger = get_logger(__name__)

class CouplingMode(Enum):
    """耦合模式枚举"""
    DC = "DC"
    AC = "AC"
    GND = "GND"

class TriggerSlope(Enum):
    """触发边沿枚举"""
    RISING = "RISING"
    FALLING = "FALLING"
    BOTH = "BOTH"

class TriggerMode(Enum):
    """触发模式枚举"""
    AUTO = "AUTO"
    NORMAL = "NORMAL"
    SINGLE = "SINGLE"

class AcquisitionMode(Enum):
    """采集模式枚举"""
    NORMAL = "NORMAL"
    PEAK_DETECT = "PEAK_DETECT"
    AVERAGE = "AVERAGE"
    HIGH_RESOLUTION = "HIGH_RESOLUTION"

# 模拟示波器状态
class AdvancedOscilloscopeState:
    """高级示波器状态管理类"""
    def __init__(self):
        self.channels = {
            1: {
                "enabled": True, 
                "voltage_scale": 1.0, 
                "coupling": CouplingMode.DC.value, 
                "probe": "1X",
                "offset": 0.0,
                "bandwidth_limit": False,
                "invert": False
            },
            2: {
                "enabled": False, 
                "voltage_scale": 1.0, 
                "coupling": CouplingMode.DC.value, 
                "probe": "1X",
                "offset": 0.0,
                "bandwidth_limit": False,
                "invert": False
            },
            3: {
                "enabled": False, 
                "voltage_scale": 1.0, 
                "coupling": CouplingMode.DC.value, 
                "probe": "1X",
                "offset": 0.0,
                "bandwidth_limit": False,
                "invert": False
            },
            4: {
                "enabled": False, 
                "voltage_scale": 1.0, 
                "coupling": CouplingMode.DC.value, 
                "probe": "1X",
                "offset": 0.0,
                "bandwidth_limit": False,
                "invert": False
            }
        }
        self.time_scale = 1e-3  # 1ms/div
        self.time_offset = 0.0  # 时间偏移
        self.trigger = {
            "source": "CH1",
            "level": 0.0,
            "slope": TriggerSlope.RISING.value,
            "mode": TriggerMode.AUTO.value,
            "holdoff": 100e-9,  # 触发抑制时间
            "noise_reject": False,
            "high_frequency_reject": False
        }
        self.acquisition = {
            "mode": AcquisitionMode.NORMAL.value,
            "sample_rate": 1e9,  # 1GSa/s
            "memory_depth": 1000,
            "averages": 16,
            "run_stop": True,
            "vertical_noise_reduction": False,
            "reduction_ratio": "10:1"
        }
        self.measurements = {}
        self.math_channels = {
            "MATH1": {"enabled": False, "expression": "CH1+CH2", "scale": 1.0},
            "MATH2": {"enabled": False, "expression": "CH1-CH2", "scale": 1.0}
        }
        self.cursors = {
            "enabled": False,
            "type": "VOLTAGE",  # VOLTAGE, TIME, TRACK
            "cursor1": {"position": 0.0},
            "cursor2": {"position": 0.0}
        }
        
    def get_status(self) -> Dict[str, Any]:
        """获取示波器当前状态"""
        return {
            "channels": self.channels,
            "time_scale": self.time_scale,
            "time_offset": self.time_offset,
            "trigger": self.trigger,
            "acquisition": self.acquisition,
            "math_channels": self.math_channels,
            "cursors": self.cursors
        }

# 全局示波器状态实例
advanced_oscilloscope = AdvancedOscilloscopeState()

@tool
def set_channel_advanced(channel: int, enabled: bool = True, voltage_scale: float = 1.0, 
                        coupling: str = "DC", probe: str = "1X", offset: float = 0.0,
                        bandwidth_limit: bool = False, invert: bool = False) -> str:
    """
    设置示波器通道高级参数
    
    Args:
        channel: 通道号 (1-4)
        enabled: 是否启用通道
        voltage_scale: 电压刻度 (V/div)
        coupling: 耦合方式 ("DC", "AC", "GND")
        probe: 探头衰减比 ("1X", "10X", "100X")
        offset: 垂直偏移 (V)
        bandwidth_limit: 是否启用带宽限制
        invert: 是否反相显示
        
    Returns:
        str: 设置结果描述
    """
    if channel not in [1, 2, 3, 4]:
        raise ValueError("通道号必须在1-4之间")
    
    if coupling not in ["DC", "AC", "GND"]:
        raise ValueError("耦合方式必须是 DC、AC 或 GND")
    
    if probe not in ["1X", "10X", "100X"]:
        raise ValueError("探头衰减比必须是 1X、10X 或 100X")
    
    if voltage_scale <= 0:
        raise ValueError("电压刻度必须大于0")
    
    advanced_oscilloscope.channels[channel] = {
        "enabled": enabled,
        "voltage_scale": voltage_scale,
        "coupling": coupling,
        "probe": probe,
        "offset": offset,
        "bandwidth_limit": bandwidth_limit,
        "invert": invert
    }
    
    status = "启用" if enabled else "禁用"
    bw_status = "启用" if bandwidth_limit else "禁用"
    inv_status = "启用" if invert else "禁用"
    
    result = (f"通道{channel}已{status}，电压刻度: {voltage_scale}V/div，耦合: {coupling}，"
             f"探头: {probe}，偏移: {offset}V，带宽限制: {bw_status}，反相: {inv_status}")
    
    logger.debug(f"设置示波器通道: {result}")
    return result

@tool
def set_time_base_advanced(scale: float, offset: float = 0.0) -> str:
    """
    设置时间基准（高级）
    
    Args:
        scale: 时间刻度 (s/div)
        offset: 时间偏移 (s)
        
    Returns:
        str: 设置结果描述
    """
    if scale <= 0:
        raise ValueError("时间刻度必须大于0")
    
    advanced_oscilloscope.time_scale = scale
    advanced_oscilloscope.time_offset = offset
    
    # 格式化时间单位显示
    def format_time(value):
        if abs(value) >= 1:
            return f"{value:.3f}s"
        elif abs(value) >= 1e-3:
            return f"{value*1000:.3f}ms"
        elif abs(value) >= 1e-6:
            return f"{value*1e6:.3f}μs"
        else:
            return f"{value*1e9:.3f}ns"
    
    result = f"时间基准设置: 刻度={format_time(scale)}/div，偏移={format_time(offset)}"
    logger.debug(f"设置时间基准: {result}")
    return result

@tool
def set_trigger_advanced(source: str = "CH1", level: float = 0.0, slope: str = "RISING", 
                        mode: str = "AUTO", holdoff: float = 100e-9, 
                        noise_reject: bool = False, hf_reject: bool = False) -> str:
    """
    设置高级触发参数
    
    Args:
        source: 触发源 ("CH1", "CH2", "CH3", "CH4", "EXT", "LINE")
        level: 触发电平 (V)
        slope: 触发边沿 ("RISING", "FALLING", "BOTH")
        mode: 触发模式 ("AUTO", "NORMAL", "SINGLE")
        holdoff: 触发抑制时间 (s)
        noise_reject: 噪声抑制
        hf_reject: 高频抑制
        
    Returns:
        str: 设置结果描述
    """
    valid_sources = ["CH1", "CH2", "CH3", "CH4", "EXT", "LINE"]
    if source not in valid_sources:
        raise ValueError(f"触发源必须是: {', '.join(valid_sources)}")
    
    if slope not in ["RISING", "FALLING", "BOTH"]:
        raise ValueError("触发边沿必须是 RISING、FALLING 或 BOTH")
    
    if mode not in ["AUTO", "NORMAL", "SINGLE"]:
        raise ValueError("触发模式必须是 AUTO、NORMAL 或 SINGLE")
    
    if holdoff < 0:
        raise ValueError("触发抑制时间不能为负数")
    
    advanced_oscilloscope.trigger = {
        "source": source,
        "level": level,
        "slope": slope,
        "mode": mode,
        "holdoff": holdoff,
        "noise_reject": noise_reject,
        "high_frequency_reject": hf_reject
    }
    
    result = (f"触发设置: 源={source}, 电平={level}V, 边沿={slope}, 模式={mode}, "
             f"抑制={holdoff*1e9:.1f}ns, 噪声抑制={'开' if noise_reject else '关'}, "
             f"高频抑制={'开' if hf_reject else '关'}")
    
    logger.debug(f"设置触发: {result}")
    return result

@tool
def measure_rise_time(channel: int = 1, threshold_low: float = 10.0, threshold_high: float = 90.0) -> str:
    """
    测量上升时间
    
    Args:
        channel: 通道号 (1-4)
        threshold_low: 低阈值百分比 (默认10%)
        threshold_high: 高阈值百分比 (默认90%)
        
    Returns:
        str: 上升时间测量结果
    """
    if channel not in [1, 2, 3, 4]:
        raise ValueError("通道号必须在1-4之间")
    
    if not advanced_oscilloscope.channels.get(channel, {}).get("enabled", False):
        raise ValueError(f"通道{channel}未启用，无法测量上升时间")
    
    if not (0 < threshold_low < threshold_high < 100):
        raise ValueError("阈值必须满足: 0 < 低阈值 < 高阈值 < 100")
    
    # 模拟上升时间测量
    base_rise_time = random.uniform(1e-9, 50e-9)  # 1ns - 50ns
    
    # 根据时间刻度调整测量精度
    time_scale = advanced_oscilloscope.time_scale
    if time_scale > 1e-6:  # 大于1μs/div时，上升时间相对较长
        rise_time = base_rise_time * random.uniform(10, 100)
    else:
        rise_time = base_rise_time
    
    # 格式化时间单位
    if rise_time >= 1e-6:
        unit = "μs"
        value = rise_time * 1e6
    elif rise_time >= 1e-9:
        unit = "ns"
        value = rise_time * 1e9
    else:
        unit = "ps"
        value = rise_time * 1e12
    
    result = f"通道{channel}上升时间({threshold_low}%-{threshold_high}%): {value:.2f}{unit}"
    logger.debug(f"测量上升时间: {result}")
    return result

@tool
def measure_fall_time(channel: int = 1, threshold_high: float = 90.0, threshold_low: float = 10.0) -> str:
    """
    测量下降时间
    
    Args:
        channel: 通道号 (1-4)
        threshold_high: 高阈值百分比 (默认90%)
        threshold_low: 低阈值百分比 (默认10%)
        
    Returns:
        str: 下降时间测量结果
    """
    if channel not in [1, 2, 3, 4]:
        raise ValueError("通道号必须在1-4之间")
    
    if not advanced_oscilloscope.channels.get(channel, {}).get("enabled", False):
        raise ValueError(f"通道{channel}未启用，无法测量下降时间")
    
    if not (0 < threshold_low < threshold_high < 100):
        raise ValueError("阈值必须满足: 0 < 低阈值 < 高阈值 < 100")
    
    # 模拟下降时间测量
    base_fall_time = random.uniform(1e-9, 45e-9)  # 1ns - 45ns
    
    # 根据时间刻度调整测量精度
    time_scale = advanced_oscilloscope.time_scale
    if time_scale > 1e-6:
        fall_time = base_fall_time * random.uniform(8, 80)
    else:
        fall_time = base_fall_time
    
    # 格式化时间单位
    if fall_time >= 1e-6:
        unit = "μs"
        value = fall_time * 1e6
    elif fall_time >= 1e-9:
        unit = "ns"
        value = fall_time * 1e9
    else:
        unit = "ps"
        value = fall_time * 1e12
    
    result = f"通道{channel}下降时间({threshold_high}%-{threshold_low}%): {value:.2f}{unit}"
    logger.debug(f"测量下降时间: {result}")
    return result

@tool
def measure_duty_cycle(channel: int = 1) -> str:
    """
    测量占空比
    
    Args:
        channel: 通道号 (1-4)
        
    Returns:
        str: 占空比测量结果
    """
    if channel not in [1, 2, 3, 4]:
        raise ValueError("通道号必须在1-4之间")
    
    if not advanced_oscilloscope.channels.get(channel, {}).get("enabled", False):
        raise ValueError(f"通道{channel}未启用，无法测量占空比")
    
    # 模拟占空比测量
    duty_cycle = random.uniform(20.0, 80.0)  # 20% - 80%
    
    result = f"通道{channel}占空比: {duty_cycle:.2f}%"
    logger.debug(f"测量占空比: {result}")
    return result

@tool
def measure_pulse_width(channel: int = 1, polarity: str = "POSITIVE") -> str:
    """
    测量脉宽
    
    Args:
        channel: 通道号 (1-4)
        polarity: 脉冲极性 ("POSITIVE", "NEGATIVE")
        
    Returns:
        str: 脉宽测量结果
    """
    if channel not in [1, 2, 3, 4]:
        raise ValueError("通道号必须在1-4之间")
    
    if not advanced_oscilloscope.channels.get(channel, {}).get("enabled", False):
        raise ValueError(f"通道{channel}未启用，无法测量脉宽")
    
    if polarity not in ["POSITIVE", "NEGATIVE"]:
        raise ValueError("脉冲极性必须是 POSITIVE 或 NEGATIVE")
    
    # 模拟脉宽测量
    time_scale = advanced_oscilloscope.time_scale
    base_width = time_scale * random.uniform(0.5, 3.0)  # 基于时间刻度的脉宽
    
    # 格式化时间单位
    if base_width >= 1e-3:
        unit = "ms"
        value = base_width * 1000
    elif base_width >= 1e-6:
        unit = "μs"
        value = base_width * 1e6
    elif base_width >= 1e-9:
        unit = "ns"
        value = base_width * 1e9
    else:
        unit = "ps"
        value = base_width * 1e12
    
    polarity_str = "正" if polarity == "POSITIVE" else "负"
    result = f"通道{channel}{polarity_str}脉宽: {value:.2f}{unit}"
    logger.debug(f"测量脉宽: {result}")
    return result

@tool
def measure_period(channel: int = 1) -> str:
    """
    测量周期
    
    Args:
        channel: 通道号 (1-4)
        
    Returns:
        str: 周期测量结果
    """
    if channel not in [1, 2, 3, 4]:
        raise ValueError("通道号必须在1-4之间")
    
    if not advanced_oscilloscope.channels.get(channel, {}).get("enabled", False):
        raise ValueError(f"通道{channel}未启用，无法测量周期")
    
    # 模拟周期测量（基于100kHz基准频率）
    base_frequency = 100000  # 100kHz
    frequency_variation = random.uniform(0.8, 1.2)
    actual_frequency = base_frequency * frequency_variation
    period = 1.0 / actual_frequency
    
    # 格式化时间单位
    if period >= 1e-3:
        unit = "ms"
        value = period * 1000
    elif period >= 1e-6:
        unit = "μs"
        value = period * 1e6
    elif period >= 1e-9:
        unit = "ns"
        value = period * 1e9
    else:
        unit = "ps"
        value = period * 1e12
    
    result = f"通道{channel}周期: {value:.3f}{unit}"
    logger.debug(f"测量周期: {result}")
    return result

@tool
def measure_phase_difference(channel1: int = 1, channel2: int = 2) -> str:
    """
    测量两个通道之间的相位差
    
    Args:
        channel1: 参考通道号 (1-4)
        channel2: 比较通道号 (1-4)
        
    Returns:
        str: 相位差测量结果
    """
    if channel1 not in [1, 2, 3, 4] or channel2 not in [1, 2, 3, 4]:
        raise ValueError("通道号必须在1-4之间")
    
    if channel1 == channel2:
        raise ValueError("两个通道不能相同")
    
    if not advanced_oscilloscope.channels.get(channel1, {}).get("enabled", False):
        raise ValueError(f"通道{channel1}未启用")
    
    if not advanced_oscilloscope.channels.get(channel2, {}).get("enabled", False):
        raise ValueError(f"通道{channel2}未启用")
    
    # 模拟相位差测量
    phase_diff_degrees = random.uniform(-180.0, 180.0)
    phase_diff_radians = math.radians(phase_diff_degrees)
    
    result = f"通道{channel1}到通道{channel2}相位差: {phase_diff_degrees:.2f}° ({phase_diff_radians:.3f}rad)"
    logger.debug(f"测量相位差: {result}")
    return result

@tool
def measure_delay(channel1: int = 1, channel2: int = 2) -> str:
    """
    测量两个通道之间的延迟时间
    
    Args:
        channel1: 参考通道号 (1-4)
        channel2: 比较通道号 (1-4)
        
    Returns:
        str: 延迟时间测量结果
    """
    if channel1 not in [1, 2, 3, 4] or channel2 not in [1, 2, 3, 4]:
        raise ValueError("通道号必须在1-4之间")
    
    if channel1 == channel2:
        raise ValueError("两个通道不能相同")
    
    if not advanced_oscilloscope.channels.get(channel1, {}).get("enabled", False):
        raise ValueError(f"通道{channel1}未启用")
    
    if not advanced_oscilloscope.channels.get(channel2, {}).get("enabled", False):
        raise ValueError(f"通道{channel2}未启用")
    
    # 模拟延迟测量
    time_scale = advanced_oscilloscope.time_scale
    max_delay = time_scale * 2  # 最大延迟为2个时间刻度
    delay = random.uniform(-max_delay, max_delay)
    
    # 格式化时间单位
    if abs(delay) >= 1e-3:
        unit = "ms"
        value = delay * 1000
    elif abs(delay) >= 1e-6:
        unit = "μs"
        value = delay * 1e6
    elif abs(delay) >= 1e-9:
        unit = "ns"
        value = delay * 1e9
    else:
        unit = "ps"
        value = delay * 1e12
    
    direction = "滞后" if delay > 0 else "超前"
    result = f"通道{channel2}相对于通道{channel1}{direction}: {abs(value):.2f}{unit}"
    logger.debug(f"测量延迟: {result}")
    return result

@tool
def measure_overshoot(channel: int = 1) -> str:
    """
    测量过冲
    
    Args:
        channel: 通道号 (1-4)
        
    Returns:
        str: 过冲测量结果
    """
    if channel not in [1, 2, 3, 4]:
        raise ValueError("通道号必须在1-4之间")
    
    if not advanced_oscilloscope.channels.get(channel, {}).get("enabled", False):
        raise ValueError(f"通道{channel}未启用，无法测量过冲")
    
    # 模拟过冲测量
    overshoot_percent = random.uniform(0.0, 15.0)  # 0% - 15%
    overshoot_voltage = random.uniform(0.0, 0.5)   # 0V - 0.5V
    
    result = f"通道{channel}过冲: {overshoot_percent:.2f}% ({overshoot_voltage:.3f}V)"
    logger.debug(f"测量过冲: {result}")
    return result

@tool
def measure_undershoot(channel: int = 1) -> str:
    """
    测量下冲
    
    Args:
        channel: 通道号 (1-4)
        
    Returns:
        str: 下冲测量结果
    """
    if channel not in [1, 2, 3, 4]:
        raise ValueError("通道号必须在1-4之间")
    
    if not advanced_oscilloscope.channels.get(channel, {}).get("enabled", False):
        raise ValueError(f"通道{channel}未启用，无法测量下冲")
    
    # 模拟下冲测量
    undershoot_percent = random.uniform(0.0, 12.0)  # 0% - 12%
    undershoot_voltage = random.uniform(0.0, 0.4)   # 0V - 0.4V
    
    result = f"通道{channel}下冲: {undershoot_percent:.2f}% ({undershoot_voltage:.3f}V)"
    logger.debug(f"测量下冲: {result}")
    return result

@tool
def measure_rms(channel: int = 1) -> str:
    """
    测量RMS有效值
    
    Args:
        channel: 通道号 (1-4)
        
    Returns:
        str: RMS测量结果
    """
    if channel not in [1, 2, 3, 4]:
        raise ValueError("通道号必须在1-4之间")
    
    if not advanced_oscilloscope.channels.get(channel, {}).get("enabled", False):
        raise ValueError(f"通道{channel}未启用，无法测量RMS")
    
    # 模拟RMS测量
    voltage_scale = advanced_oscilloscope.channels[channel]["voltage_scale"]
    base_rms = voltage_scale * random.uniform(0.3, 0.8)  # 基于电压刻度的RMS值
    
    # 根据耦合方式调整RMS值
    coupling = advanced_oscilloscope.channels[channel]["coupling"]
    if coupling == "AC":
        rms_value = base_rms * random.uniform(0.7, 1.0)
    else:  # DC或GND
        rms_value = base_rms
    
    result = f"通道{channel} RMS有效值: {rms_value:.4f}V"
    logger.debug(f"测量RMS: {result}")
    return result

@tool
def measure_peak_to_peak(channel: int = 1) -> str:
    """
    测量峰峰值
    
    Args:
        channel: 通道号 (1-4)
        
    Returns:
        str: 峰峰值测量结果
    """
    if channel not in [1, 2, 3, 4]:
        raise ValueError("通道号必须在1-4之间")
    
    if not advanced_oscilloscope.channels.get(channel, {}).get("enabled", False):
        raise ValueError(f"通道{channel}未启用，无法测量峰峰值")
    
    # 模拟峰峰值测量
    voltage_scale = advanced_oscilloscope.channels[channel]["voltage_scale"]
    peak_to_peak = voltage_scale * random.uniform(1.5, 6.0)  # 基于电压刻度的峰峰值
    
    # 计算正峰值和负峰值
    offset = advanced_oscilloscope.channels[channel]["offset"]
    positive_peak = offset + peak_to_peak / 2
    negative_peak = offset - peak_to_peak / 2
    
    result = f"通道{channel} 峰峰值: {peak_to_peak:.4f}V (正峰: {positive_peak:.4f}V, 负峰: {negative_peak:.4f}V)"
    logger.debug(f"测量峰峰值: {result}")
    return result

@tool
def set_acquisition_mode(mode: str = "HIGH_RESOLUTION", memory_depth: str = "1M", 
                        vertical_noise_reduction: bool = True, reduction_ratio: str = "10:1") -> str:
    """
    设置采集模式和参数
    
    Args:
        mode: 采集模式 ("NORMAL", "PEAK_DETECT", "AVERAGE", "HIGH_RESOLUTION")
        memory_depth: 存储深度 ("1K", "10K", "100K", "1M", "10M", "100M")
        vertical_noise_reduction: 是否启用垂直降噪
        reduction_ratio: 降噪比例 ("2:1", "4:1", "10:1", "20:1")
        
    Returns:
        str: 设置结果描述
    """
    valid_modes = ["NORMAL", "PEAK_DETECT", "AVERAGE", "HIGH_RESOLUTION"]
    if mode not in valid_modes:
        raise ValueError(f"采集模式必须是: {', '.join(valid_modes)}")
    
    valid_depths = ["1K", "10K", "100K", "1M", "10M", "100M"]
    if memory_depth not in valid_depths:
        raise ValueError(f"存储深度必须是: {', '.join(valid_depths)}")
    
    valid_ratios = ["2:1", "4:1", "10:1", "20:1"]
    if reduction_ratio not in valid_ratios:
        raise ValueError(f"降噪比例必须是: {', '.join(valid_ratios)}")
    
    # 更新采集设置
    advanced_oscilloscope.acquisition["mode"] = mode
    
    # 转换存储深度为数值
    depth_map = {
        "1K": 1000, "10K": 10000, "100K": 100000,
        "1M": 1000000, "10M": 10000000, "100M": 100000000
    }
    advanced_oscilloscope.acquisition["memory_depth"] = depth_map[memory_depth]
    
    # 设置降噪参数
    advanced_oscilloscope.acquisition["vertical_noise_reduction"] = vertical_noise_reduction
    advanced_oscilloscope.acquisition["reduction_ratio"] = reduction_ratio
    
    # 根据模式调整采样率
    if mode == "HIGH_RESOLUTION":
        advanced_oscilloscope.acquisition["sample_rate"] = 500e6  # 500MSa/s，高分辨率模式
    elif mode == "PEAK_DETECT":
        advanced_oscilloscope.acquisition["sample_rate"] = 2e9   # 2GSa/s，峰值检测模式
    else:
        advanced_oscilloscope.acquisition["sample_rate"] = 1e9   # 1GSa/s，正常模式
    
    noise_status = f"启用({reduction_ratio})" if vertical_noise_reduction else "禁用"
    
    result = (f"采集设置: 模式={mode}, 存储深度={memory_depth}点, "
             f"采样率={advanced_oscilloscope.acquisition['sample_rate']/1e6:.0f}MSa/s, "
             f"垂直降噪={noise_status}")
    
    logger.debug(f"设置采集模式: {result}")
    return result

@tool
def start_timer(duration_seconds: float = 10.0, timer_name: str = "测量定时器") -> str:
    """
    启动定时器
    
    Args:
        duration_seconds: 定时器持续时间（秒）
        timer_name: 定时器名称
        
    Returns:
        str: 定时器启动结果
    """
    if duration_seconds <= 0:
        raise ValueError("定时器持续时间必须大于0")
    
    if duration_seconds > 3600:  # 限制最大1小时
        raise ValueError("定时器持续时间不能超过3600秒（1小时）")
    
    # 将定时器信息存储到示波器状态中
    if not hasattr(advanced_oscilloscope, 'timers'):
        advanced_oscilloscope.timers = {}
    
    timer_id = f"timer_{len(advanced_oscilloscope.timers) + 1}"
    start_time = time.time()
    
    advanced_oscilloscope.timers[timer_id] = {
        "name": timer_name,
        "start_time": start_time,
        "duration": duration_seconds,
        "end_time": start_time + duration_seconds,
        "status": "running"
    }
    
    # 格式化时间显示
    if duration_seconds >= 60:
        time_str = f"{duration_seconds/60:.1f}分钟"
    else:
        time_str = f"{duration_seconds:.1f}秒"
    
    result = f"定时器 '{timer_name}' 已启动，持续时间: {time_str} (ID: {timer_id})"
    logger.debug(f"启动定时器: {result}")
    return result

@tool
def check_timer_status(timer_id: str = None) -> str:
    """
    检查定时器状态
    
    Args:
        timer_id: 定时器ID，如果为None则显示所有定时器状态
        
    Returns:
        str: 定时器状态信息
    """
    if not hasattr(advanced_oscilloscope, 'timers') or not advanced_oscilloscope.timers:
        return "当前没有运行的定时器"
    
    current_time = time.time()
    
    if timer_id:
        # 检查特定定时器
        if timer_id not in advanced_oscilloscope.timers:
            return f"定时器 {timer_id} 不存在"
        
        timer = advanced_oscilloscope.timers[timer_id]
        remaining = timer["end_time"] - current_time
        
        if remaining <= 0:
            timer["status"] = "completed"
            result = f"定时器 '{timer['name']}' (ID: {timer_id}) 已完成"
        else:
            if remaining >= 60:
                time_str = f"{remaining/60:.1f}分钟"
            else:
                time_str = f"{remaining:.1f}秒"
            result = f"定时器 '{timer['name']}' (ID: {timer_id}) 剩余时间: {time_str}"
    else:
        # 显示所有定时器状态
        status_lines = ["=== 定时器状态 ==="]
        for tid, timer in advanced_oscilloscope.timers.items():
            remaining = timer["end_time"] - current_time
            if remaining <= 0:
                timer["status"] = "completed"
                status_lines.append(f"{tid}: '{timer['name']}' - 已完成")
            else:
                if remaining >= 60:
                    time_str = f"{remaining/60:.1f}分钟"
                else:
                    time_str = f"{remaining:.1f}秒"
                status_lines.append(f"{tid}: '{timer['name']}' - 剩余 {time_str}")
        
        result = "\n".join(status_lines)
    
    logger.debug(f"检查定时器状态: {result}")
    return result

@tool
def stop_timer(timer_id: str) -> str:
    """
    停止定时器
    
    Args:
        timer_id: 定时器ID
        
    Returns:
        str: 停止结果
    """
    if not hasattr(advanced_oscilloscope, 'timers') or not advanced_oscilloscope.timers:
        return "当前没有运行的定时器"
    
    if timer_id not in advanced_oscilloscope.timers:
        return f"定时器 {timer_id} 不存在"
    
    timer = advanced_oscilloscope.timers[timer_id]
    timer["status"] = "stopped"
    
    elapsed = time.time() - timer["start_time"]
    if elapsed >= 60:
        time_str = f"{elapsed/60:.1f}分钟"
    else:
        time_str = f"{elapsed:.1f}秒"
    
    result = f"定时器 '{timer['name']}' (ID: {timer_id}) 已停止，运行时间: {time_str}"
    logger.debug(f"停止定时器: {result}")
    return result

@tool
def clear_all_timers() -> str:
    """
    清除所有定时器
    
    Returns:
        str: 清除结果
    """
    if not hasattr(advanced_oscilloscope, 'timers'):
        advanced_oscilloscope.timers = {}
    
    timer_count = len(advanced_oscilloscope.timers)
    advanced_oscilloscope.timers.clear()
    
    result = f"已清除 {timer_count} 个定时器"
    logger.debug(f"清除定时器: {result}")
    return result

@tool
def set_math_channel(math_channel: str = "MATH1", expression: str = "CH1+CH2", 
                    enabled: bool = True, scale: float = 1.0) -> str:
    """
    设置数学运算通道
    
    Args:
        math_channel: 数学通道名称 ("MATH1", "MATH2")
        expression: 数学表达式 (如 "CH1+CH2", "CH1-CH2", "CH1*CH2", "FFT(CH1)")
        enabled: 是否启用
        scale: 垂直刻度
        
    Returns:
        str: 设置结果描述
    """
    if math_channel not in ["MATH1", "MATH2"]:
        raise ValueError("数学通道必须是 MATH1 或 MATH2")
    
    if scale <= 0:
        raise ValueError("垂直刻度必须大于0")
    
    # 验证表达式格式（简单验证）
    valid_operators = ["+", "-", "*", "/", "FFT", "INTG", "DIFF"]
    valid_channels = ["CH1", "CH2", "CH3", "CH4"]
    
    advanced_oscilloscope.math_channels[math_channel] = {
        "enabled": enabled,
        "expression": expression,
        "scale": scale
    }
    
    status = "启用" if enabled else "禁用"
    result = f"{math_channel}已{status}: 表达式={expression}, 刻度={scale}V/div"
    logger.debug(f"设置数学通道: {result}")
    return result

@tool
def set_cursors(cursor_type: str = "VOLTAGE", enabled: bool = True, 
               cursor1_pos: float = 0.0, cursor2_pos: float = 0.0) -> str:
    """
    设置光标测量
    
    Args:
        cursor_type: 光标类型 ("VOLTAGE", "TIME", "TRACK")
        enabled: 是否启用光标
        cursor1_pos: 光标1位置
        cursor2_pos: 光标2位置
        
    Returns:
        str: 设置结果描述
    """
    if cursor_type not in ["VOLTAGE", "TIME", "TRACK"]:
        raise ValueError("光标类型必须是 VOLTAGE、TIME 或 TRACK")
    
    advanced_oscilloscope.cursors = {
        "enabled": enabled,
        "type": cursor_type,
        "cursor1": {"position": cursor1_pos},
        "cursor2": {"position": cursor2_pos}
    }
    
    status = "启用" if enabled else "禁用"
    delta = abs(cursor2_pos - cursor1_pos)
    
    if cursor_type == "VOLTAGE":
        unit = "V"
    elif cursor_type == "TIME":
        unit = "s"
    else:
        unit = ""
    
    result = f"光标{status}: 类型={cursor_type}, 差值={delta:.3f}{unit}"
    logger.debug(f"设置光标: {result}")
    return result

@tool
def auto_scale() -> str:
    """
    执行自动量程调整
    
    Returns:
        str: 自动量程结果描述
    """
    # 模拟自动量程过程
    time.sleep(0.5)  # 模拟调整时间
    
    # 自动调整各通道参数
    adjusted_channels = []
    for ch_num, ch_config in advanced_oscilloscope.channels.items():
        if ch_config["enabled"]:
            # 模拟自动调整电压刻度
            new_scale = random.choice([0.1, 0.2, 0.5, 1.0, 2.0, 5.0])
            ch_config["voltage_scale"] = new_scale
            adjusted_channels.append(f"CH{ch_num}: {new_scale}V/div")
    
    # 自动调整时间刻度
    new_time_scale = random.choice([1e-6, 2e-6, 5e-6, 10e-6, 20e-6, 50e-6])
    advanced_oscilloscope.time_scale = new_time_scale
    
    time_str = f"{new_time_scale*1e6:.1f}μs/div"
    
    result = f"自动量程完成: 时间={time_str}, 通道设置: {', '.join(adjusted_channels)}"
    logger.debug(f"自动量程: {result}")
    return result

@tool
def single_trigger() -> str:
    """
    执行单次触发
    
    Returns:
        str: 单次触发结果描述
    """
    # 设置为单次触发模式
    advanced_oscilloscope.trigger["mode"] = TriggerMode.SINGLE.value
    advanced_oscilloscope.acquisition["run_stop"] = False
    
    # 模拟触发等待和捕获
    time.sleep(0.2)
    
    result = "单次触发完成，波形已捕获并停止"
    logger.debug(f"单次触发: {result}")
    return result

@tool
def run_stop_acquisition(run: bool = True) -> str:
    """
    启动/停止采集
    
    Args:
        run: True为启动，False为停止
        
    Returns:
        str: 采集状态描述
    """
    advanced_oscilloscope.acquisition["run_stop"] = run
    
    if run:
        advanced_oscilloscope.trigger["mode"] = TriggerMode.AUTO.value
        result = "采集已启动，连续运行模式"
    else:
        result = "采集已停止"
    
    logger.debug(f"采集控制: {result}")
    return result

@tool
def get_oscilloscope_status() -> str:
    """
    获取示波器完整状态信息
    
    Returns:
        str: 状态信息描述
    """
    status = advanced_oscilloscope.get_status()
    
    # 格式化状态信息
    enabled_channels = [f"CH{ch}" for ch, config in status["channels"].items() if config["enabled"]]
    
    time_scale_str = f"{status['time_scale']*1e6:.1f}μs/div"
    
    result_lines = [
        "=== 示波器状态 ===",
        f"启用通道: {', '.join(enabled_channels)}",
        f"时间刻度: {time_scale_str}",
        f"触发源: {status['trigger']['source']}",
        f"触发模式: {status['trigger']['mode']}",
        f"采集状态: {'运行' if status['acquisition']['run_stop'] else '停止'}",
        f"数学通道: {', '.join([ch for ch, config in status['math_channels'].items() if config['enabled']])}",
        f"光标: {'启用' if status['cursors']['enabled'] else '禁用'}"
    ]
    
    result = "\n".join(result_lines)
    logger.debug(f"获取状态: {result}")
    return result

@tool
def manual_confirmation(prompt: str = "请确认操作", timeout_seconds: int = 30) -> str:
    """
    人工确认工具 - 需要用户手动确认操作
    
    Args:
        prompt: 确认提示信息
        timeout_seconds: 超时时间（秒）
        
    Returns:
        str: 确认结果
    """
    import threading
    import time
    
    print(f"\n{'='*50}")
    print(f"🔔 需要人工确认")
    print(f"📝 {prompt}")
    print(f"⏰ 超时时间: {timeout_seconds}秒")
    print(f"{'='*50}")
    print("请输入 'y' 或 'yes' 确认，'n' 或 'no' 取消：")
    
    result = {"confirmed": False, "response": "", "timeout": False}
    
    def get_input():
        try:
            user_input = input().strip().lower()
            result["response"] = user_input
            if user_input in ['y', 'yes', '是', '确认']:
                result["confirmed"] = True
            elif user_input in ['n', 'no', '否', '取消']:
                result["confirmed"] = False
            else:
                result["confirmed"] = False
                result["response"] = f"无效输入: {user_input}"
        except Exception as e:
            result["response"] = f"输入错误: {str(e)}"
    
    # 启动输入线程
    input_thread = threading.Thread(target=get_input)
    input_thread.daemon = True
    input_thread.start()
    
    # 等待输入或超时
    input_thread.join(timeout=timeout_seconds)
    
    if input_thread.is_alive():
        result["timeout"] = True
        final_result = f"❌ 人工确认超时（{timeout_seconds}秒），操作已取消"
    elif result["confirmed"]:
        final_result = f"✅ 人工确认成功：{prompt}"
    else:
        final_result = f"❌ 人工确认取消：{result.get('response', '用户取消')}"
    
    logger.debug(f"人工确认: {final_result}")
    return final_result

@tool
def manual_input(prompt: str = "请输入信息", input_type: str = "text", timeout_seconds: int = 60) -> str:
    """
    人工输入工具 - 需要用户手动输入信息
    
    Args:
        prompt: 输入提示信息
        input_type: 输入类型 ("text", "number", "voltage", "time", "frequency")
        timeout_seconds: 超时时间（秒）
        
    Returns:
        str: 输入结果
    """
    import threading
    import time
    
    print(f"\n{'='*50}")
    print(f"✏️ 需要人工输入")
    print(f"📝 {prompt}")
    print(f"🔤 输入类型: {input_type}")
    print(f"⏰ 超时时间: {timeout_seconds}秒")
    print(f"{'='*50}")
    
    # 根据输入类型提供提示
    type_hints = {
        "text": "请输入文本信息：",
        "number": "请输入数字：",
        "voltage": "请输入电压值（如：3.3V 或 3.3）：",
        "time": "请输入时间值（如：10ms 或 0.01）：",
        "frequency": "请输入频率值（如：1MHz 或 1000000）："
    }
    
    print(type_hints.get(input_type, "请输入信息："))
    
    result = {"input": "", "valid": False, "timeout": False}
    
    def get_input():
        try:
            user_input = input().strip()
            result["input"] = user_input
            
            # 根据类型验证输入
            if input_type == "number":
                try:
                    float(user_input)
                    result["valid"] = True
                except ValueError:
                    result["valid"] = False
                    result["input"] = f"无效数字: {user_input}"
            elif input_type in ["voltage", "time", "frequency"]:
                try:
                    # 简单验证是否包含数字
                    import re
                    if re.search(r'\d', user_input):
                        result["valid"] = True
                    else:
                        result["valid"] = False
                        result["input"] = f"无效{input_type}: {user_input}"
                except:
                    result["valid"] = False
                    result["input"] = f"验证失败: {user_input}"
            else:  # text
                result["valid"] = True if user_input else False
                
        except Exception as e:
            result["input"] = f"输入错误: {str(e)}"
            result["valid"] = False
    
    # 启动输入线程
    input_thread = threading.Thread(target=get_input)
    input_thread.daemon = True
    input_thread.start()
    
    # 等待输入或超时
    input_thread.join(timeout=timeout_seconds)
    
    if input_thread.is_alive():
        result["timeout"] = True
        final_result = f"❌ 人工输入超时（{timeout_seconds}秒），操作已取消"
    elif result["valid"]:
        final_result = f"✅ 人工输入成功：{result['input']}"
    else:
        final_result = f"❌ 人工输入失败：{result.get('input', '输入无效')}"
    
    logger.debug(f"人工输入: {final_result}")
    return final_result

@tool
def manual_operation_guide(operation: str, steps: list = None, wait_confirmation: bool = True) -> str:
    """
    人工操作指导工具 - 指导用户完成手动操作
    
    Args:
        operation: 操作名称
        steps: 操作步骤列表
        wait_confirmation: 是否等待确认完成
        
    Returns:
        str: 操作指导结果
    """
    print(f"\n{'='*60}")
    print(f"🔧 人工操作指导")
    print(f"📋 操作名称: {operation}")
    print(f"{'='*60}")
    
    if steps:
        print("📝 操作步骤:")
        for i, step in enumerate(steps, 1):
            print(f"   {i}. {step}")
    else:
        # 默认步骤
        default_steps = [
            "检查设备连接状态",
            "确认探头连接正确",
            "调整探头位置",
            "观察波形显示",
            "记录测量结果"
        ]
        print("📝 通用操作步骤:")
        for i, step in enumerate(default_steps, 1):
            print(f"   {i}. {step}")
    
    print(f"\n{'='*60}")
    
    if wait_confirmation:
        print("⏳ 请按照上述步骤完成操作...")
        confirmation_result = manual_confirmation.invoke({
            "prompt": f"是否已完成操作：{operation}？",
            "timeout_seconds": 120  # 给更长时间完成操作
        })
        
        if "成功" in confirmation_result:
            result = f"✅ 人工操作完成：{operation}"
        else:
            result = f"❌ 人工操作未完成：{operation} - {confirmation_result}"
    else:
        result = f"📋 人工操作指导已显示：{operation}"
    
    logger.debug(f"人工操作指导: {result}")
    return result

@tool
def manual_measurement_reading(measurement_type: str = "voltage", unit: str = "V", timeout_seconds: int = 90) -> str:
    """
    人工读数工具 - 需要用户手动读取测量值
    
    Args:
        measurement_type: 测量类型
        unit: 测量单位
        timeout_seconds: 超时时间（秒）
        
    Returns:
        str: 读数结果
    """
    prompt = f"请读取{measurement_type}测量值并输入（单位：{unit}）"
    
    print(f"\n{'='*50}")
    print(f"📊 人工读数")
    print(f"🔍 测量类型: {measurement_type}")
    print(f"📏 单位: {unit}")
    print(f"{'='*50}")
    print("💡 提示：请仔细观察示波器显示屏上的测量结果")
    
    # 使用人工输入工具获取读数
    input_result = manual_input.invoke({
        "prompt": prompt,
        "input_type": "number",
        "timeout_seconds": timeout_seconds
    })
    
    if "成功" in input_result:
        # 提取输入值
        import re
        match = re.search(r'成功：(.+)', input_result)
        if match:
            value = match.group(1).strip()
            result = f"📊 人工读数完成：{measurement_type} = {value}{unit}"
        else:
            result = f"📊 人工读数完成：{input_result}"
    else:
        result = f"❌ 人工读数失败：{input_result}"
    
    logger.debug(f"人工读数: {result}")
    return result

@tool
def manual_probe_adjustment(channel: int = 1, adjustment_type: str = "position") -> str:
    """
    人工探头调整工具 - 指导用户调整探头
    
    Args:
        channel: 通道号
        adjustment_type: 调整类型 ("position", "compensation", "coupling")
        
    Returns:
        str: 调整结果
    """
    adjustment_guides = {
        "position": [
            "将探头连接到指定测试点",
            "确保探头接触良好",
            "检查接地夹是否正确连接",
            "避免探头与其他导体接触"
        ],
        "compensation": [
            "连接探头到示波器校准信号输出",
            "观察方波信号的边沿",
            "使用小螺丝刀调整探头补偿电容",
            "调整直到方波边沿平直无过冲"
        ],
        "coupling": [
            "根据信号类型选择合适的耦合方式",
            "DC耦合：观察信号的直流分量",
            "AC耦合：滤除直流分量，观察交流信号",
            "确认耦合设置与测量需求匹配"
        ]
    }
    
    operation_name = f"通道{channel}探头{adjustment_type}调整"
    steps = adjustment_guides.get(adjustment_type, [])
    
    result = manual_operation_guide.invoke({
        "operation": operation_name,
        "steps": steps,
        "wait_confirmation": True
    })
    
    return result

@tool
def manual_signal_verification(signal_description: str, expected_parameters: dict = None) -> str:
    """
    人工信号验证工具 - 需要用户验证信号特征
    
    Args:
        signal_description: 信号描述
        expected_parameters: 期望的信号参数
        
    Returns:
        str: 验证结果
    """
    print(f"\n{'='*60}")
    print(f"🔍 人工信号验证")
    print(f"📡 信号描述: {signal_description}")
    print(f"{'='*60}")
    
    if expected_parameters:
        print("📋 期望参数:")
        for param, value in expected_parameters.items():
            print(f"   • {param}: {value}")
        print()
    
    verification_steps = [
        "观察信号波形形状",
        "检查信号幅度是否正常",
        "验证信号频率或周期",
        "确认信号稳定性",
        "检查是否有异常噪声或干扰"
    ]
    
    print("🔎 验证要点:")
    for i, step in enumerate(verification_steps, 1):
        print(f"   {i}. {step}")
    
    print(f"\n{'='*60}")
    
    # 等待用户确认
    confirmation_result = manual_confirmation.invoke({
        "prompt": f"信号 '{signal_description}' 是否符合预期？",
        "timeout_seconds": 120
    })
    
    if "成功" in confirmation_result:
        result = f"✅ 信号验证通过：{signal_description}"
    else:
        result = f"❌ 信号验证失败：{signal_description} - {confirmation_result}"
    
    logger.debug(f"人工信号验证: {result}")
    return result

# 高级示波器工具集合
ADVANCED_OSCILLOSCOPE_TOOLS = [
    set_channel_advanced, set_time_base_advanced, set_trigger_advanced,
    measure_rise_time, measure_fall_time, measure_duty_cycle, measure_pulse_width,
    measure_period, measure_phase_difference, measure_delay,
    measure_overshoot, measure_undershoot, set_math_channel, set_cursors,
    auto_scale, single_trigger, run_stop_acquisition, get_oscilloscope_status,
    measure_rms, measure_peak_to_peak, set_acquisition_mode, start_timer,
    check_timer_status, stop_timer, clear_all_timers,
    manual_confirmation, manual_input, manual_operation_guide, manual_measurement_reading,
    manual_probe_adjustment, manual_signal_verification
]

if __name__ == "__main__":
    # 测试代码
    print("=== 高级示波器工具测试 ===")
    
    # 测试基本设置
    print(set_channel_advanced.invoke({"channel": 1, "enabled": True, "voltage_scale": 1.0, "coupling": "DC"}))
    print(set_channel_advanced.invoke({"channel": 2, "enabled": True, "voltage_scale": 1.0, "coupling": "DC"}))
    print(set_time_base_advanced.invoke({"scale": 10e-6}))  # 10μs/div
    print(set_trigger_advanced.invoke({"source": "CH1", "level": 1.5, "slope": "RISING"}))
    
    # 测试各种测量
    print("\n=== 测量功能测试 ===")
    print(measure_rise_time.invoke({"channel": 1}))
    print(measure_fall_time.invoke({"channel": 1}))
    print(measure_duty_cycle.invoke({"channel": 1}))
    print(measure_pulse_width.invoke({"channel": 1, "polarity": "POSITIVE"}))
    print(measure_period.invoke({"channel": 1}))
    print(measure_phase_difference.invoke({"channel1": 1, "channel2": 2}))
    print(measure_delay.invoke({"channel1": 1, "channel2": 2}))
    print(measure_overshoot.invoke({"channel": 1}))
    print(measure_undershoot.invoke({"channel": 1}))
    print(measure_rms.invoke({"channel": 1}))
    print(measure_peak_to_peak.invoke({"channel": 1}))
    
    # 测试高级功能
    print("\n=== 高级功能测试 ===")
    print(set_math_channel.invoke({"math_channel": "MATH1", "expression": "CH1-CH2"}))
    print(set_cursors.invoke({"cursor_type": "VOLTAGE", "enabled": True, "cursor1_pos": -1.0, "cursor2_pos": 1.0}))
    print(auto_scale.invoke({}))
    print(single_trigger.invoke({}))
    
    print("\n" + get_oscilloscope_status.invoke({}))

    # 测试采集模式设置
    print("\n=== 采集模式测试 ===")
    print(set_acquisition_mode.invoke({"mode": "HIGH_RESOLUTION", "memory_depth": "1M", "vertical_noise_reduction": True, "reduction_ratio": "10:1"}))
    
    # 测试定时器功能
    print("\n=== 定时器功能测试 ===")
    print(start_timer.invoke({"duration_seconds": 5.0, "timer_name": "信号稳定性测试"}))
    print(start_timer.invoke({"duration_seconds": 10.0, "timer_name": "长期测量"}))
    print(check_timer_status.invoke({}))
    
    # 模拟等待一段时间后检查定时器
    time.sleep(1)
    print("等待1秒后:")
    print(check_timer_status.invoke({}))
    
    # 测试人工操作工具（演示模式，不需要真实输入）
    print("\n=== 人工操作工具演示 ===")
    print("注意：以下是人工操作工具的功能演示，实际使用时需要真实的用户交互")
    
    # 演示人工操作指导（不等待确认）
    print("\n1. 人工操作指导演示:")
    guide_result = manual_operation_guide.invoke({
        "operation": "探头校准",
        "steps": ["连接探头到校准输出", "调整补偿电容", "观察方波边沿"],
        "wait_confirmation": False
    })
    print(f"指导结果: {guide_result}")
    
    print("\n人工操作工具已集成，包括以下功能:")
    print("• manual_confirmation - 人工确认")
    print("• manual_input - 人工输入")
    print("• manual_operation_guide - 操作指导")
    print("• manual_measurement_reading - 人工读数")
    print("• manual_probe_adjustment - 探头调整")
    print("• manual_signal_verification - 信号验证")
