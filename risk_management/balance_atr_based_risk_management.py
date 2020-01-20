from currency_converter import CurrencyConverter
import pandas as pd
import numpy as np
import os, sys, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

from db_controller import Db_Controller
from indicators import atr
import warnings
warnings.filterwarnings("ignore")

pd.options.mode.chained_assignment = None
np.seterr(divide='ignore', invalid='ignore')

if __name__=='__main__':
    from general_functions import pip_value_cal, leverage_cal
else:
    from risk_management.general_functions import pip_value_cal, leverage_cal


risk_management_name='Balance and ATR based risk management'

risk_management_description="""



Balance and ATR based risk management calculate stop loss, limit and position size based on current value of ATR indicator and
the specified ATR multipy

The conditions is as follow:

Stop loss is calculated by subtracting or adding (depending on position type 'buy or sell') currenct ATR multiplied specified multiply
to current price. Using ATR enables dynamic risk management.

Limit is calculated by subtracting or adding (depending on position type 'buy or sell') currenct ATR multiplied specified multiply
to current price.

Position size is calculated based on this formula:

Position size = ((balance x risk per trade) / calculated stop loss value based on pip)/ pip value per standard lot
Lot         Number of unit
Standard	100,000
Mini	    10,000
Micro	    1,000
Nano	    100





"""

inputs_name_dict={
                'ATR period':['atr_period', 200],
                'Stop loss ATR multiply':['stop_loss_atr_multiply', 3],
                'Limit ATR multiply':['limit_atr_multiply', 30],
                'Risk percent':['risk_percent', 1]
                }

class balance_atr_based_risk_management:
    def __init__(self, account_currency, account_id, symbol, timeframe, atr_period, stop_loss_atr_multiply, limit_atr_multiply, risk_percent):
        self.account_currency=account_currency
        self.account_id=account_id
        self.symbol=symbol
        self.timeframe=timeframe
        self.atr_period=int(atr_period)
        self.stop_loss_atr_multiply=stop_loss_atr_multiply
        self.limit_atr_multiply=limit_atr_multiply
        self.risk_percent=risk_percent
        self.db=Db_Controller()


    def get_account_info(self):
        fxcm_info=self.db.query_table('Fxcm_Info', ('*',), fields=("accountId",), values=(self.account_id,))
        return fxcm_info

    def stop_loss_limit(self, price, last_atr, position_type):

        '''
            stop loss is placed stop_loss_atr_multiply time of atr
        '''
        try:
            if position_type=='buy':
                stop_loss_pip=last_atr*self.stop_loss_atr_multiply
                stop_loss=price-stop_loss_pip
                limit_pip=last_atr*self.limit_atr_multiply
                limit=price+limit_pip
            else:
                stop_loss_pip=last_atr*self.stop_loss_atr_multiply
                stop_loss=price+stop_loss_pip
                limit_pip=last_atr*self.limit_atr_multiply
                limit=price-limit_pip
            if self.symbol[3:]=='JPY':
                stop_loss_pip=stop_loss_pip*100
                limit_pip=limit_pip*100
            else:
                stop_loss_pip=stop_loss_pip*10000
                limit_pip=limit_pip*10000


            return stop_loss, limit, stop_loss_pip, limit_pip
        except Exception as e:
            print(e, 'stop_loss_limit')

    def position_size_stop_loss(self, position_type):
        try:
            ''' Lot         Number of unit
                Standard	100,000
                Mini	    10,000
                Micro	    1,000
                Nano	    100
                Position size = ((account value x risk per trade) / pips risked)/ pip value per standard lot
                Margin Requirement = Current Price × Units Traded × Margin
            '''
            data=self.db.query_price_data(self.symbol, self.timeframe, self.atr_period*2)
            data['atr']=atr(list(data.bidclose), self.atr_period)
            last_atr=data.atr.iloc[-1]
            price=data.bidclose.iloc[-1]

            fxcm_info=self.get_account_info()[0]
            balance=fxcm_info[2]
            stop_loss, limit, stop_loss_pip, limit_pip=self.stop_loss_limit(price, last_atr, position_type)
            leverage=leverage_cal(self.symbol, balance)
            standard_lot_pip_value=pip_value_cal(self.symbol, self.account_currency, price, 100000)
            position_size=int(((((balance*self.risk_percent/100)/stop_loss_pip)/standard_lot_pip_value)*100)*1000)
            required_margin=int(price*position_size/leverage)
            c = CurrencyConverter()
            required_margin=int(c.convert(required_margin, self.symbol[:3], self.account_currency))
            if self.symbol[3:]=='JPY':
                required_margin=required_margin/100

            return position_size/1000, required_margin, stop_loss, limit, stop_loss_pip, limit_pip
        except Exception as e:
            print(e, 'position_size_stop_loss')

    def backtest(self, position_type, data, balance):
        try:
            ''' Lot         Number of unit
                Standard	100,000
                Mini	    10,000
                Micro	    1,000
                Nano	    100
                Position size = ((account value x risk per trade) / pips risked)/ pip value per standard lot
                Margin Requirement = Current Price × Units Traded × Margin
            '''
            data['atr']=atr(list(data.bidclose), self.atr_period)
            last_atr=data.atr.iloc[-1]
            price=data.bidclose.iloc[-1]
            
            stop_loss, limit, stop_loss_pip, limit_pip=self.stop_loss_limit(price, last_atr, position_type)
            leverage=leverage_cal(self.symbol, balance)
            standard_lot_pip_value=pip_value_cal(self.symbol, self.account_currency, price, 100000)
            position_size=int(((((balance*self.risk_percent/100)/stop_loss_pip)/standard_lot_pip_value)*100)*1000)
            required_margin=int(price*position_size/leverage)
            c = CurrencyConverter()
            required_margin=int(c.convert(required_margin, self.symbol[:3], self.account_currency))
            pip_value=pip_value_cal(self.symbol, self.account_currency, price, position_size)
            if self.symbol[3:]=='JPY':
                required_margin=required_margin/100

            return position_size, required_margin, stop_loss, limit, stop_loss_pip, limit_pip, pip_value
        except Exception as e:
            print(e, 'backtest')

if __name__=="__main__":
    #rk=balance_atr_based_risk_management('EURUSD', 'm5', 200, 3, 10, 2)
    #print(rk.position_size_stop_loss('buy'))
    pass