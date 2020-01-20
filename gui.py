"""
This file is GUI file acting as a controller, as it uses retrieves required data from other parts 
of the project and uses view classes (UI files) to display them.

"""



"""
Import main class from all related UI files here
"""
from main_window import Ui_Main
from login_popup import Ui_Login
from acc_info_popup import Ui_Account
from view_open_positions import Ui_Positions
from view_closed_positions import Ui_ClosedPositions
from edit_order_stop_limit import Ui_OrderStopLimit
from open_position import Ui_OpenPos
from open_order import Ui_OpenOrd
from edit_popup import Ui_EditPosition
from edit_position_stop_limit import Ui_EditTradeStopLimit
from view_orders import Ui_Orders
from app_login_page import Ui_app_login
from chart_page import Ui_chart_page
from auto_trading_page import Ui_autotrading_page
from auto_trading_add_strategy import Ui_autotrading_add_strategy_page
from auto_trading_edit_strategy import Ui_autotrading_edit_strategy_page
from auto_trading_backtest_strategy import Ui_Ui_autotrading_backtest_strategy_page
from help_page import Ui_help_page

"""
Import required modules from the project folder
"""

from fxcm_controller import Fxcm
from db_controller import Db_Controller
import configuration
from strategy import strategy_controller
import help_content


"""
Import required libraries
"""
import sys
import datetime
import pandas
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QTableWidgetItem, qApp, QAction, QMessageBox
from PyQt5.QtCore import QAbstractTableModel, Qt, QThread, QObject, pyqtSignal, pyqtSlot
import os
import pickle
import multiprocessing
import queue
import threading
import pandas as pd
import numpy as np
import time
import pyqtgraph as pg
import random




