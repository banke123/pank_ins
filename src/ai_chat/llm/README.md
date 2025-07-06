# LLM模块文档

LLM模块提供了大语言模型的调用接口和通用智能Agent功能，基于LangChain框架构建。

## 模块结构

```
llm/
├── __init__.py          # 模块入口
├── base_model.py        # 基础模型抽象类
├── llm.py              # 聊天模型实现
├── agent.py            # 通用Agent实现
├── tools.py            # 工具套件
├── errors.py           # 错误定义
└── tests/              # 测试文件
    ├── chat_llm_test.py         # 聊天模型测试
    ├── universal_agent_test.py  # 通用Agent测试
    ├── agent_test.py            # 数学Agent测试（向后兼容）
    └── simple_agent_test.py     # 简单Agent测试
```

## 功能特性

### 基础聊天模型 (ChatLLM)
- 支持基本的对话功能
- 可配置系统提示词
- 支持流式和非流式响应
- 历史对话管理
- 错误处理和重试机制

### 通用Agent (UniversalAgent)
- 基于LangChain的工具调用框架
- 支持自定义工具集配置
- 多种工具配置方式（工具集名称、工具名称列表、工具对象列表）
- 流式执行过程展示
- 完善的错误处理机制
- 工具信息查询功能
- **外部历史管理**: 接收完整消息列表，历史由外部数据库管理

### 工具套件 (tools.py)
- **数学工具集**: 加减乘除、幂运算、阶乘等
- **文本工具集**: 字符串处理、大小写转换等
- **工具管理**: 按名称或工具集获取工具
- **扩展性**: 易于添加自定义工具

### 数学Agent (MathAgent) - 向后兼容
- 专门用于数学计算的Agent
- 基于UniversalAgent实现
- 保持原有API兼容性

## 设计理念

### 历史管理分离
本模块采用**外部历史管理**的设计理念：
- Agent不内部维护对话历史
- 接收完整的消息列表（包含历史和当前查询）
- 历史信息由外部数据库系统管理
- 提高了系统的模块化和可扩展性

### 消息格式
所有消息都使用统一的格式：
```python
{
    "role": "user|assistant|system",
    "content": "消息内容"
}
```

## 使用指南

### 环境配置

在使用前需要设置环境变量：

```bash
# 必需
export QIANFAN_API_KEY="your_api_key"

# 可选，不设置将使用默认值
export QIANFAN_API_URL="your_api_url"
```

### 基础聊天模型使用

#### 初始化模型

```python
from ai_chat.llm.llm import ChatLLM

# 基本初始化
llm = ChatLLM(
    model_name="ernie-3.5-8k",
    temperature=0.5,
    max_tokens=1000
)

# 带系统提示词的初始化
llm = ChatLLM(
    model_name="ernie-3.5-8k",
    temperature=0.5,
    max_tokens=1000,
    system_prompt="你是一个有用的AI助手，请用中文回答问题。"
)
```

#### 单次对话

```python
# 准备消息
messages = [{"role": "user", "content": "你好，请介绍一下自己"}]

# 获取响应
response = llm.chat_get_response(messages)
print(response)
```

#### 流式对话

```python
# 流式获取响应
messages = [{"role": "user", "content": "请写一首关于春天的诗"}]

for chunk in llm.chat_get_response_stream(messages):
    print(chunk, end="", flush=True)
print()  # 换行
```

#### 多轮对话

```python
# 维护对话历史
conversation_history = []

while True:
    user_input = input("用户: ")
    if user_input.lower() in ['quit', 'exit']:
        break
    
    # 添加用户消息
    conversation_history.append({"role": "user", "content": user_input})
    
    # 获取响应
    response = llm.chat_get_response(conversation_history)
    print(f"助手: {response}")
    
    # 添加助手响应
    conversation_history.append({"role": "assistant", "content": response})
```

### 通用Agent使用

#### 基本初始化

