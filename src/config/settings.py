#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
应用设置模块

提供应用程序的配置管理功能，包括UI设置、系统参数等。

@author: PankIns Team
@version: 2.0.0
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
import logging


class Settings:
    """
    应用设置管理器
    
    负责加载、保存和管理应用程序设置
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        初始化设置管理器
        
        Args:
            config_file: 配置文件路径，如果为None则使用默认路径
        """
        self.logger = logging.getLogger(__name__)
        
        # 设置配置文件路径
        if config_file is None:
            project_root = Path(__file__).parent.parent.parent
            config_dir = project_root / "config"
            config_dir.mkdir(exist_ok=True)
            self.config_file = config_dir / "app_settings.json"
        else:
            self.config_file = Path(config_file)
        
        # 默认配置
        self._default_config = {
            "app": {
                "name": "Pank Ins",
                "version": "2.0.0",
                "debug_mode": False,
                "log_level": "INFO"
            },
            "ui": {
                "window_width": 1600,
                "window_height": 1000,
                "theme": "Material",
                "language": "zh_CN",
                "enable_animations": True,
                "high_dpi_scaling": True
            },
            "qml": {
                "style": "Material",
                "theme": "Light",
                "accent_color": "#4f46e5",
                "enable_gpu_acceleration": True
            },
            "actors": {
                "system_name": "PankInsSystem",
                "max_queue_size": 1000,
                "timeout_seconds": 30,
                "retry_attempts": 3
            },
            "ai": {
                "model_type": "langchain",
                "max_tokens": 4000,
                "temperature": 0.7,
                "enable_memory": True,
                "enable_streaming": True
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
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "file_enabled": True,
                "console_enabled": True,
                "max_file_size": "10MB",
                "backup_count": 5
            }
        }
        
        self.config = {}
        self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        try:
            if self.config_file.exists():
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
        """保存配置到文件"""
        try:
            # 确保配置目录存在
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            
            self.logger.info(f"配置文件保存成功: {self.config_file}")
            
        except Exception as e:
            self.logger.error(f"配置文件保存失败: {e}")
    
    def get(self, key_path: str, default=None):
        """
        获取配置值
        
        Args:
            key_path: 配置路径，使用.分隔，如 "ui.window_width"
            default: 默认值
            
        Returns:
            配置值
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
        
        Args:
            key_path: 配置路径，使用.分隔
            value: 配置值
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
    
    def get_config_path(self) -> str:
        """获取配置文件路径"""
        return str(self.config_file)
    
    def get_all(self) -> Dict[str, Any]:
        """获取所有配置"""
        return self.config.copy()
    
    def reset_to_default(self):
        """重置为默认配置"""
        self.config = self._default_config.copy()
        self.save_config()
        self.logger.info("配置已重置为默认值")
    
    def _merge_configs(self, default: Dict, loaded: Dict) -> Dict:
        """
        合并配置字典
        
        Args:
            default: 默认配置
            loaded: 加载的配置
            
        Returns:
            合并后的配置
        """
        result = default.copy()
        
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    # 便捷方法
    @property
    def app_name(self) -> str:
        """应用名称"""
        return self.get("app.name", "Pank Ins")
    
    @property
    def app_version(self) -> str:
        """应用版本"""
        return self.get("app.version", "2.0.0")
    
    @property
    def debug_mode(self) -> bool:
        """调试模式"""
        return self.get("app.debug_mode", False)
    
    @property
    def window_size(self) -> tuple:
        """窗口大小"""
        width = self.get("ui.window_width", 1600)
        height = self.get("ui.window_height", 1000)
        return (width, height)
    
    @property
    def qml_style(self) -> str:
        """QML样式"""
        return self.get("qml.style", "Material")
    
    @property
    def qml_theme(self) -> str:
        """QML主题"""
        return self.get("qml.theme", "Light")
    
    @property
    def accent_color(self) -> str:
        """强调色"""
        return self.get("qml.accent_color", "#4f46e5")
    
    @property
    def actor_system_name(self) -> str:
        """Actor系统名称"""
        return self.get("actors.system_name", "PankInsSystem")
    
    @property
    def log_level(self) -> str:
        """日志级别"""
        return self.get("logging.level", "INFO") 