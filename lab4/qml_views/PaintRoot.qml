import QtQuick 2.0
import QtQuick.Window 2.3

import "."

Window {
    id: root
    visible: true
    width: 1000
    height: 1000
    title: "Paint!"

    Rectangle {
        id: tools
        width: parent.width
        height: 150
        color: "#545454"

        property color paintColor: "#33B5E5"
        property int thickness: 1
        property int spacing: 4

        Column {
            spacing: tools.spacing
            anchors.centerIn: parent

            Row {
                spacing: tools.spacing
                anchors.horizontalCenter: parent.horizontalCenter

                Repeater {
                    model: ["#33B5E5", "#99CC00", "#FFBB33", "#FF4444"]

                    ColorSwatchRect {
                        color: modelData
                        active: tools.paintColor === color
                        onClicked: tools.paintColor = color
                    }
                }
            }

            Row {
                spacing: tools.spacing
                anchors.horizontalCenter: parent.horizontalCenter

                Repeater {
                    model: [1, 2, 3, 4, 5]

                    StrokeWidthDot {
                        active: tools.thickness === thickness
                        thickness: modelData
                        text: String(thickness)
                        onClicked: tools.thickness = thickness
                    }
                }
            }
        }
    }

    Canvas {
        id: canvas
        objectName: "canvas"

        anchors {
            left: parent.left
            right: parent.right
            top: tools.bottom
            bottom: parent.bottom
            margins: 8
        }

        property real lastX
        property real lastY
        property color color: tools.paintColor
        property bool isInitialized: false

        function saveCanvas(filePath) {
            canvas.save(filePath)
        }

        onPaint: {
            var ctx = getContext("2d", { preserveDrawingBuffer: true })

            if (!isInitialized) {
                ctx.fillStyle = "white"
                ctx.fillRect(0, 0, canvas.width, canvas.height)
                isInitialized = true
                return
            }

            ctx.lineWidth = tools.thickness
            ctx.strokeStyle = canvas.color
            ctx.lineCap = "round"
            ctx.beginPath()
            ctx.moveTo(lastX, lastY)

            lastX = paint_area.mouseX
            lastY = paint_area.mouseY

            ctx.lineTo(lastX, lastY)
            ctx.stroke()
        }

        MouseArea {
            id: paint_area
            anchors.fill: parent

            onPressed: {
                canvas.lastX = mouseX
                canvas.lastY = mouseY
            }

            onPositionChanged: {
                canvas.requestPaint()
            }
        }
    }
}