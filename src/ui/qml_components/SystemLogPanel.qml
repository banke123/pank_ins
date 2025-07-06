import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: systemLogPanel
    
    property alias logsData: logsList.model
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
    
    color: theme.surface
    
    ColumnLayout {
        anchors.fill: parent
        spacing: 0
        
        // 日志头部
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 40
            color: theme.surface
            border.color: theme.border
            border.width: 1
            
            RowLayout {
                anchors.fill: parent
                anchors.margins: 12
                
                Text {
                    text: "📝 系统日志"
                    font.pixelSize: 14
                    font.bold: true
                    color: theme.text
                }
                
                Item { Layout.fillWidth: true }
                
                // 清空按钮
                Button {
                    Layout.preferredWidth: 60
                    Layout.preferredHeight: 24
                    text: "清空"
                    
                    background: Rectangle {
                        color: parent.hovered ? theme.error : "transparent"
                        border.color: theme.error
                        border.width: 1
                        radius: 4
                    }
                    
                    contentItem: Text {
                        text: parent.text
                        color: parent.hovered ? "white" : theme.error
                        font.pixelSize: 10
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                    
                    onClicked: clearLogs()
                }
            }
        }
        
        // 日志列表
        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            
            ListView {
                id: logsList
                spacing: 2
                
                // 自动滚动到底部
                onCountChanged: {
                    Qt.callLater(function() {
                        logsList.positionViewAtEnd()
                    })
                }
                
                delegate: Rectangle {
                    width: logsList.width
                    height: logText.height + 8
                    color: getLogLevelColor(modelData.level)
                    
                    function getLogLevelColor(level) {
                        switch(level) {
                            case "ERROR": return "#fef2f2"
                            case "WARNING": return "#fffbeb"
                            case "INFO": return "#f0f9ff"
                            case "DEBUG": return "#f9fafb"
                            default: return theme.background
                        }
                    }
                    
                    Text {
                        id: logText
                        anchors.left: parent.left
                        anchors.right: parent.right
                        anchors.verticalCenter: parent.verticalCenter
                        anchors.margins: 8
                        
                        text: "[" + modelData.timestamp + "] " + modelData.level + ": " + modelData.message
                        font.pixelSize: 11
                        font.family: "Consolas, Monaco, 'Lucida Console', monospace"
                        color: getLogTextColor(modelData.level)
                        wrapMode: Text.Wrap
                        
                        function getLogTextColor(level) {
                            switch(level) {
                                case "ERROR": return theme.error
                                case "WARNING": return theme.warning
                                case "INFO": return theme.accent
                                case "DEBUG": return theme.textSecondary
                                default: return theme.text
                            }
                        }
                    }
                }
            }
        }
    }
    
    signal clearLogs()
} 