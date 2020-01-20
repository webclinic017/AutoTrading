# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'open_order.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_OpenOrd(object):
    def setupUi(self, OpenOrd):
        OpenOrd.setObjectName("OpenOrd")
        OpenOrd.resize(276, 327)
        self.gridLayout = QtWidgets.QGridLayout(OpenOrd)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(OpenOrd)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.comboBox = QtWidgets.QComboBox(OpenOrd)
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.gridLayout.addWidget(self.comboBox, 0, 1, 1, 1)
        self.radioButton = QtWidgets.QRadioButton(OpenOrd)
        self.radioButton.setObjectName("radioButton")
        self.gridLayout.addWidget(self.radioButton, 1, 0, 1, 1)
        self.radioButton_2 = QtWidgets.QRadioButton(OpenOrd)
        self.radioButton_2.setObjectName("radioButton_2")
        self.gridLayout.addWidget(self.radioButton_2, 1, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(OpenOrd)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 1)
        self.lineEdit = QtWidgets.QLineEdit(OpenOrd)
        self.lineEdit.setObjectName("lineEdit")
        self.gridLayout.addWidget(self.lineEdit, 2, 1, 1, 1)
        self.label_6 = QtWidgets.QLabel(OpenOrd)
        self.label_6.setObjectName("label_6")
        self.gridLayout.addWidget(self.label_6, 3, 0, 1, 1)
        self.lineEdit_2 = QtWidgets.QLineEdit(OpenOrd)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.gridLayout.addWidget(self.lineEdit_2, 3, 1, 1, 1)
        self.checkBox = QtWidgets.QCheckBox(OpenOrd)
        self.checkBox.setObjectName("checkBox")
        self.gridLayout.addWidget(self.checkBox, 4, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(OpenOrd)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 5, 0, 1, 1)
        self.lineEdit_3 = QtWidgets.QLineEdit(OpenOrd)
        self.lineEdit_3.setEnabled(False)
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.gridLayout.addWidget(self.lineEdit_3, 5, 1, 1, 1)
        self.checkBox_2 = QtWidgets.QCheckBox(OpenOrd)
        self.checkBox_2.setObjectName("checkBox_2")
        self.gridLayout.addWidget(self.checkBox_2, 6, 0, 1, 2)
        self.label_4 = QtWidgets.QLabel(OpenOrd)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 7, 0, 1, 1)
        self.lineEdit_4 = QtWidgets.QLineEdit(OpenOrd)
        self.lineEdit_4.setEnabled(False)
        self.lineEdit_4.setObjectName("lineEdit_4")
        self.gridLayout.addWidget(self.lineEdit_4, 7, 1, 1, 1)
        self.label_5 = QtWidgets.QLabel(OpenOrd)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 8, 0, 1, 1)
        self.lineEdit_5 = QtWidgets.QLineEdit(OpenOrd)
        self.lineEdit_5.setEnabled(True)
        self.lineEdit_5.setObjectName("lineEdit_5")
        self.gridLayout.addWidget(self.lineEdit_5, 8, 1, 1, 1)
        self.checkBox_3 = QtWidgets.QCheckBox(OpenOrd)
        self.checkBox_3.setObjectName("checkBox_3")
        self.gridLayout.addWidget(self.checkBox_3, 9, 0, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(OpenOrd)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 10, 1, 1, 1)

        self.retranslateUi(OpenOrd)
        self.buttonBox.accepted.connect(OpenOrd.accept)
        self.buttonBox.rejected.connect(OpenOrd.reject)
        QtCore.QMetaObject.connectSlotsByName(OpenOrd)

    def retranslateUi(self, OpenOrd):
        _translate = QtCore.QCoreApplication.translate
        OpenOrd.setWindowTitle(_translate("OpenOrd", "Dialog"))
        self.label.setText(_translate("OpenOrd", "Symbol"))
        self.comboBox.setItemText(0, _translate("OpenOrd", "EUR/USD"))
        self.radioButton.setText(_translate("OpenOrd", "Long"))
        self.radioButton_2.setText(_translate("OpenOrd", "Short"))
        self.label_2.setText(_translate("OpenOrd", "Amoiunt"))
        self.label_6.setText(_translate("OpenOrd", "Rate"))
        self.checkBox.setText(_translate("OpenOrd", "Stop"))
        self.label_3.setText(_translate("OpenOrd", "Stop"))
        self.checkBox_2.setText(_translate("OpenOrd", "Trailing Step"))
        self.label_4.setText(_translate("OpenOrd", "Trailing Step"))
        self.label_5.setText(_translate("OpenOrd", "Limit"))
        self.checkBox_3.setText(_translate("OpenOrd", "In pips"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    OpenOrd = QtWidgets.QDialog()
    ui = Ui_OpenOrd()
    ui.setupUi(OpenOrd)
    OpenOrd.show()
    sys.exit(app.exec_())
