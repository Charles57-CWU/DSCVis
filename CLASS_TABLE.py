from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QBrush
import numpy as np


# def show_hide_classes(dataset, class_table, plot):
#     for i in range(dataset.class_count):
#         if class_table.item(i, 1).checkState() == Qt.CheckState.Checked:
#             dataset.active_classes[i] = True
#         else:
#             dataset.active_classes[i] = False
#
#         if class_table.item(i, 2).checkState() == Qt.CheckState.Checked:
#             dataset.active_markers[i] = True
#         else:
#             dataset.active_markers[i] = False
#
#         plot.update()


def table_swap(table, dataset, plot, event):
    moved_from = table.currentRow()
    from_item = table.item(moved_from, 0).text()
    moved_to = table.rowAt(event.pos().y())
    to_item = table.item(moved_to, 0).text()

    from_rgb = dataset.class_colors[moved_to]
    table.item(moved_from, 0).setText(to_item)
    table.item(moved_from, 0).setForeground(QBrush(QColor(from_rgb[0], from_rgb[1], from_rgb[2])))

    to_rgb = dataset.class_colors[moved_from]
    table.item(moved_to, 0).setText(from_item)
    table.item(moved_to, 0).setForeground(QBrush(QColor(to_rgb[0], to_rgb[1], to_rgb[2])))

    # place_holder = dataset.class_names[moved_from]
    # dataset.class_names[moved_from] = dataset.class_names[moved_to]
    # dataset.class_names[moved_to] = place_holder

    place_holder = dataset.class_order[moved_from]
    dataset.class_order[moved_from] = dataset.class_order[moved_to]
    dataset.class_order[moved_to] = place_holder

    place_holder = dataset.class_colors[moved_from]
    dataset.class_colors[moved_from] = dataset.class_colors[moved_to]
    dataset.class_colors[moved_to] = place_holder

    plot.update()


class ClassTable(QtWidgets.QTableWidget):
    refresh_GUI = pyqtSignal()

    def __init__(self, dataset, parent=None):
        super(ClassTable, self).__init__(parent)

        self.data = dataset
        self.refresh_GUI.connect(self.parent().refresh)

        self.setRowCount(dataset.class_count)
        self.setColumnCount(4)

        self.setHorizontalHeaderItem(0, QtWidgets.QTableWidgetItem('Class Order'))
        self.setHorizontalHeaderItem(1, QtWidgets.QTableWidgetItem('Class'))
        self.setHorizontalHeaderItem(2, QtWidgets.QTableWidgetItem('Markers'))
        self.setHorizontalHeaderItem(3, QtWidgets.QTableWidgetItem('Color'))

        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

        class_header = self.horizontalHeader()
        class_header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        class_header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)

        counter = 0
        for ele in dataset.class_names:
            class_name = QtWidgets.QTableWidgetItem(str(ele))
            class_name.setForeground(
                QBrush(QColor(dataset.class_colors[counter][0], dataset.class_colors[counter][1],
                              dataset.class_colors[counter][2])))
            self.setItem(counter, 0, class_name)

            class_checkbox = CheckBox(counter, self.data, self.refresh_GUI, 'class', parent=self)
            self.setCellWidget(counter, 1, class_checkbox)

            marker_checkbox = CheckBox(counter, self.data, self.refresh_GUI, 'marker', parent=self)
            self.setCellWidget(counter, 2, marker_checkbox)

            button = Button(counter, self.data, self.refresh_GUI, parent=self)
            self.setCellWidget(counter, 3, button)

            counter += 1


class Button(QtWidgets.QPushButton):
    def __init__(self, row, dataset, refresh, parent=None):
        super(Button, self).__init__(parent=parent)

        self.setText('Color')
        self.index = row
        self.cell = self.parent().item(self.index, 0)
        self.data = dataset
        self.r = refresh
        self.clicked.connect(self.color_dialog)

    def color_dialog(self):
        color = QtWidgets.QColorDialog.getColor()
        rgb = color.getRgb()
        self.cell.setForeground(QBrush(QColor(rgb[0], rgb[1], rgb[2])))
        self.data.class_colors[self.index] = [rgb[0], rgb[1], rgb[2]]


class CheckBox(QtWidgets.QCheckBox):
    def __init__(self, row, dataset, refresh, option, parent=None):
        super(CheckBox, self).__init__(parent)
        self.index = row
        self.data = dataset
        self.r = refresh
        self.option = option
        self.setCheckState(Qt.CheckState.Checked)
        self.stateChanged.connect(self.show_hide_classes)

    def show_hide_classes(self):
        if self.isChecked():
            if self.option == 'class':
                self.data.active_classes[self.index] = True
            else:
                self.data.active_markers[self.index] = True
        else:
            if self.option == 'class':
                self.data.active_classes[self.index] = False
            else:
                self.data.active_markers[self.index] = False

        self.r.emit()