```python
from ai_chat.llm.agent import UniversalAgent

# 使用工具集名称初始化
agent = UniversalAgent(
    model_name="ernie-3.5-8k",
    tools="math",  # 使用数学工具集
    temperature=0.1,
    system_prompt="你是一个数学计算助手"
)

# 使用工具名称列表初始化
agent = UniversalAgent(
    model_name="ernie-3.5-8k",
    tools=["add", "multiply", "string_length"],  # 自定义工具组合
    temperature=0.2,
    system_prompt="你是一个多功能助手"
)

# 使用所有工具
agent = UniversalAgent(
    model_name="ernie-3.5-8k",
    tools="all",  # 使用所有可用工具
    temperature=0.2,
    system_prompt="你是一个全能助手"
)
```

#### 执行任务

```python
# 单次查询（无历史）
messages = [{"role": "user", "content": "计算 15 + 27 * 3"}]
result = agent.execute(messages)
print(result)

# 带历史的查询
messages = [
    {"role": "user", "content": "我需要做一些计算"},
    {"role": "assistant", "content": "好的，我可以帮您进行计算"},
    {"role": "user", "content": "先算 10 + 20"},
    {"role": "assistant", "content": "10 + 20 = 30"},
    {"role": "user", "content": "然后把结果乘以 3"}  # 当前查询
]
result = agent.execute(messages)
print(result)
```

#### 流式执行

```python
# 流式查看执行过程
messages = [{"role": "user", "content": "计算 123 * 456 + 789"}]
print("执行过程: ", end="")

for chunk in agent.execute_stream(messages):
    print(chunk, end="", flush=True)
print()
```

#### 与外部数据库集成

```python
from ai_chat.memory import get_chat_memory_manager

# 假设已有记忆管理器
memory_manager = get_chat_memory_manager()
session_id = "user_session_123"

# 从数据库获取历史消息
history_messages = memory_manager.get_messages(session_id)

# 添加当前用户查询
current_query = "计算 50 * 2"
history_messages.append({"role": "user", "content": current_query})

# 执行Agent
result = agent.execute(history_messages)

# 保存结果到数据库
memory_manager.add_message(session_id, {"role": "user", "content": current_query})
memory_manager.add_message(session_id, {"role": "assistant", "content": result})
```

#### 工具信息查询

```python
# 查看可用工具
print("可用工具:", agent.get_available_tools())

# 查看工具描述
descriptions = agent.get_tool_descriptions()
for name, desc in descriptions.items():
    print(f"{name}: {desc}")
```

### 工具套件使用

#### 工具集管理

```python
from ai_chat.llm.tools import get_tool_set, get_tools_by_name, TOOL_SETS

# 查看所有可用工具集
print("可用工具集:", list(TOOL_SETS.keys()))

# 获取特定工具集
math_tools = get_tool_set("math")
print("数学工具:", [tool.name for tool in math_tools])

text_tools = get_tool_set("text")
print("文本工具:", [tool.name for tool in text_tools])

# 获取特定工具
specific_tools = get_tools_by_name(["add", "subtract", "string_length"])
print("特定工具:", [tool.name for tool in specific_tools])
```

#### 直接使用工具

```python
from ai_chat.llm.tools import add, multiply, string_length, uppercase

# 直接调用工具函数
result1 = add(10, 20)
result2 = multiply(5, 6)
result3 = string_length("Hello World")
result4 = uppercase("hello")

print(f"10 + 20 = {result1}")
print(f"5 * 6 = {result2}")
print(f"'Hello World' 长度 = {result3}")
print(f"'hello' 大写 = {result4}")
```

### 数学Agent使用（向后兼容）

```python
from ai_chat.llm.agent import MathAgent

# 初始化数学Agent
agent = MathAgent(
    model_name="ernie-3.5-8k",
    temperature=0.1,
    max_tokens=1000
)

# 使用原有API（内部会转换为消息列表格式）
result = agent.calculate("计算 15 + 27 * 3")
print(result)

# 带历史的计算
history = [
    {"role": "user", "content": "我要算数"},
    {"role": "assistant", "content": "好的"}
]
result = agent.calculate("100 除以 4", history)
print(result)

# 流式计算
for chunk in agent.calculate_stream("帮我算一下 100 除以 4 的结果"):
    print(chunk, end="", flush=True)
```

## 工具集详细说明

### 数学工具集 (math)

| 工具名 | 函数签名 | 说明 |
|--------|----------|------|
| add | `add(a: int, b: int) -> int` | 加法运算 |
| subtract | `subtract(a: int, b: int) -> int` | 减法运算 |
| multiply | `multiply(a: int, b: int) -> int` | 乘法运算 |
| divide | `divide(a: float, b: float) -> float` | 除法运算 |
| power | `power(base: int, exponent: int) -> int` | 幂运算 |
| factorial | `factorial(n: int) -> int` | 阶乘运算 |

