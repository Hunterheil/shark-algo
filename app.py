from flask import Flask
import requests
import pandas as pd
import ta
import os
import time
import hmac
import hashlib

app = Flask(__name__)

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")

BASE_URL = "https://api.sharkexchange.in"

SYMBOL = "BTCUSDT"
INTERVAL = "5m"
LIMIT = 200


# ---------- Helper: sign private requests ----------
def sign_payload(query_string):
    signature = hmac.new(
        API_SECRET.encode(),
        query_string.encode(),
        hashlib.sha256
    ).hexdigest()
    return signature


# ---------- Fetch OHLCV from Shark ----------
def fetch_klines():
    url = f"{BASE_URL}/api/v1/klines"
    params = {
        "symbol": SYMBOL,
        "interval": INTERVAL,
        "limit": LIMIT
    }

    res = requests.get(url, params=params)
    data = res.json()

    df = pd.DataFrame(data, columns=[
        'time','open','high','low','close','volume',
        '_1','_2','_3','_4','_5','_6'
    ])

    df = df[['time','open','high','low','close','volume']]
    df[['open','high','low','close','volume']] = df[['open','high','low','close','volume']].astype(float)

    return df


# ---------- Strategy ----------
def strategy(df):
    df['ema20'] = ta.trend.ema_indicator(df['close'], 20)
    df['ema50'] = ta.trend.ema_indicator(df['close'], 50)
    df['rsi'] = ta.momentum.rsi(df['close'], 14)

    last = df.iloc[-1]

    if last['ema20'] > last['ema50'] and last['rsi'] < 70:
        return "buy"
    elif last['ema20'] < last['ema50'] and last['rsi'] > 30:
        return "sell"
    else:
        return "hold"


# ---------- Place Order (Shark Private API) ----------
def place_order(side, quantity):
    endpoint = "/api/v1/order"
    url = BASE_URL + endpoint

    timestamp = int(time.time() * 1000)

    params = f"symbol={SYMBOL}&side={side}&type=MARKET&quantity={quantity}&timestamp={timestamp}"
    signature = sign_payload(params)

    headers = {
        "X-MBX-APIKEY": API_KEY
    }

    final_url = f"{url}?{params}&signature={signature}"

    res = requests.post(final_url, headers=headers)
    return res.json()


# ---------- Flask route ----------
@app.route("/")
def run_bot():
    df = fetch_klines()
    signal = strategy(df)

    return f"Signal: {signal}"
