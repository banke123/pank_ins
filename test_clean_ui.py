"""
清理后的UI测试脚本
"""

import sys
import logging
from pathlib import Path

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_clean_ui():
    """测试清理后的UI"""
    try:
        logger.info("=== 测试清理后的QML UI界面 ===")
        
        # 添加项目根目录到路径
        project_root = Path(__file__).parent
        sys.path.insert(0, str(project_root))
        
        # 导入QML主窗口
        from src.ui.qml_main_window import test_qml_main_window
        
        logger.info("启动QML主窗口...")
        test_qml_main_window()
        
        logger.info("=== 测试完成 ===")
        
    except Exception as e:
        logger.error(f"测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_clean_ui() 