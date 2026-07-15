import yfinance as yf
import pandas as pd

def get_market_signal(symbol="BTC-USD"):
    # 1. Pull the last 100 hours of data
    data = yf.download(symbol, period="5d", interval="1h", progress=False)
    
    if data.empty:
        return "Error: No data", 0

    # 2. Calculate RSI (Relative Strength Index)
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    current_rsi = rsi.iloc[-1].values[0] # Get the latest value
    current_price = data['Close'].iloc[-1].values[0]

    # 3. Decision Logic
    if current_rsi < 30:
        signal = "🟢 BUY (Oversold)"
    elif current_rsi > 70:
        signal = "🔴 SELL (Overbought)"
    else:
        signal = "⏳ WAIT (Neutral)"
        
    return signal, round(current_price, 2), round(current_rsi, 2)