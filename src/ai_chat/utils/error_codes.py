#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
错误代码定义模块
定义系统中使用的各种错误代码
"""

from enum import IntEnum


class ErrorCode(IntEnum):
    """错误代码枚举"""
    
    # 通用错误 (1000-1999)
    SUCCESS = 1000
    UNKNOWN_ERROR = 1001
    INVALID_PARAMETER = 1002
    PERMISSION_DENIED = 1003
    
    # 初始化错误 (2000-2099)
    INIT_ERROR = 2000
    CONFIG_ERROR = 2001
    
    # 模型相关错误 (3000-3099)
    MODEL_ERROR = 3000
    MODEL_NOT_FOUND = 3001
    MODEL_TIMEOUT = 3002
    MODEL_RATE_LIMIT = 3003
    
    # 工具相关错误 (4000-4099)
    TOOL_ERROR = 4000
    TOOL_NOT_FOUND = 4001
    TOOL_EXECUTION_ERROR = 4002
    
    # 解析错误 (5000-5099)
    PARSE_ERROR = 5000
    JSON_PARSE_ERROR = 5001
    
    # 网络错误 (6000-6099)
    NETWORK_ERROR = 6000
    API_ERROR = 6001
    TIMEOUT_ERROR = 6002 