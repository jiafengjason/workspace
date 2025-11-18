import ccxt
import os

proxy_address = "http://192.168.74.10:9910"

#print(ccxt.exchanges)

hitbtc = ccxt.hitbtc({
    'verbose': False,
    'proxies': {
        'http': proxy_address,
        'https': proxy_address
    }
})
orderbook = hitbtc.fetch_order_book(symbol="BTC/USDT", limit=5)
print("orderbook:", orderbook)

ticker = hitbtc.fetch_ticker(symbol="BTC/USDT")
print("ticker:", ticker)

'''
print("hitbtc")
hitbtc = ccxt.hitbtc({
    'verbose': False,
    'proxies': {
        'http': proxy_address,
        'https': proxy_address
    }
})
hitbtc_markets = hitbtc.load_markets()
print(hitbtc.id, hitbtc_markets)

bitmex = ccxt.bitmex({
    # 设置代理
    'proxies': {
        'http': proxy_address,
        'https': proxy_address
    }
})
print(bitmex.id, bitmex.load_markets())

print("huobi")
huobi = ccxt.huobi({
    'proxies': {
        'http': proxy_address,
        'https': proxy_address
    }
})
print(huobi.id, huobi.load_markets())


exchange = ccxt.okx({
    'apiKey': '1e9e4338-c701-4345-b00f',
    'secret': '3C59D08A6572CC1DDB4FC28',
    'password': '123456',
    'timeout': 30000,
    'enableRateLimit': True,
    'proxies': {
        'http': proxy_address,
        'https': proxy_address
    }
})

orderbook = exchange.fetch_order_book(symbol="BTC/USDT", limit=5)
print("orderbook:", orderbook)
'''