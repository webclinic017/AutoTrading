# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'edit_popup.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_EditPosition(object):
    def setupUi(self, EditPosition):
        EditPosition.setObjectName("EditPosition")
        EditPosition.resize(240, 253)
        self.gridLayout = QtWidgets.QGridLayout(EditPosition)
        self.gridLayout.setObjectName("gridLayout")
        self.lineEdit_2 = QtWidgets.QLineEdit(EditPosition)
        self.lineEdit_2.setEnabled(False)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.gridLayout.addWidget(self.lineEdit_2, 2, 1, 1, 1)
        self.checkBox_3 = QtWidgets.QCheckBox(EditPosition)
        self.checkBox_3.setObjectName("checkBox_3")
        self.gridLayout.addWidget(self.checkBox_3, 6, 0, 1, 2)
        self.buttonBox = QtWidgets.QDialogButtonBox(EditPosition)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 8, 0, 1, 2)
        self.lineEdit = QtWidgets.QLineEdit(EditPosition)
        self.lineEdit.setObjectName("lineEdit")
        self.gridLayout.addWidget(self.lineEdit, 0, 1, 1, 1)
        self.checkBox_2 = QtWidgets.QCheckBox(EditPosition)
        self.checkBox_2.setObjectName("checkBox_2")
        self.gridLayout.addWidget(self.checkBox_2, 3, 0, 1, 1)
        self.lineEdit_3 = QtWidgets.QLineEdit(EditPosition)
        self.lineEdit_3.setEnabled(False)
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.gridLayout.addWidget(self.lineEdit_3, 5, 1, 1, 1)
        self.lineEdit_4 = QtWidgets.QLineEdit(EditPosition)
        self.lineEdit_4.setEnabled(False)
        self.lineEdit_4.setObjectName("lineEdit_4")
        self.gridLayout.addWidget(self.lineEdit_4, 7, 1, 1, 1)
        self.label_4 = QtWidgets.QLabel(EditPosition)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 7, 0, 1, 1, QtCore.Qt.AlignHCenter)
        self.label = QtWidgets.QLabel(EditPosition)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1, QtCore.Qt.AlignHCenter)
        self.checkBox = QtWidgets.QCheckBox(EditPosition)
        self.checkBox.setObjectName("checkBox")
        self.gridLayout.addWidget(self.checkBox, 1, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(EditPosition)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 1, QtCore.Qt.AlignHCenter)
        self.label_3 = QtWidgets.QLabel(EditPosition)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 5, 0, 1, 1, QtCore.Qt.AlignHCenter)

        self.retranslateUi(EditPosition)
        self.buttonBox.accepted.connect(EditPosition.accept)
        self.buttonBox.rejected.connect(EditPosition.reject)
        QtCore.QMetaObject.connectSlotsByName(EditPosition)

    def retranslateUi(self, EditPosition):
        _translate = QtCore.QCoreApplication.translate
        EditPosition.setWindowTitle(_translate("EditPosition", "Dialog"))
        self.checkBox_3.setText(_translate("EditPosition", "Trailing Step"))
        self.checkBox_2.setText(_translate("EditPosition", "Range"))
        self.label_4.setText(_translate("EditPosition", "Trailing Step"))
        self.label.setText(_translate("EditPosition", "Amount"))
        self.checkBox.setText(_translate("EditPosition", "Rate"))
        self.label_2.setText(_translate("EditPosition", "Rate"))
        self.label_3.setText(_translate("EditPosition", "Range"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    EditPosition = QtWidgets.QDialog()
    ui = Ui_EditPosition()
    ui.setupUi(EditPosition)
    EditPosition.show()
    sys.exit(app.exec_())
