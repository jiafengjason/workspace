import os
import talib
import pybroker
import numpy as np
from numba import njit
from pybroker import Strategy, StrategyConfig, YFinance, highest

proxy_address = "http://192.168.74.10:9910"
os.environ['HTTP_PROXY'] = proxy_address
os.environ['HTTPS_PROXY'] = proxy_address

pybroker.enable_indicator_cache('my_indicators')
pybroker.enable_data_source_cache('yfinance')
#pybroker.clear_data_source_cache()
#pybroker.disable_data_source_cache()

def exec_fn(ctx):
   # Get the rolling 10 day high.
   high_10d = ctx.indicator('high_10d')
   # Buy on a new 10 day high.
   if not ctx.long_pos() and high_10d[-1] > high_10d[-2]:
      ctx.buy_shares = 100
      # Hold the position for 5 days.
      ctx.hold_bars = 5
      # Set a stop loss of 2%.
      ctx.stop_loss_pct = 2

def buy_low(ctx):
    # If shares were already purchased and are currently being held, then return.
    if ctx.long_pos():
        return
    # If the latest close price is less than the previous day's low price,
    # then place a buy order.
    if ctx.bars >= 2 and ctx.close[-1] < ctx.low[-2]:
        # Buy a number of shares that is equal to 25% the portfolio.
        ctx.buy_shares = ctx.calc_target_shares(0.25)
        # Set the limit price of the order.
        ctx.buy_limit_price = ctx.close[-1] - 0.01
        # Hold the position for 3 bars before liquidating (in this case, 3 days).
        ctx.hold_bars = 3

def short_high(ctx):
    # If shares were already shorted then return.
    if ctx.short_pos():
        return
    # If the latest close price is more than the previous day's high price,
    # then place a sell order.
    if ctx.bars >= 2 and ctx.close[-1] > ctx.high[-2]:
        # Short 100 shares.
        ctx.sell_shares = 100
        # Cover the shares after 2 bars (in this case, 2 days).
        ctx.hold_bars = 2

def buy_highest_volume(ctx):
    # If there are no long positions across all tickers being traded:
    if not tuple(ctx.long_positions()):
        ctx.buy_shares = ctx.calc_target_shares(1)
        ctx.hold_bars = 2
        ctx.score = ctx.volume[-1]

def pos_size_handler(ctx):
    # Fetch all buy signals.
    signals = tuple(ctx.signals("buy"))
    # Return if there are no buy signals (i.e. there are only sell signals).
    if not signals:
        return
    # Calculates the inverse volatility, where volatility is defined as the
    # standard deviation of close prices for the last 100 days.
    get_inverse_volatility = lambda signal: 1 / np.std(signal.bar_data.close[-100:])
    # Sums the inverse volatilities for all of the buy signals.
    total_inverse_volatility = sum(map(get_inverse_volatility, signals))
    for signal in signals:
        size = get_inverse_volatility(signal) / total_inverse_volatility
        # Calculate the number of shares given the latest close price.
        shares = ctx.calc_target_shares(size, signal.bar_data.close[-1], cash=95_000)
        ctx.set_shares(signal, shares)

def cmma(bar_data, lookback):
    @njit  # Enable Numba JIT.
    def vec_cmma(values):
        # Initialize the result array.
        n = len(values)
        out = np.array([np.nan for _ in range(n)])

        # For all bars starting at lookback:
        for i in range(lookback, n):
            # Calculate the moving average for the lookback.
            ma = 0
            for j in range(i - lookback, i):
                ma += values[j]
            ma /= lookback
            # Subtract the moving average from value.
            out[i] = values[i] - ma
        return out

    # Calculate with close prices.
    return vec_cmma(bar_data.close)

def buy_cmma_cross(ctx):
    if ctx.long_pos():
        return
    # Place a buy order if the most recent value of the 20 day CMMA is < 0:
    if ctx.indicator('cmma_20')[-1] < 0:
        ctx.buy_shares = ctx.calc_target_shares(1)
        ctx.hold_bars = 3

#config = StrategyConfig(initial_cash=500_000, bootstrap_sample_size=100)
config = StrategyConfig(max_long_positions=1)
strategy = Strategy(YFinance(), '1/1/2020', '11/10/2024', config)
#strategy.add_execution(exec_fn, ['AAPL', 'MSFT'], indicators=highest('high_10d', 'close', period=10))
#strategy.add_execution(buy_low, ['AAPL', 'MSFT'])
#strategy.add_execution(short_high, ['TSLA'])
#strategy.add_execution(buy_highest_volume, ['T', 'F', 'GM', 'PFE'])
#strategy.set_pos_size_handler(pos_size_handler)
cmma_20 = pybroker.indicator('cmma_20', cmma, lookback=20)
rsi_20 = pybroker.indicator('rsi_20', lambda data: talib.RSI(data.close, timeperiod=20))
strategy.add_execution(buy_cmma_cross, 'PG', indicators=rsi_20)

# Run the backtest after 20 days have passed.
result = strategy.backtest(warmup=20)
#result = strategy.backtest(calc_bootstrap=True)
#result = strategy.backtest()
print(result.trades)
#print(result.portfolio['market_value'])
#print(result.positions)
#print(result.orders)
print(result.metrics_df.round(4))
#print(result.bootstrap.conf_intervals)
#print(result.bootstrap.drawdown_conf)