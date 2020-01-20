from currency_converter import CurrencyConverter

trading_instruments_dict={
                            'forex':['AUD/CAD','AUD/CHF','AUD/JPY','AUD/NZD','AUD/USD','CAD/CHF','CAD/JPY',
                                    'CHF/JPY','EUR/AUD','EUR/CAD','EUR/CHF','EUR/GBP','EUR/JPY','EUR/NOK','EUR/NZD',
                                    'EUR/SEK','EUR/TRY','EUR/USD','GBP/AUD','GBP/CAD','GBP/CHF','GBP/JPY','GBP/NZD',
                                    'GBP/USD','NZD/CAD','NZD/CHF','NZD/JPY','NZD/USD','TRY/JPY','USD/CAD','USD/CHF',
                                    'USD/CNH','USD/JPY','USD/MXN','USD/NOK','USD/SEK','USD/TRY','USD/ZAR','ZAR/JPY'],
                            'commodity':['NGAS', 'UKOil', 'USOil', 'Copper', 'XAG/USD', 'XAU/USD', 'CORNF', 'SOYF', 'WHEATF'],
                            'indices':[],
                            'cryptocurrency':[]

                        }

def pip_value_cal(symbol, account_currency, price, position_size):
    if account_currency!=symbol[:3]:
        if symbol[3:]=='JPY':
            c = CurrencyConverter()
            return c.convert((0.01/price)*position_size, symbol[:3], account_currency)
        else:    
            c = CurrencyConverter()
            return c.convert((0.0001/price)*position_size, symbol[:3], account_currency)
    else:
        if symbol[3:]=='JPY':
            return (0.01/price)*position_size
        else:    
            return (0.0001/price)*position_size


def leverage_cal(symbol, equity):
    if equity>20000:
        if symbol in trading_instruments_dict['forex']:
            return 200
        else:
            return 100 
    else:
        if symbol in trading_instruments_dict['forex']:
            return 400
        else:
            return 200 


if __name__=='__main__':
    print(pip_value_cal('EURUSD', 'AUD', 1.1116, 10000))




