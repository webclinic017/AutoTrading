import pandas as pd
import os, glob, sys, inspect
import numpy as np

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
from indicators import r_percent, cmf, ema, sma
from db_controller import Db_Controller

import warnings
warnings.filterwarnings("ignore")

pd.options.mode.chained_assignment = None
np.seterr(divide='ignore', invalid='ignore')

strategy_name='MA Crossing Renko'

strategy_description="""



MA Crossing Renko
"""

inputs_name_dict={
                'EMA Entry':['ma_entry_period', 20],
                'SMA Exit':['ma_exit_period', 50],
                'EMA Long Term':['ma_long_term_period', 100],
                }


class ma_crossing_renko:
    def __init__(self, symbol, timeframe, ma_entry_period, ma_exit_period, ma_long_term_period):
        self.symbol=symbol
        self.timeframe=timeframe
        self.ma_entry_period=int(ma_entry_period)
        self.ma_exit_period=int(ma_exit_period)
        self.ma_long_term_period=int(ma_long_term_period)
        self.data=pd.DataFrame()
        self.required_score=10
        self.conditions_weights={'ma':10}
        self.condictions_state={
                                'buy':{
                                        'ma':False,
                                        },
                                'sell':{
                                        'ma':False
                                        }
                                }



    def get_data(self):
        quantity=2*max(self.ma_entry_period, self.ma_exit_period, self.ma_long_term_period)
        self.db=Db_Controller()
        if len(self.timeframe)>4:
            self.renko_range=int(self.timeframe[6:])
            self.data=self.db.query_price_data_renko(self.symbol, self.renko_range, quantity)
        else:
            self.data=self.db.query_price_data(self.symbol, self.timeframe, quantity)



    def check_exit(self, current_position):
        try:
            self.get_data()
            self.data['ma_entry']=ema(list(self.data.bidclose), self.ma_entry_period)
            self.data['ma_exit']=sma(list(self.data.bidclose), self.ma_exit_period)

            if current_position=='buy':
                if ((self.data.bidclose.iloc[-2]<self.data.ma_exit.iloc[-2] and self.data.bidclose.iloc[-1]>self.data.ma_exit.iloc[-1])):
                    self.condictions_state['sell']['ma']=True
                    self.condictions_state['buy']['ma']=False
                    return 'exit'
            elif current_position=='sell':
                if ((self.data.bidclose.iloc[-2]>self.data.ma_exit.iloc[-2] and self.data.bidclose.iloc[-1]<self.data.ma_exit.iloc[-1])):
                    self.condictions_state['buy']['ma']=True
                    self.condictions_state['sell']['ma']=False
                    return 'exit'
            else:
                self.condictions_state['buy']['ma']=False
                self.condictions_state['sell']['ma']=False
                return None
        except Exception as e:
            print(e, 454545)



    def check_entry(self):
        try:
            self.get_data()
            self.data['ma_entry']=ema(list(self.data.bidclose), self.ma_entry_period)
            self.data['ma_exit']=sma(list(self.data.bidclose), self.ma_exit_period)
            self.data['ma_long_term']=ema(list(self.data.bidclose), self.ma_long_term_period)


            if ((self.data.bidclose.iloc[-1]>self.data.ma_long_term.iloc[-1] and self.data.bidclose.iloc[-3]<self.data.ma_entry.iloc[-3] and self.data.bidclose.iloc[-2]>self.data.ma_entry.iloc[-2] and self.data.bidclose.iloc[-1]>self.data.bidclose.iloc[-2])):
                    self.condictions_state['sell']['ma']=True
                    self.condictions_state['buy']['ma']=False
            elif ((self.data.bidclose.iloc[-1]<self.data.ma_long_term.iloc[-1] and self.data.bidclose.iloc[-3]>self.data.ma_entry.iloc[-3] and self.data.bidclose.iloc[-2]>self.data.ma_entry.iloc[-2] and self.data.bidclose.iloc[-1]<self.data.bidclose.iloc[-2])):
                    self.condictions_state['buy']['ma']=True
                    self.condictions_state['sell']['ma']=False
            else:
                self.condictions_state['buy']['ma']=False
                self.condictions_state['sell']['ma']=False
            
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
                                                    'ma':False,
                                                    },
                                            'sell':{
                                                    'ma':False,
                                                    }
                                            }

            
            if len(data.date)>max(self.ma_entry_period, self.ma_long_term_period):
                data['ma_entry']=ema(list(self.data.bidclose), self.ma_entry_period)
                data['ma_exit']=sma(list(self.data.bidclose), self.ma_exit_period)

                if current_position=='buy':
                    if ((data.ema_exit.iloc[-1]>data.bidclose.iloc[-1])):
                        self.condictions_state_backtest['sell']['ma']=True
                        self.condictions_state_backtest['buy']['ma']=False
                        return 'exit'
                elif current_position=='sell':    
                    if ((data.ema_exit.iloc[-1]<data.bidclose.iloc[-1])):
                        self.condictions_state_backtest['buy']['ma']=True
                        self.condictions_state_backtest['sell']['ma']=False
                        return 'exit'
                else:
                    self.condictions_state_backtest['buy']['ma']=False
                    self.condictions_state_backtest['sell']['ma']=False
                    return None
            else:
                return None

        except:
            return None
                    

    def backtest_entry(self, data):
        try:
            self.condictions_state_backtest={
                                            'buy':{
                                                    'ma':False,
                                                    },
                                            'sell':{
                                                    'ma':False,
                                                    }
                                            }

            
            if len(data.date)>max(self.ma_entry_period, self.ma_exit_period, self.ma_long_term_period):
                data['ma_entry']=ema(list(self.data.bidclose), self.ma_entry_period)
                data['ma_exit']=sma(list(self.data.bidclose), self.ma_exit_period)
                data['ma_long_term']=ema(list(self.data.bidclose), self.ma_long_term_period)


                if ((data.bidclose.iloc[-1]>data.ma_long_term.iloc[-1] and data.bidclose.iloc[-3]<data.ma_entry.iloc[-3] and data.bidclose.iloc[-2]>data.ma_entry.iloc[-2] and data.bidclose.iloc[-1]>data.bidclose.iloc[-2])):
                        self.condictions_state['sell']['ma']=True
                        self.condictions_state['buy']['ma']=False
                elif ((data.bidclose.iloc[-1]<data.ma_long_term.iloc[-1] and data.bidclose.iloc[-3]>data.ma_entry.iloc[-3] and data.bidclose.iloc[-2]>data.ma_entry.iloc[-2] and data.bidclose.iloc[-1]<data.bidclose.iloc[-2])):
                        self.condictions_state['buy']['ma']=True
                        self.condictions_state['sell']['ma']=False
                else:
                    self.condictions_state['buy']['ma']=False
                    self.condictions_state['sell']['ma']=False
                    
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
