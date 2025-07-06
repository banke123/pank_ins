# 链式处理框架使用说明

## 概述

这是一个自定义的链式处理框架，不依赖LangChain，支持串行、并行、条件分支和回环处理。可以将多个函数组合成复杂的处理流程。

## 核心组件

### 1. ChainNode (基类)
所有链式节点的抽象基类，定义了基本的执行接口。

### 2. FunctionNode (函数节点)
将普通函数包装为链式节点，使其可以参与链式处理。

### 3. SerialChain (串行链)
**功能**: 一个输入 → 函数1 → 函数2 → ... → 输出
**用途**: 数据处理流水线，每个步骤依次执行

### 4. ParallelChain (并行链)
**功能**: 一个输入 → 同时给多个函数 → 收集所有输出
**用途**: 需要同时进行多种处理的场景

### 5. ConditionalChain (条件链)
**功能**: 根据条件函数的结果选择不同的执行路径
**用途**: 需要根据输入特征选择不同处理逻辑的场景

### 6. LoopChain (回环链)
**功能**: 重复执行某个链式结构直到满足条件或达到最大次数
**用途**: 需要迭代优化、重试机制或收敛计算的场景

### 7. MergeChain (合并链)
**功能**: 将多个输入合并后传给一个函数
**用途**: 将并行处理的结果合并

### 8. ChainBuilder (构建器)
提供便捷的静态方法来创建各种链式结构。

## 使用方法

### 基本用法

```python
from ai_chat.llm.chain import ChainBuilder

# 定义处理函数
def add_10(x):
    return x + 10

def multiply_2(x):
    return x * 2

# 创建串行链
chain = ChainBuilder.serial(
    ChainBuilder.function(add_10, "加10"),
    ChainBuilder.function(multiply_2, "乘2")
)

# 执行
result = chain.execute(5)  # 输出: 30 ((5+10)*2)
```

### 串行链示例

```python
# 文本处理流水线
def preprocess_text(text):
    return text.strip().lower()

def extract_keywords(text):
    return text.split()

def count_words(words):
    return len(words)

# 构建串行链
text_pipeline = ChainBuilder.serial(
    ChainBuilder.function(preprocess_text, "预处理"),
    ChainBuilder.function(extract_keywords, "提取关键词"),
    ChainBuilder.function(count_words, "统计词数")
)

result = text_pipeline.execute("  Hello World  ")  # 输出: 2
```

### 并行链示例

```python
# 数据分析
def calculate_mean(data):
    return sum(data) / len(data)

def calculate_max(data):
    return max(data)

def calculate_min(data):
    return min(data)

# 构建并行链
analysis_chain = ChainBuilder.parallel(
    ChainBuilder.function(calculate_mean, "平均值"),
    ChainBuilder.function(calculate_max, "最大值"),
    ChainBuilder.function(calculate_min, "最小值")
)

results = analysis_chain.execute([1, 2, 3, 4, 5])  # 输出: [3.0, 5, 1]
```

### 条件链示例

```python
# 根据数据类型选择处理方式
def data_type_condition(data):
    if isinstance(data, str):
        return "text"
    elif isinstance(data, (int, float)):
        return "number"
    else:
        return "other"

def process_text(data):
    return f"文本处理: {data.upper()}"

def process_number(data):
    return f"数字处理: {data * 2}"

def process_other(data):
    return f"其他处理: {str(data)}"

# 构建条件链
conditional_chain = ChainBuilder.conditional(
    condition_func=data_type_condition,
    branches={
        "text": ChainBuilder.function(process_text, "文本处理"),
        "number": ChainBuilder.function(process_number, "数字处理"),
        "other": ChainBuilder.function(process_other, "其他处理")
    }
)

result1 = conditional_chain.execute("hello")  # 输出: "文本处理: HELLO"
result2 = conditional_chain.execute(42)       # 输出: "数字处理: 84"
```

### 回环链示例

