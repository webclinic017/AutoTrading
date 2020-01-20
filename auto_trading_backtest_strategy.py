# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'auto_trading_backtest_strategy.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Ui_autotrading_backtest_strategy_page(object):
    def setupUi(self, Ui_autotrading_backtest_strategy_page):
        Ui_autotrading_backtest_strategy_page.setObjectName("Ui_autotrading_backtest_strategy_page")
        Ui_autotrading_backtest_strategy_page.resize(800, 600)
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(Ui_autotrading_backtest_strategy_page)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(Ui_autotrading_backtest_strategy_page)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.label_2 = QtWidgets.QLabel(Ui_autotrading_backtest_strategy_page)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.lineEdit = QtWidgets.QLineEdit(Ui_autotrading_backtest_strategy_page)
        self.lineEdit.setObjectName("lineEdit")
        self.verticalLayout_2.addWidget(self.lineEdit)
        self.lineEdit_2 = QtWidgets.QLineEdit(Ui_autotrading_backtest_strategy_page)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.verticalLayout_2.addWidget(self.lineEdit_2)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        self.scrollArea = QtWidgets.QScrollArea(Ui_autotrading_backtest_strategy_page)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 378, 166))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout_3.addWidget(self.scrollArea)
        self.progressBar = QtWidgets.QProgressBar(Ui_autotrading_backtest_strategy_page)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName("progressBar")
        self.verticalLayout_3.addWidget(self.progressBar)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.pushButton_2 = QtWidgets.QPushButton(Ui_autotrading_backtest_strategy_page)
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout_2.addWidget(self.pushButton_2)
        self.pushButton = QtWidgets.QPushButton(Ui_autotrading_backtest_strategy_page)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout_2.addWidget(self.pushButton)
        self.verticalLayout_3.addLayout(self.horizontalLayout_2)
        self.verticalLayout_4.addLayout(self.verticalLayout_3)

        self.retranslateUi(Ui_autotrading_backtest_strategy_page)
        QtCore.QMetaObject.connectSlotsByName(Ui_autotrading_backtest_strategy_page)

    def retranslateUi(self, Ui_autotrading_backtest_strategy_page):
        _translate = QtCore.QCoreApplication.translate
        Ui_autotrading_backtest_strategy_page.setWindowTitle(_translate("Ui_autotrading_backtest_strategy_page", "Dialog"))
        self.label.setText(_translate("Ui_autotrading_backtest_strategy_page", "Quantity"))
        self.label_2.setText(_translate("Ui_autotrading_backtest_strategy_page", "Capital"))
        self.pushButton_2.setText(_translate("Ui_autotrading_backtest_strategy_page", "Cancel"))
        self.pushButton.setText(_translate("Ui_autotrading_backtest_strategy_page", "Start"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Ui_autotrading_backtest_strategy_page = QtWidgets.QDialog()
    ui = Ui_Ui_autotrading_backtest_strategy_page()
    ui.setupUi(Ui_autotrading_backtest_strategy_page)
    Ui_autotrading_backtest_strategy_page.show()
    sys.exit(app.exec_())
