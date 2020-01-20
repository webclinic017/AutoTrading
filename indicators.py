"""
This file includes function for calculating indicators
"""


import numpy as np
import pandas as pd
from pyti.simple_moving_average import simple_moving_average as sma
from pyti.exponential_moving_average import exponential_moving_average as ema
from pyti.bollinger_bands import upper_bollinger_band as bbu
from pyti.bollinger_bands import lower_bollinger_band as bbl
from pyti.chaikin_money_flow import chaikin_money_flow as cmf
from pyti.average_true_range import average_true_range as atr
from pyti.aroon import aroon_up, aroon_down
from pyti.bollinger_bands import upper_bollinger_band, lower_bollinger_band
from pyti.triple_exponential_moving_average import triple_exponential_moving_average as tema
from pyti.smoothed_moving_average import smoothed_moving_average
from pyti.moving_average_convergence_divergence import moving_average_convergence_divergence as macd
from pyti.weighted_moving_average import weighted_moving_average as vma
from pyti.price_channels import upper_price_channel as upc
from pyti.price_channels import lower_price_channel as lpc
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures


import warnings
warnings.filterwarnings("ignore")

pd.options.mode.chained_assignment = None
np.seterr(divide='ignore', invalid='ignore')



def donchian_channel(data, period):
    donchian_channel_up=[]
    donchian_channel_down=[]
    donchian_channel_middle=[]
    for i, j in enumerate(data.bidclose):
        if i<period:
            donchian_channel_up.append(0)
            donchian_channel_down.append(0)
            donchian_channel_middle.append(0)
        elif i>=period and i<len(data.bidclose)-1:
            donchian_channel_up.append(max(data.bidhigh.iloc[i-period:i+1]))
            donchian_channel_down.append(min(data.bidlow.iloc[i-period:i+1]))
            donchian_channel_middle.append((donchian_channel_up[-1]+donchian_channel_down[-1])/2)
        else:
            donchian_channel_up.append(max(data.bidhigh.iloc[i-period:]))
            donchian_channel_down.append(min(data.bidlow.iloc[i-period:]))
            donchian_channel_middle.append((donchian_channel_up[-1]+donchian_channel_down[-1])/2)
            
    return donchian_channel_up, donchian_channel_down, donchian_channel_middle



def linear_regression_channel_indicator(data, period, standard_deviation):
    try:
        x = data.index.values.reshape(-1,1)
        x=x.astype(float)
        y = data.bidclose.values.reshape(-1,1)
        reg = LinearRegression()
        reg.fit(x, y)
        predictions = reg.predict(x)
        linear_regression=predictions.flatten()
        standard_deviation=np.std(y)*standard_deviation
        upper_line=linear_regression+standard_deviation
        lower_line=linear_regression-standard_deviation
        
        if len(linear_regression)>0:
            slope=round(((linear_regression[-1]-linear_regression[0])/period)*100, 8)
        else:
            slope=float(0)
        channel_width=upper_line[-1]-lower_line[-1]
        return linear_regression, upper_line, lower_line, slope, channel_width
    except:
        slope=float(0)
        return linear_regression, upper_line, lower_line, slope, channel_width


def polinomial_linear_regression_channel_indicator(data, period, degree, standard_deviation):
    try:
        x = np.array(range(len(data.index[:]))).reshape(-1,1)
        y = data.bidclose.values.reshape(-1,1)
        poly_reg = PolynomialFeatures(degree=degree)
        X_poly = poly_reg.fit_transform(x)
        reg = LinearRegression()
        reg.fit(X_poly, y)
        predictions = reg.predict(poly_reg.fit_transform(x))
        linear_regression=predictions.flatten()
        standard_deviation=np.std(y)*standard_deviation
        upper_line=linear_regression+standard_deviation
        lower_line=linear_regression-standard_deviation
        
        if len(linear_regression)>0:
            slope=round(((linear_regression[-1]-linear_regression[0])/period)*100, 8)
        else:
            slope=float(0)
        channel_width=upper_line[-1]-lower_line[-1]
        return linear_regression, upper_line, lower_line, slope, channel_width
    except Exception as e:
        print(e)
        slope=float(0)
        return linear_regression, upper_line, lower_line, slope, channel_width
    


def vidya(data, short_period, long_period):
    vidya_list=[]
    for i, j in enumerate(data.bidclose):
        if i<long_period:
           vidya_list.append(0)
        elif i>=long_period and i<len(data.bidclose)-1:
            alpha=0.2*((data.bidclose.iloc[i-short_period:i+1].values.std(ddof=1))/(data.bidclose.iloc[i-long_period:i+1].values.std(ddof=1)))
            vidya_list.append(alpha*data.bidclose.iloc[i]+(1-alpha)*vidya_list[-1])
        else:
            alpha=0.2*((data.bidclose.iloc[i-short_period:].values.std(ddof=1))/(data.bidclose.iloc[i-long_period:].values.std(ddof=1)))
            vidya_list.append(alpha*data.bidclose.iloc[i]+(1-alpha)*vidya_list[-1])
    return vidya_list
    


