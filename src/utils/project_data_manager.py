"""
测试计划数据管理器

提供线程安全的测试计划数据管理，支持动态添加、删除、更新计划
包括信号机制以通知UI组件更新

主要功能：
1. 线程安全的计划数据操作
2. Qt信号槽机制通知UI更新
3. 支持计划状态管理
4. 单例模式确保数据一致性
"""

import threading
import json
from typing import Dict, List, Optional, Callable
from PySide6.QtCore import QObject, Signal
from datetime import datetime
import uuid


class ProjectDataManager(QObject):
    """
    测试计划数据管理器
    
    提供线程安全的计划数据管理，使用Qt信号通知UI更新
    """
    
    # 定义信号
    plan_added = Signal(dict)       # 计划添加信号
    plan_removed = Signal(str)      # 计划删除信号（传递计划ID）
    plan_updated = Signal(dict)     # 计划更新信号
    plans_cleared = Signal()        # 清空所有计划信号
    plan_status_changed = Signal(str, str)  # 计划状态变更信号（计划ID，新状态）
    
    def __init__(self):
        super().__init__()
        self._projects = {}  # 存储计划数据，键为计划ID
        self._lock = threading.RLock()  # 递归锁，允许同一线程多次获取锁
        
    def add_project(self, project_data: dict) -> str:
        """
        添加新的测试计划
        
        Args:
            project_data (dict): 计划数据
            
        Returns:
            str: 计划ID
        """
        with self._lock:
            # 确保有计划ID
            project_id = project_data.get('project_id')
            if not project_id:
                project_id = str(uuid.uuid4())
                project_data['project_id'] = project_id
            
            # 添加创建时间戳
            if 'created_at' not in project_data:
                project_data['created_at'] = datetime.now().isoformat()
            
            # 确保状态字段存在
            if 'status' not in project_data:
                project_data['status'] = 'planning'
                
            # 存储计划数据
            self._projects[project_id] = project_data.copy()
            
        # 在锁外发送信号，避免死锁
        self.plan_added.emit(project_data.copy())
        return project_id
        
    def remove_project(self, project_id: str) -> bool:
        """
        删除指定的测试计划
        
        Args:
            project_id (str): 计划ID
            
        Returns:
            bool: 是否删除成功
        """
        with self._lock:
            if project_id in self._projects:
                del self._projects[project_id]
                removed = True
            else:
                removed = False
                
        if removed:
            # 在锁外发送信号
            self.plan_removed.emit(project_id)
            
        return removed
        
    def update_project(self, project_id: str, updates: dict) -> bool:
        """
        更新指定计划的数据
        
        Args:
            project_id (str): 计划ID
            updates (dict): 更新的数据字典
            
        Returns:
            bool: 是否更新成功
        """
        with self._lock:
            if project_id not in self._projects:
                return False
                
            # 更新数据
            old_status = self._projects[project_id].get('status')
            self._projects[project_id].update(updates)
            
            # 添加更新时间戳
            self._projects[project_id]['updated_at'] = datetime.now().isoformat()
            
            updated_project = self._projects[project_id].copy()
            new_status = updated_project.get('status')
            
        # 在锁外发送信号
        self.plan_updated.emit(updated_project)
        
        # 如果状态有变化，发送状态变更信号
        if old_status != new_status and new_status:
            self.plan_status_changed.emit(project_id, new_status)
            
        return True
        
    def get_project(self, project_id: str) -> Optional[dict]:
        """
        获取指定的计划数据
        
        Args:
            project_id (str): 计划ID
            
        Returns:
            Optional[dict]: 计划数据，如果不存在返回None
        """
        with self._lock:
            return self._projects.get(project_id, {}).copy() if project_id in self._projects else None
            
    def get_all_projects(self) -> List[dict]:
        """
        获取所有计划数据
        
        Returns:
            List[dict]: 所有计划数据的列表
        """
        with self._lock:
            return [project.copy() for project in self._projects.values()]
            
    def get_projects_by_status(self, status: str) -> List[dict]:
        """
        根据状态获取计划列表
        
        Args:
            status (str): 计划状态
            
        Returns:
            List[dict]: 符合状态的计划列表
        """
        with self._lock:
            return [
                project.copy() 
                for project in self._projects.values() 
                if project.get('status') == status
            ]
            
    def clear_all_projects(self) -> int:
        """
        清空所有计划数据
        
        Returns:
            int: 清空的计划数量
        """
        with self._lock:
            count = len(self._projects)
            self._projects.clear()
            
        if count > 0:
            # 在锁外发送信号
            self.plans_cleared.emit()
            
        return count
        
    def get_project_count(self) -> int:
        """
        获取计划总数
        
        Returns:
            int: 计划数量
        """
        with self._lock:
            return len(self._projects)
            
    def project_exists(self, project_id: str) -> bool:
        """
        检查计划是否存在
        
        Args:
            project_id (str): 计划ID
            
        Returns:
            bool: 计划是否存在
        """
        with self._lock:
            return project_id in self._projects
            
    def set_project_status(self, project_id: str, status: str) -> bool:
        """
        设置计划状态
        
        Args:
            project_id (str): 计划ID
            status (str): 新状态
            
        Returns:
            bool: 是否设置成功
        """
        return self.update_project(project_id, {'status': status})
        
    def advance_project_task(self, project_id: str) -> bool:
        """
        推进计划任务进度
        
        Args:
            project_id (str): 计划ID
            
        Returns:
            bool: 是否推进成功
        """
        with self._lock:
            if project_id not in self._projects:
                return False
                
            project = self._projects[project_id]
            current_task = project.get('current_task', 0)
            total_tasks = project.get('total_tasks', 0)
            
            if current_task < total_tasks:
                old_status = project.get('status')
                updates = {
                    'current_task': current_task + 1,
                    'status': 'completed' if current_task + 1 >= total_tasks else 'running'
                }
                # 使用已有的锁，直接更新
                project.update(updates)
                project['updated_at'] = datetime.now().isoformat()
                
                updated_project = project.copy()
                new_status = updated_project.get('status')
                
                # 在锁外发送信号
                # 使用临时变量避免在锁外访问
                should_emit_status = old_status != new_status and new_status
            else:
                # 任务已完成，无需推进
                return False
                
        # 在锁外发送信号
        self.plan_updated.emit(updated_project)
        
        # 如果状态有变化，发送状态变更信号
        if should_emit_status:
            self.plan_status_changed.emit(project_id, new_status)
            
        return True


# 全局单例实例
_project_manager_instance = None
_instance_lock = threading.Lock()


def get_project_manager() -> ProjectDataManager:
    """
    获取测试计划数据管理器的单例实例
    
    Returns:
        ProjectDataManager: 数据管理器实例
    """
    global _project_manager_instance
    
    if _project_manager_instance is None:
        with _instance_lock:
            if _project_manager_instance is None:
                _project_manager_instance = ProjectDataManager()
                
    return _project_manager_instance 