'''
This file consists of two classes including 'strategy_controller' and 'trading_strategy' for used for autotrading

'''


"""
Importing required libraries
"""
import os, glob, sys, inspect, glob
import importlib
import warnings
import pandas as pd
import numpy as np
import fxcm_controller
import pickle
import multiprocessing
import datetime
import time

"""
Importing required modules from the app project
"""
if __name__.endswith('__main__'):
    import ema_cross, strategy_linear_regression_channel, ml_williamR_cmf_ema, ma_crossing_renko
    from strategy import strategies_module_name_list
else:
    from strategy import ma_crossing_renko, ema_cross, linear_regression_channel, polinomial_linear_regression_channel, ml_williamR_cmf_ema, strategies_module_name_list

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
from db_controller import Db_Controller
from risk_management import risk_management_module_name_list, balance_atr_based_risk_management, equity_atr_based_risk_management, margin_atr_based_risk_management
from news_reactor import news_reactor_module_name_list, check_economic_calendar_entry_atr_based_stop, economic_calendar_trading


"""
Disabling warnings
"""
warnings.filterwarnings("ignore")
pd.options.mode.chained_assignment = None
np.seterr(divide='ignore', invalid='ignore')




'''
strategy_controller is the class which holds all created strategies' instances and provides methods for controlling them.
also new strategies are made through this class.
'''
class strategy_controller:
    def __init__(self):
        self.init_strategies_modules()
        self.strategies_dict={}
        self.strategies_shared_memory_dict={}
        self.init_saved_strategies()

    #Loading saved strategies information and creating their trading_strategy instances.


    def init_strategies_modules(self):
        """
        This method retrieve risk management systems, strategy systems and news reactor systems from their specific folders (strategy, risk_management and rews reactor),
        then it insert their name and description in a specific dictionary, and their required inputs in another dictionary, and their class names in another dictionart.
        These are implemented in order to be able to retrieve them from other parts of the app such as GUI.
        """

        self.risk_management_classes_dict={}
        self.risk_management_inputs_dict={}
        self.risk_management_name_description_dict={}
        for i in risk_management_module_name_list:
            self.risk_management_classes_dict[eval(i).risk_management_name]=i+'.'+i
            self.risk_management_inputs_dict[eval(i).risk_management_name]=eval(i).inputs_name_dict
            self.risk_management_name_description_dict[eval(i).risk_management_name]=eval(i).risk_management_description


        '''
        Collecting all news reactor systems and inserting their information in three dictionaries.
        '''
        self.news_reactor_classes_dict={}
        self.news_reactor_inputs_dict={}
        self.news_reactor_name_description_dict={'None':''}
        for i in news_reactor_module_name_list:
            self.news_reactor_classes_dict[eval(i).news_reactor_name]=i+'.'+i
            self.news_reactor_inputs_dict[eval(i).news_reactor_name]=eval(i).inputs_name_dict
            self.news_reactor_name_description_dict[eval(i).news_reactor_name]=eval(i).news_reactor_description


        '''
        Collecting all trading strategy systems and inserting their information in three dictionaries.
        '''
        self.trading_strategies_classes_dict={}
        self.trading_strategies_inputs_dict={}
        self.trading_strategies_name_description_dict={}
        for i in strategies_module_name_list:
            self.trading_strategies_classes_dict[eval(i).strategy_name]=i+'.'+i
            self.trading_strategies_inputs_dict[eval(i).strategy_name]=eval(i).inputs_name_dict
            self.trading_strategies_name_description_dict[eval(i).strategy_name]=eval(i).strategy_description


    def init_saved_strategies(self, strategy_name=None):
        """
        This method retrieves saved strategies and their data from strategies_settings.cfg file and instantiate a trading_strategy class
        for each using stored data
        """

        with open('./data/strategies_settings.cfg', 'rb') as f: 
            self.strategy_setting_dict = pickle.load(f)
        if strategy_name==None:
            for key, value in self.strategy_setting_dict.items():
                self.add_strategy(**self.strategy_setting_dict[key])
        else:
            self.add_strategy(**self.strategy_setting_dict[strategy_name])
        
    #Creating new strategies. It gets a list of arguments and passes them to trading_strategy class to create an instance of trading_strategy class.
    #Then it checks if the name of the strategy is not in the saved strategies's list or strategy_setting_dict(it hold inputs of strategies), it inserts the inputs in strategies_settings.cfg file.
    def add_strategy(self, strategy_name, trading_strategy_system, trading_strategy_inputs, symbol, timeframe, risk_management_system, risk_management_system_inputs, news_reactor_system, news_reactor_inputs, position_type=None, position_trade_id=None, position_size=None, news_position_type=None, news_position_trade_id=None, news_position_size=None):
        self.manager=multiprocessing.Manager()
        self.strategies_shared_memory_dict[strategy_name]=self.manager.dict()
        self.strategies_shared_memory_dict[strategy_name]['stop_signal']=True
        self.strategies_shared_memory_dict[strategy_name]['strategy_status']='Not started'
        self.strategies_shared_memory_dict[strategy_name]['last_start']='Never'
        self.strategies_shared_memory_dict[strategy_name]['last_stop']='Never'
        self.strategies_shared_memory_dict[strategy_name]['stop_backtesting_signal']=True
        self.strategies_shared_memory_dict[strategy_name]['backtest_progress_counter']=0
        self.strategies_shared_memory_dict[strategy_name]['backtesting_result']={}
        self.strategies_shared_memory_dict[strategy_name]['position_type']=position_type
        self.strategies_shared_memory_dict[strategy_name]['position_trade_id']=position_trade_id
        self.strategies_shared_memory_dict[strategy_name]['position_size']=position_size
        self.strategies_shared_memory_dict[strategy_name]['news_position_type']=news_position_type
        self.strategies_shared_memory_dict[strategy_name]['news_position_trade_id']=news_position_trade_id
        self.strategies_shared_memory_dict[strategy_name]['news_position_size']=news_position_size
        
        self.strategies_dict[strategy_name]=trading_strategy(self.trading_strategies_classes_dict, self.news_reactor_classes_dict, self.risk_management_classes_dict,  self.strategies_shared_memory_dict[strategy_name], strategy_name, trading_strategy_system, trading_strategy_inputs, symbol, timeframe, risk_management_system, risk_management_system_inputs, news_reactor_system, news_reactor_inputs)
        if strategy_name not in self.strategy_setting_dict:
            self.strategy_setting_dict[strategy_name]={
                                                        'strategy_name':strategy_name,
                                                        'symbol':symbol,
                                                        'timeframe':timeframe,
                                                        'trading_strategy_system':trading_strategy_system,
                                                        'trading_strategy_inputs':trading_strategy_inputs,
                                                        'risk_management_system':risk_management_system,
                                                        'risk_management_system_inputs':risk_management_system_inputs,
                                                        'news_reactor_system':news_reactor_system,
                                                        'news_reactor_inputs':news_reactor_inputs,
                                                        'position_type':None,
                                                        'position_trade_id':None,
                                                        'position_size':None,
                                                        'news_position_type':None,
                                                        'news_position_trade_id':None,
                                                        'news_position_size':None
                                                        }
            with open('./data/strategies_settings.cfg', 'wb') as f: 
                pickle.dump(self.strategy_setting_dict, f)



    #Editing strategy. It gets the strategy name and parameters to edit, then it reinstantiates the strategy system class, and saves the new setting.
    def edit_strategy(self, strategy_name, arguments):
        self.stop_strategy(strategy_name)
        for key, value in arguments.items():
            setattr(self.strategies_dict[strategy_name], key, value)
            self.strategy_setting_dict[self.strategies_dict[strategy_name].strategy_name][key]=value
            
        self.strategies_dict[strategy_name].init_strategy()
        with open('./data/strategies_settings.cfg', 'wb') as f: 
            pickle.dump(self.strategy_setting_dict, f)
        
    #Deleting strategy. It gets strategy name and calls delete method of the trading_strategy class, the it update strategies_settings.cfg file
    def delete_strategy(self, strategy_name):
        self.strategies_dict[strategy_name].delete()
        try:
            self.strategies_dict[strategy_name].terminate()
        except:
            pass
        del self.strategy_setting_dict[strategy_name]
        with open('./data/strategies_settings.cfg', 'wb') as f: 
            pickle.dump(self.strategy_setting_dict, f)
        del self.strategies_dict[strategy_name]

    #Stoping all strategies. It stops all strategies by stoping their processes.
    def stop_all_strategies(self):
        for key, value in self.strategies_dict.items():
            if self.strategies_dict[key].process_status()==True:
                self.strategies_dict[key].stop()
                try:
                    self.strategies_dict[key].terminate()
                except:
                    pass

    #Stoping a strategy. It stops the strategy by stoping its processes.
    def stop_strategy(self, strategy_name):
        if self.strategies_dict[strategy_name].process_status()==True:
            self.strategies_dict[strategy_name].stop()
            try:
                self.strategies_dict[strategy_name].terminate()
            except:
                pass

    #Starting all strategies. It starts all strategies by starting their processes.
    def start_all_strategies(self):
        self.stop_all_strategies()
        self.init_saved_strategies()
        for key, value in self.strategies_dict.items():
            try:
                if self.strategies_dict[key].start_process()==True:
                    self.strategies_dict[key].start()
            except Exception as e:
                print(e)

    #Starting a strategy. It starts the strategy by starting its processes.
    def start_strategy(self, strategy_name):
        self.stop_strategy(strategy_name)
        self.init_saved_strategies(strategy_name)
        try:
            if self.strategies_dict[strategy_name].start_process()==True:
                self.strategies_dict[strategy_name].start()
        except Exception as e:
            print(e)

    #Backtesting strategy. It gets strategy name, quantity of prices for backtesting and initial capital.
    def backtest_strategy(self, strategy_name, quantity, capital):
        self.strategies_dict[strategy_name].backtest(quantity, capital)

    def get_backtest_result(self, strategy_name):
        return self.strategies_shared_memory_dict[strategy_name]['backtesting_result']


    #It gets the progress perventage of backtesing.
    def get_backtest_progress_rate(self, strategy_name):
        return self.strategies_shared_memory_dict[strategy_name]['backtest_progress_counter']

    #It raises a flag to stop backtesting.
    def backtest_stop(self, strategy_name):
        self.strategies_shared_memory_dict[strategy_name]['stop_backtesting_signal']=True
        self.strategies_shared_memory_dict[strategy_name]['backtesting_result']={}

    #It gets the status of the strategy.
    def strategy_status_get(self, strategy_name):
        return self.strategies_shared_memory_dict[strategy_name]['strategy_status'], self.strategies_shared_memory_dict[strategy_name]['last_start'], self.strategies_shared_memory_dict[strategy_name]['last_stop']



