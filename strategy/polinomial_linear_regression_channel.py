import pandas as pd
import os, glob, sys, inspect
import numpy as np

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
from indicators import r_percent, cmf, ema, polinomial_linear_regression_channel_indicator
from db_controller import Db_Controller

import warnings
warnings.filterwarnings("ignore")

pd.options.mode.chained_assignment = None
np.seterr(divide='ignore', invalid='ignore')

strategy_name='Polinomial Linear Regression Channel'

strategy_description="""



Polinomial Linear Regression Channel strategy works based on identifying potential price channels and trading the channel. 
It uses linear regression channel indicator to calculate linear regresion and its upper and lower channel based on specified 
standard deviation for a specified loopback period.

This strategy uses four linear regression channel based on four different setting to find channel in four different 
periods. Three of them are used for entry and one for exit
It also uses CMF and %R William as confirmation indicator.



The conditions is as follow:



Entry conditions:


Thes conditions are checked if there is no open postion created by this strategy. 
if the price is above one of the three upper channels and cmf is below zero and %R William has crossed below -20, then signal sell
if the price is below one of the three lower channels and cmf is above zero and %R William has crossed above -80, then signal buy


Exit conditions:


if the position is buy, and price is above upper channel of exit linear regression, then signal exit
if the position is sell, and price is below lower channel of exit linear regression, then signal exit

"""

inputs_name_dict={
                'Linear regression 1 standard deviation':['lrc_std_1', 2.2],
                'Linear regression 1 degree':['lrc_degree_1', 3],
                'Linear regression 1 period':['lrc_period_1', 400],
                'Linear regression 2 standard deviation':['lrc_std_2', 2.2],
                'Linear regression 2 degree':['lrc_degree_2', 3],
                'Linear regression 2 period':['lrc_period_2', 200],
                'Linear regression 3 standard deviation':['lrc_std_3', 2.2],
                'Linear regression 3 degree':['lrc_degree_3', 3],
                'Linear regression 3 period':['lrc_period_3', 100],
                'Linear regression exit standard deviation':['lrc_std_exit', 2],
                'Linear regression exit degree':['lrc_degree_exit', 3],
                'Linear regression exit period':['lrc_period_exit', 400],
                'CMF period':['cmf_period', 3],
                'CMF EMA period':['cmf_ma_period', 5],
                'William %R period':['r_percent_period', 5]
                }


