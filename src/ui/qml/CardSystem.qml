import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

ApplicationWindow {
    id: root
    title: "AI示波器控制 - 动态卡片系统"
    width: 1400
    height: 900
    visible: true
    
    // 主题配置
    property var theme: ({
        "colors": {
            "background": "#f8fafc",
            "surface": "#ffffff",
            "primary": "#3b82f6",
            "secondary": "#10b981",
            "accent": "#f59e0b",
            "text": "#1f2937",
            "textSecondary": "#6b7280",
            "border": "#e5e7eb",
            "success": "#10b981",
            "warning": "#f59e0b",
            "error": "#ef4444"
        },
        "spacing": {
            "xs": 4,
            "sm": 8,
            "md": 16,
            "lg": 24,
            "xl": 32
        },
        "borderRadius": {
            "sm": 6,
            "md": 12,
            "lg": 16
        },
        "shadows": {
            "sm": "0 1px 3px rgba(0,0,0,0.12)",
            "md": "0 4px 6px rgba(0,0,0,0.1)",
            "lg": "0 10px 15px rgba(0,0,0,0.1)"
        }
    })
    
    // 数据模型
    property var cardData: []
    
    // 信号定义
    signal cardClicked(var cardData)
    signal actionTriggered(string action, var cardData)
    
    Rectangle {
        anchors.fill: parent
        color: theme.colors.background
        
        RowLayout {
            anchors.fill: parent
            anchors.margins: theme.spacing.md
            spacing: theme.spacing.lg
            
            // 左侧卡片区域
            Rectangle {
                Layout.fillHeight: true
                Layout.preferredWidth: 800
                color: theme.colors.surface
                radius: theme.borderRadius.lg
                border.color: theme.colors.border
                border.width: 1
                
                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: theme.spacing.lg
                    spacing: theme.spacing.md
                    
                    // 控制按钮区域
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: theme.spacing.sm
                        
                        Button {
                            text: "添加Level3计划"
                            onClicked: {
                                if (cardBridge) {
                                    cardBridge.addLevel3Plan()
                                }
                            }
                            
                            background: Rectangle {
                                color: parent.pressed ? Qt.darker(theme.colors.primary, 1.2) : 
                                       parent.hovered ? Qt.lighter(theme.colors.primary, 1.1) : theme.colors.primary
                                radius: theme.borderRadius.sm
                                
                                Behavior on color {
                                    ColorAnimation { duration: 150 }
                                }
                            }
                            
                            contentItem: Text {
                                text: parent.text
                                color: "white"
                                font.pixelSize: 12
                                font.bold: true
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                            }
                        }
                        
                        Button {
                            text: "执行当前任务"
                            onClicked: executeCurrentTask()
                            
                            background: Rectangle {
                                color: parent.pressed ? Qt.darker(theme.colors.secondary, 1.2) : 
                                       parent.hovered ? Qt.lighter(theme.colors.secondary, 1.1) : theme.colors.secondary
                                radius: theme.borderRadius.sm
                                
                                Behavior on color {
                                    ColorAnimation { duration: 150 }
                                }
                            }
                            
                            contentItem: Text {
                                text: parent.text
                                color: "white"
                                font.pixelSize: 12
                                font.bold: true
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                            }
                        }
                        
                        Button {
                            text: "清空重置"
                            onClicked: {
                                if (cardBridge) {
                                    cardBridge.clearAllCards()
                                }
                            }
                            
                            background: Rectangle {
                                color: parent.pressed ? Qt.darker(theme.colors.error, 1.2) : 
                                       parent.hovered ? Qt.lighter(theme.colors.error, 1.1) : theme.colors.error
                                radius: theme.borderRadius.sm
                                
                                Behavior on color {
                                    ColorAnimation { duration: 150 }
                                }
                            }
                            
                            contentItem: Text {
                                text: parent.text
                                color: "white"
                                font.pixelSize: 12
                                font.bold: true
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                            }
                        }
                        
                        Item { Layout.fillWidth: true }
                    }
                    
                    // 状态显示
                    Rectangle {
                        Layout.fillWidth: true
                        height: 40
                        color: "#f0f9ff"
                        radius: theme.borderRadius.sm
                        border.color: theme.colors.primary
                        border.width: 1
                        
                        Text {
                            id: statusText
                            anchors.centerIn: parent
                            text: "状态: 等待开始"
                            color: theme.colors.primary
                            font.pixelSize: 14
                            font.bold: true
                        }
                    }
                    
                    // 卡片容器
                    CardContainer {
                        id: cardContainer
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        theme: root.theme
                        
                        onCardClicked: function(cardData) {
                            root.cardClicked(cardData)
                        }
                        
                        onActionTriggered: function(action, cardData) {
                            root.actionTriggered(action, cardData)
                            
                            // 转发到Python桥接对象
                            if (cardBridge && cardData.id) {
                                cardBridge.executeCard(cardData.id, action)
                            }
                        }
                    }
                }
            }
            
            // 右侧日志区域
            Rectangle {
                Layout.fillHeight: true
                Layout.preferredWidth: 580
                color: theme.colors.surface
                radius: theme.borderRadius.lg
                border.color: theme.colors.border
                border.width: 1
                
                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: theme.spacing.lg
                    spacing: theme.spacing.md
                    
                    Text {
                        text: "流程日志"
                        color: theme.colors.text
                        font.pixelSize: 16
                        font.bold: true
                    }
                    
                    ScrollView {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        
                        TextArea {
                            id: logArea
                            readOnly: true
                            wrapMode: TextArea.Wrap
                            selectByMouse: true
                            
                            background: Rectangle {
                                color: "#1e1e1e"
                                radius: theme.borderRadius.sm
                                border.color: "#404040"
                                border.width: 1
                            }
                            
                            color: "#d4d4d4"
                            font.family: "Consolas, Monaco, monospace"
                            font.pixelSize: 11
                        }
                    }
                }
            }
        }
    }
    
    // 连接Python桥接对象的信号
    Connections {
        target: cardBridge
        
        function onCardAdded(cardData) {
            try {
                var card = JSON.parse(cardData)
                cardContainer.addCard(card)
                logMessage("添加卡片: " + (card["计划名"] || card["任务名"] || "未知"))
                statusText.text = "状态: 已添加新卡片"
            } catch (e) {
                logMessage("错误: 解析卡片数据失败 - " + e.toString())
            }
        }
        
        function onCardUpdated(cardId, updateData) {
            try {
                var card = JSON.parse(updateData)
                cardContainer.updateCard(cardId, card)
                logMessage("更新卡片: " + cardId)
            } catch (e) {
                logMessage("错误: 更新卡片数据失败 - " + e.toString())
            }
        }
        
        function onCardRemoved(cardId) {
            cardContainer.removeCard(cardId)
            logMessage("删除卡片: " + cardId)
        }
        
        function onSystemCleared() {
            cardContainer.clearAll()
            logArea.text = ""
            statusText.text = "状态: 系统已重置"
            logMessage("系统已重置，准备新的演示")
        }
        
        function onLogMessageAdded(message) {
            logMessage(message)
        }
    }
    
    // JavaScript 函数
    function executeCurrentTask() {
        // 查找当前可执行的任务
        var currentCard = cardContainer.findExecutableCard()
        if (currentCard && cardBridge) {
            cardBridge.executeCard(currentCard.id, "execute")
        } else {
            logMessage("没有找到可执行的任务")
            statusText.text = "状态: 没有可执行的任务"
        }
    }
    
    function logMessage(message) {
        var timestamp = Qt.formatDateTime(new Date(), "[hh:mm:ss]")
        logArea.text += timestamp + " " + message + "\n"
        logArea.cursorPosition = logArea.length
    }
    
    Component.onCompleted: {
        logMessage("QML动态卡片系统初始化完成")
        if (cardBridge) {
            logMessage("Python桥接对象连接成功")
        } else {
            logMessage("警告: Python桥接对象未连接")
        }
    }
} 