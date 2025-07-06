"""
测试计划管理API

提供简化的测试计划操作接口，包装底层的ProjectDataManager
支持快速创建、管理和控制测试计划

主要功能：
1. 简化的计划创建和管理接口
2. 状态管理（启动、暂停、完成、错误）
3. 进度控制（推进任务、更新进度）
4. 后台执行模拟
5. 便捷的单例访问
"""

import time
import threading
from typing import List, Dict, Optional, Any
from src.utils.project_data_manager import get_project_manager


class ProjectAPI:
    """
    测试计划API管理器
    
    提供便于使用的测试计划操作方法，简化对ProjectDataManager的调用
    """
    
    def __init__(self):
        self.data_manager = get_project_manager()
        
    def create_project(self, plan_name: str, description: str = "", signal_type: str = "", 
                      tasks: List[Dict] = None) -> Optional[str]:
        """
        创建新的测试计划
        
        Args:
            plan_name (str): 计划名称
            description (str): 计划描述
            signal_type (str): 信号类型
            tasks (List[Dict]): 任务列表
            
        Returns:
            Optional[str]: 计划ID，创建失败返回None
        """
        if not plan_name:
            return None
            
        if tasks is None:
            tasks = []
            
        project_data = {
            "card_type": "level3",
            "project_name": plan_name,
            "project_description": description,
            "signal_type": signal_type,
            "status": "planning",
            "current_task": 0,
            "total_tasks": len(tasks),
            "tasks": tasks,
            "estimated_total_time": self._calculate_total_time(tasks)
        }
        
        return self.data_manager.add_project(project_data)
        
    def delete_project(self, project_id: str) -> bool:
        """
        删除指定的测试计划
        
        Args:
            project_id (str): 计划ID
            
        Returns:
            bool: 是否删除成功
        """
        return self.data_manager.remove_project(project_id)
        
    def get_project(self, project_id: str) -> Optional[Dict]:
        """
        获取指定的测试计划数据
        
        Args:
            project_id (str): 计划ID
            
        Returns:
            Optional[Dict]: 计划数据，不存在返回None
        """
        return self.data_manager.get_project(project_id)
        
    def get_all_projects(self) -> List[Dict]:
        """
        获取所有测试计划
        
        Returns:
            List[Dict]: 所有计划数据列表
        """
        return self.data_manager.get_all_projects()
        
    def start_project(self, project_id: str) -> bool:
        """
        启动测试计划
        
        Args:
            project_id (str): 计划ID
            
        Returns:
            bool: 是否启动成功
        """
        return self.data_manager.set_project_status(project_id, "running")
        
    def pause_project(self, project_id: str) -> bool:
        """
        暂停测试计划
        
        Args:
            project_id (str): 计划ID
            
        Returns:
            bool: 是否暂停成功
        """
        return self.data_manager.set_project_status(project_id, "paused")
        
    def complete_project(self, project_id: str) -> bool:
        """
        完成测试计划
        
        Args:
            project_id (str): 计划ID
            
        Returns:
            bool: 是否设置成功
        """
        # 同时更新进度到最大值
        project = self.get_project(project_id)
        if project:
            total_tasks = project.get('total_tasks', 0)
            updates = {
                'status': 'completed',
                'current_task': total_tasks
            }
            return self.data_manager.update_project(project_id, updates)
        return False
        
    def set_project_error(self, project_id: str, error_message: str = "") -> bool:
        """
        设置测试计划为错误状态
        
        Args:
            project_id (str): 计划ID
            error_message (str): 错误信息
            
        Returns:
            bool: 是否设置成功
        """
        updates = {'status': 'error'}
        if error_message:
            updates['error_message'] = error_message
        return self.data_manager.update_project(project_id, updates)
        
    def advance_task(self, project_id: str) -> bool:
        """
        推进计划任务进度
        
        Args:
            project_id (str): 计划ID
            
        Returns:
            bool: 是否推进成功
        """
        return self.data_manager.advance_project_task(project_id)
        
    def update_task_progress(self, project_id: str, current_task: int, 
                           additional_data: Dict = None) -> bool:
        """
        更新计划任务进度
        
        Args:
            project_id (str): 计划ID
            current_task (int): 当前任务序号
            additional_data (Dict): 额外的更新数据
            
        Returns:
            bool: 是否更新成功
        """
        project = self.get_project(project_id)
        if not project:
            return False
            
        total_tasks = project.get('total_tasks', 0)
        
        updates = {'current_task': current_task}
        
        # 根据进度自动更新状态
        if current_task >= total_tasks:
            updates['status'] = 'completed'
        elif current_task > 0:
            updates['status'] = 'running'
            
        if additional_data:
            updates.update(additional_data)
            
        return self.data_manager.update_project(project_id, updates)
        
    def get_projects_by_status(self, status: str) -> List[Dict]:
        """
        根据状态获取测试计划列表
        
        Args:
            status (str): 计划状态
            
        Returns:
            List[Dict]: 符合条件的计划列表
        """
        return self.data_manager.get_projects_by_status(status)
        
    def clear_all_projects(self) -> int:
        """
        清空所有测试计划
        
        Returns:
            int: 清空的计划数量
        """
        return self.data_manager.clear_all_projects()
        
    def simulate_project_execution(self, project_id: str, task_duration: float = 3.0) -> bool:
        """
        在后台线程中模拟测试计划执行
        
        Args:
            project_id (str): 计划ID
            task_duration (float): 每个任务的执行时间（秒）
            
        Returns:
            bool: 是否开始模拟成功
        """
        project = self.get_project(project_id)
        if not project:
            return False
            
        def simulate_execution():
            # 启动计划
            self.start_project(project_id)
            time.sleep(0.5)
            
            total_tasks = project.get('total_tasks', 0)
            current_task = project.get('current_task', 0)
            
            # 逐个执行任务
            for task_num in range(current_task + 1, total_tasks + 1):
                time.sleep(task_duration)
                self.advance_task(project_id)
                
        # 在后台线程中执行
        thread = threading.Thread(target=simulate_execution, daemon=True)
        thread.start()
        return True
        
    def _calculate_total_time(self, tasks: List[Dict]) -> str:
        """
        计算任务总时间
        
        Args:
            tasks (List[Dict]): 任务列表
            
        Returns:
            str: 总时间估算
        """
        if not tasks:
            return "0分钟"
            
        total_minutes = 0
        for task in tasks:
            time_str = task.get('estimated_time', '0分钟')
            # 简单解析时间字符串
            try:
                if '分钟' in time_str:
                    minutes = int(time_str.replace('分钟', ''))
                    total_minutes += minutes
                elif '小时' in time_str:
                    hours = float(time_str.replace('小时', ''))
                    total_minutes += int(hours * 60)
            except (ValueError, AttributeError):
                continue
                
        if total_minutes >= 60:
            hours = total_minutes // 60
            minutes = total_minutes % 60
            if minutes > 0:
                return f"{hours}小时{minutes}分钟"
            else:
                return f"{hours}小时"
        else:
            return f"{total_minutes}分钟"


