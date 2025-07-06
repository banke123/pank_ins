"""
测试基础对话链
用于测试和演示level_base_chain.py的功能
"""
import os
import sys
from dotenv import load_dotenv

# 添加项目根目录到Python路径
current_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
sys.path.insert(0, project_root)

from src.utils.logger_config import setup_logging, get_logger
from src.ai_chat.tests.llm.level_base_chain import LevelBaseChain

# 加载环境变量 - 从项目根目录加载
load_dotenv(dotenv_path=os.path.join(project_root, '.env'))

# 初始化日志系统
setup_logging()
logger = get_logger(__name__)


def check_environment():
    """检查环境变量"""
    api_key = os.getenv("QIANFAN_API_KEY")
    api_url = os.getenv("QIANFAN_API_URL")
    
    if not api_key or not api_url:
        raise ValueError("请检查环境变量: QIANFAN_API_KEY 和 QIANFAN_API_URL")
    
    print("✓ 环境检查通过")


def run_interactive_test():
    """运行交互式测试"""
    print("\n=== 基础对话链测试 ===")
    print("支持4种复杂度的智能处理：")
    print("  难度0: 直接问答")
    print("  难度1: 直接示波器操作")
    print("  难度2: 指令解析 → 具体设置")
    print("  难度3: 项目规划 → 步骤管理")
    print("\n可用命令:")
    print("  /exit    - 退出程序")
    print("  /clear   - 清空对话历史")
    print("  /history - 显示对话历史")
    print("=" * 50)
    
    # 创建基础对话链
    chain = LevelBaseChain()
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
                    chain.clear_history(container_id)
                    print("已清空对话历史")
                    continue
                    
                elif command == "history":
                    history = chain.get_history(container_id)
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
            response = chain.process_message(container_id, user_input)
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
        # 检查环境
        check_environment()
        
        # 运行交互式测试
        run_interactive_test()
        
    except Exception as e:
        logger.error(f"程序运行错误: {e}")
        print(f"程序运行错误: {e}")


if __name__ == "__main__":
    main()


