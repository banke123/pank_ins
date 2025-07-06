"""
基础对话链模块
用于区分对话难度并进行基础处理
"""
from typing import Dict, Any
from ai_chat.llm.llm import ChatLLM
from ai_chat.llm.parser.json_parser import json_extract
from ai_chat.llm.chain import ChainBuilder
from src.utils.logger_config import get_logger
from ai_chat.tests.llm.history_manager import HistoryManager
from ai_chat.tests.llm.level_1_chain import Level1Chain
from ai_chat.tests.llm.level_2_chain import Level2Chain
from ai_chat.tests.llm.level_3_chain import Level3Chain
logger = get_logger(__name__)

class LevelBaseChain:
    """基础对话链，用于区分对话难度"""
    
    def __init__(self, stream_callback=None, flow_card_update=None):
        """初始化基础对话链
        
        Args:
            stream_callback: 流式响应回调函数
            flow_card_update: 流程卡片更新回调函数
        """
        # 保存回调函数
        self.stream_callback = stream_callback
        self.flow_card_update = flow_card_update
        
        # 初始化历史记录管理器
        self.history_manager = HistoryManager()
        
        # 初始化各级处理链
        self.level_1_chain = Level1Chain()
        self.level_2_chain = Level2Chain()
        self.level_3_chain = Level3Chain()
        
        # 初始化基本对话大模型
        self.chat_llm = ChatLLM(
            model_name="deepseek-v3",
            system_prompt="""你是一个专业的示波器操作助手，请仔细分析用户的问题并判断其复杂程度。

对于简单的问候、自我介绍、闲聊等，应该友好回应，不要误解为技术问题。

复杂度分类：
0: 最简单 - 问候、自我介绍、闲聊、查询历史数据等，不需要操作示波器
   例如："你好"、"我是banke"、"我们之前通道1测量的数据是多少？"

1: 简单 - 明确具体的示波器操作指令，参数都很具体
   例如："设置通道1电压刻度为1V，时间刻度为1us"

2: 中等 - 需要操作示波器，但指令不够明确，需要推理
   例如："帮我测量I2C信号质量"、"测量通道3的时钟频率"

3: 复杂 - 需要制定测试计划，不直接操作示波器
   例如："制定某个项目的完整测试计划"

请按以下JSON格式输出：
{
    "difficulty": 复杂度数字(0-3),
    "complex_reason": "判断原因的详细说明",
    "content": "如果复杂度为0，则友好回应用户；其他复杂度则重复用户问题"
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
            # 发送流式开始信号
            if self.stream_callback:
                self.stream_callback("START_STREAM", "")
            
            # 调用LLM处理（流式输出）
            logger.debug("开始LLM流式处理...")
            response = ""
            
            try:
                for chunk in self.chat_llm.chat_get_response_stream(data):
                    response += chunk
                    
                    # 发送流式数据片段
                    if self.stream_callback:
                        self.stream_callback("STREAM_CHUNK", chunk)
                
                # 发送流式结束信号
                if self.stream_callback:
                    self.stream_callback("END_STREAM", "")
                    
                logger.debug(f"LLM流式处理完成，响应长度: {len(response)}")
                return response
                
            except Exception as e:
                logger.error(f"LLM流式处理失败: {e}")
                # 发送流式结束信号
                if self.stream_callback:
                    self.stream_callback("END_STREAM", "")
                return "抱歉，处理您的消息时出现错误。"
        
        def json_extract_main(data):
            """主JSON提取"""
            result = json_extract(data)
            logger.debug(f"JSON解析结果: {result}")
            return result
        
        def case_condition(data):
            """条件判断函数"""
            difficulty = data["difficulty"]
            logger.debug(f"判断难度: {difficulty}")
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
            
            return {
                "difficulty": 1,
                "content": result,
                "complex_reason": data.get("complex_reason", "")
            }
        
        def response_level_2(data):
            """难度2处理"""
            logger.debug("调用Level2Chain处理")
            
            # 获取最后一条用户消息
            last_message = ""
            last_message = self.current_message[-1]["content"]
            
            
            # 调用Level2Chain处理
            result = self.level_2_chain.process(last_message)
            
            return {
                "difficulty": 2,
                "content": result,
                "complex_reason": data.get("complex_reason", "")
            }
        
        def response_level_3(data):
            """难度3处理"""
            logger.debug("调用Level3Chain处理")
            
            # 获取最后一条用户消息
            last_message = ""
            last_message = self.current_message[-1]["content"]
            
            
            # 调用Level3Chain处理
            result = self.level_3_chain.process(last_message)
            
            return {
                "difficulty": 3,
                "content": result,
                "complex_reason": data.get("complex_reason", "")
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