def ssl_vidya(data, short_period, long_period):
    vidya_list_high=[]
    vidya_list_low=[]
    for i, j in enumerate(data.bidclose):
        if i<long_period:
           vidya_list_high.append(0)
           vidya_list_low.append(0)
        elif i>=long_period and i<len(data.bidclose)-1:
            alpha=0.2*((data.bidhigh.iloc[i-short_period:i+1].values.std(ddof=1))/(data.bidhigh.iloc[i-long_period:i+1].values.std(ddof=1)))
            vidya_list_high.append(alpha*data.bidhigh.iloc[i]+(1-alpha)*vidya_list_high[-1])
            
            alpha=0.2*((data.bidlow.iloc[i-short_period:i+1].values.std(ddof=1))/(data.bidlow.iloc[i-long_period:i+1].values.std(ddof=1)))
            vidya_list_low.append(alpha*data.bidhigh.iloc[i]+(1-alpha)*vidya_list_low[-1])
            
        else:
            alpha=0.2*((data.bidhigh.iloc[i-short_period:].values.std(ddof=1))/(data.bidhigh.iloc[i-long_period:].values.std(ddof=1)))
            vidya_list_high.append(alpha*data.bidhigh.iloc[i]+(1-alpha)*vidya_list_high[-1])
            
            alpha=0.2*((data.bidlow.iloc[i-short_period:].values.std(ddof=1))/(data.bidlow.iloc[i-long_period:].values.std(ddof=1)))
            vidya_list_low.append(alpha*data.bidlow.iloc[i]+(1-alpha)*vidya_list_low[-1])
            
        
    ssl_vidya_list=[]
    for i, j in enumerate(data.bidclose):
        hlv = 1 if j > vidya_list_high[i] else -1
        
        if hlv == -1:
            ssl_vidya_list.append(vidya_list_high[i])
    
        elif hlv == 1:
            ssl_vidya_list.append(vidya_list_low[i])

    
    return ssl_vidya_list


def adx(data, n, n_ADX):
    """Calculate the Average Directional Movement Index for given data.
    """
    i = 0
    UpI = []
    DoI = []
    TR_l = []
    for i, j in enumerate(data.bidclose):
        if i==0:
            UpI.append(0)
            DoI.append(0)
            TR_l.append(0)
        else:
            UpMove = data.bidhigh.iloc[i] - data.bidhigh.iloc[i-1]
            DoMove = data.bidlow.iloc[i-1] - data.bidlow.iloc[i]
            if UpMove > DoMove and UpMove > 0:
                UpD = UpMove
            else:
                UpD = 0
            UpI.append(UpD)
            if DoMove > UpMove and DoMove > 0:
                DoD = DoMove
            else:
                DoD = 0
            TR = max(data.bidhigh.iloc[i]-data.bidlow.iloc[i], data.bidhigh.iloc[i]-data.bidclose.iloc[i-1], data.bidclose.iloc[i-1]-data.bidlow.iloc[i])    
            
            DoI.append(DoD)
            TR_l.append(TR)
            
    TR_s = pd.Series(TR_l)
    UpI = pd.Series(UpI)
    DoI = pd.Series(DoI)
    ATR = pd.Series(TR_s.ewm(span=n, min_periods=n).mean())
    PosDI = pd.Series((UpI.ewm(span=n, min_periods=n).mean() / ATR)*100)
    NegDI = pd.Series((DoI.ewm(span=n, min_periods=n).mean() / ATR)*100)

    DX = pd.Series((abs(PosDI - NegDI) / (PosDI + NegDI))*100)
    DX=DX.values
    DX=list(DX)
    final_adx=[]
    for i, j in enumerate(DX):
        if i==0:
            final_adx.append(0)
        else:
            if str(j)!='nan':
                try:
                    final_adx.append(((final_adx[-1]*(n_ADX-1))+j)/n_ADX)
                except:
                    final_adx.append(0)
            else:
                final_adx.append(0)
    return final_adx


def kijunsen(data, period):
    kijunsen_list=[]
    for i, j in enumerate(data.bidclose):
        if i<period:
            kijunsen_list.append(0)
        elif i>=period and i!=len(data.bidclose)-1:
            kijunsen_list.append((max(data.bidhigh.iloc[i-period:i+1])+min(data.bidlow.iloc[i-period:i+1]))/2)
        else:
            kijunsen_list.append((max(data.bidhigh.iloc[i-period:])+min(data.bidlow.iloc[i-period:]))/2)
    return kijunsen_list

