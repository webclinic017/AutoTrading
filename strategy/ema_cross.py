import pandas as pd
import os, glob, sys, inspect
import numpy as np

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
from indicators import r_percent, cmf, ema
from db_controller import Db_Controller

import warnings
warnings.filterwarnings("ignore")

pd.options.mode.chained_assignment = None
np.seterr(divide='ignore', invalid='ignore')

strategy_name='EMA cross'

strategy_description="""



EMA cross is a simple strategy based on EMA indicator.


It calculates two EMAs for two specified loopback period, and considers one as long ema which is calculated based on higher 
period and another one as short ema which is calculated based on lower period.


Entry conditions:


if EMA short crosses above EMA long, then singal buy
if EMA short crosses below EMA long, then singal sell
Exit conditions:


if the position is buy, EMA short crosses below EMA long, then signal exit
if the position is sell, EMA short crosses above EMA long, then signal exit
"""

inputs_name_dict={
                'EMA long':['ema_1_period', 21],
                'EMA short':['ema_2_period', 13],
                }


class ema_cross:
    def __init__(self, symbol, timeframe, ema_1_period, ema_2_period):
        self.symbol=symbol
        self.timeframe=timeframe
        self.ema_1_period=int(ema_1_period)
        self.ema_2_period=int(ema_2_period)
        self.data=pd.DataFrame()
        self.required_score=10
        self.conditions_weights={'ema':10}
        self.condictions_state={
                                'buy':{
                                        'ema':False,
                                        },
                                'sell':{
                                        'ema':False
                                        }
                                }



    def get_data(self):
        quantity=2*max(self.ema_1_period, self.ema_2_period)
        self.db=Db_Controller()
        if len(self.timeframe)>4:
            self.renko_range=int(self.timeframe[6:])
            self.data=self.db.query_price_data_renko(self.symbol, self.renko_range, quantity)
        else:
            self.data=self.db.query_price_data(self.symbol, self.timeframe, quantity)



    def check_exit(self, current_position):
        try:
            self.get_data()
            self.data['ema_1']=ema(list(self.data.bidclose), self.ema_1_period)
            self.data['ema_2']=ema(list(self.data.bidclose), self.ema_2_period)

            if current_position=='buy':
                if ((self.data.ema_1.iloc[-1]>self.data.ema_2.iloc[-1])):
                    self.condictions_state['sell']['ema']=True
                    self.condictions_state['buy']['ema']=False
                    return 'exit'
            elif current_position=='sell':
                if ((self.data.ema_1.iloc[-1]<self.data.ema_2.iloc[-1])):
                    self.condictions_state['buy']['ema']=True
                    self.condictions_state['sell']['ema']=False
                    return 'exit'
            else:
                self.condictions_state['buy']['ema']=False
                self.condictions_state['sell']['ema']=False
                return None
        except Exception as e:
            print(e, 454545)



    def check_entry(self):
        try:
            self.get_data()
            self.data['ema_1']=ema(list(self.data.bidclose), self.ema_1_period)
            self.data['ema_2']=ema(list(self.data.bidclose), self.ema_2_period)

            if ((self.data.ema_1.iloc[-1]>self.data.ema_2.iloc[-1])):
                    self.condictions_state['sell']['ema']=True
                    self.condictions_state['buy']['ema']=False
            elif ((self.data.ema_1.iloc[-1]<self.data.ema_2.iloc[-1])):
                    self.condictions_state['buy']['ema']=True
                    self.condictions_state['sell']['ema']=False
            else:
                self.condictions_state['buy']['ema']=False
                self.condictions_state['sell']['ema']=False
            
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
            print(e, 98555555986668)
            return None

    def backtest_exit(self, current_position, data):
        try:
            self.condictions_state_backtest={
                                            'buy':{
                                                    'ema':False,
                                                    },
                                            'sell':{
                                                    'ema':False,
                                                    }
                                            }

            
            if len(data.date)>max(self.ema_1_period, self.ema_2_period):
                data['ema_1']=ema(list(data.bidclose), self.ema_1_period)
                data['ema_2']=ema(list(data.bidclose), self.ema_2_period)

                if current_position=='buy':
                    if ((data.ema_1.iloc[-1]>data.ema_2.iloc[-1])):
                        self.condictions_state_backtest['sell']['ema']=True
                        self.condictions_state_backtest['buy']['ema']=False
                        return 'exit'
                elif current_position=='sell':    
                    if ((data.ema_1.iloc[-1]<data.ema_2.iloc[-1])):
                        self.condictions_state_backtest['buy']['ema']=True
                        self.condictions_state_backtest['sell']['ema']=False
                        return 'exit'
                else:
                    self.condictions_state_backtest['buy']['ema']=False
                    self.condictions_state_backtest['sell']['ema']=False
                    return None
            else:
                return None

        except:
            return None
                    

    def backtest_entry(self, data):
        try:
            self.condictions_state_backtest={
                                            'buy':{
                                                    'ema':False,
                                                    },
                                            'sell':{
                                                    'ema':False,
                                                    }
                                            }

            
            if len(data.date)>max(self.ema_1_period, self.ema_2_period):
                data['ema_1']=ema(list(data.bidclose), self.ema_1_period)
                data['ema_2']=ema(list(data.bidclose), self.ema_2_period)


                if ((data.ema_1.iloc[-1]>data.ema_2.iloc[-1])):
                    self.condictions_state_backtest['sell']['ema']=True
                    self.condictions_state_backtest['buy']['ema']=False
                elif ((data.ema_1.iloc[-1]<data.ema_2.iloc[-1])):
                    self.condictions_state_backtest['buy']['ema']=True
                    self.condictions_state_backtest['sell']['ema']=False
                else:
                    self.condictions_state_backtest['buy']['ema']=False
                    self.condictions_state_backtest['sell']['ema']=False
                    
                self.required_score
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