'''
trading_strategy class is a class of strategy. It gets list of setting for a strategy including:
strategy_name: str,
trading_strategy_system: str,
trading_strategy_inputs: dict,
symbol: str,
timeframe: str,
risk_management_system: str,
risk_management_system_inputs:dict,
news_reactor_system: str,
news_reactor_inputs:dict

trading_strategy class inherits from multiprocessing.Process for multiprocessing.
When start_process method of this class is called, a new process starts.

'''

class trading_strategy(multiprocessing.Process):
    def __init__(self, trading_strategies_classes_dict, news_reactor_classes_dict, risk_management_classes_dict, shared_memory_dict, strategy_name, trading_strategy_system, trading_strategy_inputs, symbol, timeframe, risk_management_system, risk_management_system_inputs, news_reactor_system, news_reactor_inputs):
        multiprocessing.Process.__init__(self)
        self.trading_strategies_classes_dict=trading_strategies_classes_dict
        self.news_reactor_classes_dict=news_reactor_classes_dict
        self.risk_management_classes_dict=risk_management_classes_dict
        self.shared_memory_dict=shared_memory_dict
        self.strategy_name=strategy_name
        self.trading_strategy_system=trading_strategy_system
        self.symbol=symbol
        self.timeframe=timeframe
        self.quantity=1000
        self.risk_management_system=risk_management_system
        self.news_reactor_system=news_reactor_system
        self.trading_strategy_inputs=trading_strategy_inputs
        self.risk_management_system_inputs=risk_management_system_inputs
        self.news_reactor_inputs=news_reactor_inputs
        self.db=Db_Controller()
        self.name=self.strategy_name
        self.init_strategy()

    def __str__(self):
        return self.strategy_name

    #Preparing required sources. This method instantiate the classes of selected systems (risk management system, trading strategy system and news reactor system) using given inputs. 
    def init_strategy(self):
        try:
            self.fxcm_instance_internal=fxcm_controller.Fxcm()
            strategy_args=self.trading_strategy_inputs
            strategy_args['symbol']=self.symbol
            strategy_args['timeframe']=self.timeframe
            risk_management_args=self.risk_management_system_inputs
            risk_management_args['symbol']=self.symbol
            risk_management_args['timeframe']=self.timeframe
            risk_management_args['account_id']=self.fxcm_instance_internal.account_id
            risk_management_args['account_currency']=self.fxcm_instance_internal.account_currency
            self.trading_strategy_instance=eval(self.trading_strategies_classes_dict[self.trading_strategy_system])(**strategy_args)
            self.risk_management_instance=eval(self.risk_management_classes_dict[self.risk_management_system])(**risk_management_args)
            if self.news_reactor_system==None or self.news_reactor_system=='None':
                self.news_reactor_instance=None  #Temporary
            else:
                news_reactor_args=self.news_reactor_inputs
                news_reactor_args['symbol']=self.symbol
                news_reactor_args['timeframe']=self.timeframe
                news_reactor_args['account_id']=self.fxcm_instance_internal.account_id
                news_reactor_args['account_currency']=self.fxcm_instance_internal.account_currency
                self.news_reactor_instance=eval(self.news_reactor_classes_dict[self.news_reactor_system])(**news_reactor_args)
            
            if len(self.timeframe)>4:
                self.db.create_price_data_renko_table(self.symbol, self.timeframe[6:])
            else:
                self.db.create_price_data_table(self.symbol, self.timeframe)
        except Exception as e:
            print(e)

    def get_data_backtest(self, quantity):
        if len(self.timeframe)>4:
            renko_range=self.timeframe[6:]
            return self.db.query_price_data_renko(self.symbol, renko_range, quantity)
        else:
            return self.db.query_price_data(self.symbol, self.timeframe, quantity)


    def backtest(self, qty, cap):
        """
        This method runs backtesting based on current settings of the strategy
        """
        try:
            """
            Setting default result dictionary
            """
            self.shared_memory_dict['backtesting_result']={} 
            self.shared_memory_dict['backtest_progress_counter']=0 
            quantity=int(qty)
            capital=int(cap)
            initial_capital=capital
            backtest_result_dict={}
            backtest_result_dict['Backtesting period']=datetime.timedelta(minutes=0)
            backtest_result_dict['Number of trades']=0
            backtest_result_dict['Number of successful trades']=0
            backtest_result_dict['Number of unsuccessful trades']=0
            backtest_result_dict['Number of stop loss triggered']=0
            backtest_result_dict['Number of limit triggered']=0
            backtest_result_dict['Longest time in a trade']=0
            backtest_result_dict['Shortest time in a trade']=0
            backtest_result_dict['Average time in a trade']=0
            backtest_result_dict['Maximum drawup']=0
            backtest_result_dict['Maximum drawdown']=0
            backtest_result_dict['Maximum profit in one trade']=0
            backtest_result_dict['Maximum loss in one trade']=0
            backtest_result_dict['Maximum gained pip in one trade']=0
            backtest_result_dict['Maximum lost pip in one trade']=0
            backtest_result_dict['Average gained/lost pip per trade']=0
            backtest_result_dict['Maximum consecutive successfull trade']=0
            backtest_result_dict['Maximum consecutive unsuccessfull trade']=0
            backtest_result_dict['Total gained/lost pip']=0
            backtest_result_dict['Net gained/lost pip']=0
            backtest_result_dict['Average gained/lost pip per day']=0
            backtest_result_dict['Gained pip']=0
            backtest_result_dict['Lost pip']=0
            backtest_result_dict['Profit']=0
            backtest_result_dict['Loss']=0
            backtest_result_dict['Capital']=0
            backtest_result_dict['Net profit/loss']=0
            backtest_result_dict['Net profit/loss percentage']=0
            backtest_result_dict['Largest position size']=0
            backtest_result_dict['Smallest position size']=0
            backtest_result_dict['Largest stop loss']=0
            backtest_result_dict['Smallest stop loss']=0
            backtest_result_dict['Largest limit']=0
            backtest_result_dict['Smallest limit']=0
            try: #Checking if the required price data is avaliable, if not get from fxcm
                data=self.get_data_backtest(quantity)
                if data.empty or len(data)<quantity:
                    if self.fxcm_instance_internal.connection==None or self.fxcm_instance_internal.connection.is_connected()!=True:
                        self.fxcm_instance_internal.connect(self.strategy_name+'_backtest')
                        if self.fxcm_instance_internal.connection.is_connected():
                            if len(self.timeframe)>4:
                                self.renko_cal_init()
                                data=self.get_data_backtest(quantity)
                            else:
                                result=self.fxcm_instance_internal.get_price_data(self.symbol, self.timeframe, quantity)
                                if result==True:
                                    data=self.get_data_backtest(quantity)
                                    self.fxcm_instance_internal.disconnect()
                        else:
                            self.fxcm_instance_internal.disconnect()
                            self.shared_memory_dict['backtest_progress_counter']=0
                            self.shared_memory_dict['backtesting_result']=backtest_result_dict   
                            return backtest_result_dict

            except Exception as e:
                print(e, 'backtesting')
                self.fxcm_instance_internal.disconnect()
                self.shared_memory_dict['backtest_progress_counter']=0
                self.shared_memory_dict['backtesting_result']=backtest_result_dict     
                return backtest_result_dict

            try:
                data['date'] =  pd.to_datetime(data['date'], format='%Y-%m-%d %H:%M:%S')
            except:
                data['date'] =  pd.to_datetime(data['date'], format='%m/%d/%Y %H:%M')

            if self.symbol[-3:]=='JPY':
                pip_multiplier=100
            else:
                pip_multiplier=10000
            round_digit=3
            position_type=None
            position_entered_price=None
            position_entered_price_index=None
            lost_pip=[]
            lost_money=[]
            gained_pip=[]
            gained_money=[]
            all_trades_pip_net=[]
            all_trades_pip_total=[]
            drawdowns=[]
            drawups=[]
            stop_loss_triggered=0
            limit_triggered=0
            time_in_trade=[]
            position_size_list=[]
            stop_loss_list=[]
            limit_list=[]

            """
            Starting checking condition
            """

            self.shared_memory_dict['stop_backtesting_signal']=False
            for i in range(len(data)):
                try:
                    if self.shared_memory_dict['stop_backtesting_signal']==True:
                        self.shared_memory_dict['backtest_progress_counter']=0
                        self.shared_memory_dict['backtesting_result']=backtest_result_dict   
                        return backtest_result_dict
                    else:
                        if i==len(data)-1:
                            data_temp=data.iloc[:].copy()
                        else:
                            data_temp=data.iloc[:i+1].copy()

                        """
                        Checking for exit signal, stop loss and limit
                        """
                        if position_type!=None:
                            condition_exit_result=self.trading_strategy_instance.backtest_exit(position_type, data_temp)
                            print(343433434)
                            position_exit_price=data.bidclose.iloc[i]
                            spread=abs(data.bidclose.iloc[i]-data.askclose.iloc[i])
                            if condition_exit_result=='exit' or i==len(data)-1:
                                if position_type=='buy':
                                    pl_pip=position_exit_price-position_entered_price
                                    pl_pip-=spread
                                    drawups.append(max(data.bidclose.iloc[position_entered_price_index:])-position_entered_price)
                                    drawdowns.append(min(data.bidclose.iloc[position_entered_price_index:])-position_entered_price)
                                    pl=pl_pip*pip_multiplier*pip_value
                                    capital+=pl
                                    if pl_pip>0:
                                        gained_pip.append(pl_pip)
                                        gained_money.append(pl)
                                    else:
                                        lost_pip.append(pl_pip)
                                        lost_money.append(pl)
                                    all_trades_pip_net.append(pl_pip)
                                    all_trades_pip_total.append(pl_pip+spread)
                                    duration_in_trade=data.date.iloc[i]-data.date.iloc[position_entered_price_index]
                                    time_in_trade.append(duration_in_trade)
                                    position_type=None
                                
                                else:
                                    pl_pip=position_entered_price-position_exit_price
                                    pl_pip-=spread
                                    drawups.append(position_entered_price-min(data.bidclose.iloc[position_entered_price_index:i+1]))
                                    drawdowns.append(position_entered_price-max(data.bidclose.iloc[position_entered_price_index:i+1]))
                                    pl=pl_pip*pip_multiplier*pip_value
                                    capital+=pl
                                    if pl_pip>0:
                                        gained_pip.append(pl_pip)
                                        gained_money.append(pl)
                                    else:
                                        lost_pip.append(pl_pip)
                                        lost_money.append(pl)
                                    all_trades_pip_net.append(pl_pip)
                                    all_trades_pip_total.append(pl_pip+spread)
                                    duration_in_trade=data.date.iloc[i]-data.date.iloc[position_entered_price_index]
                                    time_in_trade.append(duration_in_trade)
                                    position_type=None
                                

                            elif data.bidhigh.iloc[i]>stop_loss and position_type=='sell':
                                pl_pip=position_entered_price-stop_loss
                                pl_pip-=spread
                                stop_loss_triggered+=1
                                drawups.append(position_entered_price-min(data.bidclose.iloc[position_entered_price_index:i+1]))
                                drawdowns.append(position_entered_price-max(data.bidclose.iloc[position_entered_price_index:i+1]))
                                pl=pl_pip*pip_multiplier*pip_value
                                capital+=pl
                                if pl_pip>0:
                                    gained_pip.append(pl_pip)
                                    gained_money.append(pl)
                                else:
                                    lost_pip.append(pl_pip)
                                    lost_money.append(pl)
                                all_trades_pip_net.append(pl_pip)
                                all_trades_pip_total.append(pl_pip+spread)
                                duration_in_trade=data.date.iloc[i]-data.date.iloc[position_entered_price_index]
                                time_in_trade.append(duration_in_trade)
                                position_type=None
                                

                            elif data.bidlow.iloc[i]<limit and position_type=='sell':
                                pl_pip=position_entered_price-limit
                                pl_pip-=spread
                                limit_triggered+=1
                                drawups.append(position_entered_price-min(data.bidclose.iloc[position_entered_price_index:i+1]))
                                drawdowns.append(position_entered_price-max(data.bidclose.iloc[position_entered_price_index:i+1]))
                                pl=pl_pip*pip_multiplier*pip_value
                                capital+=pl
                                if pl_pip>0:
                                    gained_pip.append(pl_pip)
                                    gained_money.append(pl)
                                else:
                                    lost_pip.append(pl_pip)
                                    lost_money.append(pl)
                                all_trades_pip_net.append(pl_pip)
                                all_trades_pip_total.append(pl_pip+spread)
                                duration_in_trade=data.date.iloc[i]-data.date.iloc[position_entered_price_index]
                                time_in_trade.append(duration_in_trade)
                                position_type=None

                            elif data.bidlow.iloc[i]<stop_loss and position_type=='buy':
                                pl_pip=stop_loss-position_entered_price
                                pl_pip-=spread
                                stop_loss_triggered+=1
                                drawups.append(max(data.bidclose.iloc[position_entered_price_index:i+1])-position_entered_price)
                                drawdowns.append(min(data.bidclose.iloc[position_entered_price_index:i+1])-position_entered_price)
                                pl=pl_pip*pip_multiplier*pip_value
                                capital+=pl
                                if pl_pip>0:
                                    gained_pip.append(pl_pip)
                                    gained_money.append(pl)
                                else:
                                    lost_pip.append(pl_pip)
                                    lost_money.append(pl)
                                all_trades_pip_net.append(pl_pip)
                                all_trades_pip_total.append(pl_pip+spread)
                                duration_in_trade=data.date.iloc[i]-data.date.iloc[position_entered_price_index]
                                time_in_trade.append(duration_in_trade)
                                position_type=None

                            elif data.bidhigh.iloc[i]>limit and position_type=='buy':
                                pl_pip=limit-position_entered_price
                                pl_pip-=spread
                                limit_triggered+1
                                drawups.append(max(data.bidclose.iloc[position_entered_price_index:i+1])-position_entered_price)
                                drawdowns.append(min(data.bidclose.iloc[position_entered_price_index:i+1])-position_entered_price)
                                pl=pl_pip*pip_multiplier*pip_value
                                capital+=pl
                                if pl_pip>0:
                                    gained_pip.append(pl_pip)
                                    gained_money.append(pl)
                                else:
                                    lost_pip.append(pl_pip)
                                    lost_money.append(pl)
                                all_trades_pip_net.append(pl_pip)
                                all_trades_pip_total.append(pl_pip+spread)
                                duration_in_trade=data.date.iloc[i]-data.date.iloc[position_entered_price_index]
                                time_in_trade.append(duration_in_trade)
                                position_type=None


                        """
                        Checking for entry
                        """
                        if position_type==None and i<len(data)-2:
                            condition_entry_result=self.trading_strategy_instance.backtest_entry(data_temp)
                            print(67676767)
                            if condition_entry_result=='buy':
                                position_size, required_margin, stop_loss, limit, stop_loss_pip, limit_pip, pip_value=self.risk_management_instance.backtest('buy', data_temp, capital)
                                print(989898)
                                position_type='buy'
                                position_entered_price=data_temp.bidclose.iloc[i]
                                position_entered_price_index=i
                                position_size_list.append(position_size)
                                stop_loss_list.append(stop_loss_pip)
                                limit_list.append(limit_pip)
                                
                            elif condition_entry_result=='sell':
                                position_size, required_margin, stop_loss, limit, stop_loss_pip, limit_pip, pip_value=self.risk_management_instance.backtest('sell', data_temp, capital)
                                print(989898)
                                position_type='sell'
                                position_entered_price=data_temp.bidclose.iloc[i]
                                position_entered_price_index=i
                                position_size_list.append(position_size)
                                stop_loss_list.append(stop_loss_pip)
                                limit_list.append(limit_pip)
                                
                        self.shared_memory_dict['backtest_progress_counter']=(i/len(data))*100

                except Exception as e:
                    print(e, 'backtesting')

            self.shared_memory_dict['backtest_progress_counter']=100

            """
            Calculating result values
            """

            consecutive_negative=0
            consecutive_positive=0
            consecutive_negative_temp=0
            consecutive_positive_temp=0
            for i, j in enumerate(all_trades_pip_net):
                if j>0:
                    consecutive_positive_temp+=1
                    consecutive_negative_temp=0
                elif j<0:
                    consecutive_negative_temp+=1
                    consecutive_positive_temp=0
                if consecutive_positive_temp>consecutive_positive:
                    consecutive_positive=consecutive_positive_temp
                elif consecutive_negative_temp>consecutive_negative:
                    consecutive_negative=consecutive_negative_temp

            
            backtest_result_dict={}
            backtest_result_dict['Backtesting period']=str(data.date.iloc[-1]-data.date.iloc[0])
            backtest_result_dict['Number of trades']=len(all_trades_pip_net)
            backtest_result_dict['Number of successful trades']=len(gained_pip)
            backtest_result_dict['Number of unsuccessful trades']=len(lost_pip)
            backtest_result_dict['Number of stop loss triggered']=stop_loss_triggered
            backtest_result_dict['Number of limit triggered']=limit_triggered
            try:
                backtest_result_dict['Longest time in a trade']=str(max(time_in_trade))
            except:
                backtest_result_dict['Longest time in a trade']=str(datetime.timedelta(minutes=0))
            try:
                backtest_result_dict['Shortest time in a trade']=str(min(time_in_trade))
            except:
                backtest_result_dict['Shortest time in a trade']=str(datetime.timedelta(minutes=0))
            try:
                backtest_result_dict['Average time in a trade']=str(np.mean(time_in_trade))
            except:
                backtest_result_dict['Average time in a trade']=str(datetime.timedelta(minutes=0))
            try:
                backtest_result_dict['Maximum drawup']=round(max(drawups)*pip_multiplier, round_digit)
            except:
                backtest_result_dict['Maximum drawup']=0
            try:
                backtest_result_dict['Maximum drawdown']=round(min(drawdowns)*pip_multiplier, round_digit)
            except:
                backtest_result_dict['Maximum drawdown']=0
            try:
                backtest_result_dict['Maximum profit in one trade']=round(max(gained_money), round_digit)
            except:
                backtest_result_dict['Maximum profit in one trade']=0
            try:
                backtest_result_dict['Maximum loss in one trade']=round(min(lost_money), round_digit)
            except:
                backtest_result_dict['Maximum loss in one trade']=0
            try:
                backtest_result_dict['Maximum gained pip in one trade']=round(max(gained_pip)*pip_multiplier, round_digit)
            except:
                backtest_result_dict['Maximum gained pip in one trade']=0
            try:
                backtest_result_dict['Maximum lost pip in one trade']=round(min(lost_pip)*pip_multiplier, round_digit)
            except:
                backtest_result_dict['Maximum lost pip in one trade']=0
            try:
                backtest_result_dict['Average gained/lost pip per trade']=round((sum(all_trades_pip_net)*pip_multiplier)/len(data.date), round_digit)
            except:
                backtest_result_dict['Average gained/lost pip per trade']=0
            backtest_result_dict['Maximum consecutive successfull trade']=consecutive_positive
            backtest_result_dict['Maximum consecutive unsuccessfull trade']=consecutive_negative
            try:
                backtest_result_dict['Total gained/lost pip']=round(sum(all_trades_pip_total)*pip_multiplier, round_digit)
            except:
                backtest_result_dict['Total gained/lost pip']=0
            try:
                backtest_result_dict['Net gained/lost pip']=round(sum(all_trades_pip_net)*pip_multiplier, round_digit)
            except:
                backtest_result_dict['Net gained/lost pip']=0
            try:
                backtest_result_dict['Average gained/lost pip per day']=round((sum(all_trades_pip_net)*pip_multiplier)/(data.date.iloc[-1]-data.date.iloc[0]).days, round_digit)
            except:
                backtest_result_dict['Average gained/lost pip per day']=0
            try:
                backtest_result_dict['Gained pip']=round(sum(gained_pip)*pip_multiplier, round_digit)
            except:
                backtest_result_dict['Gained pip']=0
            try:
                backtest_result_dict['Lost pip']=round(sum(lost_pip)*pip_multiplier, round_digit)
            except:
                backtest_result_dict['Lost pip']=0
            try:
                backtest_result_dict['Profit']=round(sum(gained_money), round_digit)
            except:
                backtest_result_dict['Profit']=0
            try:
                backtest_result_dict['Loss']=round(sum(lost_money), round_digit)
            except:
                backtest_result_dict['Loss']=0
            backtest_result_dict['Capital']=round(capital, round_digit)
            try:
                backtest_result_dict['Net profit/loss']=round(capital-initial_capital, round_digit)
            except:
                backtest_result_dict['Net profit/loss']=0
            try:
                backtest_result_dict['Net profit/loss percentage']=round(((capital-initial_capital)/initial_capital)*100, round_digit)
            except:
                backtest_result_dict['Net profit/loss percentage']=0
            try:
                backtest_result_dict['Largest position size']=max(position_size_list)
            except:
                backtest_result_dict['Largest position size']=0
            try:
                backtest_result_dict['Smallest position size']=min(position_size_list)
            except:
                backtest_result_dict['Smallest position size']=0
            try:
                backtest_result_dict['Smallest stop loss']=round(min(stop_loss_list), round_digit)
            except:
                backtest_result_dict['Smallest stop loss']=0
            try:
                backtest_result_dict['Largest stop loss']=round(max(stop_loss_list), round_digit)
            except:
                backtest_result_dict['Largest stop loss']=0
            try:
                backtest_result_dict['Smallest limit']=round(min(limit_list), round_digit)
            except:
                backtest_result_dict['Smallest limit']=0
            try:
                backtest_result_dict['Largest limit']=round(max(limit_list), round_digit)
            except:
                backtest_result_dict['Largest limit']=0

            self.shared_memory_dict['backtesting_result']=backtest_result_dict
            return backtest_result_dict
        except Exception as e:
            print(e, 'backtesting')
            self.shared_memory_dict['backtest_progress_counter']=0
            self.shared_memory_dict['backtesting_result']=backtest_result_dict
            return backtest_result_dict


    def check_condition(self):
        """
        This method checks the condition and called from running process
        """
        try:
            if self.news_reactor_instance==None:
                if len(self.db.query_table('OpenPosition', ('tradeId',), fields=('tradeId',), values=(self.shared_memory_dict['position_trade_id'],)))==0:
                    self.shared_memory_dict['position_trade_id']=None
                    self.shared_memory_dict['position_type']=None
                    self.shared_memory_dict['position_size']=None
                    with open('./data/strategies_settings.cfg', 'rb') as f: 
                        strategy_setting_dict = pickle.load(f)
                        strategy_setting_dict[self.strategy_name]['position_type']=self.shared_memory_dict['position_type']
                        strategy_setting_dict[self.strategy_name]['position_trade_id']=self.shared_memory_dict['position_trade_id']
                        strategy_setting_dict[self.strategy_name]['position_size']=self.shared_memory_dict['position_size']
                    with open('./data/strategies_settings.cfg', 'wb') as f: 
                        pickle.dump(strategy_setting_dict, f)


                if self.shared_memory_dict['position_type']!=None:
                    condition_exit_result=self.trading_strategy_instance.check_exit(self.shared_memory_dict['position_type'])
                    if condition_exit_result!=None:
                        close_position_args={'trade_id':self.shared_memory_dict['position_trade_id'], 'amount':self.db.query_table('OpenPosition', ('amountK',), fields=('tradeId',), values=(self.shared_memory_dict['position_trade_id'],))[0][0], 'maker':self.strategy_name}
                        if self.fxcm_instance.close_position(**close_position_args)==True:
                            self.shared_memory_dict['position_trade_id']=None
                            self.shared_memory_dict['position_type']=None
                            self.shared_memory_dict['position_size']=None
                            with open('./data/strategies_settings.cfg', 'rb') as f: 
                                strategy_setting_dict = pickle.load(f)
                                strategy_setting_dict[self.strategy_name]['position_type']=self.shared_memory_dict['position_type']
                                strategy_setting_dict[self.strategy_name]['position_trade_id']=self.shared_memory_dict['position_trade_id']
                                strategy_setting_dict[self.strategy_name]['position_size']=self.shared_memory_dict['position_size']
                            with open('./data/strategies_settings.cfg', 'wb') as f: 
                                pickle.dump(strategy_setting_dict, f)
                
                if self.shared_memory_dict['position_type']==None:
                    condition_entry_result=self.trading_strategy_instance.check_entry()
                    if condition_entry_result!=None:
                        if self.shared_memory_dict['position_type']==None:
                            if condition_entry_result=='buy':
                                self.shared_memory_dict['position_size'], required_margin, stop_loss, limit, stop_loss_pip, limit_pip=self.risk_management_instance.position_size_stop_loss('buy')
                                fxcm_info=self.db.query_table('Fxcm_Info', ('*',), fields=("accountId",), values=(self.fxcm_instance.account_id,))
                                if fxcm_info[0][11]>required_margin:
                                    open_position_args={'symbol':self.symbol, 'is_buy':True,
                                                        'stop':stop_loss, 'is_in_pips':False,
                                                        'amount':self.shared_memory_dict['position_size'], 'time_in_force':'GTC',
                                                        'order_type':'AtMarket', "limit":limit, 'maker':self.strategy_name}
                                    self.shared_memory_dict['position_trade_id']=self.fxcm_instance.open_position(**open_position_args)
                                    if self.shared_memory_dict['position_trade_id']!=None:
                                        self.shared_memory_dict['position_type']='buy'
                                        with open('./data/strategies_settings.cfg', 'rb') as f: 
                                            strategy_setting_dict = pickle.load(f)
                                            strategy_setting_dict[self.strategy_name]['position_type']=self.shared_memory_dict['position_type']
                                            strategy_setting_dict[self.strategy_name]['position_trade_id']=self.shared_memory_dict['position_trade_id']
                                            strategy_setting_dict[self.strategy_name]['position_size']=self.shared_memory_dict['position_size']
                                        with open('./data/strategies_settings.cfg', 'wb') as f: 
                                            pickle.dump(strategy_setting_dict, f)

                                
                            elif condition_entry_result=='sell':
                                self.shared_memory_dict['position_size'], required_margin, stop_loss, limit, stop_loss_pip, limit_pip=self.risk_management_instance.position_size_stop_loss('sell')
                                fxcm_info=self.db.query_table('Fxcm_Info', ('*',), fields=("accountId",), values=(self.fxcm_instance.account_id,))
                                if fxcm_info[0][11]>required_margin:
                                    open_position_args={'symbol':self.symbol, 'is_buy':False,
                                                        'stop':stop_loss, 'is_in_pips':False,
                                                        'amount':self.shared_memory_dict['position_size'], 'time_in_force':'GTC',
                                                        'order_type':'AtMarket', "limit":limit, 'maker':self.strategy_name}
                                    self.shared_memory_dict['position_trade_id']=self.fxcm_instance.open_position(**open_position_args)
                                    if self.shared_memory_dict['position_trade_id']!=None:
                                        self.shared_memory_dict['position_type']='sell'
                                        with open('./data/strategies_settings.cfg', 'rb') as f: 
                                            strategy_setting_dict = pickle.load(f)
                                            strategy_setting_dict[self.strategy_name]['position_type']=self.shared_memory_dict['position_type']
                                            strategy_setting_dict[self.strategy_name]['position_trade_id']=self.shared_memory_dict['position_trade_id']
                                            strategy_setting_dict[self.strategy_name]['position_size']=self.shared_memory_dict['position_size']
                                        with open('./data/strategies_settings.cfg', 'wb') as f: 
                                            pickle.dump(strategy_setting_dict, f)

            else:
                if len(self.db.query_table('OpenPosition', ('tradeId',), fields=('tradeId',), values=(self.shared_memory_dict['position_trade_id'],)))==0:
                    self.shared_memory_dict['position_trade_id']=None
                    self.shared_memory_dict['position_type']=None
                    self.shared_memory_dict['position_size']=None
                    with open('./data/strategies_settings.cfg', 'rb') as f: 
                        strategy_setting_dict = pickle.load(f)
                        strategy_setting_dict[self.strategy_name]['position_type']=self.shared_memory_dict['position_type']
                        strategy_setting_dict[self.strategy_name]['position_trade_id']=self.shared_memory_dict['position_trade_id']
                        strategy_setting_dict[self.strategy_name]['position_size']=self.shared_memory_dict['position_size']
                    with open('./data/strategies_settings.cfg', 'wb') as f: 
                        pickle.dump(strategy_setting_dict, f)
                if len(self.db.query_table('OpenPosition', ('tradeId',), fields=('tradeId',), values=(self.shared_memory_dict['news_position_trade_id'],)))==0:
                    self.shared_memory_dict['news_position_trade_id']=None
                    self.shared_memory_dict['news_position_type']=None
                    self.shared_memory_dict['news_position_size']=None
                    with open('./data/strategies_settings.cfg', 'rb') as f: 
                        strategy_setting_dict = pickle.load(f)
                        strategy_setting_dict[self.strategy_name]['news_position_type']=self.shared_memory_dict['news_position_type']
                        strategy_setting_dict[self.strategy_name]['news_position_trade_id']=self.shared_memory_dict['news_position_trade_id']
                        strategy_setting_dict[self.strategy_name]['news_position_size']=self.shared_memory_dict['news_position_size']
                    with open('./data/strategies_settings.cfg', 'wb') as f: 
                        pickle.dump(strategy_setting_dict, f)


                news_check_condition_entry_result=self.news_reactor_instance.check_condition_entry()
                news_check_condition_stop_buy_result=self.news_reactor_instance.check_condition_stop('buy')
                news_check_condition_stop_sell_result=self.news_reactor_instance.check_condition_stop('sell')
                if news_check_condition_entry_result==False:
                    if self.shared_memory_dict['position_type']!=None:
                        condition_exit_result=self.trading_strategy_instance.check_exit(self.shared_memory_dict['position_type'])
                        if condition_exit_result!=None:
                            close_position_args={'trade_id':self.shared_memory_dict['position_trade_id'], 'amount':self.db.query_table('OpenPosition', ('amountK',), fields=('tradeId',), values=(self.shared_memory_dict['position_trade_id'],))[0][0], 'maker':self.strategy_name}
                            if self.fxcm_instance.close_position(**close_position_args)==True:
                                self.shared_memory_dict['position_trade_id']=None
                                self.shared_memory_dict['position_type']=None
                                self.shared_memory_dict['position_size']=None
                                with open('./data/strategies_settings.cfg', 'rb') as f: 
                                    strategy_setting_dict = pickle.load(f)
                                    strategy_setting_dict[self.strategy_name]['position_type']=self.shared_memory_dict['position_type']
                                    strategy_setting_dict[self.strategy_name]['position_trade_id']=self.shared_memory_dict['position_trade_id']
                                    strategy_setting_dict[self.strategy_name]['position_size']=self.shared_memory_dict['position_size']
                                with open('./data/strategies_settings.cfg', 'wb') as f: 
                                    pickle.dump(strategy_setting_dict, f)
                    
                    if self.shared_memory_dict['position_type']==None:
                        condition_entry_result=self.trading_strategy_instance.check_entry()
                        if condition_entry_result!=None:
                            if self.shared_memory_dict['position_type']==None:
                                if condition_entry_result=='buy':
                                    self.shared_memory_dict['position_size'], required_margin, stop_loss, limit, stop_loss_pip, limit_pip=self.risk_management_instance.position_size_stop_loss('buy')
                                    fxcm_info=self.db.query_table('Fxcm_Info', ('*',), fields=("accountId",), values=(self.fxcm_instance.account_id,))
                                    if fxcm_info[0][11]>required_margin:
                                        open_position_args={'symbol':self.symbol, 'is_buy':True,
                                                            'stop':stop_loss, 'is_in_pips':False,
                                                            'amount':self.shared_memory_dict['position_size'], 'time_in_force':'GTC',
                                                            'order_type':'AtMarket', "limit":limit, 'maker':self.strategy_name}
                                        self.shared_memory_dict['position_trade_id']=self.fxcm_instance.open_position(**open_position_args)
                                        if self.shared_memory_dict['position_trade_id']!=None:
                                            self.shared_memory_dict['position_type']='buy'
                                            with open('./data/strategies_settings.cfg', 'rb') as f: 
                                                strategy_setting_dict = pickle.load(f)
                                                strategy_setting_dict[self.strategy_name]['position_type']=self.shared_memory_dict['position_type']
                                                strategy_setting_dict[self.strategy_name]['position_trade_id']=self.shared_memory_dict['position_trade_id']
                                                strategy_setting_dict[self.strategy_name]['position_size']=self.shared_memory_dict['position_size']
                                            with open('./data/strategies_settings.cfg', 'wb') as f: 
                                                pickle.dump(strategy_setting_dict, f)

                                    
                                elif condition_entry_result=='sell':
                                    self.shared_memory_dict['position_size'], required_margin, stop_loss, limit, stop_loss_pip, limit_pip=self.risk_management_instance.position_size_stop_loss('sell')
                                    fxcm_info=self.db.query_table('Fxcm_Info', ('*',), fields=("accountId",), values=(self.fxcm_instance.account_id,))
                                    if fxcm_info[0][11]>required_margin:
                                        open_position_args={'symbol':self.symbol, 'is_buy':False,
                                                            'stop':stop_loss, 'is_in_pips':False,
                                                            'amount':self.shared_memory_dict['position_size'], 'time_in_force':'GTC',
                                                            'order_type':'AtMarket', "limit":limit, 'maker':self.strategy_name}
                                        self.shared_memory_dict['position_trade_id']=self.fxcm_instance.open_position(**open_position_args)
                                        if self.shared_memory_dict['position_trade_id']!=None:
                                            self.shared_memory_dict['position_type']='sell'
                                            with open('./data/strategies_settings.cfg', 'rb') as f: 
                                                strategy_setting_dict = pickle.load(f)
                                                strategy_setting_dict[self.strategy_name]['position_type']=self.shared_memory_dict['position_type']
                                                strategy_setting_dict[self.strategy_name]['position_trade_id']=self.shared_memory_dict['position_trade_id']
                                                strategy_setting_dict[self.strategy_name]['position_size']=self.shared_memory_dict['position_size']
                                            with open('./data/strategies_settings.cfg', 'wb') as f: 
                                                pickle.dump(strategy_setting_dict, f)
                
                elif type(news_check_condition_entry_result)!=bool:
                    if news_check_condition_entry_result['position_type']=='buy':
                        if self.shared_memory_dict['news_position_type']=='sell':
                            close_position_args={'trade_id':self.shared_memory_dict['news_position_trade_id'], 'amount':self.db.query_table('OpenPosition', ('amountK',), fields=('tradeId',), values=(self.shared_memory_dict['position_trade_id'],))[0][0], 'maker':self.strategy_name+'(News)'}
                            if self.fxcm_instance.close_position(**close_position_args)==True:
                                self.shared_memory_dict['news_position_trade_id']=None
                                self.shared_memory_dict['news_position_type']=None
                                self.shared_memory_dict['news_position_size']=None
                                with open('./data/strategies_settings.cfg', 'rb') as f: 
                                    strategy_setting_dict = pickle.load(f)
                                    strategy_setting_dict[self.strategy_name]['news_position_type']=self.shared_memory_dict['news_position_type']
                                    strategy_setting_dict[self.strategy_name]['news_position_trade_id']=self.shared_memory_dict['news_position_trade_id']
                                    strategy_setting_dict[self.strategy_name]['news_position_size']=self.shared_memory_dict['news_position_size']
                                with open('./data/strategies_settings.cfg', 'wb') as f: 
                                    pickle.dump(strategy_setting_dict, f)

                        if self.shared_memory_dict['news_position_type']==None:
                            fxcm_info=self.db.query_table('Fxcm_Info', ('*',), fields=("accountId",), values=(self.fxcm_instance.account_id,))
                            if fxcm_info[0][11]>news_check_condition_entry_result['required_margin']:
                                open_position_args={'symbol':self.symbol, 'is_buy':True,
                                                    'rate':news_check_condition_entry_result['stop_loss'], 'is_in_pips':False,
                                                    'amount':news_check_condition_entry_result['position_size'], 'time_in_force':'GTC',
                                                    'order_type':'AtMarket', "limit":news_check_condition_entry_result['limit'], 'maker':self.strategy_name+'(News)'}
                                self.shared_memory_dict['news_position_trade_id']=self.fxcm_instance.open_position(**open_position_args)
                                if self.shared_memory_dict['news_position_trade_id']!=None:
                                    self.shared_memory_dict['news_position_type']='buy'
                                    self.shared_memory_dict['news_position_size']=news_check_condition_entry_result['position_size']
                                    with open('./data/strategies_settings.cfg', 'rb') as f: 
                                        strategy_setting_dict = pickle.load(f)
                                        strategy_setting_dict[self.strategy_name]['news_position_type']=self.shared_memory_dict['news_position_type']
                                        strategy_setting_dict[self.strategy_name]['news_position_trade_id']=self.shared_memory_dict['news_position_trade_id']
                                        strategy_setting_dict[self.strategy_name]['news_position_size']=self.shared_memory_dict['news_position_size']
                                    with open('./data/strategies_settings.cfg', 'wb') as f: 
                                        pickle.dump(strategy_setting_dict, f)
                        
                    elif news_check_condition_entry_result['position_type']=='sell':
                        if self.shared_memory_dict['news_position_type']=='buy':
                            close_position_args={'trade_id':self.shared_memory_dict['news_position_trade_id'], 'amount':self.db.query_table('OpenPosition', ('amountK',), fields=('tradeId',), values=(self.shared_memory_dict['position_trade_id'],))[0][0], 'maker':self.strategy_name+'(News)'}
                            if self.fxcm_instance.close_position(**close_position_args)==True:
                                self.shared_memory_dict['news_position_trade_id']=None
                                self.shared_memory_dict['news_position_type']=None
                                self.shared_memory_dict['news_position_size']=None
                                with open('./data/strategies_settings.cfg', 'rb') as f: 
                                    strategy_setting_dict = pickle.load(f)
                                    strategy_setting_dict[self.strategy_name]['news_position_type']=self.shared_memory_dict['news_position_type']
                                    strategy_setting_dict[self.strategy_name]['news_position_trade_id']=self.shared_memory_dict['news_position_trade_id']
                                    strategy_setting_dict[self.strategy_name]['news_position_size']=self.shared_memory_dict['news_position_size']
                                with open('./data/strategies_settings.cfg', 'wb') as f: 
                                    pickle.dump(strategy_setting_dict, f)
                                
                        if self.shared_memory_dict['news_position_type']==None:
                            fxcm_info=self.db.query_table('Fxcm_Info', ('*',), fields=("accountId",), values=(self.fxcm_instance.account_id,))
                            if fxcm_info[0][11]>news_check_condition_entry_result['required_margin']:
                                open_position_args={'symbol':self.symbol, 'is_buy':False,
                                                    'rate':news_check_condition_entry_result['stop_loss'], 'is_in_pips':False,
                                                    'amount':news_check_condition_entry_result['position_size'], 'time_in_force':'GTC',
                                                    'order_type':'AtMarket', "limit":news_check_condition_entry_result['limit'], 'maker':self.strategy_name+'(News)'}
                                self.shared_memory_dict['news_position_trade_id']=self.fxcm_instance.open_position(**open_position_args)
                                if self.shared_memory_dict['news_position_trade_id']!=None:
                                    self.shared_memory_dict['news_position_type']='sell'
                                    self.shared_memory_dict['news_position_size']=news_check_condition_entry_result['position_size']
                                    with open('./data/strategies_settings.cfg', 'rb') as f: 
                                        strategy_setting_dict = pickle.load(f)
                                        strategy_setting_dict[self.strategy_name]['news_position_type']=self.shared_memory_dict['news_position_type']
                                        strategy_setting_dict[self.strategy_name]['news_position_trade_id']=self.shared_memory_dict['news_position_trade_id']
                                        strategy_setting_dict[self.strategy_name]['news_position_size']=self.shared_memory_dict['news_position_size']
                                    with open('./data/strategies_settings.cfg', 'wb') as f: 
                                        pickle.dump(strategy_setting_dict, f)

                
                
                if self.shared_memory_dict['position_type']=='buy' and news_check_condition_stop_buy_result!=False:
                    edit_position_args={
                                        'tradeId':self.shared_memory_dict['position_trade_id'], 'is_in_pips':False,
                                        'is_stop':True, 'rate':news_check_condition_stop_buy_result
                                        }
                    self.fxcm_instance.edit_position_stop_limit(**edit_position_args)
                elif self.shared_memory_dict['position_type']=='sell' and news_check_condition_stop_sell_result!=False:
                    edit_position_args={
                                        'tradeId':self.shared_memory_dict['position_trade_id'], 'is_in_pips':False,
                                        'is_stop':True, 'rate':news_check_condition_stop_sell_result
                                        }
                    self.fxcm_instance.edit_position_stop_limit(**edit_position_args)

        except Exception as e:
            print(e, 'condition_cheking')


    def renko_cal_init(self):
        try:
            now=datetime.datetime.now()
            end=now
            start=end-datetime.timedelta(days=90)
            try:
                self.ticks=self.fxcm_instance.get_tick_data(self.symbol, start, end)
            except:
                self.ticks=self.fxcm_instance_internal.get_tick_data(self.symbol, start, end)
            renko_date_list=[]
            renko_close_price_list=[]
            renko_open_price_list=[]
            renko_high_price_list=[]
            renko_low_price_list=[]
            tickqty=[]
            past_closed_price=self.ticks.Bid.iloc[0]
            past_opened_price=self.ticks.Bid.iloc[0]
            temp_qty=0
            for i, j in enumerate(self.ticks.Bid):
                temp_qty+=1
                if len(renko_close_price_list)>0:
                    if brick_color==1:
                        if j>=past_closed_price+self.renko_range:
                            past_opened_price=past_closed_price
                            past_closed_price=past_opened_price+self.renko_range
                            brick_color=1
                            renko_date_list.append(self.ticks.index[i])
                            renko_close_price_list.append(past_closed_price)
                            renko_open_price_list.append(past_opened_price)
                            renko_high_price_list.append(past_closed_price)
                            renko_low_price_list.append(past_opened_price)
                            tickqty.append(temp_qty)
                            temp_qty=0
                        elif j<=past_opened_price-(self.renko_range):
                            past_opened_price=past_opened_price
                            past_closed_price=past_opened_price-(self.renko_range)
                            brick_color=0
                            renko_date_list.append(self.ticks.index[i])
                            renko_close_price_list.append(past_closed_price)
                            renko_open_price_list.append(past_opened_price)
                            renko_high_price_list.append(past_opened_price)
                            renko_low_price_list.append(past_closed_price)
                            tickqty.append(temp_qty)
                            temp_qty=0
                    else:
                        if j>=past_opened_price+(self.renko_range):
                            past_opened_price=past_opened_price
                            past_closed_price=past_opened_price+(self.renko_range)
                            brick_color=1
                            renko_date_list.append(self.ticks.index[i])
                            renko_close_price_list.append(past_closed_price)
                            renko_open_price_list.append(past_opened_price)
                            renko_high_price_list.append(past_closed_price)
                            renko_low_price_list.append(past_opened_price)
                            tickqty.append(temp_qty)
                            temp_qty=0
                        elif j<=past_closed_price-self.renko_range:
                            past_opened_price=past_closed_price
                            past_closed_price=past_opened_price-self.renko_range
                            brick_color=0
                            renko_date_list.append(self.ticks.index[i])
                            renko_close_price_list.append(past_closed_price)
                            renko_open_price_list.append(past_opened_price)
                            renko_high_price_list.append(past_opened_price)
                            renko_low_price_list.append(past_closed_price)
                            tickqty.append(temp_qty)
                            temp_qty=0
                else:
                    if j>=past_opened_price+self.renko_range:
                        past_opened_price=past_closed_price
                        past_closed_price=past_closed_price+self.renko_range
                        brick_color=1
                        renko_date_list.append(self.ticks.index[i])
                        renko_close_price_list.append(past_closed_price)
                        renko_open_price_list.append(past_opened_price)
                        renko_high_price_list.append(past_closed_price)
                        renko_low_price_list.append(past_opened_price)
                        tickqty.append(temp_qty)
                        temp_qty=0
                    elif j<=past_closed_price-self.renko_range:
                        past_opened_price=past_closed_price
                        past_closed_price=past_closed_price-self.renko_range
                        brick_color=0
                        renko_date_list.append(self.ticks.index[i])
                        renko_close_price_list.append(past_closed_price)
                        renko_open_price_list.append(past_opened_price)
                        renko_high_price_list.append(past_opened_price)
                        renko_low_price_list.append(past_closed_price)
                        tickqty.append(temp_qty)
                        temp_qty=0

            self.renko_data['date']=renko_date_list
            self.renko_data['bidclose']=renko_close_price_list
            self.renko_data['bidopen']=renko_open_price_list
            self.renko_data['bidhigh']=renko_high_price_list
            self.renko_data['bidlow']=renko_low_price_list
            self.renko_data['tickqty']=tickqty

            self.db.insert_into_price_data_renko_table(self.renko_data, self.symbol, self.renko_range)
        except Exception as e:
            print(e)

    def renko_cal(self, last_price):
        self.tickqty+=1
        if self.renko_data.bidclose.iloc[-1]>self.renko_data.bidclose.iloc[-2]:
            brick_color=1
        else:
            brick_color=0

        past_closed_price=self.renko_data.bidclose.iloc[-1]
        past_opened_price=self.renko_data.bidopen.iloc[-1]
        temp_renko_data_list=[]

        if brick_color==1:
            if last_price>=past_closed_price+self.renko_range:
                past_opened_price=past_closed_price
                past_closed_price=past_opened_price+self.renko_range
                brick_color=1
                renko_date=datetime.datetime.now()
                renko_close_price=past_closed_price
                renko_open_price=past_opened_price
                renko_high_price=past_closed_price
                renko_low_price=past_opened_price
                temp_renko_data_list.append(renko_date, renko_close_price, renko_open_price, renko_high_price, renko_low_price, self.tickqty)
                self.renko_data.loc[len(self.renko_data)]=temp_renko_data_list
                self.db.insert_into_price_data_renko_table(self.renko_data[-3:], self.symbol, self.renko_range)
                self.tickqty=0

            elif last_price<=past_opened_price-self.renko_range:
                past_opened_price=past_opened_price
                past_closed_price=past_opened_price-self.renko_range
                brick_color=0
                renko_date=datetime.datetime.now()
                renko_close_price=past_closed_price
                renko_open_price=past_opened_price
                renko_high_price=past_opened_price
                renko_low_price=past_closed_price
                temp_renko_data_list.append(renko_date, renko_close_price, renko_open_price, renko_high_price, renko_low_price, self.tickqty)
                self.renko_data.loc[len(self.renko_data)]=temp_renko_data_list
                self.db.insert_into_price_data_renko_table(self.renko_data[-3:], self.symbol, self.renko_range)
                self.tickqty=0
        else:
            if last_price>=past_opened_price+(self.renko_range):
                past_opened_price=past_opened_price
                past_closed_price=past_opened_price+self.renko_range
                brick_color=1
                renko_date=datetime.datetime.now()
                renko_close_price=past_closed_price
                renko_open_price=past_opened_price
                renko_high_price=past_closed_price
                renko_low_price=past_opened_price
                temp_renko_data_list.append(renko_date, renko_close_price, renko_open_price, renko_high_price, renko_low_price, self.tickqty)
                self.renko_data.loc[len(self.renko_data)]=temp_renko_data_list
                self.db.insert_into_price_data_renko_table(self.renko_data[-3:], self.symbol, self.renko_range)
                self.tickqty=0
                
            elif last_price<=past_closed_price-self.renko_range:
                past_opened_price=past_closed_price
                past_closed_price=past_opened_price-self.renko_range
                brick_color=0
                renko_date=datetime.datetime.now()
                renko_close_price=past_closed_price
                renko_open_price=past_opened_price
                renko_high_price=past_opened_price
                renko_low_price=past_closed_price
                temp_renko_data_list=(renko_date, renko_close_price, renko_open_price, renko_high_price, renko_low_price, self.tickqty)
                self.renko_data.loc[len(self.renko_data)]=temp_renko_data_list
                self.db.insert_into_price_data_renko_table(self.renko_data[-3:], self.symbol, self.renko_range)
                self.tickqty=0


    def check_renko_con(self, data, dataframe):
        self.renko_cal(data['Rates'][0])
        self.check_condition()
        self.shared_memory_dict['strategy_status']='Running'


    def start_process(self):
        if self.process_status()==False and self.shared_memory_dict['stop_signal']==True:
            last_start=str(datetime.datetime.now())
            self.shared_memory_dict['stop_signal']=False
            self.shared_memory_dict['strategy_status']='Initializing'
            self.shared_memory_dict['last_start']=last_start
            self.fxcm_instance=fxcm_controller.Fxcm()
            self.init_strategy()
            return True
        else:
            self.shared_memory_dict['stop_signal']=False
            return False
            

    def stop(self):
        self.shared_memory_dict['stop_signal']=True
        self.shared_memory_dict['last_stop']=str(datetime.datetime.now())
        self.shared_memory_dict['strategy_status']='Stopped'

    def delete(self):
        if self.is_alive():
            self.stop()

    def process_status(self):
        return self.is_alive()

                
    def run(self):
        try:
            self.fxcm_instance=fxcm_controller.Fxcm()
            def fxcm_reconnect_in_process():
                try:
                    if self.fxcm_instance.connection==None or self.fxcm_instance.connection.is_connected()!=True:
                        self.shared_memory_dict['strategy_status']='Connecting to server'
                        self.fxcm_instance.connect(self.strategy_name)
                        if self.fxcm_instance.connection_status=='Connected':
                            self.shared_memory_dict['strategy_status']='Connected'
                except:
                    self.shared_memory_dict['strategy_status']='Connection issue'
                    self.fxcm_instance.connect(self.strategy_name)
                    if self.fxcm_instance.connection_status=='Connected':
                        self.shared_memory_dict['strategy_status']='Connected'

            try:
                while True:
                    if self.shared_memory_dict['stop_signal']==True:
                        break
                    else:
                        self.shared_memory_dict['strategy_status']='Connecting to server'
                        self.fxcm_instance.connect(self.strategy_name)
                        if self.fxcm_instance.connection_status=='Connected' and self.fxcm_instance.connection.is_connected()==True:
                            self.shared_memory_dict['strategy_status']='Connected'
                            break
                        else:
                            time.sleep(30)
            except Exception as e:
                self.shared_memory_dict['strategy_status']='Connection issue'


            if len(self.timeframe)>4:
                symbol_temp=list(self.symbol)
                symbol_temp.insert(3, '/')
                symbol_temp=''.join(symbol_temp)
                self.renko_range=int(self.timeframe[6:])
                self.ticks=None
                self.tickqty=0
                self.renko_data=pd.DataFrame()
                self.renko_cal_init()
                self.fxcm_instance.connection.subscribe_market_data(symbol_temp, (self.check_renko_con))
            else:
                self.fxcm_instance.get_price_data(self.symbol, self.timeframe)
                while True:
                    if self.shared_memory_dict['stop_signal']==True:
                        break
                    elif datetime.datetime.now().second==0:
                        try:
                            if self.fxcm_instance.connection.is_connected()==True:
                                try:
                                    candle_result=self.fxcm_instance.get_price_data(self.symbol, self.timeframe, 500)
                                    if candle_result==True:
                                        self.shared_memory_dict['strategy_status']='Checking condition'
                                        self.check_condition()
                                        self.shared_memory_dict['strategy_status']='Running'
                                    else:
                                        self.shared_memory_dict['strategy_status']='Connection issue'
                                        fxcm_reconnect_in_process()
                                except Exception as e:
                                    self.shared_memory_dict['strategy_status']='Connection issue'
                                    fxcm_reconnect_in_process()
                            else:
                                self.shared_memory_dict['strategy_status']='Connection issue'
                                fxcm_reconnect_in_process()
                        except Exception as e:
                            print(e, 'in process')
                            self.shared_memory_dict['strategy_status']='Connection issue'
                            fxcm_reconnect_in_process()
                    time.sleep(0.3)
        except Exception as e:
            print(e)

