import QtQuick 2.0
Rectangle {
    width: 640; height: 480
    color: "lightgray"
    Text {
        id: txt
        text: "Clicked me"
        font.pixelSize: 20
        anchors.centerIn: parent
    }
    MouseArea {
        id: mouse_area
        anchors.fill: parent  // ζζεΊε
        onClicked: {
           con.outputString("Hello, Python3")
        }
    }
}