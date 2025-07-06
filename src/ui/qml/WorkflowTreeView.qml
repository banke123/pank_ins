import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Controls.Material 2.15

Rectangle {
    id: root
    
    // 属性定义
    property var workflowData: defaultWorkflowData
    property var theme: Material
    
    // 信号定义
    signal itemClicked(var itemData)
    signal itemDoubleClicked(var itemData)
    signal contextMenuRequested(var itemData)
    
    // 默认数据
    property var defaultWorkflowData: [
        {
            "name": "项目计划 1",
            "type": "plan", 
            "status": "running",
            "progress": 0.6,
            "expanded": true,
            "children": [
                {"name": "任务 1.1", "type": "task", "status": "completed", "progress": 1.0},
                {"name": "任务 1.2", "type": "task", "status": "running", "progress": 0.7},
                {"name": "任务 1.3", "type": "task", "status": "waiting", "progress": 0.0}
            ]
        },
        {
            "name": "项目计划 2",
            "type": "plan",
            "status": "waiting", 
            "progress": 0.0,
            "expanded": false,
            "children": [
                {"name": "任务 2.1", "type": "task", "status": "waiting", "progress": 0.0},
                {"name": "任务 2.2", "type": "task", "status": "waiting", "progress": 0.0}
            ]
        }
    ]
    
    color: Material.color(Material.Grey, Material.Shade900)
    radius: 8
    
    Column {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 10
        
        // 标题栏
        Row {
            width: parent.width
            spacing: 10
            
            Label {
                text: "工作流程"
                font.pixelSize: 18
                font.bold: true
                color: Material.color(Material.Blue)
                anchors.verticalCenter: parent.verticalCenter
            }
            
            // 刷新按钮
            Button {
                width: 32
                height: 32
                
                background: Rectangle {
                    color: parent.pressed ? Material.color(Material.Blue, Material.Shade800) : 
                           parent.hovered ? Material.color(Material.Blue, Material.Shade700) : "transparent"
                    radius: 16
                }
                
                contentItem: Text {
                    text: "🔄"
                    color: Material.color(Material.Blue)
                    font.pixelSize: 14
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
                
                onClicked: {
                    // 刷新工作流数据
                    console.log("刷新工作流数据")
                }
            }
        }
        
        // 树状图滚动视图
        ScrollView {
            width: parent.width
            height: parent.height - 50
            clip: true
            
            ListView {
                id: treeView
                anchors.fill: parent
                spacing: 2
                
                model: ListModel {
                    id: treeModel
                    
                    Component.onCompleted: {
                        buildTreeModel()
                    }
                }
                
                delegate: Rectangle {
                    id: itemDelegate
                    
                    width: treeView.width
                    height: 40
                    color: mouseArea.containsMouse ? Material.color(Material.Grey, Material.Shade800) : "transparent"
                    radius: 4
                    
                    Behavior on color {
                        ColorAnimation { duration: 150 }
                    }
                    
                    // 缩进指示器
                    Rectangle {
                        x: model.level * 20 + 5
                        y: parent.height / 2 - height / 2
                        width: 2
                        height: parent.height * 0.6
                        color: Material.color(Material.Grey, Material.Shade600)
                        visible: model.level > 0
                    }
                    
                    Row {
                        anchors.left: parent.left
                        anchors.leftMargin: model.level * 20 + 15
                        anchors.verticalCenter: parent.verticalCenter
                        spacing: 8
                        
                        // 展开/收起按钮
                        Button {
                            width: 16
                            height: 16
                            visible: model.hasChildren
                            
                            background: Rectangle {
                                color: "transparent"
                            }
                            
                            contentItem: Text {
                                text: model.expanded ? "▼" : "▶"
                                color: Material.color(Material.Grey, Material.Shade300)
                                font.pixelSize: 10
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                            }
                            
                            onClicked: {
                                toggleExpanded(model)
                            }
                        }
                        
                        // 状态指示点
                        Rectangle {
                            width: 8
                            height: 8
                            radius: 4
                            color: root.getStatusColor(model.status)
                            
                            // 运行状态的闪烁动画
                            SequentialAnimation on opacity {
                                running: model.status === "running"
                                loops: Animation.Infinite
                                NumberAnimation { to: 0.3; duration: 1000 }
                                NumberAnimation { to: 1.0; duration: 1000 }
                            }
                        }
                        
                        // 名称
                        Label {
                            text: model.name
                            color: Material.color(Material.Grey, Material.Shade100)
                            font.pixelSize: model.type === "plan" ? 14 : 12
                            font.bold: model.type === "plan"
                            anchors.verticalCenter: parent.verticalCenter
                        }
                        
                        // 进度指示
                        Rectangle {
                            width: 60
                            height: 4
                            radius: 2
                            color: Material.color(Material.Grey, Material.Shade700)
                            visible: model.progress > 0
                            anchors.verticalCenter: parent.verticalCenter
                            
                            Rectangle {
                                width: parent.width * model.progress
                                height: parent.height
                                radius: parent.radius
                                color: root.getStatusColor(model.status)
                                
                                Behavior on width {
                                    NumberAnimation { duration: 300 }
                                }
                            }
                        }
                    }
                    
                    // 鼠标交互
                    MouseArea {
                        id: mouseArea
                        anchors.fill: parent
                        hoverEnabled: true
                        acceptedButtons: Qt.LeftButton | Qt.RightButton
                        
                        onClicked: function(mouse) {
                            if (mouse.button === Qt.LeftButton) {
                                root.itemClicked(model)
                            } else if (mouse.button === Qt.RightButton) {
                                root.contextMenuRequested(model)
                            }
                        }
                        
                        onDoubleClicked: {
                            root.itemDoubleClicked(model)
                        }
                    }
                }
            }
        }
    }
    
    // 构建树形模型
    function buildTreeModel() {
        treeModel.clear()
        
        for (let i = 0; i < workflowData.length; i++) {
            let plan = workflowData[i]
            
            // 添加计划节点
            treeModel.append({
                "name": plan.name,
                "type": plan.type,
                "status": plan.status,
                "progress": plan.progress || 0,
                "level": 0,
                "expanded": plan.expanded || false,
                "hasChildren": plan.children && plan.children.length > 0,
                "planIndex": i,
                "taskIndex": -1
            })
            
            // 如果展开，添加任务节点
            if (plan.expanded && plan.children) {
                for (let j = 0; j < plan.children.length; j++) {
                    let task = plan.children[j]
                    
                    treeModel.append({
                        "name": task.name,
                        "type": task.type,
                        "status": task.status,
                        "progress": task.progress || 0,
                        "level": 1,
                        "expanded": false,
                        "hasChildren": false,
                        "planIndex": i,
                        "taskIndex": j
                    })
                }
            }
        }
    }
    
    // 切换展开状态
    function toggleExpanded(itemData) {
        if (itemData.type === "plan") {
            workflowData[itemData.planIndex].expanded = !workflowData[itemData.planIndex].expanded
            buildTreeModel()
        }
    }
    
    // 更新工作流数据
    function updateWorkflowData(newData) {
        workflowData = newData
        buildTreeModel()
    }
    
    // 获取状态颜色
    function getStatusColor(status) {
        switch (status) {
            case "running": return Material.color(Material.Orange)
            case "completed": return Material.color(Material.Green)
            case "error": return Material.color(Material.Red)
            case "waiting": return Material.color(Material.Grey)
            default: return Material.color(Material.Grey)
        }
    }
    
    // 获取状态文字
    function getStatusText(status) {
        switch (status) {
            case "running": return "进行中"
            case "completed": return "已完成"
            case "error": return "错误"
            case "waiting": return "等待中"
            default: return "未知"
        }
    }
} 