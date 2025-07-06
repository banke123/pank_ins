import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: aiChatPanel
    objectName: "aiChatPanel"  // 🔥 新增：设置objectName以便Python代码查找
    
    property alias messagesData: messagesList.model
    property bool isStreaming: false  // 🔥 新增：流式响应状态
    property real lastContentHeight: 0  // 🔥 新增：记录上次内容高度
    property var theme: parent.theme || ({
        primary: "#4f46e5",
        secondary: "#7c3aed", 
        accent: "#06b6d4",
        success: "#10b981",
        warning: "#f59e0b",
        error: "#ef4444",
        background: "#ffffff",
        surface: "#f8fafc",
        text: "#111827",
        textSecondary: "#6b7280",
        border: "#e5e7eb"
    })
    
    signal sendMessage(string message)
    
    color: theme.background
    
    ColumnLayout {
        anchors.fill: parent
        spacing: 0
        
        // AI对话头部
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 50
            color: theme.primary
            
            gradient: Gradient {
                GradientStop { position: 0.0; color: theme.primary }
                GradientStop { position: 1.0; color: theme.secondary }
            }
            
            RowLayout {
                anchors.fill: parent
                anchors.margins: 16
                
                Text {
                    text: "🎨 AI 对话画布"
                    font.pixelSize: 16
                    font.bold: true
                    color: "white"
                }
                
                Item { Layout.fillWidth: true }
                
                // 🔥 新增：流式响应状态指示器
                Rectangle {
                    width: 8
                    height: 8
                    radius: 4
                    color: isStreaming ? "#f59e0b" : "#10b981"
                    
                    SequentialAnimation on opacity {
                        running: isStreaming
                        loops: Animation.Infinite
                        PropertyAnimation { to: 0.3; duration: 500 }
                        PropertyAnimation { to: 1.0; duration: 500 }
                    }
                }
                
                Text {
                    text: isStreaming ? "思考中..." : "就绪"
                    font.pixelSize: 12
                    color: "white"
                    opacity: 0.9
                }
            }
        }
        
        // 🔥 主要修改：画布区域 - 长条布局，不自动滚动
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: theme.surface
            border.color: theme.border
            border.width: 1
            
            // 🔥 画布滚动视图 - 修改滚动行为
            ScrollView {
                id: canvasScrollView
                anchors.fill: parent
                anchors.margins: 8
                clip: true
                
                // 🔥 关键：禁用自动滚动到底部的行为
                ScrollBar.vertical.policy: ScrollBar.AlwaysOn
                
                // 🔥 画布内容区域 - 长条布局
                Rectangle {
                    id: canvasContentContainer
                    width: canvasScrollView.width - 16
                    height: Math.max(canvasContent.height, canvasScrollView.height)
                    color: "transparent"
                    
                    Column {
                        id: canvasContent
                        width: parent.width
                        spacing: 16  // 🔥 增加间距，让画布看起来更舒适
                        
                        // 🔥 添加顶部间距
                        Item {
                            width: parent.width
                            height: 20
                        }
                        
                        Repeater {
                            id: messagesList
                            model: messagesData
                            
                            // 🔥 每个消息为一个长条画布项
                            Rectangle {
                                width: canvasContent.width
                                height: messageContent.height + 32
                                
                                // 🔥 画布样式：用户消息和AI消息用不同的风格
                                color: modelData.isUser ? 
                                       Qt.rgba(0.31, 0.27, 0.90, 0.08) :  // 用户消息：淡紫色背景
                                       Qt.rgba(0.06, 0.71, 0.83, 0.08)    // AI消息：淡蓝色背景
                                
                                border.color: modelData.isUser ? 
                                            Qt.rgba(0.31, 0.27, 0.90, 0.3) : 
                                            Qt.rgba(0.06, 0.71, 0.83, 0.3)
                                border.width: 1
                                radius: 12
                                
                                // 🔥 画布条目内容
                                Rectangle {
                                    id: messageContent
                                    anchors.left: parent.left
                                    anchors.right: parent.right
                                    anchors.top: parent.top
                                    anchors.margins: 16
                                    height: messageLayout.height
                                    color: "transparent"
                                    
                                    ColumnLayout {
                                        id: messageLayout
                                        anchors.fill: parent
                                        spacing: 8
                                        
                                        // 🔥 消息头部：角色标识 + 时间戳
                                        RowLayout {
                                            Layout.fillWidth: true
                                            
                                            // 角色标识
                                            Rectangle {
                                                Layout.preferredWidth: 40
                                                Layout.preferredHeight: 40
                                                
                                                color: modelData.isUser ? theme.primary : theme.accent
                                                radius: 20
                                                
                                                Text {
                                                    anchors.centerIn: parent
                                                    text: modelData.isUser ? "👤" : "🤖"
                                                    font.pixelSize: 16
                                                }
                                            }
                                            
                                            // 角色名称
                                            Text {
                                                text: modelData.isUser ? "用户" : "AI助手"
                                                font.pixelSize: 14
                                                font.bold: true
                                                color: modelData.isUser ? theme.primary : theme.accent
                                            }
                                            
                                            Item { Layout.fillWidth: true }
                                            
                                            // 时间戳
                                            Text {
                                                text: modelData.timestamp || ""
                                                font.pixelSize: 11
                                                color: theme.textSecondary
                                            }
                                        }
                                        
                                        // 🔥 消息内容区域 - 可以很长的画布文本
                                        Rectangle {
                                            Layout.fillWidth: true
                                            Layout.preferredHeight: messageTextEdit.height + 16
                                            
                                            color: modelData.isUser ? 
                                                   Qt.rgba(0.31, 0.27, 0.90, 0.05) : 
                                                   Qt.rgba(0.06, 0.71, 0.83, 0.05)
                                            radius: 8
                                            
                                            TextEdit {
                                                id: messageTextEdit
                                                anchors.left: parent.left
                                                anchors.right: parent.right
                                                anchors.top: parent.top
                                                anchors.margins: 8
                                                
                                                text: modelData.content || ""
                                                color: theme.text
                                                font.pixelSize: 14
                                                font.family: "Microsoft YaHei"
                                                wrapMode: TextEdit.Wrap
                                                textFormat: TextEdit.PlainText
                                                selectByMouse: true
                                                readOnly: true
                                                
                                                // 🔥 自动调整高度以适应内容
                                                height: contentHeight
                                            }
                                        }
                                    }
                                }
                            }
                        }
                        
                        // 🔥 底部间距，确保最后一条消息有足够的空间
                        Item {
                            width: parent.width
                            height: 40
                        }
                    }
                }
            }
            
            // 🔥 画布导航按钮
            Row {
                anchors.right: parent.right
                anchors.bottom: parent.bottom
                anchors.margins: 16
                spacing: 8
                
                // 回到顶部按钮
                Button {
                    width: 40
                    height: 40
                    visible: canvasScrollView.ScrollBar.vertical.position > 0.1
                    
                    background: Rectangle {
                        color: theme.accent
                        radius: 20
                        opacity: 0.8
                    }
                    
                    contentItem: Text {
                        text: "↑"
                        color: "white"
                        font.pixelSize: 16
                        font.bold: true
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                    
                    onClicked: {
                        canvasScrollView.ScrollBar.vertical.position = 0.0
                    }
                }
                
                // 🔥 修改：滚动到底部按钮（手动控制）
                Button {
                    width: 40
                    height: 40
                    visible: canvasScrollView.ScrollBar.vertical.position < 0.9
                    
                    background: Rectangle {
                        color: theme.primary
                        radius: 20
                        opacity: 0.8
                    }
                    
                    contentItem: Text {
                        text: "↓"
                        color: "white"
                        font.pixelSize: 16
                        font.bold: true
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                    
                    onClicked: {
                        canvasScrollView.ScrollBar.vertical.position = 1.0
                    }
                }
            }
        }
        
        // 🔥 输入区域 - 保持不变但调整样式
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 80
            color: theme.surface
            border.color: theme.border
            border.width: 1
            
            RowLayout {
                anchors.fill: parent
                anchors.margins: 12
                spacing: 12
                
                ScrollView {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    
                    background: Rectangle {
                        color: theme.background
                        border.color: messageInputArea.focus ? theme.primary : theme.border
                        border.width: messageInputArea.focus ? 2 : 1
                        radius: 6
                    }
                    
                    TextArea {
                        id: messageInputArea
                        placeholderText: "在画布上输入消息... (Enter发送，Shift+Enter换行)"
                        font.pixelSize: 14
                        font.family: "Microsoft YaHei"
                        color: theme.text
                        wrapMode: TextArea.Wrap
                        selectByMouse: true
                        
                        background: Rectangle {
                            color: "transparent"
                        }
                        
                        Keys.onPressed: function(event) {
                            if (event.key === Qt.Key_Return && !(event.modifiers & Qt.ShiftModifier)) {
                                sendMessageInternal()
                                event.accepted = true
                            }
                        }
                    }
                }
                
                Button {
                    Layout.preferredWidth: 70
                    Layout.preferredHeight: 36
                    text: "发送"
                    
                    background: Rectangle {
                        color: parent.enabled ? theme.primary : theme.textSecondary
                        radius: 6
                    }
                    
                    contentItem: Text {
                        text: parent.text
                        color: "white"
                        font.bold: true
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                    
                    enabled: messageInputArea.text.trim().length > 0
                    onClicked: sendMessageInternal()
                }
            }
        }
    }
    
    // 🔥 修改：发送消息函数 - 不自动滚动到底部
    function sendMessageInternal() {
        var message = messageInputArea.text.trim()
        if (message.length > 0) {
            sendMessage(message)
            messageInputArea.text = ""
            
            // 🔥 关键修改：发送消息后不自动滚动到底部
            // 保持当前的滚动位置，让用户手动控制
        }
    }
    
    // 🔥 修改：监听数据变化 - 不自动滚动到底部
    onMessagesDataChanged: {
        // 🔥 关键修改：移除自动滚动到底部的逻辑
        // 让用户手动控制滚动位置，特别是在流式响应时
        
        // 记录当前内容高度变化
        lastContentHeight = canvasContent.height
    }
    
    // 🔥 新增：流式响应状态管理
    function setStreamingState(streaming) {
        isStreaming = streaming
    }
    
    // 🔥 新增：手动滚动到底部的函数（供外部调用）
    function scrollToBottom() {
        canvasScrollView.ScrollBar.vertical.position = 1.0
    }
    
    // 🔥 新增：保持当前滚动位置的函数
    function maintainScrollPosition() {
        // 在流式响应时，保持当前的滚动位置
        // 不进行任何自动滚动
    }
    
    // 🔥 新增：流式响应相关方法
    function startStreamResponse() {
        isStreaming = true
    }
    
    function appendStreamChunk(chunk) {
        // 这里可以添加处理流式数据片段的逻辑
        // 目前保持滚动位置不变
    }
    
    function finishStreamResponse() {
        isStreaming = false
    }
} 