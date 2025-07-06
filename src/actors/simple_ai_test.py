#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简化的AI测试脚本
直接测试基本的AI功能，避免复杂的依赖链
"""

import os
import sys

# 添加项目根目录到Python路径
current_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
sys.path.insert(0, project_root)

from src.utils.logger_config import setup_logging, get_logger
from src.ai_chat.tests.llm.history_manager import HistoryManager

# 配置日志系统 - 简单测试使用INFO级别
setup_logging(
    level="INFO",
    console_level="INFO",
    file_level="DEBUG",
    enable_colored_console=True
)
logger = get_logger(__name__)


class SimpleAIChat:
    """简化的AI聊天类"""
    
    def __init__(self):
        """初始化"""
        self.history_manager = HistoryManager()
        logger.info("SimpleAIChat 初始化成功")
    
    def process_message(self, container_id: str, message: str) -> str:
        """处理用户消息（模拟版本）"""
        try:
            # 如果容器不存在，创建新容器
            if container_id not in self.history_manager.get_all_container_ids():
                self.history_manager.create_container(container_id)
            
            # 添加用户消息到历史
            self.history_manager.add_message(container_id, "user", message)
            
            # 模拟AI回复
            if "你好" in message or "hello" in message.lower():
                response = "你好！我是示波器AI助手，可以帮助您进行测量和分析。"
            elif "示波器" in message:
                response = "我可以帮助您操作示波器，包括设置通道、触发、测量频率等功能。"
            elif "测试" in message:
                response = "系统正在正常运行，所有模块导入成功！您可以进行各种测试。"
            elif "help" in message.lower() or "帮助" in message:
                response = """我可以帮助您：
1. 示波器操作和设置
2. 信号测量和分析  
3. 测试流程规划
4. 数据记录和导出
请告诉我您需要什么帮助？"""
            else:
                response = f"收到您的消息：{message}。这是一个模拟回复，实际AI功能需要配置API密钥后才能使用。"
            
            # 添加助手回复到历史
            self.history_manager.add_message(container_id, "assistant", response)
            
            logger.info(f"处理消息成功 - 容器ID: {container_id}")
            return response
            
        except Exception as e:
            logger.error(f"处理消息失败: {e}")
            return f"处理消息时发生错误: {str(e)}"
    
    def get_history(self, container_id: str) -> list:
        """获取对话历史"""
        return self.history_manager.get_history(container_id)
    
    def clear_history(self, container_id: str) -> bool:
        """清空对话历史"""
        return self.history_manager.clear_history(container_id)


def run_interactive_test():
    """运行交互式测试"""
    print("\n=== 简化AI聊天测试 ===")
    print("这是一个基础功能测试版本")
    print("支持基本的对话管理和历史记录功能")
    print("\n可用命令:")
    print("  /exit    - 退出程序")
    print("  /clear   - 清空对话历史")
    print("  /history - 显示对话历史")
    print("=" * 50)
    
    # 创建简化AI聊天
    ai_chat = SimpleAIChat()
    container_id = "test_user"  # 使用固定的测试用户ID
    
    while True:
        try:
            user_input = input("\n请输入问题: ").strip()
            
            if not user_input:
                continue
                
            if user_input.startswith("/"):
                command = user_input[1:].lower()
                
                if command in ["exit", "quit"]:
                    print("再见！")
                    break
                    
                elif command == "clear":
                    ai_chat.clear_history(container_id)
                    print("已清空对话历史")
                    continue
                    
                elif command == "history":
                    history = ai_chat.get_history(container_id)
                    if not history:
                        print("暂无对话历史")
                    else:
                        print("\n=== 对话历史 ===")
                        for msg in history:
                            role = "用户" if msg["role"] == "user" else "助手"
                            print(f"{role}: {msg['content']}")
                    continue
                    
                else:
                    print(f"未知命令: {command}")
                    continue
            
            # 处理用户输入
            print(f"\n用户: {user_input}")
            response = ai_chat.process_message(container_id, user_input)
            print(f"\n助手: {response}")
            
        except KeyboardInterrupt:
            print("\n程序已中断")
            break
        except Exception as e:
            logger.error(f"处理消息时发生错误: {e}")
            print(f"发生错误: {e}")


def main():
    """主函数"""
    try:
        print("=== 简化AI测试程序 ===")
        print("✓ 导入成功")
        print("✓ 日志系统初始化成功")
        print("✓ 历史管理器准备就绪")
        
        # 运行交互式测试
        run_interactive_test()
        
    except Exception as e:
        logger.error(f"程序运行错误: {e}")
        print(f"程序运行错误: {e}")


if __name__ == "__main__":
    main() 