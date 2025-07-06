"""
QML卡片系统 - Python端集成
提供QML界面与Python后端的数据桥接功能
"""

import sys
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

from PySide6.QtCore import QObject, Signal, Slot, Property, QUrl, QTimer
from PySide6.QtQml import QmlElement, qmlRegisterType
from PySide6.QtQuick import QQuickView
from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine

# 配置日志
logger = logging.getLogger(__name__)

QML_IMPORT_NAME = "CardSystem"
QML_IMPORT_MAJOR_VERSION = 1


@QmlElement
class CardSystemBridge(QObject):
    """QML卡片系统桥接类"""
    
    # 信号定义
    cardAdded = Signal(str, arguments=['cardData'])
    cardUpdated = Signal(str, str, arguments=['cardId', 'updateData'])
    cardRemoved = Signal(str, arguments=['cardId'])
    systemCleared = Signal()
    logMessageAdded = Signal(str, arguments=['message'])
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._cards = {}
        self._card_counter = 0
        
        # 设置定时器用于模拟数据更新
        self._update_timer = QTimer()
        self._update_timer.timeout.connect(self._simulate_progress_update)
        
    @Slot(result=str)
    def addLevel3Plan(self):
        """添加Level3计划"""
        self._card_counter += 1
        plan_id = f"LEVEL3_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        card_data = {
            "id": f"level3_{self._card_counter}",
            "type": "level3",
            "plan_id": plan_id,
            "任务总数": 3,
            "计划名": f"I2C协议测试计划 {self._card_counter}",
            "Json A样式": {
                "任务具体内容": [
                    {
                        "任务名": "I2C时钟信号测试",
                        "任务类型": "signal_test",
                        "任务描述": "测试I2C时钟线(SCL)信号质量",
                        "执行情况": "待执行",
                        "预估时间": "10分钟"
                    },
                    {
                        "任务名": "I2C数据信号测试",
                        "任务类型": "signal_test",
                        "任务描述": "测试I2C数据线(SDA)信号完整性",
                        "执行情况": "待执行",
                        "预估时间": "12分钟"
                    },
                    {
                        "任务名": "I2C协议解码验证",
                        "任务类型": "protocol_test",
                        "任务描述": "解码I2C通信协议并验证数据",
                        "执行情况": "待执行",
                        "预估时间": "15分钟"
                    }
                ],
                "当前任务": 0,
                "计划时间": "37分钟",
                "计划状态": "planning",
                "计划结果": "",
                "计划计数": self._card_counter
            }
        }
        
        self._cards[card_data["id"]] = card_data
        card_json = json.dumps(card_data, ensure_ascii=False)
        
        self.cardAdded.emit(card_json)
        self.logMessageAdded.emit(f"创建Level3计划: {card_data['计划名']}")
        
        return card_json
    
    @Slot(str, result=str)
    def addLevel2Task(self, plan_id: str):
        """添加Level2任务"""
        self._card_counter += 1
        task_id = f"LEVEL2_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        card_data = {
            "id": f"level2_{self._card_counter}",
            "type": "level2",
            "plan_id": task_id,
            "计划计数": self._card_counter,
            "任务名": "I2C时钟信号测试",
            "步骤总数": 4,
            "Json B样式": {
                "每个步骤具体内容": [
                    {
                        "步骤名": "连接示波器探头",
                        "步骤描述": "将探头连接到I2C时钟线",
                        "步骤状态": "待执行",
                        "执行时间": ""
                    },
                    {
                        "步骤名": "设置触发条件",
                        "步骤描述": "配置示波器触发参数",
                        "步骤状态": "待执行",
                        "执行时间": ""
                    },
                    {
                        "步骤名": "开始信号采集",
                        "步骤描述": "启动示波器采集I2C信号",
                        "步骤状态": "待执行",
                        "执行时间": ""
                    },
                    {
                        "步骤名": "分析信号质量",
                        "步骤描述": "分析采集到的信号数据",
                        "步骤状态": "待执行",
                        "执行时间": ""
                    }
                ],
                "当前步骤": 0,
                "任务状态": "waiting",
                "最终结果": ""
            }
        }
        
        self._cards[card_data["id"]] = card_data
        card_json = json.dumps(card_data, ensure_ascii=False)
        
        self.cardAdded.emit(card_json)
        self.logMessageAdded.emit(f"创建Level2任务: {card_data['任务名']}")
        
        return card_json
    
    @Slot(str, str)
    def executeCard(self, card_id: str, action: str):
        """执行卡片操作"""
        if card_id not in self._cards:
            self.logMessageAdded.emit(f"错误: 卡片 {card_id} 不存在")
            return
            
        card = self._cards[card_id]
        
        if action == "execute":
            if card["type"] == "level3":
                # 开始执行Level3计划
                card["Json A样式"]["计划状态"] = "running"
                self.logMessageAdded.emit(f"开始执行Level3计划: {card['计划名']}")
                
                # 创建对应的Level2任务
                level2_json = self.addLevel2Task(card["plan_id"])
                
                # 启动进度更新定时器
                self._update_timer.start(2000)  # 每2秒更新一次
                
            elif card["type"] == "level2":
                # 开始执行Level2任务
                card["Json B样式"]["任务状态"] = "running"
                self.logMessageAdded.emit(f"开始执行Level2任务: {card['任务名']}")
                
                # 启动步骤执行
                self._execute_level2_steps(card_id)
        
        elif action == "view_detail":
            self.logMessageAdded.emit(f"查看卡片详情: {card.get('计划名', card.get('任务名', '未知'))}")
            
        elif action == "delete":
            self._remove_card(card_id)
            
        # 更新卡片数据
        self._update_card(card_id, card)
    
    @Slot()
    def clearAllCards(self):
        """清空所有卡片"""
        self._cards.clear()
        self._card_counter = 0
        self._update_timer.stop()
        self.systemCleared.emit()
        self.logMessageAdded.emit("系统已重置，准备新的演示")
    
    def _update_card(self, card_id: str, card_data: Dict[str, Any]):
        """更新卡片数据"""
        if card_id in self._cards:
            self._cards[card_id] = card_data
            update_json = json.dumps(card_data, ensure_ascii=False)
            self.cardUpdated.emit(card_id, update_json)
    
    def _remove_card(self, card_id: str):
        """移除卡片"""
        if card_id in self._cards:
            card = self._cards[card_id]
            del self._cards[card_id]
            self.cardRemoved.emit(card_id)
            self.logMessageAdded.emit(f"删除卡片: {card.get('计划名', card.get('任务名', '未知'))}")
    
    def _execute_level2_steps(self, card_id: str):
        """执行Level2任务步骤"""
        if card_id not in self._cards:
            return
            
        card = self._cards[card_id]
        if card["type"] != "level2":
            return
            
        # 启动步骤执行定时器
        timer = QTimer()
        timer.timeout.connect(lambda: self._advance_level2_step(card_id, timer))
        timer.start(3000)  # 每3秒执行一个步骤
    
    def _advance_level2_step(self, card_id: str, timer: QTimer):
        """推进Level2任务步骤"""
        if card_id not in self._cards:
            timer.stop()
            return
            
        card = self._cards[card_id]
        current_step = card["Json B样式"]["当前步骤"]
        total_steps = card["步骤总数"]
        
        if current_step < total_steps:
            # 更新当前步骤状态
            if current_step > 0:
                card["Json B样式"]["每个步骤具体内容"][current_step - 1]["步骤状态"] = "已完成"
                card["Json B样式"]["每个步骤具体内容"][current_step - 1]["执行时间"] = datetime.now().strftime("%H:%M:%S")
            
            # 开始下一步骤
            if current_step < total_steps:
                card["Json B样式"]["每个步骤具体内容"][current_step]["步骤状态"] = "执行中"
                step_name = card["Json B样式"]["每个步骤具体内容"][current_step]["步骤名"]
                self.logMessageAdded.emit(f"执行步骤 {current_step + 1}: {step_name}")
                
                card["Json B样式"]["当前步骤"] = current_step + 1
        else:
            # 任务完成
            card["Json B样式"]["任务状态"] = "completed"
            card["Json B样式"]["最终结果"] = "任务执行成功"
            self.logMessageAdded.emit(f"Level2任务完成: {card['任务名']}")
            timer.stop()
        
        self._update_card(card_id, card)
    
    def _simulate_progress_update(self):
        """模拟进度更新"""
        level3_cards = [card for card in self._cards.values() if card["type"] == "level3" and card["Json A样式"]["计划状态"] == "running"]
        
        for card in level3_cards:
            current_task = card["Json A样式"]["当前任务"]
            total_tasks = card["任务总数"]
            
            if current_task < total_tasks:
                # 随机推进任务进度
                import random
                if random.random() < 0.3:  # 30% 概率推进
                    if current_task > 0:
                        card["Json A样式"]["任务具体内容"][current_task - 1]["执行情况"] = "已完成"
                    
                    if current_task < total_tasks:
                        card["Json A样式"]["任务具体内容"][current_task]["执行情况"] = "执行中"
                        task_name = card["Json A样式"]["任务具体内容"][current_task]["任务名"]
                        self.logMessageAdded.emit(f"Level3计划推进: 开始执行 {task_name}")
                        
                        card["Json A样式"]["当前任务"] = current_task + 1
                    
                    self._update_card(card["id"], card)
            else:
                # 计划完成
                card["Json A样式"]["计划状态"] = "completed"
                card["Json A样式"]["计划结果"] = "计划执行成功"
                self.logMessageAdded.emit(f"Level3计划完成: {card['计划名']}")
                self._update_card(card["id"], card)


