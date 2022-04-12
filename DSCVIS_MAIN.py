from PyQt5 import QtWidgets
from PyQt5 import uic
from PyQt5 import Qt
import sys
from csv import writer
import numpy as np

import GET_DATA
import DATA_DISPLAY
import CLASS_TABLE
import ATTRIBUTE_TABLE
import PLOT_CONTEXT
import UPDATE_CLASS_ORDER
import CLIPPING


class Dataset(object):
    # dataset info
    name = None
    dataframe = None

    # class information
    class_count = None
    count_per_class = []
    class_names = []
    class_colors = []
    # attribute information
    attribute_count = None
    attribute_names = []
    active_attributes = []
    vertex_count = None
    attribute_alpha = 255
    # sample information
    sample_count = None
    clipped_samples = []
    vertex_in = []
    last_vertex_in = []

    # plot information
    plot_type = None
    positions = []
    axis_positions = []
    axis_count = None

    active_classes = []  # show/hide classes
    active_markers = []  # show/hide markers
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

        # color test button
        self.color_button = self.findChild(QtWidgets.QPushButton, 'recenterButton')

        # color test button
        self.remove_clip_button = self.findChild(QtWidgets.QPushButton, 'removeClipButton')
        self.remove_clip_button.clicked.connect(self.remove_clip)

        # attribute slider
        self.attribute_slide = self.findChild(QtWidgets.QSlider, 'horizontalSlider')
        self.attribute_slide.setMinimum(0)
        self.attribute_slide.setMaximum(255)
        self.attribute_slide.setValue(128)

        self.attribute_slide.valueChanged.connect(self.attr_slider)

        # ====================================== tables and text boxes ======================================
        # dataset information text box
        self.dataset_textbox = self.findChild(QtWidgets.QTextBrowser, 'datasetInfoBrowser')
        self.clipped_area_textbox = self.findChild(QtWidgets.QTextBrowser, 'attributeBrowser')

        # tables
        self.class_table_layout = self.findChild(QtWidgets.QVBoxLayout, 'verticalLayout_7')
        self.class_table = None
        self.attribute_table_layout = self.findChild(QtWidgets.QVBoxLayout, 'verticalLayout_5')
        self.attribute_table = None
        # for swapping cells
        self.cell_swap = QtWidgets.QTableWidget()
        self.cell_swap.__class__.dropEvent = self.table_swap

        # ====================================== plot module ======================================
        self.plot_layout = self.findChild(QtWidgets.QVBoxLayout, 'plotDisplay')

        place_holder = self.findChild(QtWidgets.QWidget, 'placeHolder')
        self.plot_layout.removeWidget(place_holder)

    def upload_dataset(self):
        self.class_table_layout.removeWidget(self.class_table)
        self.attribute_table_layout.removeWidget(self.attribute_table)

        self.data = Dataset()
        filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File')

        GET_DATA.GetData(self.data, filename[0])
        DATA_DISPLAY.DisplayData(self.data, self.dataset_textbox)

        self.class_table = CLASS_TABLE.ClassTable(self.data, parent=self)
        self.class_table_layout.addWidget(self.class_table)

    # ====================================== create plots ======================================
    def create_plot(self):
        self.plot_layout.removeWidget(self.plot_widget)
        self.attribute_table_layout.removeWidget(self.attribute_table)
        self.data.positions = []

        pc_checked = self.findChild(QtWidgets.QRadioButton, 'pcCheck')
        if pc_checked.isChecked():
            self.data.plot_type = 'PC'
            self.plot_widget = PLOT_CONTEXT.MakePlot(self.data)

        dsc1_checked = self.findChild(QtWidgets.QRadioButton, 'dsc1Check')
        if dsc1_checked.isChecked():
            self.data.plot_type = 'DSC1'
            self.plot_widget = PLOT_CONTEXT.MakePlot(self.data)

        dsc2_checked = self.findChild(QtWidgets.QRadioButton, 'dsc2Check')
        if dsc2_checked.isChecked():
            self.data.plot_type = 'DSC2'
            self.plot_widget = PLOT_CONTEXT.MakePlot(self.data)

        spc_checked = self.findChild(QtWidgets.QRadioButton, 'spcCheck')
        if spc_checked.isChecked():
            self.data.plot_type = 'SPC'
            self.plot_widget = PLOT_CONTEXT.MakePlot(self.data)

        self.attribute_table = ATTRIBUTE_TABLE.AttributeTable(self.data, parent=self)
        self.attribute_table_layout.addWidget(self.attribute_table)

        self.plot_layout.addWidget(self.plot_widget)

    # exit the app
    def exit_app(self):
        print("Exit pressed")
        self.close()

    # function to save clip files
    def test(self):
        CLIPPING.clip_files(self.data, self.clipped_area_textbox)

    # function remove clip and reset variables
    def remove_clip(self):
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
        self.data.attribute_names.append('class')
        self.data.dataframe = self.data.dataframe[self.data.attribute_names]

        self.data.attribute_names.pop()
        self.data.positions = []
        self.data.active_attributes = np.repeat(True, self.data.attribute_count)
        ATTRIBUTE_TABLE.reset_checkmarks(self.attribute_table, self.data.vertex_count, self.data.plot_type)
        self.create_plot()

    # function to refresh plot
    def refresh(self):
        self.plot_widget.update()

    # function to get alpha value for hidden attributes
    def attr_slider(self):
        value = self.attribute_slide.value()
        self.data.attribute_alpha = value
        self.plot_widget.update()


app = QtWidgets.QApplication(sys.argv)
window = Ui()
window.show()
app.exec_()
