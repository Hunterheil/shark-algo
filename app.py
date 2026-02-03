import ccxt
import pandas as pd
import ta
import time
import os

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")

exchange = ccxt.Exchange({
    'apiKey': API_KEY,
    'secret': API_SECRET,
    'enableRateLimit': True,
})

symbol = 'BTC/USDT'
timeframe = '5m'

def fetch_data():
    bars = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=200)
    df = pd.DataFrame(bars, columns=['time','open','high','low','close','volume'])
    return df

def strategy(df):
    df['ema20'] = ta.trend.ema_indicator(df['close'], 20)
    df['ema50'] = ta.trend.ema_indicator(df['close'], 50)
    df['rsi'] = ta.momentum.rsi(df['close'], 14)
    last = df.iloc[-1]

    if last['ema20'] > last['ema50'] and last['rsi'] < 70:
        return 'buy'
    elif last['ema20'] < last['ema50'] and last['rsi'] > 30:
        return 'sell'
    return 'hold'

while True:
    df = fetch_data()
    signal = strategy(df)
    print("Signal:", signal)
    time.sleep(300)
