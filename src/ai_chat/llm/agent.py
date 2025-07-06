"""
通用Agent模块
基于ChatLLM大模型，支持自定义工具调用功能
"""

import os
import sys
from typing import List, Dict, Any, Optional, Union
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate

# 添加项目根目录到Python路径
current_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
sys.path.insert(0, project_root)

from .llm import ChatLLM
from .tools import get_tools_by_name, get_tool_set, TOOL_SETS
from src.utils.logger_config import get_logger

logger = get_logger(__name__)

class UniversalAgent:
    """
    通用Agent
    基于ChatLLM大模型，支持自定义工具调用
    """
    
    def __init__(self, model_name: str, tools: Union[List, str, None] = None, 
                 api_key: Optional[str] = None, api_url: Optional[str] = None, 
                 temperature: float = 0.1, max_tokens: int = 1000, 
                 system_prompt: Optional[str] = None):
        """
        初始化通用Agent
        
        Args:
            model_name: 模型名称
            tools: 工具列表，可以是：
                  - 工具对象列表
                  - 工具名称列表 
                  - 工具集名称字符串 ("math", "oscilloscope", "text", "all")
                  - None (将抛出错误)
            api_key: API密钥
            api_url: API URL
            temperature: 温度参数
            max_tokens: 最大token数
            system_prompt: 系统提示词
            
        Raises:
            ValueError: 当未提供工具列表时抛出
        """
        if tools is None:
            available_sets = list(TOOL_SETS.keys())
            raise ValueError(f"必须提供工具列表。可以使用工具集: {available_sets}，或提供具体的工具列表")
        
        # 处理工具参数
        self.tools = self._process_tools(tools)
        
        if not self.tools:
            raise ValueError("工具列表不能为空")
        
        # 初始化ChatLLM
        self.llm = ChatLLM(
            model_name=model_name,
            api_key=api_key,
            api_url=api_url,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system_prompt
        )
        
        # 创建简单的提示模板
        self.prompt = ChatPromptTemplate.from_messages([
            ("placeholder", "{chat_messages}"),
            ("placeholder", "{agent_scratchpad}"),
        ])
        
        # 创建Agent
        self.agent = create_tool_calling_agent(self.llm.llm, self.tools, self.prompt)
        
        # 创建AgentExecutor
        self.agent_executor = AgentExecutor(
            agent=self.agent, 
            tools=self.tools, 
            verbose=False,
            handle_parsing_errors=True
        )
        
        tool_names = [tool.name for tool in self.tools]
        logger.debug(f"初始化通用Agent完成，模型: {model_name}，工具: {tool_names}")
    
    def _process_tools(self, tools: Union[List, str]) -> List:
        """
        处理工具参数，统一转换为工具对象列表
        
        Args:
            tools: 工具参数
            
        Returns:
            List: 工具对象列表
        """
        if isinstance(tools, str):
            # 字符串类型，当作工具集名称处理
            return get_tool_set(tools)
        elif isinstance(tools, list):
            if not tools:
                return []
            
            # 检查列表第一个元素的类型
            first_item = tools[0]
            if isinstance(first_item, str):
                # 字符串列表，当作工具名称列表处理
                return get_tools_by_name(tools)
            else:
                # 假设是工具对象列表，直接返回
                return tools
        else:
            raise ValueError(f"不支持的工具类型: {type(tools)}")
    
    def execute(self, messages: List[Dict[str, Any]]) -> str:
        """
        执行Agent任务
        
        Args:
            messages: 完整的消息列表，包含历史对话和当前查询
                     格式: [{"role": "user/assistant/system", "content": "..."}]
                     最后一条消息应该是用户的当前查询
            
        Returns:
            str: 执行结果
        """
        try:
            
            logger.debug(f"执行Agent任务: {messages}")
            input_data = {"chat_messages": messages}
            # 执行Agent
            response = self.agent_executor.invoke(input_data)
            
            result = response.get("output", "执行失败")
            logger.debug(f"执行结果: {result}")
            
            return result
            
        except Exception as e:
            logger.error(f"执行过程中发生错误: {e}")
            return f"执行过程中发生错误: {str(e)}"
    
    def execute_stream(self, messages: List[Dict[str, Any]]):
        """
        流式执行Agent任务
        
        Args:
            messages: 完整的消息列表，包含历史对话和当前查询
                     格式: [{"role": "user/assistant/system", "content": "..."}]
                     最后一条消息应该是用户的当前查询
            
        Yields:
            str: 执行过程的流式输出
        """
        try:
            if not messages:
                raise ValueError("消息列表不能为空")
            
            chat_messages = messages
            logger.debug(f"流式执行Agent任务: {chat_messages}")
            
            # 流式执行Agent
            for chunk in self.agent_executor.stream(chat_messages):
                if chunk:
                    # 提取有用的信息
                    if "agent" in chunk:
                        messages_chunk = chunk["agent"].get("messages", [])
                        for message in messages_chunk:
                            logger.debug(f"流式执行Agent任务: {message}")
                            if hasattr(message, 'content') and message.content:
                                yield message.content
                    elif "tools" in chunk:
                        # 工具执行结果
                        yield "\n[工具执行完成]\n"
                    else:
                        yield str(chunk)
                        
        except Exception as e:
            logger.error(f"流式执行过程中发生错误: {e}")
            yield f"执行过程中发生错误: {str(e)}"
    
    def get_available_tools(self) -> List[str]:
        """
        获取当前可用的工具列表
        
        Returns:
            List[str]: 工具名称列表
        """
        return [tool.name for tool in self.tools]
    
    def get_tool_descriptions(self) -> Dict[str, str]:
        """
        获取工具描述信息
        
        Returns:
            Dict[str, str]: 工具名称到描述的映射
        """
        descriptions = {}
        for tool in self.tools:
            descriptions[tool.name] = tool.description
        return descriptions