### 文本工具集 (text)

| 工具名 | 函数签名 | 说明 |
|--------|----------|------|
| string_length | `string_length(text: str) -> int` | 计算字符串长度 |
| reverse_string | `reverse_string(text: str) -> str` | 反转字符串 |
| uppercase | `uppercase(text: str) -> str` | 转换为大写 |
| lowercase | `lowercase(text: str) -> str` | 转换为小写 |

### 工具配置方式

1. **工具集名称**
   ```python
   tools="math"        # 数学工具集
   tools="text"        # 文本工具集
   tools="all"         # 所有工具
   ```

2. **工具名称列表**
   ```python
   tools=["add", "subtract", "string_length"]  # 混合工具
   ```

3. **工具对象列表**
   ```python
   from ai_chat.llm.tools import add, subtract
   tools=[add, subtract]  # 直接传入工具对象
   ```

## 配置参数

### ChatLLM参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| model_name | str | 必需 | 模型名称，如"ernie-3.5-8k" |
| api_key | str | None | API密钥，可通过环境变量设置 |
| api_url | str | None | API地址，可通过环境变量设置 |
| temperature | float | 0.5 | 温度参数，控制输出随机性 |
| max_tokens | int | 1000 | 最大输出token数 |
| system_prompt | str | None | 系统提示词 |

### UniversalAgent参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| model_name | str | 必需 | 模型名称 |
| tools | Union[List, str] | 必需 | 工具配置，不能为None |
| api_key | str | None | API密钥 |
| api_url | str | None | API地址 |
| temperature | float | 0.1 | 温度参数 |
| max_tokens | int | 1000 | 最大输出token数 |
| system_prompt | str | None | 系统提示词 |

### MathAgent参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| model_name | str | 必需 | 模型名称 |
| api_key | str | None | API密钥 |
| api_url | str | None | API地址 |
| temperature | float | 0.1 | 温度参数，数学计算建议使用低值 |
| max_tokens | int | 1000 | 最大输出token数 |
| system_prompt | str | 默认数学助手提示词 | 系统提示词 |

## 错误处理

### 常见错误类型

1. **工具配置错误**
   ```python
   # 未提供工具
   ValueError: 必须提供工具列表。可以使用工具集: ['math', 'text', 'all']，或提供具体的工具列表
   
   # 无效工具名称
   ValueError: 工具 'invalid_tool' 不存在。可用工具: ['add', 'subtract', ...]
   
   # 无效工具集名称
   ValueError: 工具集 'invalid_set' 不存在。可用工具集: ['math', 'text', 'all']
   
   # 空消息列表
   ValueError: 消息列表不能为空
   ```

2. **API认证错误** - 检查API密钥是否正确
3. **网络连接错误** - 检查网络连接和API地址
4. **工具执行错误** - 检查工具参数是否合法

### 错误处理示例

```python
# 工具配置错误处理
try:
    agent = UniversalAgent("ernie-3.5-8k", tools=None)
except ValueError as e:
    print(f"配置错误: {e}")

# 空消息列表错误处理
try:
    agent = UniversalAgent("ernie-3.5-8k", tools="math")
    result = agent.execute([])  # 空消息列表
except ValueError as e:
    print(f"输入错误: {e}")

# 工具执行错误处理
try:
    messages = [{"role": "user", "content": "100 除以 0"}]  # 除零错误
    result = agent.execute(messages)
except Exception as e:
    print(f"执行错误: {e}")

# Agent内部会处理工具错误并返回友好的错误信息
messages = [{"role": "user", "content": "这不是一个有效的任务"}]
result = agent.execute(messages)
print(result)  # 会返回相应的错误说明
```

## 测试

### 运行测试

```bash
# 基础聊天模型测试
python src/ai_chat/tests/llm/chat_llm_test.py

# 通用Agent测试
python src/ai_chat/tests/llm/universal_agent_test.py

# 数学Agent测试（向后兼容）
python src/ai_chat/tests/llm/agent_test.py

# 简单Agent测试
python src/ai_chat/tests/llm/simple_agent_test.py
```

