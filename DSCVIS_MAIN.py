"""
DSV_MAIN.py is the main python script to execute and holds information related to the GUI and dataset

Author: Charles Recaido
Program: MSc in Computational Science
School: Central Washington University
"""

from PyQt5 import QtWidgets
from PyQt5 import uic
import numpy as np
import sys
from PyQt5 import sip

import GET_DATA
import DATA_DISPLAY
import CLASS_TABLE
import ATTRIBUTE_TABLE
import PLOT_CONTEXT
import CLIPPING
import WARNINGS


class Dataset(object):
    # dataset info
    name = ''
    dataframe = None

    # class information
    class_count = 0
    count_per_class = []
    class_names = []
    class_colors = []
    # attribute information
    attribute_count = 0
    attribute_names = []
    attribute_alpha = 255  # for attribute slider
    # sample information
    sample_count = 0
    clipped_samples = []  # for line clip option
    vertex_in = []  # for vertex clip option
    last_vertex_in = []  # for last vertex clip option

    # plot information
    plot_type = ''
    positions = []
    axis_positions = []
    axis_on = True
    axis_count = 0
    vertex_count = 0  # number of vertices depends on plot type

    active_attributes = []  # show/hide markers by attribute
    active_classes = []  # show/hide classes
    active_markers = []  # show/hide markers by class

    class_order = []  # choose which class is on top
    attribute_order = []  # choose attribute order (requires running graph construction algorithm again)


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        # load Ui from ui File made in QTDesigner
        uic.loadUi('visualizationGui1.ui', self)
        self.plot_layout = None
        self.plot_widget = None
        self.data = None
        self.data_uploaded = False

        self.warnings = WARNINGS.getWarning()

        # ====================================== buttons ======================================
        # file upload button
        self.upload_button = self.findChild(QtWidgets.QPushButton, 'uploadButton')
        self.upload_button.clicked.connect(self.upload_dataset)

        # generate plot button
        self.plot_button = self.findChild(QtWidgets.QPushButton, 'makePlotButton')
        self.plot_button.clicked.connect(self.create_plot)

        # exit button
        self.exit_button = self.findChild(QtWidgets.QPushButton, 'exitButton')
        self.exit_button.clicked.connect(self.exit_app)

        # update attribute button
        self.replot_attribute_button = self.findChild(QtWidgets.QPushButton, 'replotFeatureButton')
        self.replot_attribute_button.clicked.connect(self.replot_attributes)

        # test button
        self.test_button = self.findChild(QtWidgets.QPushButton, 'testButton')
        self.test_button.clicked.connect(self.test)

        # recenter button
        self.recenter_button = self.findChild(QtWidgets.QPushButton, 'recenterButton')
        self.recenter_button.clicked.connect(self.recenter_plot)

        # color test button
        self.remove_clip_button = self.findChild(QtWidgets.QPushButton, 'removeClipButton')
        self.remove_clip_button.clicked.connect(self.remove_clip)

        # attribute slider
        self.attribute_slide = self.findChild(QtWidgets.QSlider, 'horizontalSlider')
        self.attribute_slide.setMinimum(0)
        self.attribute_slide.setMaximum(255)
        self.attribute_slide.setValue(128)

        self.attribute_slide.valueChanged.connect(self.attr_slider)

        # plot selection
        self.pc_checked = self.findChild(QtWidgets.QRadioButton, 'pcCheck')
        self.spc_checked = self.findChild(QtWidgets.QRadioButton, 'spcCheck')
        self.dsc1_checked = self.findChild(QtWidgets.QRadioButton, 'dsc1Check')
        self.dsc2_checked = self.findChild(QtWidgets.QRadioButton, 'dsc2Check')

        # axes on/off
        self.show_axes = self.findChild(QtWidgets.QCheckBox, 'axesCheck')
        self.show_axes.stateChanged.connect(self.axes_func)

        # ====================================== tables and text boxes ======================================
        # dataset information text box
        self.dataset_textbox = self.findChild(QtWidgets.QTextBrowser, 'datasetInfoBrowser')
        self.clipped_area_textbox = self.findChild(QtWidgets.QTextBrowser, 'attributeBrowser')

        # tables
        self.class_table_layout = self.findChild(QtWidgets.QVBoxLayout, 'classTableLayout')
        self.class_table = None
        self.class_pl = self.findChild(QtWidgets.QTableWidget, 'classTablePlaceholder')
        self.class_pl_exists = True

        self.check_classes = self.findChild(QtWidgets.QPushButton, 'uncheckClasses')
        self.check_classes.clicked.connect(self.check_all_class)

        self.uncheck_classes = self.findChild(QtWidgets.QPushButton, 'checkClasses')
        self.uncheck_classes.clicked.connect(self.uncheck_all_class)

        self.attribute_table_layout = self.findChild(QtWidgets.QVBoxLayout, 'attributeTableLayout')
        self.attribute_table = None
        self.attribute_pl = self.findChild(QtWidgets.QTableWidget, 'attributeTablePlaceholder')
        self.attribute_pl_exists = True

        self.check_attributes = self.findChild(QtWidgets.QPushButton, 'checkAttributes')
        self.check_attributes.clicked.connect(self.check_all_attr)

        self.uncheck_attributes = self.findChild(QtWidgets.QPushButton, 'uncheckAttributes')
        self.uncheck_attributes.clicked.connect(self.uncheck_all_attr)

        # for swapping cells
        self.cell_swap = QtWidgets.QTableWidget()
        self.cell_swap.__class__.dropEvent = self.table_swap

        # ====================================== plot module ======================================
        self.plot_layout = self.findChild(QtWidgets.QVBoxLayout, 'plotDisplay')

        self.pl = self.findChild(QtWidgets.QWidget, 'placeHolderWidget')
        self.pl_exists = True

    def upload_dataset(self):
        if self.data_uploaded:
            del self.data
            self.data = Dataset()
        else:
            self.data = None
            self.data = Dataset()
        filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File')
        if filename[0] == '':
            return

        # GUI changes for changing datasets
        if self.data_uploaded:
            self.plot_layout.removeWidget(self.plot_widget)
            sip.delete(self.plot_widget)
            self.plot_widget = None
            self.plot_layout.addWidget(self.pl)

            self.class_table_layout.removeWidget(self.class_table)
            print(self.class_table_layout.count())
            print(self.class_table.rowCount())
            sip.delete(self.class_table)
            self.class_table = None
            self.class_table_layout.addWidget(self.class_pl)
            self.class_pl_exists = True

            self.attribute_table_layout.removeWidget(self.attribute_table)
            sip.delete(self.attribute_table)
            self.attribute_table = None
            self.attribute_table_layout.addWidget(self.attribute_pl)
            self.attribute_pl_exists = True

            self.pl_exists = True

        GET_DATA.GetData(self.data, filename[0])
        DATA_DISPLAY.DisplayData(self.data, self.dataset_textbox)
        self.class_table = CLASS_TABLE.ClassTable(self.data, parent=self)
        self.data_uploaded = True

    # ====================================== create plots ======================================
    def create_plot(self):
        if not self.data_uploaded:
            self.warnings.noDataWarning()
            return

        # remove initial placeholder
        if not self.pl_exists:
            self.plot_layout.removeWidget(self.plot_widget)
            self.plot_layout.addWidget(self.pl)
            self.pl_exists = True

        self.data.positions = []

        # draw PC plot
        if self.pc_checked.isChecked():
            self.data.plot_type = 'PC'
            self.plot_widget = PLOT_CONTEXT.MakePlot(self.data, parent=self)

        # draw DSC1 plot
        if self.dsc1_checked.isChecked():
            self.data.plot_type = 'DSC1'
            self.plot_widget = PLOT_CONTEXT.MakePlot(self.data, parent=self)

        # draw DSC2 plot
        if self.dsc2_checked.isChecked():
            if self.data.attribute_count % 2 != 0:
                print('This plot requires an even feature count.')
                return
            self.data.plot_type = 'DSC2'
            self.plot_widget = PLOT_CONTEXT.MakePlot(self.data, parent=self)

        # draw SPC plot
        if self.spc_checked.isChecked():
            if self.data.attribute_count % 2 != 0:
                print('This plot requires an even feature count.')
                return
            self.data.plot_type = 'SPC'
            self.plot_widget = PLOT_CONTEXT.MakePlot(self.data, parent=self)

        # class table placeholder
        if self.class_pl_exists:
            self.class_table_layout.removeWidget(self.class_pl)
            self.class_table_layout.addWidget(self.class_table)
            self.class_pl_exists = False

        # attribute table placeholder
        if self.attribute_pl_exists:
            self.attribute_table_layout.removeWidget(self.attribute_pl)
            self.attribute_pl_exists = False
        else:
            self.attribute_table_layout.removeWidget(self.attribute_table)

        self.attribute_table = ATTRIBUTE_TABLE.AttributeTable(self.data, parent=self)
        self.attribute_table_layout.addWidget(self.attribute_table)

        # plot placeholder
        if self.pl_exists:
            self.plot_layout.removeWidget(self.pl)
            self.pl_exists = False

        self.plot_layout.addWidget(self.plot_widget)

    # exit the app
    def exit_app(self):
        print("Exit pressed")
        self.close()

    # function to save clip files
    def test(self):
        if not self.data_uploaded:
            self.warnings.noDataWarning()
            return

        CLIPPING.clip_files(self.data, self.clipped_area_textbox)

    # function remove clip and reset variables
    def remove_clip(self):
        if not self.data_uploaded:
            self.warnings.noDataWarning()
            return

        self.data.clipped_samples = np.zeros(self.data.sample_count)
        self.data.vertex_in = np.zeros(self.data.sample_count)
        self.data.last_vertex_in = np.zeros(self.data.sample_count)
        self.plot_widget.rect = []
        self.plot_widget.all_rect = []

        self.clipped_area_textbox.setText('')

        self.plot_widget.update()

    # function to help with reordering tables when user swaps rows
    def table_swap(self, event):
        table = event.source()

        if table == self.class_table:
            CLASS_TABLE.table_swap(table, self.data, self.plot_widget, event)
        elif table == self.attribute_table:
            ATTRIBUTE_TABLE.table_swap(table, self.data, event)

        event.accept()

    # function to reorder attributes
    # reordering attributes requires running the GCA again
    def replot_attributes(self):
        if not self.data_uploaded:
            self.warnings.noDataWarning()
            return

        self.data.attribute_names.append('class')
        self.data.dataframe = self.data.dataframe[self.data.attribute_names]

        self.data.attribute_names.pop()
        self.data.positions = []
        self.data.active_attributes = np.repeat(True, self.data.attribute_count)
        ATTRIBUTE_TABLE.reset_checkmarks(self.attribute_table, self.data.vertex_count, self.data.plot_type)
        self.create_plot()

    def axes_func(self):
        if not self.data_uploaded:
            self.warnings.noDataWarning()
            return

        if self.show_axes.isChecked():
            self.data.axis_on = True
        else:
            self.data.axis_on = False

        self.refresh()

    # function to refresh plot
    def refresh(self):
        self.plot_widget.update()

    def check_all_attr(self):
        if not self.data_uploaded:
            self.warnings.noDataWarning()
            return
        ATTRIBUTE_TABLE.reset_checkmarks(self.attribute_table, self.data.vertex_count, self.data.plot_type)

    def check_all_class(self):
        if not self.data_uploaded:
            self.warnings.noDataWarning()
            return
        CLASS_TABLE.reset_checkmarks(self.class_table, self.data.class_count)

    def uncheck_all_attr(self):
        if not self.data_uploaded:
            self.warnings.noDataWarning()
            return
        ATTRIBUTE_TABLE.uncheck_checkmarks(self.attribute_table, self.data.vertex_count, self.data.plot_type)

    def uncheck_all_class(self):
        if not self.data_uploaded:
            self.warnings.noDataWarning()
            return
        CLASS_TABLE.uncheck_checkmarks(self.class_table, self.data.class_count)

    def recenter_plot(self):
        if not self.data_uploaded:
            self.warnings.noDataWarning()
            return

        if not self.data.plot_type:
            return

        # for zooming
        self.plot_widget.m_left = -1.125
        self.plot_widget.m_right = 1.125
        self.plot_widget.m_bottom = -1.125
        self.plot_widget.m_top = 1.125

        self.refresh()

    # function to get alpha value for hidden attributes
    def attr_slider(self):
        if not self.data_uploaded:
            self.warnings.noDataWarning()
            return
        value = self.attribute_slide.value()
        self.data.attribute_alpha = value
        self.plot_widget.update()


app = QtWidgets.QApplication(sys.argv)
window = Ui()
window.show()
app.exec_()
