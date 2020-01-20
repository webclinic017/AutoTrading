from fxcmpy import *
from db_controller import Db_Controller
import threading
import time
import pickle
import datetime
import pandas as pd
from fxcmpy import fxcmpy_tick_data_reader as tdr


class Fxcm():
    """
    FXCM controller.
    This class contains methods acting as wrapers for FXCM API class with additional functionality.
    All the methods are direct implementation of FXCM API
    Full documentation can be retrived from: https://fxcm.github.io/rest-api-docs/#section/Overview
    
    """
    def __init__(self):
        with open('./data/account_info.cfg', 'rb') as f: # Reading user's fxcm information from a stored file
            account_info_dict = pickle.load(f)
        self.token = account_info_dict['token']   # FXCM token or API key " a46718dbcf04edf1b8135816d96d38a7703f2d65 " use this in gui
        self.account_type=account_info_dict['account_type']  #Can be demo or real
        self.connection = None
        self.connection_status = 'Disconnected'
        self.db = Db_Controller()
        self.account_id=account_info_dict['account_id']
        self.account_name=account_info_dict['account_name']
        self.fxcm_account_currency_list=['AUD', 'USD', 'EUR', 'GBP']
        self.account_currency=account_info_dict['account_currency']
        self.available_symbols_list=['AUDUSD', 'EURUSD', 'USDJPY', 'GBPUSD', 'USDCHF', 'NZDUSD']
        self.available_timeframe_list=['m1', 'm5', 'm15', 'm30', 'H1', 'H2', 'H3', 'H4', 'H6', 'H8', 'D1', 'W1', 'M1']

    
    def timestamp_to_datetime(self, given_time):
        """
        This function converts timestamp to datetime
        """
        given_time=str(given_time)
        if len(given_time)==13:
            given_time=str(0)+given_time
            new_time=datetime.datetime.strptime(given_time, '%m%d%Y%H%M%S')
            new_time=new_time.strftime("%Y-%m-%d %H:%M")
            return new_time
        elif len(given_time)==14:
            new_time=datetime.datetime.strptime(given_time, '%m%d%Y%H%M%S')
            new_time=new_time.strftime("%Y-%m-%d %H:%M")
            return new_time
        elif len(given_time)==16:
            given_time=str(0)+given_time
            new_time=datetime.datetime.strptime(given_time, '%m%d%Y%H%M%S%f')
            new_time=new_time.strftime("%Y-%m-%d %H:%M")
            return new_time
        elif len(given_time)==17:
            new_time=datetime.datetime.strptime(given_time, '%m%d%Y%H%M%S%f')
            new_time=new_time.strftime("%Y-%m-%d %H:%M")
            return new_time    
    
    
    
    
    def connect(self, startegy_name):
        """
        This function makes an instance of fxcmpy.fxcmpy to connect to server, and is used by auto trading system for creating connection
        Once the fxcmpy instance is created, two new threads will be created as fxcmpy does that automatically.
        the name of its thread can be gotten from 'socket_thread._name' on the connection object. when closing the connection
        this name is used to stop its thread
        """
        if self.connection==None or self.connection.is_connected()!=True:
            try:
                self.disconnect()
                self.connection = fxcmpy(access_token=self.token, log_level='error', server=self.account_type)
                if self.connection.is_connected():
                    self.connection_status='Connected'
                    return True
                else:
                    self.disconnect()
                    self.connection_status='Disconnected'
                    return False
            except:
                self.connection_status='Disconnected'
                self.disconnect()
                return False
        else:
            return True



    def connect_gui(self):
        """
        This function makes an instance of fxcmpy.fxcmpy to connect to server, and is used by gui for creating connection and starting required threads
        Once the fxcmpy instance is created, two new threads will be created as fxcmpy does that automatically.
        the name of its thread can be gotten from 'socket_thread._name' on the connection object. when closing the connection
        this name is used to stop its thread
        """
            
        try:
            if self.connection==None or self.connection.is_connected()!=True:
                self.disconnect_gui()
                self.connection = fxcmpy(access_token=self.token, log_level='error', server=self.account_type)
                connection_status = self.connection.is_connected()
                if connection_status!=True:
                    self.connection_status='Disconnected'
                    self.disconnect_gui()
                    return 'Problem in connection'
                else:
                    self.connection_status='Connected'
                    account_info=self.connection.get_accounts() #Getting account info data 
                    # Inserting account info data if not exits into db
                    if len(self.db.query_table('Fxcm_Info', ('accountId',), fields=('accountId',), values=(self.account_id,)))==0:
                        self.db.insert_into_account_info_table(account_info)
                    return True
            else:
                'Connection is already established'
        except Exception as e:
            self.disconnect_gui()
            return str(e)


    def start_connection_thread_gui(self):
        """
        This function is called from login page when connect button is clicked.
        It calls connect_gui ethod to establish connection and then calls gui_threads
        to create and start threads for updating fxcm data
        """
        if self.connection_status!='Connected':
            result=self.connect_gui()
            if result==True:
                self.gui_threads()
                return True
            else:
                return result
        else:
            return 'Connection is already established'


    def gui_threads(self):
        """
        This method initializes threads for updating fxcm data 
        """

        class update_all_info_thread(threading.Thread):
            """
            This class inherits from threading.Thread class. Created to handle updating account data, open positions, closed positions
            and price data for chart
            """

            def __init__(self, fxcm_instance, symbol, timeframe):
                threading.Thread.__init__(self)
                self.event=threading.Event()
                self.fxcm_instance=fxcm_instance
                self.symbol=symbol
                self.timeframe=timeframe
                self.name='Update_info_thread'
                self.change_symbol_timeframe_signal=False
                self.change_symbol_timeframe(self.symbol, self.timeframe)
                self.get_candle_signal=False

            def change_symbol_timeframe(self, symbol, timeframe):
                """
                This method changes symbol and timeframe for getting price data
                """
                self.fxcm_instance.db.create_price_data_table(symbol, timeframe) #Creating price data table for new symbol and timeframe
                self.symbol=symbol
                self.timeframe=timeframe
                self.change_symbol_timeframe_signal=True
                

            def activate_get_candle(self):
                self.get_candle_signal=True

            def disactivate_get_candle(self):
                self.get_candle_signal=False

            def stop(self):
                self.event.set()
                
            def run(self):
                self.first_time_candle=datetime.datetime.now()
                while True:
                    try:
                        if self.event.is_set()==True:
                            break
                        else:
                            connection_status=self.fxcm_instance.connection.is_connected()
                            if connection_status==True:
                                self.fxcm_instance.connection_status='Connected'
                                self.fxcm_instance.get_acc_info()
                                self.fxcm_instance.get_open_positions()
                                self.fxcm_instance.get_closed_positions()
                                if self.get_candle_signal==True:
                                    if self.change_symbol_timeframe_signal==True:
                                        candle_result=self.fxcm_instance.get_price_data(self.symbol, self.timeframe)
                                        if candle_result==True:
                                            self.change_symbol_timeframe_signal=False
                                        else:
                                            self.fxcm_instance.connection_status='Disconnected'
                                            self.fxcm_instance.disconnect_gui()
                                            self.fxcm_instance.connect_gui()
                                            self.event.clear()
                                    else:
                                        if datetim.datetime.now()>=datetime.timedelta(seconds=60)+self.first_time_candle:
                                            candle_result=self.fxcm_instance.get_price_data(self.symbol, self.timeframe, 100)
                                            if candle_result==False:
                                                self.fxcm_instance.connection_status='Disconnected'
                                                self.fxcm_instance.disconnect_gui()
                                                self.fxcm_instance.connect_gui()
                                                self.event.clear()
                                time.sleep(5)
                            else:
                                self.fxcm_instance.connection_status='Disconnected'
                                self.fxcm_instance.disconnect_gui()
                                self.fxcm_instance.connect_gui()
                                self.event.clear()
                                time.sleep(5)
                    except:
                        self.fxcm_instance.connection_status='Disconnected'
                        self.fxcm_instance.disconnect_gui()
                        self.fxcm_instance.connect_gui()
                        self.event.clear()
                        time.sleep(5)
                        

        #Creating an instance of update_all_info_thread and starting it to start updating required data
        self.all_info_thread=update_all_info_thread(self, self.available_symbols_list[0], self.available_timeframe_list[0])                
        self.all_info_thread.start()


    def get_tick_data(self, symbol, start, end):
        self.tick_obj=tdr(symbol, start, end, verbosity=True)
        return self.tick_obj.get_data()


    def disconnect(self):
        """
        This method disconnect autotrading fxcm connection objects 
        """
        try:
            self.connection.socket._heartbeat_thread._halt.set()
            self.connection = None
            self.connection_status = 'Disconnected'
        except:
            self.connection = None
            self.connection_status = 'Disconnected'
        
    def disconnect_gui(self):
        """
        This method disconnect gui fxcm connection objects and stop update related threads
        """
        try:
            try:
                self.all_info_thread.stop() #Stoping the thread of updating information 
            except:
                pass

            try:
                self.connection.socket._heartbeat_thread._halt.set()
                self.connection = None
                self.connection_status = 'Disconnected'
            except:
                self.connection = None
                self.connection_status = 'Disconnected'
        except:
            pass

    def change_symbol_timeframe_chart(self, symbol, timeframe):
        """
        This method is called from gui to change symbol and timeframe used in update_all_info_thread to get new data
        """
        try:
            self.all_info_thread.change_symbol_timeframe(symbol, timeframe)
        except:
            pass
        

    def get_price_data(self, trading_symbol, timeframe, quantity=10000):
        """
        This method gets price data for given symbol and timeframe from fxcm and sends it to be stored in db
        """
        try:
            symbol=list(trading_symbol)
            symbol.insert(3, '/')
            symbol=''.join(symbol)
            data=pd.DataFrame()
            data=self.connection.get_candles(symbol, period=timeframe, number=quantity)
            if data.empty!=True:
                self.db.insert_into_price_data_table(data, trading_symbol, timeframe)
                return True
            else:
                return False
        except:
            return False
        

    
    def get_acc_info(self):
        """
        This method gets account info from fxcm and sends it to be stored in db
        """
        acc_info=self.connection.get_accounts()
        self.db.update_account_info_table(self.account_id, acc_info)

    def update_token(self, new_token, account_currency, account_type):
        """
        This method updates token and account currency.
        It does not only changes the token value, it validates it by connecting to server using given token and account type
        and if the connection is established, the it get account info from fxcm to store accountId and accountName and
        finally it disconnects and store update token, accountId and accountName, account type and account currency in a
        file named account_info.cfg.
        """
        try:
            self.token = new_token
            self.account_type=account_type
            self.account_currency=account_currency
            self.connection = fxcmpy(access_token=self.token, log_level='error', server=self.account_type)
            account_info=self.connection.get_accounts()
            self.disconnect()

            self.account_id=account_info.accountId.iloc[0]
            self.account_name=account_info.accountName.iloc[0]
            if len(self.db.query_table('Fxcm_Info', ('accountId',), fields=('accountId',), values=(self.account_id,)))==0:
                self.db.insert_into_account_info_table(account_info)
            with open('./data/account_info.cfg', 'rb') as f: 
                account_info_dict = pickle.load(f)
            account_info_dict['token']=self.token
            account_info_dict['account_type']=self.account_type
            account_info_dict['account_id']=self.account_id
            account_info_dict['account_name']=self.account_name
            account_info_dict['account_currency']=self.account_currency
            with open('./data/account_info.cfg', 'wb') as f: 
                pickle.dump(account_info_dict, f)
            self.connection=None
            return True
        except Exception as e:
            try:
                self.disconnect()
            except:
                pass
            self.connection=None
            self.account_id=None
            self.account_name=None
            self.account_type=''
            self.token=''
            self.account_currency=None
            return str(e)

    def get_open_positions(self):
        """
        This method gets open positions from fxcm and sends it to be stored in db
        """
        open_positions=self.connection.get_open_positions()
        self.db.update_open_positions_table(open_positions, self.account_id)

    def get_open_trade_ids(self):
        return self.connection.get_open_trade_ids()
    def get_closed_positions(self):
        """
        This method gets closed positions from fxcm and sends it to be stored in db
        """
        closed_positions=self.connection.get_closed_positions()
        self.db.update_closed_positions_table(closed_positions)

    def open_position(self, **position_parameters):
        try:
            print('open_position...............')
            """
            Function to add a position to FXCM server
            
            Inputs: **position_parameters->dictionary List of different variables to open a position
            Output: Opened position and created db row and tradeId
            """
            position_maker=position_parameters['maker']
            symbol=position_parameters['symbol']
            symbol=list(symbol)
            symbol.insert(3, '/')
            symbol=''.join(symbol)
            del position_parameters['maker']
            position_parameters['symbol']=symbol
            order=self.connection.open_trade(**position_parameters)
            trade_id = int(order.get_tradeId())
            
            while True:
                open_positions=self.connection.get_open_positions()
                data = open_positions.loc[open_positions['tradeId']==str(trade_id)]
                if data.empty==False:
                    break
                time.sleep(10)
            data['positionMaker']=[position_maker,]
            self.db.insert_into_open_positions(data)
            return trade_id
        except:
            return None

    def close_position(self, **position_parameters):
        try:
            print('close_position...............')
            """
            Function to close a position from FXCM server
            
            Inputs: **position_parameters->dictionary List of different variables to close a position
            Output: Closed FXCM position, deleted OpenPosition row and created ClosedPosition row in db
            """
            position_maker=position_parameters['maker']
            del position_parameters['maker']
            self.connection.close_trade(**position_parameters)
            self.db.delete_from_table('OpenPosition', position_parameters['trade_id'])
            closed_positions=self.connection.get_closed_positions()
            closed_position=closed_positions.loc[closed_positions['tradeId']==str(position_parameters['trade_id'])]
            closed_position['positionMaker']=[position_maker,]
            self.db.insert_into_closed_positions(closed_position)
            return True
        except Exception as e:
            print(e)
            return False

            

    def edit_position_stop_limit(self, **position_parameters):
        """
        This method edits an open position
        """
        try:
            self.connection.change_trade_stop_limit(**position_parameters)
        except:
            pass

    def close_all_positions(self):
        """
        This method closess all open positions 
        """

        try:
            data = self.connection.get_open_positions()
            for i, j in enumerate(data.tradeId):
                self.db.delete_from_table('OpenPosition', j)
            self.connection.close_all()
            data = self.connection.get_closed_positions()
            makers_list=[]
            for i in range(len(data.tadeId)):
                makers_list.append('Manual')
            data['positionMaker']=makers_list
            self.db.insert_into_closed_positions(data)
        except:
            pass



    def get_open_positions_ids(self):
        try:
            return self.connection.get_open_trade_ids()
        except:
            return []
    def get_default_acc_id(self):
        try:
            return self.connection.get_default_account()
        except:
            return []



