# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'edit_position_stop_limit.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_EditTradeStopLimit(object):
    def setupUi(self, EditTradeStopLimit):
        EditTradeStopLimit.setObjectName("EditTradeStopLimit")
        EditTradeStopLimit.resize(250, 291)
        self.gridLayout = QtWidgets.QGridLayout(EditTradeStopLimit)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(EditTradeStopLimit)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.comboBox = QtWidgets.QComboBox(EditTradeStopLimit)
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.gridLayout.addWidget(self.comboBox, 0, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(EditTradeStopLimit)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.lineEdit = QtWidgets.QLineEdit(EditTradeStopLimit)
        self.lineEdit.setObjectName("lineEdit")
        self.gridLayout.addWidget(self.lineEdit, 1, 1, 1, 1)
        self.label_3 = QtWidgets.QLabel(EditTradeStopLimit)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.lineEdit_2 = QtWidgets.QLineEdit(EditTradeStopLimit)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.gridLayout.addWidget(self.lineEdit_2, 2, 1, 1, 1)
        self.checkBox = QtWidgets.QCheckBox(EditTradeStopLimit)
        self.checkBox.setObjectName("checkBox")
        self.gridLayout.addWidget(self.checkBox, 3, 0, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(EditTradeStopLimit)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 4, 0, 1, 2)

        self.retranslateUi(EditTradeStopLimit)
        self.buttonBox.accepted.connect(EditTradeStopLimit.accept)
        self.buttonBox.rejected.connect(EditTradeStopLimit.reject)
        QtCore.QMetaObject.connectSlotsByName(EditTradeStopLimit)

    def retranslateUi(self, EditTradeStopLimit):
        _translate = QtCore.QCoreApplication.translate
        EditTradeStopLimit.setWindowTitle(_translate("EditTradeStopLimit", "Dialog"))
        self.label.setText(_translate("EditTradeStopLimit", "Change parameter"))
        self.comboBox.setItemText(0, _translate("EditTradeStopLimit", "Stop"))
        self.comboBox.setItemText(1, _translate("EditTradeStopLimit", "Limit"))
        self.label_2.setText(_translate("EditTradeStopLimit", "Rate"))
        self.label_3.setText(_translate("EditTradeStopLimit", "Trailing Step"))
        self.checkBox.setText(_translate("EditTradeStopLimit", "In pips"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    EditTradeStopLimit = QtWidgets.QDialog()
    ui = Ui_EditTradeStopLimit()
    ui.setupUi(EditTradeStopLimit)
    EditTradeStopLimit.show()
    sys.exit(app.exec_())
