import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: workflowSidebar
    
    property alias cardsData: cardsList.model
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
    
    signal cardClicked(string cardId, var cardData)
    signal refreshWorkflow()
    
    color: theme.surface
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 16
        
        // 头部区域
        RowLayout {
            Layout.fillWidth: true
            spacing: 12
            
            Text {
                text: "🌳 计划工作流"
                font.pixelSize: 20
                font.bold: true
                color: theme.text
            }
            
            Item { Layout.fillWidth: true }
            
            // 刷新按钮
            Button {
                Layout.preferredWidth: 32
                Layout.preferredHeight: 32
                
                background: Rectangle {
                    color: parent.hovered ? theme.primary : "transparent"
                    border.color: theme.primary
                    border.width: 1
                    radius: 16
                }
                
                contentItem: Text {
                    text: "🔄"
                    font.pixelSize: 14
                    color: parent.parent.hovered ? "white" : theme.primary
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
                
                onClicked: refreshWorkflow()
            }
        }
        
        // 统计信息
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 80
            color: theme.background
            radius: 8
            border.color: theme.border
            border.width: 1
            
            RowLayout {
                anchors.fill: parent
                anchors.margins: 16
                
                // 总数
                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 4
                    
                    Text {
                        text: getTotalCount()
                        font.pixelSize: 24
                        font.bold: true
                        color: theme.primary
                        horizontalAlignment: Text.AlignHCenter
                    }
                    
                    Text {
                        text: "总任务"
                        font.pixelSize: 12
                        color: theme.textSecondary
                        horizontalAlignment: Text.AlignHCenter
                    }
                }
                
                Rectangle {
                    Layout.preferredWidth: 1
                    Layout.fillHeight: true
                    color: theme.border
                }
                
                // 运行中
                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 4
                    
                    Text {
                        text: getRunningCount()
                        font.pixelSize: 24
                        font.bold: true
                        color: theme.success
                        horizontalAlignment: Text.AlignHCenter
                    }
                    
                    Text {
                        text: "运行中"
                        font.pixelSize: 12
                        color: theme.textSecondary
                        horizontalAlignment: Text.AlignHCenter
                    }
                }
                
                Rectangle {
                    Layout.preferredWidth: 1
                    Layout.fillHeight: true
                    color: theme.border
                }
                
                // 完成
                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 4
                    
                    Text {
                        text: getCompletedCount()
                        font.pixelSize: 24
                        font.bold: true
                        color: theme.accent
                        horizontalAlignment: Text.AlignHCenter
                    }
                    
                    Text {
                        text: "已完成"
                        font.pixelSize: 12
                        color: theme.textSecondary
                        horizontalAlignment: Text.AlignHCenter
                    }
                }
            }
            
            function getTotalCount() {
                return cardsData ? cardsData.length : 0
            }
            
            function getRunningCount() {
                if (!cardsData) return 0
                var count = 0
                for (var i = 0; i < cardsData.length; i++) {
                    if (cardsData[i].status === "running") count++
                }
                return count
            }
            
            function getCompletedCount() {
                if (!cardsData) return 0
                var count = 0
                for (var i = 0; i < cardsData.length; i++) {
                    if (cardsData[i].status === "completed") count++
                }
                return count
            }
        }
        
        // 卡片列表
        ListView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 12
            model: cardsData
            id: cardsList
            
            delegate: Rectangle {
                width: ListView.view.width
                height: cardContent.height + 24
                color: theme.background
                radius: 8
                border.color: theme.border
                border.width: 1
                
                // 悬停效果
                property bool hovered: false
                
                MouseArea {
                    anchors.fill: parent
                    hoverEnabled: true
                    
                    onEntered: parent.hovered = true
                    onExited: parent.hovered = false
                    onClicked: cardClicked(modelData.cardId || "", modelData)
                }
                
                // 悬停时的阴影效果
                Rectangle {
                    anchors.fill: parent
                    color: "transparent"
                    border.color: parent.hovered ? theme.primary : "transparent"
                    border.width: 2
                    radius: 8
                    opacity: parent.hovered ? 0.3 : 0
                    
                    Behavior on opacity {
                        NumberAnimation { duration: 200 }
                    }
                }
                
                ColumnLayout {
                    id: cardContent
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.top: parent.top
                    anchors.margins: 12
                    spacing: 8
                    
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 12
                        
                        // 状态指示器
                        Rectangle {
                            Layout.preferredWidth: 24
                            Layout.preferredHeight: 24
                            color: getStatusColor(modelData.status)
                            radius: 12
                            
                            Text {
                                anchors.centerIn: parent
                                text: getStatusIcon(modelData.status)
                                font.pixelSize: 12
                                color: "white"
                            }
                            
                            function getStatusColor(status) {
                                switch(status) {
                                    case "running": return theme.success
                                    case "completed": return theme.accent
                                    case "error": return theme.error
                                    case "paused": return theme.warning
                                    default: return theme.textSecondary
                                }
                            }
                            
                            function getStatusIcon(status) {
                                switch(status) {
                                    case "running": return "▶"
                                    case "completed": return "✓"
                                    case "error": return "✗"
                                    case "paused": return "⏸"
                                    default: return "⏹"
                                }
                            }
                        }
                        
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 4
                            
                            Text {
                                text: modelData.title || "未命名任务"
                                font.pixelSize: 14
                                font.bold: true
                                color: theme.text
                                elide: Text.ElideRight
                                Layout.fillWidth: true
                            }
                            
                            Text {
                                text: modelData.description || "无描述"
                                font.pixelSize: 12
                                color: theme.textSecondary
                                elide: Text.ElideRight
                                Layout.fillWidth: true
                            }
                        }
                        
                        // 类型标签
                        Rectangle {
                            Layout.preferredHeight: 20
                            Layout.preferredWidth: typeText.width + 12
                            color: getTypeColor(modelData.type)
                            radius: 10
                            
                            Text {
                                id: typeText
                                anchors.centerIn: parent
                                text: modelData.type || "Unknown"
                                font.pixelSize: 10
                                font.bold: true
                                color: "white"
                            }
                            
                            function getTypeColor(type) {
                                switch(type) {
                                    case "Level1": return theme.error
                                    case "Level2": return theme.warning
                                    case "Level3": return theme.success
                                    default: return theme.textSecondary
                                }
                            }
                        }
                    }
                    
                    // 进度条
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 4
                        color: theme.border
                        radius: 2
                        visible: (modelData.progress || 0) > 0
                        
                        Rectangle {
                            width: parent.width * ((modelData.progress || 0) / 100)
                            height: parent.height
                            color: theme.success
                            radius: 2
                            
                            Behavior on width {
                                NumberAnimation { duration: 300 }
                            }
                        }
                    }
                    
                    // 状态文字
                    Text {
                        text: getStatusText(modelData.status, modelData.progress)
                        font.pixelSize: 10
                        color: theme.textSecondary
                        
                        function getStatusText(status, progress) {
                            switch(status) {
                                case "running": return "运行中 " + (progress || 0) + "%"
                                case "completed": return "已完成"
                                case "error": return "执行失败"
                                case "paused": return "已暂停"
                                default: return "等待执行"
                            }
                        }
                    }
                }
            }
        }
    }
} 