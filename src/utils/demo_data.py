#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
演示数据生成器

用于生成模拟的示波器数据，方便系统功能演示和测试。

@author: PankIns Team
@version: 1.0.0
"""

import numpy as np
import random
from typing import Tuple, Dict, Any, List


class DemoDataGenerator:
    """
    演示数据生成器类
    
    生成各种类型的模拟信号数据
    """
    
    def __init__(self):
        """
        初始化数据生成器
        """
        self.sample_rate = 1000  # 采样率 (Hz)
        self.duration = 1.0      # 持续时间 (秒)
        self.noise_level = 0.1   # 噪声水平
        
    def generate_sine_wave(self, frequency: float = 10.0, amplitude: float = 1.0, 
                          phase: float = 0.0) -> Tuple[np.ndarray, np.ndarray]:
        """
        生成正弦波信号
        
        @param {float} frequency - 频率 (Hz)
        @param {float} amplitude - 幅度
        @param {float} phase - 相位 (弧度)
        @returns {tuple} (时间数组, 信号数组)
        """
        t = np.linspace(0, self.duration, int(self.sample_rate * self.duration))
        signal = amplitude * np.sin(2 * np.pi * frequency * t + phase)
        
        # 添加噪声
        noise = np.random.normal(0, self.noise_level * amplitude, len(signal))
        signal += noise
        
        return t, signal
    
    def generate_square_wave(self, frequency: float = 5.0, amplitude: float = 1.0,
                           duty_cycle: float = 0.5) -> Tuple[np.ndarray, np.ndarray]:
        """
        生成方波信号
        
        @param {float} frequency - 频率 (Hz)
        @param {float} amplitude - 幅度
        @param {float} duty_cycle - 占空比 (0-1)
        @returns {tuple} (时间数组, 信号数组)
        """
        t = np.linspace(0, self.duration, int(self.sample_rate * self.duration))
        signal = amplitude * (2 * (t * frequency % 1 < duty_cycle) - 1)
        
        # 添加噪声
        noise = np.random.normal(0, self.noise_level * amplitude, len(signal))
        signal += noise
        
        return t, signal
    
    def generate_triangle_wave(self, frequency: float = 8.0, 
                             amplitude: float = 1.0) -> Tuple[np.ndarray, np.ndarray]:
        """
        生成三角波信号
        
        @param {float} frequency - 频率 (Hz)
        @param {float} amplitude - 幅度
        @returns {tuple} (时间数组, 信号数组)
        """
        t = np.linspace(0, self.duration, int(self.sample_rate * self.duration))
        signal = amplitude * (2 * np.abs(2 * (t * frequency % 1) - 1) - 1)
        
        # 添加噪声
        noise = np.random.normal(0, self.noise_level * amplitude, len(signal))
        signal += noise
        
        return t, signal
    
    def generate_pulse_train(self, frequency: float = 20.0, amplitude: float = 1.0,
                           pulse_width: float = 0.1) -> Tuple[np.ndarray, np.ndarray]:
        """
        生成脉冲序列
        
        @param {float} frequency - 脉冲频率 (Hz)
        @param {float} amplitude - 幅度
        @param {float} pulse_width - 脉冲宽度 (秒)
        @returns {tuple} (时间数组, 信号数组)
        """
        t = np.linspace(0, self.duration, int(self.sample_rate * self.duration))
        period = 1.0 / frequency
        signal = np.zeros_like(t)
        
        for i, time_val in enumerate(t):
            if (time_val % period) < pulse_width:
                signal[i] = amplitude
        
        # 添加噪声
        noise = np.random.normal(0, self.noise_level * amplitude, len(signal))
        signal += noise
        
        return t, signal
    
    def generate_noisy_signal(self, amplitude: float = 1.0) -> Tuple[np.ndarray, np.ndarray]:
        """
        生成噪声信号
        
        @param {float} amplitude - 噪声幅度
        @returns {tuple} (时间数组, 信号数组)
        """
        t = np.linspace(0, self.duration, int(self.sample_rate * self.duration))
        signal = np.random.normal(0, amplitude, len(t))
        
        return t, signal
    
    def generate_mixed_signal(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        生成混合信号（多个频率成分）
        
        @returns {tuple} (时间数组, 信号数组)
        """
        t = np.linspace(0, self.duration, int(self.sample_rate * self.duration))
        
        # 基波
        signal = 1.0 * np.sin(2 * np.pi * 10 * t)
        
        # 三次谐波
        signal += 0.3 * np.sin(2 * np.pi * 30 * t)
        
        # 五次谐波
        signal += 0.1 * np.sin(2 * np.pi * 50 * t)
        
        # 低频调制
        signal *= (1 + 0.2 * np.sin(2 * np.pi * 2 * t))
        
        # 添加噪声
        noise = np.random.normal(0, self.noise_level, len(signal))
        signal += noise
        
        return t, signal
    
    def generate_exponential_decay(self, time_constant: float = 0.2,
                                 amplitude: float = 1.0) -> Tuple[np.ndarray, np.ndarray]:
        """
        生成指数衰减信号
        
        @param {float} time_constant - 时间常数 (秒)
        @param {float} amplitude - 初始幅度
        @returns {tuple} (时间数组, 信号数组)
        """
        t = np.linspace(0, self.duration, int(self.sample_rate * self.duration))
        signal = amplitude * np.exp(-t / time_constant)
        
        # 添加噪声
        noise = np.random.normal(0, self.noise_level * amplitude, len(signal))
        signal += noise
        
        return t, signal
    
    def generate_chirp_signal(self, f0: float = 1.0, f1: float = 50.0,
                            amplitude: float = 1.0) -> Tuple[np.ndarray, np.ndarray]:
        """
        生成线性调频信号（Chirp）
        
        @param {float} f0 - 起始频率 (Hz)
        @param {float} f1 - 结束频率 (Hz)
        @param {float} amplitude - 幅度
        @returns {tuple} (时间数组, 信号数组)
        """
        t = np.linspace(0, self.duration, int(self.sample_rate * self.duration))
        
        # 线性调频
        freq_sweep = f0 + (f1 - f0) * t / self.duration
        phase = 2 * np.pi * np.cumsum(freq_sweep) / self.sample_rate
        signal = amplitude * np.sin(phase)
        
        # 添加噪声
        noise = np.random.normal(0, self.noise_level * amplitude, len(signal))
        signal += noise
        
        return t, signal
    
    def get_signal_info(self, signal_type: str) -> Dict[str, Any]:
        """
        获取信号类型信息
        
        @param {str} signal_type - 信号类型
        @returns {dict} 信号信息
        """
        signal_info = {
            "sine": {
                "name": "正弦波",
                "description": "纯净的周期性信号，常用于基础测试",
                "typical_use": "频率响应测试、失真分析",
                "parameters": ["频率", "幅度", "相位"]
            },
            "square": {
                "name": "方波",
                "description": "包含丰富谐波成分的数字信号",
                "typical_use": "数字电路测试、上升时间测量",
                "parameters": ["频率", "幅度", "占空比"]
            },
            "triangle": {
                "name": "三角波",
                "description": "线性变化的周期信号",
                "typical_use": "线性度测试、积分电路测试",
                "parameters": ["频率", "幅度"]
            },
            "pulse": {
                "name": "脉冲序列",
                "description": "短脉冲组成的信号",
                "typical_use": "时序分析、脉冲响应测试",
                "parameters": ["频率", "幅度", "脉冲宽度"]
            },
            "noise": {
                "name": "噪声信号",
                "description": "随机信号，用于噪声分析",
                "typical_use": "噪声测量、信噪比分析",
                "parameters": ["幅度"]
            },
            "mixed": {
                "name": "混合信号",
                "description": "多频率成分的复合信号",
                "typical_use": "频谱分析、滤波器测试",
                "parameters": ["基频", "谐波成分"]
            },
            "decay": {
                "name": "指数衰减",
                "description": "按指数规律衰减的信号",
                "typical_use": "RC电路分析、时间常数测量",
                "parameters": ["时间常数", "初始幅度"]
            },
            "chirp": {
                "name": "线性调频",
                "description": "频率随时间线性变化的信号",
                "typical_use": "频率响应扫描、雷达信号分析",
                "parameters": ["起始频率", "结束频率"]
            }
        }
        
        return signal_info.get(signal_type, {})
    
    def generate_random_signal(self) -> Tuple[np.ndarray, np.ndarray, str, Dict[str, Any]]:
        """
        生成随机类型的信号
        
        @returns {tuple} (时间数组, 信号数组, 信号类型, 参数信息)
        """
        signal_types = [
            ("sine", lambda: self.generate_sine_wave(
                frequency=random.uniform(5, 50),
                amplitude=random.uniform(0.5, 2.0)
            )),
            ("square", lambda: self.generate_square_wave(
                frequency=random.uniform(2, 20),
                amplitude=random.uniform(0.5, 2.0),
                duty_cycle=random.uniform(0.2, 0.8)
            )),
            ("triangle", lambda: self.generate_triangle_wave(
                frequency=random.uniform(3, 25),
                amplitude=random.uniform(0.5, 2.0)
            )),
            ("pulse", lambda: self.generate_pulse_train(
                frequency=random.uniform(10, 100),
                amplitude=random.uniform(0.5, 2.0),
                pulse_width=random.uniform(0.01, 0.1)
            )),
            ("mixed", lambda: self.generate_mixed_signal()),
            ("chirp", lambda: self.generate_chirp_signal(
                f0=random.uniform(1, 10),
                f1=random.uniform(20, 100)
            ))
        ]
        
        signal_type, generator = random.choice(signal_types)
        t, signal = generator()
        info = self.get_signal_info(signal_type)
        
        return t, signal, signal_type, info
    
    def set_parameters(self, sample_rate: int = None, duration: float = None,
                      noise_level: float = None):
        """
        设置生成器参数
        
        @param {int} sample_rate - 采样率
        @param {float} duration - 持续时间
        @param {float} noise_level - 噪声水平
        """
        if sample_rate is not None:
            self.sample_rate = sample_rate
        if duration is not None:
            self.duration = duration
        if noise_level is not None:
            self.noise_level = noise_level
    
    def get_available_signals(self) -> List[str]:
        """
        获取可用的信号类型列表
        
        @returns {list} 信号类型列表
        """
        return ["sine", "square", "triangle", "pulse", "noise", "mixed", "decay", "chirp"]


# 全局实例
demo_generator = DemoDataGenerator() 