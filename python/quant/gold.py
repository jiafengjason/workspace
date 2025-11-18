import os
import numpy as np
import pandas as pd
import pandas_datareader.data as web
import matplotlib.pyplot as plt
import yfinance as yf

# 设置代理服务器的地址和端口
proxy_address = "http://192.168.74.10:9910"
 
# 设置环境变量
os.environ['HTTP_PROXY'] = proxy_address
os.environ['HTTPS_PROXY'] = proxy_address
  
# 获取黄金价格数据
if os.path.exists('gold.csv'):
    df = pd.read_csv('gold.csv')
else:
    start = '2024-01-01'
    end = '2024-11-15'
    #df = web.DataReader('GC=F', 'yahoo', start, end)
    df = yf.download('GC=F', start=start, end=end)
    df.to_csv('gold.csv', index=True)

print(df)

# 计算短期和长期均线
df['SMA20'] = df['Close'].rolling(window=20).mean()
df['SMA30'] = df['Close'].rolling(window=30).mean()
df['SMA50'] = df['Close'].rolling(window=50).mean()
df['SMA100'] = df['Close'].rolling(window=100).mean()

# 生成买卖信号
df['signal'] = 0
df['signal'][20:] = np.where(df['SMA20'][20:] > df['SMA50'][20:], 1, 0)  # 买入信号为1，卖出信号为0
df['OpenInterest'] = df['signal'].diff()  # 根据信号变化生成仓位（买入或卖出）

df.to_csv('signal.csv', index=False)

# 绘制价格和移动平均线  
plt.figure(figsize=(10, 5))  
plt.plot(df.index, df['Close'], label='df Price')
plt.plot(df.index, df['SMA30'], label='SMA 30')
plt.plot(df.index, df['SMA100'], label='SMA 100')
plt.legend()  
plt.show()

 
