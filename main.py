#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI示波器控制系统主程序

主要功能：
1. 初始化系统
2. 启动Actor系统
3. 使用AppLauncher启动UI界面
4. 系统清理和退出

@author: PankIns Team
@version: 1.0.0
"""

import sys
import os
import logging
import argparse


def setup_environment():
    """
    设置环境变量和DPI支持
    """
    # 设置高DPI支持 - 必须在QApplication创建之前
    os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '1'
    os.environ['QT_SCALE_FACTOR'] = '1'
    
    # Windows特有的DPI设置
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)  # 设置DPI感知
    except:
        pass  # 如果失败则忽略


def setup_logging_and_core():
    """
    设置日志和核心系统
    """
    from src.utils import setup_logging
    from src.core import SystemManager
    
    # 设置日志
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("启动AI示波器控制系统")
    
    # 创建系统管理器
    system_manager = SystemManager()
    
    return logger, system_manager


class MainApplication:
    """
    主应用程序类，管理整个应用的生命周期
    """
    
    def __init__(self, skip_login=False):
        self.logger = None
        self.system_manager = None
        self.app_launcher = None
        self.skip_login = skip_login
        
    def initialize(self):
        """
        初始化应用程序
        """
        # 1. 设置环境
        setup_environment()
        
        # 2. 设置日志和核心系统
        self.logger, self.system_manager = setup_logging_and_core()
        
        # 3. 启动系统管理器
        try:
            self.system_manager.start_actors()
            self.logger.info("系统管理器启动成功")
        except Exception as e:
            self.logger.error(f"系统管理器启动失败: {e}")
            raise
            
    def run(self):
        """
        运行应用程序
        """
        try:
            # 导入AppLauncher
            from src.ui import AppLauncher
            
            # 创建应用启动器
            self.app_launcher = AppLauncher()
            
            # 根据参数选择启动方式
            if self.skip_login:
                self.logger.info("直接启动主窗口")
                return self.app_launcher.start_main_directly()
            else:
                self.logger.info("启动登录窗口")
                return self.app_launcher.start_with_login()
                
        except KeyboardInterrupt:
            self.logger.info("用户请求关闭系统")
            return 0
        except Exception as e:
            self.logger.error(f"应用程序运行错误: {e}")
            return 1
            
    def cleanup(self):
        """
        清理资源
        """
        try:
            if self.system_manager:
                self.system_manager.stop_actors()
                self.logger.info("系统管理器已停止")
        except Exception as e:
            self.logger.error(f"系统清理失败: {e}")
        
        if self.logger:
            self.logger.info("应用程序退出")


def main():
    """
    主程序入口
    """
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description="Pank Ins - AI 控制示波器系统")
    parser.add_argument(
        "--skip-login", 
        action="store_true", 
        help="跳过登录直接启动主窗口"
    )
    parser.add_argument(
        "--mode",
        choices=["login", "main"],
        default="login",
        help="启动模式: login(登录窗口) 或 main(主窗口)"
    )
    
    args = parser.parse_args()
    
    # 确定是否跳过登录
    skip_login = args.skip_login or args.mode == "main"
    
    # 创建应用实例
    app_instance = MainApplication(skip_login=skip_login)
    
    try:
        # 初始化应用程序
        app_instance.initialize()
        
        # 运行应用程序
        exit_code = app_instance.run()
        
    except Exception as e:
        print(f"系统启动失败: {e}")
        if app_instance.logger:
            app_instance.logger.error(f"系统启动失败: {e}")
        exit_code = 1
        
    finally:
        # 清理资源
        app_instance.cleanup()
        
    return exit_code


if __name__ == "__main__":
    sys.exit(main()) 