"""
数学计算工具
为Agent提供基础数学运算功能
"""

import os
import sys
import math
from langchain_core.tools import tool

# 添加项目根目录到Python路径
current_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..', '..'))
sys.path.insert(0, project_root)

from src.utils.logger_config import get_logger

logger = get_logger(__name__)

# 数学计算工具套件
@tool
def add(a: int, b: int) -> int:
    """
    加法运算
    
    Args:
        a: 第一个数字
        b: 第二个数字
        
    Returns:
        int: 两数之和
    """
    result = a + b
    logger.debug(f"执行加法: {a} + {b} = {result}")
    return result

@tool
def subtract(a: int, b: int) -> int:
    """
    减法运算
    
    Args:
        a: 被减数
        b: 减数
        
    Returns:
        int: 两数之差
    """
    result = a - b
    logger.debug(f"执行减法: {a} - {b} = {result}")
    return result

@tool
def multiply(a: int, b: int) -> int:
    """
    乘法运算
    
    Args:
        a: 第一个数字
        b: 第二个数字
        
    Returns:
        int: 两数之积
    """
    result = a * b
    logger.debug(f"执行乘法: {a} * {b} = {result}")
    return result

@tool
def divide(a: float, b: float) -> float:
    """
    除法运算
    
    Args:
        a: 被除数
        b: 除数
        
    Returns:
        float: 两数之商
        
    Raises:
        ValueError: 当除数为0时抛出
    """
    if b == 0:
        raise ValueError("除数不能为0")
    result = a / b
    logger.debug(f"执行除法: {a} / {b} = {result}")
    return result

@tool
def power(base: int, exponent: int) -> int:
    """
    幂运算
    
    Args:
        base: 底数
        exponent: 指数
        
    Returns:
        int: 幂运算结果
    """
    result = base ** exponent
    logger.debug(f"执行幂运算: {base} ^ {exponent} = {result}")
    return result

@tool
def factorial(n: int) -> int:
    """
    计算阶乘
    
    Args:
        n: 非负整数
        
    Returns:
        int: n的阶乘
        
    Raises:
        ValueError: 当n为负数时抛出
    """
    if n < 0:
        raise ValueError("阶乘只能计算非负整数")
    if n == 0 or n == 1:
        return 1
    result = 1
    for i in range(2, n + 1):
        result *= i
    logger.debug(f"执行阶乘: {n}! = {result}")
    return result

# 数学工具集合
MATH_TOOLS = [add, subtract, multiply, divide, power, factorial] 