### 测试功能

1. **chat_llm_test.py**
   - 交互式聊天测试
   - 流式和非流式响应测试
   - 对话历史管理测试

2. **universal_agent_test.py**
   - 数学工具集测试
   - 文本工具集测试
   - 自定义工具组合测试
   - 所有工具测试
   - 带历史对话测试
   - 错误处理测试
   - 交互式测试

3. **agent_test.py**
   - 数学Agent向后兼容测试
   - 交互式数学计算测试
   - 流式执行测试

4. **simple_agent_test.py**
   - 快速功能验证
   - 基本计算测试
   - 向后兼容性测试
   - 带历史对话测试

## 扩展开发

### 添加新工具

```python
from langchain_core.tools import tool
from ai_chat.utils.logger import get_logger

logger = get_logger(__name__)

@tool
def square_root(n: float) -> float:
    """
    计算平方根
    
    Args:
        n: 非负数
        
    Returns:
        float: n的平方根
        
    Raises:
        ValueError: 当n为负数时抛出
    """
    if n < 0:
        raise ValueError("不能计算负数的平方根")
    
    import math
    result = math.sqrt(n)
    logger.debug(f"计算平方根: √{n} = {result}")
    return result

# 将新工具添加到工具集
from ai_chat.llm.tools import MATH_TOOLS
MATH_TOOLS.append(square_root)
```

### 创建自定义工具集

```python
from ai_chat.llm.tools import get_tools_by_name

# 创建科学计算工具集
SCIENCE_TOOLS = get_tools_by_name([
    "add", "subtract", "multiply", "divide", 
    "power", "factorial"
]) + [square_root]  # 添加自定义工具

# 使用自定义工具集
agent = UniversalAgent(
    model_name="ernie-3.5-8k",
    tools=SCIENCE_TOOLS,
    system_prompt="你是一个科学计算助手"
)
```

### 创建专用Agent

```python
class ScienceAgent(UniversalAgent):
    """科学计算Agent"""
    
    def __init__(self, model_name: str, **kwargs):
        # 设置默认工具和提示词
        if 'tools' not in kwargs:
            kwargs['tools'] = SCIENCE_TOOLS
        if 'system_prompt' not in kwargs:
            kwargs['system_prompt'] = """你是一个科学计算助手。你可以使用以下工具：
- 基础数学运算：加减乘除
- 高级数学运算：幂运算、阶乘、平方根
请根据用户需求选择合适的工具进行计算。"""
        
        super().__init__(model_name, **kwargs)
    
    def calculate(self, messages: List[Dict[str, Any]]) -> str:
        """科学计算方法"""
        return self.execute(messages)
```

## 最佳实践

1. **历史管理**
   - 使用外部数据库管理对话历史
   - 传递完整的消息列表给Agent
   - 合理控制历史长度以避免token超限

2. **工具选择**
   - 根据任务类型选择合适的工具集
   - 避免加载不必要的工具以提高性能
   - 使用自定义工具组合满足特定需求

3. **温度设置**
   - 数学计算：使用较低温度（0.1-0.3）
   - 文本处理：使用中等温度（0.3-0.5）
   - 创意任务：使用较高温度（0.5-0.8）

4. **系统提示词**
   - 明确定义Agent的角色和能力
   - 列出可用工具及其用途
   - 提供使用指导和约束条件

5. **错误处理**
   - 始终检查工具配置的有效性
   - 处理工具执行中的异常情况
   - 提供用户友好的错误信息

6. **性能优化**
   - 合理设置max_tokens避免不必要的开销
   - 使用流式输出提升用户体验
   - 适当管理对话历史长度

7. **消息格式**
   - 确保消息格式正确（role和content字段）
   - 最后一条消息通常是用户的当前查询
   - 历史消息按时间顺序排列

## 依赖项

- langchain >= 0.2.0
- langchain-openai
- langchain-core
- 其他依赖见requirements.txt

## 版本历史

- v1.0.0: 基础聊天模型实现
- v1.1.0: 添加数学Agent功能
- v1.2.0: 重构为通用Agent系统，添加工具套件
- v1.2.1: 优化错误处理和文档
- v1.3.0: 重构为外部历史管理模式，简化Agent接口 