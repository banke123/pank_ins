"""
流程卡片功能测试

测试基于JSON格式的流程卡片显示和交互功能
"""

import sys
import json
from pathlib import Path

# 添加src目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PySide6.QtCore import Qt

from ui.left_sidebar import LeftSidebar, ProcessCard


def test_process_card():
    """
    测试单个流程卡片
    """
    app = QApplication(sys.argv)
    
    # 测试数据
    test_process = {
        "id": "test_001",
        "title": "测试流程卡片",
        "status": "running",
        "type": "测试类型",
        "progress": 65,
        "duration": "00:03:45",
        "description": "这是一个测试流程卡片的示例",
        "start_time": "15:30:00"
    }
    
    # 创建卡片
    card = ProcessCard(test_process)
    card.card_clicked.connect(lambda data: print(f"点击卡片: {data['title']}"))
    
    # 显示卡片
    card.show()
    card.resize(300, 120)
    
    return app.exec()


def test_sidebar_with_json():
    """
    测试左侧边栏的JSON数据加载
    """
    app = QApplication(sys.argv)
    
    # 创建主窗口
    window = QMainWindow()
    window.setWindowTitle("流程卡片测试")
    window.setGeometry(100, 100, 400, 800)
    
    # 创建左侧边栏
    sidebar = LeftSidebar()
    
    # 测试JSON数据
    test_json = {
        "processes": [
            {
                "id": "proc_001",
                "title": "AI控制测试",
                "status": "running",
                "type": "AI控制",
                "progress": 80,
                "description": "正在执行AI控制示波器测试"
            },
            {
                "id": "proc_002",
                "title": "数据分析任务",
                "status": "completed",
                "type": "数据分析",
                "progress": 100,
                "description": "波形数据分析已完成"
            },
            {
                "id": "proc_003",
                "title": "设备检查",
                "status": "error",
                "type": "系统检查",
                "description": "设备连接检查失败"
            }
        ]
    }
    
    # 加载JSON数据
    sidebar.load_processes_from_json(test_json)
    
    # 连接信号
    sidebar.process_selected.connect(
        lambda data: print(f"选择流程: {data['title']} (状态: {data['status']})")
    )
    
    # 设置为中央组件
    window.setCentralWidget(sidebar)
    window.show()
    
    return app.exec()


def test_json_format():
    """
    测试JSON格式支持
    """
    # 测试不同的JSON格式
    formats = [
        # 格式1: 直接数组
        [
            {"id": "1", "title": "流程1", "status": "running"},
            {"id": "2", "title": "流程2", "status": "idle"}
        ],
        
        # 格式2: 包装对象
        {
            "processes": [
                {"id": "1", "title": "流程1", "status": "running"},
                {"id": "2", "title": "流程2", "status": "idle"}
            ]
        },
        
        # 格式3: 单个对象
        {"id": "1", "title": "单个流程", "status": "completed"}
    ]
    
    app = QApplication(sys.argv)
    sidebar = LeftSidebar()
    
    for i, format_data in enumerate(formats):
        print(f"\n测试格式 {i+1}:")
        sidebar.load_processes_from_json(format_data)
        processes = sidebar.get_processes_data()
        print(f"加载了 {len(processes)} 个流程")
        for proc in processes:
            print(f"  - {proc.get('title', '未知')} ({proc.get('status', '未知')})")
    
    return 0


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="流程卡片测试")
    parser.add_argument("--test", choices=["card", "sidebar", "json"], 
                       default="sidebar", help="选择测试类型")
    
    args = parser.parse_args()
    
    if args.test == "card":
        sys.exit(test_process_card())
    elif args.test == "sidebar":
        sys.exit(test_sidebar_with_json())
    elif args.test == "json":
        sys.exit(test_json_format()) 