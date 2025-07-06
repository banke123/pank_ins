"""
难度1处理链
用于处理简单的示波器操作指令
"""
import os
import sys
from typing import Dict, Any, List

# 添加项目根目录到Python路径
current_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..', '..'))
sys.path.insert(0, project_root)

from src.ai_chat.llm.agent import UniversalAgent
from src.ai_chat.llm.tools.osc_tools_test import ADVANCED_OSCILLOSCOPE_TOOLS
from src.utils.logger_config import get_logger

logger = get_logger(__name__)

class Level1Chain:
    """难度1处理链，用于处理简单的示波器操作"""
    
    def __init__(self):
        """初始化难度1处理链"""
        # 初始化示波器Agent
        self.oscilloscope_agent = UniversalAgent(
            model_name="deepseek-v3",
            temperature=0.7,
            tools=ADVANCED_OSCILLOSCOPE_TOOLS,
            system_prompt="""你是一个专业的示波器操作助手。你的任务是根据用户的明确指令来操作示波器。按照要求设置指令即可，
            不做任何其他扩展，如果用户没有明确指令，则直接回复没有该指令即可"""

# 你可以使用以下示波器工具：
# - set_channel: 设置通道参数（启用/禁用、电压刻度、耦合方式、探头）
# - set_voltage_scale: 设置电压刻度
# - set_time_scale: 设置时间刻度
# - set_trigger: 设置触发参数
# - capture_waveform: 捕获波形
# - measure_frequency: 测量频率
# - measure_amplitude: 测量幅度
# - save_screenshot: 保存截图
# - reset_oscilloscope: 重置示波器

# 请根据用户的指令，选择合适的工具进行操作。如果指令不够明确，请要求用户提供更多信息。
# 操作完成后，请简洁地描述执行的操作和结果。

# 注意：
# 1. 通道号范围是1-4
# 2. 电压刻度和时间刻度必须大于0
# 3. 在进行测量前，确保相应通道已启用
# 4. 操作前可以先查看当前设置状态"""
        )
    
    def process(self, message: str) -> str:
        """
        处理难度1的消息
        
        Args:
            message: 用户消息
            
        Returns:
            str: 处理结果
        """
        try:
            logger.debug(f"Level1Chain处理消息: {message}")
            
            # 准备消息列表（只包含当前消息）
            messages = [{
                "role": "user",
                "content": message
            }]
            
            # 调用Agent处理
            result = self.oscilloscope_agent.execute(messages)
            
            logger.debug(f"Level1Chain处理结果: {result}")
            print(f"Level1Chain处理结果: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Level1Chain处理失败: {e}")
            return f"示波器操作失败: {str(e)}"
    
    def process_stream(self, message: str):
        """
        流式处理难度1的消息
        
        Args:
            message: 用户消息
            
        Yields:
            str: 流式处理结果
        """
        try:
            logger.debug(f"Level1Chain流式处理消息: {message}")
            
            # 准备消息列表（只包含当前消息）
            messages = [{
                "role": "user",
                "content": message
            }]
            
            # 流式调用Agent处理
            for chunk in self.oscilloscope_agent.execute_stream(messages):
                print(f"Level1Chain流式处理结果: {chunk}")
                yield chunk
                
        except Exception as e:
            logger.error(f"Level1Chain流式处理失败: {e}")
            yield f"示波器操作失败: {str(e)}"
    
    def get_available_tools(self) -> List[str]:
        """获取可用的工具列表"""
        return self.oscilloscope_agent.get_available_tools()
    
    def get_tool_descriptions(self) -> Dict[str, str]:
        """获取工具描述"""
        return self.oscilloscope_agent.get_tool_descriptions()
