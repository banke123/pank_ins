#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
历史记录管理器
用于管理多个对话容器的历史记录
"""

import os
import sys
from typing import Dict, List, Any

# 添加项目根目录到Python路径
current_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..', '..'))
sys.path.insert(0, project_root)

from src.utils.logger_config import get_logger

logger = get_logger(__name__)


class HistoryManager:
    """历史记录管理器"""
    
    def __init__(self):
        """初始化历史记录管理器"""
        self.containers = {}  # container_id -> messages list
    
    def create_container(self, container_id: str) -> bool:
        """创建新的对话容器"""
        try:
            if container_id not in self.containers:
                self.containers[container_id] = []
                logger.debug(f"创建对话容器: {container_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"创建对话容器失败: {e}")
            return False
    
    def add_message(self, container_id: str, role: str, content: str) -> bool:
        """添加消息到指定容器"""
        try:
            if container_id not in self.containers:
                self.create_container(container_id)
            
            message = {
                "role": role,
                "content": content,
                "timestamp": self._get_timestamp()
            }
            
            self.containers[container_id].append(message)
            logger.debug(f"添加消息到容器 {container_id}: {role}")
            return True
            
        except Exception as e:
            logger.error(f"添加消息失败: {e}")
            return False
    
    def get_history(self, container_id: str) -> List[Dict[str, Any]]:
        """获取指定容器的历史记录"""
        return self.containers.get(container_id, [])
    
    def clear_history(self, container_id: str) -> bool:
        """清空指定容器的历史记录"""
        try:
            if container_id in self.containers:
                self.containers[container_id] = []
                logger.debug(f"清空容器历史: {container_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"清空历史记录失败: {e}")
            return False
    
    def get_all_container_ids(self) -> List[str]:
        """获取所有容器ID"""
        return list(self.containers.keys())
    
    def remove_container(self, container_id: str) -> bool:
        """删除指定容器"""
        try:
            if container_id in self.containers:
                del self.containers[container_id]
                logger.debug(f"删除容器: {container_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"删除容器失败: {e}")
            return False
    
    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        import datetime
        return datetime.datetime.now().isoformat() 