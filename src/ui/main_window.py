"""
主窗口模块

这个模块提供了Pank Ins的主界面
包含左侧边栏、右侧AI对话窗口、中间工作区和底部日志区域
支持拖动调整各区域大小
"""

import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QSplitter
)
from PySide6.QtCore import Qt

# 导入模块化组件
from .left_sidebar import LeftSidebar
from .work_area import WorkArea
from .ai_chat_panel import AIChatPanel
from .log_area import LogArea


class MainWindow(QMainWindow):
    """
    主窗口类
    
    整合所有UI组件，提供主界面
    """
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        """
        设置主窗口界面
        """
        # 设置窗口属性
        self.setWindowTitle("Pank Ins - AI 控制示波器系统")
        self.setGeometry(100, 100, 1400, 900)
        
        # 设置窗口样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
            }
        """)
        
        # 创建菜单栏
        self.create_menu_bar()
        
        # 创建状态栏
        self.create_status_bar()
        
        # 创建中央组件
        self.create_central_widget()
        
    def create_menu_bar(self):
        """
        创建菜单栏
        """
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件(&F)")
        file_menu.addAction("新建项目", self.new_project)
        file_menu.addAction("打开项目", self.open_project)
        file_menu.addSeparator()
        file_menu.addAction("退出", self.close)
        
        # 编辑菜单
        edit_menu = menubar.addMenu("编辑(&E)")
        edit_menu.addAction("设置", self.open_settings)
        
        # 视图菜单
        view_menu = menubar.addMenu("视图(&V)")
        view_menu.addAction("重置布局", self.reset_layout)
        
        # 工具菜单
        tools_menu = menubar.addMenu("工具(&T)")
        tools_menu.addAction("设备管理", self.open_device_manager)
        tools_menu.addAction("插件管理", self.open_plugin_manager)
        
        # 帮助菜单
        help_menu = menubar.addMenu("帮助(&H)")
        help_menu.addAction("关于", self.show_about)
        
    def create_status_bar(self):
        """
        创建状态栏
        """
        status_bar = self.statusBar()
        status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #f8fafc;
                border-top: 1px solid #e2e8f0;
                color: #718096;
                font-size: 11px;
            }
        """)
        
        status_bar.showMessage("就绪")
        
    def create_central_widget(self):
        """
        创建中央组件
        """
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主分割器（水平）
        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #e2e8f0;
                width: 2px;
            }
            QSplitter::handle:hover {
                background-color: #cbd5e0;
            }
        """)
        
        # 创建左侧边栏
        self.left_sidebar = LeftSidebar()
        main_splitter.addWidget(self.left_sidebar)
        
        # 创建中间区域分割器（垂直）
        middle_splitter = QSplitter(Qt.Vertical)
        middle_splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #e2e8f0;
                height: 2px;
            }
            QSplitter::handle:hover {
                background-color: #cbd5e0;
            }
        """)
        
        # 创建工作区
        self.work_area = WorkArea()
        middle_splitter.addWidget(self.work_area)
        
        # 创建日志区
        self.log_area = LogArea()
        middle_splitter.addWidget(self.log_area)
        
        # 设置中间分割器的比例
        middle_splitter.setSizes([600, 200])  # 工作区:日志区 = 3:1
        
        main_splitter.addWidget(middle_splitter)
        
        # 创建右侧AI对话面板
        self.ai_chat_panel = AIChatPanel()
        main_splitter.addWidget(self.ai_chat_panel)
        
        # 设置主分割器的比例
        main_splitter.setSizes([250, 900, 350])  # 左:中:右 = 1:3.6:1.4
        
        # 设置布局
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.addWidget(main_splitter)
        central_widget.setLayout(layout)
        
    def setup_connections(self):
        """
        设置信号连接
        """
        # 连接左侧边栏信号
        self.left_sidebar.process_selected.connect(self.on_process_selected)
        
        # 连接AI对话面板信号
        self.ai_chat_panel.message_sent.connect(self.on_ai_message_sent)
        
        # 连接工作区信号
        self.work_area.process_action_requested.connect(self.on_process_action_requested)
        
    def on_process_selected(self, process_data):
        """
        处理流程选择事件
        
        Args:
            process_data (dict): 选中的流程数据
        """
        process_title = process_data.get('title', '未知流程')
        process_status = process_data.get('status', 'unknown')
        
        self.log_area.add_log("INFO", f"选择流程: {process_title} (状态: {process_status})")
        self.statusBar().showMessage(f"当前流程: {process_title}")
        
        # 可以在这里添加更多处理逻辑，比如在工作区显示流程详情
        self.work_area.show_process_details(process_data)
        
    def on_process_action_requested(self, action, process_data):
        """
        处理流程操作请求
        
        Args:
            action (str): 操作类型
            process_data (dict): 流程数据
        """
        process_title = process_data.get('title', '未知流程')
        process_id = process_data.get('id', 'unknown')
        
        self.log_area.add_log("INFO", f"流程操作: {action} - {process_title}")
        
        # 根据操作类型执行相应的处理
        if action == "start":
            self.log_area.add_log("INFO", f"启动流程: {process_title}")
            # 更新左侧边栏中的流程状态
            self.left_sidebar.update_process_status(process_id, "running")
            
        elif action == "pause":
            self.log_area.add_log("INFO", f"暂停流程: {process_title}")
            self.left_sidebar.update_process_status(process_id, "paused")
            
        elif action == "resume":
            self.log_area.add_log("INFO", f"继续流程: {process_title}")
            self.left_sidebar.update_process_status(process_id, "running")
            
        elif action == "stop":
            self.log_area.add_log("INFO", f"停止流程: {process_title}")
            self.left_sidebar.update_process_status(process_id, "stopped")
            
        elif action == "restart":
            self.log_area.add_log("INFO", f"重新启动流程: {process_title}")
            self.left_sidebar.update_process_status(process_id, "running")
            
        elif action == "edit":
            self.log_area.add_log("INFO", f"编辑流程: {process_title}")
            # 这里可以打开编辑对话框
            
        elif action == "delete":
            self.log_area.add_log("WARNING", f"删除流程: {process_title}")
            # 这里可以显示确认对话框
            
        # 更新状态栏
        self.statusBar().showMessage(f"执行操作: {action} - {process_title}")
        
    def on_ai_message_sent(self, message):
        """
        处理AI消息发送事件
        
        Args:
            message (str): 发送的消息
        """
        self.log_area.add_log("INFO", f"AI对话: {message}")
        
    # 菜单事件处理方法
    def new_project(self):
        """新建项目"""
        self.log_area.add_log("INFO", "新建项目")
        
    def open_project(self):
        """打开项目"""
        self.log_area.add_log("INFO", "打开项目")
        
    def open_settings(self):
        """打开设置"""
        self.log_area.add_log("INFO", "打开设置")
        
    def reset_layout(self):
        """重置布局"""
        self.log_area.add_log("INFO", "重置布局")
        
    def open_device_manager(self):
        """打开设备管理"""
        self.log_area.add_log("INFO", "打开设备管理")
        
    def open_plugin_manager(self):
        """打开插件管理"""
        self.log_area.add_log("INFO", "打开插件管理")
        
    def show_about(self):
        """显示关于"""
        self.log_area.add_log("INFO", "显示关于信息")


def main():
    """
    主函数，用于测试主窗口
    """
    app = QApplication(sys.argv)
    
    # 创建主窗口
    main_window = MainWindow()
    
    # 显示窗口
    main_window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 