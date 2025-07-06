"""
应用启动器

提供统一的应用程序启动入口
登录成功后启动完整的Actor系统，实现多线程架构
"""

import sys
import os
import logging
import pykka
import time

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from PySide6.QtWidgets import QApplication
from src.ui.login_window import LoginWindow
from src.actors import (
    UIActor, 
    # AIActor, 
    # OscilloscopeActor, 
    # DataProcessorActor
)

# 导入AI Actor
from src.actors.ai_actor import AIActor


class ActorSystem:
    """Actor系统管理器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.actors = {}
        self.startup_order = [
            # ('logger', LoggerActor),
            # ('data_processor', DataProcessorActor), 
            # ('oscilloscope', OscilloscopeActor),
            ('ai', AIActor),        # 添加AI Actor
            ('ui', UIActor)  # UI Actor最后启动，因为它需要与其他Actor通信
        ]
        
    def start_all_actors(self) -> bool:
        """
        启动所有Actor
        
        Returns:
            bool: 是否启动成功
        """
        self.logger.info("开始启动Actor系统...")
        
        try:
            for actor_name, actor_class in self.startup_order:
                self.logger.info(f"启动 {actor_name} Actor...")
                
                # 启动Actor
                actor_ref = actor_class.start()
                
                # 根据Actor类型设置不同的等待时间
                if actor_name == 'ai':
                    # AI Actor需要更多初始化时间
                    self.logger.info(f"等待 {actor_name} Actor 初始化完成...")
                    time.sleep(3.0)  # 给AI Actor更多初始化时间
                else:
                    time.sleep(0.2)  # 其他Actor较短等待时间
                
                # 检查Actor状态（带重试机制）
                status_ok = False
                max_retries = 3
                timeout_seconds = 10.0 if actor_name == 'ai' else 3.0
                
                for retry in range(max_retries):
                    try:
                        self.logger.info(f"检查 {actor_name} Actor状态 (尝试 {retry + 1}/{max_retries})")
                        status = actor_ref.ask({'action': 'get_status'}, timeout=timeout_seconds)
                        
                        if status.get('status') == 'running':
                            self.actors[actor_name] = actor_ref
                            self.logger.info(f"{actor_name} Actor启动成功")
                            status_ok = True
                            break
                        else:
                            self.logger.warning(f"{actor_name} Actor状态异常: {status}")
                            
                    except Exception as e:
                        self.logger.warning(f"检查 {actor_name} Actor状态失败 (尝试 {retry + 1}): {e}")
                        if retry < max_retries - 1:
                            self.logger.info(f"等待 2 秒后重试...")
                            time.sleep(2.0)  # 重试前等待
                
                if not status_ok:
                    self.logger.error(f"{actor_name} Actor启动失败，状态检查超时")
                    return False
            
            # 建立Actor之间的连接
            self._setup_actor_connections()
            
            self.logger.info(f"Actor系统启动完成，共启动 {len(self.actors)} 个Actor")
            return True
            
        except Exception as e:
            self.logger.error(f"Actor系统启动失败: {e}")
            return False
    
    def _setup_actor_connections(self):
        """建立Actor之间的连接"""
        try:
            # 向UI Actor发送其他Actor的引用，以便后续通信
            if 'ui' in self.actors and 'ai' in self.actors:
                self.actors['ui'].tell({
                    'action': 'register_actor',
                    'actor_name': 'ai',
                    'actor_ref': self.actors['ai']
                })
                
                # 向AI Actor设置UI Actor引用，用于流式回调
                self.actors['ai'].tell({
                    'action': 'set_ui_actor_ref',
                    'ui_actor_ref': self.actors['ui']
                })
            
            if 'ui' in self.actors and 'oscilloscope' in self.actors:
                self.actors['ui'].tell({
                    'action': 'register_actor', 
                    'actor_name': 'oscilloscope',
                    'actor_ref': self.actors['oscilloscope']
                })
                
            if 'ui' in self.actors and 'data_processor' in self.actors:
                self.actors['ui'].tell({
                    'action': 'register_actor',
                    'actor_name': 'data_processor', 
                    'actor_ref': self.actors['data_processor']
                })
                
            self.logger.info("Actor连接建立完成")
            
        except Exception as e:
            self.logger.error(f"建立Actor连接失败: {e}")
    
    def stop_all_actors(self):
        """停止所有Actor"""
        self.logger.info("停止Actor系统...")
        
        # 按相反顺序停止Actor
        for actor_name in reversed(list(self.actors.keys())):
            try:
                self.logger.info(f"停止 {actor_name} Actor...")
                self.actors[actor_name].stop()
            except Exception as e:
                self.logger.error(f"停止 {actor_name} Actor失败: {e}")
        
        # 停止Actor系统
        try:
            pykka.ActorRegistry.stop_all()
            self.logger.info("Actor系统已完全停止")
        except Exception as e:
            self.logger.error(f"停止Actor系统失败: {e}")
        
        self.actors.clear()
    
    def get_actor(self, actor_name: str):
        """获取指定Actor的引用"""
        return self.actors.get(actor_name)
    
    def get_system_status(self) -> dict:
        """获取系统状态"""
        status = {}
        for actor_name, actor_ref in self.actors.items():
            try:
                actor_status = actor_ref.ask({'action': 'get_status'}, timeout=1.0)
                status[actor_name] = actor_status
            except Exception as e:
                status[actor_name] = {"status": "error", "message": str(e)}
        return status


class AppLauncher:
    """
    应用启动器类
    
    管理应用程序的启动流程，登录成功后启动完整的Actor系统
    """
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.setup_app()
        
        self.login_window = None
        self.actor_system = None
        self.logger = logging.getLogger(__name__)
        
    def setup_app(self):
        """
        设置应用程序属性
        """
        self.app.setApplicationName("Pank Ins")
        self.app.setApplicationVersion("1.0.0")
        self.app.setOrganizationName("Pank Ins Team")
        self.app.setApplicationDisplayName("AI 控制示波器系统")
        
    def start_with_login(self):
        """
        从登录窗口开始启动应用
        """
        self.login_window = LoginWindow()
        
        # 连接登录成功信号
        self.login_window.login_success.connect(self.on_login_success)
        self.login_window.login_failed.connect(self.on_login_failed)
        
        # 显示登录窗口
        self.login_window.show_with_animation()
        
        # 设置应用退出时的清理
        self.app.aboutToQuit.connect(self._cleanup_system)
        
        return self.app.exec()
        
    def start_main_directly(self):
        """
        直接启动主窗口（跳过登录）
        """
        self.logger.info("跳过登录，直接启动系统")
        
        # 直接启动Actor系统
        success = self._start_actor_system()
        
        if success:
            # 启动主窗口
            self._start_main_window()
        else:
            self.logger.error("Actor系统启动失败，无法启动主窗口")
            return 1
        
        # 设置应用退出时的清理
        self.app.aboutToQuit.connect(self._cleanup_system)
        
        return self.app.exec()
        
    def on_login_success(self, username, password):
        """
        登录成功处理
        
        Args:
            username (str): 用户名
            password (str): 密码
        """
        self.logger.info(f"用户 {username} 登录成功，开始启动系统...")
        
        # 启动Actor系统
        success = self._start_actor_system()
        
        if success:
            # 启动主窗口
            self._start_main_window(username)
            
            # 稍微延迟再关闭登录窗口，确保主窗口已经创建
            from PySide6.QtCore import QTimer
            QTimer.singleShot(500, self._close_login_window)
        else:
            self.logger.error("Actor系统启动失败")
            # 可以显示错误对话框或重新显示登录窗口
    
    def _close_login_window(self):
        """延迟关闭登录窗口"""
        if self.login_window:
            self.login_window.close()
            self.login_window = None
    
    def on_login_failed(self, error_message):
        """
        登录失败处理
        
        Args:
            error_message (str): 错误信息
        """
        self.logger.warning(f"登录失败: {error_message}")
    
    def _start_actor_system(self) -> bool:
        """
        启动Actor系统
        
        Returns:
            bool: 启动是否成功
        """
        try:
            self.logger.info("正在启动Actor系统...")
            
            # 创建Actor系统
            self.actor_system = ActorSystem()
            
            # 启动所有Actor
            success = self.actor_system.start_all_actors()
            
            if success:
                self.logger.info("Actor系统启动成功")
                # 打印系统状态
                status = self.actor_system.get_system_status()
                for actor_name, actor_status in status.items():
                    self.logger.info(f"{actor_name}: {actor_status.get('status', 'unknown')}")
            else:
                self.logger.error("Actor系统启动失败")
                
            return success
            
        except Exception as e:
            self.logger.error(f"启动Actor系统异常: {e}")
            return False
    
    def _start_main_window(self, username=None):
        """
        启动主窗口
        
        Args:
            username (str): 用户名
        """
        try:
            # 获取UI Actor
            ui_actor = self.actor_system.get_actor('ui')
            
            if ui_actor:
                # 通过UI Actor启动主窗口
                result = ui_actor.ask({
                    'action': 'start_main_window',
                    'username': username
                }, timeout=5.0)
                
                if result.get('status') == 'ok':
                    self.logger.info("主窗口启动成功")
                else:
                    self.logger.error(f"主窗口启动失败: {result.get('message')}")
            else:
                self.logger.error("UI Actor未找到，无法启动主窗口")
                
        except Exception as e:
            self.logger.error(f"启动主窗口异常: {e}")
    
    def _cleanup_system(self):
        """清理系统资源"""
        try:
            self.logger.info("开始清理系统资源...")
            
            if self.actor_system:
                self.actor_system.stop_all_actors()
                
            self.logger.info("系统清理完成")
            
        except Exception as e:
            self.logger.error(f"清理系统资源失败: {e}")
    
    def get_actor_system(self):
        """获取Actor系统引用"""
        return self.actor_system


# def main():
#     """
#     主函数
#     """
#     import argparse
    
#     # 创建命令行参数解析器
#     parser = argparse.ArgumentParser(description="Pank Ins - AI 控制示波器系统")
#     parser.add_argument(
#         "--skip-login", 
#         action="store_true", 
#         help="跳过登录直接启动主窗口"
#     )
#     parser.add_argument(
#         "--mode",
#         choices=["login", "main"],
#         default="login",
#         help="启动模式: login(登录窗口) 或 main(主窗口)"
#     )
    
#     args = parser.parse_args()
    
#     # 创建启动器
#     launcher = AppLauncher()
    
#     # 根据参数选择启动方式
#     if args.skip_login or args.mode == "main":
#         print("直接启动主窗口...")
#         return launcher.start_main_directly()
#     else:
#         print("启动登录窗口...")
#         return launcher.start_with_login()


# if __name__ == "__main__":
#     sys.exit(main()) 