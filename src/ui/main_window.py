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
from PySide6.QtCore import Qt, Signal, QTimer

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
    
    # 定义信号
    window_closed = Signal()
    
    def __init__(self):
        super().__init__()
        self.ai_actor_ref = None  # AI Actor引用
        self.pending_futures = {}  # 存储等待中的future {timer_id: (future, container_id, timer)}
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
        main_splitter.setSizes([290, 860, 350])  # 左:中:右 = 调整左侧宽度
        
        # 设置布局
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)  # 进一步增加主窗口边距
        layout.setSpacing(12)  # 增加间距
        layout.addWidget(main_splitter)
        central_widget.setLayout(layout)
        
    def setup_connections(self):
        """
        设置信号连接
        """
        # 连接左侧边栏信号
        self.left_sidebar.plan_card_clicked.connect(self.on_plan_project_selected)
        
        # 连接AI对话面板信号
        self.ai_chat_panel.message_sent.connect(self.on_ai_message_sent)
        
        # 连接工作区信号
        self.work_area.process_action_requested.connect(self.on_process_action_requested)
        self.work_area.task_card_clicked.connect(self.on_task_card_clicked)
        
    def on_plan_project_selected(self, project_data):
        """
        处理计划选择事件
        
        Args:
            project_data (dict): 选中的计划数据
        """
        project_name = project_data.get('project_name', '未知计划')
        project_status = project_data.get('status', 'unknown')
        
        self.log_area.add_log("INFO", f"选择计划: {project_name} (状态: {project_status})")
        self.statusBar().showMessage(f"当前计划: {project_name}")
        
        # 显示计划的任务在工作区域
        self.work_area.show_plan_project_tasks(project_data)
        
        # 如果需要，可以在这里添加其他处理逻辑
        print(f"计划已选择: {project_name}, 但工作区保持空白状态")
        
    def on_task_card_clicked(self, task_data):
        """
        处理任务卡片点击事件
        
        Args:
            task_data (dict): 任务卡片数据
        """
        task_name = task_data.get('task_name', '未知任务')
        signal_type = task_data.get('signal_type', '未知')
        
        self.log_area.add_log("INFO", f"选择任务: {task_name} ({signal_type})")
        self.statusBar().showMessage(f"当前任务: {task_name}")
        
        # 这里可以添加具体的任务处理逻辑
        # 比如：显示任务详情、开始测试等
        print(f"处理任务: {task_name}")

    def on_process_selected(self, process_data):
        """
        处理流程选择事件（保留用于兼容性）
        
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
        self.log_area.add_log("INFO", f"用户发送消息: {message[:50]}...")
        
        # 如果AI Actor已连接，发送消息进行处理
        if self.ai_actor_ref:
            try:
                # 创建用户容器ID（可以基于会话或用户标识）
                container_id = "main_window_user"
                
                # 发送流式消息到AI Actor进行处理
                ai_message = {
                    "action": "process_message_stream",
                    "container_id": container_id,
                    "content": message
                }
                
                # 使用pykka的ask方法非阻塞获取future
                future = self.ai_actor_ref.ask(ai_message, block=False)
                
                # 创建定时器来检查future状态
                timer = QTimer()
                timer_id = id(timer)  # 使用timer对象的id作为唯一标识
                timer.timeout.connect(lambda: self.check_ai_future(timer_id))
                
                # 存储future和相关信息
                self.pending_futures[timer_id] = (future, container_id, timer)
                
                # 每100ms检查一次
                timer.start(100)
                
                self.log_area.add_log("INFO", "AI消息已发送，等待响应...")
                
            except Exception as e:
                self.log_area.add_log("ERROR", f"发送AI消息失败: {e}")
                # 显示错误消息
                self.ai_chat_panel.add_ai_response(f"抱歉，AI服务暂时不可用: {str(e)}")
        else:
            self.log_area.add_log("WARNING", "AI Actor未连接")
            self.ai_chat_panel.add_ai_response("抱歉，AI服务尚未启动，请稍后再试。")
    
    def check_ai_future(self, timer_id):
        """
        检查AI Future的状态
        
        Args:
            timer_id: 定时器ID
        """
        if timer_id not in self.pending_futures:
            return
            
        future, container_id, timer = self.pending_futures[timer_id]
        
        try:
            # 尝试非阻塞获取结果（使用很短的超时）
            try:
                result = future.get(timeout=0.001)  # 1毫秒超时，如果没完成会抛出异常
                
                # 如果能获取到结果，说明已完成
                timer.stop()
                
                if result.get("status") == "success":
                    ai_response = result.get("response", "AI处理完成，但无回复内容。")
                    self.ai_chat_panel.add_ai_response(ai_response)
                    self.log_area.add_log("INFO", "AI响应已显示")
                else:
                    error_msg = result.get("message", "未知错误")
                    self.ai_chat_panel.add_ai_response(f"处理失败: {error_msg}")
                    self.log_area.add_log("ERROR", f"AI处理失败: {error_msg}")
                
                # 清理
                del self.pending_futures[timer_id]
                
            except Exception:
                # 如果get超时，说明还没完成，继续等待
                # 这里不是错误，只是结果还没准备好
                pass
                
        except Exception as e:
            # 处理其他异常
            timer.stop()
            self.log_area.add_log("ERROR", f"检查AI响应时发生错误: {e}")
            self.ai_chat_panel.add_ai_response(f"检查AI响应时发生错误: {str(e)}")
            
            # 清理
            if timer_id in self.pending_futures:
                del self.pending_futures[timer_id]

    def closeEvent(self, event):
        """
        重写关闭事件，发射窗口关闭信号，清理pending futures
        """
        # 清理所有pending futures
        for timer_id, (future, container_id, timer) in self.pending_futures.items():
            try:
                timer.stop()
            except Exception as e:
                print(f"清理定时器失败: {e}")
        self.pending_futures.clear()
        
        self.window_closed.emit()
        super().closeEvent(event)

    def set_ai_actor_ref(self, ai_actor_ref):
        """
        设置AI Actor引用
        
        Args:
            ai_actor_ref: AI Actor的引用
        """
        self.ai_actor_ref = ai_actor_ref
        self.log_area.add_log("INFO", "AI Actor连接成功")

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


# def main():
#     """
#     主函数，用于测试主窗口
#     """
#     app = QApplication(sys.argv)
    
#     # 创建主窗口
#     main_window = MainWindow()
    
#     # 显示窗口
#     main_window.show()
    
#     sys.exit(app.exec())


# if __name__ == "__main__":
#     main() 