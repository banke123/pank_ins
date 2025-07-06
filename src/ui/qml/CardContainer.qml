import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Item {
    id: root
    
    // 属性定义
    property var theme
    property int cardCount: cardModel.count
    
    // 信号定义
    signal cardClicked(var cardData)
    signal actionTriggered(string action, var cardData)
    
    // 数据模型
    ListModel {
        id: cardModel
    }
    
    // 主滚动视图
    ScrollView {
        anchors.fill: parent
        contentWidth: availableWidth
        
        ListView {
            id: cardListView
            anchors.fill: parent
            model: cardModel
            spacing: root.theme.spacing.md
            
            // 添加边距
            topMargin: root.theme.spacing.sm
            bottomMargin: root.theme.spacing.sm
            leftMargin: root.theme.spacing.sm
            rightMargin: root.theme.spacing.sm
            
            delegate: DynamicCard {
                width: cardListView.width - root.theme.spacing.md
                cardData: model.data
                theme: root.theme
                
                onCardClicked: function(data) {
                    root.cardClicked(data)
                }
                
                onActionTriggered: function(action, data) {
                    root.actionTriggered(action, data)
                }
            }
            
            // 空状态显示
            Rectangle {
                anchors.centerIn: parent
                width: 300
                height: 200
                color: "transparent"
                visible: cardModel.count === 0
                
                ColumnLayout {
                    anchors.centerIn: parent
                    spacing: root.theme.spacing.md
                    
                    Text {
                        text: "📋"
                        font.pixelSize: 48
                        horizontalAlignment: Text.AlignHCenter
                        Layout.alignment: Qt.AlignHCenter
                    }
                    
                    Text {
                        text: "暂无流程卡片"
                        font.pixelSize: 16
                        color: root.theme.colors.textSecondary
                        horizontalAlignment: Text.AlignHCenter
                        Layout.alignment: Qt.AlignHCenter
                    }
                    
                    Text {
                        text: "点击上方按钮创建新的测试计划"
                        font.pixelSize: 12
                        color: root.theme.colors.textSecondary
                        horizontalAlignment: Text.AlignHCenter
                        Layout.alignment: Qt.AlignHCenter
                    }
                }
            }
            
            // 滚动动画
            Behavior on contentY {
                NumberAnimation {
                    duration: 200
                    easing.type: Easing.OutCubic
                }
            }
        }
    }
    
    // 公共方法
    function addCard(cardData) {
        cardModel.append({"data": cardData})
        
        // 滚动到底部显示新卡片
        Qt.callLater(function() {
            cardListView.positionViewAtEnd()
        })
    }
    
    function updateCard(cardId, updateData) {
        for (var i = 0; i < cardModel.count; i++) {
            var item = cardModel.get(i)
            if (item.data.id === cardId) {
                // 深度合并更新数据
                var newData = JSON.parse(JSON.stringify(item.data))
                mergeObjects(newData, updateData)
                cardModel.setProperty(i, "data", newData)
                break
            }
        }
    }
    
    function removeCard(cardId) {
        for (var i = 0; i < cardModel.count; i++) {
            var item = cardModel.get(i)
            if (item.data.id === cardId) {
                cardModel.remove(i)
                break
            }
        }
    }
    
    function clearAll() {
        cardModel.clear()
    }
    
    function getCard(cardId) {
        for (var i = 0; i < cardModel.count; i++) {
            var item = cardModel.get(i)
            if (item.data.id === cardId) {
                return item.data
            }
        }
        return null
    }
    
    function findExecutableCard() {
        // 查找可执行的卡片（优先Level2，然后Level3）
        for (var i = 0; i < cardModel.count; i++) {
            var item = cardModel.get(i)
            var card = item.data
            
            if (card.type === "level2") {
                var status = card["Json B样式"] && card["Json B样式"]["任务状态"]
                if (status === "waiting" || status === "running") {
                    return card
                }
            }
        }
        
        // 如果没有Level2任务，查找Level3计划
        for (var i = 0; i < cardModel.count; i++) {
            var item = cardModel.get(i)
            var card = item.data
            
            if (card.type === "level3") {
                var status = card["Json A样式"] && card["Json A样式"]["计划状态"]
                if (status === "planning" || status === "running") {
                    return card
                }
            }
        }
        
        return null
    }
    
    // 辅助函数：深度合并对象
    function mergeObjects(target, source) {
        for (var key in source) {
            if (source.hasOwnProperty(key)) {
                if (typeof source[key] === 'object' && source[key] !== null && !Array.isArray(source[key])) {
                    if (!target[key] || typeof target[key] !== 'object') {
                        target[key] = {}
                    }
                    mergeObjects(target[key], source[key])
                } else {
                    target[key] = source[key]
                }
            }
        }
    }
} 