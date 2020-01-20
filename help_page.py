# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'help_page.ui'
#
# Created by: PyQt5 UI code generator 5.13.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_help_page(object):
    def setupUi(self, help_page):
        help_page.setObjectName("help_page")
        help_page.resize(1280, 720)
        self.verticalLayout = QtWidgets.QVBoxLayout(help_page)
        self.verticalLayout.setObjectName("verticalLayout")
        self.textBrowser = QtWidgets.QTextBrowser(help_page)
        self.textBrowser.setObjectName("textBrowser")
        self.verticalLayout.addWidget(self.textBrowser)

        self.retranslateUi(help_page)
        QtCore.QMetaObject.connectSlotsByName(help_page)

    def retranslateUi(self, help_page):
        _translate = QtCore.QCoreApplication.translate
        help_page.setWindowTitle(_translate("help_page", "Dialog"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    help_page = QtWidgets.QDialog()
    ui = Ui_help_page()
    ui.setupUi(help_page)
    help_page.show()
    sys.exit(app.exec_())
