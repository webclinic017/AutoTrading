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
from risk_management.equity_atr_based_risk_management import equity_atr_based_risk_management
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


news_reactor_name='Economic calendar trading'

news_reactor_description="""




Economic calendar trading checks economic calendar and if it finds a news that is just released
and has the specified impacts, it takes the following actions:
It is possible to assgin certain level of impact for system to look for (option are: high impact, medium impact and low impact)


If the strategy has any open position created by this system, the system might close the position if the result of news is not in favour of the position


If the strategy has any open position created by this system, it analyzes the result and signal buy or sell

When opening news position it uses Equity and ATR based risk management and has it own risk management settig to calculate stop loss
limit and position size.





"""

inputs_name_dict={
                'ATR period for stop loss':['atr_period_for_stop_loss', 20],
                'ATR multiply for stop loss':['atr_multiply_for_stop_loss', 3],
                'ATR multiply for limit':['atr_multiply_for_limit', 10],
                'Watch for high impact news':['watch_for_high_impact_news', True],
                'Watch for medium impact news':['watch_for_medium_impact_news', True],
                'Watch for low impact news':['watch_for_low_impact_news', False],
                'Risk percent':['risk_percent', 3]
                }

# 1 means if the actual is greater than forecast, currency goes bullish.
# 2 means if the actual is greater than forecast, currency goes bearish.
# 3 means speech.

