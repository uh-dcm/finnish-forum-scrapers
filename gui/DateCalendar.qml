import QtQuick 2.12
import QtQuick.Layouts 1.12
import QtQuick.Controls 2.12
import QtQuick.Controls.Basic as Basic

Rectangle {
    id: root
    width: 320
    height: 340
    color: "white"
    radius: 6
    border.color: "#cccccc"
    border.width: 1

    property date selectedDate: new Date()
    property date minimumDate: new Date(1900, 0, 1)
    property date maximumDate: new Date(2100, 11, 31)

    // visible month/year (0-11 indexed month, matching the Calendar API)
    property int visibleMonth: selectedDate.getMonth()
    property int visibleYear: selectedDate.getFullYear()

    // Emitted when the mouse is clicked on a valid date in the calendar.
    signal clicked(date date)

    function showPreviousMonth() {
        if (visibleMonth == 0) {
            visibleMonth = 11
            visibleYear--
        } else {
            visibleMonth--
        }
    }

    function showNextMonth() {
        if (visibleMonth == 11) {
            visibleMonth = 0
            visibleYear++
        } else {
            visibleMonth++
        }
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 8

        // Navigation bar
        RowLayout {
            Layout.fillWidth: true

            Button {
                text: "<"
                onClicked: root.showPreviousMonth()
            }

            Label {
                Layout.fillWidth: true
                horizontalAlignment: Text.AlignHCenter
                text: Qt.locale().standaloneMonthName(root.visibleMonth, Locale.ShortFormat) + " " + root.visibleYear
                font.bold: true
            }

            Button {
                text: ">"
                onClicked: root.showNextMonth()
            }
        }

        GridLayout {
            columns: 2
            columnSpacing: 4
            Layout.fillWidth: true
            Layout.fillHeight: true

            Basic.DayOfWeekRow {
                locale: grid.locale

                Layout.column: 1
                Layout.fillWidth: true
            }

            Basic.WeekNumberColumn {
                month: grid.month
                year: grid.year
                locale: grid.locale

                Layout.fillHeight: true
            }

            Basic.MonthGrid {
                id: grid
                month: root.visibleMonth
                year: root.visibleYear
                locale: Qt.locale()

                Layout.fillWidth: true
                Layout.fillHeight: true

                delegate: Rectangle {
                    id: cell
                    color: paintColor()
                    required property var model

                    function paintColor() {
                        if (model.date.getTime() === root.selectedDate.getTime())
                            return "#3b82c4"
                        if (model.today)
                            return "#ffeaa7"
                        return "transparent"
                    }

                    Text {
                        anchors.centerIn: parent
                        text: model.day
                        opacity: model.month === grid.month ? 1 : 0
                        color: model.date.getTime() === root.selectedDate.getTime() ? "white" : "black"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        font: grid.font
                    }

                    MouseArea {
                        anchors.fill: parent
                        onClicked: {
                            if (model.date >= root.minimumDate && model.date <= root.maximumDate) {
                                root.selectedDate = model.date
                                root.clicked(model.date)
                            }
                        }
                        cursorShape: Qt.PointingHandCursor
                    }
                }
            }
        }
    }
}