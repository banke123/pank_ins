"""
难度3处理链
用于处理项目级别的测试规划
将复杂项目分解为多个信号测试任务，并按优先级顺序执行
"""
import os
import sys
from typing import Dict, Any, List
from datetime import datetime

# 添加项目根目录到Python路径
current_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..', '..'))
sys.path.insert(0, project_root)

from src.ai_chat.llm.llm import ChatLLM
from src.ai_chat.llm.parser.json_parser import json_extract
from src.ai_chat.llm.chain import ChainBuilder
from src.utils.logger_config import get_logger
from src.ai_chat.tests.llm.level_2_chain import Level2Chain
from src.ai_chat.tests.llm.history_manager import HistoryManager

logger = get_logger(__name__)

class Level3Chain:
    """难度3处理链，用于处理项目级别的测试规划"""
    
    def __init__(self, stream_callback=None, flow_card_update=None):
        """初始化难度3处理链"""
        # 首先设置流程卡片回调函数和流式回调函数
        self.flow_card_update = flow_card_update
        self.stream_callback = stream_callback
        
        # 初始化项目规划LLM
        self.project_planner_llm = ChatLLM(
            model_name="deepseek-r1",
            temperature=0.1,
            system_prompt="""你是一个专业的示波器项目测试规划专家。你的核心任务是将复杂的项目测试需求分解为有序的信号测试任务序列。

## 核心工作流程
1. **项目分析**：理解项目整体测试需求和目标
2. **任务分解**：将项目分解为独立的信号测试任务
3. **优先级排序**：根据依赖关系和重要性确定测试顺序
4. **任务执行**: 按顺序将每个任务传递给Level2Chain处理
5. **结果汇总**：收集所有测试结果，生成项目测试报告

## 项目规划原则
- **依赖优先**：先测试基础信号（如时钟、电源），再测试依赖信号
- **风险优先**：优先测试关键信号和高风险接口
- **效率优先**：合理安排测试顺序，减少探头重新连接次数
- **完整性**：确保所有关键信号都被覆盖测试
- **输出格式**: 严格按照以下JSON模板输出, 确保语法正确
- **任务分解要合理**: 避免过度细分或粗糙

## 常见项目测试场景

### 嵌入式系统项目
典型测试序列：
1. 电源电压稳定性测试
2. 主时钟信号质量测试  
3. 复位信号时序测试
4. I2C总线通信测试
5. SPI接口数据传输测试
6. UART串口通信测试
7. PWM信号输出测试


## 任务类型说明
- **signal_test**：具体信号测试任务，传递给Level2Chain处理


## 输出格式模板
严格按照以下JSON模板输出，确保语法正确：

{
    "任务总数": 0,
    "计划名": "如：项目test1 测试计划，临时项目测试计划等",
    "Json A样式": {
        "任务具体内容": [
            {
                "任务名": "如：GsensorI2C测试或者通道1 clk测试之类的",
                "任务类型": "signal_test/protocol_test",
                "任务描述": "具体的测试任务描述，将传递给Level2Chain",
                "执行情况": "任务的执行状态和结果",
                "预估时间": "预计执行时间（分钟）"
            }
        ],
        "当前任务": 0,
        "计划时间": "总计划预计时间",
        "计划状态": "planning/running/completed/error",
        "计划结果": "整体计划的执行结果",
        "计划计数": 0
    }
}
"""
        )
        
        # 初始化Level2Chain用于执行具体信号测试，传递流式回调和流程卡片回调
        self.level_2_chain = Level2Chain(
            stream_callback=self.stream_callback, 
            flow_card_update=self.flow_card_update
        )
        
        # 初始化HistoryManager
        self.history_manager = HistoryManager()
        
        # 初始化容器ID
        self.container_id = "level_3_chain"
        
        # 创建历史容器
        self.history_manager.create_container(self.container_id)
        
        # 当前处理状态
        self.current_project = None
        self.max_tasks = 20  # 最大任务数限制
        self.max_plan_num = 3  # 最大重新规划次数
        self.last_plan_num = 0  # 上一次的计划数
        
        # 创建主处理链
        self.main_chain = self.create_main_chain()
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理项目级别的消息
        
        Args:
            data (Dict[str, Any]): 包含消息和计划ID的数据
                {
                    "message": str,  # 用户消息
                    "plan_id": str   # 计划ID
                }
            
        Returns:
            Dict[str, Any]: 处理结果
        """
        try:
            message = data["message"]
            self.current_plan_id = data["plan_id"]
            logger.debug(f"Level3Chain处理消息: {message}, 计划ID: {self.current_plan_id}")
            
            # 执行主链
            result = self.main_chain.execute(message)
            
            # 返回包含计划ID的结果字典
            return {
                "plan_id": self.current_plan_id,
                "content": result if isinstance(result, str) else str(result),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Level3Chain处理失败: {e}")
            # 错误情况也返回字典格式
            return {
                "plan_id": getattr(self, 'current_plan_id', 'unknown'),
                "content": f"项目规划失败: {str(e)}",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": "error"
            }
    
    def create_main_chain(self):
        """创建主处理链"""
        
        def project_planning(data):
            """项目规划"""
            print("\n正在进行项目规划...")
            response = ""

            # 添加用户消息到历史（只添加字符串）
            self.history_manager.add_message(self.container_id, "user", data)
            history_message = self.history_manager.get_history(self.container_id)
            
            # 如果有流式回调，通知UI开始流式响应
            if self.stream_callback:
                self.stream_callback("START_STREAM", "")
            
            for chunk in self.project_planner_llm.chat_get_response_stream(history_message):
                print(chunk, end="", flush=True)
                # 通知UI显示流式响应片段
                if self.stream_callback:
                    self.stream_callback("STREAM_CHUNK", chunk)
                response += chunk
            print("\n")
            
            # 通知UI流式响应结束
            if self.stream_callback:
                self.stream_callback("END_STREAM", response)
            
            logger.debug(f"项目规划响应: {response}")
            # 添加助手消息到历史
            self.history_manager.add_message(self.container_id, "assistant", response)
            return response
        
        def json_extract_step(data):
            """JSON解析步骤"""
            result = json_extract(data)
            if not result or "Json A样式" not in result:
                raise ValueError("无法解析项目规划结构")
            
            logger.debug(f"项目规划解析结果: {result}")
            
            # 更新max_tasks
            self.max_tasks = result.get("任务总数", 20)
            
            # 发送Level3流程卡片信息到UI
            if self.flow_card_update:
                json_a_data = result.get("Json A样式", {})
                card_data = {
                    "card_type": "level3",
                    "plan_id": getattr(self, 'current_plan_id', 'unknown'),
                    "project_name": result.get("计划名", "未知计划"),
                    "total_tasks": result.get("任务总数", 0),
                    "current_task": json_a_data.get("当前任务", 0),
                    "status": json_a_data.get("计划状态", "planning"),
                    "estimated_total_time": json_a_data.get("计划时间", "未知"),
                    "tasks": json_a_data.get("任务具体内容", []),
                    "result": json_a_data.get("计划结果", "")
                }
                self.flow_card_update("UPDATE_PLAN", card_data)
            
            return result
        
        def single_task_processor(data):
            """单任务处理器 - 处理当前任务"""
            # 确保data是字典类型
            if isinstance(data, tuple):
                logger.warning(f"single_task_processor收到tuple类型数据: {data}")
                data = data[0] if len(data) > 0 and isinstance(data[0], dict) else {}
            
            if not isinstance(data, dict):
                logger.error(f"single_task_processor收到非字典数据: {type(data)} - {data}")
                return {"计划状态": "error", "计划结果": "数据格式错误"}
            
            json_a_data = data.get("Json A样式", {})
            tasks = json_a_data.get("任务具体内容", [])
            current_index = json_a_data.get("当前任务", 0)
            
            if current_index >= len(tasks):
                return "所有任务已完成"
            
            current_task = tasks[current_index]
            task_type = current_task.get("任务类型", "signal_test")
            
            print(f"\n=== 执行任务 {current_index + 1}/{len(tasks)} ===")
            print(f"计划ID: {self.current_plan_id}")
            print(f"任务类型: {task_type}")
            print(f"任务描述: {current_task.get('任务描述', '')}")
            print(f"预估时间: {current_task.get('预估时间', '未知')}")
            print("=" * 50)
            
            if task_type == "signal_test":
                # 将任务传递给Level2Chain处理，使用同一个计划ID
                test_description = current_task.get("任务名", "") + " " + current_task.get("任务描述", "")
                result = self.level_2_chain.process({
                    "message": test_description,
                    "plan_id": self.current_plan_id  # 传递同一个计划ID
                })
                
                # 如果Level2返回字典格式，提取内容
                if isinstance(result, dict):
                    result_content = result.get("content", "")
                    return f"任务{current_index + 1}执行结果: {result_content}"
                else:
                    # 兼容旧格式
                    return f"任务{current_index + 1}执行结果: {result}"
            
        
        def task_continue_condition(data, iteration):
            """任务循环继续条件"""
            # 如果计划重新调整，停止当前循环
            if self.last_plan_num != data.get("Json A样式", {}).get("计划计数", 0):
                self.last_plan_num = data.get("Json A样式", {}).get("计划计数", 0)
                return False
            
            json_a_data = data.get("Json A样式", {})
            # 如果项目已完成，停止循环
            if json_a_data.get("计划状态", "running") == "completed":
                return False
            
            # 检查是否还有未完成的任务
            current_task = json_a_data.get("当前任务", 0)
            total_tasks = data.get("任务总数", 0)
            
            return current_task < total_tasks
        
        def plan_continue_condition(data, iteration):
            """计划循环继续条件"""
            # 检查data是否为tuple类型，如果是则提取其中的data参数
            if isinstance(data, tuple):
                data = data[0] if len(data) > 0 else {}
            
            json_a_data = data.get("Json A样式", {})
            if json_a_data.get("计划状态", "running") == "completed":
                return False
            else:
                return True
        
        def format_final_result(data):
            """格式化最终结果"""
            if isinstance(data, tuple):
                data1 = data[0][0] if len(data) > 0 else {}
            else:
                data1 = data
                
            json_a_data = data1.get("Json A样式", {})
            if json_a_data.get("计划状态", "running") == "completed":
                
                summary = f"""
