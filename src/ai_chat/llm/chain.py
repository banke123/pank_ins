"""
链式文件，用于将多个LLM模型串联起来，形成一个完整的链式结构。
支持串行、并行、条件分支和回环处理。
"""

from pydantic import BaseModel, Field
from .llm import ChatLLM
from src.utils.logger_config import get_logger
import json
import asyncio
from typing import Any, Dict, List, Callable, Union, Optional, Tuple
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed

# 获取logger
logger = get_logger(__name__)

class LLMResponse(BaseModel):
    """结构化响应模型，用于判断用户问题的复杂度"""
    difficulty: int = Field(description="用户问题的复杂度，0-3")
    complex_reason: str = Field(description="用户问题的复杂度原因")
    content: str = Field(description="复杂度为0时，用户问题的内容，其他不需要回复")


class ChainNode(ABC):
    """链式节点基类"""
    
    def __init__(self, name: str = None):
        self.name = name or self.__class__.__name__
        
    @abstractmethod
    def execute(self, input_data: Any) -> Any:
        """执行节点处理逻辑"""
        pass
    
    def __call__(self, input_data: Any) -> Any:
        """使节点可调用"""
        return self.execute(input_data)


class FunctionNode(ChainNode):
    """函数节点，包装普通函数为链式节点"""
    
    def __init__(self, func: Callable, name: str = None):
        super().__init__(name or func.__name__)
        self.func = func
        
    def execute(self, input_data: Any) -> Any:
        """执行函数"""
        logger.debug(f"执行函数节点: {self.name}, 输入: {input_data}")
        result = self.func(input_data)
        logger.debug(f"函数节点 {self.name} 输出: {result}")
        return result


class SerialChain(ChainNode):
    """串行链：一个输入 -> 函数1 -> 函数2 -> ... -> 输出"""
    
    def __init__(self, nodes: List[ChainNode], name: str = None):
        super().__init__(name or "SerialChain")
        self.nodes = nodes
        
    def execute(self, input_data: Any) -> Any:
        """串行执行所有节点"""
        logger.debug(f"开始串行执行链: {self.name}, 输入: {input_data}")
        
        current_data = input_data
        for i, node in enumerate(self.nodes):
            logger.debug(f"串行链 {self.name} - 执行节点 {i+1}/{len(self.nodes)}: {node.name}")
            current_data = node.execute(current_data)
            
        logger.debug(f"串行链 {self.name} 执行完成, 最终输出: {current_data}")
        return current_data


class ParallelChain(ChainNode):
    """并行链：一个输入 -> 同时给多个函数 -> 收集所有输出"""
    
    def __init__(self, nodes: List[ChainNode], name: str = None):
        super().__init__(name or "ParallelChain")
        self.nodes = nodes
        
    def execute(self, input_data: Any) -> List[Any]:
        """并行执行所有节点"""
        logger.debug(f"开始并行执行链: {self.name}, 输入: {input_data}")
        
        results = []
        with ThreadPoolExecutor(max_workers=len(self.nodes)) as executor:
            # 提交所有任务
            future_to_node = {
                executor.submit(node.execute, input_data): node 
                for node in self.nodes
            }
            
            # 收集结果
            for future in as_completed(future_to_node):
                node = future_to_node[future]
                try:
                    result = future.result()
                    results.append(result)
                    logger.debug(f"并行链 {self.name} - 节点 {node.name} 完成: {result}")
                except Exception as e:
                    logger.error(f"并行链 {self.name} - 节点 {node.name} 执行失败: {e}")
                    results.append(None)
        
        logger.debug(f"并行链 {self.name} 执行完成, 输出: {results}")
        return results