def mfi(data):
    mfi=[]
    for i, j in enumerate(data.tickqty):
        mfi.append((data.bidhigh.iloc[i]-data.bidlow.iloc[i])/j)
    return mfi


def ssl(data, period):
    ssl_list=[]

    high_ma = sma(list(data.bidhigh), period=period)
    low_ma = sma(list(data.bidlow), period=period)
    data['ssl_high_ma']=high_ma
    data['ssl_low_ma']=low_ma
    
    for i, j in enumerate(data.bidclose):
        hlv = 1 if j > data.ssl_high_ma.iloc[i] else -1
        
        if hlv == -1:
            ssl_list.append(data['ssl_high_ma'].iloc[i])
    
        elif hlv == 1:
            ssl_list.append(data['ssl_low_ma'].iloc[i])
    
    return ssl_list


def r_percent(data, period):
    """
    Williams %R.
    Formula:
    wr = (HighestHigh - close / HighestHigh - LowestLow) * -100
    """
    wr=[]
    for i, j in enumerate(data.bidclose):
        try:
            if i<period:
                wr.append(-50)
            elif i>=period and i<(len(data.bidclose)-1):
                hp=max(data.bidhigh.iloc[i-period:i+1])
                lp=min(data.bidlow.iloc[i-period:i+1])
                wr.append(((hp - j) / (hp - lp)) * -100)
            else:
                hp=max(data.bidhigh.iloc[i-period:])
                lp=min(data.bidlow.iloc[i-period:])
                wr.append(((hp - j) / (hp - lp)) * -100)
        except:
            wr.append(-50)
    return wr



def fisher(data, period):
    fisher_list=[]
    trigger_list=[]
    hl_list=[]
    val_list=[]
    for i, j in enumerate(data.bidhigh):
        hl_list.append((data.bidhigh.iloc[i]+data.bidlow.iloc[i])/2)
        
    for i, j in enumerate(data.bidhigh):
        if i<period:
            fisher_list.append(0)
            trigger_list.append(0)
            
        elif i==period:
            maxi=max(hl_list[i-period:i+1])
            mini=min(hl_list[i-period:i+1])
            val=0.33*2*(((hl_list[i]-mini)/(maxi-mini))-0.5)+0.67*1
            if val>0.9999:
                val=0.9999
            elif val<-0.9999:
                val=-0.9999
            val_list.append(val)
            fisher_list.append(round(0.5*np.log((1+val_list[-1])/(1-val_list[-1]))+0.5*1, 4))
            trigger_list.append(fisher_list[-2])
        
        elif i>period and i<len(data.bidhigh)-1:
            maxi=max(hl_list[i-period:i+1])
            mini=min(hl_list[i-period:i+1])
            val=0.33*2*(((hl_list[i]-mini)/(maxi-mini))-0.5)+0.67*val_list[-1]
            if val>0.9999:
                val=0.9999
            elif val<-0.9999:
                val=-0.9999
            val_list.append(val)
            fisher_list.append(round(0.5*np.log((1+val_list[-1])/(1-val_list[-1]))+0.5*fisher_list[-1], 4))
            trigger_list.append(fisher_list[-2])
            
        elif i==len(data.bidclose)-1:
            maxi=max(hl_list[i-period:])
            mini=min(hl_list[i-period:])
            val=0.33*2*(((hl_list[i]-mini)/(maxi-mini))-0.5)+0.67*val_list[-1]
            if val>0.9999:
                val=0.9999
            elif val<-0.9999:
                val=-0.9999
            val_list.append(val)
            fisher_list.append(round(0.5*np.log((1+val_list[-1])/(1-val_list[-1]))+0.5*fisher_list[-1], 4))
            trigger_list.append(fisher_list[-2])
            
    return fisher_list, trigger_list
                

def stochastic_k(data, period, periodK):

    stoch_k_list=[]
    for i, j in enumerate(data.bidclose):
        if i<period-1:
            stoch_k_list.append(0)
        elif i==period-1:
            stoch_k_list.append(round(100*((data.bidclose.iloc[i]-min(data.bidclose[:period]))/(max(data.bidclose[:period])-min(data.bidclose[:period]))), 4))
        elif i>period-1 and i<len(data.bidclose)-1:
            stoch_k_list.append(round(100*((data.bidclose.iloc[i]-min(data.bidclose[i-period:i+1]))/(max(data.bidclose[i-period:i+1])-min(data.bidclose[i-period:i+1]))), 4))
        elif i==len(data.bidclose)-1:
            stoch_k_list.append(round(100*((data.bidclose.iloc[i]-min(data.bidclose[i-period:]))/(max(data.bidclose[i-period:])-min(data.bidclose[i-period:]))), 4))
        
    k=sma(stoch_k_list, periodK)

    return k



