# Actor模块

## 概述

此模块包含系统中所有的Actor实现，采用pykka框架实现Actor模式。

## Actor类型

### BaseActor
所有Actor的基类，提供通用功能：
- 生命周期管理
- 消息处理框架
- 错误处理
- 状态管理

### UIActor
处理用户界面相关的消息和事件：
- 状态更新
- 通知显示
- 数据展示更新

### AIActor
负责AI模型调用和智能分析：
- 数据分析
- 命令生成
- 自然语言查询处理
- AI模型管理

### OscilloscopeActor
示波器设备控制：
- 设备连接/断开
- 设备配置
- 数据采集
- 命令发送

### DataProcessorActor
数据处理和分析：
- 数据预处理
- 统计分析
- 数据滤波
- 数据导入/导出

### LoggerActor
系统日志管理：
- 日志收集
- 日志分级
- 日志导出
- 日志查询

## 使用方法

```python
from src.actors import UIActor, AIActor

# 启动Actor
ui_actor = UIActor.start()
ai_actor = AIActor.start()

# 发送消息
response = ui_actor.ask({'action': 'update_status', 'data': {...}})

# 停止Actor
ui_actor.stop()
ai_actor.stop()
``` 