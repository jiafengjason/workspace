from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import os
import pandas as pd
import backtrader as bt
import yfinance as yf

class TestStrategy(bt.Strategy):
    params = (
        ('exitbars', 5),
        ('mashortperiod', 20),
        ('malongperiod', 50),
        ('printlog', False),
    )

    """创建策略（继承bt.Strategy）"""
    def log(self, txt, dt=None, doprint=False):
        ''' 这个策略的日志函数（输出信息）'''
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        """保存一个原数据中close的副本（便于比较）"""
        self.dataclose = self.datas[0].close
        self.order = None
        self.buyprice = None
        self.buycomm = None
        # Add a MovingAverageSimple indicator
        self.smashort = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.mashortperiod)
        self.smalong = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.malongperiod)

        # Indicators for the plotting show
        '''
        bt.indicators.ExponentialMovingAverage(self.datas[0], period=25)
        bt.indicators.WeightedMovingAverage(self.datas[0], period=25,
                                            subplot=True)
        bt.indicators.StochasticSlow(self.datas[0])
        bt.indicators.MACDHisto(self.datas[0])
        rsi = bt.indicators.RSI(self.datas[0])
        bt.indicators.SmoothedMovingAverage(rsi, period=10)
        bt.indicators.ATR(self.datas[0], plot=False)
        '''

    def notify_order(self, order):
        """订单状态的更改将通过notify方法通知给策略Strategy"""
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        """检查一个订单order是否完成completed，当cash本金不够时，broker经纪人可以拒绝订单"""
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            elif order.issell():
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

            self.bar_executed = len(self)# 衡量已经执行过几个k线柱/ticks（系统时钟周期）
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
        """执行完之后，将order重新标记为none，标明没有待执行订单"""
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose[0])
        
        # 检查订单是否待执行，如果待执行，不能发送第二个订单
        if self.order:
            return

        # 如果仓位为空（有本金 但是还没有买证券，没有进行市场进行交易的权利，只能买）
        if not self.position:
            #如果连续三天跌，就买
            #if (self.dataclose[0] < self.dataclose[-1]) and (self.dataclose[-1] < self.dataclose[-2]):
            #if self.dataclose[0] > self.smashort[0]:
            if self.smashort[0] > self.smalong[0]:
                    self.log('BUY CREATE, %.2f' % self.dataclose[0])
                    self.buy()
        else:
            # 已经在市场中（有可以交易的证券了）才可以卖
            # 经过5个k线柱之后，不管涨跌都卖
            #if len(self) >= (self.bar_executed + self.params.exitbars):
            #if self.dataclose[0] < self.smashort[0]:
            if self.smashort[0] < self.smalong[0]:
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                # 继续追踪避免产生第二个订单
                self.order = self.sell()

    def stop(self):
        self.log('(MA Short Period %2d, Long Period %2d) Ending Value %.2f' %
                 (self.params.mashortperiod, self.params.malongperiod, self.broker.getvalue()), doprint=True)

if __name__ == '__main__':
    cerebro = bt.Cerebro()

    """添加策略 虽然那个策略就是打印信息，剩下啥都没干"""
    #cerebro.addstrategy(TestStrategy)
    strats = cerebro.optstrategy(TestStrategy, mashortperiod=range(10, 31), malongperiod=range(50, 80))

    # Create a Data Feed
    df = None
    if os.path.exists('gold.csv'):
        df = pd.read_csv('gold.csv')
    else:
        proxy_address = "http://192.168.74.10:9910"
        os.environ['HTTP_PROXY'] = proxy_address
        os.environ['HTTPS_PROXY'] = proxy_address
        start = '2024-01-01'
        end = '2024-11-15'
        df = yf.download('GC=F', start=start, end=end)
        df.to_csv('gold.csv', index=True)
    df['Datetime'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')
    df.set_index('Datetime', inplace=True)
    data = bt.feeds.PandasData(dataname=df)
    
    # Add the Data Feed to Cerebro
    cerebro.adddata(data)
    
    # Set our desired cash start
    cerebro.broker.setcash(100000.0)

    # Add a FixedSize sizer according to the stake
    cerebro.addsizer(bt.sizers.FixedSize, stake=10)

    # Set the commission - 0.1% ... divide by 100 to remove the %
    cerebro.broker.setcommission(commission=0.001)

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    cerebro.run(maxcpus=8)

    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    #cerebro.plot()
