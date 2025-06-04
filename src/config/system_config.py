#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
系统配置模块

管理整个系统的配置参数，包括UI设置、Actor配置、设备参数等。

@author: PankIns Team
@version: 1.0.0
"""

import json
import os
from typing import Dict, Any
import logging


class SystemConfig:
    """
    系统配置管理器
    
    负责加载、保存和管理系统配置
    """
    
    def __init__(self, config_file: str = "config/system_config.json"):
        """
        初始化系统配置
        
        @param {str} config_file - 配置文件路径
        """
        self.logger = logging.getLogger(__name__)
        self.config_file = config_file
        self.config: Dict[str, Any] = {}
        
        # 默认配置
        self._default_config = {
            "system": {
                "name": "AI示波器控制系统",
                "version": "1.0.0",
                "debug_mode": False,
                "log_level": "INFO"
            },
            "ui": {
                "window_width": 1200,
                "window_height": 800,
                "theme": "default",
                "language": "zh_CN"
            },
            "actors": {
                "max_queue_size": 1000,
                "timeout_seconds": 30,
                "retry_attempts": 3
            },
            "oscilloscope": {
                "connection_type": "USB",
                "timeout": 5000,
                "auto_connect": True,
                "default_settings": {
                    "time_scale": "1ms",
                    "voltage_scale": "1V",
                    "trigger_mode": "AUTO"
                }
            },
            "ai": {
                "model_type": "langchain",
                "max_tokens": 4000,
                "temperature": 0.7,
                "enable_memory": True
            },
            "data": {
                "buffer_size": 10000,
                "auto_save": True,
                "save_format": "csv",
                "data_retention_days": 30
            }
        }
        
        self.load_config()
    
    def load_config(self):
        """
        加载配置文件
        """
        try:
            # 确保配置目录存在
            config_dir = os.path.dirname(self.config_file)
            if config_dir and not os.path.exists(config_dir):
                os.makedirs(config_dir)
            
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                
                # 合并默认配置和加载的配置
                self.config = self._merge_configs(self._default_config, loaded_config)
                self.logger.info(f"配置文件加载成功: {self.config_file}")
            else:
                # 使用默认配置并保存
                self.config = self._default_config.copy()
                self.save_config()
                self.logger.info("使用默认配置并已保存到文件")
                
        except Exception as e:
            self.logger.error(f"配置文件加载失败: {e}")
            self.config = self._default_config.copy()
    
    def save_config(self):
        """
        保存配置到文件
        """
        try:
            # 确保配置目录存在
            config_dir = os.path.dirname(self.config_file)
            if config_dir and not os.path.exists(config_dir):
                os.makedirs(config_dir)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            
            self.logger.info(f"配置文件保存成功: {self.config_file}")
            
        except Exception as e:
            self.logger.error(f"配置文件保存失败: {e}")
    
    def get(self, key_path: str, default=None):
        """
        获取配置值
        
        @param {str} key_path - 配置路径，使用.分隔，如 "ui.window_width"
        @param {Any} default - 默认值
        @returns {Any} 配置值
        """
        keys = key_path.split('.')
        value = self.config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value: Any):
        """
        设置配置值
        
        @param {str} key_path - 配置路径，使用.分隔
        @param {Any} value - 配置值
        """
        keys = key_path.split('.')
        config = self.config
        
        # 导航到目标位置
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        # 设置值
        config[keys[-1]] = value
        self.logger.debug(f"配置已更新: {key_path} = {value}")
    
    def _merge_configs(self, default: Dict, loaded: Dict) -> Dict:
        """
        合并配置字典
        
        @param {Dict} default - 默认配置
        @param {Dict} loaded - 加载的配置
        @returns {Dict} 合并后的配置
        """
        result = default.copy()
        
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def reset_to_default(self):
        """
        重置为默认配置
        """
        self.config = self._default_config.copy()
        self.save_config()
        self.logger.info("配置已重置为默认值")
    
    def get_all(self) -> Dict[str, Any]:
        """
        获取所有配置
        
        @returns {Dict[str, Any]} 完整配置字典
        """
        return self.config.copy() 