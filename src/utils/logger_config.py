#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
日志配置模块

配置系统日志格式和输出。

@author: PankIns Team
@version: 1.0.0
"""

import os
import logging
from logging.handlers import RotatingFileHandler


def setup_logging():
    """
    设置日志配置
    """
    # 创建logs目录
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # 设置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # 日志格式
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # 文件处理器
    file_handler = RotatingFileHandler(
        'logs/system.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """
    获取指定名称的日志记录器
    
    @param {str} name - 日志记录器名称
    @returns {logging.Logger} 日志记录器
    """
    return logging.getLogger(name) 