# 全局单例实例
_project_api_instance = None


def get_project_api() -> ProjectAPI:
    """
    获取测试计划API的单例实例
    
    Returns:
        ProjectAPI: API实例
    """
    global _project_api_instance
    if _project_api_instance is None:
        _project_api_instance = ProjectAPI()
    return _project_api_instance


# 便捷函数
def create_project(plan_name: str, description: str = "", signal_type: str = "", 
                  tasks: List[Dict] = None) -> Optional[str]:
    """
    便捷函数：创建新的测试计划
    """
    return get_project_api().create_project(plan_name, description, signal_type, tasks)


def start_project(project_id: str) -> bool:
    """
    便捷函数：启动测试计划
    """
    return get_project_api().start_project(project_id)


def pause_project(project_id: str) -> bool:
    """
    便捷函数：暂停测试计划
    """
    return get_project_api().pause_project(project_id)


def complete_project(project_id: str) -> bool:
    """
    便捷函数：完成测试计划
    """
    return get_project_api().complete_project(project_id)


def set_error(project_id: str, error_message: str = "") -> bool:
    """
    便捷函数：设置计划错误状态
    """
    return get_project_api().set_project_error(project_id, error_message)


def advance_task(project_id: str) -> bool:
    """
    便捷函数：推进计划任务
    """
    return get_project_api().advance_task(project_id)


def simulate_execution(project_id: str, task_duration: float = 3.0) -> bool:
    """
    便捷函数：模拟计划执行
    """
    return get_project_api().simulate_project_execution(project_id, task_duration)


# 使用示例
if __name__ == "__main__":
    """
    使用示例代码
    展示如何在不同线程中动态操作项目数据
    """
    
    # 获取API实例
    api = get_project_api()
    
    # 创建新项目
    project_id = api.create_project(
        "动态测试项目",
        "这是一个演示动态更新的测试项目",
        "SPI",
        [
            {
                "task_name": "SPI初始化",
                "signal_type": "SPI",
                "priority": "high",
                "estimated_time": "5分钟",
                "test_description": "初始化SPI接口"
            },
            {
                "task_name": "SPI数据传输",
                "signal_type": "SPI",
                "priority": "high",
                "estimated_time": "10分钟",
                "test_description": "测试SPI数据传输"
            },
            {
                "task_name": "SPI性能测试",
                "signal_type": "SPI",
                "priority": "medium",
                "estimated_time": "8分钟",
                "test_description": "测试SPI传输性能"
            }
        ]
    )
    
    print(f"创建项目成功，ID: {project_id}")
    
    # 模拟项目执行（在后台线程中）
    if project_id:
        api.simulate_project_execution(project_id, task_duration=2.0)
        
    # 等待一段时间观察变化
    time.sleep(10) 