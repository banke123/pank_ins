
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Controls.Material 2.15

Rectangle {
    id: mainWindow
    
    Material.theme: Material.Dark
    Material.accent: Material.Blue
    
    color: Material.color(Material.Grey, Material.Shade950)
    
    // 主布局
    RowLayout {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 10
        
        // 左侧：工作流程树状图
        WorkflowTreeView {
            id: workflowTree
            Layout.fillHeight: true
            Layout.preferredWidth: 300
            Layout.minimumWidth: 250
            
            onItemClicked: function(itemData) {
                console.log("工作流项目点击:", itemData.name)
            }
            
            onItemDoubleClicked: function(itemData) {
                console.log("工作流项目双击:", itemData.name)
            }
        }
        
        // 中间：主工作区域
        ColumnLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 10
            
            // 上部分：主工作区
            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                color: Material.color(Material.Grey, Material.Shade900)
                radius: 8
                
                Column {
                    anchors.fill: parent
                    anchors.margins: 10
                    spacing: 10
                    
                    Label {
                        text: "主工作区域"
                        font.pixelSize: 18
                        font.bold: true
                        color: Material.color(Material.Blue)
                    }
                    
                    TabBar {
                        id: workAreaTabBar
                        width: parent.width
                        
                        TabButton {
                            text: "任务卡片"
                        }
                        TabButton {
                            text: "数据可视化"
                        }
                        TabButton {
                            text: "测试结果"
                        }
                    }
                    
                    StackLayout {
                        width: parent.width
                        height: parent.height - 80
                        currentIndex: workAreaTabBar.currentIndex
                        
                        // 任务卡片页面
                        Rectangle {
                            color: "transparent"
                            Label {
                                anchors.centerIn: parent
                                text: "任务卡片区域\n(开发中)"
                                horizontalAlignment: Text.AlignHCenter
                                color: Material.color(Material.Grey)
                            }
                        }
                        
                        // 数据可视化页面
                        Rectangle {
                            color: "transparent"
                            Label {
                                anchors.centerIn: parent
                                text: "数据可视化区域\n(开发中)"
                                horizontalAlignment: Text.AlignHCenter
                                color: Material.color(Material.Grey)
                            }
                        }
                        
                        // 测试结果页面
                        Rectangle {
                            color: "transparent"
                            Label {
                                anchors.centerIn: parent
                                text: "测试结果区域\n(开发中)"
                                horizontalAlignment: Text.AlignHCenter
                                color: Material.color(Material.Grey)
                            }
                        }
                    }
                }
            }
            
            // 下部分：日志显示区
            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 200
                Layout.minimumHeight: 150
                color: Material.color(Material.Grey, Material.Shade900)
                radius: 8
                
                Column {
                    anchors.fill: parent
                    anchors.margins: 10
                    spacing: 10
                    
                    Label {
                        text: "系统日志"
                        font.pixelSize: 16
                        font.bold: true
                        color: Material.color(Material.Blue)
                    }
                    
                    ScrollView {
                        width: parent.width
                        height: parent.height - 40
                        
                        TextArea {
                            id: logArea
                            readOnly: true
                            wrapMode: TextArea.Wrap
                            color: Material.color(Material.Green)
                            font.family: "Consolas, Monaco, monospace"
                            font.pixelSize: 12
                            
                            // 连接到日志信号
                            Connections {
                                target: mainWindowBridge
                                function onLogMessageReceived(level, message) {
                                    var timestamp = new Date().toLocaleTimeString()
                                    logArea.append("[" + timestamp + "] " + level + ": " + message)
                                }
                            }
                        }
                    }
                }
            }
        }
        
        // 右侧：AI对话区域
        AIChatPanel {
            id: aiChatPanel
            Layout.fillHeight: true
            Layout.preferredWidth: 400
            Layout.minimumWidth: 350
            
            onMessageSent: function(message) {
                console.log("用户发送消息:", message)
                mainWindowBridge.userMessageSent(message)
            }
            
            // 连接流式响应信号
            Connections {
                target: mainWindowBridge
                function onStreamStarted() {
                    aiChatPanel.startStreamResponse()
                }
                function onStreamChunkReceived(chunk) {
                    aiChatPanel.appendStreamChunk(chunk)
                }
                function onStreamFinished() {
                    aiChatPanel.finishStreamResponse()
                }
            }
        }
    }
    
    // 初始化时添加欢迎日志
    Component.onCompleted: {
        logArea.append("[" + new Date().toLocaleTimeString() + "] INFO: 系统启动完成")
        logArea.append("[" + new Date().toLocaleTimeString() + "] INFO: 所有模块加载成功")
    }
    
    // 🔥 新增：AI聊天画布流式状态管理方法
    function setAiChatStreamingState(streaming) {
        if (aiChatPanel) {
            aiChatPanel.setStreamingState(streaming)
            console.log("设置AI聊天画布流式状态:", streaming)
        } else {
            console.log("AI聊天面板未找到")
        }
    }
    
    function maintainAiChatScrollPosition() {
        if (aiChatPanel) {
            aiChatPanel.maintainScrollPosition()
            console.log("维持AI聊天画布滚动位置")
        } else {
            console.log("AI聊天面板未找到")
        }
    }
    
    function scrollAiChatToBottom() {
        if (aiChatPanel) {
            aiChatPanel.scrollToBottom()
            console.log("滚动AI聊天画布到底部")
        } else {
            console.log("AI聊天面板未找到")
        }
    }
}
