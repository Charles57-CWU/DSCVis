"""
WARNINGS.py holds information related to various warning messages

Author: Charles Recaido
Program: MSc in Computational Science
School: Central Washington University
"""
from PyQt5 import QtWidgets


class getWarning:
    def noDataWarning(self):
        no_data_message = QtWidgets.QMessageBox()
        no_data_message.setWindowTitle('Warning: No dataset')
        no_data_message.setText('Please upload dataset before generating plot.')
        no_data_message.setIcon(QtWidgets.QMessageBox.Warning)
        no_data_message.setStandardButtons(QtWidgets.QMessageBox.Ok)

        #no_data_message.exec()

    def oddFeatureCount(self):
        no_data_message = QtWidgets.QMessageBox()
        no_data_message.setWindowTitle('Warning: Odd Feature Count')
        no_data_message.setText('This plot requires an even feature count.')
        no_data_message.setIcon(QtWidgets.QMessageBox.Warning)
        no_data_message.setStandardButtons(QtWidgets.QMessageBox.Ok)
        print('iamhere3')
        #no_data_message.exec()
