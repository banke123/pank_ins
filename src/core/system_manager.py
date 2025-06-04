#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
系统管理器模块

管理系统的各个组件和状态。

@author: PankIns Team
@version: 1.0.0
"""

import logging
from typing import Dict, Any


class SystemManager:
    """
    系统管理器类
    
    负责管理系统的各个组件和状态
    """
    
    def __init__(self):
        """
        初始化系统管理器
        """
        self.logger = logging.getLogger(__name__)
        self._running = False
        self._actors = {}
        
        self.logger.info("系统管理器初始化完成")
    
    def is_running(self) -> bool:
        """
        获取系统运行状态
        
        @returns {bool} 系统是否正在运行
        """
        return self._running
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        获取系统状态
        
        @returns {Dict[str, Any]} 系统状态信息
        """
        return {
            "running": self._running,
            "actors": {
                name: actor.is_alive() if actor else False
                for name, actor in self._actors.items()
            }
        }
    
    def start_actors(self):
        """
        启动所有Actor
        """
        self.logger.info("启动系统组件")
        self._running = True
    
    def stop_actors(self):
        """
        停止所有Actor
        """
        self.logger.info("停止系统组件")
        self._running = False 