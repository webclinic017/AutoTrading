import pandas as pd
import os, glob, sys, inspect
import numpy as np
from sklearn import svm
from sklearn.neural_network import MLPClassifier, MLPRegressor

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
from indicators import r_percent, cmf, ema, sma
from db_controller import Db_Controller

import warnings
warnings.filterwarnings("ignore")

pd.options.mode.chained_assignment = None
np.seterr(divide='ignore', invalid='ignore')

strategy_name='Machine learning based strategy using cmf, %R, EMA'

strategy_description="""



Machine learning based strategy using cmf, %R, EMA

"""

inputs_name_dict={
                'Lag':['lag', 3],
                'William %R period':['r_percent_period', 55],
                'William %R short period':['r_percent_short_period', 8],
                'CMF period':['cmf_period', 55],
                'EMA period':['ema_period', 55],
                'EMA short period':['ema_short_period', 21],
                'EMA long period':['ema_long_period', 100],
                'SMA Long period':['sma_long_period', 100],
                'Entry confirmaiton number':['entry_confirmation_number', 1],
                'Exit confirmaiton number':['exit_confirmation_number', 5],
                }


class ml_williamR_cmf_ema:
    def __init__(self, symbol, timeframe, lag, r_percent_period, r_percent_short_period, cmf_period, ema_period, ema_short_period, ema_long_period, sma_long_period, entry_confirmation_number, exit_confirmation_number):
        self.symbol=symbol
        self.timeframe=timeframe
        self.lag=int(lag)
        self.r_percent_period=int(r_percent_period)
        self.r_percent_short_period=int(r_percent_short_period)
        self.cmf_period=int(cmf_period)
        self.ema_period=int(ema_period)
        self.ema_short_period=int(ema_short_period)
        self.ema_long_period=int(ema_long_period)
        self.sma_long_period=int(sma_long_period)
        self.entry_confirmation_number=int(entry_confirmation_number)
        self.exit_confirmation_number=int(exit_confirmation_number)
        self.entry_confirmation_buy_counter=0
        self.entry_confirmation_sell_counter=0
        self.exit_confirmation_buy_counter=0
        self.exit_confirmation_sell_counter=0
        self.entry_confirmation_counter_buy_backtest=0
        self.entry_confirmation_counter_sell_backtest=0
        self.exit_confirmation_counter_buy_backtest=0
        self.exit_confirmation_counter_sell_backtest=0        
        self.data=pd.DataFrame()
        self.model=None



    def get_data(self):
        quantity=10000
        self.db=Db_Controller()
        if len(self.timeframe)>4:
            self.renko_range=int(self.timeframe[6:])
            self.data=self.db.query_price_data_renko(self.symbol, self.renko_range, quantity)
        else:
            self.data=self.db.query_price_data(self.symbol, self.timeframe, quantity)



    def check_exit(self, current_position):
        try:
            self.get_data()
            columns=[]
            data=pd.DataFrame(self.data[['bidclose', 'askclose']].mean(axis=1), columns=['midclose'])
            data['tickqty']=self.data.tickqty
            data['wr']=r_percent(self.data, self.r_percent_period)
            data['wr_short']=r_percent(self.data, self.r_percent_short_period)
            data['cmf']=cmf(list(self.data.bidclose), list(self.data.bidhigh), list(self.data.bidlow), list(self.data.tickqty), self.cmf_period)
            data['ema']=ema(list(self.data.bidclose), self.ema_period)
            data['ema_short']=ema(list(self.data.bidclose), self.ema_short_period)
            data['ema_long']=ema(list(self.data.bidclose), self.ema_long_period)
            data['sma_long']=sma(list(self.data.bidclose), self.sma_long_period)

            data['wr_1']=data['wr'].copy()
            data['wr_short_1']=data['wr_short'].copy()
            data['cmf_1']=data['cmf'].copy()
            data['ema_1']=data['ema'].copy()
            data['ema_short_1']=data['ema_short'].copy()
            data['ema_long_1']=data['ema_long'].copy()
            data['sma_long_1']=data['sma_long'].copy()

            columns=[]

            data['returns']=np.log(data.midclose)-np.log(data.midclose.shift(1))
            data['tick_lag']=np.log(data.tickqty)-np.log(data.tickqty.shift(1))
            data['cmf_lag']=data.cmf_1-data.cmf_1.shift(1)
            data['sma_long_lag']=np.log(data.sma_long_1)-np.log(data.sma_long_1.shift(1))
            data['ema_lag']=np.log(data.ema_1)-np.log(data.ema_1.shift(1))
            data['ema_short_lag']=np.log(data.ema_short_1)-np.log(data.ema_short_1.shift(1))
            data['ema_long_lag']=np.log(data.ema_long_1)-np.log(data.ema_long_1.shift(1))
            data['wr_lag']=data.wr_1-data.wr_1.shift(1)
            data['wr_short_lag']=data.wr_short_1-data.wr_short_1.shift(1)
            

            for i in range(1, self.lag+1):
                column='lag_'+str(i)
                data[column]=data['returns'].shift(i)
                columns.append(column)

                column='tick_lag_'+str(i)
                data[column]=data['tick_lag'].shift(i)
                columns.append(column)
                
                column='cmf_lag_'+str(i)
                data[column]=data['cmf_lag'].shift(i)
                columns.append(column)
                
                column='sma_long_lag_'+str(i)
                data[column]=data['sma_long_lag'].shift(i)
                columns.append(column)
                
                column='ema_lag_'+str(i)
                data[column]=data['ema_lag'].shift(i)
                columns.append(column)

                column='wr_lag_'+str(i)
                data[column]=data['wr_lag'].shift(i)
                columns.append(column)

                column='wr_short_lag_'+str(i)
                data[column]=data['wr_short_lag'].shift(i)
                columns.append(column)

                column='ema_short_lag_'+str(i)
                data[column]=data['ema_short_lag'].shift(i)
                columns.append(column)
                
                column='ema_long_lag_'+str(i)
                data[column]=data['ema_long_lag'].shift(i)
                columns.append(column)
                
            data.dropna(inplace=True)
            
            if self.model==None:
                self.model = MLPClassifier(solver='adam', alpha=0.0000001, learning_rate='adaptive',
                                        hidden_layer_sizes=(10, 3), random_state=1, activation='relu')
                self.model.fit(np.sign(data[columns]), np.sign(data['returns']))
            prediction=self.model.predict(np.sign(data[columns]))[-1]

            if current_position=='buy' and prediction<0:
                if self.exit_confirmation_buy_counter==self.exit_confirmation_number:
                    self.exit_confirmation_buy_counter=0
                    self.exit_confirmation_sell_counter=0
                    return 'exit'
                else:
                    self.exit_confirmation_buy_counter+=1
                    self.exit_confirmation_sell_counter=0
            elif current_position=='sell' and prediction>0:
                if self.exit_confirmation_sell_counter==self.exit_confirmation_number:
                    self.exit_confirmation_sell_counter=0
                    self.exit_confirmation_buy_counter=0
                    return 'exit'
                else:
                    self.exit_confirmation_sell_counter+=1
                    self.exit_confirmation_buy_counter=0
            else:
                self.exit_confirmation_sell_counter=0
                self.exit_confirmation_buy_counter=0
                return None
        except Exception as e:
            print(e)
            return None

    def check_entry(self):
        try:
            self.get_data()
            columns=[]
            data=pd.DataFrame(self.data[['bidclose', 'askclose']].mean(axis=1), columns=['midclose'])
            data['tickqty']=self.data.tickqty
            data['wr']=r_percent(self.data, self.r_percent_period)
            data['wr_short']=r_percent(self.data, self.r_percent_short_period)
            data['cmf']=cmf(list(self.data.bidclose), list(self.data.bidhigh), list(self.data.bidlow), list(self.data.tickqty), self.cmf_period)
            data['ema']=ema(list(self.data.bidclose), self.ema_period)
            data['ema_short']=ema(list(self.data.bidclose), self.ema_short_period)
            data['ema_long']=ema(list(self.data.bidclose), self.ema_long_period)
            data['sma_long']=sma(list(self.data.bidclose), self.sma_long_period)

            data['wr_1']=data['wr'].copy()
            data['wr_short_1']=data['wr_short'].copy()
            data['cmf_1']=data['cmf'].copy()
            data['ema_1']=data['ema'].copy()
            data['ema_short_1']=data['ema_short'].copy()
            data['ema_long_1']=data['ema_long'].copy()
            data['sma_long_1']=data['sma_long'].copy()

            columns=[]

            data['returns']=np.log(data.midclose)-np.log(data.midclose.shift(1))
            data['tick_lag']=np.log(data.tickqty)-np.log(data.tickqty.shift(1))
            data['cmf_lag']=data.cmf_1-data.cmf_1.shift(1)
            data['sma_long_lag']=np.log(data.sma_long_1)-np.log(data.sma_long_1.shift(1))
            data['ema_lag']=np.log(data.ema_1)-np.log(data.ema_1.shift(1))
            data['ema_short_lag']=np.log(data.ema_short_1)-np.log(data.ema_short_1.shift(1))
            data['ema_long_lag']=np.log(data.ema_long_1)-np.log(data.ema_long_1.shift(1))
            data['wr_lag']=data.wr_1-data.wr_1.shift(1)
            data['wr_short_lag']=data.wr_short_1-data.wr_short_1.shift(1)
            

            for i in range(1, self.lag+1):
                column='lag_'+str(i)
                data[column]=data['returns'].shift(i)
                columns.append(column)

                column='tick_lag_'+str(i)
                data[column]=data['tick_lag'].shift(i)
                columns.append(column)
                
                column='cmf_lag_'+str(i)
                data[column]=data['cmf_lag'].shift(i)
                columns.append(column)
                
                column='sma_long_lag_'+str(i)
                data[column]=data['sma_long_lag'].shift(i)
                columns.append(column)
                
                column='ema_lag_'+str(i)
                data[column]=data['ema_lag'].shift(i)
                columns.append(column)

                column='wr_lag_'+str(i)
                data[column]=data['wr_lag'].shift(i)
                columns.append(column)

                column='wr_short_lag_'+str(i)
                data[column]=data['wr_short_lag'].shift(i)
                columns.append(column)

                column='ema_short_lag_'+str(i)
                data[column]=data['ema_short_lag'].shift(i)
                columns.append(column)
                
                column='ema_long_lag_'+str(i)
                data[column]=data['ema_long_lag'].shift(i)
                columns.append(column)
                
            data.dropna(inplace=True)
            
            if self.model==None:
                self.model = MLPClassifier(solver='adam', alpha=0.0000001, learning_rate='adaptive',
                                        hidden_layer_sizes=(10, 3), random_state=1, activation='relu')
                self.model.fit(np.sign(data[columns]), np.sign(data['returns']))
            prediction=self.model.predict(np.sign(data[columns]))[-1]

            if prediction<0:
                if self.entry_confirmation_sell_counter==self.entry_confirmation_number:
                    self.entry_confirmation_sell_counter=0
                    self.entry_confirmation_buy_counter=0
                    return 'sell'
                else:
                    self.entry_confirmation_sell_counter+=1
                    self.entry_confirmation_buy_counter=0
            elif prediction>0:
                if self.entry_confirmation_buy_counter==self.entry_confirmation_number:
                    self.entry_confirmation_buy_counter=0
                    self.entry_confirmation_sell_counter=0
                    return 'buy'
                else:
                    self.entry_confirmation_buy_counter+=1
                    self.entry_confirmation_sell_counter=0
            else:
                self.entry_confirmation_buy_counter=0
                self.entry_confirmation_sell_counter=0
                return None

        except Exception as e:
            print(e, 9898989898)
            return None


    def backtest_exit(self, current_position, given_data):
        try:
            if len(given_data)>=1000:
                given_data=given_data[-1000:]
                columns=[]
                data=pd.DataFrame(given_data[['bidclose', 'askclose']].mean(axis=1), columns=['midclose'])
                data['tickqty']=given_data.tickqty
                data['wr']=r_percent(given_data, self.r_percent_period)
                data['wr_short']=r_percent(given_data, self.r_percent_short_period)
                data['cmf']=cmf(list(given_data.bidclose), list(given_data.bidhigh), list(given_data.bidlow), list(given_data.tickqty), self.cmf_period)
                data['ema']=ema(list(given_data.bidclose), self.ema_period)
                data['ema_short']=ema(list(given_data.bidclose), self.ema_short_period)
                data['ema_long']=ema(list(given_data.bidclose), self.ema_long_period)
                data['sma_long']=sma(list(given_data.bidclose), self.sma_long_period)

                data['wr_1']=data['wr'].copy()
                data['wr_short_1']=data['wr_short'].copy()
                data['cmf_1']=data['cmf'].copy()
                data['ema_1']=data['ema'].copy()
                data['ema_short_1']=data['ema_short'].copy()
                data['ema_long_1']=data['ema_long'].copy()
                data['sma_long_1']=data['sma_long'].copy()

                columns=[]

                data['returns']=np.log(data.midclose)-np.log(data.midclose.shift(1))
                data['tick_lag']=np.log(data.tickqty)-np.log(data.tickqty.shift(1))
                data['cmf_lag']=data.cmf_1-data.cmf_1.shift(1)
                data['sma_long_lag']=np.log(data.sma_long_1)-np.log(data.sma_long_1.shift(1))
                data['ema_lag']=np.log(data.ema_1)-np.log(data.ema_1.shift(1))
                data['ema_short_lag']=np.log(data.ema_short_1)-np.log(data.ema_short_1.shift(1))
                data['ema_long_lag']=np.log(data.ema_long_1)-np.log(data.ema_long_1.shift(1))
                data['wr_lag']=data.wr_1-data.wr_1.shift(1)
                data['wr_short_lag']=data.wr_short_1-data.wr_short_1.shift(1)
                

                for i in range(1, self.lag+1):
                    column='lag_'+str(i)
                    data[column]=data['returns'].shift(i)
                    columns.append(column)

                    column='tick_lag_'+str(i)
                    data[column]=data['tick_lag'].shift(i)
                    columns.append(column)
                    
                    column='cmf_lag_'+str(i)
                    data[column]=data['cmf_lag'].shift(i)
                    columns.append(column)
                    
                    column='sma_long_lag_'+str(i)
                    data[column]=data['sma_long_lag'].shift(i)
                    columns.append(column)
                    
                    column='ema_lag_'+str(i)
                    data[column]=data['ema_lag'].shift(i)
                    columns.append(column)

                    column='wr_lag_'+str(i)
                    data[column]=data['wr_lag'].shift(i)
                    columns.append(column)

                    column='wr_short_lag_'+str(i)
                    data[column]=data['wr_short_lag'].shift(i)
                    columns.append(column)

                    column='ema_short_lag_'+str(i)
                    data[column]=data['ema_short_lag'].shift(i)
                    columns.append(column)
                    
                    column='ema_long_lag_'+str(i)
                    data[column]=data['ema_long_lag'].shift(i)
                    columns.append(column)
                    
                data.dropna(inplace=True)
                
                if self.model==None:
                    self.model = MLPClassifier(solver='adam', alpha=0.0000001, learning_rate='adaptive',
                                            hidden_layer_sizes=(10, 3), random_state=1, activation='relu')
                    self.model.fit(np.sign(data[columns]), np.sign(data['returns']))
                prediction=self.model.predict(np.sign(data[columns]))[-1]

                if current_position=='buy' and prediction<0:
                    if self.exit_confirmation_counter_buy_backtest==self.exit_confirmation_number:
                        self.exit_confirmation_counter_buy_backtest=0
                        self.exit_confirmation_counter_sell_backtest=0
                        return 'exit'
                    else:
                        self.exit_confirmation_counter_buy_backtest+=1
                        self.exit_confirmation_counter_sell_backtest=0
                elif current_position=='sell' and prediction>0:
                    if self.exit_confirmation_counter_sell_backtest==self.exit_confirmation_number:
                        self.exit_confirmation_counter_sell_backtest=0
                        self.exit_confirmation_counter_buy_backtest=0
                        return 'exit'
                    else:
                        self.exit_confirmation_counter_sell_backtest+=1
                        self.exit_confirmation_counter_buy_backtest=0
                else:
                    self.exit_confirmation_counter_sell_backtest=0
                    self.exit_confirmation_counter_buy_backtest=0
                    return None
            else:
                return None
        except Exception as e:
            print(e)
            return None

    def backtest_entry(self, given_data):
        try:
            if len(given_data)>=1000:
                given_data=given_data[-1000:]
                columns=[]
                data=pd.DataFrame(given_data[['bidclose', 'askclose']].mean(axis=1), columns=['midclose'])
                data['tickqty']=given_data.tickqty
                data['wr']=r_percent(given_data, self.r_percent_period)
                data['wr_short']=r_percent(given_data, self.r_percent_short_period)
                data['cmf']=cmf(list(given_data.bidclose), list(given_data.bidhigh), list(given_data.bidlow), list(given_data.tickqty), self.cmf_period)
                data['ema']=ema(list(given_data.bidclose), self.ema_period)
                data['ema_short']=ema(list(given_data.bidclose), self.ema_short_period)
                data['ema_long']=ema(list(given_data.bidclose), self.ema_long_period)
                data['sma_long']=sma(list(given_data.bidclose), self.sma_long_period)

                data['wr_1']=data['wr'].copy()
                data['wr_short_1']=data['wr_short'].copy()
                data['cmf_1']=data['cmf'].copy()
                data['ema_1']=data['ema'].copy()
                data['ema_short_1']=data['ema_short'].copy()
                data['ema_long_1']=data['ema_long'].copy()
                data['sma_long_1']=data['sma_long'].copy()

                columns=[]

                data['returns']=np.log(data.midclose)-np.log(data.midclose.shift(1))
                data['tick_lag']=np.log(data.tickqty)-np.log(data.tickqty.shift(1))
                data['cmf_lag']=data.cmf_1-data.cmf_1.shift(1)
                data['sma_long_lag']=np.log(data.sma_long_1)-np.log(data.sma_long_1.shift(1))
                data['ema_lag']=np.log(data.ema_1)-np.log(data.ema_1.shift(1))
                data['ema_short_lag']=np.log(data.ema_short_1)-np.log(data.ema_short_1.shift(1))
                data['ema_long_lag']=np.log(data.ema_long_1)-np.log(data.ema_long_1.shift(1))
                data['wr_lag']=data.wr_1-data.wr_1.shift(1)
                data['wr_short_lag']=data.wr_short_1-data.wr_short_1.shift(1)
                

                for i in range(1, self.lag+1):
                    column='lag_'+str(i)
                    data[column]=data['returns'].shift(i)
                    columns.append(column)

                    column='tick_lag_'+str(i)
                    data[column]=data['tick_lag'].shift(i)
                    columns.append(column)
                    
                    column='cmf_lag_'+str(i)
                    data[column]=data['cmf_lag'].shift(i)
                    columns.append(column)
                    
                    column='sma_long_lag_'+str(i)
                    data[column]=data['sma_long_lag'].shift(i)
                    columns.append(column)
                    
                    column='ema_lag_'+str(i)
                    data[column]=data['ema_lag'].shift(i)
                    columns.append(column)

                    column='wr_lag_'+str(i)
                    data[column]=data['wr_lag'].shift(i)
                    columns.append(column)

                    column='wr_short_lag_'+str(i)
                    data[column]=data['wr_short_lag'].shift(i)
                    columns.append(column)

                    column='ema_short_lag_'+str(i)
                    data[column]=data['ema_short_lag'].shift(i)
                    columns.append(column)
                    
                    column='ema_long_lag_'+str(i)
                    data[column]=data['ema_long_lag'].shift(i)
                    columns.append(column)
                    
                data.dropna(inplace=True)
                
                if self.model==None:
                    self.model = MLPClassifier(solver='adam', alpha=0.0000001, learning_rate='adaptive',
                                            hidden_layer_sizes=(10, 3), random_state=1, activation='relu')
                    self.model.fit(np.sign(data[columns]), np.sign(data['returns']))
                prediction=self.model.predict(np.sign(data[columns]))[-1]

                if prediction<0:
                    if self.entry_confirmation_counter_sell_backtest==self.entry_confirmation_number:
                        self.entry_confirmation_counter_sell_backtest=0
                        self.entry_confirmation_counter_buy_backtest=0
                        return 'sell'
                    else:
                        self.entry_confirmation_counter_sell_backtest+=1
                        self.entry_confirmation_counter_buy_backtest=0
                elif prediction>0:
                    if self.entry_confirmation_counter_buy_backtest==self.entry_confirmation_number:
                        self.entry_confirmation_counter_buy_backtest=0
                        self.entry_confirmation_counter_sell_backtest=0
                        return 'buy'
                    else:
                        self.entry_confirmation_counter_buy_backtest+=1
                        self.entry_confirmation_counter_sell_backtest=0
                else:
                    self.entry_confirmation_counter_buy_backtest=0
                    self.entry_confirmation_counter_sell_backtest=0
                    return None
            else:
                return None

        except Exception as e:
            print(e, 11111111111111)
            return None
