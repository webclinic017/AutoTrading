# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'edit_order_stop_limit.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_OrderStopLimit(object):
    def setupUi(self, OrderStopLimit):
        OrderStopLimit.setObjectName("OrderStopLimit")
        OrderStopLimit.resize(263, 312)
        self.gridLayout = QtWidgets.QGridLayout(OrderStopLimit)
        self.gridLayout.setObjectName("gridLayout")
        self.label_2 = QtWidgets.QLabel(OrderStopLimit)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.label = QtWidgets.QLabel(OrderStopLimit)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.lineEdit = QtWidgets.QLineEdit(OrderStopLimit)
        self.lineEdit.setObjectName("lineEdit")
        self.gridLayout.addWidget(self.lineEdit, 0, 1, 1, 1)
        self.checkBox = QtWidgets.QCheckBox(OrderStopLimit)
        self.checkBox.setObjectName("checkBox")
        self.gridLayout.addWidget(self.checkBox, 0, 2, 1, 1)
        self.lineEdit_2 = QtWidgets.QLineEdit(OrderStopLimit)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.gridLayout.addWidget(self.lineEdit_2, 1, 1, 1, 1)
        self.checkBox_2 = QtWidgets.QCheckBox(OrderStopLimit)
        self.checkBox_2.setObjectName("checkBox_2")
        self.gridLayout.addWidget(self.checkBox_2, 1, 2, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(OrderStopLimit)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 2, 1, 1, 1)

        self.retranslateUi(OrderStopLimit)
        self.buttonBox.accepted.connect(OrderStopLimit.accept)
        self.buttonBox.rejected.connect(OrderStopLimit.reject)
        QtCore.QMetaObject.connectSlotsByName(OrderStopLimit)

    def retranslateUi(self, OrderStopLimit):
        _translate = QtCore.QCoreApplication.translate
        OrderStopLimit.setWindowTitle(_translate("OrderStopLimit", "Dialog"))
        self.label_2.setText(_translate("OrderStopLimit", "Stop"))
        self.label.setText(_translate("OrderStopLimit", "Limit"))
        self.checkBox.setText(_translate("OrderStopLimit", "In pips"))
        self.checkBox_2.setText(_translate("OrderStopLimit", "In pips"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    OrderStopLimit = QtWidgets.QDialog()
    ui = Ui_OrderStopLimit()
    ui.setupUi(OrderStopLimit)
    OrderStopLimit.show()
    sys.exit(app.exec_())
