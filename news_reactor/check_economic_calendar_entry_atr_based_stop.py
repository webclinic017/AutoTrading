from bs4 import BeautifulSoup
import requests
import datetime
import csv
import pandas as pd
import numpy as np
from dateutil import tz 
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
    from economic_data_collection import get_economic_calendar, utc_to_central_time
else:
    from news_reactor.economic_data_collection import get_economic_calendar, utc_to_central_time


news_reactor_name='Entry and ATR based stop loss news reactor'

news_reactor_description="""




Entry and ATR based stop loss news reactor checks economic calendar and if it finds a news that will be released
in specified period of time, it takes the following actions:
It is possible to assgin certain level of impact for system to look for (option are: high impact, medium impact and low impact)

If the strategy is in a position and the news will happen in specified period of time, it changes position's stop loss


If the strategy is not in a position and the news will happen in specified period of time, does not let the trade happen





"""


inputs_name_dict={
                'Position entry time limit (in minute)':['position_entry_time_limit', 30],
                'Time to change stop loss before news (in minute)':['time_to_change_stop_loss_before_news', 5],
                'ATR period for stop loss':['atr_period_for_stop_loss', 20],
                'ATR multiply for stop loss':['atr_multiply_for_stop_loss', 1],
                'Watch for high impact news':['watch_for_high_impact_news', True],
                'Watch for medium impact news':['watch_for_medium_impact_news', True],
                'Watch for low impact news':['watch_for_low_impact_news', False],
                }

class check_economic_calendar_entry_atr_based_stop:
    def __init__(self, account_currency, account_id, symbol, timeframe, position_entry_time_limit, time_to_change_stop_loss_before_news, atr_period_for_stop_loss, atr_multiply_for_stop_loss, watch_for_high_impact_news, watch_for_medium_impact_news, watch_for_low_impact_news):
        self.account_id=account_id
        self.account_currency=account_currency
        self.symbol=symbol
        self.timeframe=timeframe
        self.position_entry_time_limit=datetime.timedelta(minutes=position_entry_time_limit)
        self.time_to_change_stop_loss_before_news=datetime.timedelta(minutes=time_to_change_stop_loss_before_news)
        self.atr_period=int(atr_period_for_stop_loss)
        self.stop_loss_atr_multiply=atr_multiply_for_stop_loss
        self.impact_list_to_watch=[]
        if watch_for_high_impact_news=='True':
            self.impact_list_to_watch.append('High Impact Expected')
        if watch_for_medium_impact_news=='True':
            self.impact_list_to_watch.append('Medium Impact Expected')
        if watch_for_low_impact_news=='True':
            self.impact_list_to_watch.append('Low Impact Expected')
        self.db=Db_Controller()
        self.economic_calendar=pd.DataFrame()

    def update_economic_calendar(self):
        self.last_update_time=datetime.datetime.utcnow()
        self.economic_calendar=get_economic_calendar()

    def check_condition_entry(self):
        if self.economic_calendar.empty:
            self.update_economic_calendar()
            if self.economic_calendar.empty:
                return False
        if utc_to_central_time(self.last_update_time).day!=utc_to_central_time(datetime.datetime.utcnow()).day:
            self.update_economic_calendar()
        now_utc=datetime.datetime.utcnow()
        check_time_ahead=now_utc+self.position_entry_time_limit
        
        if self.economic_calendar.loc[(self.economic_calendar['date']>now_utc) & (self.economic_calendar['date']<check_time_ahead) & (self.economic_calendar['impact'].isin(self.impact_list_to_watch)) & (self.economic_calendar['currency'].str.contains(self.symbol))].empty:
            return False  #Trade allowed
        else:
            return True #Trade not allowed

    def check_condition_stop(self, position_type):
        if self.economic_calendar.empty:
            self.update_economic_calendar()
            if self.economic_calendar.empty:
                return False
        if utc_to_central_time(self.last_update_time).day!=utc_to_central_time(datetime.datetime.utcnow()).day:
            self.update_economic_calendar()
        now_utc=datetime.datetime.utcnow()
        check_time_ahead=now_utc+self.time_to_change_stop_loss_before_news
        if self.economic_calendar.loc[(self.economic_calendar['date']>now_utc) & (self.economic_calendar['date']<check_time_ahead) & (self.economic_calendar['impact'].isin(self.impact_list_to_watch)) & (self.economic_calendar['currency'].str.contains(self.symbol))].empty:
            data=self.db.query_price_data(self.symbol, self.timeframe, self.atr_period*2)
            data['atr']=atr(list(data.bidclose), self.atr_period)
            last_atr=data.atr.iloc[-1]
            price=data.bidclose.iloc[-1]
            if position_type=='buy':
                stop_loss=price-last_atr*self.stop_loss_atr_multiply
                return stop_loss
            else:
                stop_loss=price+last_atr*self.stop_loss_atr_multiply
                return stop_loss
        else:
            return False #No need to change stop loss





