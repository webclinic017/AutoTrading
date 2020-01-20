# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'acc_info_popup.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Account(object):
    def setupUi(self, Account):
        Account.setObjectName("Account")
        Account.resize(1280, 310)
        self.gridLayout = QtWidgets.QGridLayout(Account)
        self.gridLayout.setObjectName("gridLayout")
        self.tableWidget = QtWidgets.QTableWidget(Account)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(17)
        self.tableWidget.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(5, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(6, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(7, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(8, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(9, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(10, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(11, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(12, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(13, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(14, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(15, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(16, item)

        self.gridLayout.addWidget(self.tableWidget, 0, 0, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(Account)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)

        self.retranslateUi(Account)
        self.buttonBox.accepted.connect(Account.accept)
        self.buttonBox.rejected.connect(Account.reject)
        QtCore.QMetaObject.connectSlotsByName(Account)

    def retranslateUi(self, Account):
        _translate = QtCore.QCoreApplication.translate
        Account.setWindowTitle(_translate("Account", "Dialog"))
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("Account", "Account ID"))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("Account", "Account Name"))
        item = self.tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("Account", "Balance"))
        item = self.tableWidget.horizontalHeaderItem(3)
        item.setText(_translate("Account", "DayPL"))
        item = self.tableWidget.horizontalHeaderItem(4)
        item.setText(_translate("Account", "Equity"))
        item = self.tableWidget.horizontalHeaderItem(5)
        item.setText(_translate("Account", "Gross PL"))
        item = self.tableWidget.horizontalHeaderItem(6)
        item.setText(_translate("Account", "Hedging"))
        item = self.tableWidget.horizontalHeaderItem(7)
        item.setText(_translate("Account", "mc"))
        item = self.tableWidget.horizontalHeaderItem(8)
        item.setText(_translate("Account", "mcDate"))
        item = self.tableWidget.horizontalHeaderItem(9)
        item.setText(_translate("Account", "Rate Precision"))
        item = self.tableWidget.horizontalHeaderItem(10)
        item.setText(_translate("Account", "t"))
        item = self.tableWidget.horizontalHeaderItem(11)
        item.setText(_translate("Account", "UsableMargin"))
        item = self.tableWidget.horizontalHeaderItem(12)
        item.setText(_translate("Account", "usableMarginPerc"))
        item = self.tableWidget.horizontalHeaderItem(13)
        item.setText(_translate("Account", "usableMargin3"))
        item = self.tableWidget.horizontalHeaderItem(14)
        item.setText(_translate("Account", "usableMargin3Perc"))
        item = self.tableWidget.horizontalHeaderItem(15)
        item.setText(_translate("Account", "UsdMr"))
        item = self.tableWidget.horizontalHeaderItem(16)
        item.setText(_translate("Account", "usdMr3"))





if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Account = QtWidgets.QDialog()
    ui = Ui_Account()
    ui.setupUi(Account)
    Account.show()
    sys.exit(app.exec_())