=== 项目测试完成报告 ===
总任务数: {data1.get("任务总数", 0)}
计划时间: {json_a_data.get("计划时间", "未知")}

测试摘要:
{json_a_data.get("计划结果", "无摘要信息")}

详细结果请查看各任务执行日志。
"""
                return summary
            else:
                return "项目规划超过预期次数，请重新调整规划"
        
        # 项目规划链
        Project_Plan_Chain = ChainBuilder.serial(
            ChainBuilder.function(project_planning, "项目规划"),
            ChainBuilder.function(json_extract_step, "JSON解析"),
        )

        # 任务执行链
        Task_Chain = ChainBuilder.serial(
            ChainBuilder.function(single_task_processor, "任务执行"),
            ChainBuilder.function(project_planning, "规划调整"),
            ChainBuilder.function(json_extract_step, "JSON解析"),
        )

        # 任务循环链
        Task_loop_Chain = ChainBuilder.loop(
            loop_node=Task_Chain,
            continue_condition=task_continue_condition,
            max_iterations=self.max_tasks,
            name="任务循环处理"
        )

        # 项目循环链
        Project_loop_Chain = ChainBuilder.loop(
            loop_node=Task_loop_Chain,
            continue_condition=plan_continue_condition,
            max_iterations=self.max_plan_num,
            name="项目循环处理"
        )
        
        # 构建主链：项目规划 → 任务循环执行 → 格式化结果
        return ChainBuilder.serial(
            Project_Plan_Chain,
            Project_loop_Chain,
            ChainBuilder.function(format_final_result, "结果格式化")
        )
