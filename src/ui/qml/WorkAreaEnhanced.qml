import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: workArea
    color: "#f8fafc"
    
    // 主题配置
    readonly property var theme: ({
        primary: "#4338ca",
        secondary: "#6366f1", 
        accent: "#8b5cf6",
        success: "#10b981",
        warning: "#f59e0b",
        error: "#ef4444",
        background: "#ffffff",
        surface: "#f8fafc",
        text: "#1f2937",
        textSecondary: "#6b7280",
        border: "#e5e7eb",
        shadow: "#00000020"
    })
    
    // 状态管理
    property string currentMode: "default" // default, project, task, device
    property var currentData: null
    
    // 信号定义
    signal actionRequested(string action, var data)
    signal contentChanged(string mode, var data)
    
    // 动画配置
    readonly property int animationDuration: 300
    
    StackLayout {
        id: contentStack
        anchors.fill: parent
        anchors.margins: 20
        currentIndex: {
            switch(workArea.currentMode) {
                case "project": return 1
                case "task": return 2  
                case "device": return 3
                default: return 0
            }
        }
        
        // 默认欢迎页面
        Item {
            id: defaultView
            
            Rectangle {
                anchors.centerIn: parent
                width: Math.min(parent.width * 0.8, 800)
                height: Math.min(parent.height * 0.8, 600)
                color: workArea.theme.background
                radius: 24
                
                // 阴影效果
                Rectangle {
                    anchors.fill: parent
                    anchors.margins: -4
                    color: workArea.theme.shadow
                    radius: parent.radius + 4
                    z: -1
                }
                
                ColumnLayout {
                    anchors.centerIn: parent
                    spacing: 40
                    
                    // 主标题
                    Text {
                        Layout.alignment: Qt.AlignHCenter
                        text: "🎯 AI 示波器控制系统"
                        font.pixelSize: 32
                        font.bold: true
                        color: workArea.theme.primary
                    }
                    
                    // 副标题
                    Text {
                        Layout.alignment: Qt.AlignHCenter
                        text: "点击左侧项目卡片展开测试步骤，开始您的测试流程"
                        font.pixelSize: 18
                        color: workArea.theme.secondary
                        wrapMode: Text.WordWrap
                        Layout.maximumWidth: 600
                        horizontalAlignment: Text.AlignHCenter
                    }
                    
                    // 功能特性网格
                    GridLayout {
                        Layout.alignment: Qt.AlignHCenter
                        columns: 3
                        columnSpacing: 30
                        rowSpacing: 20
                        
                        Repeater {
                            model: [
                                {icon: "🤖", title: "AI智能控制", desc: "智能识别测试需求"},
                                {icon: "📊", title: "实时数据", desc: "实时显示测量结果"},
                                {icon: "🔧", title: "自动化测试", desc: "一键执行测试流程"},
                                {icon: "📈", title: "数据分析", desc: "智能分析测试数据"},
                                {icon: "📋", title: "报告生成", desc: "自动生成测试报告"},
                                {icon: "🔗", title: "设备管理", desc: "统一管理测试设备"}
                            ]
                            
                            Rectangle {
                                Layout.preferredWidth: 180
                                Layout.preferredHeight: 120
                                color: workArea.theme.surface
                                radius: 16
                                border.color: workArea.theme.border
                                border.width: 1
                                
                                // 悬停效果
                                MouseArea {
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    
                                    onEntered: parent.color = Qt.lighter(workArea.theme.surface, 1.05)
                                    onExited: parent.color = workArea.theme.surface
                                }
                                
                                ColumnLayout {
                                    anchors.centerIn: parent
                                    spacing: 8
                                    
                                    Text {
                                        Layout.alignment: Qt.AlignHCenter
                                        text: modelData.icon
                                        font.pixelSize: 24
                                    }
                                    
                                    Text {
                                        Layout.alignment: Qt.AlignHCenter
                                        text: modelData.title
                                        font.pixelSize: 14
                                        font.bold: true
                                        color: workArea.theme.text
                                    }
                                    
                                    Text {
                                        Layout.alignment: Qt.AlignHCenter
                                        text: modelData.desc
                                        font.pixelSize: 11
                                        color: workArea.theme.textSecondary
                                        wrapMode: Text.WordWrap
                                        Layout.maximumWidth: 150
                                        horizontalAlignment: Text.AlignHCenter
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        
        // 项目详情页面
        Item {
            id: projectView
            
            ScrollView {
                anchors.fill: parent
                ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
                
                Rectangle {
                    width: projectView.width
                    height: Math.max(projectView.height, contentColumn.implicitHeight + 40)
                    color: "transparent"
                    
                    ColumnLayout {
                        id: contentColumn
                        anchors.fill: parent
                        anchors.margins: 20
                        spacing: 24
                        
                        // 项目头部
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 120
                            color: workArea.theme.background
                            radius: 16
                            
                            RowLayout {
                                anchors.fill: parent
                                anchors.margins: 24
                                spacing: 20
                                
                                // 项目图标
                                Rectangle {
                                    Layout.preferredWidth: 72
                                    Layout.preferredHeight: 72
                                    color: workArea.theme.primary
                                    radius: 36
                                    
                                    Text {
                                        anchors.centerIn: parent
                                        text: "📋"
                                        font.pixelSize: 32
                                    }
                                }
                                
                                // 项目信息
                                ColumnLayout {
                                    Layout.fillWidth: true
                                    spacing: 8
                                    
                                    Text {
                                        text: currentData ? currentData.title || "项目名称" : "项目名称"
                                        font.pixelSize: 24
                                        font.bold: true
                                        color: workArea.theme.text
                                    }
                                    
                                    Text {
                                        text: currentData ? currentData.description || "项目描述" : "项目描述"
                                        font.pixelSize: 14
                                        color: workArea.theme.textSecondary
                                        wrapMode: Text.WordWrap
                                        Layout.fillWidth: true
                                    }
                                    
                                    // 状态标签
                                    Rectangle {
                                        Layout.preferredWidth: statusText.implicitWidth + 16
                                        Layout.preferredHeight: 28
                                        color: workArea.theme.success
                                        radius: 14
                                        
                                        Text {
                                            id: statusText
                                            anchors.centerIn: parent
                                            text: "进行中"
                                            color: "white"
                                            font.pixelSize: 12
                                            font.bold: true
                                        }
                                    }
                                }
                                
                                // 操作按钮
                                RowLayout {
                                    spacing: 12
                                    
                                    Button {
                                        text: "开始测试"
                                        font.pixelSize: 14
                                        
                                        background: Rectangle {
                                            color: parent.pressed ? Qt.darker(workArea.theme.primary, 1.1) : 
                                                   parent.hovered ? Qt.lighter(workArea.theme.primary, 1.1) : 
                                                   workArea.theme.primary
                                            radius: 8
                                        }
                                        
                                        contentItem: Text {
                                            text: parent.text
                                            color: "white"
                                            font: parent.font
                                            horizontalAlignment: Text.AlignHCenter
                                            verticalAlignment: Text.AlignVCenter
                                        }
                                        
                                        onClicked: workArea.actionRequested("start_test", currentData)
                                    }
                                    
                                    Button {
                                        text: "查看报告"
                                        font.pixelSize: 14
                                        
                                        background: Rectangle {
                                            color: parent.pressed ? Qt.darker(workArea.theme.surface, 1.1) : 
                                                   parent.hovered ? Qt.lighter(workArea.theme.surface, 1.05) : 
                                                   workArea.theme.surface
                                            radius: 8
                                            border.color: workArea.theme.border
                                            border.width: 1
                                        }
                                        
                                        contentItem: Text {
                                            text: parent.text
                                            color: workArea.theme.text
                                            font: parent.font
                                            horizontalAlignment: Text.AlignHCenter
                                            verticalAlignment: Text.AlignVCenter
                                        }
                                        
                                        onClicked: workArea.actionRequested("view_report", currentData)
                                    }
                                }
                            }
                        }
                        
                        // 任务列表
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            Layout.minimumHeight: 400
                            color: workArea.theme.background
                            radius: 16
                            
                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: 24
                                spacing: 16
                                
                                Text {
                                    text: "测试任务"
                                    font.pixelSize: 20
                                    font.bold: true
                                    color: workArea.theme.text
                                }
                                
                                ListView {
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true
                                    model: currentData ? currentData.tasks || [] : []
                                    spacing: 12
                                    
                                    delegate: Rectangle {
                                        width: ListView.view.width
                                        height: 80
                                        color: workArea.theme.surface
                                        radius: 12
                                        border.color: workArea.theme.border
                                        border.width: 1
                                        
                                        // 悬停效果
                                        MouseArea {
                                            anchors.fill: parent
                                            hoverEnabled: true
                                            
                                            onEntered: parent.color = Qt.lighter(workArea.theme.surface, 1.02)
                                            onExited: parent.color = workArea.theme.surface
                                            onClicked: workArea.actionRequested("select_task", modelData)
                                        }
                                        
                                        RowLayout {
                                            anchors.fill: parent
                                            anchors.margins: 16
                                            spacing: 16
                                            
                                            // 任务状态指示器
                                            Rectangle {
                                                Layout.preferredWidth: 12
                                                Layout.preferredHeight: 12
                                                radius: 6
                                                color: {
                                                    switch(modelData.status) {
                                                        case "completed": return workArea.theme.success
                                                        case "running": return workArea.theme.warning
                                                        case "failed": return workArea.theme.error
                                                        default: return workArea.theme.textSecondary
                                                    }
                                                }
                                            }
                                            
                                            // 任务信息
                                            ColumnLayout {
                                                Layout.fillWidth: true
                                                spacing: 4
                                                
                                                Text {
                                                    text: modelData.name || "任务名称"
                                                    font.pixelSize: 16
                                                    font.bold: true
                                                    color: workArea.theme.text
                                                }
                                                
                                                Text {
                                                    text: modelData.description || "任务描述"
                                                    font.pixelSize: 12
                                                    color: workArea.theme.textSecondary
                                                    wrapMode: Text.WordWrap
                                                    Layout.fillWidth: true
                                                }
                                            }
                                            
                                            // 任务进度
                                            Text {
                                                text: (modelData.progress || 0) + "%"
                                                font.pixelSize: 14
                                                font.bold: true
                                                color: workArea.theme.primary
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        
        // 任务详情页面
        Item {
            id: taskView
            
            Text {
                anchors.centerIn: parent
                text: "任务详情视图\n(开发中...)"
                font.pixelSize: 18
                color: workArea.theme.textSecondary
                horizontalAlignment: Text.AlignHCenter
            }
        }
        
        // 设备管理页面
        Item {
            id: deviceView
            
            Text {
                anchors.centerIn: parent
                text: "设备管理视图\n(开发中...)"
                font.pixelSize: 18
                color: workArea.theme.textSecondary
                horizontalAlignment: Text.AlignHCenter
            }
        }
    }
    
    // 切换动画
    Behavior on currentMode {
        SequentialAnimation {
            PropertyAnimation {
                target: contentStack
                property: "opacity"
                to: 0
                duration: workArea.animationDuration / 2
                easing.type: Easing.OutCubic
            }
            PropertyAction {
                target: contentStack
                property: "currentIndex"
            }
            PropertyAnimation {
                target: contentStack
                property: "opacity"
                to: 1
                duration: workArea.animationDuration / 2
                easing.type: Easing.InCubic
            }
        }
    }
    
    // 公共方法
    function setContent(mode, data) {
        currentMode = mode
        currentData = data
        contentChanged(mode, data)
    }
    
    function clearContent() {
        currentMode = "default"
        currentData = null
        contentChanged("default", null)
    }
} 