import QtCore
import QtQuick 2.12
import QtQuick.Window 2.12


// Libraries
import QtQuick.Controls 2.12
import QtQuick.Controls.Material 2.12
import QtQuick.Dialogs
import QtQuick.Layouts 1.12

ApplicationWindow {
    id: mainWindow
    visible: true
    width: 800
    height: 1000
    title: "Finnish Forum Scraper"

    function collectSelected() {
        var selected = []
        for (var i = 0; i < forumsModel.count; i++) {
            var cb = forumsModel.get(i);
            if (cb.checked){
                selected.push(cb.text);
            }
        }
        return selected
    }

    Column {
        id: form
        anchors.fill: parent
        anchors.margins: 10
        spacing: 10

        ListView {
            model: ListModel { id: forumsModel }
            id: forums
            width: parent.width
            height: 400
            
            delegate: CheckBox {
                text: model.text
                checked: model.checked
                onCheckedChanged: model.checked = checked
            }

            Component.onCompleted: {
                console.log( spiders )
                for (let i = 0; i < spiders.length; i++) {
                    forumsModel.append({
                        "text": spiders[i],
                        "checked": false
                    })
                }
            }
        }

        TextField {
            id: search
            width: parent.width
            placeholderText: "Search term"
        }

        Row {
            spacing: 10
            
            Label { text: "Start Date:" }
            TextField {
                id: startDate
                placeholderText: "YYYY-MM-DD"
                readOnly: true

                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    onClicked: startDatePopup.open()
                }
            }

            Label { text: "End Date:" }
            TextField {
                id: endDate
                placeholderText: "YYYY-MM-DD"
                readOnly: true

                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    onClicked: endDatePopup.open()
                }
            }
        }

        Popup {
            id: startDatePopup
            modal: true
            x: (mainWindow.width - width) / 2
            y: (mainWindow.height - height) / 2

            DateCalendar {
                selectedDate: (startDate.text !== "") ? Date.fromLocaleString(Qt.locale(), startDate.text, "yyyy-MM-dd") : new Date()
                onClicked: function(date) {
                    startDate.text = Qt.formatDate(date, "yyyy-MM-dd")
                    startDatePopup.close()
                }
            }
        }

        Popup {
            id: endDatePopup
            modal: true
            x: (mainWindow.width - width) / 2
            y: (mainWindow.height - height) / 2

            DateCalendar {
                selectedDate: (endDate.text !== "") ? Date.fromLocaleString(Qt.locale(), endDate.text, "yyyy-MM-dd") : new Date()
                onClicked: function(date) {
                    endDate.text = Qt.formatDate(date, "yyyy-MM-dd")
                    endDatePopup.close()
                }
            }
        }

        FileDialog {
            id: saveDialog
            title: "Save file as..."
            fileMode: FileDialog.SaveFile 
            nameFilters: ["CSV files (*.csv)"]

            onAccepted: {
                console.log("Chosen save path:", selectedFile)
                backend.on_spider_start(collectSelected(), search.text, startDate.text, endDate.text, saveDialog.selectedFile )
            }
        }

        Button {
            id: go
            text: "Start data collection"

            Layout.fillWidth: true

            onClicked: saveDialog.open()
        }
    }

    Rectangle {
        id: loadingOverlay
        anchors.fill: parent
        color: "#88777777"
        z: 10
        visible: false

        Rectangle {
            anchors.centerIn: parent
            width: 240
            height: 180
            radius: 8
            color: "white"
            border.color: "#cccccc"
            border.width: 1

            Column {
                anchors.centerIn: parent
                spacing: 12

                BusyIndicator {
                    running: loadingOverlay.visible
                    anchors.horizontalCenter: parent.horizontalCenter
                }

                Label {
                    text: "Collecting data..."
                    anchors.horizontalCenter: parent.horizontalCenter
                    font.pixelSize: 14
                }

                Button {
                    text: "Stop collection"
                    anchors.horizontalCenter: parent.horizontalCenter
                    onClicked: backend.on_spider_stop()
                    background: Rectangle {
                        implicitWidth: 140
                        implicitHeight: 36
                        radius: 4
                        color: parent.down ? "#b71c1c" : (parent.hovered ? "#e53935" : "#f44336")
                    }
                }
            }
        }
    }

    Connections {
        target: backend

        function onCollectionStarted() {
            go.enabled = false
            loadingOverlay.visible = true
        }

        function onCollectionFinished() {
            go.enabled = true
            loadingOverlay.visible = false
        }
    }

}