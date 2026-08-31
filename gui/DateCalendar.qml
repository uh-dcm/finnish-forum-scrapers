import QtQuick 2.12
import QtQuick.Layouts 1.12
import QtQuick.Controls 2.12
import QtQuick.Controls.Basic as Basic

Rectangle {
    id: root
    width: 340
    height: 360
    color: "#ffffff"
    radius: 10
    border.color: "#e2e8f0"
    border.width: 1

    // Accessibility: Set the root component as a Calendar for assistive technologies
    Accessible.role: Accessible.Client
    Accessible.name: "Calendar"
    Accessible.description: "Date picker calendar. Use arrow keys to navigate dates."

    property date selectedDate: new Date()
    property date minimumDate: new Date(1900, 0, 1)
    property date maximumDate: new Date(2100, 11, 31)

    property int visibleMonth: selectedDate.getMonth()
    property int visibleYear: selectedDate.getFullYear()

    signal clicked(date date)

    function showPreviousMonth() {
        if (visibleMonth === 0) {
            visibleMonth = 11
            visibleYear--
        } else {
            visibleMonth--
        }
    }

    function showNextMonth() {
        if (visibleMonth === 11) {
            visibleMonth = 0
            visibleYear++
        } else {
            visibleMonth++
        }
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 12
        spacing: 12

        // --- Navigation Bar ---
        RowLayout {
            Layout.fillWidth: true
            spacing: 6

            // Previous Button
            Rectangle {
                width: 36
                height: 36
                radius: 6
                color: prevBtnMouseArea.containsMouse ? "#f1f5f9" : "transparent"
                
                Accessible.role: Accessible.PushButton
                Accessible.name: "Previous month"
                Accessible.onPressAction: root.showPreviousMonth()

                Text {
                    anchors.centerIn: parent
                    text: "‹"
                    font.pixelSize: 24
                    font.bold: true
                    color: "#475569"
                }

                MouseArea {
                    id: prevBtnMouseArea
                    anchors.fill: parent
                    onClicked: root.showPreviousMonth()
                    cursorShape: Qt.PointingHandCursor
                    hoverEnabled: true
                }
            }

            // Month Selector Button
            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                radius: 6
                color: monthBtnMouseArea.containsMouse ? "#f1f5f9" : "transparent"

                Accessible.role: Accessible.PushButton
                Accessible.name: "Select month. Current month is " + Qt.locale().standaloneMonthName(root.visibleMonth, Locale.LongFormat)
                Accessible.onPressAction: monthPopup.open()

                Row {
                    anchors.centerIn: parent
                    spacing: 4

                    Text {
                        text: Qt.locale().standaloneMonthName(root.visibleMonth, Locale.LongFormat)
                        font.pixelSize: 16
                        font.bold: true
                        color: "#1e293b"
                    }
                    
                    Text {
                        text: "▼"
                        font.pixelSize: 8
                        color: "#64748b"
                        anchors.verticalCenter: parent.verticalCenter
                        anchors.verticalCenterOffset: 2
                    }
                }

                MouseArea {
                    id: monthBtnMouseArea
                    anchors.fill: parent
                    onClicked: monthPopup.open()
                    cursorShape: Qt.PointingHandCursor
                    hoverEnabled: true
                }
            }

            // Year Selector Button
            Rectangle {
                width: 70
                height: 36
                radius: 6
                color: yearBtnMouseArea.containsMouse ? "#f1f5f9" : "transparent"

                Accessible.role: Accessible.PushButton
                Accessible.name: "Select year. Current year is " + root.visibleYear
                Accessible.onPressAction: yearPopup.open()

                Row {
                    anchors.centerIn: parent
                    spacing: 4

                    Text {
                        text: root.visibleYear
                        font.pixelSize: 16
                        font.bold: true
                        color: "#1e293b"
                    }
                    
                    Text {
                        text: "▼"
                        font.pixelSize: 8
                        color: "#64748b"
                        anchors.verticalCenter: parent.verticalCenter
                        anchors.verticalCenterOffset: 2
                    }
                }

                MouseArea {
                    id: yearBtnMouseArea
                    anchors.fill: parent
                    onClicked: yearPopup.open()
                    cursorShape: Qt.PointingHandCursor
                    hoverEnabled: true
                }
            }

            // Next Button
            Rectangle {
                width: 36
                height: 36
                radius: 6
                color: nextBtnMouseArea.containsMouse ? "#f1f5f9" : "transparent"

                Accessible.role: Accessible.PushButton
                Accessible.name: "Next month"
                Accessible.onPressAction: root.showNextMonth()

                Text {
                    anchors.centerIn: parent
                    text: "›"
                    font.pixelSize: 24
                    font.bold: true
                    color: "#475569"
                }

                MouseArea {
                    id: nextBtnMouseArea
                    anchors.fill: parent
                    onClicked: root.showNextMonth()
                    cursorShape: Qt.PointingHandCursor
                    hoverEnabled: true
                }
            }
        }

        // --- Calendar Grid Area ---
        GridLayout {
            columns: 2
            columnSpacing: 8
            rowSpacing: 8
            Layout.fillWidth: true
            Layout.fillHeight: true

            Basic.DayOfWeekRow {
                locale: grid.locale
                Layout.column: 1
                Layout.fillWidth: true
                
                delegate: Text {
                    text: model.shortName
                    color: "#64748b"
                    font.pixelSize: 12
                    font.bold: true
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    
                    Accessible.role: Accessible.StaticText
                    Accessible.name: model.longName
                }
            }

            Basic.WeekNumberColumn {
                month: grid.month
                year: grid.year
                locale: grid.locale
                Layout.row: 1
                Layout.fillHeight: true

                delegate: Text {
                    text: model.weekNumber
                    color: "#94a3b8"
                    font.pixelSize: 11
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
            }

            Basic.MonthGrid {
                id: grid
                month: root.visibleMonth
                year: root.visibleYear
                locale: Qt.locale()

                Layout.column: 1
                Layout.row: 1
                Layout.fillWidth: true
                Layout.fillHeight: true

                spacing: 4

                delegate: Rectangle {
                    id: cell
                    property bool isSelected: model.date.getTime() === root.selectedDate.getTime()
                    property bool isHovered: cellMouseArea.containsMouse
                    property bool isValid: model.date >= root.minimumDate && model.date <= root.maximumDate
                    property bool isCurrentMonth: model.month === grid.month

                    color: "transparent"
                    radius: 6

                    Rectangle {
                        anchors.centerIn: parent
                        width: Math.min(parent.width, parent.height) * 0.85
                        height: width
                        radius: width / 2
                        
                        color: {
                            if (isSelected) return "#4f46e5";
                            if (isHovered && isValid) return "#e0e7ff";
                            if (model.today) return "#fef9c3";
                            return "transparent";
                        }
                        
                        border.color: model.today && !isSelected ? "#facc15" : "transparent"
                        border.width: 1

                        Behavior on color { ColorAnimation { duration: 100 } }
                    }

                    Text {
                        anchors.centerIn: parent
                        text: model.day
                        font.pixelSize: 14
                        font.bold: model.today || isSelected
                        
                        color: {
                            if (isSelected) return "#ffffff";
                            if (!isCurrentMonth) return "#cbd5e1";
                            if (model.today) return "#854d0e";
                            return "#334155";
                        }
                        
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }

                    MouseArea {
                        id: cellMouseArea
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: isValid ? Qt.PointingHandCursor : Qt.ArrowCursor
                        onClicked: {
                            if (isValid) {
                                root.selectedDate = model.date
                                root.clicked(model.date)
                                cell.forceActiveFocus()
                            }
                        }
                    }

                    Accessible.role: Accessible.PushButton
                    Accessible.name: model.date.toLocaleDateString(Qt.locale(), "dddd, MMMM d, yyyy")
                    Accessible.description: isSelected ? "Selected date" : (model.today ? "Today" : "Date")
                    Accessible.focusable: isValid
                    Accessible.selectable: true
                    Accessible.selected: isSelected
                    
                    Keys.onPressed: {
                        if (!isValid) return;
                        
                        var newDate = new Date(model.date);
                        
                        if (event.key === Qt.Key_Left) newDate.setDate(newDate.getDate() - 1);
                        else if (event.key === Qt.Key_Right) newDate.setDate(newDate.getDate() + 1);
                        else if (event.key === Qt.Key_Up) newDate.setDate(newDate.getDate() - 7);
                        else if (event.key === Qt.Key_Down) newDate.setDate(newDate.getDate() + 7);
                        else if (event.key === Qt.Key_Return || event.key === Qt.Key_Enter) {
                            root.selectedDate = model.date;
                            root.clicked(model.date);
                            event.accepted = true;
                            return;
                        } else {
                            return;
                        }
                        
                        if (newDate >= root.minimumDate && newDate <= root.maximumDate) {
                            root.selectedDate = newDate;
                            root.clicked(newDate);
                            
                            if (newDate.getMonth() !== root.visibleMonth || newDate.getFullYear() !== root.visibleYear) {
                                root.visibleMonth = newDate.getMonth();
                                root.visibleYear = newDate.getFullYear();
                            }
                            event.accepted = true;
                        }
                    }

                    Rectangle {
                        anchors.fill: parent
                        radius: parent.radius
                        color: "transparent"
                        border.color: "#3b82f4"
                        border.width: 2
                        visible: cell.activeFocus && isValid
                    }
                }
            }
        }
    }

    // --- Month Selection Popup ---
    Popup {
        id: monthPopup
        x: (root.width - width) / 2
        y: 60
        width: 220
        height: 200
        modal: true
        focus: true
        closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside

        background: Rectangle {
            color: "#ffffff"
            radius: 8
            border.color: "#e2e8f0"
            border.width: 1
        }

        GridLayout {
            anchors.fill: parent
            columns: 3
            rowSpacing: 4
            columnSpacing: 4

            Repeater {
                model: 12
                delegate: Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    radius: 4
                    color: monthMouseArea.containsMouse ? "#e0e7ff" : (index === root.visibleMonth ? "#eef2ff" : "transparent")

                    Text {
                        anchors.centerIn: parent
                        text: Qt.locale().standaloneMonthName(index, Locale.ShortFormat)
                        color: index === root.visibleMonth ? "#4f46e5" : "#334155"
                        font.bold: index === root.visibleMonth
                    }

                    MouseArea {
                        id: monthMouseArea
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: {
                            root.visibleMonth = index
                            monthPopup.close()
                        }
                    }
                }
            }
        }
    }

    // --- Year Selection Popup ---
    Popup {
        id: yearPopup
        x: (root.width - width) / 2
        y: 60
        width: 100
        height: 240
        modal: true
        focus: true
        closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside

        background: Rectangle {
            color: "#ffffff"
            radius: 8
            border.color: "#e2e8f0"
            border.width: 1
        }

        ListView {
            id: yearListView
            anchors.fill: parent
            anchors.margins: 4
            clip: true
            
            // Generates an array of valid years from minimumDate to maximumDate
            model: {
                var years = []
                for (var y = root.minimumDate.getFullYear(); y <= root.maximumDate.getFullYear(); y++) {
                    years.push(y)
                }
                return years
            }
            
            currentIndex: root.visibleYear - root.minimumDate.getFullYear()

            delegate: ItemDelegate {
                width: yearListView.width
                height: 36
                
                text: modelData
                font.pixelSize: 14
                font.bold: modelData === root.visibleYear
                
                highlighted: modelData === root.visibleYear
                
                onClicked: {
                    root.visibleYear = modelData
                    yearPopup.close()
                }
            }

            ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }
        }

        // Ensure the list scrolls to the currently visible year when opened
        onOpened: {
            Qt.callLater(function() {
                yearListView.positionViewAtIndex(yearListView.currentIndex, ListView.Center)
            })
        }
    }
}