class ConditionalChain(ChainNode):
    """条件链：根据条件函数的结果选择不同的执行路径"""
    
    def __init__(self, 
                 condition_func: Callable[[Any], str], 
                 branches: Dict[str, ChainNode], 
                 default_branch: ChainNode = None,
                 name: str = None):
        super().__init__(name or "ConditionalChain")
        self.condition_func = condition_func
        self.branches = branches
        self.default_branch = default_branch
        
    def execute(self, input_data: Any) -> Any:
        """根据条件执行相应分支"""
        logger.debug(f"开始条件执行链: {self.name}, 输入: {input_data}")
        
        # 执行条件判断
        condition_result = self.condition_func(input_data)
        logger.debug(f"条件链 {self.name} - 条件判断结果: {condition_result}")
        
        # 选择执行分支
        if condition_result in self.branches:
            selected_node = self.branches[condition_result]
            logger.debug(f"条件链 {self.name} - 选择分支: {condition_result} -> {selected_node.name}")
            result = selected_node.execute(input_data)
        elif self.default_branch:
            logger.debug(f"条件链 {self.name} - 使用默认分支: {self.default_branch.name}")
            result = self.default_branch.execute(input_data)
        else:
            logger.warning(f"条件链 {self.name} - 未找到匹配分支且无默认分支")
            result = input_data
            
        logger.debug(f"条件链 {self.name} 执行完成, 输出: {result}")
        return result


class LoopChain(ChainNode):
    """回环链：重复执行某个链式结构直到满足条件或达到最大次数"""
    
    def __init__(self, 
                 loop_node: ChainNode,
                 continue_condition: Callable[[Any, int], bool],
                 max_iterations: int = 10,
                 name: str = None):
        """
        初始化回环链
        
        Args:
            loop_node: 要重复执行的链式节点
            continue_condition: 继续条件函数，接收(当前结果, 当前迭代次数)，返回是否继续循环
            max_iterations: 最大迭代次数，防止无限循环
            name: 链的名称
        """
        super().__init__(name or "LoopChain")
        self.loop_node = loop_node
        self.continue_condition = continue_condition
        self.max_iterations = max_iterations
        
    def execute(self, input_data: Any) -> Tuple[Any, int]:
        """
        执行回环处理
        
        Returns:
            Tuple[Any, int]: (最终结果, 实际执行次数)
        """
        logger.debug(f"开始回环执行链: {self.name}, 输入: {input_data}, 最大迭代次数: {self.max_iterations}")
        
        current_data = input_data
        iteration = 0
        
        while iteration < self.max_iterations:
            iteration += 1
            logger.debug(f"回环链 {self.name} - 第 {iteration} 次迭代开始")
            
            # 执行循环体
            current_data = self.loop_node.execute(current_data)
            logger.debug(f"回环链 {self.name} - 第 {iteration} 次迭代结果: {current_data}")
            
            # 检查是否继续循环
            should_continue = self.continue_condition(current_data, iteration)
            logger.debug(f"回环链 {self.name} - 第 {iteration} 次迭代继续条件: {should_continue}")
            
            if not should_continue:
                logger.debug(f"回环链 {self.name} - 条件不满足，结束循环")
                break
                
        if iteration >= self.max_iterations:
            logger.warning(f"回环链 {self.name} - 达到最大迭代次数 {self.max_iterations}，强制结束")
        
        logger.debug(f"回环链 {self.name} 执行完成, 总迭代次数: {iteration}, 最终输出: {current_data}")
        return current_data, iteration


class MergeChain(ChainNode):
    """合并链：将多个输入合并后传给一个函数"""
    
    def __init__(self, merge_func: Callable[[List[Any]], Any], name: str = None):
        super().__init__(name or "MergeChain")
        self.merge_func = merge_func
        
    def execute(self, input_data: List[Any]) -> Any:
        """合并多个输入"""
        logger.debug(f"开始合并链: {self.name}, 输入: {input_data}")
        result = self.merge_func(input_data)
        logger.debug(f"合并链 {self.name} 输出: {result}")
        return result


class ChainBuilder:
    """链式构建器，用于方便地构建复杂的链式结构"""
    
    @staticmethod
    def serial(*nodes) -> SerialChain:
        """创建串行链"""
        return SerialChain(list(nodes))
    
    @staticmethod
    def parallel(*nodes) -> ParallelChain:
        """创建并行链"""
        return ParallelChain(list(nodes))
    
    @staticmethod
    def conditional(condition_func: Callable, branches: Dict[str, ChainNode], default=None) -> ConditionalChain:
        """创建条件链"""
        return ConditionalChain(condition_func, branches, default)
    
    @staticmethod
    def loop(loop_node: ChainNode, 
             continue_condition: Callable[[Any, int], bool], 
             max_iterations: int = 10, 
             name: str = None) -> LoopChain:
        """创建回环链"""
        return LoopChain(loop_node, continue_condition, max_iterations, name)
    
    @staticmethod
    def merge(merge_func: Callable) -> MergeChain:
        """创建合并链"""
        return MergeChain(merge_func)
    
    @staticmethod
    def function(func: Callable, name: str = None) -> FunctionNode:
        """创建函数节点"""
        return FunctionNode(func, name)