class GUI():
    """
    GUI class represents the actual GUI and its functionality
    Functions represent specific windows and popups
    """
    def __init__(self):
        """
        Main window generation method. The UI template can be taken from main_window.py
        """
        
        self.init_required_files() #Initializing the required files including data.dll, acount_info.cfg and strategies_settiing.cfg
        
        """
        Initializing app main window and menu functions. 
        """
        self.app = QtWidgets.QApplication(sys.argv)  #Creating an instance of the pyqt app
        self.main_window = QtWidgets.QMainWindow() #Creating main window instance
        self.main_window.closeEvent=self.closeEvent #Overriding close event to add more functionalities when closing the app.
        self.ui = Ui_Main()
        self.ui.setupUi(self.main_window)
        self.ui.actionLogin.triggered.connect(self.open_login)
        self.ui.actionAccInfo.triggered.connect(self.open_acc_info)
        self.ui.actionPositions.triggered.connect(self.view_open_positions)
        self.ui.actionOpenPosition.triggered.connect(self.open_position)
        self.ui.actionView_Closed_Positions.triggered.connect(self.view_closed_positions)
        self.ui.actionAutotrading_panel.triggered.connect(self.open_auto_trading_page)
        self.ui.actionAutotrading_start_all.triggered.connect(self.start_all_trading_strategy)
        self.ui.actionAutotrading_stop_all.triggered.connect(self.stop_all_trading_strategy)
        self.ui.actionCharts_price_chart.triggered.connect(self.open_price_chart)
        self.ui.actionHelp_instructions.triggered.connect(self.open_instructions)
        
        """
        Instantiating required modules and variables of the project
        """
        self.controller = Fxcm() #Fxcm is the class acting as a controller to handle API and storing data on db.
        self.strategy_controller=strategy_controller.strategy_controller() #strategy_controller is the class act as a controller for strategies
        self.db = Db_Controller()
        self.instruction_text=help_content.instructions

        self.strategies_name_description_dict=self.strategy_controller.trading_strategies_name_description_dict #Built in strategies'names and description dictionary
        self.strategies_inputs_dict=self.strategy_controller.trading_strategies_inputs_dict #Built in strategies'inputs dictionary
        self.risk_managements_name_description_dict=self.strategy_controller.risk_management_name_description_dict #Built in risk managements'names and description dictionary
        self.risk_managements_inputs_dict=self.strategy_controller.risk_management_inputs_dict #Built in risk managements'inputs dictionary
        self.news_reactors_name_description_dict=self.strategy_controller.news_reactor_name_description_dict #Built in news reactor'names and description dictionary
        self.news_reactors_inputs_dict=self.strategy_controller.news_reactor_inputs_dict #Built in news reactor'inputs dictionary
        self.auto_trading_symbol_list=configuration.auto_trading_symbol_list #List of vailable symbols for autotrading
        self.auto_trading_timeframe_list=configuration.auto_trading_timeframe_list #List of vailable timeframes for autotrading
        
        """
        Calling dashboard to create dashboard's content
        """
        self.dashboard()


    """
    Function to show dashboard and keep it updated
    """
    def dashboard(self):

        """
        Function to update dashboard items (It is called when the below thread emits new data)
        """
        def update_dashboard_func(data_dict):
            try:
                if len(data_dict)>0: #checking if data is empty
                    """
                    Section to update items of open position table
                    """
                    try:
                        self.ui.tableWidget1.setRowCount(0) #Removing items from table
                        """
                        Creating tables' items
                        """
                        for row_number, row_data in enumerate(data_dict['open_positions']):
                            self.ui.tableWidget1.insertRow(row_number)
                            for column_number, data in enumerate(row_data):
                                self.ui.tableWidget1.setItem(row_number, column_number, QtWidgets.QTableWidgetItem(str(data)))     
                    except Exception as e:
                        print(e)

                    """
                    Section to update items of closed position table
                    """                        
                    try:
                        self.ui.tableWidget1_2.setRowCount(0) #Removing items from table
                        """
                        Creating tables' items
                        """
                        for row_number, row_data in enumerate(data_dict['closed_positions']):
                            self.ui.tableWidget1_2.insertRow(row_number)
                            for column_number, data in enumerate(row_data):
                                self.ui.tableWidget1_2.setItem(row_number, column_number, QtWidgets.QTableWidgetItem(str(data)))
                    except Exception as e:
                        print(e)
            except Exception as e:
                print(e)



        """
        This class inherits from QThread, created to handle updating dashboard. (It retrieves required data from db and signals update_dashboard_func to update table)
        """
        class update_dashboard_thread_class(QThread):
            dictReady=pyqtSignal(dict)
            def __init__(self, db):
                self.db=db
                self.stop_signal=False
                QThread.__init__(self)

            def stop(self):
                self.stop_signal=True

            def run(self):
                while True:
                    try:
                        if self.stop_signal==True:
                            break
                        else:
                            dict_temp={}
                            dict_temp["open_positions"]=self.db.query_open_positon_dashboard()
                            dict_temp["closed_positions"]=self.db.query_closed_positon_dashboard()
                            self.dictReady.emit(dict_temp)
                            time.sleep(5)
                    except Exception as e:
                        print(e)

        """
        Creating the instance of the created thread class and starting it
        """

        self.update_dashboard_thread=update_dashboard_thread_class(self.db)
        self.update_dashboard_thread.dictReady.connect(update_dashboard_func)
        self.update_dashboard_thread.start()


    
    def open_warning(self):
        """
        Opens a popup window if connection is not established.
        Applied to every function that requires the connection to prevent unauthorized access
        """
        self.dialog_open_warning = QMessageBox()
        self.dialog_open_warning.setWindowTitle('Not connected to FXCM')
        self.dialog_open_warning.setText('Please connect to FXCM server to proceed')
        self.dialog_open_warning.setIcon(QMessageBox.Information)
        self.dialog_open_warning.show()


    def closeEvent(self, event):
        """
        CloseEvent function to be replaced with main menu exit event 
        """

        quit_msg = "Are you sure you want to exit the program?"
        reply = QtWidgets.QMessageBox.question(self.main_window, 'Message', 
                        quit_msg, QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)

        if reply == QtWidgets.QMessageBox.Yes:
            self.strategy_controller.stop_all_strategies() # Stoping all strategies
            try:
                self.ui_price_chart.update_price_data_chart_thread.closeEvent() #Stoping price chart thread
            except Exception as e:
                print(e)
            event.accept()
            self.app.exit()
        else:
            event.ignore()

    def open_login(self):
        """
        Method to generate login popup window. The UI template can be taken from login_popup.py
        """
        # Window initialization
        self.dialog_open_login = QtWidgets.QDialog()
        self.ui_open_login = Ui_Login()
        self.ui_open_login.setupUi(self.dialog_open_login)
        self.dialog_open_login.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
        self.dialog_open_login.setWindowFlag(Qt.WindowMaximizeButtonHint, True)

        def connection_result(msg):
            """
            Showing the result of connection (It is called when the below thread finishes its job and passes the result)
            """
            QtWidgets.QMessageBox.about(self.dialog_open_login, 'Result message', msg)
            self.ui_open_login.pushButton.setEnabled(True)
            self.ui_open_login.pushButton_2.setEnabled(True)
            self.ui_open_login.pushButton_3.setEnabled(True)
            if msg=="Connection is established":
                self.ui_open_login.label_2.setText('Connected')
            else:
                self.ui_open_login.label_2.setText('Disconnected')

        
        class connect_fxcm_thread_class(QThread):
            """
            This class inherits from QThread, created to handle connecting to server. (It prevents the app from getting frozen when waiting for result)
            """
            finished=pyqtSignal(str)
            def __init__(self, controller):
                QThread.__init__(self)
                self.controller=controller
            def run(self):
                try:
                    result=self.controller.start_connection_thread_gui() #Calling start_connection_thread_gui(A special method for connecting to server from GUI)
                    if result==True:
                        self.finished.emit('Connection is established')
                    else:
                        self.finished.emit(str(result))
                except Exception as e:
                    print(e)
                    self.finished.emit(str(e))

        
        def connect_fxcm():
            """
            Function to be called when connect button clicked.
            It create the instance of connect_fxcm_thread_class and starts it.
            Also disables other buttons to prevent any recalling when function is still running
            """
            if self.controller.token!='':
                self.to_connect_thread=connect_fxcm_thread_class(self.controller)
                self.to_connect_thread.finished.connect(connection_result)
                self.to_connect_thread.start()
                self.ui_open_login.pushButton.setEnabled(False)
                self.ui_open_login.pushButton_2.setEnabled(False)
                self.ui_open_login.pushButton_3.setEnabled(False)
                self.ui_open_login.label_2.setText('Connecting...')
            else:
                QtWidgets.QMessageBox.about(self.dialog_open_login, 'Result message', 'Token is not defined')
        
        def disconnect_fxcm():
            """
            Function to be called when disconnect button clicked. It calls disconnect method of fxcm (controller)
            to disconnect connection to FXCM
            """
            if self.controller.connection_status!='Disconnected':
                self.controller.disconnect_gui()
                self.ui_open_login.label_2.setText('Disconnected')
                self.stop_all_trading_strategy()
            else:
                QtWidgets.QMessageBox.about(self.dialog_open_login, 'Result message', 'Connection is not established')


        def token_updated_result(msg):
            """
            Showing the result of changing token and enabling buttons It is called when below thread finishes its job.
            """
            QtWidgets.QMessageBox.about(self.dialog_open_login, 'Result message', msg)
            self.ui_open_login.pushButton.setEnabled(True)
            self.ui_open_login.pushButton_2.setEnabled(True)
            self.ui_open_login.pushButton_3.setEnabled(True)

        class update_token_thread_class(QThread):
            """
            This class inherits from QThread, created to handle changing API token and account currency.
            The destination function validates the thread and if token is valid then new token will be stored in account_info.cfg
            (It prevents the app from getting frozen when waiting for result)
            """
            finished=pyqtSignal(str)
            def __init__(self, token, account_currency, account_type, controller):
                QThread.__init__(self)
                self.token=token
                self.controller=controller
                self.account_currency=account_currency
                self.account_type=account_type
            def run(self):
                try:
                    result=self.controller.update_token(self.token, self.account_currency, self.account_type)
                    if result==True:
                        self.finished.emit('Token is updated')
                    else:
                        self.finished.emit(str(result))
                except Exception as e:
                    print(e)
                    self.finished.emit(str(e))

        def update_token():
            """
            Function to be called when update token and account currency button clicked.
            It create the instance of update_token_thread_class and starts it.
            Also disables other buttons to prevent any recalling when function is still running
            """
            
            if self.ui_open_login.lineEdit.text()!='':
                self.update_token_thread=update_token_thread_class(self.ui_open_login.lineEdit.text(), self.ui_open_login.comboBox.currentText(), self.ui_open_login.comboBox_2.currentText(), self.controller)
                self.update_token_thread.finished.connect(token_updated_result)
                self.update_token_thread.start()
                self.ui_open_login.pushButton.setEnabled(False)
                self.ui_open_login.pushButton_2.setEnabled(False)
                self.ui_open_login.pushButton_3.setEnabled(False)
            else:
                QtWidgets.QMessageBox.about(self.dialog_open_login, 'Result message', 'Token is empty')

        """
        Setting items' settings and variables and setting button trigger functions

        """
        self.ui_open_login.comboBox_2.addItems(['demo', 'real'])
        self.ui_open_login.comboBox.addItems(self.controller.fxcm_account_currency_list)
        if self.controller.account_currency!=None:
            self.ui_open_login.comboBox.setCurrentIndex(self.ui_open_login.comboBox.findText(self.controller.account_currency))
            self.ui_open_login.comboBox_2.setCurrentIndex(self.ui_open_login.comboBox_2.findText(self.controller.account_type))
        if self.controller.connection_status=='Disconnected' or self.controller.connection_status==None:
            self.ui_open_login.label_2.setText('Disconnected')
        elif self.controller.connection_status=='Connected':
            self.ui_open_login.label_2.setText('Connected')
        else:
            self.ui_open_login.label_2.setText(str(self.controller.connection_status))
        self.ui_open_login.lineEdit.setText(self.controller.token)
        self.ui_open_login.pushButton_2.clicked.connect(connect_fxcm)
        self.ui_open_login.pushButton_3.clicked.connect(disconnect_fxcm)
        self.ui_open_login.pushButton.clicked.connect(update_token)
        self.dialog_open_login.show()

    def open_acc_info(self):
        """
        Method to generate account info popup. The UI template can be taken from acc_info_popup.py
        """
        self.dialog_account_info = QtWidgets.QDialog()
        self.ui_account_info = Ui_Account()
        self.ui_account_info.setupUi(self.dialog_account_info)
        self.dialog_account_info.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
        self.dialog_account_info.setWindowFlag(Qt.WindowMaximizeButtonHint, True)

        def closeEvent(event):
            """
            CloseEvent function to be replaced with this window's exit event 
            """
            try:
                self.update_account_info_thread.stop()
                self.update_account_info_thread.wait()
                del self.update_account_info_thread
                event.accept()
            except Exception as e:
                print(e)
                event.accept()

        def fill_account_info_tables(data):
            """
            Updating acount inforamtion table. (It is called when the below thread receives new data)
            """
            for column, field in enumerate(data):
                # setItem function cannot accept not QTableWidgetItem objects. QTableWidgetItem accepts only strings
                # Thus, to populate the table, convert all the data to string first, then QTableWidgetItem
                self.ui_account_info.tableWidget.setItem(0, column, QTableWidgetItem(str(field)))

        class update_account_info_thread_class(QThread):
            """
            This class is inherits from QThread, created to handle retrieving account info data from db periodically.
            (It prevents the app from getting frozen when waiting for result)
            """
            tupleReady=pyqtSignal(tuple)
            def __init__(self, db, account_id):
                QThread.__init__(self)
                self.db=db
                self.account_id=account_id
                self.stop_signal=False

            def stop(self):
                self.stop_signal=True
            
            def run(self):
                while True:
                    try:
                        if self.stop_signal==False:
                            data = self.db.query_table('Fxcm_Info', ('*',), fields=('accountId',), values=(self.account_id,))[0]
                            self.tupleReady.emit(data)
                            time.sleep(5)
                        else:
                            break
                    except:
                        pass

        
        """
        Setting items' settings and variables and setting button trigger functions

        """

        self.dialog_account_info.closeEvent=closeEvent

        if self.controller.account_id!=None: #Checking if self.controller (Fxcm) has set its account_id attribute
            self.ui_account_info.tableWidget.setRowCount(1)
            self.update_account_info_thread=update_account_info_thread_class(self.db, self.controller.account_id)
            self.update_account_info_thread.tupleReady.connect(fill_account_info_tables)
            self.update_account_info_thread.start()
        else:
            QtWidgets.QMessageBox.about(self.dialog_account_info, '', 'The app has never connected to fxcm server using current token')
        self.dialog_account_info.show()



    def view_open_positions(self):
        """
        Function to open view open position window.
        """

        # Initial table to store the requred for closing position
        position_data = {
            'maker':'Manual',
            'trade_id': '',
            'amount': ''
        }

        # Window initialization
        self.dialog_view_open_positions = QtWidgets.QDialog()
        self.ui_view_open_positions = Ui_Positions()
        self.ui_view_open_positions.setupUi(self.dialog_view_open_positions)
        self.dialog_view_open_positions.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
        self.dialog_view_open_positions.setWindowFlag(Qt.WindowMaximizeButtonHint, True)


        def closeEvent(event):
            """
            CloseEvent function to be replaced with this window's exit event 
            """
            try:
                self.update_open_positions_thread.stop()
                self.update_open_positions_thread.wait()
                del self.update_open_positions_thread
                event.accept()
            except Exception as e:
                print(e)
                event.accept()
        

        # Window functionality
        def position_info_review():
            """
            Small 'capture' controller. Sends the required data from selected row to the position_data
            """
            # 2 and 15 are corresponding to 'trade_id' and 'amount' columns in QTableWidget
            position_data['trade_id'] = self.ui_view_open_positions.tableWidget.item(self.ui_view_open_positions.tableWidget.currentRow(), 2).text()
            position_data['amount'] = self.ui_view_open_positions.tableWidget.item(self.ui_view_open_positions.tableWidget.currentRow(), 15).text()


        def fill_open_position_tables(data):
            """
            Reseting tables row count and refilling table items, this function is called when below thread receives
            data.
            """
            try:
                self.ui_view_open_positions.tableWidget.setRowCount(len(data))
                for row, position in enumerate(data):
                    for column, data in enumerate(position):
                        try:
                            if column==17:
                                data=self.controller.timestamp_to_datetime(data)
                            # setItem function cannot accept not QTableWidgetItem objects. QTableWidgetItem accepts only strings
                            # Thus, to populate the table, convert all the data to string first, then QTableWidgetItem
                            self.ui_view_open_positions.tableWidget.setItem(row, column, QTableWidgetItem(str(data)))
                        except Exception as e:
                            pass
            except Exception as e:
                print(e)

        class update_open_positions_thread_class(QThread):
            """
            This class inherits from QThread, created to handle updating open position view.
            (It prevents the app from getting frozen when waiting for result)
            """

            listReady=pyqtSignal(list)
            def __init__(self, db, account_id):
                QThread.__init__(self)
                self.db=db
                self.account_id=account_id
                self.stop_signal=False

            def stop(self):
                self.stop_signal=True
            
            def run(self):
                while True:
                    try:
                        if self.stop_signal==False:
                            """
                            Retrieving open positions data from db
                            """
                            data = self.db.query_table('OpenPosition', ('*',), fields=('accountId',), values=(self.account_id,))
                            self.listReady.emit(data)
                            time.sleep(5)
                        else:
                            break
                    except Exception as e:
                        print(e)

        class close_all_position_thread_class(QThread):
            """
            This class inherits from QThread, created to handle closing all position command.
            As the interval to get the result from fxcm api may vary, a long waiting to recieve the 
            result freezes the app.
            (It prevents the app from getting frozen when waiting for result)
            """
            def __init__(self, controller):
                QThread.__init__(self)
                self.controller=controller
            def run(self):
                try:
                    self.controller.close_all_positions()
                except:
                    pass

        class close_position_thread_class(QThread):
            """
            This class inherits from QThread, created to handle close position command.
            As the interval to get the result from fxcm api may vary, a long waiting to recieve the 
            result freezes the app.
            (It prevents the app from getting frozen when waiting for result)
            """
            
            def __init__(self, controller, position_data):
                QThread.__init__(self)
                self.controller=controller
                self.position_data=position_data

            def run(self):
                try:
                    self.controller.close_position(**position_data)
                except:
                    pass

        def close_all_positions():
            """
            This function creates an instance of close_all_position_thread_class to start closing all postions
            It is called when close all positions button is clicked
            """
            if self.controller.connection_status == 'Disconnected': #Checking if the connection is established, to show
                self.open_warning()
            else:
                quit_msg = "Are you sure you want close all positions?"
                reply = QtWidgets.QMessageBox.question(self.dialog_view_open_positions, 'Message', 
                                quit_msg, QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)

                if reply == QtWidgets.QMessageBox.Yes:
                    self.close_all_position_thread=close_all_position_thread_class(self.controller)
                    self.close_all_position_thread.start()
                else:
                    pass



        def close_position():
            """
            This function creates an instance of close_position_thread_class to start closing postions
            It is called when close positions button is clicked
            """
            if self.controller.connection_status == 'Disconnected':
                self.open_warning()
            else:
                quit_msg = "Are you sure you want close this position?"
                reply = QtWidgets.QMessageBox.question(self.dialog_view_open_positions, 'Message', 
                                quit_msg, QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)

                if reply == QtWidgets.QMessageBox.Yes:
                    self.close_position_thread=close_position_thread_class(self.controller, position_data)
                    self.close_position_thread.start()
                else:
                    pass



        """
        Setting button's trigger function and starting the thread for updating content
        """

        self.ui_view_open_positions.tableWidget.clicked.connect(position_info_review)
        self.dialog_view_open_positions.closeEvent=closeEvent
        self.ui_view_open_positions.pushButton.clicked.connect(close_all_positions)
        self.ui_view_open_positions.pushButton_2.clicked.connect(close_position)
        self.ui_view_open_positions.pushButton_3.clicked.connect(self.edit_position_stop_limit)

        self.update_open_positions_thread=update_open_positions_thread_class(self.db, self.controller.account_id)
        self.update_open_positions_thread.listReady.connect(fill_open_position_tables)
        self.update_open_positions_thread.start()

        # Show the window
        self.dialog_view_open_positions.show()

    def view_closed_positions(self):
        """
        Function to open view closed position window.
        """


        # Window initialization
        self.dialog_view_closed_positions = QtWidgets.QDialog()
        self.ui_view_closed_positions = Ui_ClosedPositions()
        self.ui_view_closed_positions.setupUi(self.dialog_view_closed_positions)
        self.dialog_view_closed_positions.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
        self.dialog_view_closed_positions.setWindowFlag(Qt.WindowMaximizeButtonHint, True)

        def update_closed_positions(data):
            """
            Reseting tables row count and refilling table items, this function is called when below thread receives
            data.
            """
            self.ui_view_closed_positions.tableWidget.setRowCount(len(data)) # Creating rows based on data
            # Populating the QTableWidget
            for row, position in enumerate(data):
                for column, data in enumerate(position):
                    try:
                        if column==15 or column==16:
                            data=self.controller.timestamp_to_datetime(data)
                        # setItem function cannot accept not QTableWidgetItem objects. QTableWidgetItem accepts only strings
                        # Thus, to populate the table, convert all the data to string first, then QTableWidgetItem
                        self.ui_view_closed_positions.tableWidget.setItem(row, column, QTableWidgetItem(str(data)))
                    except Exception as e:
                        print(e)
        
        
        class update_closed_positions_thread_class(QThread):
            """
            This class inherits from QThread, created to handle updating closed positions.
            (It prevents the app from getting frozen when waiting for result)
            """
            
            listReady=pyqtSignal(list)
            def __init__(self, db, account_name):
                QThread.__init__(self)
                self.db=db
                self.account_name=account_name
                self.stop_signal=False

            def stop(self):
                self.stop_signal=True
            
            def run(self):
                while True:
                    try:
                        if self.stop_signal==False:
                            data = self.db.query_table('ClosedPosition', ('*',), fields=('accountName',), values=(self.account_name,))
                            self.listReady.emit(data)
                            time.sleep(5)
                        else:
                            break
                    except Exception as e:
                        print(e)
        
        
        
        """
        Setting button's trigger function and starting the thread for updating content
        """

        self.update_closed_positions_thread=update_closed_positions_thread_class(self.db, self.controller.account_name)
        self.update_closed_positions_thread.listReady.connect(update_closed_positions)
        self.update_closed_positions_thread.start()
        self.dialog_view_closed_positions.show()



    def open_position(self):
        """
        This method opens open position windows
        """
        if self.controller.connection_status == 'Disconnected':
            self.open_warning()
        else:

            # Window initialization
            self.dialog_open_position = QtWidgets.QDialog()
            self.ui_open_position = Ui_OpenPos()
            self.ui_open_position.setupUi(self.dialog_open_position)
            self.dialog_open_position.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
            self.dialog_open_position.setWindowFlag(Qt.WindowMaximizeButtonHint, True)

            # Window functionality

            #Default values for opening position
            trading_values = {
                "maker":'Manual',
                "symbol": "EURUSD",
                "is_buy": False,
                "amount": 1,
                "order_type": "AtMarket",
                "time_in_force": "GTC",
                "is_in_pips": ''
                }



            def change_status(checkbox, line_edit):
                """
                Small checkbox controller (toggle on/of corresponing line based on status)
                input: checkbox object, corresponding line_edit
                output: toggle on/off line edit
                """
                if checkbox.isChecked():
                    line_edit.setEnabled(1)
                else:
                    line_edit.setDisabled(1)
            def update_trading_values():
                """
                Function to update trading values for future operations
                """
                trading_values['amount'] = float(self.ui_open_position.lineEdit.text())
                trading_values['symbol'] = str(self.ui_open_position.comboBox.currentText())
                if self.ui_open_position.lineEdit_2.isEnabled():
                    trading_values['stop'] = float(self.ui_open_position.lineEdit_2.text())
                if self.ui_open_position.lineEdit_3.isEnabled():
                    trading_values['trailing_step'] = float(self.ui_open_position.lineEdit_3.text())
                if self.ui_open_position.lineEdit_4.isEnabled():
                    trading_values['limit'] = float(self.ui_open_position.lineEdit_4.text())
                trading_values['is_in_pips'] = bool(self.ui_open_position.checkBox_4.isChecked)
                if self.ui_open_position.radioButton.isChecked():
                    trading_values['is_buy'] = True

            
            
            def open_position_result(result):
                """
                Showing result when open_position_thread_class gets the result of opening a position. 
                """
                QtWidgets.QMessageBox.about(self.dialog_open_position, 'Result message', result)
            
            class open_position_thread_class(QThread):
                """
                This class inherits from QThread, created to handle opening a position.
                (It prevents the app from getting frozen when waiting for result)
                """

                finished=pyqtSignal(str)
                def __init__(self, trading_values, controller):
                    QThread.__init__(self)
                    self.controller=controller
                    self.trading_values=trading_values

                def run(self):
                    try:
                        result=self.controller.open_position(**trading_values)
                        if result!=None:
                            self.finished.emit('Position created')
                        else:
                            self.finished.emit('Position could not be created!')
                    except Exception as e:
                         self.finished.emit(str(e))
            
            def open_position_func():
                """
                This function is called when open postion button is clicked
                Is creates an instance of open_position_thread_class and starts it to 
                open a position without causing app to freeze.
                """
                self.open_position_thread=open_position_thread_class(trading_values, self.controller)
                self.open_position_thread.finished.connect(open_position_result)
                self.open_position_thread.start()


            """
            Setting button's trigger function and default items' values
            """
            self.ui_open_position.lineEdit.setText('1')
            self.ui_open_position.comboBox.addItems(self.controller.available_symbols_list)
            self.ui_open_position.radioButton.setChecked(True)
            self.ui_open_position.checkBox.stateChanged.connect(lambda: change_status(self.ui_open_position.checkBox, self.ui_open_position.lineEdit_2))
            self.ui_open_position.checkBox_2.stateChanged.connect(lambda: change_status(self.ui_open_position.checkBox_2, self.ui_open_position.lineEdit_3))
            self.ui_open_position.checkBox_3.stateChanged.connect(lambda: change_status(self.ui_open_position.checkBox_3, self.ui_open_position.lineEdit_4))
            self.ui_open_position.buttonBox.accepted.connect(update_trading_values)
            self.ui_open_position.buttonBox.accepted.connect(open_position_func)
            self.dialog_open_position.show()

            
    def edit_position_stop_limit(self):
        """
        This function is called from open positions window when edit button is clicked.
        It opens edit position page
        """
        if self.controller.connection_status == 'Disconnected':
            self.open_warning()
        else:

            self.dialog_view_open_positions.dialog = QtWidgets.QDialog()
            self.dialog_view_open_positions.ui = Ui_EditTradeStopLimit()
            self.dialog_view_open_positions.ui.setupUi(self.dialog_view_open_positions.dialog)
            self.dialog_view_open_positions.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
            self.dialog_view_open_positions.setWindowFlag(Qt.WindowMaximizeButtonHint, True)

            #Dictionary holding values for editing postion
            edit_position = {
                'trade_id': 0
            }

            # Window functionality
            def update_fields_func():
                """
                Updating position values
                """
                edit_position['trade_id'] = int(self.ui_view_open_positions.tableWidget.item(self.ui_view_open_positions.tableWidget.currentRow(), 2).text())
                if str(self.dialog_view_open_positions.ui.comboBox.currentText()) == "Stop":
                    edit_position['is_stop'] = True
                else:
                    edit_position['is_stop'] = False
                if self.dialog_view_open_positions.ui.lineEdit.text():
                    edit_position['rate'] = float(self.dialog_view_open_positions.ui.lineEdit.text())
                if self.dialog_view_open_positions.ui.lineEdit_2.text():
                    edit_position['trailing_step'] = float(self.dialog_view_open_positions.ui.lineEdit_2.text())
                if self.dialog_view_open_positions.ui.checkBox.isChecked():
                    edit_position['is_in_pips'] = True
                else:
                    edit_position['is_in_pips'] = False

            class edit_position_thread_class(QThread):
                """
                This class inherits from QThread, created to handle editing a position.
                (It prevents the app from getting frozen when waiting for result)
                """
                def __init__(self, controller, edit_position):
                    QThread.__init__(self)
                    self.controller=controller
                    self.edit_position=edit_position
                
                def run(self):
                    try:
                        self.controller.edit_position_stop_limit(**self.edit_position)
                    except:
                        pass

            def edit_position_func(self):
                """
                This function is called when edit or ok button is clicked
                Is creates an instance of edit_position_thread_class and starts it to 
                edit a position without causing app to freeze.
                """
                self.edit_position_thread=edit_position_thread_class(self.controller, edit_position)
                self.edit_position_thread.start()


            """
            Setting button's trigger function
            """

            self.dialog_view_open_positions.ui.buttonBox.accepted.connect(update_fields_func)
            self.dialog_view_open_positions.ui.buttonBox.accepted.connect(edit_position_func)
            self.dialog_view_open_positions.dialog.show()


    def start_all_trading_strategy(self):
        """
        This function does not open any page, it just creates a temporary thread to start all strategeis 
        """
        if self.controller.connection_status == 'Disconnected':
            self.open_warning()
        else:
            class start_all_strategies_thread_class(QThread):
                """
                This class inherits from QThread, created to handle starting all strategies.
                (It prevents the app from getting frozen when waiting for result)
                """
                def __init__(self, strategy_controller):
                    QThread.__init__(self)
                    self.strategy_controller=strategy_controller

                def run(self):
                    try:
                        self.strategy_controller.start_all_strategies()
                    except:
                        pass


            """
            Instantiating start_all_strategies_thread_class and starting it to start all strategies
            """
            self.start_all_strategies_thread=start_all_strategies_thread_class(self.strategy_controller)
            self.start_all_strategies_thread.start()            



    def stop_all_trading_strategy(self):
        """
        This function does not open any page, it just calls stop_all_strategies method of strategy controller to stop 
        all strategies
        """
        self.strategy_controller.stop_all_strategies()


    def open_auto_trading_page(self):
        """
        Function to open strategy panel window.
        """

        """
        Checking if threads of strategy panel are alive, if so stop them 
        """
        try:
            self.ui_autotrading.update_strategy_status_thread.stop()
            self.ui_autotrading.update_strategy_status_thread.wait()
            del self.ui_autotrading.update_strategy_status_thread
        except:
            pass

        # Window initialization
        self.dialog_autotrading = QtWidgets.QDialog()
        self.ui_autotrading = Ui_autotrading_page()
        self.ui_autotrading.setupUi(self.dialog_autotrading)
        self.dialog_autotrading.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
        self.dialog_autotrading.setWindowFlag(Qt.WindowMaximizeButtonHint, True)
        
        #Setting all button disable
        self.ui_autotrading.selected_strategies_delete_strategy_button_2.setEnabled(False)
        self.ui_autotrading.selected_strategies_start_strategy_button_2.setEnabled(False)
        self.ui_autotrading.selected_strategies_stop_strategy_button_2.setEnabled(False)
        self.ui_autotrading.selected_strategies_edit_button_2.setEnabled(False)
        self.ui_autotrading.pushButton.setEnabled(False)
        self.ui_autotrading.selected_strategies_start_all_strategy_button_2.setEnabled(False)
        self.ui_autotrading.selected_strategies_stop_all_strategy_button_2.setEnabled(False)


        def closeEvent(event):
            try:
                """
                CloseEvent function to be replaced with this window's exit event 
                """
                self.ui_autotrading.update_strategy_status_thread.stop()
                self.ui_autotrading.update_strategy_status_thread.wait()
                del self.ui_autotrading.update_strategy_status_thread
                event.accept()
            except Exception as e:
                print(e)
                event.accept()

        
        def switch_strategy_status():
            """
            This function is called when an item in the list is clicked
            If no error happens, it enables all buttons and changes the current strategy name
            that the start_strategy_thread_class thread uses for updating strategy status bar
            otherwise, it disables buttons
            """

            try:
                self.ui_autotrading.selected_strategies_delete_strategy_button_2.setEnabled(True)
                self.ui_autotrading.selected_strategies_start_strategy_button_2.setEnabled(True)
                self.ui_autotrading.selected_strategies_stop_strategy_button_2.setEnabled(True)
                self.ui_autotrading.selected_strategies_edit_button_2.setEnabled(True)
                self.ui_autotrading.pushButton.setEnabled(True)
                self.ui_autotrading.update_strategy_status_thread.change_strategy_name(self.ui_autotrading.selected_strategies_list.currentItem().text())
            except Exception as e:
                print(e)
                self.ui_autotrading.selected_strategies_delete_strategy_button_2.setEnabled(False)
                self.ui_autotrading.selected_strategies_start_strategy_button_2.setEnabled(False)
                self.ui_autotrading.selected_strategies_stop_strategy_button_2.setEnabled(False)
                self.ui_autotrading.selected_strategies_edit_button_2.setEnabled(False)
                self.ui_autotrading.pushButton.setEnabled(False)

        def delete_trading_strategy():
            """
            It is called when delete button is clicked, it calls delete_strategy method of strategy controller and passes strategy name
            then it disables all buttons again, and checks if no strategy is in the list, it disables start all and stop all button too.
            """
            question_result=QtWidgets.QMessageBox.question(self.dialog_autotrading,'', "Are you sure to delete the strategy?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if question_result==QtWidgets.QMessageBox.Yes:
                self.strategy_controller.delete_strategy(self.ui_autotrading.selected_strategies_list.currentItem().text())
                self.ui_autotrading.selected_strategies_list.takeItem(self.ui_autotrading.selected_strategies_list.row(self.ui_autotrading.selected_strategies_list.selectedItems()[0]))
                self.ui_autotrading.selected_strategies_delete_strategy_button_2.setEnabled(False)
                self.ui_autotrading.selected_strategies_start_strategy_button_2.setEnabled(False)
                self.ui_autotrading.selected_strategies_stop_strategy_button_2.setEnabled(False)
                self.ui_autotrading.selected_strategies_edit_button_2.setEnabled(False)
                self.ui_autotrading.pushButton.setEnabled(False)
                self.ui_autotrading.update_strategy_status_thread.change_strategy_name('')
                if self.ui_autotrading.selected_strategies_list.count()==0:
                    self.ui_autotrading.selected_strategies_start_all_strategy_button_2.setEnabled(False)
                    self.ui_autotrading.selected_strategies_stop_all_strategy_button_2.setEnabled(False)



        
        class start_strategy_thread_class(QThread):
            """
            This class inherits from QThread, created to handle starting strategies.
            (It prevents the app from getting frozen when waiting for result)
            """
            
            def __init__(self, strategy_controller, strategy_name):
                QThread.__init__(self)
                self.strategy_controller=strategy_controller
                self.strategy_name=strategy_name

            def run(self):
                try:
                    self.strategy_controller.start_strategy(self.strategy_name)
                except:
                    pass

        
    
        def start_trading_strategy():
            """
            It is called when start strategy button is clicked, it creates an instance of start_strategy_thread_class
            by passing strategy controller instance and selected strategy from list, and starts it to start a strategy.
            """
            if self.controller.connection_status == 'Disconnected':
                self.open_warning()
            else:
                self.start_strategy_thread=start_strategy_thread_class(self.strategy_controller, self.ui_autotrading.selected_strategies_list.currentItem().text())
                self.start_strategy_thread.start()            

        def stop_trading_strategy():
            """
            It is called when stop strategy button is clicked.
            """
            self.strategy_controller.stop_strategy(self.ui_autotrading.selected_strategies_list.currentItem().text())
    
        def create_saved_strategies_content():
            """
            This functions shows created strategies on the list.
            It is the first function called when strategy panel opens
            strategy_setting_dict attribute of strategy controller is a dictionary that keeps 
            the information of created strategies 
            """
            for key, value in self.strategy_controller.strategy_setting_dict.items():
                self.ui_autotrading.selected_strategies_list.addItem(value['strategy_name'])
            self.ui_autotrading.selected_strategies_list.clicked.connect(switch_strategy_status)


        def update_strategy_status(status_tuple):
            """
            This function is called when the below thread (update_strategy_status_thread_class) emits new data
            It changes values of last start last stop and strategy status in status bar
            """
            self.ui_autotrading.label_10.setText(status_tuple[0])
            self.ui_autotrading.label_11.setText(status_tuple[1])
            self.ui_autotrading.label_12.setText(status_tuple[2])

        class update_strategy_status_thread_class(QThread):
            """
            This class inherits from QThread, created to handle updating strategy status.
            It is started as soon as the window is opened, using strategy_controller instances passed to it,
            it call strategy_status_get method of strategy controller by passing strategy name to get strategy status.
            In every iteration in while loop of run method, it checks for changes in the selected strategy from the list 
            (It prevents the app from getting frozen when waiting for result)
            """

            tupleReady=pyqtSignal(tuple)
            def __init__(self, strategy_controller_obj):
                QThread.__init__(self)
                self.strategy_controller_obj=strategy_controller_obj
                self.strategy_name=''
                self.stop_signal=False
            
            def stop(self):
                self.stop_signal=True

            def change_strategy_name(self, strategy_name):
                self.strategy_name=strategy_name

            def run(self):
                try:
                    strategy_name=self.strategy_name
                    while True:
                        if self.stop_signal==True:
                            break
                        else:
                            try:
                                if strategy_name!=self.strategy_name:
                                    strategy_name=self.strategy_name
                                if self.strategy_name!='':
                                    status_tuple=self.strategy_controller_obj.strategy_status_get(self.strategy_name)
                                    self.tupleReady.emit(status_tuple)
                                time.sleep(1)
                            except Exception as e:
                                print(e)
                except Exception as e:
                    print(e, 'update_strategy_status_thread_class')



        """
        Setting button's trigger function and default items' values and creating update_strategy_status_thread and 
        starting it 
        """
        create_saved_strategies_content()
        if self.ui_autotrading.selected_strategies_list.count()>0:
            self.ui_autotrading.selected_strategies_start_all_strategy_button_2.setEnabled(True)
            self.ui_autotrading.selected_strategies_stop_all_strategy_button_2.setEnabled(True)
        self.ui_autotrading.selected_strategies_add_strategy_button_2.clicked.connect(self.open_auto_trading_add_strategy_page)
        self.ui_autotrading.selected_strategies_delete_strategy_button_2.clicked.connect(delete_trading_strategy)
        self.ui_autotrading.selected_strategies_start_strategy_button_2.clicked.connect(start_trading_strategy)
        self.ui_autotrading.selected_strategies_stop_strategy_button_2.clicked.connect(stop_trading_strategy)
        self.ui_autotrading.selected_strategies_start_all_strategy_button_2.clicked.connect(self.start_all_trading_strategy)
        self.ui_autotrading.selected_strategies_stop_all_strategy_button_2.clicked.connect(self.stop_all_trading_strategy)
        self.ui_autotrading.selected_strategies_edit_button_2.clicked.connect(lambda: self.open_auto_trading_edit_strategy_page(self.ui_autotrading.selected_strategies_list.currentItem().text()))
        self.ui_autotrading.pushButton.clicked.connect(lambda: self.open_auto_trading_backtest_page(self.ui_autotrading.selected_strategies_list.currentItem().text()))
        self.dialog_autotrading.closeEvent=closeEvent
        self.ui_autotrading.update_strategy_status_thread=update_strategy_status_thread_class(self.strategy_controller)
        self.ui_autotrading.update_strategy_status_thread.tupleReady.connect(update_strategy_status)
        self.ui_autotrading.update_strategy_status_thread.start()
        self.dialog_autotrading.show()


    def open_auto_trading_backtest_page(self, strategy_name):
        """
        This function opens backtest window, it is called when backtest button from strategy panel is clicked.
        """

        # Window initialization
        self.dialog_auto_trading_backtest = QtWidgets.QDialog()
        self.ui_auto_trading_backtest = Ui_Ui_autotrading_backtest_strategy_page()
        self.ui_auto_trading_backtest.setupUi(self.dialog_auto_trading_backtest)
        self.dialog_auto_trading_backtest.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
        self.dialog_auto_trading_backtest.setWindowFlag(Qt.WindowMaximizeButtonHint, True)

        self.ui_auto_trading_backtest.horizontalLayout_backtest_result = QtWidgets.QHBoxLayout()
        self.ui_auto_trading_backtest.verticalLayout_backtest_result_labels = QtWidgets.QVBoxLayout()
        self.ui_auto_trading_backtest.verticalLayout_backtest_result_labels_result = QtWidgets.QVBoxLayout()
        self.ui_auto_trading_backtest.horizontalLayout_backtest_result.addLayout(self.ui_auto_trading_backtest.verticalLayout_backtest_result_labels)
        self.ui_auto_trading_backtest.horizontalLayout_backtest_result.addLayout(self.ui_auto_trading_backtest.verticalLayout_backtest_result_labels_result)
        self.ui_auto_trading_backtest.scrollAreaWidgetContents.setLayout(self.ui_auto_trading_backtest.horizontalLayout_backtest_result)
        self.ui_auto_trading_backtest.progressBar.setValue(0)
        self.ui_auto_trading_backtest.backtest_label_dict={}
        self.ui_auto_trading_backtest.backtest_label_result_dict={}



        def closeEvent(event):
            """
            CloseEvent function to be replaced with this window's exit event 
            """            
            try:
                self.ui_auto_trading_backtest.progressBar.setValue(0)
                self.strategy_controller.backtest_stop(strategy_name)
                self.ui_auto_trading_backtest.backtesting_thread.stop()
                self.ui_auto_trading_backtest.backtesting_thread.wait()
                self.ui_auto_trading_backtest.backtesting_start_thread.wait()
                del self.ui_auto_trading_backtest.backtesting_thread
                del self.ui_auto_trading_backtest.backtesting_start_thread
                event.accept()
            except Exception as e:
                print(e)
                self.ui_auto_trading_backtest.progressBar.setValue(0)
                self.strategy_controller.backtest_stop(strategy_name)
                event.accept()
            


        def create_backtest_result_content(backtest_result):
            try:
                """
                It shows backtest when the backtesting thread finishes its task.
                """
                #Deleting all result container content.
                for key, value in self.ui_auto_trading_backtest.backtest_label_dict.items():
                    self.ui_auto_trading_backtest.verticalLayout_backtest_result_labels.removeWidget(value)
                    value.deleteLater()
                    value=None

                for key, value in self.ui_auto_trading_backtest.backtest_label_result_dict.items():
                    self.ui_auto_trading_backtest.verticalLayout_backtest_result_labels_result.removeWidget(value)
                    value.deleteLater()
                    value=None
                    
                #Creating content
                self.ui_auto_trading_backtest.backtest_label_dict={}
                self.ui_auto_trading_backtest.backtest_label_result_dict={}
                for key, value in backtest_result.items():
                    self.ui_auto_trading_backtest.backtest_label_dict[key] = QtWidgets.QLabel()
                    self.ui_auto_trading_backtest.backtest_label_dict[key].setText(key)
                    self.ui_auto_trading_backtest.backtest_label_result_dict[key] = QtWidgets.QLabel()
                    self.ui_auto_trading_backtest.backtest_label_result_dict[key].setText(str(value))
                    self.ui_auto_trading_backtest.verticalLayout_backtest_result_labels.addWidget(self.ui_auto_trading_backtest.backtest_label_dict[key])
                    self.ui_auto_trading_backtest.verticalLayout_backtest_result_labels_result.addWidget(self.ui_auto_trading_backtest.backtest_label_result_dict[key])
                self.ui_auto_trading_backtest.progressBar.setValue(0)
            except Exception as e:
                print(e)

        def update_progress_bar(progress_percentage):
            """
            It updates progress bar. It is called when backtesting_thread emits new progress value.
            """
            self.ui_auto_trading_backtest.progressBar.setValue(progress_percentage)

        def strategy_backtest_clicked():
            try:
                """
                It is called when backtest button is clicked. it creates an instance of backtesting_start_thread and
                backtesting_thread and starts them to start backtesing and getting its progress percentage and finally
                show the result
                """
                qty=int(self.ui_auto_trading_backtest.lineEdit.text())
                cap=int(self.ui_auto_trading_backtest.lineEdit_2.text())
                if qty<=10000:
                    self.ui_auto_trading_backtest.progressBar.setValue(0)
                    self.ui_auto_trading_backtest.backtesting_start_thread=backtesting_start_thread(self.strategy_controller, strategy_name, qty, cap)
                    self.ui_auto_trading_backtest.backtesting_start_thread.start()          
                    self.ui_auto_trading_backtest.backtesting_thread=backtesting_thread(self.strategy_controller, strategy_name)
                    self.ui_auto_trading_backtest.backtesting_thread.intReady.connect(update_progress_bar)
                    self.ui_auto_trading_backtest.backtesting_thread.dictReady.connect(create_backtest_result_content)
                    self.ui_auto_trading_backtest.backtesting_thread.start()
                else:
                    QtWidgets.QMessageBox.about(self.dialog_auto_trading_backtest, 'Result message', 'Quantity must be less than or equal 10000')
            except:
                QtWidgets.QMessageBox.about(self.dialog_auto_trading_backtest, 'Result message', 'All fields must be filled')

        
        class backtesting_start_thread(QThread):
            """
            This class inherits from QThread, created to handle starting backtest.
            (It prevents the app from getting frozen when waiting for result)
            """
            def __init__(self, strategy_controller_obj, strategy_name, quantity, capital):
                QThread.__init__(self)
                self.strategy_controller_obj=strategy_controller_obj
                self.strategy_name=strategy_name
                self.quantity=quantity
                self.capital=capital

            def run(self):
                backtesting_result=self.strategy_controller_obj.backtest_strategy(self.strategy_name, self.quantity, self.capital)



        class backtesting_thread(QThread):
            """
            This class inherits from QThread, created to handle getting progress percentage and final result.
            (It prevents the app from getting frozen when waiting for result)
            """
            intReady=pyqtSignal(int)
            dictReady=pyqtSignal(dict)

            def __init__(self, strategy_controller_obj, strategy_name):
                QThread.__init__(self)
                self.strategy_controller_obj=strategy_controller_obj
                self.strategy_name=strategy_name
                self.stop_signal=False

            def stop(self):
                self.stop_signal=True

            def run(self):
                backtest_result={}
                while True:
                    try:
                        if self.stop_signal==True:
                            break
                        elif self.strategy_controller_obj.get_backtest_result(strategy_name)!={}:
                            backtest_result=self.strategy_controller_obj.get_backtest_result(strategy_name)
                            progress_percentage=self.strategy_controller_obj.get_backtest_progress_rate(self.strategy_name)
                            self.intReady.emit(progress_percentage)
                            break
                        else:
                            progress_percentage=self.strategy_controller_obj.get_backtest_progress_rate(self.strategy_name)
                            self.intReady.emit(progress_percentage)
                            time.sleep(1)
                    
                    except Exception as e:
                        print(e)
                        backtest_result={}
                self.dictReady.emit(backtest_result)

        def cancel_button_clicked():
            try:
                """
                This function is called when cancel button is clicked.
                """

                self.ui_auto_trading_backtest.progressBar.setValue(0)
                self.strategy_controller.backtest_stop(strategy_name)
                self.ui_auto_trading_backtest.backtesting_thread.stop()
                self.ui_auto_trading_backtest.backtesting_thread.wait()
                self.ui_auto_trading_backtest.backtesting_start_thread.wait()
                del self.ui_auto_trading_backtest.backtesting_thread
                del self.ui_auto_trading_backtest.backtesting_start_thread
                self.dialog_auto_trading_backtest.done(1)

            except Exception as e:
                print(e)
                self.ui_auto_trading_backtest.progressBar.setValue(0)
                self.strategy_controller.backtest_stop(strategy_name)
                self.dialog_auto_trading_backtest.done(1)
            


        """
        Setting buttons' trigger function
        """
        self.dialog_auto_trading_backtest.closeEvent=closeEvent
        self.ui_auto_trading_backtest.pushButton.clicked.connect(strategy_backtest_clicked)
        self.ui_auto_trading_backtest.pushButton_2.clicked.connect(cancel_button_clicked)

        self.dialog_auto_trading_backtest.show()


    def open_auto_trading_edit_strategy_page(self, strategy_name):
        """
        This function opens add strategy window
        """
        # Window initialization
        self.dialog_edit_strategy = QtWidgets.QDialog()
        self.ui_edit_strategy = Ui_autotrading_edit_strategy_page()
        self.ui_edit_strategy.setupUi(self.dialog_edit_strategy)
        self.dialog_edit_strategy.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
        self.dialog_edit_strategy.setWindowFlag(Qt.WindowMaximizeButtonHint, True)

        self.ui_edit_strategy.horizontalLayout_risk_management_inputs = QtWidgets.QHBoxLayout()
        self.ui_edit_strategy.verticalLayout_risk_management_inputs_labels = QtWidgets.QVBoxLayout()
        self.ui_edit_strategy.verticalLayout_risk_management_inputs_lineEdit = QtWidgets.QVBoxLayout()
        self.ui_edit_strategy.horizontalLayout_risk_management_inputs.addLayout(self.ui_edit_strategy.verticalLayout_risk_management_inputs_labels)
        self.ui_edit_strategy.horizontalLayout_risk_management_inputs.addLayout(self.ui_edit_strategy.verticalLayout_risk_management_inputs_lineEdit)
        self.ui_edit_strategy.scrollAreaWidgetContents_3.setLayout(self.ui_edit_strategy.horizontalLayout_risk_management_inputs)

        self.ui_edit_strategy.horizontalLayout_strategy_inputs = QtWidgets.QHBoxLayout()
        self.ui_edit_strategy.verticalLayout_strategy_inputs_labels = QtWidgets.QVBoxLayout()
        self.ui_edit_strategy.verticalLayout_strategy_inputs_lineEdit = QtWidgets.QVBoxLayout()
        self.ui_edit_strategy.horizontalLayout_strategy_inputs.addLayout(self.ui_edit_strategy.verticalLayout_strategy_inputs_labels)
        self.ui_edit_strategy.horizontalLayout_strategy_inputs.addLayout(self.ui_edit_strategy.verticalLayout_strategy_inputs_lineEdit)
        self.ui_edit_strategy.scrollAreaWidgetContents_2.setLayout(self.ui_edit_strategy.horizontalLayout_strategy_inputs)

        self.ui_edit_strategy.horizontalLayout_news_reactor_inputs = QtWidgets.QHBoxLayout()
        self.ui_edit_strategy.verticalLayout_news_reactor_inputs_labels = QtWidgets.QVBoxLayout()
        self.ui_edit_strategy.verticalLayout_news_reactor_inputs_lineEdit = QtWidgets.QVBoxLayout()
        self.ui_edit_strategy.horizontalLayout_news_reactor_inputs.addLayout(self.ui_edit_strategy.verticalLayout_news_reactor_inputs_labels)
        self.ui_edit_strategy.horizontalLayout_news_reactor_inputs.addLayout(self.ui_edit_strategy.verticalLayout_news_reactor_inputs_lineEdit)
        self.ui_edit_strategy.scrollAreaWidgetContents.setLayout(self.ui_edit_strategy.horizontalLayout_news_reactor_inputs)



        """
        Getting saved values of selected strategy and assiging them to a certain variable
        """
        strategy_system=self.strategy_controller.strategy_setting_dict[strategy_name]['trading_strategy_system']
        risk_management_system=self.strategy_controller.strategy_setting_dict[strategy_name]['risk_management_system']
        news_reactor_system=self.strategy_controller.strategy_setting_dict[strategy_name]['news_reactor_system']


        def create_risk_management_inputs():
            """
            This function creates selected risk management system content and sets the saved values to its related field.
            It removes the content first and gets the data of selected system from its related class attribute and 
            iterates over the data to create content
            """
            self.ui_edit_strategy.risk_management_inputs_labels_obj_dict={}
            self.ui_edit_strategy.risk_management_inputs_inputs_obj_dict={}            
            for key, value in self.risk_managements_inputs_dict[risk_management_system].items():
                self.ui_edit_strategy.risk_management_inputs_labels_obj_dict[value[0]] = QtWidgets.QLabel()
                self.ui_edit_strategy.risk_management_inputs_labels_obj_dict[value[0]].setText(key)
                self.ui_edit_strategy.risk_management_inputs_inputs_obj_dict[value[0]] = QtWidgets.QLineEdit()
                self.ui_edit_strategy.risk_management_inputs_inputs_obj_dict[value[0]].setText(str(self.strategy_controller.strategy_setting_dict[strategy_name]['risk_management_system_inputs'][value[0]]))
                self.ui_edit_strategy.verticalLayout_risk_management_inputs_labels.addWidget(self.ui_edit_strategy.risk_management_inputs_labels_obj_dict[value[0]])
                self.ui_edit_strategy.verticalLayout_risk_management_inputs_lineEdit.addWidget(self.ui_edit_strategy.risk_management_inputs_inputs_obj_dict[value[0]])

        def create_trading_strategy_inputs():
            """
            This function creates selected trading strategy system content and sets the saved values to its related field.
            It removes the content first and gets the data of selected system from its related class attribute and 
            iterates over the data to create content
            """
            self.ui_edit_strategy.strategy_inputs_labels_obj_dict={}
            self.ui_edit_strategy.strategy_inputs_inputs_obj_dict={}
            for key, value in self.strategies_inputs_dict[strategy_system].items():
                self.ui_edit_strategy.strategy_inputs_labels_obj_dict[value[0]] = QtWidgets.QLabel()
                self.ui_edit_strategy.strategy_inputs_labels_obj_dict[value[0]].setText(key)
                self.ui_edit_strategy.strategy_inputs_inputs_obj_dict[value[0]] = QtWidgets.QLineEdit()
                self.ui_edit_strategy.strategy_inputs_inputs_obj_dict[value[0]].setText(str(self.strategy_controller.strategy_setting_dict[strategy_name]['trading_strategy_inputs'][value[0]]))
                self.ui_edit_strategy.verticalLayout_strategy_inputs_labels.addWidget(self.ui_edit_strategy.strategy_inputs_labels_obj_dict[value[0]])
                self.ui_edit_strategy.verticalLayout_strategy_inputs_lineEdit.addWidget(self.ui_edit_strategy.strategy_inputs_inputs_obj_dict[value[0]])

        def create_news_reactor_inputs():
            """
            This function creates selected news reactor system content and sets the saved values to its related field.
            It removes the content first and gets the data of selected system from its related class attribute and 
            iterates over the data to create content
            """
            self.ui_edit_strategy.news_reactor_inputs_labels_obj_dict={}
            self.ui_edit_strategy.news_reactor_inputs_inputs_obj_dict={}
            for key, value in self.news_reactors_inputs_dict[news_reactor_system].items():
                if type(value[1])==bool: #Checking if the type of stored value is bool, then it create checkbox instead of lineEdit widget.
                    self.ui_edit_strategy.news_reactor_inputs_labels_obj_dict[value[0]] = QtWidgets.QLabel()
                    self.ui_edit_strategy.news_reactor_inputs_labels_obj_dict[value[0]].setText(key)
                    self.ui_edit_strategy.news_reactor_inputs_inputs_obj_dict[value[0]] = QtWidgets.QCheckBox()
                    if value[1]==True:
                        self.ui_edit_strategy.news_reactor_inputs_inputs_obj_dict[value[0]].setChecked(True)
                    self.ui_edit_strategy.verticalLayout_news_reactor_inputs_labels.addWidget(self.ui_edit_strategy.news_reactor_inputs_labels_obj_dict[value[0]])
                    self.ui_edit_strategy.verticalLayout_news_reactor_inputs_lineEdit.addWidget(self.ui_edit_strategy.news_reactor_inputs_inputs_obj_dict[value[0]])
                else:
                    self.ui_edit_strategy.news_reactor_inputs_labels_obj_dict[value[0]] = QtWidgets.QLabel()
                    self.ui_edit_strategy.news_reactor_inputs_labels_obj_dict[value[0]].setText(key)
                    self.ui_edit_strategy.news_reactor_inputs_inputs_obj_dict[value[0]] = QtWidgets.QLineEdit()
                    self.ui_edit_strategy.news_reactor_inputs_inputs_obj_dict[value[0]].setText(str(self.strategy_controller.strategy_setting_dict[strategy_name]['news_reactor_inputs'][value[0]]))
                    self.ui_edit_strategy.verticalLayout_news_reactor_inputs_labels.addWidget(self.ui_edit_strategy.news_reactor_inputs_labels_obj_dict[value[0]])
                    self.ui_edit_strategy.verticalLayout_news_reactor_inputs_lineEdit.addWidget(self.ui_edit_strategy.news_reactor_inputs_inputs_obj_dict[value[0]])

        
        def edit_strategy_clicked():
            """
            This function adds strategy. It is called when add button is clicked
            """

            #Setting initial values for input validation 
            check_symbol=True
            check_timeframe=True
            check_risk_management_inputs=True
            check_strategy_inputs=True
            check_news_reactor_inputs=True
            strategy_inputs_dict_args={} #Dictionary for holding trading strategy system inputs to pass to add_strategy method of strategy controller
            risk_management_inputs_dict_args={} #Dictionary for holding risk management system inputs to pass to add_strategy method of strategy controller
            news_reactor_inputs_dict_args={} #Dictionary for holding news reactor system inputs to pass to add_strategy method of strategy controller
            

            """
            This section is for validation of inputs.
            But currently it just checks if all inputs are filled, not any kind of validation to check if the inputs are correct 
            """            
            for key, value in self.ui_edit_strategy.risk_management_inputs_inputs_obj_dict.items(): #Iterating over risk management system inputs and converting them to float and inserting them to 
                try:
                    input_temp=float(value.text())
                    risk_management_inputs_dict_args[key]=input_temp
                except Exception as e:
                    check_risk_management_inputs=False
                    print(e)

            for key, value in self.ui_edit_strategy.strategy_inputs_inputs_obj_dict.items(): #Iterating over trading strategy system inputs and converting them to float and inserting them to 
                try:
                    input_temp=float(value.text())
                    strategy_inputs_dict_args[key]=input_temp
                except Exception as e:
                    check_strategy_inputs=False
                    print(e)

            if news_reactor_system!='None':
                for key, value in self.ui_edit_strategy.news_reactor_inputs_inputs_obj_dict.items(): #Iterating over news reactor system inputs and converting them to float and inserting them to 
                    try:
                        if type(value).__name__=='QCheckBox': #Checking if type of pyqt object of the input field is checkbox, then if is checked it adds True to news reactor argument
                            input_temp=True if value.isChecked() == True else False
                            news_reactor_inputs_dict_args[key]=input_temp
                        else:
                            input_temp=float(value.text())
                            news_reactor_inputs_dict_args[key]=input_temp
                    except Exception as e:
                        check_news_reactor_inputs=False
                        print(e)

                """
                Checking all validation related variables, and if the condition is ture, then inserting inputs to a dictionary to pass to 
                edit_strategy method of strategy_controller to add a strategy.
                """                        
            if check_risk_management_inputs==True and check_strategy_inputs==True and check_news_reactor_inputs==True and check_symbol==True and check_timeframe==True:
                strategy_arguments_dict={
                                        'timeframe':self.ui_edit_strategy.comboBox.currentText(),
                                        'trading_strategy_system':strategy_system,
                                        'trading_strategy_inputs':strategy_inputs_dict_args,
                                        'risk_management_system':risk_management_system,
                                        'risk_management_system_inputs':risk_management_inputs_dict_args,
                                        'news_reactor_system':news_reactor_system,
                                        'news_reactor_inputs':news_reactor_inputs_dict_args
                                        }
                self.strategy_controller.edit_strategy(strategy_name, strategy_arguments_dict)
                QtWidgets.QMessageBox.about(self.dialog_edit_strategy, 'Result message', 'Strategy is successfully edited')
                self.dialog_edit_strategy.close()
            else:
                QtWidgets.QMessageBox.about(self.dialog_edit_strategy, 'Result message', 'All fields must be filled')

        def cancel_button_clicked():
            """
            This function is called when cancel button is clicked. Basically it destroys the window.
            """
            self.dialog_edit_strategy.destroy()

        """
        Setting buttons' trigger function, and default values of items
        """
        create_risk_management_inputs()
        create_trading_strategy_inputs()
        if news_reactor_system!='None':
            create_news_reactor_inputs()
        self.ui_edit_strategy.comboBox.addItems(self.auto_trading_timeframe_list)
        self.ui_edit_strategy.comboBox.setCurrentIndex(self.ui_edit_strategy.comboBox.findText(self.strategy_controller.strategy_setting_dict[strategy_name]['timeframe']))
        self.ui_edit_strategy.pushButton.clicked.connect(edit_strategy_clicked)
        self.ui_edit_strategy.pushButton_2.clicked.connect(cancel_button_clicked)

        self.dialog_edit_strategy.show()


    def open_auto_trading_add_strategy_page(self):
        """
        This function opens add strategy window
        """

        # Window initialization
        self.dialog_add_strategy = QtWidgets.QDialog()
        self.ui_add_strategy = Ui_autotrading_add_strategy_page()
        self.ui_add_strategy.setupUi(self.dialog_add_strategy)
        self.ui_add_strategy.stackedWidget.setCurrentIndex(0)
        self.ui_add_strategy.textEdit.setReadOnly(True)
        self.ui_add_strategy.textEdit_2.setReadOnly(True)
        self.ui_add_strategy.auto_trading_add_strategy_next_1_button.setEnabled(False)
        self.dialog_add_strategy.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
        self.dialog_add_strategy.setWindowFlag(Qt.WindowMaximizeButtonHint, True)

        
        self.ui_add_strategy.horizontalLayout_risk_management_inputs = QtWidgets.QHBoxLayout()
        self.ui_add_strategy.verticalLayout_risk_management_inputs_labels = QtWidgets.QVBoxLayout()
        self.ui_add_strategy.verticalLayout_risk_management_inputs_lineEdit = QtWidgets.QVBoxLayout()
        self.ui_add_strategy.horizontalLayout_risk_management_inputs.addLayout(self.ui_add_strategy.verticalLayout_risk_management_inputs_labels)
        self.ui_add_strategy.horizontalLayout_risk_management_inputs.addLayout(self.ui_add_strategy.verticalLayout_risk_management_inputs_lineEdit)
        self.ui_add_strategy.scrollAreaWidgetContents_3.setLayout(self.ui_add_strategy.horizontalLayout_risk_management_inputs)

        self.ui_add_strategy.horizontalLayout_strategy_inputs = QtWidgets.QHBoxLayout()
        self.ui_add_strategy.verticalLayout_strategy_inputs_labels = QtWidgets.QVBoxLayout()
        self.ui_add_strategy.verticalLayout_strategy_inputs_lineEdit = QtWidgets.QVBoxLayout()
        self.ui_add_strategy.horizontalLayout_strategy_inputs.addLayout(self.ui_add_strategy.verticalLayout_strategy_inputs_labels)
        self.ui_add_strategy.horizontalLayout_strategy_inputs.addLayout(self.ui_add_strategy.verticalLayout_strategy_inputs_lineEdit)
        self.ui_add_strategy.scrollAreaWidgetContents_4.setLayout(self.ui_add_strategy.horizontalLayout_strategy_inputs)

        self.ui_add_strategy.horizontalLayout_news_reactor_inputs = QtWidgets.QHBoxLayout()
        self.ui_add_strategy.verticalLayout_news_reactor_inputs_labels = QtWidgets.QVBoxLayout()
        self.ui_add_strategy.verticalLayout_news_reactor_inputs_lineEdit = QtWidgets.QVBoxLayout()
        self.ui_add_strategy.horizontalLayout_news_reactor_inputs.addLayout(self.ui_add_strategy.verticalLayout_news_reactor_inputs_labels)
        self.ui_add_strategy.horizontalLayout_news_reactor_inputs.addLayout(self.ui_add_strategy.verticalLayout_news_reactor_inputs_lineEdit)
        self.ui_add_strategy.scrollAreaWidgetContents_6.setLayout(self.ui_add_strategy.horizontalLayout_news_reactor_inputs)

        
        """
        Dictionary to hold state of selected systems.
        Since, in adding strategy, in the first slide all three systems (trading system, risk management system and news reactor system)
        must be selected, here we check if all systems all selected then the app enables next button
        """
        required_option={'strategy':False, 'risk_management':False, 'news_reactor':False}
        def strategy_clicked():
            """
            This function is called when an item from strategies list is clicked
            """
            self.ui_add_strategy.textEdit.clear()
            self.ui_add_strategy.textEdit.textCursor().insertHtml(self.strategies_name_description_dict[self.ui_add_strategy.auto_trading_add_strategy_strategy_list.currentItem().text()])
            required_option['strategy']=True
            if required_option['risk_management']==True and required_option['news_reactor']==True:
                self.ui_add_strategy.auto_trading_add_strategy_next_1_button.setEnabled(True)
        def risk_management_clicked():
            """
            This function is called when an item from risk management list is clicked
            """
            self.ui_add_strategy.textEdit_2.clear()
            self.ui_add_strategy.textEdit_2.textCursor().insertHtml(self.risk_managements_name_description_dict[self.ui_add_strategy.auto_trading_add_strategy_risk_management_list.currentItem().text()])
            required_option['risk_management']=True
            if required_option['strategy']==True and required_option['news_reactor']==True:
                self.ui_add_strategy.auto_trading_add_strategy_next_1_button.setEnabled(True)
        def news_reactor_clicked():
            """
            This function is called when an item from news reactor list is clicked
            """
            self.ui_add_strategy.textEdit_3.clear()
            self.ui_add_strategy.textEdit_3.textCursor().insertHtml(self.news_reactors_name_description_dict[self.ui_add_strategy.listWidget_3.currentItem().text()])
            required_option['news_reactor']=True
            if required_option['strategy']==True and required_option['risk_management']==True:
                self.ui_add_strategy.auto_trading_add_strategy_next_1_button.setEnabled(True)


        """
        This section is for creating content (setting) for each system.
        """
        def create_risk_management_inputs():
            """
            This function creates selected risk management system content.
            It removes the content first and gets the data of selected system from its related class attribute and 
            iterates over the data to create content
            """

            self.ui_add_strategy.risk_management_inputs_labels_obj_dict={}
            self.ui_add_strategy.risk_management_inputs_inputs_obj_dict={}
            for i in reversed(range(self.ui_add_strategy.verticalLayout_risk_management_inputs_labels.count())): 
                self.ui_add_strategy.verticalLayout_risk_management_inputs_labels.itemAt(i).widget().setParent(None)
            for i in reversed(range(self.ui_add_strategy.verticalLayout_risk_management_inputs_lineEdit.count())): 
                self.ui_add_strategy.verticalLayout_risk_management_inputs_lineEdit.itemAt(i).widget().setParent(None)
                
            for key, value in self.risk_managements_inputs_dict[self.ui_add_strategy.auto_trading_add_strategy_risk_management_list.currentItem().text()].items():
                self.ui_add_strategy.risk_management_inputs_labels_obj_dict[value[0]] = QtWidgets.QLabel()
                self.ui_add_strategy.risk_management_inputs_labels_obj_dict[value[0]].setText(key)
                self.ui_add_strategy.risk_management_inputs_inputs_obj_dict[value[0]] = QtWidgets.QLineEdit()
                self.ui_add_strategy.risk_management_inputs_inputs_obj_dict[value[0]].setText(str(value[1]))
                self.ui_add_strategy.verticalLayout_risk_management_inputs_labels.addWidget(self.ui_add_strategy.risk_management_inputs_labels_obj_dict[value[0]])
                self.ui_add_strategy.verticalLayout_risk_management_inputs_lineEdit.addWidget(self.ui_add_strategy.risk_management_inputs_inputs_obj_dict[value[0]])


        def create_trading_strategy_inputs():
            """
            This function creates selected trading strategy system content.
            It removes the content first and gets the data of selected system from its related class attribute and 
            iterates over the data to create content
            """
            self.ui_add_strategy.strategy_inputs_labels_obj_dict={}
            self.ui_add_strategy.strategy_inputs_inputs_obj_dict={}
            for i in reversed(range(self.ui_add_strategy.verticalLayout_strategy_inputs_labels.count())): 
                self.ui_add_strategy.verticalLayout_strategy_inputs_labels.itemAt(i).widget().setParent(None)
            for i in reversed(range(self.ui_add_strategy.verticalLayout_strategy_inputs_lineEdit.count())): 
                self.ui_add_strategy.verticalLayout_strategy_inputs_lineEdit.itemAt(i).widget().setParent(None)
            
            for key, value in self.strategies_inputs_dict[self.ui_add_strategy.auto_trading_add_strategy_strategy_list.currentItem().text()].items():
                self.ui_add_strategy.strategy_inputs_labels_obj_dict[value[0]] = QtWidgets.QLabel()
                self.ui_add_strategy.strategy_inputs_labels_obj_dict[value[0]].setText(key)
                self.ui_add_strategy.strategy_inputs_inputs_obj_dict[value[0]] = QtWidgets.QLineEdit()
                self.ui_add_strategy.strategy_inputs_inputs_obj_dict[value[0]].setText(str(value[1]))
                self.ui_add_strategy.verticalLayout_strategy_inputs_labels.addWidget(self.ui_add_strategy.strategy_inputs_labels_obj_dict[value[0]])
                self.ui_add_strategy.verticalLayout_strategy_inputs_lineEdit.addWidget(self.ui_add_strategy.strategy_inputs_inputs_obj_dict[value[0]])

        def create_news_reactor_inputs():
            """
            This function creates selected news reactor system content.
            It removes the content first and gets the data of selected system from its related class attribute and 
            iterates over the data to create content
            """
            
            self.ui_add_strategy.news_reactor_inputs_labels_obj_dict={}
            self.ui_add_strategy.news_reactor_inputs_inputs_obj_dict={}
            for i in reversed(range(self.ui_add_strategy.verticalLayout_news_reactor_inputs_labels.count())): 
                self.ui_add_strategy.verticalLayout_news_reactor_inputs_labels.itemAt(i).widget().setParent(None)
            for i in reversed(range(self.ui_add_strategy.verticalLayout_news_reactor_inputs_lineEdit.count())): 
                self.ui_add_strategy.verticalLayout_news_reactor_inputs_lineEdit.itemAt(i).widget().setParent(None)
            
            for key, value in self.news_reactors_inputs_dict[self.ui_add_strategy.listWidget_3.currentItem().text()].items():
                if type(value[1])==bool:
                    self.ui_add_strategy.news_reactor_inputs_labels_obj_dict[value[0]] = QtWidgets.QLabel()
                    self.ui_add_strategy.news_reactor_inputs_labels_obj_dict[value[0]].setText(key)
                    self.ui_add_strategy.news_reactor_inputs_inputs_obj_dict[value[0]] = QtWidgets.QCheckBox()
                    if value[1]==True:
                        self.ui_add_strategy.news_reactor_inputs_inputs_obj_dict[value[0]].setChecked(True)
                    self.ui_add_strategy.verticalLayout_news_reactor_inputs_labels.addWidget(self.ui_add_strategy.news_reactor_inputs_labels_obj_dict[value[0]])
                    self.ui_add_strategy.verticalLayout_news_reactor_inputs_lineEdit.addWidget(self.ui_add_strategy.news_reactor_inputs_inputs_obj_dict[value[0]])
                else:
                    self.ui_add_strategy.news_reactor_inputs_labels_obj_dict[value[0]] = QtWidgets.QLabel()
                    self.ui_add_strategy.news_reactor_inputs_labels_obj_dict[value[0]].setText(key)
                    self.ui_add_strategy.news_reactor_inputs_inputs_obj_dict[value[0]] = QtWidgets.QLineEdit()
                    self.ui_add_strategy.news_reactor_inputs_inputs_obj_dict[value[0]].setText(str(value[1]))
                    self.ui_add_strategy.verticalLayout_news_reactor_inputs_labels.addWidget(self.ui_add_strategy.news_reactor_inputs_labels_obj_dict[value[0]])
                    self.ui_add_strategy.verticalLayout_news_reactor_inputs_lineEdit.addWidget(self.ui_add_strategy.news_reactor_inputs_inputs_obj_dict[value[0]])
        

        def go_second_page():
            """
            It shows the second page and sets the name of each system container label. 
            it is called when next button is clicked
            """

            self.ui_add_strategy.stackedWidget.setCurrentIndex(1)
            self.ui_add_strategy.label_5.setText(self.ui_add_strategy.auto_trading_add_strategy_strategy_list.currentItem().text())
            self.ui_add_strategy.label_11.setText(self.ui_add_strategy.auto_trading_add_strategy_risk_management_list.currentItem().text())
            self.ui_add_strategy.label_14.setText(self.ui_add_strategy.listWidget_3.currentItem().text())
            create_risk_management_inputs()
            create_trading_strategy_inputs()
            if self.ui_add_strategy.listWidget_3.currentItem().text()!='None':
                create_news_reactor_inputs()

        def go_first_page():
            """
            It shows the first page and sets. 
            it is called when back button is clicked
            """
            self.ui_add_strategy.stackedWidget.setCurrentIndex(0)

        def add_strategy_clicked():
            """
            This function adds strategy. It is called when add button is clicked
            """

            #Setting initial values for input validation 

            check_strategy_name=False
            check_strategy_name_unique=False
            check_symbol=True
            check_timeframe=True
            check_risk_management_inputs=True
            check_news_reactor_inputs=True
            check_strategy_inputs=True

            strategy_inputs_dict_args={} #Dictionary for holding trading strategy system inputs to pass to add_strategy method of strategy controller
            risk_management_inputs_dict_args={} #Dictionary for holding risk management system inputs to pass to add_strategy method of strategy controller
            news_reactor_inputs_dict_args={} #Dictionary for holding news reactor system inputs to pass to add_strategy method of strategy controller

            """
            This section is for validation of inputs.
            But currently it just checks if all inputs are filled, not any kind of validation to check if the input are correct 
            """
            if self.ui_add_strategy.lineEdit.text()!='': #Checking if strategy name filled is not empty
                check_strategy_name=True
            else:
                QtWidgets.QMessageBox.about(self.dialog_add_strategy, 'Result message', 'The strategy name is not given')

            if self.ui_add_strategy.lineEdit.text() not in self.strategy_controller.strategy_setting_dict: #Checking if strategy name is unique 
                check_strategy_name_unique=True
            else:
                QtWidgets.QMessageBox.about(self.dialog_add_strategy, 'Result message', 'The strategy name must be unique')
            
            for key, value in self.ui_add_strategy.risk_management_inputs_inputs_obj_dict.items(): #Iterating over trading strategy system inputs and converting them to float and inserting them to 
                try:
                    input_temp=float(value.text())
                    risk_management_inputs_dict_args[key]=input_temp
                except Exception as e:
                    check_risk_management_inputs=False
                    print(e)

            for key, value in self.ui_add_strategy.strategy_inputs_inputs_obj_dict.items():  #Iterating over risk management system inputs and converting them to float and inserting them to 
                try:
                    input_temp=float(value.text())
                    strategy_inputs_dict_args[key]=input_temp
                except Exception as e:
                    check_strategy_inputs=False
                    print(e)

            if self.ui_add_strategy.listWidget_3.currentItem().text()!='None':
                for key, value in self.ui_add_strategy.news_reactor_inputs_inputs_obj_dict.items():  #Iterating over news reactor system inputs and converting them to float and inserting them to 
                    try:
                        if type(value).__name__=='QCheckBox':
                            input_temp=True if value.isChecked() == True else False
                            news_reactor_inputs_dict_args[key]=input_temp
                        else:
                            input_temp=float(value.text())
                            news_reactor_inputs_dict_args[key]=input_temp
                    except Exception as e:
                        check_news_reactor_inputs=False
                        print(e)


                """
                Checking all validation related variables, and if the condition is ture, then inserting inputs to a dictionary to pass to 
                add_strategy method of strategy_controller to add a strategy.
                """            
            if check_strategy_name_unique==True and check_risk_management_inputs==True and check_strategy_inputs==True and check_news_reactor_inputs==True and check_strategy_name==True and check_symbol==True and check_timeframe==True:
                strategy_arguments_dict={
                                        'strategy_name':self.ui_add_strategy.lineEdit.text(),
                                        'symbol':self.ui_add_strategy.comboBox_3.currentText(),
                                        'timeframe':self.ui_add_strategy.comboBox.currentText(),
                                        'trading_strategy_system':self.ui_add_strategy.auto_trading_add_strategy_strategy_list.currentItem().text(),
                                        'trading_strategy_inputs':strategy_inputs_dict_args,
                                        'risk_management_system':self.ui_add_strategy.auto_trading_add_strategy_risk_management_list.currentItem().text(),
                                        'risk_management_system_inputs':risk_management_inputs_dict_args,
                                        'news_reactor_system':self.ui_add_strategy.listWidget_3.currentItem().text(),
                                        'news_reactor_inputs':news_reactor_inputs_dict_args
                                        }

                self.strategy_controller.add_strategy(**strategy_arguments_dict)
                QtWidgets.QMessageBox.about(self.dialog_add_strategy, 'Result message', 'Strategy is successfully added')
                self.dialog_add_strategy.close()
                self.open_auto_trading_page()
            else:
                QtWidgets.QMessageBox.about(self.dialog_add_strategy, 'Result message', 'All fields must be filled')

        

        def cancel_button_clicked():
            """
            This function is called when cancel button is clicked. Basically it destroys the window.
            """
            self.dialog_add_strategy.destroy()



        """
        Setting buttons' trigger function, and default values of items
        """
        for key, value in self.strategies_name_description_dict.items(): #Gets strategy name and description of each built in strategy and insert them their related fields to show them in the first page
            self.ui_add_strategy.auto_trading_add_strategy_strategy_list.addItem(key)

        for key, value in self.risk_managements_name_description_dict.items(): #Gets risk management name and description of each built in risk management and insert them their related fields to show them in the first page
            self.ui_add_strategy.auto_trading_add_strategy_risk_management_list.addItem(key)

        for key, value in self.news_reactors_name_description_dict.items(): #Gets news reactor name and description of each built in news reactor and insert them their related fields to show them in the first page
            self.ui_add_strategy.listWidget_3.addItem(key)

        self.ui_add_strategy.comboBox_3.addItems(self.auto_trading_symbol_list)
        self.ui_add_strategy.comboBox.addItems(self.auto_trading_timeframe_list)
        self.ui_add_strategy.auto_trading_add_strategy_strategy_list.currentItemChanged.connect(strategy_clicked)
        self.ui_add_strategy.auto_trading_add_strategy_risk_management_list.currentItemChanged.connect(risk_management_clicked)
        self.ui_add_strategy.listWidget_3.currentItemChanged.connect(news_reactor_clicked)
        self.ui_add_strategy.auto_trading_add_strategy_next_1_button.clicked.connect(go_second_page)
        self.ui_add_strategy.pushButton.clicked.connect(add_strategy_clicked)
        self.ui_add_strategy.auto_trading_add_strategy_cancel_1_button.clicked.connect(cancel_button_clicked)
        self.ui_add_strategy.pushButton_2.clicked.connect(cancel_button_clicked)
        self.ui_add_strategy.pushButton_3.clicked.connect(go_first_page)
        self.dialog_add_strategy.show()



    def open_price_chart(self):
        """
        This function open price chart window.
        """

        try: #Checking if self.dialog_price_chart exits then stop its thread
            if self.dialog_price_chart==False:
                self.ui_price_chart.update_price_data_chart_thread.stop()
                self.ui_price_chart.update_price_data_chart_thread.wait()
        except:
            pass


        # Window initialization
        self.dialog_price_chart = QtWidgets.QDialog()
        self.ui_price_chart = Ui_chart_page()
        self.ui_price_chart.setupUi(self.dialog_price_chart)
        self.dialog_price_chart.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
        self.dialog_price_chart.setWindowFlag(Qt.WindowMaximizeButtonHint, True)

        class TimeAxisItem(pg.AxisItem):
            """
            This class inherits from pg.AxisItem. Created to manipulate x axis.
            As pyqtgraph does not support datetime x axis, we need to pass time as timestamp to 
            plotting method and set a new class to convert timestamp to datetime
            """

            def tickStrings(self, values, scale, spacing): 
                values_list=[]
                for i, j in enumerate(values):
                    try:
                        values_list.append(datetime.datetime.fromtimestamp(j))
                    except:
                        values_list.append(str(j))
                return values_list    

        """
        Initializing the plot
        """
        date_axis = TimeAxisItem(orientation='bottom') #Creating an instance of TimeAxisItem to pass it to PlotWidget method when creating plot widget
        self.ui_price_chart.graphWidget = pg.PlotWidget(axisItems = {'bottom': date_axis}) 
        self.ui_price_chart.graphWidget.setBackground('w')
        self.ui_price_chart.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.ui_price_chart.widget)
        self.ui_price_chart.horizontalLayout_5.setObjectName("horizontalLayout_3")
        self.ui_price_chart.horizontalLayout_5.addWidget(self.ui_price_chart.graphWidget)
        self.ui_price_chart.pen=pg.mkPen(color=(255, 0, 0))
        self.app.setAttribute(QtCore.Qt.AA_Use96Dpi) #It resovels problems with displaying plot axis
        self.ui_price_chart.graphWidget.showGrid(x=True, y=True)
        self.ui_price_chart.price_Data_plot=self.ui_price_chart.graphWidget.plot(pen=self.ui_price_chart.pen)
        self.ui_price_chart.price_chart_annotation=[] #List to holld annotations items


        def closeEvent(event):
            """
            CloseEvent function to be replaced with this window's exit event 
            """            
            try:
                self.ui_price_chart.update_price_data_chart_thread.stop()
                self.ui_price_chart.update_price_data_chart_thread.wait()
                self.controller.all_info_thread.disactivate_get_candle()

                event.accept()
            except:
                event.accept()
    

        def update_price_chart_func(data):
            try:
                """
                This function updates plot and annotations, it is called when update_price_data_chart_thread_class thread emits
                new data
                """
                def create_annotations(annotation_data):
                    """
                    This function updates annotation (positions' info on chart)
                    It removes all annotations and creates annotations using new annotation_data
                    """
                    try:
                        try: #Removing all annotations
                            for i in self.ui_price_chart.price_chart_annotation:
                                self.ui_price_chart.graphWidget.removeItem(i)
                        except:
                            pass
                        self.ui_price_chart.price_chart_annotation = []


                        #Creating annotations for open positions
                        for t in annotation_data[0]:
                            try:
                                item = pg.TextItem(t[0], anchor=(1,1), border=t[3], color=t[3])
                                item.setPos(t[1], float(t[2]))
                                self.ui_price_chart.graphWidget.addItem(item)
                                self.ui_price_chart.price_chart_annotation.append(item)
                            except Exception as e:
                                print(e, 'create_annotations')
                        #Creating annotations for closed positions
                        for t in annotation_data[1]:
                            try:
                                item = pg.TextItem(t[0], anchor=(0,1), border=t[3], color=t[3])
                                item.setPos(t[1], float(t[2]))
                                self.ui_price_chart.graphWidget.addItem(item)
                                self.ui_price_chart.price_chart_annotation.append(item)
                            except Exception as e:
                                print(e, 'create_annotations')
                                
                    except Exception as e:
                        print(e, 'update_price_chart_func')

                self.ui_price_chart.price_Data_plot.setData(data[0], data[1]) #setting plot's new values
                create_annotations(data[2])
            except:
                pass

        
        class update_price_data_chart_thread_class(QThread):
            """
            This class inherits from QThread, created to handle updating price chart.
            it gets news price list and positions data from db and emit.
            (It prevents the app from getting frozen when waiting for result)
            """            
            listReady=pyqtSignal(list)
            def __init__(self, db, controller, symbol, timeframe):
                QThread.__init__(self)
                self.db=db
                self.controller=controller
                self.symbol=symbol
                self.timeframe=timeframe
                self.stop_signal=False
                self.colors={}

            def change_symbol_timeframe(self, symbol, timeframe):
                """
                This method is called when update button is pressed is updates symbol and timeframe
                values 
                """
                self.symbol=symbol
                self.timeframe=timeframe
                self.controller.change_symbol_timeframe_chart(symbol, timeframe)

            def stop(self):
                self.stop_signal=True
                self.terminate()

            def create_random_color(self, strategies):
                """
                This function create new random color for each strategy 
                """
                for i in strategies:
                    r=random.randint(0, 255)
                    g=random.randint(0, 255)
                    b=random.randint(0, 255)
                    rgb=[r, g, b]
                    random.shuffle(rgb)
                    if i not in self.colors:
                        self.colors[i]=tuple(rgb)
                return self.colors


            def run(self):
                try:
                    while True:
                        if self.stop_signal==True:
                            break
                        else:
                            try:
                                data=self.db.query_price_data(self.symbol, self.timeframe) #Getting price list data from db as dataframe
                                try:
                                    data['date'] =  pd.to_datetime(data['date'], format='%Y-%m-%d %H:%M:%S') #converting date column from string to datetime
                                except:
                                    data['date'] =  pd.to_datetime(data['date'], format='%m/%d/%Y %H:%M') #converting date column from string to datetime
                                
                                data['date']=[pd.Timestamp(x).to_pydatetime().timestamp() for x in data['date']] #converting date to timestampe
                                positions_data=self.db.query_positions_data_chart_annotation(self.controller.account_name, self.symbol) #Getting positions information
                                
                                #This part is for exctracting strategy names in positions to create a different color for its annotations on chart
                                strategies_list_open_position=list(positions_data[0].groupby(['positionMaker']).count().index[:].values) #Grouping open position by strategy name
                                strategies_list_closed_position=list(positions_data[1].groupby(['positionMaker']).count().index[:].values) #Grouping closed position by strategy name
                                strategies_list=[]
                                for i in strategies_list_open_position:
                                    if i not in strategies_list:
                                        strategies_list.append(i)
                                for i in strategies_list_closed_position:
                                    if i not in strategies_list:
                                        strategies_list.append(i)
                                self.colors=self.create_random_color(strategies_list)


                                #Converting positions from dataframe to list
                                positions_data[0]=positions_data[0].values.tolist() 
                                positions_data[1]=positions_data[1].values.tolist()

                                #Converiting open positions time column to timestamp
                                for i, j in enumerate(positions_data[0]):
                                    positions_data[0][i]=list(positions_data[0][i])
                                    positions_data[0][i][1]=datetime.datetime.strptime(self.controller.timestamp_to_datetime(positions_data[0][i][1]), '%Y-%m-%d %H:%M').timestamp()

                                #Converiting closed and open positions time column to timestamp
                                #This part exctract open time and rate from closed positions to append them to positions_data[0]
                                #which hold open positions' annotation info
                                old_open_position_data=[]
                                for i, j in enumerate(positions_data[1]):
                                    positions_data[1][i]=list(positions_data[1][i])
                                    positions_data[1][i][1]=datetime.datetime.strptime(self.controller.timestamp_to_datetime(positions_data[1][i][1]), '%Y-%m-%d %H:%M').timestamp()
                                    positions_data[1][i][2]=datetime.datetime.strptime(self.controller.timestamp_to_datetime(positions_data[1][i][2]), '%Y-%m-%d %H:%M').timestamp()
                                    old_open_position_data.append([positions_data[1][i][0], positions_data[1][i][2], positions_data[1][i][4], positions_data[1][i][5], positions_data[1][i][7]])
                                
                                open_position_data=old_open_position_data+positions_data[0]
                                positions_data[0]=open_position_data



                                annotation_open_position_data_list=[] #Open position annotation data to pass 
                                annotation_closed_position_data_list=[] #Closed position annotation data to pass 
                                for t in positions_data[0]:
                                    try:
                                        color=self.colors[t[4]]
                                        postion_type='Buy' if t[3]==1 else 'Sell'
                                        text="\n".join(['Open', str(t[0]), str(t[2]), postion_type, t[4]])
                                        annotation_open_position_data_list.append([text, t[1], float(t[2]), color])
                                    except Exception as e:
                                        print(e, 'create_annotations')
                                for t in positions_data[1]:
                                    try:
                                        color=self.colors[t[7]]
                                        postion_type='Buy' if t[5]==1 else 'Sell'
                                        text="\n".join(['Closed', str(t[0]), str(t[3]), postion_type, str(t[6]), t[7]])
                                        annotation_closed_position_data_list.append([text, t[1], float(t[3]), color])
                                    except Exception as e:
                                        print(e, 'create_annotations')

                                annotation_data=[annotation_open_position_data_list, annotation_closed_position_data_list]
                                price_list=data.bidclose.values
                                date_list=data.date.values
                                self.listReady.emit([date_list, price_list, annotation_data])
                                time.sleep(10)
                            except Exception as e:
                                print(e)
                                time.sleep(10)
                except Exception as e:
                    print(e)
                    time.sleep(10)

        """
        Setting buttons' trigger function and creating and starting thread to start updating chart
        """
        self.dialog_price_chart.closeEvent=closeEvent
        self.ui_price_chart.comboBox.addItems(self.controller.available_symbols_list)
        self.ui_price_chart.comboBox_2.addItems(self.controller.available_timeframe_list)
        self.ui_price_chart.update_price_data_chart_thread=update_price_data_chart_thread_class(self.db, self.controller, self.ui_price_chart.comboBox.currentText(), self.ui_price_chart.comboBox_2.currentText())
        self.ui_price_chart.pushButton.clicked.connect(lambda: self.ui_price_chart.update_price_data_chart_thread.change_symbol_timeframe(self.ui_price_chart.comboBox.currentText(), self.ui_price_chart.comboBox_2.currentText()))
        self.ui_price_chart.update_price_data_chart_thread.listReady.connect(update_price_chart_func)
        self.ui_price_chart.update_price_data_chart_thread.start()
        self.ui_price_chart.update_price_data_chart_thread.change_symbol_timeframe(self.controller.available_symbols_list[0], self.controller.available_timeframe_list[1])
        self.controller.all_info_thread.activate_get_candle()
        self.dialog_price_chart.show()


    def open_instructions(self):
        """
        Open instruction window
        """
        self.dialog_instructions = QtWidgets.QDialog()
        self.ui_instructions = Ui_help_page()
        self.ui_instructions.setupUi(self.dialog_instructions)
        self.dialog_instructions.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
        self.dialog_instructions.setWindowFlag(Qt.WindowMaximizeButtonHint, True)
        
        self.ui_instructions.textBrowser.setText(self.instruction_text)
        self.dialog_instructions.show()


    def launch(self):
        self.main_window.show()
        sys.exit(self.app.exec_())

    def init_required_files(self):
        """
        Creating required files for the app including db and its tables, strategies_settings.cfg for saving created strategies' settings
        and information, and acount_info.cfg to store account_id, account_name, account_type, and token
        """
        db=Db_Controller()
        if os.path.isdir('./data'):
            pass
        else:
            os.mkdir('./data')
        if os.path.isfile('./data/data.dll')==False:
            db.create_schema()
        if os.path.isfile('./data/strategies_settings.cfg')==False:
            strategy_setting_dict={}
            with open('./data/strategies_settings.cfg', 'wb') as f: 
                pickle.dump(strategy_setting_dict, f)
        if os.path.isfile('./data/account_info.cfg')==False:
            account_info_dict={'token':'', 'account_id':None, 'account_name':None, 'account_currency':None, 'account_type':None}
            with open('./data/account_info.cfg', 'wb') as f: 
                pickle.dump(account_info_dict, f)

# Launch
if __name__=="__main__":
    multiprocessing.freeze_support() #This causes the gui not to freeze when using multiprocessing
    a = GUI()
    a.launch()