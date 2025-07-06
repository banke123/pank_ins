"""
    JSON解析器
"""
import json
import re
import os
import sys

# 添加项目根目录到Python路径
current_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..', '..'))
sys.path.insert(0, project_root)

from src.utils.logger_config import get_logger

logger = get_logger(__name__)

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