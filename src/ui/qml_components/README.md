# QML 组件模块

这个文件夹包含了主窗口的模块化QML组件，用于构建AI示波器控制系统的用户界面。

## 组件结构

### 1. AIChatPanel.qml
AI对话面板组件，包含：
- 对话消息列表显示
- 消息输入区域
- 自动滚动到最新消息
- 流式响应支持

**属性：**
- `messagesData`: 消息数据模型
- `theme`: 主题配置对象

**信号：**
- `sendMessage(string message)`: 发送消息信号

### 2. SystemLogPanel.qml
系统日志面板组件，包含：
- 日志列表显示
- 按日志级别分色显示
- 清空日志功能
- 自动滚动到最新日志

**属性：**
- `logsData`: 日志数据模型
- `theme`: 主题配置对象

**信号：**
- `clearLogs()`: 清空日志信号

### 3. WorkflowSidebar.qml
工作流侧边栏组件，包含：
- 计划卡片列表
- 任务统计信息
- 卡片状态指示器
- 进度条显示
- 刷新功能

**属性：**
- `cardsData`: 卡片数据模型
- `theme`: 主题配置对象

**信号：**
- `cardClicked(string cardId, var cardData)`: 卡片点击信号
- `refreshWorkflow()`: 刷新工作流信号

### 4. MainWorkArea.qml
主工作区组件，包含：
- 多视图切换（仪表板、示波器、分析）
- 工具栏功能
- 示波器控制面板
- 数据分析工具

**属性：**
- `theme`: 主题配置对象
- `currentView`: 当前视图模式

**信号：**
- `viewChanged(string view)`: 视图切换信号
- `openFileDialog()`: 打开文件对话框信号
- `saveCurrentWork()`: 保存当前工作信号
- `exportResults()`: 导出结果信号

## 主题系统

所有组件都使用统一的主题系统，主题对象包含以下颜色定义：

```javascript
theme: {
    primary: "#4f46e5",      // 主色调
    secondary: "#7c3aed",    // 次要色调
    accent: "#06b6d4",       // 强调色
    success: "#10b981",      // 成功色
    warning: "#f59e0b",      // 警告色
    error: "#ef4444",        // 错误色
    background: "#ffffff",   // 背景色
    surface: "#f8fafc",      // 表面色
    text: "#111827",         // 文本色
    textSecondary: "#6b7280", // 次要文本色
    border: "#e5e7eb"        // 边框色
}
```

## 信号通信

组件通过信号与Python后端通信：

1. **用户操作** → **组件信号** → **主窗口QML** → **Python桥接对象** → **业务逻辑**

2. **业务逻辑** → **Python桥接对象** → **数据模型更新** → **QML组件自动刷新**

## 使用方式

在主QML文件中导入并使用组件：

```qml
import "qml_components" as Components

Components.AIChatPanel {
    messagesData: mainBridge.messagesData
    theme: mainWindow.theme
    
    onSendMessage: function(message) {
        // 处理发送消息
        mainBridge.sendMessage(message)
    }
}
```

## 开发指南

### 添加新组件

1. 在此目录创建新的.qml文件
2. 在qmldir文件中注册新组件
3. 在主QML文件中导入并使用
4. 在Python桥接对象中添加相应的数据属性和方法

### 修改现有组件

1. 直接编辑对应的.qml文件
2. 确保属性和信号定义与主窗口的使用方式匹配
3. 测试组件的独立性和重用性

### 主题定制

1. 在主窗口中修改theme对象的颜色值
2. 所有组件会自动应用新的主题色彩
3. 组件内部使用theme属性来引用颜色

## 注意事项

- 所有组件都应该保持独立性，不依赖外部特定实现
- 使用属性绑定而不是硬编码的数据
- 通过信号进行组件间通信
- 保持一致的命名规范和代码风格
- 确保组件的响应式设计适配不同窗口大小 