class polinomial_linear_regression_channel:
    def __init__(self, symbol, timeframe, lrc_std_1, lrc_degree_1, lrc_period_1, lrc_std_2, lrc_degree_2, lrc_period_2, lrc_std_3, lrc_degree_3, lrc_period_3, lrc_std_exit, lrc_degree_exit, lrc_period_exit, cmf_period, cmf_ma_period, r_percent_period):
        self.symbol=symbol
        self.timeframe=timeframe
        self.lrc_std_1=lrc_std_1
        self.lrc_degree_1=lrc_degree_1
        self.lrc_period_1=int(lrc_period_1)
        self.lrc_std_2=lrc_std_2
        self.lrc_degree_2=lrc_degree_1
        self.lrc_period_2=int(lrc_period_2)
        self.lrc_std_3=lrc_std_3
        self.lrc_degree_3=lrc_degree_1
        self.lrc_period_3=int(lrc_period_3)
        self.lrc_std_exit=lrc_std_exit
        self.lrc_degree_exit=lrc_degree_1
        self.lrc_period_exit=int(lrc_period_exit)
        self.cmf_period=int(cmf_period)
        self.cmf_ma_period=int(cmf_ma_period)
        self.r_percent_period=int(r_percent_period)
        self.data=pd.DataFrame()
        self.required_score=30
        self.conditions_weights={'linear_regression_channel':10, 'r_percent':10, 'cmf':10}
        self.condictions_state={
                                'buy':{
                                        'linear_regression_channel':False,
                                        'r_percent':False,
                                        'cmf':False
                                        },
                                'sell':{
                                        'linear_regression_channel':False,
                                        'r_percent':False,
                                        'cmf':False
                                        }
                                }



    def get_data(self):
        quantity=2*max(self.lrc_period_1, self.lrc_period_2, self.lrc_period_3)
        self.db=Db_Controller()
        if len(self.timeframe)>4:
            self.renko_range=int(self.timeframe[6:])
            self.data=self.db.query_price_data_renko(self.symbol, self.renko_range, quantity)
        else:
            self.data=self.db.query_price_data(self.symbol, self.timeframe, quantity)



    def check_exit(self, current_position):
        try:
            self.get_data()
            linear_regression_exit, upper_line_exit, lower_line_exit, slope_exit, channel_width_exit=polinomial_linear_regression_channel_indicator(self.data, self.lrc_period_exit, self.lrc_degree_exit, self.lrc_std_exit)
            self.data['cmf']=cmf(list(self.data.bidclose), list(self.data.bidhigh), list(self.data.bidlow), list(self.data.tickqty), self.cmf_period)
            self.data['cmf_ma']=ema(list(self.data.cmf), self.cmf_ma_period)
            self.data['r_percent']=r_percent(self.data, self.r_percent_period)

            if current_position=='buy':
                if ((self.data.bidclose.iloc[-1]>upper_line_exit[-1])):
                    self.condictions_state['sell']['linear_regression_channel']=True
                    self.condictions_state['buy']['linear_regression_channel']=False
                    return 'exit'
            elif current_position=='sell':
                if ((self.data.bidclose.iloc[-1]<lower_line_exit[-1])):
                    self.condictions_state['buy']['linear_regression_channel']=True
                    self.condictions_state['sell']['linear_regression_channel']=False
                    return 'exit'
            else:
                self.condictions_state['buy']['linear_regression_channel']=False
                self.condictions_state['sell']['linear_regression_channel']=False
                return None
        except Exception as e:
            print(e)
            return None




    def check_entry(self):
        try:
            self.get_data()
            linear_regression_1, upper_line_1, lower_line_1, slope_1, channel_width_1=polinomial_linear_regression_channel_indicator(self.data, self.lrc_period_1, self.lrc_degree_1, self.lrc_std_1)
            linear_regression_2, upper_line_2, lower_line_2, slope_2, channel_width_2=polinomial_linear_regression_channel_indicator(self.data, self.lrc_period_2, self.lrc_degree_2, self.lrc_std_2)
            linear_regression_3, upper_line_3, lower_line_3, slope_3, channel_width_3=polinomial_linear_regression_channel_indicator(self.data, self.lrc_period_3, self.lrc_degree_3, self.lrc_std_3)
            self.data['cmf']=cmf(list(self.data.bidclose), list(self.data.bidhigh), list(self.data.bidlow), list(self.data.tickqty), self.cmf_period)
            self.data['cmf_ma']=ema(list(self.data.cmf), self.cmf_ma_period)
            self.data['r_percent']=r_percent(self.data, self.r_percent_period)

            if ((self.data.bidclose.iloc[-1]>upper_line_1[-1]) and (self.data.bidclose.iloc[-1]>upper_line_2[-1]) and (self.data.bidclose.iloc[-1]>upper_line_3[-1])):
                self.condictions_state_backtest['sell']['linear_regression_channel']=True
                self.condictions_state_backtest['buy']['linear_regression_channel']=False
            elif ((self.data.bidclose.iloc[-1]<lower_line_1[-1]) and (self.data.bidclose.iloc[-1]>upper_line_2[-1]) and (self.data.bidclose.iloc[-1]>upper_line_3[-1])):
                self.condictions_state['buy']['linear_regression_channel']=True
                self.condictions_state['sell']['linear_regression_channel']=False
            else:
                self.condictions_state['buy']['linear_regression_channel']=False
                self.condictions_state['sell']['linear_regression_channel']=False
                
            
            if self.data.r_percent.iloc[-2]>-20 and self.data.r_percent.iloc[-1]<-20:
                self.condictions_state['sell']['r_percent']=True
                self.condictions_state['buy']['r_percent']=False
            elif self.data.r_percent.iloc[-2]<-80 and self.data.r_percent.iloc[-1]>-80:
                self.condictions_state['buy']['r_percent']=True
                self.condictions_state['sell']['r_percent']=False
            else:
                self.condictions_state['buy']['r_percent']=False
                self.condictions_state['sell']['r_percent']=False
                
                
            if self.data.cmf.iloc[-1]>self.data.cmf_ma.iloc[-1]:
                self.condictions_state['sell']['cmf']=False
                self.condictions_state['buy']['cmf']=True
            else:
                self.condictions_state['sell']['cmf']=True
                self.condictions_state['buy']['cmf']=False
                
            
            collected_score_buy=0
            collected_score_sell=0
            for k, v in self.conditions_weights.items():
                if self.condictions_state['buy'][k]==True:
                    collected_score_buy+=v
                elif self.condictions_state['sell'][k]==True:
                    collected_score_sell+=v
                    
                                
            if collected_score_buy>=self.required_score:
                return 'buy'

            elif collected_score_sell>=self.required_score:
                return 'sell'

            else:
                return None

        except Exception as e:
            print(e, 9898989898)
            return None


    def backtest_exit(self, current_position, data):
        try:
            self.condictions_state_backtest={
                                            'buy':{'linear_regression_channel':False,
                                                    'r_percent':False,
                                                    'cmf':False
                                                    },
                                            'sell':{
                                                    'linear_regression_channel':False,
                                                    'r_percent':False,
                                                    'cmf':False
                                                    }
                                            }

            
            if len(data.date)>exit*2:
                data=data.iloc[(len(data.date)-(2*max(self.lrc_period_1, self.lrc_period_2, self.lrc_period_3))):]
                linear_regression_exit, upper_line_exit, lower_line_exit, slope_exit, channel_width_exit=polinomial_linear_regression_channel_indicator(data, self.lrc_period_exit, self.lrc_degree_exit, self.lrc_std_exit)
                data['cmf']=cmf(list(data.bidclose), list(data.bidhigh), list(data.bidlow), list(data.tickqty), self.cmf_period)
                data['cmf_ma']=ema(list(data.cmf), self.cmf_ma_period)
                data['r_percent']=r_percent(data, self.r_percent_period)

                if current_position=='buy':
                    if ((data.bidclose.iloc[-1]>upper_line_exit[-1])):
                        self.condictions_state_backtest['sell']['linear_regression_channel']=True
                        self.condictions_state_backtest['buy']['linear_regression_channel']=False
                        return 'exit'
                elif current_position=='sell':    
                    if ((data.bidclose.iloc[-1]<lower_line_exit[-1])):
                        self.condictions_state_backtest['buy']['linear_regression_channel']=True
                        self.condictions_state_backtest['sell']['linear_regression_channel']=False
                        return 'exit'
                else:
                    self.condictions_state_backtest['buy']['linear_regression_channel']=False
                    self.condictions_state_backtest['sell']['linear_regression_channel']=False
                    return None
            else:
                return None
        except:
            return None

    def backtest_entry(self, data):
        try:
            self.condictions_state_backtest={
                                            'buy':{'linear_regression_channel':False,
                                                    'r_percent':False,
                                                    'cmf':False
                                                    },
                                            'sell':{
                                                    'linear_regression_channel':False,
                                                    'r_percent':False,
                                                    'cmf':False
                                                    }
                                            }

            
            if len(data.date)>max(self.lrc_period_1, self.lrc_period_2, self.lrc_period_3):
                data=data.iloc[(len(data.date)-(2*max(self.lrc_period_1, self.lrc_period_2, self.lrc_period_3))):]
                linear_regression_1, upper_line_1, lower_line_1, slope_1, channel_width_1=polinomial_linear_regression_channel_indicator(data, self.lrc_period_1, self.lrc_degree_1, self.lrc_std_1)
                linear_regression_2, upper_line_2, lower_line_2, slope_2, channel_width_2=polinomial_linear_regression_channel_indicator(data, self.lrc_period_2, self.lrc_degree_2, self.lrc_std_2)
                linear_regression_3, upper_line_3, lower_line_3, slope_3, channel_width_3=polinomial_linear_regression_channel_indicator(data, self.lrc_period_3, self.lrc_degree_3, self.lrc_std_3)
                data['cmf']=cmf(list(data.bidclose), list(data.bidhigh), list(data.bidlow), list(data.tickqty), self.cmf_period)
                data['cmf_ma']=ema(list(data.cmf), self.cmf_ma_period)
                data['r_percent']=r_percent(data, self.r_percent_period)


                if ((data.bidclose.iloc[-1]>upper_line_1[-1]) and (data.bidclose.iloc[-1]>upper_line_2[-1]) and (data.bidclose.iloc[-1]>upper_line_3[-1])):
                    self.condictions_state_backtest['sell']['linear_regression_channel']=True
                    self.condictions_state_backtest['buy']['linear_regression_channel']=False
                elif ((data.bidclose.iloc[-1]<lower_line_1[-1]) and (data.bidclose.iloc[-1]>upper_line_2[-1]) and (data.bidclose.iloc[-1]>upper_line_3[-1])):
                    self.condictions_state_backtest['buy']['linear_regression_channel']=True
                    self.condictions_state_backtest['sell']['linear_regression_channel']=False
                else:
                    self.condictions_state_backtest['buy']['linear_regression_channel']=False
                    self.condictions_state_backtest['sell']['linear_regression_channel']=False
                    
                
                if data.r_percent.iloc[-2]>-10 and data.r_percent.iloc[-1]<-20:
                    self.condictions_state_backtest['sell']['r_percent']=True
                    self.condictions_state_backtest['buy']['r_percent']=False
                elif data.r_percent.iloc[-2]<-90 and data.r_percent.iloc[-1]>-80:
                    self.condictions_state_backtest['buy']['r_percent']=True
                    self.condictions_state_backtest['sell']['r_percent']=False
                else:
                    self.condictions_state_backtest['buy']['r_percent']=False
                    self.condictions_state_backtest['sell']['r_percent']=False
                    
                    
                if data.cmf.iloc[-1]>data.cmf_ma.iloc[-1]:
                    self.condictions_state_backtest['sell']['cmf']=False
                    self.condictions_state_backtest['buy']['cmf']=True
                else:
                    self.condictions_state_backtest['sell']['cmf']=True
                    self.condictions_state_backtest['buy']['cmf']=False
                    
                
                collected_score_buy=0
                collected_score_sell=0
                for k, v in self.conditions_weights.items():
                    if self.condictions_state_backtest['buy'][k]==True:
                        collected_score_buy+=v
                    elif self.condictions_state_backtest['sell'][k]==True:
                        collected_score_sell+=v
                        
                                    
                if collected_score_buy>=self.required_score:
                    return 'buy'

                elif collected_score_sell>=self.required_score:
                    return 'sell'

                else:
                    return None

            else:
                return None

        except Exception as e:
            print(e, 11111111111111)
            return None
