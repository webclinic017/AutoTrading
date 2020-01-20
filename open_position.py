# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'open_position.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_OpenPos(object):
    def setupUi(self, OpenPos):
        OpenPos.setObjectName("OpenPos")
        OpenPos.resize(379, 310)
        self.formLayout = QtWidgets.QFormLayout(OpenPos)
        self.formLayout.setObjectName("formLayout")
        self.comboBox = QtWidgets.QComboBox(OpenPos)
        self.comboBox.setObjectName("comboBox")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.comboBox)
        self.radioButton = QtWidgets.QRadioButton(OpenPos)
        self.radioButton.setObjectName("radioButton")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.radioButton)
        self.label_2 = QtWidgets.QLabel(OpenPos)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.lineEdit = QtWidgets.QLineEdit(OpenPos)
        self.lineEdit.setInputMask("")
        self.lineEdit.setObjectName("lineEdit")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.lineEdit)
        self.checkBox = QtWidgets.QCheckBox(OpenPos)
        self.checkBox.setObjectName("checkBox")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.LabelRole, self.checkBox)
        self.label_3 = QtWidgets.QLabel(OpenPos)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.lineEdit_2 = QtWidgets.QLineEdit(OpenPos)
        self.lineEdit_2.setEnabled(False)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.FieldRole, self.lineEdit_2)
        self.checkBox_2 = QtWidgets.QCheckBox(OpenPos)
        self.checkBox_2.setObjectName("checkBox_2")
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.SpanningRole, self.checkBox_2)
        self.label_4 = QtWidgets.QLabel(OpenPos)
        self.label_4.setObjectName("label_4")
        self.formLayout.setWidget(8, QtWidgets.QFormLayout.LabelRole, self.label_4)
        self.lineEdit_3 = QtWidgets.QLineEdit(OpenPos)
        self.lineEdit_3.setEnabled(False)
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.formLayout.setWidget(8, QtWidgets.QFormLayout.FieldRole, self.lineEdit_3)
        self.checkBox_3 = QtWidgets.QCheckBox(OpenPos)
        self.checkBox_3.setObjectName("checkBox_3")
        self.formLayout.setWidget(9, QtWidgets.QFormLayout.LabelRole, self.checkBox_3)
        self.label_5 = QtWidgets.QLabel(OpenPos)
        self.label_5.setObjectName("label_5")
        self.formLayout.setWidget(10, QtWidgets.QFormLayout.LabelRole, self.label_5)
        self.lineEdit_4 = QtWidgets.QLineEdit(OpenPos)
        self.lineEdit_4.setEnabled(False)
        self.lineEdit_4.setObjectName("lineEdit_4")
        self.formLayout.setWidget(10, QtWidgets.QFormLayout.FieldRole, self.lineEdit_4)
        self.checkBox_4 = QtWidgets.QCheckBox(OpenPos)
        self.checkBox_4.setObjectName("checkBox_4")
        self.formLayout.setWidget(11, QtWidgets.QFormLayout.LabelRole, self.checkBox_4)
        self.buttonBox = QtWidgets.QDialogButtonBox(OpenPos)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.formLayout.setWidget(12, QtWidgets.QFormLayout.FieldRole, self.buttonBox)
        self.label = QtWidgets.QLabel(OpenPos)
        self.label.setObjectName("label")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label)
        self.radioButton_2 = QtWidgets.QRadioButton(OpenPos)
        self.radioButton_2.setObjectName("radioButton_2")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.radioButton_2)

        self.retranslateUi(OpenPos)
        self.buttonBox.accepted.connect(OpenPos.accept)
        self.buttonBox.rejected.connect(OpenPos.reject)
        QtCore.QMetaObject.connectSlotsByName(OpenPos)

    def retranslateUi(self, OpenPos):
        _translate = QtCore.QCoreApplication.translate
        OpenPos.setWindowTitle(_translate("OpenPos", "Dialog"))
        self.radioButton.setText(_translate("OpenPos", "Long"))
        self.label_2.setText(_translate("OpenPos", "Amount K"))
        self.checkBox.setText(_translate("OpenPos", "Stop"))
        self.label_3.setText(_translate("OpenPos", "Stop"))
        self.checkBox_2.setText(_translate("OpenPos", "Trailing Step"))
        self.label_4.setText(_translate("OpenPos", "Trailing Step"))
        self.checkBox_3.setText(_translate("OpenPos", "Limit"))
        self.label_5.setText(_translate("OpenPos", "Limit"))
        self.checkBox_4.setText(_translate("OpenPos", "In pips"))
        self.label.setText(_translate("OpenPos", "Symbol"))
        self.radioButton_2.setText(_translate("OpenPos", "Short"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    OpenPos = QtWidgets.QDialog()
    ui = Ui_OpenPos()
    ui.setupUi(OpenPos)
    OpenPos.show()
    sys.exit(app.exec_())