newsDict={'AUD':{'MI Inflation Gauge m/m':1,
                    'ANZ Job Advertisements m/m':1,
                    'AIG Services Index':1,
                    'Retail Sales m/m':1,
                    'Trade Balance':1,
                    'RBA Rate Statement':3,
                    'Cash Rate':1,
                    'RBA Gov Lowe Speaks':3,
                    'AIG Construction Index':1,
                    'NAB Quarterly Business Confidence':1,
                    'RBA Monetary Policy Statement':3,
                    'Home Loans m/m':1,
                    'NAB Business Confidence':1,
                    'Westpac Consumer Sentiment':1,
                    'MI Inflation Expectations':1,
                    'HIA New Home Sales m/m':1,
                    'Monetary Policy Meeting Minutes':3,
                    'MI Leading Index m/m':1,
                    'Wage Price Index q/q':1,
                    'Flash Manufacturing PMI':1,
                    'Flash Services PMI':1,
                    'Employment Change':1,
                    'Unemployment Rate':2,
                    'Construction Work Done q/q':1,
                    'Private Capital Expenditure q/q':1,
                    'Private Sector Credit m/m':1,
                    'AIG Manufacturing Index':1,
                    'Commodity Prices y/y':1,
                    'Building Approvals m/m':1,
                    'Company Operating Profits q/q':1,
                    'Current Account':1,
                    'GDP q/q':1,
                    'HPI q/q':1,
                    'RBA Bulletin':3,
                    },

            'USD':{'Factory Orders m/m':1,
                    'Final Services PMI':1,
                    'ISM Non-Manufacturing PMI':1,
                    'IBD/TIPP Economic Optimism':1,
                    'Prelim Nonfarm Productivity q/q':2,
                    'Prelim Unit Labor Costs q/q':1,
                    'FOMC Member Quarles Speaks':3,
                    'Fed Chair Powell Speaks':3,
                    'Unemployment Claims':2,
                    'FOMC Member Clarida Speaks':3,
                    'Consumer Credit m/m':1,
                    'FOMC Member Bullard Speaks':3,
                    'Mortgage Delinquencies':2,
                    'NFIB Small Business Index':1,
                    'JOLTS Job Openings':1,
                    'Advance GDP q/q':1,
                    'CPI m/m':1,
                    'Core CPI m/m':1,
                    'Core Durable Goods Orders m/m':1,
                    'Core Retail Sales m/m':1,
                    'Retail Sales m/m':1,
                    'Advance GDP Price Index q/q':1,
                    'Core PCE Price Index m/m':1,
                    'Durable Goods Orders m/m':1,
                    'Personal Spending m/m':1,
                    'Goods Trade Balance':1,
                    'Personal Income m/m':1,
                    'Prelim Wholesale Inventories m/m':2,
                    'Trade Balance':1,
                    'Construction Spending m/m':1,
                    'Final Wholesale Inventories m/m':2,
                    'New Home Sales':1,
                    'Federal Budget Balance':1,
                    'PPI m/m':1,
                    'Core PPI m/m':1,
                    'Business Inventories m/m':2,
                    'Empire State Manufacturing Index':1,
                    'Import Prices m/m':1,
                    'Capacity Utilization Rate':1,
                    'Industrial Production m/m':1,
                    'Prelim UoM Consumer Sentiment':1,
                    'Prelim UoM Inflation Expectations':1,
                    'TIC Long-Term Purchases':1,
                    'Average Hourly Earnings m/m':1,
                    'Non-Farm Employment Change':1,
                    'Unemployment Rate':2,
                    'Final Manufacturing PMI':1,
                    'ISM Manufacturing PMI':1,
                    'Revised UoM Consumer Sentiment':1,
                    'ISM Manufacturing Prices':1,
                    'Revised UoM Inflation Expectations':1,
                    'NAHB Housing Market Index':1,
                    'Building Permits':1,
                    'Housing Starts':1,
                    'FOMC Meeting Minutes':3,
                    'Philly Fed Manufacturing Index':1,
                    'Flash Manufacturing PMI':1,
                    'Flash Services PMI':1,
                    'CB Leading Index m/m':1,
                    'Existing Home Sales':1,
                    'HPI m/m':1,
                    'S&P/CS Composite-20 HPI y/y':1,
                    'CB Consumer Confidence':1,
                    'Richmond Manufacturing Index':1,
                    'ADP Non-Farm Employment Change':1,
                    'Pending Home Sales m/m':1,
                    'Challenger Job Cuts y/y':2,
                    'Prelim GDP q/q':1,
                    'Prelim GDP Price Index q/q':1,
                    'Chicago PMI':1,
                    'Total Vehicle Sales':1,
                    'Beige Book':3,
                    'Revised Nonfarm Productivity q/q':2,
                    'Revised Unit Labor Costs q/q':1,
                    'FOMC Economic Projections':3,
                    'FOMC Statement':3,
                    'Federal Funds Rate':1,
                    'FOMC Press Conference':3,
                    'Final GDP q/q':1,
                    'Final GDP Price Index q/q':1,
                    },
                    
            'JPY':{'Monetary Base y/y':1,
                    'Leading Indicators':1,
                    'Household Spending y/y':1,
                    'Bank Lending y/y':1,
                    'Current Account':1,
                    'Average Cash Earnings y/y':1,
                    'Economy Watchers Sentiment':1,
                    'M2 Money Stock y/y':1,
                    'Tertiary Industry Activity m/m':1,
                    'Prelim Machine Tool Orders y/y':1,
                    'PPI y/y':1,
                    'Prelim GDP q/q':1,
                    'Prelim GDP Price Index y/y':1,
                    'Revised Industrial Production m/m':1,
                    'Core Machinery Orders m/m':1,
                    'Trade Balance':1,
                    'Flash Manufacturing PMI':1,
                    'All Industries Activity m/m':1,
                    'National Core CPI y/y':1,
                    'SPPI y/y':1,
                    'BOJ Core CPI y/y':1,
                    'Prelim Industrial Production m/m':1,
                    'Retail Sales y/y':1,
                    'Housing Starts y/y':1,
                    'Tokyo Core CPI y/y':1,
                    'Unemployment Rate':2,
                    'Capital Spending q/y':1,
                    'Final Manufacturing PMI':1,
                    'Consumer Confidence':1,
                    'Final GDP Price Index y/y':1,
                    'Final GDP q/q':1,
                    'BSI Manufacturing Index':1,
                    'Monetary Policy Statement':3,
                    'BOJ Policy Rate':1,
                    'BOJ Press Conference':1,
                    'Monetary Policy Meeting Minutes':1,
                    'BOJ Summary of Opinions':3,
                    'Tankan Manufacturing Index':1,
                    'Tankan Non-Manufacturing Index':1,
                    },
                    
            'EUR':{'Sentix Investor Confidence':1,
                    'Spanish Unemployment Change':2,
                    'Spanish Services PMI':1,
                    'Italian Services PMI':1,
                    'French Final Services PMI':1,
                    'German Final Services PMI':1,
                    'Final Services PMI':1,
                    'Retail Sales m/m':1,
                    'German Factory Orders m/m':1,
                    'German Industrial Production m/m':1,
                    'French Trade Balance':1,
                    'ECB Economic Bulletin':3,
                    'Italian Retail Sales m/m':1,
                    'EU Economic Forecasts':3,
                    'German Trade Balance':1,
                    'French Industrial Production m/m':1,
                    'French Prelim Private Payrolls q/q':1,
                    'Italian Industrial Production m/m':1,
                    'Industrial Production m/m':1,
                    'German Prelim GDP q/q':1,
                    'Flash GDP q/q':1,
                    'Flash Employment Change q/q':1,
                    'Italian Trade Balance':1,
                    'Trade Balance':1,
                    'Foreign Securities Purchases':1,
                    'French Gov Budget Balance':1,
                    'Spanish Manufacturing PMI':1,
                    'Italian Manufacturing PMI':1,
                    'French Final Manufacturing PMI':1,
                    'German Final Manufacturing PMI':1,
                    'Final Manufacturing PMI':1,
                    'CPI Flash Estimate y/y':1,
                    'Core CPI Flash Estimate y/y':1,
                    'German Buba Monthly Report':3,
                    'German WPI m/m':1,
                    'Current Account':1,
                    'German ZEW Economic Sentiment':1,
                    'ZEW Economic Sentiment':1,
                    'German Final CPI m/m':1,
                    'German PPI m/m':1,
                    'French Final CPI m/m':1,
                    'French Flash Manufacturing PMI':1,
                    'French Flash Services PMI':1,
                    'German Flash Manufacturing PMI':1,
                    'German Flash Services PMI':1,
                    'Flash Manufacturing PMI':1,
                    'Flash Services PMI':1,
                    'ECB Monetary Policy Meeting Accounts':3,
                    'German Final GDP q/q':1,
                    'German Ifo Business Climate':1,
                    'Final CPI y/y':1,
                    'Final Core CPI y/y':1,
                    'Belgian NBB Business Climate':1,
                    'M3 Money Supply y/y':1,
                    'Private Loans y/y':1,
                    'German GfK Consumer Climate':1,
                    'French Consumer Spending m/m':1,
                    'French Prelim GDP q/q':1,
                    'Spanish Flash CPI y/y':1,
                    'Italian Prelim CPI m/m':1,
                    'Consumer Confidence':1,
                    'German Prelim CPI m/m':1,
                    'French Prelim CPI m/m':1,
                    'Italian Monthly Unemployment Rate':2,
                    'German Import Prices m/m':1,
                    'German Unemployment Change':2,
                    'Unemployment Rate':2,
                    'PPI m/m':1,
                    'German Retail Sales m/m':1,
                    'Final Employment Change q/q':1,
                    'Revised GDP q/q':1,
                    'Main Refinancing Rate':1,
                    'ECB Press Conference':3,
                    },
                    
            'CNY':{'Foreign Direct Investment ytd/y':1,
                    'M2 Money Supply y/y':1,
                    'New Loans':1,
                    'Trade Balance':1,
                    'USD-Denominated Trade Balance':1,
                    'CPI y/y':1,
                    'PPI y/y':1,
                    'CB Leading Index m/m':1,
                    'Manufacturing PMI':1,
                    'Non-Manufacturing PMI':1,
                    'Caixin Manufacturing PMI':1,
                    'Caixin Services PMI':1,
                    'Fixed Asset Investment ytd/y':1,
                    'Industrial Production y/y':1,
                    'Retail Sales y/y':1,
                    'Unemployment Rate':2,                     
                    },
                    
            'GBP':{'Construction PMI':1,
                    'BRC Retail Sales Monitor y/y':1,
                    'Services PMI':1,
                    'Halifax HPI m/m':1,
                    'BOE Inflation Report':3,
                    'MPC Official Bank Rate Votes':3,
                    'Monetary Policy Summary':3,
                    'Official Bank Rate':1,
                    'Asset Purchase Facility':2,
                    'MPC Asset Purchase Facility Votes':3,
                    'GDP m/m':1,
                    'Manufacturing Production m/m':1,
                    'Prelim GDP q/q':1,
                    'Prelim Business Investment q/q':1,
                    'Construction Output m/m':1,
                    'Goods Trade Balance':1,
                    'Index of Services 3m/3m':1,
                    'Industrial Production m/m':1,
                    'CPI y/y':1,
                    'PPI Input m/m':1,
                    'RPI y/y':1,
                    'Core CPI y/y':1,
                    'HPI y/y':1,
                    'PPI Output m/m':1,
                    'RICS House Price Balance':1,
                    'Retail Sales m/m':1,
                    'Manufacturing PMI':1,
                    'Rightmove HPI m/m':1,
                    'Average Earnings Index 3m/y':1,
                    'Unemployment Rate':2,
                    'Claimant Count Change':2,
                    'CBI Industrial Order Expectations':1,
                    'Public Sector Net Borrowing':2,
                    'CBI Realized Sales':1,
                    'High Street Lending':1,
                    'BRC Shop Price Index y/y':1,
                    'GfK Consumer Confidence':1,
                    'Nationwide HPI m/m':1,
                    'Net Lending to Individuals m/m':1,
                    'M4 Money Supply m/m':1,
                    'Mortgage Approvals':1,
                    'Consumer Inflation Expectations':1,
                    'NIESR GDP Estimate':1,
                    'FPC Statement':3,
                    'BOE Quarterly Bulletin':3,
                    'Current Account':1,
                    'Final GDP q/q':1,
                    'Revised Business Investment q/q':1,                     
                    },
                    
            'CAD':{'Gov Council Member Lane Speaks':3,
                    'Building Permits m/m':1,
                    'Ivey PMI':1,
                    'Housing Starts':1,
                    'Employment Change':1,
                    'Unemployment Rate':2,
                    'Trade Balance':1,
                    'ADP Non-Farm Employment Change':1,
                    'NHPI m/m':1,
                    'Manufacturing PMI':1,
                    'Foreign Securities Purchases':1,
                    'Inflation Report Hearings':3,
                    'Wholesale Sales m/m':1,
                    'Core Retail Sales m/m':1,
                    'Retail Sales m/m':1,
                    'Corporate Profits q/q':1,
                    'CPI m/m':1,
                    'Common CPI y/y':1,
                    'Median CPI y/y':1,
                    'Trimmed CPI y/y':1,
                    'Core CPI m/m':1,
                    'GDP m/m':1,
                    'Labor Productivity q/q':2,
                    'BOC Rate Statement':3,
                    'Overnight Rate':1,
                    'Capacity Utilization Rate':1,
                    'Manufacturing Sales m/m':1,
                    'RMPI m/m':1,
                    'IPPI m/m':1,
                    },
                    
            'NZD':{'Building Consents m/m':1,
                    'ANZ Commodity Prices m/m':1,
                    'GDT Price Index':1,
                    'Employment Change q/q':1,
                    'Unemployment Rate':2,
                    'Labor Cost Index q/q':1,
                    'Official Cash Rate':1,
                    'RBNZ Monetary Policy Statement':3,
                    'RBNZ Rate Statement':3,
                    'RBNZ Press Conference':3,
                    'Inflation Expectations q/q':1,
                    'FPI m/m':1,
                    'Business NZ Manufacturing Index':1,
                    'Visitor Arrivals m/m':1,
                    'PPI Input q/q':1,
                    'PPI Output q/q':1,
                    'Credit Card Spending y/y':1,
                    'Retail Sales q/q':1,
                    'Core Retail Sales q/q':1,
                    'Trade Balance':1,
                    'Overseas Trade Index q/q':1,
                    'ANZ Business Confidence':1,
                    'Current Account':1,
                    'RMPI m/m':1,
                    'IPPI m/m':1,
                    'Manufacturing Sales q/q':1,
                    'Westpac Consumer Sentiment':1,
                    'GDP q/q':1,
                    },
                    
            'CHF':{'Foreign Currency Reserves':2,
                    'Unemployment Rate':2,
                    'PPI m/m':1,
                    'SECO Consumer Climate':1,
                    'Retail Sales y/y':1,
                    'Manufacturing PMI':1,
                    'Trade Balance':1,
                    'Credit Suisse Economic Expectations':1,
                    'GDP q/q':1,
                    'KOF Economic Barometer':1,
                    'CPI m/m':1,
                    'SNB Quarterly Bulletin':3,
                    'SNB Monetary Policy Assessment':3,
                    'Libor Rate':1,
                    'SNB Press Conference':3,
                    },
            }
            


