# QML模块化重构说明

## 概述
本次重构解决了主窗口的双窗口问题，并实现了QML组件的模块化设计。

## 问题解决

### 1. 双窗口问题
**原问题**: 
- 应用启动时出现两个窗口：一个空白的QWidget窗口 + 一个QML ApplicationWindow
- 用户体验不佳，界面混乱

**解决方案**:
- 将 `QQmlApplicationEngine` 替换为 `QQuickWidget`
- 使用 `QQuickWidget` 在单个 QWidget 中嵌入QML内容
- QML文件从 `ApplicationWindow` 改为 `Rectangle` 作为根元素

### 2. 模块化设计
**实现的模块化组件**:
- `WorkflowTreeView.qml` - 左侧工作流程树状图组件
- `AIChatPanel.qml` - 右侧AI对话面板组件
- `MainWindow.qml` - 主窗口布局，组合各个模块

**组件特性**:
- 独立的属性定义和信号系统
- 支持数据绑定和事件传递
- 可重用的设计模式

## 文件结构

```
src/ui/
├── qml_main_window.py          # 主窗口Python类
└── qml/
    ├── qmldir                  # QML模块注册文件
    ├── MainWindow.qml          # 主窗口QML文件
    ├── WorkflowTreeView.qml    # 工作流程树状图组件
    └── AIChatPanel.qml         # AI对话面板组件
```

## 组件说明

### WorkflowTreeView.qml
**功能**: 左侧工作流程树状图
- 支持计划/任务层级显示
- 可展开/收起功能
- 状态指示器（运行中/已完成/等待中/错误）
- 进度条显示
- 交互事件：点击、双击、右键菜单

**主要属性**:
- `workflowData`: 工作流数据
- `theme`: 主题配置

**主要信号**:
- `itemClicked(itemData)`: 项目点击事件
- `itemDoubleClicked(itemData)`: 项目双击事件
- `contextMenuRequested(itemData)`: 右键菜单请求

### AIChatPanel.qml
**功能**: 右侧AI对话面板
- 支持流式响应显示
- 消息历史记录
- 用户输入界面
- 状态指示器

**主要属性**:
- `messageText`: 输入框文本
- `isStreaming`: 是否正在流式响应
- `chatHistory`: 对话历史

**主要信号**:
- `messageSent(message)`: 消息发送事件
- `streamStarted()`: 流式响应开始
- `streamChunkReceived(chunk)`: 流式响应片段接收
- `streamFinished()`: 流式响应完成

### 主窗口集成
**QMLMainWindow类改进**:
- 使用 `QQuickWidget` 替代 `QQmlApplicationEngine`
- 支持备用界面机制
- 完整的Actor系统集成
- 流式响应支持

## 技术实现

### 1. 组件注册
```qml
// qmldir文件
module ui.qml
WorkflowTreeView 1.0 WorkflowTreeView.qml
AIChatPanel 1.0 AIChatPanel.qml
```

### 2. 组件导入
```qml
// MainWindow.qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Controls.Material 2.15
import "."  // 导入本地模块
```

### 3. 组件使用
```qml
// 使用WorkflowTreeView组件
WorkflowTreeView {
    id: workflowTree
    Layout.fillHeight: true
    Layout.preferredWidth: 300
    
    onItemClicked: function(itemData) {
        console.log("工作流项目点击:", itemData.name)
    }
}

// 使用AIChatPanel组件
AIChatPanel {
    id: aiChatPanel
    Layout.fillHeight: true
    Layout.preferredWidth: 400
    
    onMessageSent: function(message) {
        mainWindowBridge.userMessageSent(message)
    }
}
```

## 启动流程优化

**新的启动顺序**:
1. 配置日志系统
2. 初始化Actor系统
3. 启动UI Actor
4. 启动AI Actor
5. 建立Actor间连接

**代码实现**:
```python
class PankInsApplication:
    def run(self):
        self.setup_logging()           # 步骤1
        self.initialize_actor_system() # 步骤2
        self.start_ui_actor()          # 步骤3
        self.start_ai_actor()          # 步骤4
        self.setup_actor_connections() # 步骤5
```

## 测试验证

**测试项目**:
- ✅ 双窗口问题解决
- ✅ 模块化组件正常加载
- ✅ 流式响应功能正常
- ✅ Actor系统通信正常
- ✅ 界面风格保持一致

**测试结果**:
- 主窗口正常显示，无额外窗口
- 所有UI组件功能正常
- 流式响应实时更新
- 系统启动流程稳定

## 优势

1. **用户体验改善**:
   - 单窗口界面，用户交互清晰
   - 组件化设计，界面响应快速

2. **代码维护性**:
   - 模块化组件，易于维护和扩展
   - 清晰的文件结构和职责分离

3. **开发效率**:
   - 组件可重用性高
   - 独立开发和测试

4. **系统稳定性**:
   - 优化的启动流程
   - 完善的错误处理机制

## 后续扩展

1. **组件增强**:
   - 添加更多自定义组件
   - 实现组件间的数据共享

2. **主题系统**:
   - 统一的主题配置
   - 支持深色/浅色主题切换

3. **性能优化**:
   - 延迟加载机制
   - 虚拟化长列表

4. **功能扩展**:
   - 拖拽功能
   - 快捷键支持
   - 可定制化布局

---

*本次重构成功解决了双窗口问题，实现了完整的模块化设计，为后续功能扩展打下了良好基础。* 