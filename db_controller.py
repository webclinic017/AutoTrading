import sqlite3
import os.path
from os import path
import pandas as pd

"""
This file contains classes for db operations handling
"""



"""
Customized SQLITE functions
"""

class COUNT_UNSUCCESSFUL_TRADES:
    """
    This class is to add function to sqlite to calculate number of unsuccessful trades
    """
    def __init__(self):
        self.count = 0

    def step(self, value):
        if value<0:
            self.count += 1

    def finalize(self):
        return self.count


class COUNT_SUCCESSFUL_TRADES:
    """
    This class is to add function to sqlite to calculate number of successful trades
    """
    def __init__(self):
        self.count = 0

    def step(self, value):
        if value>=0:
            self.count += 1

    def finalize(self):
        return self.count



class Db_Controller():
    """
    Thsi class contains methods for creating tables, inserting, updating, deleteing data to certin tables and query data from certian tables
    """
    def __init__(self):
        pass
    def create_schema(self):
        
        """
        Create all the required tables and their columns
        Output: created schema in SQLITE database
        List of created tables:
        Users - user info (login and password)
        Fxcm_Info - user related info from FXCM server
        Open_Positions - list of currently opened positions at FXCM server from this user
        Closed_Positions - list of currently closed positions at FXCM server from this user
        TradeId_PositionMaker - list of position maker and tradeId
        """
        connection, cursor=self.db_open_connection()


        cursor.execute("""CREATE TABLE IF NOT EXISTS Users (
            username text PRIMARY KEY not null,
            password text not null,
            unique(username)
            )""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS Fxcm_Info(
            accountId int PRIMARY KEY not null,
            accountName text null,
            balance real null,
            dayPL real null,
            equity real null,
            grossPL real null,
            hedging text null,
            mc text null,
            mcDate text null,
            ratePrecision real null,
            t real null,
            usableMargin real null,
            usableMarginPerc real null,
            usableMargin3 real null,
            usableMargin3Perc real null,
            usdMr real null,
            usdMr3 real null
            )""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS OpenPosition(
            t real null,
            ratePrecision real null,
            tradeId text not null PRIMARY KEY,
            accountName text null,
            accountId text null,
            roll real null,
            com real null,
            open real null,
            valueDate text null,
            grossPL real null,
            close real null,
            visiblePL real null,
            isDisabled text null,
            currency text null,
            isBuy text null,
            amountK real null,
            currencyPoint real null,
            time text null,
            usedMargin real null,
            stop real null,
            stopMove real null,
            "limit" real null,
            positionMaker text DEFAULT "Manual" not null
            )""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS ClosedPosition(
            t real null,
            ratePrecision real null,
            tradeId text not null PRIMARY KEY,
            accountName text null,
            roll real null,
            com real null,
            open real null,
            valueDate text null,
            grossPL real null,
            close real null,
            visiblePL real null,
            currency text null,
            isBuy text null,
            amountK real null,
            currencyPoint real null,
            openTime text null,
            closeTime text null,
            positionMaker text DEFAULT "Manual"  not null
            )""")

        cursor.execute("""CREATE TABLE IF NOT EXISTS TradeId_PositionMaker(
            tradeId text not null PRIMARY KEY,
            positionMaker text DEFAULT "Manual"
            )""")
  
        connection.commit()

        cursor.execute("""PRAGMA auto_vacuum = FULL""")
        cursor.execute("PRAGMA journal_mode=WAL")
        connection.commit()
        
        self.db_close_connection(connection)

    def db_open_connection(self):
        """
        This function is called when a connection to db needs to be established.
        It returns connection and cursor objects
        """
        connection = sqlite3.connect('./data/data.dll') #Change for folder
        cursor = connection.cursor()
        return connection, cursor
    def db_close_connection(self, connection):
        """
        This function is called when a connection  needs to be closed.
        It gets connection object and closes it
        """
        try:
            connection.close()
        except:
            pass


    def create_price_data_table(self, symbol, timeframe):
        """
        This method creates new price table for given symbol and timeframe
        """
        connection, cursor=self.db_open_connection()
        cursor.execute("""CREATE TABLE IF NOT EXISTS {}_{}(
            date text primary key,
            bidopen real null,
            bidclose real null,
            bidhigh real null,
            bidlow real null,
            askopen real null,
            askclose real null,
            askhigh real null,
            asklow real null,
            tickqty real null
            )""".format(symbol, timeframe))

        connection.commit()
        self.db_close_connection(connection)

    def create_price_data_renko_table(self, symbol, renko_range):
        """
        This method creates new price table for given symbol and timeframe
        """
        connection, cursor=self.db_open_connection()
        cursor.execute("""CREATE TABLE IF NOT EXISTS {}_{}(
            date text primary key,
            bidopen real null,
            bidclose real null,
            bidhigh real null,
            bidlow real null,
            tickqty real null
            )""".format(symbol, renko_range))

        connection.commit()
        self.db_close_connection(connection)



    def print_table(self, table):    
        """
        Supportive function to test DB values from GUI
        Input: table->str Name of the table
        Output: Prints rows from the desired table
        """
        connection, cursor = self.db_open_connection()
        cursor.execute("SELECT * FROM {}".format(table))
        data = cursor.fetchall()
        self.db_close_connection(connection)
        print(data)

    def get_table(self, table):
        """
        Supportive function to get DB values from GUI
        Input: table->str Name of the table
        Output: Returns all rows from the desired table
        """
        connection, cursor = self.db_open_connection()
        cursor.execute("SELECT * FROM {}".format(table))
        data = cursor.fetchall()
        self.db_close_connection(connection)
        return data

    def update_from_stream(self, table, columns, values, pk_value):
        """
        Function to update a row based on update from streaming data
        Inputs:
        table->str: Name of the table
        columns->list: List of the table's columns to be updated
        values->int/float/str: Corresponding column value, must be in order with columns
        pk_value->int/float/str: Primary key value for update statement
        """
        connection, cursor = self.db_open_connection()
        cursor.execute("PRAGMA table_info({})".format(table))
        tables = cursor.fetchall()
        pk_name = ''
        for x in tables:
            if x[3]==1:
                pk_name = x[1]
                break
        statement = 'UPDATE {} SET '.format(table)
        next_statement = ', '.join([a+'='+'?' for a in columns])
        statement+= next_statement + ' WHERE '+pk_name+'= {}'.format(pk_value)
        cursor.execute(statement, values)
        connection.commit()
        self.db_close_connection(connection)

    def insert_into_price_data_table(self, data, symbol, interval):
        """
        This function insert data to the related price list table
        It recieves data as dataframe and inserts it in a temporary table, and the related price table gets its data from the created temporary table 
        """
        connection, cursor = self.db_open_connection()
        data.to_sql('{}_{}_Temp'.format(symbol, interval), con=connection, if_exists='replace', index=True)
        cursor.execute("INSERT OR IGNORE INTO {}_{}(date, bidopen, bidclose, bidhigh, bidlow, askopen, askclose, askhigh, asklow, tickqty) SELECT date, bidopen, bidclose, bidhigh, bidlow, askopen, askclose, askhigh, asklow, tickqty FROM {}_{}_Temp".format(symbol, interval, symbol, interval))
        connection.commit()
        self.db_close_connection(connection)


    def insert_into_price_data_renko_table(self, data, symbol, renko_range):
        """
        This function insert data to the related price list table
        It recieves data as dataframe and inserts it in a temporary table, and the related price table gets its data from the created temporary table 
        """
        connection, cursor = self.db_open_connection()
        data.to_sql('{}_{}_Temp'.format(symbol, renko_range), con=connection, if_exists='replace', index=True)
        cursor.execute("INSERT OR IGNORE INTO {}_{}(date, bidopen, bidclose, bidhigh, bidlow, tickqty) SELECT date, bidopen, bidclose, bidhigh, bidlow, tickqty FROM {}_{}_Temp".format(symbol, renko_range, symbol, renko_range))
        connection.commit()
        self.db_close_connection(connection)


    def insert_into_account_info_table(self, data):
        """
        This function insert data to account info table
        It function recieves data as dataframe and inserts it in a temporary table, and the account info table gets its data from the created temporary table 
        """
        connection, cursor = self.db_open_connection()
        data.to_sql('Fxcm_Info_Temp', con=connection, if_exists='replace', index=True)
        cursor.execute("INSERT OR IGNORE INTO Fxcm_Info(accountId, accountName, balance, dayPL, equity, grossPL, hedging, mc, mcDate, ratePrecision, t, usableMargin, usableMarginPerc, usableMargin3, usableMargin3Perc, usdMr, usdMr3) SELECT accountId, accountName, balance, dayPL, equity, grossPL, hedging, mc, mcDate, ratePrecision, t, usableMargin, usableMarginPerc, usableMargin3, usableMargin3Perc, usdMr, usdMr3 FROM Fxcm_Info_Temp WHERE accountId=?", (data.accountId.iloc[0],))
        connection.commit()
        self.db_close_connection(connection)


    def insert_into_table(self, table, data):
        """
        Function to input data into a specific table
        Inputs: 
        table->str: name of the table
        data->list: all the required data (must hold the same number of values as columns), ordered by columns
        Output: Imported data to the table
        """
        connection, cursor=self.db_open_connection()
        cursor.execute("PRAGMA table_info({})".format(table))
        number = len(cursor.fetchall())
        values = '(' + '?,'*number
        values = values[:-1]+')'
        statement = "INSERT OR IGNORE INTO {} VALUES"+values
        cursor.execute(statement.format(table), data)
        connection.commit()
        self.db_close_connection(connection)


    def insert_into_open_positions(self, data):
        """
        This function insert data to open positions table
        It function recieves data as dataframe and inserts it in a temporary table, and the OpenPosition table gets its data from the created temporary table 
        Also it creates a record of position tradeId and positionMaker in TradeId_PositionMaker table
        """
        
        connection, cursor = self.db_open_connection()
        data.to_sql('OpenPosition_Temp', con=connection, if_exists='replace', index=True)
        cursor.execute("""INSERT OR REPLACE INTO OpenPosition(t, ratePrecision, tradeId, accountName, accountId, roll, com, open, valueDate, grossPL, close, visiblePL, isDisabled, currency, isBuy, amountK, currencyPoint, time, usedMargin, stop, stopMove, "limit", positionMaker) SELECT t, ratePrecision, tradeId, accountName, accountId, roll, com, open, valueDate, grossPL, close, visiblePL, isDisabled, currency, isBuy, amountK, currencyPoint, time, usedMargin, stop, stopMove, "limit", positionMaker FROM OpenPosition_Temp WHERE tradeId=?""", (str(data.tradeId.iloc[0]),))
        cursor.execute("""INSERT OR IGNORE INTO TradeId_PositionMaker(tradeId, positionMaker) VALUES(?, ?)""", (str(data.tradeId.iloc[0]), str(data.positionMaker.iloc[0])))
        
        connection.commit()
        self.db_close_connection(connection)

    def insert_into_closed_positions(self, data):
        """
        This function insert data to closed positions table
        It function recieves data as dataframe and inserts it in a temporary table, and the ClosedPosition table gets its data from the created temporary table 
        """
        connection, cursor = self.db_open_connection()
        data.to_sql('ClosedPositions_Temp', con=connection, if_exists='replace', index=True)
        cursor.execute("""INSERT OR REPLACE INTO ClosedPosition(t, ratePrecision, tradeId, accountName, roll, com, open, valueDate, grossPL, close, visiblePL, currency, isBuy, amountK, currencyPoint, openTime, closeTime, positionMaker) SELECT t, ratePrecision, tradeId, accountName, roll, com, open, valueDate, grossPL, close, visiblePL, currency, isBuy, amountK, currencyPoint, openTime, closeTime, positionMaker FROM closedPositions_Temp WHERE tradeId=?""", (str(data.tradeId.iloc[0]),))
        connection.commit()
        self.db_close_connection(connection)

    def delete_from_table(self, table, pk_value):
        connection, cursor= self.db_open_connection()
        cursor.execute("PRAGMA table_info({})".format(table))
        tables = cursor.fetchall()
        pk_name = ''
        for x in tables:
            if x[3]==1:
                pk_name = x[1]
                break
        cursor.execute("DELETE FROM {} WHERE {}='{}'".format(table, pk_name, pk_value))
        connection.commit()
        self.db_close_connection(connection)


    def update_account_info_table(self, account_id, data):
        """
        Thsi method updates account info table
        """
        connection, cursor = self.db_open_connection()
        data.to_sql('Fxcm_Info_Temp', con=connection, if_exists='replace', index=True)
        cursor.execute("UPDATE Fxcm_Info SET(accountId, accountName, balance, dayPL, equity, grossPL, hedging, mc, mcDate, ratePrecision, t, usableMargin, usableMarginPerc, usableMargin3, usableMargin3Perc, usdMr, usdMr3)=(SELECT accountId, accountName, balance, dayPL, equity, grossPL, hedging, mc, mcDate, ratePrecision, t, usableMargin, usableMarginPerc, usableMargin3, usableMargin3Perc, usdMr, usdMr3 FROM Fxcm_Info_Temp WHERE accountId=?) WHERE accountId=?", (data.accountId.iloc[0], data.accountId.iloc[0]))
        connection.commit()
        self.db_close_connection(connection)


    def update_open_positions_table(self, data, account_id):
        """
        This method updates OpenPositions table, it recieves data as dataframe
        """
        try:
            #Checing if data is empty, if empty then delete all open positions from table
            if data.empty==False:
                connection, cursor = self.db_open_connection()

                #Deleting positions in db that are not in passed data
                cursor.execute("SELECT tradeId FROM OpenPosition")
                result = cursor.fetchall()
                for i, j in enumerate(result):
                    if str(j[0]) not in data.tradeId.values:
                        cursor.execute("DELETE FROM OpenPosition WHERE tradeId=?", (str(j[0]),))
                connection.commit()
                
                #inserting data to a temporary table
                #OpenPosition table gets its data from the created temporary table 
                data.to_sql('OpenPositions_Temp', con=connection, if_exists='replace', index=True)
                cursor.execute("""INSERT OR IGNORE INTO OpenPosition(t, ratePrecision, tradeId, accountName, accountId, roll, com, open, valueDate, grossPL, close, visiblePL, isDisabled, currency, isBuy, amountK, currencyPoint, time, usedMargin, stop, stopMove, "limit") SELECT t, ratePrecision, tradeId, accountName, accountId, roll, com, open, valueDate, grossPL, close, visiblePL, isDisabled, currency, isBuy, amountK, currencyPoint, time, usedMargin, stop, stopMove, "limit" FROM OpenPositions_Temp""")
                #Updating open positions values
                for i, j in enumerate(data.tradeId):
                    try:                        
                        cursor.execute("""UPDATE OpenPosition SET t=?,
                                                                ratePrecision=?,
                                                                roll=?,
                                                                com=?,
                                                                open=?,
                                                                valueDate=?,
                                                                grossPL=?,
                                                                close=?,
                                                                visiblePL=?,
                                                                isDisabled=?,
                                                                currencyPoint=?,
                                                                time=?,
                                                                usedMargin=?,
                                                                stop=?,
                                                                stopMove=?,
                                                                "limit"=?
                                                                WHERE tradeId=? """, (str(data.t.iloc[i]),str(data.ratePrecision.iloc[i]), str(data.roll.iloc[i]),
                                                                                        str(data.com.iloc[i]), str(data.open.iloc[i]), str(data.valueDate.iloc[i]),
                                                                                        str(data.grossPL.iloc[i]), str(data.close.iloc[i]), str(data.visiblePL.iloc[i]),
                                                                                        str(data.isDisabled.iloc[i]), str(data.currencyPoint.iloc[i]), str(data.time.iloc[i]), 
                                                                                        str(data.usedMargin.iloc[i]), str(data.stop.iloc[i]), str(data.stopMove.iloc[i]),
                                                                                        str(data.limit.iloc[i]), j))
                        
                    
                    
                    except Exception as e:
                        print(e)
                
                connection.commit()
                self.db_close_connection(connection)
            else:
                connection, cursor = self.db_open_connection()
                cursor.execute("DELETE FROM OpenPosition WHERE accountId=?", (str(account_id),))
                connection.commit()
                self.db_close_connection(connection)
        except Exception as e:
            print(e)
            self.db_close_connection(connection)

    def update_closed_positions_table(self, data):
        """
        This method updates ClosedPositions table, it recieves data as dataframe
        """
        try:
            if data.empty==False:
                connection, cursor = self.db_open_connection()
                #inserting data to a temporary table
                #ClosedPosition table gets its data from the created temporary table 
                data.to_sql('ClosedPositions_Temp', con=connection, if_exists='replace', index=True)
                cursor.execute("""INSERT OR IGNORE INTO ClosedPosition(t, ratePrecision, tradeId, accountName, roll, com, open, valueDate, grossPL, close, visiblePL, currency, isBuy, amountK, currencyPoint, openTime, closeTime) SELECT t, ratePrecision, tradeId, accountName, roll, com, open, valueDate, grossPL, close, visiblePL, currency, isBuy, amountK, currencyPoint, openTime, closeTime FROM ClosedPositions_Temp""")
                connection.commit()

                #Updating positionMaker value.
                #It gets positionMaker using position tradeId and uses positionMaker in OpenPosition table to update positionMaker in ClosedPoition table
                for i, j in enumerate(data.tradeId):
                    try:
                        cursor.execute("""UPDATE ClosedPosition SET positionMaker= CASE WHEN (SELECT COUNT(positionMaker) FROM TradeId_PositionMaker WHERE tradeId=?)>0 THEN (SELECT positionMaker FROM TradeId_PositionMaker WHERE tradeId=?) ELSE "Manual" END WHERE tradeId=?""", (str(j), str(j), str(j)))
                        connection.commit()
                    except:
                        pass
                self.db_close_connection(connection)
            else:
                pass
        except Exception as e:
            print(e)
            self.db_close_connection(connection)
            



    def update_table(self, table, pk_value, new_values):
        """
        Function to update a specific row in a specific table
        Inputs: 
        table->str: Name of the desired table
        pk_value->int/float/str: Primary key of the row to be updated
        new_values->list: List of the new values for the select row
        Output: Updated row in a specific table
        """
        connection, cursor= self.db_open_connection()
        cursor.execute("PRAGMA table_info({})".format(table))
        columns = [x[1] for x in cursor.fetchall()]
        cursor.execute("PRAGMA table_info({})".format(table))
        tables = cursor.fetchall()
        pk_name = ''
        for x in tables:
            if x[3]==1:
                pk_name = x[1]
                break
        statement = "UPDATE {} SET "
        next_statement = ', '.join(str(a)+'='+'?' for a, b in zip(columns, new_values))
        statement = statement.format(table)+next_statement+" WHERE {} = ?".format(pk_name)
        new_values.append(pk_value)
        cursor.execute(statement, new_values)
        connection.commit()
        self.db_close_connection(connection)

    def query_table(self, table, columns, fields=None, values=None):
        """
        This method return requested values from relate table
        """

        if values!=None and fields!=None:
            connection, cursor= self.db_open_connection()
            fields='=?, '.join(fields)
            fields=fields+'=?'
            statement = "SELECT {} FROM {} WHERE {} ".format(', '.join(columns), table, fields)
            cursor.execute(statement, values)
            result = cursor.fetchall()
            self.db_close_connection(connection)
            return result
        else:
            return []


    def query_open_positon_dashboard(self):
        """
        This method returns summary of open position data to show in dashboard
        """
        try:
            connection, cursor= self.db_open_connection()
            connection.create_aggregate("count_successful_trades", 1, COUNT_SUCCESSFUL_TRADES) #Adding functions to sqlite
            connection.create_aggregate("count_unsuccessful_trades", 1, COUNT_UNSUCCESSFUL_TRADES) #Adding functions to sqlite

            query = "Select positionMaker, currency, avg(visiblePL), avg(grossPl), max(amountK), avg(amountK), min(amountK), count(tradeId), count_successful_trades(visiblePL), count_unsuccessful_trades(visiblePL)   from OpenPosition group by positionMaker, currency order by visiblePL, grossPL"
            cursor.execute(query)
            result=cursor.fetchall()
            self.db_close_connection(connection)
            return result
        except Exception as e:
            print(e, 'query_open_positon_dashboard')
            self.db_close_connection(connection)
            return []

    def query_closed_positon_dashboard(self):
        """
        This method returns summary of closed position data to show in dashboard
        """
        try:
            connection, cursor= self.db_open_connection()
            connection.create_aggregate("count_successful_trades", 1, COUNT_SUCCESSFUL_TRADES) #Adding functions to sqlite
            connection.create_aggregate("count_unsuccessful_trades", 1, COUNT_UNSUCCESSFUL_TRADES) #Adding functions to sqlite
            
            query = "Select positionMaker, currency, avg(visiblePL), avg(grossPl), max(amountK), min(amountK), avg(amountK), count(tradeId), count_successful_trades(visiblePL), count_unsuccessful_trades(visiblePL)   from ClosedPosition group by positionMaker, currency order by visiblePL, grossPL"
            cursor.execute(query)
            result=cursor.fetchall()
            self.db_close_connection(connection)
            return result
        except Exception as e:
            print(e, 'query_closed_positon_dashboard')
            self.db_close_connection(connection)
            return []



    def query_price_data(self, symbol, interval, quantity=None):
        try:
            """
            Function to query from price data table of given symbol and timeframe
            """
            if quantity==None:
                connection, cursor = self.db_open_connection()
                query=""" SELECT * FROM {} ORDER BY datetime(date) ASC""".format('{}_{}'.format(symbol, interval))
                result=pd.read_sql(query, connection)
                self.db_close_connection(connection)
                return result
            else:
                connection, cursor = self.db_open_connection()
                cursor.execute(""" SELECT COUNT(*) FROM {} """.format('{}_{}'.format(symbol, interval)))
                count=cursor.fetchone()
                count=count[0]
                limit_number=count-quantity
                query=""" SELECT * FROM {} ORDER BY datetime(date) ASC LIMIT ? OFFSET ? """.format('{}_{}'.format(symbol, interval))
                result=pd.read_sql(query, connection, params=(quantity, limit_number))
                self.db_close_connection(connection)
                return result
        except Exception as e:
            print(e, 99999999999999)
            result=pd.DataFrame()
            self.db_close_connection(connection)
            return result



    def query_price_data_renko(self, symbol, renko_range, quantity=None):
        try:
            """
            Function to query from price data table of given symbol and timeframe
            """
            if quantity==None:
                connection, cursor = self.db_open_connection()
                query=""" SELECT * FROM {} ORDER BY datetime(date) ASC""".format('{}_{}'.format(symbol, renko_range))
                result=pd.read_sql(query, connection)
                self.db_close_connection(connection)
                return result
            else:
                connection, cursor = self.db_open_connection()
                cursor.execute(""" SELECT COUNT(*) FROM {} """.format('{}_{}'.format(symbol, renko_range)))
                count=cursor.fetchone()
                count=count[0]
                limit_number=count-quantity
                query=""" SELECT * FROM {} ORDER BY datetime(date) ASC LIMIT ? OFFSET ? """.format('{}_{}'.format(symbol, renko_range))
                result=pd.read_sql(query, connection, params=(quantity, limit_number))
                self.db_close_connection(connection)
                return result
        except Exception as e:
            print(e, 99999999999999)
            result=pd.DataFrame()
            self.db_close_connection(connection)
            return result

    def query_positions_data_chart_annotation(self, account_name, symbol):
        """
        Function to query from OpenPosition and ClosedPosition tables
        to get certain columns to use in chart annotation.
        """
        connection, cursor=self.db_open_connection()
        symbol=list(symbol)
        symbol.insert(3, '/')
        symbol=''.join(symbol)        
        query_open_positions="""SELECT tradeId, time, open, isBuy, positionMaker FROM OpenPosition WHERE accountName=? and currency=?"""
        query_closed_positions="""SELECT tradeId, closeTime, openTime, close, open, isBuy, grossPL, positionMaker FROM ClosedPosition WHERE accountName=? and currency=?"""

        open_position_data=pd.read_sql(query_open_positions, connection, params=(account_name, symbol))
        closed_position_data=pd.read_sql(query_closed_positions, connection, params=(account_name, symbol))

        self.db_close_connection(connection)

        return [open_position_data, closed_position_data]


    def test_print(self):
        
        """
        Supportive function to test DB values from GUI
        Output: Prints rows from the desired table
        """
        connection, cursor=self.db_open_connection()
        cursor.execute("SELECT * FROM Orders")
        print(cursor.fetchall())
        self.db_close_connection(connection)

