"""
基础对话链模块
用于区分对话难度并进行基础处理
"""
import os
import sys
from typing import Dict, Any

# 添加项目根目录到Python路径
current_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..', '..'))
sys.path.insert(0, project_root)

from src.ai_chat.llm.llm import ChatLLM
from src.ai_chat.llm.parser.json_parser import json_extract
from src.ai_chat.llm.chain import ChainBuilder
from src.utils.logger_config import get_logger
from src.ai_chat.tests.llm.history_manager import HistoryManager
from src.ai_chat.tests.llm.level_1_chain import Level1Chain
from src.ai_chat.tests.llm.level_2_chain import Level2Chain
from src.ai_chat.tests.llm.level_3_chain import Level3Chain

logger = get_logger(__name__)

class LevelBaseChain:
    """基础对话链，用于区分对话难度"""
    
    def __init__(self, stream_callback=None, flow_card_update=None):
        """
        初始化基础对话链
        
        Args:
            stream_callback: 流式响应回调函数
            flow_card_update: 流程卡片更新回调函数
        """
        # 初始化历史记录管理器
        self.history_manager = HistoryManager()
        
        # 保存流式回调和流程卡片回调
        self.stream_callback = stream_callback
        self.flow_card_update = flow_card_update
        
        # 初始化各级处理链
        self.level_1_chain = Level1Chain()
        self.level_2_chain = Level2Chain(stream_callback=stream_callback, flow_card_update=flow_card_update)
        self.level_3_chain = Level3Chain(stream_callback=stream_callback, flow_card_update=flow_card_update)
        
        # 当前计划ID
        self.current_plan_id = None

        # 初始化基本对话大模型
        self.chat_llm = ChatLLM(
            model_name="deepseek-v3",
            system_prompt="""你是一个示波器操作员，首先你需要判断用户问题的复杂程度，目前有4种复杂度：

                0: 最简单，不需要操作示波器，只需要回答用户问题，例如："我们之前通道1测量的数据是多少？"，类似这种，不需要操作示波器只需要查找数据回答用户，查找不到如实回答，不要乱编。

                1: 简单，需要操作示波器，当指令是非常明确的，配置参数都是非常具体的，比如："设置通道1 通道打开，电压刻度为1V，时间刻度为1us，其他默认"。

                2: 中等，需要操作示波器，但指令不是很明确，比如："帮我测量这个I2C 信号质量。","帮我测量通道3的时钟频率",这种没有说明具体怎么测量，需要根据信号特征判断，这个也叫任务，需要生成任务名。

                3: 复杂，不需要操作示波器，但需要你做出一些计划，比如："我需要测量test1 这个项目的白盒测试。这个项目有GSENSOR,SPI 3V 电压阈，也有ALS 的I2C 3V 电压阈。最后需要输出测试报告"，例如这种，需要对这个测试做一个测试计划,需要生成计划名。

                请根据用户问题分析复杂度，并按照以下JSON格式输出：
                {
                    "difficulty": 复杂度数字(0-3),
                    "complex_reason": "复杂度判断的原因说明",
                    "content": "如果复杂度为0，则回答用户问题；如果复杂度为1，则直接复制用户问题回复；如果复杂度为2，则回复任务名：任务名，任务描述：用户问题直接复制；如果复杂度为3，则生成计划名：计划名，计划描述：用户问题直接复制"
                }"""
        )

        # 调用主链处理消息
        self.main_chain = self.create_main_chain()
    
    def process_message(self, container_id: str, message: str) -> str:
        """处理用户消息
        
        Args:
            container_id: 对话容器ID
            message: 用户消息
            
        Returns:
            str: 处理结果（仅返回内容）
        """
        # 如果容器不存在，创建新容器
        if container_id not in self.history_manager.get_all_container_ids():
            self.history_manager.create_container(container_id)
        
        # 添加用户消息到历史
        self.history_manager.add_message(container_id, "user", message)
        self.current_message = self.history_manager.get_history(container_id)
        
        try:
            result = self.main_chain.execute(self.current_message)
            
            # 获取回复内容
            response_content = result.get("content", "抱歉，我无法理解您的问题。")
            
            # 添加助手回复到历史
            self.history_manager.add_message(container_id, "assistant", response_content)
            
            # 记录调试信息
            logger.debug(f"难度: {result.get('difficulty')}")
            logger.debug(f"原因: {result.get('complex_reason')}")
            
            return response_content
            
        except Exception as e:
            logger.error(f"处理消息时发生错误: {e}")
            error_response = "抱歉，处理您的消息时发生错误。"
            self.history_manager.add_message(container_id, "assistant", error_response)
            return error_response
    
    def create_main_chain(self):
        """创建主处理链"""
        
        def chat_llm_process(data):
            """主LLM处理"""
            # 调用LLM处理（流式输出）
            print("\n正在思考...")
            response = ""
            for chunk in self.chat_llm.chat_get_response_stream(data):
                print(chunk, end="", flush=True)
                response += chunk
            print("\n")  # 流式输出完成后换行
            
            logger.debug(f"LLM完整响应: {response}")
            return response
        
        def json_extract_main(data):
            """主JSON提取"""
            result = json_extract(data)
            logger.debug(f"JSON解析结果: {result}")
            return result
        
        def case_condition(data):
            """条件判断函数"""
            difficulty = data["difficulty"]
            logger.debug(f"判断难度: {difficulty}")
            
            # 如果是难度2或3，生成计划ID
            if difficulty in [2, 3]:
                # 使用时间戳生成计划ID
                from datetime import datetime
                timestamp = datetime.now()
                date_str = timestamp.strftime("%Y%m%d")
                time_str = timestamp.strftime("%H%M%S")
                
                # 生成计划ID: LEVEL{难度}_{日期}_{时间}
                self.current_plan_id = f"LEVEL{difficulty}_{date_str}_{time_str}"
                logger.info(f"生成计划ID: {self.current_plan_id}")
                data["plan_id"] = self.current_plan_id
            
            return difficulty
        
        def response_direct(data):
            """直接回复（难度0）"""
            content = data["content"]
            logger.debug(f"直接回复: {content}")
            return {
                "difficulty": 0,
                "content": content,
                "complex_reason": data.get("complex_reason", "")
            }
        
        def response_level_1(data):
            """难度1处理"""
            logger.debug("调用Level1Chain处理")
            
            # 获取最后一条用户消息
            last_message = ""
            for msg in reversed(self.current_message):
                if msg["role"] == "user":
                    last_message = msg["content"]
                    break
            
            # 调用Level1Chain处理（不传递历史）
            result = self.level_1_chain.process(last_message)
            # 调用Level1Chain处理（流式输出）
            # print("\n正在处理...")
            # response = ""
            # for chunk in self.level_1_chain.process_stream(last_message):
            #     print(chunk, end="", flush=True)
            #     response += chunk
            # print("\n")  # 流式输出完成后换行
            # result = response
            return {
                "difficulty": 1,
                "content": result,
                "complex_reason": data.get("complex_reason", "")
            }
        
        def response_level_2(data):
            """难度2处理"""
            logger.debug("调用Level2Chain处理")
            
            # 获取最后一条用户消息
            last_message = self.current_message[-1]["content"]
            
            # 使用已生成的计划ID
            logger.info(f"使用计划ID: {self.current_plan_id}")
            
            # 调用Level2Chain处理，传递计划ID
            result = self.level_2_chain.process({
                "message": last_message,
                "plan_id": self.current_plan_id
            })
            
            # Level2Chain现在返回字典，需要提取content
            content = result.get("content", "处理失败") if isinstance(result, dict) else str(result)
            
            return {
                "difficulty": 2,
                "content": content,
                "complex_reason": data.get("complex_reason", ""),
                "plan_id": self.current_plan_id
            }
        
        def response_level_3(data):
            """难度3处理"""
            logger.debug("调用Level3Chain处理")
            
            # 获取最后一条用户消息
            last_message = self.current_message[-1]["content"]
            
            # 使用已生成的计划ID
            logger.info(f"使用计划ID: {self.current_plan_id}")
            
            # 调用Level3Chain处理，传递计划ID
            result = self.level_3_chain.process({
                "message": last_message,
                "plan_id": self.current_plan_id
            })
            
            # Level3Chain现在返回字典，需要提取content
            content = result.get("content", "处理失败") if isinstance(result, dict) else str(result)
            
            return {
                "difficulty": 3,
                "content": content,
                "complex_reason": data.get("complex_reason", ""),
                "plan_id": self.current_plan_id
            }
        
        
        # 构建主链
        return ChainBuilder.serial(
            ChainBuilder.function(chat_llm_process, "主LLM分析"),
            ChainBuilder.function(json_extract_main, "JSON解析"),
            ChainBuilder.conditional(
                condition_func=case_condition,
                branches={
                    0: ChainBuilder.function(response_direct, "直接回复"),
                    1: ChainBuilder.function(response_level_1, "难度1处理"),
                    2: ChainBuilder.function(response_level_2, "难度2处理"),
                    3: ChainBuilder.function(response_level_3, "难度3处理"),
                    # 难度3的处理会在后续实现
                }
            )
        )
    
    def get_history(self, container_id: str) -> list:
        """获取对话历史"""
        return self.history_manager.get_history(container_id)
    
    def clear_history(self, container_id: str) -> bool:
        """清空对话历史"""
        return self.history_manager.clear_history(container_id)
