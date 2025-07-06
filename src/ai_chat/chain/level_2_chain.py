"""
难度2处理链
用于处理需要解析的示波器操作指令
包含循环处理机制，将模糊指令解析为具体步骤
"""
from typing import Dict, Any, List
from ai_chat.llm.llm import ChatLLM
from ai_chat.llm.parser.json_parser import json_extract
from ai_chat.llm.chain import ChainBuilder
from ai_chat.utils.logger import get_logger
from ai_chat.tests.llm.level_1_chain import Level1Chain
from ai_chat.tests.llm.history_manager import HistoryManager

logger = get_logger(__name__)

class Level2Chain:
    """难度2处理链，用于处理需要解析的示波器操作"""
    
    def __init__(self):
        """初始化难度2处理链"""
        # 初始化指令解析LLM
        self.instruction_parser_llm = ChatLLM(
            model_name="deepseek-r1",
            temperature=0,
            system_prompt="""你是一个专业的示波器测试指令解析专家。你的核心任务是将用户的模糊测试需求转换为具体、可执行的示波器操作指令序列。

## 核心工作流程
1. **初始规划**：分析用户需求，制定测试步骤（plan_num=0）,必须包含用户的所有测试内容
2. **步骤执行**：按顺序执行每个步骤，current_step递增
3. **结果验证**：检查执行结果是否符合预期
4. **完成判断**：所有步骤执行完毕时设置status=completed
5. **异常处理**：如有问题则重新调整计划（plan_num+1）
6. **输出内容**：严格按照json的格式输出，不要在json外部增加其他的东西，json的字段也不要改动

## 重要原则
- 步骤内容一旦确定不要随意改动，除非需要重新规划
- steps数组与total_steps必须保持一致
- 每个instruction应该明确、具体、可直接执行
- 步骤规划内容应包含，接线（如果用户已提供具体接线则按照客户的接线即可),示波器设置，测量。
- 步骤数量控制在3-6个，避免过度细分

## 常见信号类型测试配置
注意不一定以下的配置都需要
### **通道分配**：如果用户有指定则按照客户指定，例如：通道1(SDA数据线)，通道2(SCL时钟线)
### **探头设置**：如衰减、耦合、带宽、标签等，如果用户有指定则按照客户指定，例如：一般10X探头
### **横坐标设置**：时基设置，如果用户有指定则按照客户指定，例如：100us/div
### **纵坐标设置**：电压幅度设置，垂直偏移设置，如果用户有指定则按照客户指定，例如：1V/div
### **触发设置**：触发源、触发方式、触发阈值、触发延迟等，如果用户有指定则按照客户指定，例如：边沿触发，上升沿，触发阈值为1.5V，触发延迟为100us
### **测量设置**：测量类型、测量参数、测量单位等，如果用户有指定则按照客户指定，例如：频率、周期、上升时间、下降时间、幅值、幅值差、相位差等
### **保存设置**：保存设置，如果用户有指定则按照客户指定，例如：保存为csv文件，保存为txt文件，保存为excel文件，保存为图片文件,用户没有要求则不保存


## 指令类型说明
- **instruction**：示波器操作指令，如"设置通道1电压刻度为1V/div，开启通道1"
- **HCI**：人机交互步骤，如探头连接、信号源配置等物理操作

## 输出格式要求
严格按照以下JSON模板输出，不得遗漏任何字段，也不要增加其他内容扩展：

```json
{
    "plan_num": 0,
    "signal_type": "信号类型(I2C/SPI/UART/PWM等)",
    "steps": [
        {
            "type": "instruction",
            "content": "具体的示波器操作指令，要明确具体"
            "result": "如果没有执行则待执行，如果执行了为具体的执行结果"
        },
        {
            "type": "HCI", 
            "content": "人机交互操作说明"
            "result": "如果没有执行则待执行，如果执行了为具体的执行结果"
        }
    ],
    "current_step": 0,
    "total_steps": 步骤总数,
    "status": "running/completed",
    "results": "最终结果"
}
```
"""
        )
        
        # 初始化Level1Chain用于执行具体操作
        self.level_1_chain = Level1Chain()
        
        # 初始化HistoryManager
        self.history_manager = HistoryManager()
        
        # 初始化容器ID
        self.container_id = "level_2_chain"
        
        # 创建历史容器
        self.history_manager.create_container(self.container_id)
        
        # 当前处理状态
        self.current_task = None
        self.max_steps = 10  # 最大步骤数限制，默认值
        self.max_plan_num = 5  # 最大计划数限制
        self.last_plan_num = 0 # 上一次的计划数
        
        # 创建主处理链
        self.main_chain = self.create_main_chain()
    
    def process(self, message: str) -> str:
        """
        处理难度2的消息
        
        Args:
            message: 用户消息
            
        Returns:
            str: 处理结果
        """
        try:
            logger.debug(f"Level2Chain处理消息: {message}")
            
            # 执行主链
            result = self.main_chain.execute(message)
            
            # 如果result是字符串，直接返回
            if isinstance(result, str):
                return result
            # # 如果result是字典，获取content字段
            # elif isinstance(result, dict):
            #     return result.get("content", "处理失败")
            # 其他情况转换为字符串
            else:
                return str(result)
            
        except Exception as e:
            logger.error(f"Level2Chain处理失败: {e}")
            return f"指令解析失败: {str(e)}"
    
    def create_main_chain(self):
        """创建主处理链"""
        
        def plan_reason(data):
            """计划调整"""
            print("\n正在规划测试指令...")
            response = ""

            # 添加用户消息到历史（只添加字符串）
            self.history_manager.add_message(self.container_id, "user", data)
            history_message = self.history_manager.get_history(self.container_id)
            for chunk in self.instruction_parser_llm.chat_get_response_stream(history_message):
                print(chunk, end="", flush=True)
                response += chunk
            print("\n")
            
            logger.debug(f"指令解析响应: {response}")
            # 添加助手消息到历史
            self.history_manager.add_message(self.container_id, "assistant", response)
            return response
        
        def json_extract_step(data):
            """JSON解析步骤"""
            result = json_extract(data)
            if not result or "steps" not in result:
                raise ValueError("无法解析指令结构")
            
            logger.debug(f"解析结果: {result}")
            
            # 更新max_steps
            self.max_steps = result.get("total_steps", 10)
            
            return result
        
        def single_step_processor(data):
            """单步处理器 - 处理当前步骤"""
            # 确保data是字典类型
            if isinstance(data, tuple):
                logger.warning(f"single_step_processor收到tuple类型数据: {data}")
                data = data[0] if len(data) > 0 and isinstance(data[0], dict) else {}
            
            if not isinstance(data, dict):
                logger.error(f"single_step_processor收到非字典数据: {type(data)} - {data}")
                return {"status": "error", "results": "数据格式错误"}
            
            steps = data.get("steps", [])
            current_index = data.get("current_step", 0)
            
            current_step = steps[current_index]
            
            if current_step.get("type", "unknown") == "instruction":
                result = self.level_1_chain.process(current_step.get("content", ""))
                return f"步骤{current_index}执行结果: {result}"
            else:
                print(f"步骤 {current_index + 1}/{len(steps)} [人机交互]: {current_step.get('content', '')}")
                print("请按照提示完成操作，然后继续...")
                result = "y"
                # result = input("请输入操作结果:")
                if result == "y":
                    result = "操作完成"
                else:
                    result = "操作失败"
                print(f"操作结果: {result}")
                
                return f"步骤{current_index}执行结果: {result}"
            
        
        def step_continue_condition(data, iteration):
            """循环继续条件"""

            # 如果已完成或出错，停止循环
            if self.last_plan_num != data.get("plan_num", 0):
                self.last_plan_num = data.get("plan_num", 0)
                return False
            
            if data.get("status", "running") == "completed" :
                return False
            
            else:
                return True
            
        def plan_continue_condition(data, iteration):
            """计划继续条件"""
            # 检查data是否为tuple类型，如果是则提取其中的data参数
            if isinstance(data, tuple):
                data = data[0] if len(data) > 0 else {}
            
            if data.get("status", "running") == "completed":
                return False
            else:
                return True
        
        def format_final_result(data):
            """格式化最终结果"""
            if isinstance(data, tuple):
                data1 = data[0][0] if len(data) > 0 else {}
            if data1.get("status", "running") == "completed" :
                return data1.get("results", [])
            else:
                return "计划超过预期次数，请重新调整计划"
        
        Plan_Chain = ChainBuilder.serial(
                    ChainBuilder.function(plan_reason, "计划"),
                    ChainBuilder.function(json_extract_step, "JSON解析"),
        )

        Step_Chain = ChainBuilder.serial(
            ChainBuilder.function(single_step_processor, "单步处理"),
            ChainBuilder.function(plan_reason, "计划调整"),
            ChainBuilder.function(json_extract_step, "JSON解析"),
        )

        Step_loop_Chain = ChainBuilder.loop(
            loop_node=Step_Chain,
            continue_condition=step_continue_condition,
            max_iterations=self.max_steps,
            name="步骤循环处理"
        )

        Plan_loop_Chain = ChainBuilder.loop(
            loop_node=Step_loop_Chain,
            continue_condition=plan_continue_condition,
            max_iterations=self.max_plan_num,
            name="计划循环处理"
        )
        
        # 构建主链：解析 → 循环处理 → 格式化结果
        return ChainBuilder.serial(
            Plan_Chain,
            Plan_loop_Chain,
            ChainBuilder.function(format_final_result, "结果格式化")
        )
