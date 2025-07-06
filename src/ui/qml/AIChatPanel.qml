import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Controls.Material 2.15

Rectangle {
    id: root
    
    // 属性定义
    property alias messageText: messageInput.text
    property bool isStreaming: false
    property var chatHistory: []
    
    // 信号定义
    signal messageSent(string message)
    signal streamStarted()
    signal streamChunkReceived(string chunk)
    signal streamFinished()
    signal clearHistory()
    
    // 主题配置
    property var theme: ({
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
    
    color: theme.surface
    radius: 8
    
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
                spacing: 16
                
                Text {
                    text: "🤖 AI 画布"
                    font.pixelSize: 16
                    font.bold: true
                    color: "white"
                }
                
                Item { Layout.fillWidth: true }
                
                // 状态指示器
                Rectangle {
                    width: 8
                    height: 8
                    radius: 4
                    color: isStreaming ? theme.warning : theme.success
                    
                    // 流式响应时的闪烁动画
                    SequentialAnimation on opacity {
                        running: isStreaming
                        loops: Animation.Infinite
                        NumberAnimation { to: 0.3; duration: 500 }
                        NumberAnimation { to: 1.0; duration: 500 }
                    }
                }
                
                Text {
                    text: isStreaming ? "正在输入..." : "就绪"
                    font.pixelSize: 12
                    color: "white"
                }
                
                // 清空历史按钮
                Button {
                    Layout.preferredWidth: 80
                    Layout.preferredHeight: 32
                    text: "清空"
                    
                    background: Rectangle {
                        color: parent.pressed ? Qt.darker(theme.error, 1.2) : 
                               parent.hovered ? Qt.lighter(theme.error, 1.1) : "transparent"
                        border.color: "white"
                        border.width: 1
                        radius: 6
                    }
                    
                    contentItem: Text {
                        text: parent.text
                        color: "white"
                        font.pixelSize: 12
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                    
                    onClicked: clearChatHistory()
                }
            }
        }
        
        // 主画布区域 - 一长条显示所有内容
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: theme.surface
            border.color: theme.border
            border.width: 1
            
            ScrollView {
                id: canvasScrollView
                anchors.fill: parent
                anchors.margins: 8
                clip: true
                
                ScrollBar.vertical.policy: ScrollBar.AlwaysOn
                ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
                
                // 画布内容区域
                Column {
                    id: canvasContent
                    width: canvasScrollView.width - 16
                    spacing: 8
                    
                    Repeater {
                        id: messageRepeater
                        model: ListModel {
                            id: chatModel
                        }
                        
                        // 每个消息项目为一长条
                        Rectangle {
                            width: canvasContent.width
                            height: Math.max(messageContent.height + 24, 60)
                            
                            // 用户消息和AI消息用不同的背景色区分
                            color: model.isUser ? 
                                   Qt.rgba(0.26, 0.22, 0.78, 0.1) : // 用户消息浅蓝色背景
                                   theme.background
                            
                            border.color: model.isUser ? theme.primary : theme.border
                            border.width: 1
                            radius: 8
                            
                            RowLayout {
                                anchors.fill: parent
                                anchors.margins: 12
                                spacing: 12
                                
                                // 角色标识
                                Rectangle {
                                    Layout.preferredWidth: 40
                                    Layout.preferredHeight: 40
                                    Layout.alignment: Qt.AlignTop
                                    
                                    color: model.isUser ? theme.primary : theme.accent
                                    radius: 20
                                    
                                    Text {
                                        anchors.centerIn: parent
                                        text: model.isUser ? "👤" : "🤖"
                                        font.pixelSize: 16
                                        color: "white"
                                    }
                                }
                                
                                // 消息内容区域
                                ColumnLayout {
                                    Layout.fillWidth: true
                                    spacing: 4
                                    
                                    // 消息文本
                                    TextEdit {
                                        id: messageContent
                                        Layout.fillWidth: true
                                        Layout.preferredWidth: canvasContent.width - 80
                                        
                                        text: model.content || ""
                                        color: theme.text
                                        font.pixelSize: 14
                                        wrapMode: TextEdit.Wrap
                                        textFormat: TextEdit.PlainText
                                        selectByMouse: true
                                        readOnly: true
                                    }
                                    
                                    // 时间戳
                                    Text {
                                        text: model.timestamp ? Qt.formatDateTime(model.timestamp, "hh:mm:ss") : ""
                                        color: theme.textSecondary
                                        font.pixelSize: 10
                                    }
                                }
                            }
                        }
                    }
                    
                    // 流式响应显示区
                    Rectangle {
                        id: streamingMessage
                        width: canvasContent.width
                        height: visible ? Math.max(streamingContent.height + 24, 60) : 0
                        visible: isStreaming
                        
                        color: theme.background
                        border.color: theme.border
                        border.width: 1
                        radius: 8
                        
                        property string streamContent: ""
                        
                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: 12
                            spacing: 12
                            
                            // AI头像
                            Rectangle {
                                Layout.preferredWidth: 40
                                Layout.preferredHeight: 40
                                Layout.alignment: Qt.AlignTop
                                
                                color: theme.accent
                                radius: 20
                                
                                Text {
                                    anchors.centerIn: parent
                                    text: "🤖"
                                    font.pixelSize: 16
                                    color: "white"
                                }
                            }
                            
                            // 流式消息内容
                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 4
                                
                                TextEdit {
                                    id: streamingContent
                                    Layout.fillWidth: true
                                    Layout.preferredWidth: canvasContent.width - 80
                                    
                                    text: streamingMessage.streamContent
                                    color: theme.text
                                    font.pixelSize: 14
                                    wrapMode: TextEdit.Wrap
                                    textFormat: TextEdit.PlainText
                                    selectByMouse: true
                                    readOnly: true
                                }
                                
                                // 打字指示器
                                Text {
                                    text: "●●●"
                                    color: theme.textSecondary
                                    font.pixelSize: 12
                                    
                                    SequentialAnimation on opacity {
                                        running: isStreaming
                                        loops: Animation.Infinite
                                        NumberAnimation { to: 0.3; duration: 600 }
                                        NumberAnimation { to: 1.0; duration: 600 }
                                    }
                                }
                            }
                        }
                    }
                    
                    // 添加底部间距，确保最后一条消息不会被输入框遮挡
                    Item {
                        width: parent.width
                        height: 20
                    }
                }
            }
            
            // 自动滚动到底部按钮
            Button {
                anchors.right: parent.right
                anchors.bottom: parent.bottom
                anchors.margins: 16
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
                
                onClicked: scrollToBottom()
            }
        }
        
        // 输入区域
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
                    
                    Rectangle {
                        anchors.fill: parent
                        color: theme.background
                        border.color: messageInput.focus ? theme.primary : theme.border
                        border.width: messageInput.focus ? 2 : 1
                        radius: 6
                    }
                    
                    TextArea {
                        id: messageInput
                        placeholderText: isStreaming ? "AI正在回复中..." : "在画布上输入消息..."
                        font.pixelSize: 14
                        color: theme.text
                        wrapMode: TextArea.Wrap
                        selectByMouse: true
                        enabled: !isStreaming
                        
                        background: Rectangle {
                            color: "transparent"
                        }
                        
                        Keys.onPressed: function(event) {
                            if (event.key === Qt.Key_Return && !(event.modifiers & Qt.ShiftModifier)) {
                                sendMessage()
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
                    
                    enabled: !isStreaming && messageInput.text.trim().length > 0
                    onClicked: sendMessage()
                }
            }
        }
    }
    
    // 🔧 修复AI响应解析的函数
    function parseAIResponse(rawResponse) {
        try {
            // 尝试解析JSON
            var jsonResponse = JSON.parse(rawResponse)
            if (jsonResponse.content) {
                return jsonResponse.content
            }
        } catch (e) {
            // 如果不是JSON，直接返回原始内容
            console.log("AI响应不是JSON格式，直接使用原始内容")
        }
        return rawResponse
    }
    
    // 发送消息
    function sendMessage() {
        var message = messageInput.text.trim()
        if (message.length === 0) return
        
        console.log("发送消息:", message)
        
        // 添加用户消息到历史
        addMessage(true, message)
        
        // 清空输入框
        messageInput.text = ""
        
        // 发送消息信号
        root.messageSent(message)
        
        // 自动滚动到底部
        scrollToBottom()
    }
    
    // 添加消息到历史
    function addMessage(isUser, content) {
        var messageData = {
            "isUser": isUser,
            "content": content,
            "timestamp": new Date()
        }
        
        console.log("添加消息:", isUser ? "用户" : "AI", content)
        
        chatModel.append(messageData)
        chatHistory.push(messageData)
        
        // 延迟滚动，确保内容已经渲染
        Qt.callLater(scrollToBottom)
    }
    
    // 开始流式响应
    function startStreamResponse() {
        isStreaming = true
        root.streamStarted()
        streamingMessage.streamContent = ""
        Qt.callLater(scrollToBottom)
    }
    
    // 追加流式响应内容
    function appendStreamChunk(chunk) {
        if (isStreaming) {
            // 解析AI响应中的JSON格式
            var parsedChunk = parseAIResponse(chunk)
            streamingMessage.streamContent += parsedChunk
            
            // 延迟滚动到底部
            Qt.callLater(scrollToBottom)
        }
    }
    
    // 完成流式响应
    function finishStreamResponse() {
        if (isStreaming) {
            // 解析最终的AI响应
            var finalContent = parseAIResponse(streamingMessage.streamContent)
            
            // 将流式消息添加到历史
            addMessage(false, finalContent)
            
            isStreaming = false
            root.streamFinished()
            Qt.callLater(scrollToBottom)
        }
    }
    
    // 清空对话历史
    function clearChatHistory() {
        chatModel.clear()
        chatHistory = []
        root.clearHistory()
    }
    
    // 滚动到底部
    function scrollToBottom() {
        if (canvasScrollView.ScrollBar.vertical) {
            canvasScrollView.ScrollBar.vertical.position = 1.0
        }
    }
    
    // 🔥 新增：设置流式状态方法
    function setStreamingState(streaming) {
        isStreaming = streaming
        console.log("AI聊天面板设置流式状态:", streaming)
    }
    
    // 🔥 新增：维持滚动位置方法（不自动滚动）
    function maintainScrollPosition() {
        // 什么都不做，保持当前滚动位置
        console.log("AI聊天面板维持当前滚动位置")
    }
    
    // 🔥 新增：回到顶部方法
    function scrollToTop() {
        if (canvasScrollView.ScrollBar.vertical) {
            canvasScrollView.ScrollBar.vertical.position = 0.0
        }
    }
    
    // 初始化欢迎消息
    Component.onCompleted: {
        addMessage(false, "🎉 欢迎使用 Pank Ins AI控制示波器系统!")
        addMessage(false, "💡 我可以帮助您制定测试计划、分析数据和控制设备。有什么我可以帮助您的吗？")
    }
} 