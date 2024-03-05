import yfinance as yf
import os
from pathlib import Path
import datetime
import pandas as pd
import numpy as np
import datetime,time,re
from sklearn.linear_model import LinearRegression
import requests
from bs4 import BeautifulSoup
from FinMind.data import DataLoader

api_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJkYXRlIjoiMjAyMS0xMi0yNyAxNDo1OTowOSIsInVzZXJfaWQiOiJkdXJhbnQ3MTA5MTYiLCJpcCI6IjE0MC4xMjAuMTMuMjMwIn0.8-KIC3-OA4D6JcOtQ_fJBOVkyugx60t1Gy82c57TLz4"

api = DataLoader()
api.login_by_token(api_token = api_token)

today = datetime.date.today()
end = today - datetime.timedelta(days=1)
start = end - datetime.timedelta(days=365*3.5)

#etf1 = ['0050','0051','0056', '00850', '006205', '00645', '00646', '00662', '00631L', '00632R', '00633L', '00634R', '008201', '00635U', '00642U', '00673R', '00674R']
df = pd.read_csv("etf/ETF_list.csv")
id_list = df[:]['Number'].values.tolist()
#print(id_list)

def five_line(data):
    timetrend = list(range(1, data.shape[0]+1))
    data['timetrend'] = timetrend
    data = data[['timetrend','close']]
    data = data.dropna()
    reg = LinearRegression()
    x = data['timetrend'].to_frame()
    y = data['close'].to_frame()
    reg.fit(x,y)
    
    a = reg.intercept_ #截距
    beta = reg.coef_ #斜率
    #print(beta)
    #beta = beta[0][0]
    #print(beta)
    longtrend = a + beta*x
    res = np.array(list(data['close'])) - np.array(list(longtrend['timetrend']))
    std = np.std(res,ddof=1)
    fiveline = pd.DataFrame()
    fiveline['highest'] = longtrend['timetrend'] + (2*std)
    fiveline['high'] = longtrend['timetrend'] + (1*std)
    fiveline['TL'] = longtrend['timetrend']
    fiveline['low'] = longtrend['timetrend'] - (1*std)
    fiveline['lowest'] = longtrend['timetrend'] - (2*std) 
    use_fiveline = pd.merge(data, fiveline[['highest','high','TL','low','lowest']], left_index=True, right_index=True, how='left')
    pick_fiveline = use_fiveline[['close','highest','high','TL','low','lowest']]
    return pick_fiveline,beta

def stock_price(stock:str):
    headers={
        "User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36"
    }

    data = requests.get(f"https://finance.yahoo.com/quote/{stock}.TW?p={stock}.TW", headers = headers)
    soup = BeautifulSoup(data.text)
    price = soup.find('fin-streamer',{'class':'Fw(b) Fz(36px) Mb(-4px) D(ib)'})
    return price.text

etf_data = {}
slope = []
reply = ''
def fiveline():
    for id in id_list:
        TaiwanStockTotalReturnIndex = api.taiwan_stock_daily(
            stock_id=id,
            start_date = start,
            end_date = end
        )
        df = TaiwanStockTotalReturnIndex
        df2,beta = five_line(df)
        #a = copy.deepcopy(beta[0][0])
        #print(beta)
        beta = beta.tolist()
        #print(beta)
        beta = beta[0][0]
        #print(beta)
        slope.append((id,beta))
        #print(slope)
        etf_data[id] = df2

    #print(slope)
    slope.sort(key = lambda s: s[1])
    slope.reverse()
    for i in slope:
        temp_data = etf_data[i[0]]
        #print(temp_data)
        price = stock_price(i[0])
        if temp_data.iat[-1,-6] < temp_data.iat[-1,-2]:
            reply = i[0]+'.TW低於悲觀線，股票價格 : '+price+'，可買進'
            return reply
        else:continue
    return 'none'
fiveline()