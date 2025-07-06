#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
日志配置模块

配置系统日志格式和输出，支持多级别日志分离和灵活配置。
支持原始数字级别和字符串级别。

@author: PankIns Team
@version: 2.1.0
"""

import os
import logging
import sys
from logging.handlers import RotatingFileHandler
from typing import Optional, Union


# 日志级别映射表
LOG_LEVEL_MAP = {
    # 字符串级别
    'CRITICAL': 50,
    'ERROR': 40,
    'WARNING': 30,
    'INFO': 20,
    'DEBUG': 10,
    'NOTSET': 0,
    
    # 数字级别
    50: 'CRITICAL',
    40: 'ERROR', 
    30: 'WARNING',
    20: 'INFO',
    10: 'DEBUG',
    0: 'NOTSET',
}


def normalize_log_level(level: Union[str, int]) -> int:
    """
    标准化日志级别，支持字符串和数字格式
    
    Args:
        level: 日志级别，可以是字符串（如'DEBUG'）或数字（如10）
        
    Returns:
        int: 标准化后的数字级别
        
    Examples:
        normalize_log_level('DEBUG') -> 10
        normalize_log_level(10) -> 10
        normalize_log_level('info') -> 20
    """
    if isinstance(level, int):
        # 验证数字级别的有效性
        if level in LOG_LEVEL_MAP:
            return level
        else:
            # 对于非标准数字级别，找到最接近的标准级别
            valid_levels = [0, 10, 20, 30, 40, 50]
            closest = min(valid_levels, key=lambda x: abs(x - level))
            return closest
    
    elif isinstance(level, str):
        # 字符串级别转换为数字
        level_upper = level.upper().strip()
        if level_upper in LOG_LEVEL_MAP:
            return LOG_LEVEL_MAP[level_upper]
        else:
            # 默认返回INFO级别
            return 20
    
    else:
        # 默认返回INFO级别
        return 20


def get_level_name(level: Union[str, int]) -> str:
    """
    获取日志级别的字符串名称
    
    Args:
        level: 日志级别
        
    Returns:
        str: 级别名称
    """
    numeric_level = normalize_log_level(level)
    return LOG_LEVEL_MAP.get(numeric_level, 'INFO')


class ColoredFormatter(logging.Formatter):
    """带颜色的控制台日志格式器"""
    
    # 定义颜色代码
    COLORS = {
        'DEBUG': '\033[36m',    # 青色
        'INFO': '\033[32m',     # 绿色
        'WARNING': '\033[33m',  # 黄色
        'ERROR': '\033[31m',    # 红色
        'CRITICAL': '\033[35m', # 紫色
        'RESET': '\033[0m'      # 重置
    }
    
    def format(self, record):
        # 添加颜色
        if sys.platform != 'win32':  # Windows终端可能不支持颜色
            levelname = record.levelname
            if levelname in self.COLORS:
                record.levelname = f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"
        
        return super().format(record)


class LevelFilter(logging.Filter):
    """日志级别过滤器"""
    
    def __init__(self, levels):
        """
        初始化过滤器
        
        Args:
            levels: 允许通过的日志级别列表，支持字符串和数字混合
        """
        super().__init__()
        if not isinstance(levels, list):
            levels = [levels]
        
        # 标准化所有级别为数字
        self.levels = [normalize_log_level(level) for level in levels]
    
    def filter(self, record):
        return record.levelno in self.levels


def setup_logging(level: Union[str, int] = "INFO", 
                 console_level: Union[str, int] = "INFO",
                 file_level: Union[str, int] = "DEBUG",
                 enable_colored_console: bool = True,
                 max_file_size: int = 10*1024*1024,
                 backup_count: int = 5,
                 log_dir: str = "logs"):
    """
    设置日志配置
    
    Args:
        level: 根日志级别，支持字符串('DEBUG')或数字(10)
        console_level: 控制台输出级别
        file_level: 文件输出级别
        enable_colored_console: 是否启用彩色控制台输出
        max_file_size: 单个日志文件最大大小(字节)
        backup_count: 日志文件备份数量
        log_dir: 日志文件目录
        
    Examples:
        setup_logging(level=10, console_level=20, file_level=10)  # 数字级别
        setup_logging(level="DEBUG", console_level="INFO")       # 字符串级别
        setup_logging(level=10, console_level="INFO")            # 混合级别
    """
    # 标准化日志级别
    root_level = normalize_log_level(level)
    console_numeric_level = normalize_log_level(console_level)
    file_numeric_level = normalize_log_level(file_level)
    
    # 创建logs目录
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 清除已有的处理器
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 设置根日志级别
    root_logger.setLevel(root_level)
    
    # ========== 控制台处理器 ==========
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_numeric_level)
    
    if enable_colored_console:
        console_formatter = ColoredFormatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%H:%M:%S'
        )
    else:
        console_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%H:%M:%S'
        )
    
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # ========== 文件处理器 ==========
    
    # 1. 综合日志文件 (所有级别)
    all_file_handler = RotatingFileHandler(
        os.path.join(log_dir, 'system.log'),
        maxBytes=max_file_size,
        backupCount=backup_count,
        encoding='utf-8'
    )
    all_file_handler.setLevel(file_numeric_level)
    all_file_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    all_file_handler.setFormatter(all_file_formatter)
    root_logger.addHandler(all_file_handler)
    
    # 2. 错误日志文件 (ERROR和CRITICAL)
    error_file_handler = RotatingFileHandler(
        os.path.join(log_dir, 'error.log'),
        maxBytes=max_file_size,
        backupCount=backup_count,
        encoding='utf-8'
    )
    error_file_handler.setLevel(40)  # ERROR级别
    error_file_handler.setFormatter(all_file_formatter)
    root_logger.addHandler(error_file_handler)
    
    # 3. 调试日志文件 (DEBUG级别，使用大小轮转而不是时间轮转)
    if file_numeric_level <= 10:  # DEBUG级别
        debug_file_handler = RotatingFileHandler(
            os.path.join(log_dir, 'debug.log'),
            maxBytes=max_file_size,  # 使用大小轮转
            backupCount=3,  # 保留3个备份文件
            encoding='utf-8'
        )
        debug_file_handler.setLevel(10)  # DEBUG级别
        debug_file_handler.addFilter(LevelFilter([10]))  # 只记录DEBUG级别
        debug_formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(funcName)s() - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        debug_file_handler.setFormatter(debug_formatter)
        
        # 添加错误处理，如果文件被占用就跳过这个处理器
        try:
            root_logger.addHandler(debug_file_handler)
        except (PermissionError, OSError) as e:
            print(f"警告: 无法创建debug.log处理器: {e}")
            # 继续运行，不添加debug文件处理器
    
    # 4. 性能日志文件 (特定模块)
    perf_logger = logging.getLogger('performance')
    perf_file_handler = RotatingFileHandler(
        os.path.join(log_dir, 'performance.log'),
        maxBytes=max_file_size,
        backupCount=3,
        encoding='utf-8'
    )
    perf_file_handler.setLevel(20)  # INFO级别
    perf_formatter = logging.Formatter(
        '%(asctime)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    perf_file_handler.setFormatter(perf_formatter)
    perf_logger.addHandler(perf_file_handler)
    perf_logger.propagate = False  # 防止重复输出
    
    # 设置特定模块的日志级别
    _configure_module_loggers()
    
    # 输出初始化信息
    logger = logging.getLogger(__name__)
    console_level_name = get_level_name(console_level)
    file_level_name = get_level_name(file_level)
    logger.info(f"日志系统初始化完成 - 控制台级别: {console_level_name}({console_numeric_level}), 文件级别: {file_level_name}({file_numeric_level})")


def _configure_module_loggers():
    """配置特定模块的日志级别"""
    
    # 降低第三方库的日志级别
    logging.getLogger('httpx').setLevel(30)       # WARNING
    logging.getLogger('urllib3').setLevel(30)     # WARNING
    logging.getLogger('requests').setLevel(30)    # WARNING
    logging.getLogger('langchain').setLevel(20)   # INFO
    logging.getLogger('openai').setLevel(30)      # WARNING
    
    # 设置项目模块的日志级别
    logging.getLogger('src.ai_chat').setLevel(10)    # DEBUG
    logging.getLogger('src.actors').setLevel(10)     # DEBUG
    logging.getLogger('src.core').setLevel(20)       # INFO
    logging.getLogger('src.ui').setLevel(20)         # INFO


def get_logger(name: str, level: Optional[Union[str, int]] = None) -> logging.Logger:
    """
    获取指定名称的日志记录器
    
    Args:
        name: 日志记录器名称
        level: 可选的日志级别，会覆盖默认设置，支持字符串和数字
    
    Returns:
        logging.Logger: 配置好的日志记录器
        
    Examples:
        get_logger(__name__, level=10)        # DEBUG级别
        get_logger(__name__, level="DEBUG")   # DEBUG级别
    """
    logger = logging.getLogger(name)
    
    if level is not None:
        numeric_level = normalize_log_level(level)
        logger.setLevel(numeric_level)
    
    return logger


def get_performance_logger() -> logging.Logger:
    """
    获取性能日志记录器
    
    Returns:
        logging.Logger: 性能日志记录器
    """
    return logging.getLogger('performance')


def set_debug_mode(enabled: bool = True):
    """
    设置调试模式
    
    Args:
        enabled: 是否启用调试模式
    """
    # 只调整根日志器和文件处理器的级别，不影响控制台
    level = 10 if enabled else 20  # DEBUG : INFO
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # 只调整文件处理器的级别，保持控制台级别不变
    for handler in root_logger.handlers:
        # 只调整文件处理器，不调整控制台处理器
        if isinstance(handler, RotatingFileHandler):
            if enabled:
                handler.setLevel(10)  # DEBUG
            else:
                # 根据处理器类型设置不同的级别
                if handler.level == 40:  # ERROR
                    # error.log保持ERROR级别
                    continue
                else:
                    # system.log设置为INFO级别
                    handler.setLevel(20)  # INFO
    
    logger = get_logger(__name__)
    logger.info(f"调试模式 {'启用' if enabled else '禁用'} - 控制台输出级别保持INFO不变")


def set_logger_level(logger_name: str, level: Union[str, int]):
    """
    设置指定logger的级别
    
    Args:
        logger_name: logger名称
        level: 日志级别，支持字符串和数字
        
    Examples:
        set_logger_level('src.ai_chat', 10)        # 设置为DEBUG级别
        set_logger_level('httpx', 'WARNING')       # 设置为WARNING级别
    """
    logger = logging.getLogger(logger_name)
    numeric_level = normalize_log_level(level)
    logger.setLevel(numeric_level)
    
    main_logger = get_logger(__name__)
    level_name = get_level_name(level)
    main_logger.info(f"设置 {logger_name} 日志级别为: {level_name}({numeric_level})")


def log_function_call(func):
    """
    函数调用日志装饰器
    
    Args:
        func: 要装饰的函数
    
    Returns:
        装饰后的函数
    """
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        logger.debug(f"调用函数: {func.__name__}(args={args}, kwargs={kwargs})")
        
        try:
            result = func(*args, **kwargs)
            logger.debug(f"函数 {func.__name__} 执行成功")
            return result
        except Exception as e:
            logger.error(f"函数 {func.__name__} 执行失败: {e}")
            raise
    
    return wrapper


# 示例使用
if __name__ == "__main__":
    # 测试数字级别设置
    print("🧪 测试数字级别日志配置")
    
    # 使用数字级别设置日志系统
    setup_logging(
        level=10,           # DEBUG
        console_level=20,   # INFO
        file_level=10,      # DEBUG
        enable_colored_console=True
    )
    
    # 测试不同级别的日志
    logger = get_logger(__name__, level=10)  # DEBUG级别
    perf_logger = get_performance_logger()
    
    logger.debug("数字级别测试: DEBUG(10) - 只在文件中显示")
    logger.info("数字级别测试: INFO(20) - 控制台和文件都显示")
    logger.warning("数字级别测试: WARNING(30)")
    logger.error("数字级别测试: ERROR(40)")
    logger.critical("数字级别测试: CRITICAL(50)")
    
    perf_logger.info("性能测试: 数字级别配置完成")
    
    # 测试动态设置级别
    set_logger_level('test.module', 10)
    set_logger_level('another.module', 'WARNING')
    
    print("✅ 数字级别测试完成，请查看日志文件") 