class economic_calendar_trading:
    def __init__(self, account_currency, account_id, symbol, timeframe, atr_period_for_stop_loss, atr_multiply_for_stop_loss, atr_multiply_for_limit, watch_for_high_impact_news, watch_for_medium_impact_news, watch_for_low_impact_news, risk_percent):
        self.account_id=account_id
        self.account_currency=account_currency
        self.symbol=symbol
        self.timeframe=timeframe
        self.atr_period=int(atr_period_for_stop_loss)
        self.stop_loss_atr_multiply=atr_multiply_for_stop_loss
        self.limit_atr_multiply=atr_multiply_for_limit
        self.risk_percent=risk_percent
        self.news_dict=newsDict
        self.low_impact_weight=1
        self.medium_impact_weight=2
        self.high_impact_weight=3
        self.impact_weight_dict={
                                    'High Impact Expected':3,
                                    'Medium Impact Expected':2,
                                    'Low Impact Expected':1,
                                }
        self.risk_management=equity_atr_based_risk_management(self.account_currency, self.account_id, symbol, timeframe, atr_period_for_stop_loss, atr_multiply_for_stop_loss, atr_multiply_for_limit, risk_percent)
        self.base_currency=self.symbol[:3]
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
        try:
            if self.economic_calendar.empty:
                self.update_economic_calendar()
                if self.economic_calendar.empty:
                    return False
            if utc_to_central_time(self.last_update_time).day!=utc_to_central_time(datetime.datetime.utcnow()).day:
                self.update_economic_calendar()
            now_utc=datetime.datetime.utcnow()
            now_utc=datetime.datetime(now_utc.year, now_utc.month, now_utc.day, now_utc.hour, now_utc.minute, now_utc.second)
            economic_calendar_result=self.economic_calendar.loc[(self.economic_calendar['date']==now_utc) & (self.economic_calendar['impact'].isin(self.impact_list_to_watch)) & (self.economic_calendar['currency'].str.contains(self.symbol))]
            if economic_calendar_result.empty:
                return False
            else:
                self.update_economic_calendar()
                economic_calendar_result=self.economic_calendar.loc[(self.economic_calendar['date']==now_utc) & (self.economic_calendar['impact'].isin(self.impact_list_to_watch)) & (self.economic_calendar['currency'].str.contains(self.symbol))]
                sell_score=0
                buy_score=0
                for i, j in enumerate(economic_calendar_result.impact):
                    if economic_calendar_result.actual.iloc[i]!='None' and economic_calendar_result.forecast.iloc[i]!='None':
                        if economic_calendar_result.actual.iloc[i]>economic_calendar_result.forecast.iloc[i]:
                            try:
                                if self.news_dict[economic_calendar_result.currency.iloc[i]][economic_calendar_result.event.iloc[i]]==1:
                                    if economic_calendar_result.currency.iloc[i]==self.base_currency:
                                        buy_score+=self.impact_weight_dict[economic_calendar_result.impact.iloc[i]]
                                    else:
                                        sell_score+=self.impact_weight_dict[economic_calendar_result.impact.iloc[i]]
                                elif self.news_dict[economic_calendar_result.currency.iloc[i]][economic_calendar_result.event.iloc[i]]==2:
                                    if economic_calendar_result.currency.iloc[i]==self.base_currency:
                                        sell_score+=self.impact_weight_dict[economic_calendar_result.impact.iloc[i]]
                                    else:
                                        buy_score+=self.impact_weight_dict[economic_calendar_result.impact.iloc[i]]
                                elif self.news_dict[economic_calendar_result.currency.iloc[i]][economic_calendar_result.event.iloc[i]]==3:
                                    if economic_calendar_result.currency.iloc[i]==self.base_currency:
                                        pass
                                    else:
                                        pass
                            except:
                                pass
                        elif economic_calendar_result.actual.iloc[i]<economic_calendar_result.forecast.iloc[i]:
                            try:
                                if self.news_dict[economic_calendar_result.currency.iloc[i]][economic_calendar_result.event.iloc[i]]==1:
                                    if economic_calendar_result.currency.iloc[i]==self.base_currency:
                                        sell_score+=self.impact_weight_dict[economic_calendar_result.impact.iloc[i]]
                                    else:
                                        buy_score+=self.impact_weight_dict[economic_calendar_result.impact.iloc[i]]
                                elif self.news_dict[economic_calendar_result.currency.iloc[i]][economic_calendar_result.event.iloc[i]]==2:
                                    if economic_calendar_result.currency.iloc[i]==self.base_currency:
                                        buy_score+=self.impact_weight_dict[economic_calendar_result.impact.iloc[i]]
                                    else:
                                        sell_score+=self.impact_weight_dict[economic_calendar_result.impact.iloc[i]]
                                elif self.news_dict[economic_calendar_result.currency.iloc[i]][economic_calendar_result.event.iloc[i]]==3:
                                    if economic_calendar_result.currency.iloc[i]==self.base_currency:
                                        pass
                                    else:
                                        pass
                            except:
                                pass
                        else:
                            pass
                            
                    else:
                        pass

                if buy_score>sell_score and buy_score!=0:
                    position_size, required_margin, stop_loss, limit, stop_loss_pip, limit_pip=self.risk_management.position_size_stop_loss('buy')
                    result_dict={
                                    'postion_type':'buy',
                                    'position_size':position_size,
                                    'required_margin':required_margin,
                                    'stop_loss':stop_loss,
                                    'limit':limit,
                                }
                    return result_dict
                elif sell_score>buy_score and sell_score!=0:
                    position_size, required_margin, stop_loss, limit, stop_loss_pip, limit_pip=self.risk_management.position_size_stop_loss('sell')
                    result_dict={
                                    'postion_type':'sell',
                                    'position_size':position_size,
                                    'required_margin':required_margin,
                                    'stop_loss':stop_loss,
                                    'limit':limit,
                                }
                    return result_dict
                else:
                    return False
        except Exception as e:
            print(e, 'calendar trading')

    def check_condition_stop(self, position_type):
        return False



if __name__=="__main__":
    economic_calendar_ins=economic_calendar_trading('AUD', '5116035', 'EURUSD', 'm5', 20, 3, 9, True, True, False, 3)
    economic_calendar_ins.check_condition_entry()