class test_chain:
    """示例：使用新的链式框架重构原有的test_chain"""
    
    def __init__(self):
        self.llm = ChatLLM(
            model_name="deepseek-v3",
            temperature=0.1,
            max_tokens=2000,
            system_prompt="""你是一个示波器操作员，首先你需要判断用户问题的复杂程度，目前有4种复杂度：

0: 最简单，不需要操作示波器，只需要回答用户问题，例如："我们之前通道1测量的数据是多少？"，类似这种，不需要操作示波器只需要查找数据回答用户，查找不到如实回答，不要乱编。

1: 简单，需要操作示波器，当指令是明确的，比如："设置通道1 通道打开，电压刻度为1V，时间刻度为1us，其他默认"。

2: 中等，需要操作示波器，但指令不是很明确，比如："帮我测量这个I2C 信号质量。"这种没有说明具体怎么测量，需要根据信号特征判断。

3: 复杂，不需要操作示波器，但需要你做出一些计划，比如："我需要测量test1 这个项目的白盒测试。这个项目有GSENSOR,SPI 3V 电压阈，也有ALS 的I2C 3V 电压阈。最后需要输出测试报告"，例如这种，需要对这个测试做一个测试计划。

请根据用户问题分析复杂度，并按照以下JSON格式输出：
{
    "difficulty": 复杂度数字(0-3),
    "complex_reason": "复杂度判断的原因说明",
    "content": "如果复杂度为0，则回答用户问题；其他复杂度则为空字符串"
}"""
        )
        
        # 使用新的链式框架构建处理链
        self.chain = self._build_chain()
    
    def _build_chain(self):
        """构建处理链"""
        # 定义处理函数
        def llm_process(user_question: str) -> str:
            """LLM处理函数"""
            return self.llm.chat_get_response([{"role": "user", "content": user_question}])
        
        def json_extract(llm_response: str) -> dict:
            """JSON提取函数"""
            try:
                # 查找JSON开始和结束位置
                json_start = llm_response.find('{')
                json_end = llm_response.rfind('}') + 1
                
                if json_start != -1 and json_end > json_start:
                    json_str = llm_response[json_start:json_end]
                    return json.loads(json_str)
                else:
                    # 如果没有找到JSON格式，尝试直接解析整个响应
                    return json.loads(llm_response)
                    
            except json.JSONDecodeError as e:
                logger.error(f"JSON解析失败: {e}, 原始响应: {llm_response}")
                return {
                    "difficulty": -1,
                    "complex_reason": f"JSON解析失败: {str(e)}",
                    "content": ""
                }
            except Exception as e:
                logger.error(f"响应处理失败: {e}")
                return {
                    "difficulty": -1,
                    "complex_reason": f"响应处理失败: {str(e)}",
                    "content": ""
                }
        
        # 构建串行链：用户输入 -> LLM处理 -> JSON提取 -> 输出
        return ChainBuilder.serial(
            ChainBuilder.function(llm_process, "LLM处理"),
            ChainBuilder.function(json_extract, "JSON提取")
        )
    
    def execute(self, user_question: str) -> dict:
        """执行链式处理"""
        try:
            logger.debug(f"开始执行test_chain, 输入: {user_question}")
            result = self.chain.execute(user_question)
            logger.debug(f"test_chain执行完成, 输出: {result}")
            return result
        except Exception as e:
            logger.error(f"test_chain执行失败: {e}")
            return {
                "difficulty": -1,
                "complex_reason": f"执行失败: {str(e)}",
                "content": ""
            }


# 导出类
__all__ = [
    "ChainNode",
    "FunctionNode", 
    "SerialChain",
    "ParallelChain",
    "ConditionalChain",
    "LoopChain",
    "MergeChain",
    "ChainBuilder",
    "test_chain",
    "LLMResponse"
]

