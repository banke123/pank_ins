import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: mainWorkArea
    
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
    
    property string currentView: "dashboard"  // dashboard, oscilloscope, analysis
    
    signal viewChanged(string view)
    signal openFileDialog()
    signal saveCurrentWork()
    signal exportResults()
    
    color: theme.background
    
    ColumnLayout {
        anchors.fill: parent
        spacing: 0
        
        // 工具栏
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 60
            color: theme.surface
            border.color: theme.border
            border.width: 1
            
            RowLayout {
                anchors.fill: parent
                anchors.margins: 16
                spacing: 16
                
                // 视图切换按钮组
                Row {
                    spacing: 8
                    
                    Repeater {
                        model: [
                            { id: "dashboard", text: "📊 仪表板", icon: "📊" },
                            { id: "oscilloscope", text: "📈 示波器", icon: "📈" },
                            { id: "analysis", text: "🔬 分析", icon: "🔬" }
                        ]
                        
                        Button {
                            text: modelData.text
                            checked: currentView === modelData.id
                            
                            background: Rectangle {
                                color: parent.checked ? theme.primary : 
                                       parent.hovered ? theme.surface : "transparent"
                                border.color: parent.checked ? theme.primary : theme.border
                                border.width: 1
                                radius: 6
                            }
                            
                            contentItem: Text {
                                text: parent.text
                                color: parent.checked ? "white" : theme.text
                                font.pixelSize: 14
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                            }
                            
                            onClicked: {
                                currentView = modelData.id
                                viewChanged(modelData.id)
                            }
                        }
                    }
                }
                
                Item { Layout.fillWidth: true }
                
                // 工具按钮组
                Row {
                    spacing: 8
                    
                    Button {
                        text: "📁 打开"
                        onClicked: openFileDialog()
                        
                        background: Rectangle {
                            color: parent.hovered ? theme.accent : "transparent"
                            border.color: theme.accent
                            border.width: 1
                            radius: 6
                        }
                        
                        contentItem: Text {
                            text: parent.text
                            color: parent.parent.hovered ? "white" : theme.accent
                            font.pixelSize: 12
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }
                    }
                    
                    Button {
                        text: "💾 保存"
                        onClicked: saveCurrentWork()
                        
                        background: Rectangle {
                            color: parent.hovered ? theme.success : "transparent"
                            border.color: theme.success
                            border.width: 1
                            radius: 6
                        }
                        
                        contentItem: Text {
                            text: parent.text
                            color: parent.parent.hovered ? "white" : theme.success
                            font.pixelSize: 12
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }
                    }
                    
                    Button {
                        text: "📤 导出"
                        onClicked: exportResults()
                        
                        background: Rectangle {
                            color: parent.hovered ? theme.warning : "transparent"
                            border.color: theme.warning
                            border.width: 1
                            radius: 6
                        }
                        
                        contentItem: Text {
                            text: parent.text
                            color: parent.parent.hovered ? "white" : theme.warning
                            font.pixelSize: 12
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }
                    }
                }
            }
        }
        
        // 主要内容区域
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: theme.background
            
            StackLayout {
                anchors.fill: parent
                currentIndex: getCurrentViewIndex()
                
                function getCurrentViewIndex() {
                    switch(currentView) {
                        case "dashboard": return 0
                        case "oscilloscope": return 1
                        case "analysis": return 2
                        default: return 0
                    }
                }
                
                // 仪表板视图
                Rectangle {
                    color: theme.background
                    
                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 32
                        spacing: 24
                        
                        Text {
                            text: "📊 系统仪表板"
                            font.pixelSize: 32
                            font.bold: true
                            color: theme.text
                            Layout.alignment: Qt.AlignHCenter
                        }
                        
                        // 快速统计卡片
                        GridLayout {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 200
                            columns: 3
                            columnSpacing: 20
                            
                            Repeater {
                                model: [
                                    { title: "活跃任务", value: "5", icon: "🔄", color: theme.primary },
                                    { title: "已完成", value: "12", icon: "✅", color: theme.success },
                                    { title: "设备连接", value: "3", icon: "🔗", color: theme.accent }
                                ]
                                
                                Rectangle {
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true
                                    color: theme.surface
                                    border.color: theme.border
                                    border.width: 1
                                    radius: 12
                                    
                                    ColumnLayout {
                                        anchors.centerIn: parent
                                        spacing: 12
                                        
                                        Text {
                                            text: modelData.icon
                                            font.pixelSize: 32
                                            Layout.alignment: Qt.AlignHCenter
                                        }
                                        
                                        Text {
                                            text: modelData.value
                                            font.pixelSize: 28
                                            font.bold: true
                                            color: modelData.color
                                            Layout.alignment: Qt.AlignHCenter
                                        }
                                        
                                        Text {
                                            text: modelData.title
                                            font.pixelSize: 14
                                            color: theme.textSecondary
                                            Layout.alignment: Qt.AlignHCenter
                                        }
                                    }
                                }
                            }
                        }
                        
                        // 最近活动
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            color: theme.surface
                            border.color: theme.border
                            border.width: 1
                            radius: 12
                            
                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: 20
                                spacing: 16
                                
                                Text {
                                    text: "📋 最近活动"
                                    font.pixelSize: 18
                                    font.bold: true
                                    color: theme.text
                                }
                                
                                ListView {
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true
                                    model: [
                                        "✅ I2C协议测试已完成",
                                        "🔄 电源纹波测试正在进行",
                                        "📊 数据分析报告已生成",
                                        "⚠️ 示波器通道2信号异常"
                                    ]
                                    
                                    delegate: Text {
                                        width: ListView.view.width
                                        text: modelData
                                        font.pixelSize: 14
                                        color: theme.text
                                        padding: 8
                                    }
                                }
                            }
                        }
                    }
                }
                
                // 示波器视图
                Rectangle {
                    color: theme.background
                    
                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 20
                        spacing: 16
                        
                        Text {
                            text: "📈 示波器控制面板"
                            font.pixelSize: 24
                            font.bold: true
                            color: theme.text
                            Layout.alignment: Qt.AlignHCenter
                        }
                        
                        // 示波器控制区域
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 120
                            color: theme.surface
                            border.color: theme.border
                            border.width: 1
                            radius: 8
                            
                            RowLayout {
                                anchors.fill: parent
                                anchors.margins: 16
                                spacing: 16
                                
                                ColumnLayout {
                                    Layout.fillWidth: true
                                    
                                    Text {
                                        text: "通道设置"
                                        font.pixelSize: 16
                                        font.bold: true
                                        color: theme.text
                                    }
                                    
                                    Row {
                                        spacing: 12
                                        
                                        Repeater {
                                            model: ["CH1", "CH2", "CH3", "CH4"]
                                            
                                            Button {
                                                text: modelData
                                                checkable: true
                                                checked: index < 2
                                                
                                                background: Rectangle {
                                                    color: parent.checked ? theme.success : theme.surface
                                                    border.color: parent.checked ? theme.success : theme.border
                                                    border.width: 1
                                                    radius: 4
                                                }
                                                
                                                contentItem: Text {
                                                    text: parent.text
                                                    color: parent.checked ? "white" : theme.text
                                                    font.pixelSize: 12
                                                    horizontalAlignment: Text.AlignHCenter
                                                    verticalAlignment: Text.AlignVCenter
                                                }
                                            }
                                        }
                                    }
                                }
                                
                                ColumnLayout {
                                    Layout.fillWidth: true
                                    
                                    Text {
                                        text: "触发设置"
                                        font.pixelSize: 16
                                        font.bold: true
                                        color: theme.text
                                    }
                                    
                                    Row {
                                        spacing: 8
                                        
                                        ComboBox {
                                            model: ["上升沿", "下降沿", "双边沿"]
                                            currentIndex: 0
                                        }
                                        
                                        SpinBox {
                                            from: -5000
                                            to: 5000
                                            value: 0
                                            suffix: " mV"
                                        }
                                    }
                                }
                            }
                        }
                        
                        // 波形显示区域
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            color: "#001122"
                            border.color: theme.border
                            border.width: 1
                            radius: 8
                            
                            Text {
                                anchors.centerIn: parent
                                text: "📊 波形显示区域\n\n连接示波器后这里将显示实时波形"
                                font.pixelSize: 18
                                color: "#00ff00"
                                horizontalAlignment: Text.AlignHCenter
                            }
                        }
                    }
                }
                
                // 分析视图
                Rectangle {
                    color: theme.background
                    
                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 20
                        spacing: 16
                        
                        Text {
                            text: "🔬 数据分析工作台"
                            font.pixelSize: 24
                            font.bold: true
                            color: theme.text
                            Layout.alignment: Qt.AlignHCenter
                        }
                        
                        // 分析工具栏
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 60
                            color: theme.surface
                            border.color: theme.border
                            border.width: 1
                            radius: 8
                            
                            RowLayout {
                                anchors.fill: parent
                                anchors.margins: 12
                                spacing: 12
                                
                                Text {
                                    text: "分析工具:"
                                    font.pixelSize: 14
                                    color: theme.text
                                }
                                
                                Row {
                                    spacing: 8
                                    
                                    Repeater {
                                        model: ["FFT分析", "滤波器", "测量", "导出数据"]
                                        
                                        Button {
                                            text: modelData
                                            
                                            background: Rectangle {
                                                color: parent.hovered ? theme.primary : "transparent"
                                                border.color: theme.primary
                                                border.width: 1
                                                radius: 4
                                            }
                                            
                                            contentItem: Text {
                                                text: parent.text
                                                color: parent.parent.hovered ? "white" : theme.primary
                                                font.pixelSize: 12
                                                horizontalAlignment: Text.AlignHCenter
                                                verticalAlignment: Text.AlignVCenter
                                            }
                                        }
                                    }
                                }
                                
                                Item { Layout.fillWidth: true }
                            }
                        }
                        
                        // 分析结果区域
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            color: theme.surface
                            border.color: theme.border
                            border.width: 1
                            radius: 8
                            
                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: 20
                                spacing: 16
                                
                                Text {
                                    text: "📈 分析结果"
                                    font.pixelSize: 18
                                    font.bold: true
                                    color: theme.text
                                }
                                
                                Text {
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true
                                    text: "暂无分析数据\n\n请先进行数据采集或加载已有数据文件进行分析"
                                    font.pixelSize: 16
                                    color: theme.textSecondary
                                    horizontalAlignment: Text.AlignHCenter
                                    verticalAlignment: Text.AlignVCenter
                                    wrapMode: Text.Wrap
                                }
                            }
                        }
                    }
                }
            }
        }
    }
} 