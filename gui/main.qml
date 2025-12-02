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

    Column {
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
            TextField { id: startDate; placeholderText: "YYYY-MM-DD" } // move to datepicker when possible

            Label { text: "End Date:" }
            TextField { id: endDate; placeholderText: "YYYY-MM-DD" }
        }

         FileDialog {
            id: saveDialog
            title: "Save file as..."
            fileMode: FileDialog.SaveFile 
            nameFilters: ["CSV files (*.csv)"]

            onAccepted: {
                console.log("Chosen save path:", selectedFile)
            }
        }

        Button {
            text: "Save As..."
            onClicked: saveDialog.open()
        }
    

        Button {
            id: go
            text: "Start data collection"
            
            Layout.fillWidth: true

            onClicked: {
                // move to python

                var selected = []
                for (var i = 0; i < forumsModel.count; i++) {
                    var cb = forumsModel.get(i);
                    if (cb.checked){
                        selected.push(cb.text);
                    }
                }

                backend.on_spider_start(selected,search.text,startDate.text,endDate.text, saveDialog.selectedFile )
            }
        }

    }

}
