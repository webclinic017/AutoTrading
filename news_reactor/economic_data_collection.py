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




def central_time_to_utc(central_time):
    try:
        from_zone = tz.gettz('Canada/Central')
        to_zone = tz.gettz('UTC')
        central_time = central_time.replace(tzinfo=from_zone)
        utc = central_time.astimezone(to_zone)
        utc=datetime.datetime.strftime(utc, "%Y-%m-%d %H:%M:%S")
        utc=datetime.datetime.strptime(utc, "%Y-%m-%d %H:%M:%S")
        return utc
    except Exception as e:
        print(e)

def utc_to_central_time(utc):
    try:
        to_zone = tz.gettz('Canada/Central')
        from_zone = tz.gettz('UTC')
        utc = utc.replace(tzinfo=from_zone)
        central_time = utc.astimezone(to_zone)
        central_time=datetime.datetime.strftime(central_time, "%Y-%m-%d %H:%M:%S")
        central_time=datetime.datetime.strptime(central_time, "%Y-%m-%d %H:%M:%S")
        return central_time
    except Exception as e:
        print(e)

def get_economic_calendar():

    link="calendar.php?day=today"
    output=pd.DataFrame(columns=['date', 'currency', 'impact', 'event', 'actual', 'forecast', 'previous'])
    # get the page and make the soup
    baseURL = "https://www.forexfactory.com/"
    r = requests.get(baseURL + link)
    data = r.text
    soup = BeautifulSoup(data, "lxml")

    # get and parse table data, ignoring details and graph
    table = soup.find("table", class_="calendar__table")

    # do not use the ".calendar__row--grey" css selector (reserved for historical data)
    trs = table.select("tr.calendar__row.calendar_row")
    fields = ["date","time","currency","impact","event","actual","forecast","previous"]

    # some rows do not have a date (cells merged)
    curr_year = str(datetime.datetime.utcnow().year)
    curr_date = ""
    curr_time = ""
    for tr in trs:

        # fields may mess up sometimes, see Tue Sep 25 2:45AM French Consumer Spending
        # in that case we append to errors.csv the date time where the error is
        try:
            for field in fields:
                data = tr.select("td.calendar__cell.calendar__{}.{}".format(field,field))[0]
                # print(data)
                if field=="date" and data.text.strip()!="":
                    curr_date = data.text.strip()
                elif field=="time" and data.text.strip()!="":
                    # time is sometimes "All Day" or "Day X" (eg. WEF Annual Meetings)
                    if data.text.strip().find("Day")!=-1:
                        curr_time = "12:00am"
                    else:
                        curr_time = data.text.strip()
                elif field=="currency":
                    currency = data.text.strip()
                elif field=="impact":
                    # when impact says "Non-Economic" on mouseover, the relevant
                    # class name is "Holiday", thus we do not use the classname
                    impact = data.find("span")["title"]
                elif field=="event":
                    event = data.text.strip()
                elif field=="actual":
                    actual = data.text.strip()
                    if actual=='':
                        actual='None'
                elif field=="forecast":
                    forecast = data.text.strip()
                    if forecast=='':
                        forecast='None'
                elif field=="previous":
                    previous = data.text.strip()
                
            dt = datetime.datetime.strptime(",".join([curr_year,curr_date,curr_time]),
                                            "%Y,%a%b %d,%I:%M%p")

            dt=central_time_to_utc(dt)
            output=output.append({'date':dt,
                                  'currency':currency,
                                  'impact':impact,
                                  'event':event,
                                  'actual':actual,
                                  'forecast':forecast,
                                  'previous':previous}, ignore_index=True)

            
            
        except Exception as e:
            pass

    return output


if __name__=="__main__":
    print('------------------')
    calendar=get_economic_calendar()
    print(calendar)