if __name__ == "__main__":
    a = Db_Controller()
    test = {'t': 1, 'ratePrecision': 5, 'tradeId': '31527682', 'accountName': '05616035', 'accountId': '5616035', 'roll': 0, 'com': 0, 'open': 1.10784, 'valueDate': '', 'grossPL': -0.54242, 'close': 1.10821, 'visiblePL': -3.7, 'isDisabled': False, 'currency': 'EUR/USD', 'isBuy': False, 'amountK': 1, 'currencyPoint': 0.1466, 'time': '10272019090547', 'usedMargin': 4.5, 'stop': 0, 'stopMove': 0, 'limit': 0, 'maker':'mamka'}
    test = [x for x in test.values()]
    test2 = {'t': 1, 'ratePrecision': 6, 'tradeId': '31525', 'accountName': '05665', 'accountId': '65', 'roll': 0, 'com': 0, 'open': 1.10784, 'valueDate': '', 'grossPL': -0.54242, 'close': 1.10821, 'visiblePL': -3.7, 'isDisabled': False, 'currency': 'EUR/USD', 'isBuy': False, 'amountK': 1, 'currencyPoint': 0.1466, 'time': '10272019090547', 'usedMargin': 4.5, 'stop': 0, 'stopMove': 0, 'limit': 0, 'maker':'mamka'}
    test2 = [x for x in test2.values()]
    test3 = {'t': 1, 'ratePrecision': 8, 'tradeId': '3112512525', 'accountName': '034734765', 'accountId': '65', 'roll': 122, 'com': 0, 'open': 1.10784, 'valueDate': '', 'grossPL': -0.54242, 'close': 1.10821, 'visiblePL': -3.7, 'isDisabled': False, 'currency': 'EUR/USD', 'isBuy': False, 'amountK': 1, 'currencyPoint': 0.1466, 'time': '10272019090547', 'usedMargin': 4.5, 'stop': 0, 'stopMove': 0, 'limit': 0, 'maker':'mamka'}
    test3 = [x for x in test3.values()]
    a.insert_into_table('Open_Positions', test)
    a.insert_into_table('Open_Positions', test2)
    a.update_table('Open_Positions', '31525', test3)
    a.insert_into_table('Open_Positions', test2)
    #a.update_table('Users', test2)
    a.test_print()

