import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root
    
    // 属性定义
    property var cardData
    property var theme
    property bool expanded: false
    property bool isHovered: false
    
    // 信号定义
    signal cardClicked(var cardData)
    signal actionTriggered(string action, var cardData)
    
    // 卡片基础样式
    height: cardContent.height + theme.spacing.lg * 2
    color: theme.colors.surface
    radius: theme.borderRadius.md
    border.color: isHovered ? theme.colors.primary : theme.colors.border
    border.width: isHovered ? 2 : 1
    
    // 简单阴影效果（使用Rectangle模拟）
    Rectangle {
        anchors.fill: parent
        anchors.topMargin: isHovered ? 8 : 4
        anchors.leftMargin: 2
        z: -1
        color: Qt.rgba(0, 0, 0, isHovered ? 0.15 : 0.1)
        radius: parent.radius
        
        Behavior on anchors.topMargin {
            NumberAnimation { duration: 200 }
        }
        Behavior on color {
            ColorAnimation { duration: 200 }
        }
    }
    
    // 悬停动画
    Behavior on border.color {
        ColorAnimation { duration: 200 }
    }
    
    Behavior on border.width {
        NumberAnimation { duration: 200 }
    }
    
    // 鼠标交互
    MouseArea {
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        
        onEntered: {
            root.isHovered = true
        }
        
        onExited: {
            root.isHovered = false
        }
        
        onClicked: {
            root.cardClicked(root.cardData)
        }
    }
    
    // 卡片内容
    ColumnLayout {
        id: cardContent
        anchors {
            left: parent.left
            right: parent.right
            top: parent.top
            margins: root.theme.spacing.lg
        }
        spacing: root.theme.spacing.md
        
        // 头部区域
        RowLayout {
            Layout.fillWidth: true
            spacing: root.theme.spacing.md
            
            // 类型标识
            Rectangle {
                width: 8
                height: 40
                radius: 4
                color: root.cardData && root.cardData.type === "level3" ? 
                       root.theme.colors.primary : root.theme.colors.secondary
            }
            
            ColumnLayout {
                Layout.fillWidth: true
                spacing: 4
                
                // 标题
                Text {
                    text: getCardTitle()
                    font.pixelSize: 16
                    font.bold: true
                    color: root.theme.colors.text
                    wrapMode: Text.WordWrap
                    Layout.fillWidth: true
                }
                
                // 副标题
                Text {
                    text: getCardSubtitle()
                    font.pixelSize: 12
                    color: root.theme.colors.textSecondary
                    Layout.fillWidth: true
                }
            }
            
            // 状态指示器
            Rectangle {
                width: 80
                height: 24
                radius: 12
                color: getStatusColor()
                
                Text {
                    anchors.centerIn: parent
                    text: getStatusText()
                    color: "white"
                    font.pixelSize: 10
                    font.bold: true
                }
            }
            
            // 展开/收起按钮
            Button {
                width: 32
                height: 32
                
                background: Rectangle {
                    color: parent.pressed ? Qt.darker(root.theme.colors.border, 1.2) : 
                           parent.hovered ? root.theme.colors.border : "transparent"
                    radius: 16
                    
                    Behavior on color {
                        ColorAnimation { duration: 150 }
                    }
                }
                
                contentItem: Text {
                    text: root.expanded ? "▲" : "▼"
                    color: root.theme.colors.text
                    font.pixelSize: 12
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
                
                onClicked: {
                    root.expanded = !root.expanded
                }
            }
        }
        
        // 进度条
        Rectangle {
            Layout.fillWidth: true
            height: 8
            radius: 4
            color: root.theme.colors.border
            visible: getProgressVisible()
            
            Rectangle {
                width: parent.width * getProgressValue()
                height: parent.height
                radius: parent.radius
                color: root.cardData && root.cardData.type === "level3" ? 
                       root.theme.colors.primary : root.theme.colors.secondary
                
                Behavior on width {
                    NumberAnimation { duration: 300 }
                }
            }
        }
        
        // 基础信息网格
        GridLayout {
            Layout.fillWidth: true
            columns: 2
            columnSpacing: root.theme.spacing.lg
            rowSpacing: root.theme.spacing.sm
            
            Repeater {
                model: getBasicInfo()
                
                delegate: RowLayout {
                    Layout.fillWidth: true
                    spacing: root.theme.spacing.sm
                    
                    Text {
                        text: modelData.label + ":"
                        font.pixelSize: 12
                        color: root.theme.colors.textSecondary
                        Layout.preferredWidth: 80
                    }
                    
                    Text {
                        text: modelData.value
                        font.pixelSize: 12
                        font.bold: true
                        color: root.theme.colors.text
                        Layout.fillWidth: true
                    }
                }
            }
        }
        
        // 展开内容
        ColumnLayout {
            Layout.fillWidth: true
            spacing: root.theme.spacing.md
            visible: root.expanded
            opacity: root.expanded ? 1 : 0
            
            Behavior on opacity {
                NumberAnimation { duration: 200 }
            }
            
            // 任务/步骤列表
            Rectangle {
                Layout.fillWidth: true
                height: taskList.contentHeight + root.theme.spacing.md * 2
                color: "#f8fafc"
                radius: root.theme.borderRadius.sm
                border.color: root.theme.colors.border
                border.width: 1
                
                ColumnLayout {
                    anchors {
                        fill: parent
                        margins: root.theme.spacing.md
                    }
                    spacing: root.theme.spacing.sm
                    
                    Text {
                        text: root.cardData && root.cardData.type === "level3" ? "任务列表" : "执行步骤"
                        font.pixelSize: 14
                        font.bold: true
                        color: root.theme.colors.text
                    }
                    
                    ListView {
                        id: taskList
                        Layout.fillWidth: true
                        Layout.preferredHeight: contentHeight
                        model: getTaskList()
                        spacing: root.theme.spacing.xs
                        interactive: false
                        
                        delegate: Rectangle {
                            width: taskList.width
                            height: 40
                            color: modelData.current ? Qt.rgba(0.2, 0.7, 1, 0.1) : "transparent"
                            radius: 4
                            border.color: modelData.current ? root.theme.colors.primary : "transparent"
                            border.width: modelData.current ? 1 : 0
                            
                            RowLayout {
                                anchors {
                                    fill: parent
                                    margins: root.theme.spacing.sm
                                }
                                spacing: root.theme.spacing.sm
                                
                                // 状态图标
                                Text {
                                    text: getTaskIcon(modelData.status)
                                    font.pixelSize: 16
                                    color: getTaskIconColor(modelData.status)
                                }
                                
                                // 任务名称
                                Text {
                                    text: modelData.name
                                    font.pixelSize: 12
                                    color: root.theme.colors.text
                                    Layout.fillWidth: true
                                }
                                
                                // 时间/状态
                                Text {
                                    text: modelData.time || modelData.status
                                    font.pixelSize: 10
                                    color: root.theme.colors.textSecondary
                                }
                            }
                        }
                    }
                }
            }
            
            // 操作按钮区域
            RowLayout {
                Layout.fillWidth: true
                spacing: root.theme.spacing.sm
                
                Button {
                    text: "查看详情"
                    
                    background: Rectangle {
                        color: parent.pressed ? Qt.darker(root.theme.colors.primary, 1.2) : 
                               parent.hovered ? Qt.lighter(root.theme.colors.primary, 1.1) : root.theme.colors.primary
                        radius: root.theme.borderRadius.sm
                        
                        Behavior on color {
                            ColorAnimation { duration: 150 }
                        }
                    }
                    
                    contentItem: Text {
                        text: parent.text
                        color: "white"
                        font.pixelSize: 11
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                    
                    onClicked: {
                        root.actionTriggered("view_detail", root.cardData)
                    }
                }
                
                Button {
                    text: root.cardData && root.cardData.type === "level3" ? "执行计划" : "继续执行"
                    visible: canExecute()
                    
                    background: Rectangle {
                        color: parent.pressed ? Qt.darker(root.theme.colors.secondary, 1.2) : 
                               parent.hovered ? Qt.lighter(root.theme.colors.secondary, 1.1) : root.theme.colors.secondary
                        radius: root.theme.borderRadius.sm
                        
                        Behavior on color {
                            ColorAnimation { duration: 150 }
                        }
                    }
                    
                    contentItem: Text {
                        text: parent.text
                        color: "white"
                        font.pixelSize: 11
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                    
                    onClicked: {
                        root.actionTriggered("execute", root.cardData)
                    }
                }
                
                Item { Layout.fillWidth: true }
                
                Button {
                    text: "删除"
                    
                    background: Rectangle {
                        color: parent.pressed ? Qt.darker(root.theme.colors.error, 1.2) : 
                               parent.hovered ? Qt.lighter(root.theme.colors.error, 1.1) : root.theme.colors.error
                        radius: root.theme.borderRadius.sm
                        
                        Behavior on color {
                            ColorAnimation { duration: 150 }
                        }
                    }
                    
                    contentItem: Text {
                        text: parent.text
                        color: "white"
                        font.pixelSize: 11
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                    
                    onClicked: {
                        root.actionTriggered("delete", root.cardData)
                    }
                }
            }
        }
    }
    
    // JavaScript 函数
    function getCardTitle() {
        if (!root.cardData) return "未知卡片"
        
        if (root.cardData.type === "level3") {
            return root.cardData["计划名"] || "Level3 计划"
        } else {
            return root.cardData["任务名"] || "Level2 任务"
        }
    }
    
    function getCardSubtitle() {
        if (!root.cardData) return ""
        
        return root.cardData.plan_id || ""
    }
    
    function getStatusText() {
        if (!root.cardData) return "未知"
        
        if (root.cardData.type === "level3") {
            var status = root.cardData["Json A样式"] && root.cardData["Json A样式"]["计划状态"]
            switch(status) {
                case "planning": return "计划中"
                case "running": return "执行中"
                case "completed": return "已完成"
                case "failed": return "失败"
                default: return "未知"
            }
        } else {
            var status = root.cardData["Json B样式"] && root.cardData["Json B样式"]["任务状态"]
            switch(status) {
                case "waiting": return "等待中"
                case "running": return "执行中"
                case "completed": return "已完成"
                case "failed": return "失败"
                default: return "未知"
            }
        }
    }
    
    function getStatusColor() {
        if (!root.cardData) return root.theme.colors.textSecondary
        
        var status
        if (root.cardData.type === "level3") {
            status = root.cardData["Json A样式"] && root.cardData["Json A样式"]["计划状态"]
        } else {
            status = root.cardData["Json B样式"] && root.cardData["Json B样式"]["任务状态"]
        }
        
        switch(status) {
            case "planning":
            case "waiting": return root.theme.colors.accent
            case "running": return root.theme.colors.primary
            case "completed": return root.theme.colors.success
            case "failed": return root.theme.colors.error
            default: return root.theme.colors.textSecondary
        }
    }
    
    function getProgressVisible() {
        return root.cardData && (root.cardData.type === "level3" || root.cardData.type === "level2")
    }
    
    function getProgressValue() {
        if (!root.cardData) return 0
        
        if (root.cardData.type === "level3") {
            var current = root.cardData["Json A样式"] && root.cardData["Json A样式"]["当前任务"] || 0
            var total = root.cardData["任务总数"] || 1
            return Math.min(current / total, 1.0)
        } else {
            var current = root.cardData["Json B样式"] && root.cardData["Json B样式"]["当前步骤"] || 0
            var total = root.cardData["步骤总数"] || 1
            return Math.min(current / total, 1.0)
        }
    }
    
    function getBasicInfo() {
        if (!root.cardData) return []
        
        var info = []
        
        if (root.cardData.type === "level3") {
            info.push({label: "任务总数", value: root.cardData["任务总数"] || 0})
            info.push({label: "计划时间", value: root.cardData["Json A样式"] && root.cardData["Json A样式"]["计划时间"] || "未知"})
            info.push({label: "当前任务", value: (root.cardData["Json A样式"] && root.cardData["Json A样式"]["当前任务"] || 0) + 1})
            info.push({label: "计划计数", value: root.cardData["Json A样式"] && root.cardData["Json A样式"]["计划计数"] || 1})
        } else {
            info.push({label: "步骤总数", value: root.cardData["步骤总数"] || 0})
            info.push({label: "当前步骤", value: (root.cardData["Json B样式"] && root.cardData["Json B样式"]["当前步骤"] || 0) + 1})
            info.push({label: "计划计数", value: root.cardData["计划计数"] || 1})
            info.push({label: "最终结果", value: root.cardData["Json B样式"] && root.cardData["Json B样式"]["最终结果"] || "执行中"})
        }
        
        return info
    }
    
    function getTaskList() {
        if (!root.cardData) return []
        
        var tasks = []
        
        if (root.cardData.type === "level3") {
            var taskData = root.cardData["Json A样式"] && root.cardData["Json A样式"]["任务具体内容"] || []
            var currentTask = root.cardData["Json A样式"] && root.cardData["Json A样式"]["当前任务"] || 0
            
            for (var i = 0; i < taskData.length; i++) {
                tasks.push({
                    name: taskData[i]["任务名"] || "未知任务",
                    status: taskData[i]["执行情况"] || "待执行",
                    time: taskData[i]["预估时间"] || "",
                    current: i === currentTask
                })
            }
        } else {
            var stepData = root.cardData["Json B样式"] && root.cardData["Json B样式"]["每个步骤具体内容"] || []
            var currentStep = root.cardData["Json B样式"] && root.cardData["Json B样式"]["当前步骤"] || 0
            
            for (var i = 0; i < stepData.length; i++) {
                tasks.push({
                    name: stepData[i]["步骤名"] || "步骤 " + (i + 1),
                    status: stepData[i]["步骤状态"] || "待执行",
                    time: stepData[i]["执行时间"] || "",
                    current: i === currentStep
                })
            }
        }
        
        return tasks
    }
    
    function getTaskIcon(status) {
        switch(status) {
            case "待执行": return "⏳"
            case "执行中": return "▶️"
            case "已完成": return "✅"
            case "失败": return "❌"
            default: return "⚪"
        }
    }
    
    function getTaskIconColor(status) {
        switch(status) {
            case "待执行": return root.theme.colors.accent
            case "执行中": return root.theme.colors.primary
            case "已完成": return root.theme.colors.success
            case "失败": return root.theme.colors.error
            default: return root.theme.colors.textSecondary
        }
    }
    
    function canExecute() {
        if (!root.cardData) return false
        
        if (root.cardData.type === "level3") {
            var status = root.cardData["Json A样式"] && root.cardData["Json A样式"]["计划状态"]
            return status === "planning" || status === "running"
        } else {
            var status = root.cardData["Json B样式"] && root.cardData["Json B样式"]["任务状态"]
            return status === "waiting" || status === "running"
        }
    }
} 