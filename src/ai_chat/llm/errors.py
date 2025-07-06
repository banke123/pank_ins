import os
import sys

# 添加项目根目录到Python路径
current_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
sys.path.insert(0, project_root)

from src.ai_chat.utils.error_codes import ErrorCode

class LLMError(Exception):
    """
    LLM模块基础异常类

    Attributes:
        code (ErrorCode): 错误码
        message (str): 错误信息
        details (Any): 错误详情 (可选)
    """
    def __init__(self, code: ErrorCode, message: str, details: any = None):
        self.code = code
        self.message = message
        self.details = details
        super().__init__(f"[{code.name}] {message}")

class AuthenticationError(LLMError):
    """认证或API密钥错误"""
    def __init__(self, message: str = "认证失败或API密钥无效", details: any = None):
        super().__init__(ErrorCode.AUTHENTICATION_FAILED, message, details)

class RateLimitError(LLMError):
    """请求频率超出限制"""
    def __init__(self, message: str = "请求频率超出限制", details: any = None):
        super().__init__(ErrorCode.RATE_LIMIT_EXCEEDED, message, details)

class ModelError(LLMError):
    """模型处理错误（例如输入无效、模型内部错误）"""
    def __init__(self, message: str = "模型处理错误", details: any = None):
        super().__init__(ErrorCode.MODEL_ERROR, message, details)

class ConnectionError(LLMError):
    """连接或网络错误"""
    def __init__(self, message: str = "连接或网络错误", details: any = None):
        super().__init__(ErrorCode.NETWORK_ERROR, message, details)

class ToolNotFoundError(LLMError):
    """工具不存在错误"""
    def __init__(self, tool_name: str, message: str = "工具未找到", details: any = None):
        super().__init__(ErrorCode.TOOL_NOT_FOUND, f"{message}: {tool_name}", details)
        self.tool_name = tool_name

# TODO: 根据实际需求添加更多特定的错误类型

# 更新 ErrorCode 定义 (如果需要)
# 确保在 ai_chat.utils.error_codes 中定义了以下错误码：
# AUTHENTICATION_FAILED = 1001
# RATE_LIMIT_EXCEEDED = 1002
# MODEL_ERROR = 1003
# NETWORK_ERROR = 1004
# TOOL_NOT_FOUND = 1005
# API_KEY_MISSING = 1006
# INIT_ERROR = 1007
# MEMORY_INIT_ERROR = 1008
# MESSAGE_SAVE_ERROR = 1009
# MESSAGE_GET_ERROR = 1010
# HISTORY_CLEAR_ERROR = 1011
# TOKEN_SAVE_ERROR = 1012
# RETRY_FAILED = 1013
# UNSUPPORTED_MODEL_TYPE = 1014 