```python
# 示例1：迭代优化（牛顿法求平方根）
def newton_iteration(data):
    """牛顿迭代法一次迭代"""
    target, current_guess = data["target"], data["guess"]
    new_guess = 0.5 * (current_guess + target / current_guess)
    return {"target": target, "guess": new_guess}

def convergence_condition(data, iteration):
    """收敛条件：误差小于0.001"""
    target, guess = data["target"], data["guess"]
    error = abs(guess * guess - target)
    return error >= 0.001  # 返回是否继续循环

# 构建回环链
newton_chain = ChainBuilder.loop(
    loop_node=ChainBuilder.function(newton_iteration, "牛顿迭代"),
    continue_condition=convergence_condition,
    max_iterations=10,  # 最大迭代次数
    name="牛顿法求平方根"
)

# 执行：求9的平方根
input_data = {"target": 9, "guess": 5.0}
result, iterations = newton_chain.execute(input_data)
print(f"平方根≈{result['guess']:.6f}, 迭代次数: {iterations}")

# 示例2：重试机制
def attempt_task(data):
    """模拟任务尝试"""
    import random
    attempt_count = data.get("attempts", 0) + 1
    success = random.random() < 0.3  # 30%成功率
    return {
        "attempts": attempt_count,
        "success": success,
        "result": f"结果-{attempt_count}" if success else None
    }

def retry_condition(data, iteration):
    """重试条件：未成功则继续"""
    return not data.get("success", False)

# 构建重试链
retry_chain = ChainBuilder.loop(
    loop_node=ChainBuilder.function(attempt_task, "任务尝试"),
    continue_condition=retry_condition,
    max_iterations=5,
    name="任务重试"
)

result, iterations = retry_chain.execute({"task": "重要任务"})
if result.get("success"):
    print(f"任务成功！结果: {result['result']}, 尝试次数: {iterations}")
else:
    print(f"任务失败，已达到最大重试次数: {iterations}")
```

### 复杂链组合示例

```python
# 组合多种链式结构
def preprocess(data):
    return {"value": data, "processed": True}

def analyze_basic(data):
    return {"type": "basic", "result": data["value"] * 2}

def analyze_advanced(data):
    return {"type": "advanced", "result": data["value"] ** 2}

def merge_results(results):
    basic = next(r for r in results if r["type"] == "basic")
    advanced = next(r for r in results if r["type"] == "advanced")
    return {
        "basic_value": basic["result"],
        "advanced_value": advanced["result"],
        "total": basic["result"] + advanced["result"]
    }

# 构建复杂链
complex_chain = ChainBuilder.serial(
    ChainBuilder.function(preprocess, "预处理"),
    ChainBuilder.parallel(
        ChainBuilder.function(analyze_basic, "基础分析"),
        ChainBuilder.function(analyze_advanced, "高级分析")
    ),
    ChainBuilder.function(merge_results, "结果合并")
)

result = complex_chain.execute(5)
# 输出: {"basic_value": 10, "advanced_value": 25, "total": 35}
```

## 回环链详细说明

### 回环链特性
- **自动控制**: 根据条件函数自动决定是否继续循环
- **最大限制**: 设置最大迭代次数防止无限循环
- **返回信息**: 返回最终结果和实际执行次数
- **详细日志**: 记录每次迭代的详细信息

### 回环链应用场景
1. **数值计算**: 迭代求解、收敛计算
2. **优化算法**: 梯度下降、参数调优
3. **重试机制**: API调用重试、错误恢复
4. **质量改进**: 文本优化、结果精化
5. **数据处理**: 清洗直到满足质量要求

### 回环链最佳实践
1. **合理设置最大迭代次数**: 避免无限循环
2. **清晰的继续条件**: 确保循环能够正确退出
3. **监控迭代过程**: 使用日志跟踪执行状态
4. **处理边界情况**: 考虑特殊输入的处理

## LLM处理示例

原有的`test_chain`类已经重构为使用新的链式框架：

```python
from ai_chat.llm.chain import test_chain

# 创建实例
chain = test_chain()

# 执行处理
result = chain.execute("帮我测量这个I2C信号质量")
print(result)  # 输出字典格式的结果
```

## 日志和调试

框架内置了详细的日志记录，可以跟踪每个节点的执行过程：

```python
from ai_chat.utils.logger import setup_logging

# 启用调试日志
setup_logging(log_name="chain_debug", level=10)  # DEBUG级别
```

## 错误处理

- 每个节点的执行都有异常捕获
- 并行链中单个节点失败不会影响其他节点
- 回环链会在达到最大迭代次数时自动停止
- 详细的错误日志记录

## 性能特性

- **并行执行**: 使用ThreadPoolExecutor实现真正的并行处理
- **内存效率**: 流式处理，不会积累大量中间结果
- **回环控制**: 智能的循环控制机制
- **可扩展**: 易于添加新的链式节点类型

## 最佳实践

1. **函数设计**: 保持函数功能单一，便于组合
2. **错误处理**: 在关键函数中添加适当的异常处理
3. **日志记录**: 在复杂链中添加适当的日志输出
4. **性能考虑**: 对于CPU密集型任务，考虑使用并行链
5. **回环安全**: 设置合理的最大迭代次数和退出条件
6. **测试**: 为每个函数和链式结构编写单元测试

## 扩展开发

要添加新的链式节点类型，继承`ChainNode`基类：

```python
class CustomChain(ChainNode):
    def __init__(self, custom_param, name=None):
        super().__init__(name or "CustomChain")
        self.custom_param = custom_param
    
    def execute(self, input_data):
        # 实现自定义逻辑
        return processed_data
```

然后在`ChainBuilder`中添加对应的静态方法：

```python
@staticmethod
def custom(custom_param):
    return CustomChain(custom_param)
``` 