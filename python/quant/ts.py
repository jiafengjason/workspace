import tushare as ts

pro = ts.pro_api('f34de100f0f8f4a4cf9eb5ef6473430ccdafd41320e2168d84585dd3')

def get_daily(ts_code='', trade_date='', start_date='', end_date=''):
    for _ in range(3):
        try:
            if trade_date:
                df = pro.daily(ts_code=ts_code, trade_date=trade_date)
            else:
                df = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
        except:
            time.sleep(1)
        else:
            return df

df = pro.trade_cal(exchange='SSE', is_open='1', 
                            start_date='20241115', 
                            end_date='20241118', 
                            fields='cal_date')
for date in df['cal_date'].values:
    print(date)
    df = get_daily('000001.SZ', date)
    print(df)