class QMLCardSystem:
    """QML卡片系统主类"""
    
    def __init__(self):
        self.app = None
        self.engine = None
        self.bridge = None
        self.qml_dir = Path(__file__).parent / "qml"
        
    def initialize(self):
        """初始化QML系统"""
        try:
            # 创建Qt应用
            if not QApplication.instance():
                self.app = QApplication(sys.argv)
            else:
                self.app = QApplication.instance()
            
            # 注册QML类型
            qmlRegisterType(CardSystemBridge, QML_IMPORT_NAME, QML_IMPORT_MAJOR_VERSION, 0, "CardSystemBridge")
            
            # 创建桥接对象
            self.bridge = CardSystemBridge()
            
            # 创建QML引擎
            self.engine = QQmlApplicationEngine()
            
            # 添加QML模块路径
            self.engine.addImportPath(str(self.qml_dir.parent))
            
            # 设置上下文属性
            self.engine.rootContext().setContextProperty("cardBridge", self.bridge)
            
            # 加载QML文件
            qml_file = self.qml_dir / "CardSystem.qml"
            if qml_file.exists():
                self.engine.load(QUrl.fromLocalFile(str(qml_file)))
            else:
                logger.error(f"QML文件不存在: {qml_file}")
                return False
            
            # 检查是否加载成功
            if not self.engine.rootObjects():
                logger.error("QML文件加载失败")
                return False
                
            logger.info("QML卡片系统初始化成功")
            return True
            
        except Exception as e:
            logger.error(f"QML卡片系统初始化失败: {e}")
            return False
    
    def run(self):
        """运行QML应用"""
        if self.app:
            return self.app.exec()
        return -1
    
    def add_level3_plan(self, plan_data: Dict[str, Any]) -> bool:
        """添加Level3计划"""
        if self.bridge:
            try:
                card_json = self.bridge.addLevel3Plan()
                return True
            except Exception as e:
                logger.error(f"添加Level3计划失败: {e}")
                return False
        return False
    
    def add_level2_task(self, task_data: Dict[str, Any]) -> bool:
        """添加Level2任务"""
        if self.bridge:
            try:
                plan_id = task_data.get("plan_id", "")
                card_json = self.bridge.addLevel2Task(plan_id)
                return True
            except Exception as e:
                logger.error(f"添加Level2任务失败: {e}")
                return False
        return False
    
    def update_card(self, card_id: str, update_data: Dict[str, Any]) -> bool:
        """更新卡片数据"""
        if self.bridge and card_id in self.bridge._cards:
            try:
                card = self.bridge._cards[card_id]
                # 深度合并更新数据
                self._deep_merge(card, update_data)
                self.bridge._update_card(card_id, card)
                return True
            except Exception as e:
                logger.error(f"更新卡片失败: {e}")
                return False
        return False
    
    def _deep_merge(self, target: Dict, source: Dict):
        """深度合并字典"""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._deep_merge(target[key], value)
            else:
                target[key] = value


def main():
    """主函数 - 用于测试QML卡片系统"""
    import logging
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 创建并运行QML卡片系统
    qml_system = QMLCardSystem()
    
    if qml_system.initialize():
        logger.info("启动QML卡片系统...")
        sys.exit(qml_system.run())
    else:
        logger.error("QML卡片系统初始化失败")
        sys.exit(1)


if __name__ == "__main__":
    main() 