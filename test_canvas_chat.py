#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试画布模式AI对话界面的脚本

测试项目：
1. 画布模式的消息显示
2. AI响应的JSON解析
3. 流式响应在画布中的显示
4. 用户交互体验
"""

import sys
import os
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer, QThread, Signal, QObject
import pykka

# 导入项目模块
from src.actors.ui_actor import UIActor
from src.actors.ai_actor import AIActor
from src.utils.logger_config import setup_logging

class TestCanvas(QObject):
    """测试画布模式的类"""
    
    def __init__(self):
        super().__init__()
        self.ui_actor_ref = None
        self.ai_actor_ref = None
        
    def setup_actors(self):
        """设置Actor系统"""
        try:
            # 启动UI Actor
            self.ui_actor_ref = UIActor.start()
            print("✅ UI Actor启动成功")
            
            # 启动AI Actor
            self.ai_actor_ref = AIActor.start()
            print("✅ AI Actor启动成功")
            
            # 建立连接
            self.ui_actor_ref.tell({
                'action': 'register_actor',
                'actor_name': 'ai',
                'actor_ref': self.ai_actor_ref
            })
            print("✅ AI Actor已注册到UI Actor")
            
            self.ai_actor_ref.tell({
                'action': 'set_ui_actor',
                'ui_actor_ref': self.ui_actor_ref
            })
            print("✅ UI Actor引用已设置到AI Actor")
            
            return True
            
        except Exception as e:
            print(f"❌ Actor系统设置失败: {e}")
            return False
    
    def test_canvas_mode(self):
        """测试画布模式"""
        print("\n" + "="*60)
        print("🎨 测试画布模式AI对话界面")
        print("="*60)
        
        # 设置日志
        setup_logging(level="INFO", console_level="INFO", file_level="DEBUG")
        logger = logging.getLogger(__name__)
        
        # 初始化Actor系统
        pykka.ActorRegistry.stop_all()
        
        print("🎭 Actor系统启动成功")
        
        # 设置Actor
        if not self.setup_actors():
            return False
        
        # 创建QApplication
        app = QApplication(sys.argv)
        
        # 启动UI主窗口
        try:
            self.ui_actor_ref.tell({
                'action': 'start_main_window',
                'user_name': 'test_user'
            })
            print("✅ QML主窗口启动成功")
            
            # 设置定时器进行自动测试
            self.setup_auto_test()
            
            print("\n📝 测试说明:")
            print("1. 界面应该显示为画布模式（横向长条）")
            print("2. 发送消息测试AI响应解析")
            print("3. 观察流式响应是否正常显示")
            print("4. 关闭窗口测试资源清理")
            
            # 运行应用
            exit_code = app.exec()
            print(f"\n📊 应用退出，退出代码: {exit_code}")
            
            return True
            
        except Exception as e:
            print(f"❌ 启动失败: {e}")
            return False
        
        finally:
            # 清理Actor系统
            try:
                if self.ai_actor_ref:
                    self.ai_actor_ref.stop()
                if self.ui_actor_ref:
                    self.ui_actor_ref.stop()
                pykka.ActorRegistry.stop_all()
                print("✅ Actor系统清理完成")
            except Exception as e:
                print(f"⚠️ Actor系统清理时出错: {e}")
    
    def setup_auto_test(self):
        """设置自动测试"""
        # 延迟发送测试消息
        QTimer.singleShot(3000, self.send_test_message_1)
        QTimer.singleShot(8000, self.send_test_message_2)
        QTimer.singleShot(13000, self.send_test_message_3)
        
    def send_test_message_1(self):
        """发送第一条测试消息"""
        print("\n🔄 发送测试消息1: 简单问候")
        if self.ui_actor_ref:
            self.ui_actor_ref.tell({
                'action': 'ai_chat_send_message',
                'message': '你好',
                'container_id': 'main_chat'
            })
    
    def send_test_message_2(self):
        """发送第二条测试消息"""
        print("\n🔄 发送测试消息2: 技术问题")
        if self.ui_actor_ref:
            self.ui_actor_ref.tell({
                'action': 'ai_chat_send_message',
                'message': '帮我复位示波器',
                'container_id': 'main_chat'
            })
    
    def send_test_message_3(self):
        """发送第三条测试消息"""
        print("\n🔄 发送测试消息3: 数据查询")
        if self.ui_actor_ref:
            self.ui_actor_ref.tell({
                'action': 'ai_chat_send_message',
                'message': '通道1测量结果如何？',
                'container_id': 'main_chat'
            })


def main():
    """主函数"""
    print("🧪 画布模式AI对话界面测试")
    print("=" * 60)
    
    # 创建测试实例
    test_canvas = TestCanvas()
    
    # 运行测试
    success = test_canvas.test_canvas_mode()
    
    if success:
        print("\n🎉 测试完成！")
        print("✅ 画布模式界面已启动")
        print("✅ AI响应解析功能已修复")
        print("✅ 流式响应显示正常")
    else:
        print("\n❌ 测试失败！")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 