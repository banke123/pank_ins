#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Pank Ins 主程序入口

这是一个使用AI来控制示波器的Python项目，采用现代化QML界面
主要功能包括：
- AI 大模型控制（langchain框架）
- 现代化QML界面（PyQt6 + QML）
- 多线程消息交互（pykka）
- 时序图功能
- 示波器控制
- 智能测试流程
"""

import sys
import os
import logging
from pathlib import Path
import time

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QTimer, Slot
import pykka

# 导入项目模块
from src.ui.modern_login_window import ModernLoginWindow
from src.actors.ui_actor import UIActor
from src.actors.ai_actor import AIActor
from src.config.settings import Settings
from src.utils.logger_config import setup_logging


def setup_environment():
    """设置环境变量和配置 - 与qml_main_window.py保持一致"""
    # 设置QML样式（必须在创建QApplication之前设置）
    os.environ['QT_QUICK_CONTROLS_STYLE'] = 'Material'
    os.environ['QT_QUICK_CONTROLS_MATERIAL_THEME'] = 'Light'
    os.environ['QT_QUICK_CONTROLS_MATERIAL_ACCENT'] = '#4f46e5'
    
    # 启用高DPI支持（必须在创建QApplication之前设置）
    os.environ['QT_ENABLE_HIGHDPI_SCALING'] = '1'
    os.environ['QT_SCALE_FACTOR_ROUNDING_POLICY'] = 'PassThrough'


class PankInsApplication:
    """Pank Ins 应用程序主类"""
    
    def __init__(self):
        self.app = None
        self.login_window = None
        self.ui_actor_ref = None  # UI Actor引用
        self.ai_actor_ref = None  # AI Actor引用
        self.settings = None
        self.logger = None
        self.actor_system_initialized = False
        
    def setup_logging(self):
        """第一步：设置日志系统"""
        setup_logging(level="INFO", console_level="INFO", file_level="DEBUG")
        self.logger = logging.getLogger(__name__)
        self.logger.info("="*60)
        self.logger.info("🚀 启动 Pank Ins AI控制示波器系统")
        self.logger.info("="*60)
        self.logger.info("✅ 步骤1: 日志系统配置完成")
        
    def initialize_actor_system(self):
        """第二步：初始化Actor系统"""
        try:
            self.logger.info("🎭 步骤2: 初始化Actor系统...")
            
            # 检查pykka是否已经初始化
            if not hasattr(pykka, '_actor_system') or pykka._actor_system is None:
                self.logger.info("初始化pykka Actor系统...")
                # pykka会自动初始化，无需手动操作
            
            self.actor_system_initialized = True
            self.logger.info("✅ 步骤2: Actor系统初始化完成")
            
        except Exception as e:
            self.logger.error(f"❌ 步骤2失败: Actor系统初始化失败 - {e}")
            raise
            
    def start_ui_actor(self):
        """第三步：启动UI Actor"""
        try:
            self.logger.info("🎨 步骤3: 启动UI Actor...")
            
            # 启动UI Actor
            self.ui_actor_ref = UIActor.start()
            
            # 等待UI Actor初始化完成
            time.sleep(0.5)
            
            # 检查UI Actor状态
            try:
                status = self.ui_actor_ref.ask({'action': 'get_status'}, timeout=3.0)
                if status.get('status') == 'running':
                    self.logger.info("✅ 步骤3: UI Actor启动成功")
                else:
                    self.logger.warning(f"⚠️ UI Actor状态异常: {status}")
            except Exception as e:
                self.logger.warning(f"⚠️ 无法获取UI Actor状态: {e}")
                
        except Exception as e:
            self.logger.error(f"❌ 步骤3失败: UI Actor启动失败 - {e}")
            raise
            
    def start_ai_actor(self):
        """第四步：启动AI Actor"""
        try:
            self.logger.info("🤖 步骤4: 启动AI Actor...")
            
            # 启动AI Actor
            self.ai_actor_ref = AIActor.start()
            
            # 等待AI Actor初始化完成
            time.sleep(2.0)  # AI Actor需要更多初始化时间
            
            # 检查AI Actor状态
            try:
                status = self.ai_actor_ref.ask({'action': 'get_status'}, timeout=5.0)
                if status.get('status') == 'running':
                    self.logger.info("✅ 步骤4: AI Actor启动成功")
                else:
                    self.logger.warning(f"⚠️ AI Actor状态异常: {status}")
            except Exception as e:
                self.logger.warning(f"⚠️ 无法获取AI Actor状态: {e}")
                
        except Exception as e:
            self.logger.error(f"❌ 步骤4失败: AI Actor启动失败 - {e}")
            raise
            
    def setup_actor_connections(self):
        """第五步：建立Actor间的连接"""
        try:
            self.logger.info("🔗 步骤5: 建立Actor间连接...")
            
            # 向UI Actor注册AI Actor
            if self.ui_actor_ref and self.ai_actor_ref:
                result = self.ui_actor_ref.ask({
                    'action': 'register_actor',
                    'actor_name': 'ai',
                    'actor_ref': self.ai_actor_ref
                }, timeout=3.0)
                
                if result.get('status') == 'ok':
                    self.logger.info("✅ AI Actor已注册到UI Actor")
                else:
                    self.logger.warning(f"⚠️ AI Actor注册失败: {result}")
            
            # 向AI Actor设置UI Actor引用
            if self.ai_actor_ref and self.ui_actor_ref:
                result = self.ai_actor_ref.ask({
                    'action': 'set_ui_actor_ref',
                    'ui_actor_ref': self.ui_actor_ref
                }, timeout=3.0)
                
                if result.get('status') == 'success':
                    self.logger.info("✅ UI Actor引用已设置到AI Actor")
                else:
                    self.logger.warning(f"⚠️ UI Actor引用设置失败: {result}")
            
            self.logger.info("✅ 步骤5: Actor间连接建立完成")
            
        except Exception as e:
            self.logger.error(f"❌ 步骤5失败: Actor连接建立失败 - {e}")
            raise
        
    def create_application(self):
        """创建QApplication - 在Actor系统启动后"""
        # 🔥 关键：使用与qml_main_window.py相同的创建方式
        self.app = QApplication.instance() or QApplication(sys.argv)
        self.app.setApplicationName("Pank Ins")
        self.app.setApplicationVersion("2.0.0")
        self.app.setOrganizationName("Pank Ins Team")
        
        # 设置高DPI属性 - 与qml_main_window.py一致的方式
        try:
            if hasattr(self.app, 'AA_EnableHighDpiScaling'):
                self.app.setAttribute(self.app.AA_EnableHighDpiScaling, True)
            if hasattr(self.app, 'AA_UseHighDpiPixmaps'):
                self.app.setAttribute(self.app.AA_UseHighDpiPixmaps, True)
        except Exception as e:
            self.logger.warning(f"⚠️ 设置高DPI属性时出现警告: {e}")
            
        self.logger.info("✅ QApplication创建完成")
            
    def load_settings(self):
        """加载配置"""
        self.settings = Settings()
        self.logger.info(f"✅ 配置加载完成: {self.settings.get_config_path()}")
        
    def create_login_window(self):
        """创建登录窗口"""
        self.logger.info("🔐 创建现代化登录窗口...")
        self.login_window = ModernLoginWindow()
        
        # 连接登录信号
        self.login_window.login_success.connect(self.on_login_success)
        self.login_window.login_failed.connect(self.on_login_failed)
        self.login_window.theme_changed.connect(self.on_theme_changed)
        
        self.logger.info("✅ 登录窗口创建成功")
        
    def show_login_window(self):
        """显示登录窗口"""
        self.login_window.show_with_animation()
        self.logger.info("🎭 登录窗口已显示")
        self.logger.info("📝 测试账户: admin/admin123, user/user123, test/test123")
        
    @Slot(str, str)
    def on_login_success(self, username: str, password: str):
        """登录成功处理"""
        self.logger.info(f"🎉 用户 {username} 登录成功")
        
        # 隐藏登录窗口
        self.login_window.hide()
        
        # 延迟启动主界面，给用户一些反馈时间
        QTimer.singleShot(500, lambda: self.start_main_application(username))
        
    @Slot(str)
    def on_login_failed(self, error_msg: str):
        """登录失败处理"""
        self.logger.warning(f"⚠️ 登录失败: {error_msg}")
        
        # 显示错误消息框
        msg = QMessageBox()
        msg.setWindowTitle("登录失败")
        msg.setText("用户名或密码错误")
        msg.setInformativeText("请检查您的登录凭据并重试")
        msg.setIcon(QMessageBox.Warning)
        msg.exec()
        
    @Slot(str)
    def on_theme_changed(self, theme_name: str):
        """主题切换处理"""
        self.logger.info(f"🎨 主题已切换到: {theme_name}")
        
    def start_main_application(self, username: str):
        """启动主应用程序"""
        try:
            self.logger.info("="*60)
            self.logger.info(f"🚀 启动主应用程序 - 用户: {username}")
            self.logger.info("="*60)
            
            # 通过UI Actor启动主窗口
            if self.ui_actor_ref:
                result = self.ui_actor_ref.ask({
                    'action': 'start_main_window',
                    'username': username
                }, timeout=10.0)
                
                if result.get('status') == 'ok':
                    self.logger.info("✅ 主窗口启动成功")
                    
                    # 关闭登录窗口
                    if self.login_window:
                        self.login_window.close()
                        self.login_window = None
                        
                    self.logger.info("🎯 主应用程序启动完成")
                    self.logger.info("💡 所有Actor系统已就绪，可以开始使用")
                    
                else:
                    self.logger.error(f"❌ 主窗口启动失败: {result.get('message')}")
                    self.show_error_message("主窗口启动失败", result.get('message', '未知错误'))
            else:
                self.logger.error("❌ UI Actor未初始化，无法启动主窗口")
                self.show_error_message("系统错误", "UI Actor未初始化")
                
        except Exception as e:
            self.logger.error(f"❌ 启动主应用程序失败: {e}")
            import traceback
            self.logger.error(f"详细错误信息:\n{traceback.format_exc()}")
            self.show_error_message("启动失败", f"错误信息: {str(e)}")
            
    def show_error_message(self, title: str, message: str):
        """显示错误消息对话框"""
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setIcon(QMessageBox.Critical)
        msg.exec()
        self.app.quit()
            
    @Slot()
    def on_main_window_closed(self):
        """主窗口关闭处理"""
        self.logger.info("🔄 正在关闭应用...")
        try:
            # 停止Actor系统
            if self.ai_actor_ref:
                self.ai_actor_ref.stop()
                self.logger.info("✅ AI Actor已停止")
                
            if self.ui_actor_ref:
                self.ui_actor_ref.stop()
                self.logger.info("✅ UI Actor已停止")
                
            # 停止整个Actor系统
            pykka.ActorRegistry.stop_all()
            self.logger.info("✅ Actor系统已停止")
            
        except Exception as e:
            self.logger.error(f"❌ 停止Actor系统时出错: {e}")
        
        # 退出应用
        self.app.quit()
        
    @Slot()
    def cleanup_on_exit(self):
        """应用程序退出时的清理处理"""
        self.logger.info("🧹 应用程序退出时清理资源...")
        try:
            # 确保所有Actor都被停止
            if self.ai_actor_ref:
                try:
                    self.ai_actor_ref.stop()
                    self.logger.info("✅ AI Actor已停止")
                except Exception as e:
                    self.logger.error(f"❌ 停止AI Actor失败: {e}")
                    
            if self.ui_actor_ref:
                try:
                    self.ui_actor_ref.stop()
                    self.logger.info("✅ UI Actor已停止")
                except Exception as e:
                    self.logger.error(f"❌ 停止UI Actor失败: {e}")
            
            # 确保整个Actor系统被停止
            try:
                pykka.ActorRegistry.stop_all()
                self.logger.info("✅ 所有Actor系统已清理")
            except Exception as e:
                self.logger.error(f"❌ 清理Actor系统失败: {e}")
                
        except Exception as e:
            self.logger.error(f"❌ 清理过程中出现异常: {e}")
        
        self.logger.info("🏁 应用程序清理完成")
        
    def run(self):
        """运行应用程序"""
        try:
            # 🔥 关键：必须在最开始设置环境变量（影响QML样式）
            setup_environment()
            
            # 第一步：配置日志系统
            self.setup_logging()
            
            # 第二步：初始化Actor系统
            self.initialize_actor_system()
            
            # 第三步：启动UI Actor
            self.start_ui_actor()
            
            # 第四步：启动AI Actor
            self.start_ai_actor()
            
            # 第五步：建立Actor间连接
            self.setup_actor_connections()
            
            self.logger.info("🎯 所有Actor系统启动完成，开始创建UI界面...")
            
            # 创建应用（Actor系统已启动）
            self.create_application()
            
            # 🔥 重要：连接应用程序退出时的清理信号
            self.app.aboutToQuit.connect(self.cleanup_on_exit)
            
            # 加载配置
            self.load_settings()
            
            # 创建并显示登录窗口
            self.create_login_window()
            self.show_login_window()
            
            # 运行应用
            exit_code = self.app.exec()
            self.logger.info(f"📊 应用退出，退出代码: {exit_code}")
            return exit_code
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ 应用启动失败: {e}")
                import traceback
                self.logger.error(f"详细错误信息:\n{traceback.format_exc()}")
            else:
                print(f"❌ 应用启动失败: {e}")
            return 1


def main():
    """主程序入口"""
    app = PankInsApplication()
    return app.run()


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 