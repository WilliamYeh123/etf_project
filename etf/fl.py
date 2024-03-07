import yfinance as yf
import os
from pathlib import Path
import datetime
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from FinMind.data import DataLoader
import matplotlib.pyplot as plt

#api_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJkYXRlIjoiMjAyMS0xMi0yNyAxNDo1OTowOSIsInVzZXJfaWQiOiJkdXJhbnQ3MTA5MTYiLCJpcCI6IjE0MC4xMjAuMTMuMjMwIn0.8-KIC3-OA4D6JcOtQ_fJBOVkyugx60t1Gy82c57TLz4"
api_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRlIjoiMjAyNC0wMy0wNiAxNDozMDozMSIsInVzZXJfaWQiOiJXaWxsaWFtWWVoIiwiaXAiOiI2MS4yMjAuOTMuMSJ9.L019gncpo4SWMS-F2eLoY8yx-3Y7Yl3B3lYJCsmKtYw'
api = DataLoader()
api.login_by_token(api_token = api_token)

today = datetime.date.today()
end = today - datetime.timedelta(days=1)
start = end - datetime.timedelta(days=365*3.5)

#etf1 = ['0050','0051','0056', '00850', '006205', '00645', '00646', '00662', '00631L', '00632R', '00633L', '00634R', '008201', '00635U', '00642U', '00673R', '00674R']
df = pd.read_csv("etf/ETF_list.csv")
id_list = df[:]['Number'].values.tolist()
etf_list = ['006208','00692','00900','00903','00730','00897','0052','00645','00662','00700','00709','00731','00636','00701','00875','00878','00881','00893','00861','00932','00921','006206']
stock_list = ['1102','1216','1301','1504','2002','2049','2303','2308','2317','2324','2330','2353','2356','2357','2382','2409','2454','2886','3231','8299']
stock_list = ['006208']
def draw_fl(df,name):
    plt.figure(figsize=(12, 6))
    for column, color in zip(df.columns, ['blue', 'green', 'red', 'cyan', 'magenta', 'yellow']):
        plt.plot(df.index, df[column], label=column, color=color)

    # Add legend and labels
    plt.legend()
    plt.xlabel('Index')
    plt.ylabel('Value')
    plt.title('Graph with Different Colors for Each Column')
    plt.show()
    plt.savefig(f'images/{name}_fl.png')

def draw_stock(id):
    TaiwanStockTotalReturnIndex = api.taiwan_stock_daily(
        stock_id=id,
        start_date = start,
        end_date = end
    )
    df = TaiwanStockTotalReturnIndex
    df2,beta = five_line(df)
    beta = beta.tolist()
    beta = beta[0][0]
    slope.append([id,beta])
    etf_data[id] = df2
    draw_fl(df2)
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

etf_data = {}
slope = []
reply = ''
def fiveline(type):
    if type == 'etf':
        id_list = etf_list
    elif type == 'stock':
        id_list = stock_list
    for id in id_list:
        #print(id)
        TaiwanStockTotalReturnIndex = api.taiwan_stock_daily(
            stock_id=id,
            start_date = start,
            end_date = end
        )
        df = TaiwanStockTotalReturnIndex
        #print(df)
        df2,beta = five_line(df)
        #a = copy.deepcopy(beta[0][0])
        print(df2)
        beta = beta.tolist()
        #print(beta)
        beta = beta[0][0]
        #print(beta)
        slope.append([id,beta])
        #print(slope)
        etf_data[id] = df2
        draw_fl(df2)

    #print(slope)
    return_data = []
    slope.sort(key = lambda s: s[1])
    slope.reverse()
    for i in slope:
        print(i[0])
        if len(return_data) == 5:
            break
        temp_data = etf_data[i[0]]
        #print(temp_data)
        #price = stock_price(i[0])
        price = temp_data.iloc[-1]['close']
        # print(temp_data.iat[-1,-6])
        # print(temp_data.iat[-1,-2])
        # print('------------------')
        if temp_data.iat[-1,-6] < temp_data.iat[-1,-2]:
            #print('============')
            #reply = i[0]+'.TW低於悲觀線，股票價格 : '+price+'，可買進'
            i.append(price)
            return_data.append(i)
            #return reply
        else:continue
    #print(return_data)
    reply = ''
    for data in return_data:
        reply += f'{data[0]}低於悲觀線，股票價格 : {price}，可買進\n'
    if reply == '':
        return 'none'
    else:
        return reply
print(fiveline('stock'))