# 为了向后兼容，保留MathAgent作为UniversalAgent的别名
class MathAgent(UniversalAgent):
    """
    数学Agent（向后兼容）
    实际上是使用数学工具集的UniversalAgent
    """
    
    def __init__(self, model_name: str, api_key: Optional[str] = None, api_url: Optional[str] = None, 
                 temperature: float = 0.1, max_tokens: int = 1000, system_prompt: Optional[str] = None):
        """
        初始化数学Agent
        
        Args:
            model_name: 模型名称
            api_key: API密钥
            api_url: API URL
            temperature: 温度参数
            max_tokens: 最大token数
            system_prompt: 系统提示词
        """
        # 设置默认系统提示词
        if system_prompt is None:
            system_prompt = """你是一个数学计算助手。你可以使用以下工具来帮助用户进行数学计算：
- add: 加法运算
- subtract: 减法运算  
- multiply: 乘法运算
- divide: 除法运算
- power: 幂运算
- factorial: 阶乘运算

请根据用户的问题选择合适的工具进行计算，并给出清晰的解答。"""
        
        # 使用数学工具集初始化
        super().__init__(
            model_name=model_name,
            tools="math",
            api_key=api_key,
            api_url=api_url,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system_prompt
        )
    
    def calculate(self, messages: List[Dict[str, Any]] = None) -> str:
        """
        执行数学计算（向后兼容方法）
        
        Args:
            messages: 消息列表，包含历史对话和当前查询
            
        Returns:
            str: 计算结果
        """
        chat_messages = messages
        if chat_messages is None:
            raise ValueError("chat_messages不能为空")
        return self.execute(chat_messages)
    
    def calculate_stream(self, messages: List[Dict[str, Any]] = None):
        """
        流式执行数学计算（向后兼容方法）
        
        Args:
            messages: 消息列表，包含历史对话和当前查询
            
        Yields:
            str: 计算过程的流式输出
        """
        chat_messages = messages
        if chat_messages is None:
            raise ValueError("chat_messages不能为空")
        
        yield from self.execute_stream(chat_messages)

# 示波器仪器控制Agent
class OscilloscopeAgent(UniversalAgent):
    """
    示波器仪器控制Agent
    专门用于示波器仪器控制的Agent
    """
    
    def __init__(self, model_name: str, api_key: Optional[str] = None, api_url: Optional[str] = None, 
                 temperature: float = 0.1, max_tokens: int = 1000, system_prompt: Optional[str] = None):
        """
        初始化示波器Agent
        
        Args:
            model_name: 模型名称
            api_key: API密钥
            api_url: API URL
            temperature: 温度参数
            max_tokens: 最大token数
            system_prompt: 系统提示词
        """
        # 设置默认系统提示词
        if system_prompt is None:
            system_prompt = """你是一个示波器仪器控制助手。你可以使用以下工具来帮助用户控制示波器：

通道设置工具：
- set_channel: 设置示波器通道参数（启用/禁用、电压刻度、耦合方式、探头衰减比）
- set_voltage_scale: 设置指定通道的电压刻度

时间和触发设置：
- set_time_scale: 设置时间刻度
- set_trigger: 设置触发参数（触发源、电平、边沿、模式）

测量和捕获工具：
- capture_waveform: 捕获指定通道的波形数据
- measure_frequency: 测量指定通道的频率
- measure_amplitude: 测量指定通道的幅度

其他功能：
- save_screenshot: 保存示波器屏幕截图
- reset_oscilloscope: 重置示波器到默认设置

请根据用户的需求选择合适的工具进行示波器操作，并提供清晰的操作指导。"""
        
        # 使用示波器工具集初始化
        super().__init__(
            model_name=model_name,
            tools="oscilloscope",
            api_key=api_key,
            api_url=api_url,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system_prompt
        )
    
    def control(self, messages: List[Dict[str, Any]] = None) -> str:
        """
        执行示波器控制（专用方法）
        
        Args:
            messages: 消息列表，包含历史对话和当前查询
            
        Returns:
            str: 控制结果
        """
        chat_messages = messages
        if chat_messages is None:
            raise ValueError("chat_messages不能为空")
        return self.execute(chat_messages)
    
    def control_stream(self, messages: List[Dict[str, Any]] = None):
        """
        流式执行示波器控制（专用方法）
        
        Args:
            messages: 消息列表，包含历史对话和当前查询
            
        Yields:
            str: 控制过程的流式输出
        """
        chat_messages = messages
        if chat_messages is None:
            raise ValueError("chat_messages不能为空")
        
        yield from self.execute_stream(chat_messages) 