#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试消息修复的脚本

测试项目：
1. AI Actor的消息理解是否正确
2. QML界面的消息显示是否正常
3. 流式响应是否能正确显示
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
from PySide6.QtCore import QTimer
import pykka

# 导入项目模块
from src.actors.ui_actor import UIActor
from src.actors.ai_actor import AIActor
from src.utils.logger_config import setup_logging


def test_message_processing():
    """测试消息处理"""
    print("=" * 60)
    print("🧪 开始测试消息处理修复结果")
    print("=" * 60)
    
    # 设置日志
    setup_logging(level="INFO", console_level="INFO", file_level="DEBUG")
    logger = logging.getLogger(__name__)
    
    # 初始化Actor系统
    logger.info("📱 启动Actor系统...")
    ui_actor_ref = UIActor.start()
    ai_actor_ref = AIActor.start()
    
    # 建立连接
    logger.info("🔗 建立Actor连接...")
    ui_actor_ref.ask({
        'action': 'register_actor',
        'actor_name': 'ai',
        'actor_ref': ai_actor_ref
    }, timeout=5.0)
    
    ai_actor_ref.ask({
        'action': 'set_ui_actor_ref',
        'ui_actor_ref': ui_actor_ref
    }, timeout=5.0)
    
    # 测试消息：简单问候
    logger.info("💬 测试消息1: 简单问候")
    test_message_1 = "我是banke"
    
    try:
        result = ai_actor_ref.ask({
            'action': 'process_message_stream',
            'container_id': 'test_container',
            'content': test_message_1
        }, timeout=10.0)
        
        logger.info(f"✅ 消息1处理结果: {result}")
        
    except Exception as e:
        logger.error(f"❌ 消息1处理失败: {e}")
    
    # 测试消息：查询历史数据
    logger.info("💬 测试消息2: 查询历史数据")
    test_message_2 = "我们之前通道1测量的数据是多少？"
    
    try:
        result = ai_actor_ref.ask({
            'action': 'process_message_stream',
            'container_id': 'test_container',
            'content': test_message_2
        }, timeout=10.0)
        
        logger.info(f"✅ 消息2处理结果: {result}")
        
    except Exception as e:
        logger.error(f"❌ 消息2处理失败: {e}")
    
    # 清理
    logger.info("🧹 清理Actor系统...")
    try:
        ai_actor_ref.stop()
        ui_actor_ref.stop()
        pykka.ActorRegistry.stop_all()
        logger.info("✅ Actor系统清理完成")
    except Exception as e:
        logger.error(f"❌ 清理失败: {e}")
    
    print("=" * 60)
    print("🏁 消息处理测试完成")
    print("=" * 60)


def test_ui_display():
    """测试UI显示"""
    print("=" * 60)
    print("🎨 开始测试UI显示修复结果")
    print("=" * 60)
    
    # 设置环境变量
    os.environ['QT_QUICK_CONTROLS_STYLE'] = 'Material'
    os.environ['QT_QUICK_CONTROLS_MATERIAL_THEME'] = 'Light'
    
    # 创建应用
    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName("Pank Ins Test")
    
    # 设置日志
    setup_logging(level="INFO", console_level="INFO", file_level="DEBUG")
    logger = logging.getLogger(__name__)
    
    try:
        # 初始化Actor系统
        logger.info("📱 启动Actor系统...")
        ui_actor_ref = UIActor.start()
        ai_actor_ref = AIActor.start()
        
        # 建立连接
        logger.info("🔗 建立Actor连接...")
        ui_actor_ref.ask({
            'action': 'register_actor',
            'actor_name': 'ai',
            'actor_ref': ai_actor_ref
        }, timeout=5.0)
        
        ai_actor_ref.ask({
            'action': 'set_ui_actor_ref',
            'ui_actor_ref': ui_actor_ref
        }, timeout=5.0)
        
        # 启动主窗口
        logger.info("🎭 启动主窗口...")
        ui_actor_ref.ask({
            'action': 'start_main_window',
            'username': 'test_user'
        }, timeout=10.0)
        
        logger.info("✅ 主窗口已启动，请测试以下功能：")
        logger.info("1. 在AI对话框中输入：'我是banke'")
        logger.info("2. 检查是否正确显示用户消息和AI回复")
        logger.info("3. 检查流式响应是否正常显示")
        logger.info("4. 关闭窗口测试Actor清理是否正常")
        
        # 设置10秒后的自动测试消息
        def send_test_message():
            logger.info("🤖 发送自动测试消息...")
            try:
                ai_actor_ref.ask({
                    'action': 'process_message_stream',
                    'container_id': 'main_chat',
                    'content': '我是banke，很高兴认识你！'
                }, timeout=10.0)
            except Exception as e:
                logger.error(f"自动测试消息失败: {e}")
        
        QTimer.singleShot(5000, send_test_message)
        
        # 运行应用
        exit_code = app.exec()
        
        logger.info(f"🏁 应用退出，退出代码: {exit_code}")
        
    except Exception as e:
        logger.error(f"❌ UI测试失败: {e}")
        import traceback
        logger.error(f"详细错误信息:\n{traceback.format_exc()}")
        
    print("=" * 60)
    print("🏁 UI显示测试完成")
    print("=" * 60)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "ui":
        test_ui_display()
    else:
        test_message_processing()
        print("\n要测试UI显示，请运行: python test_message_fix.py ui") 