import requests
import pandas as pd

BASE_URL = "https://api.binance.com/api/v3/klines"


def fetch_binance_data(symbol="BTCUSDT", interval="1h", limit=500):
    """
    Fetch real historical candlestick data from Binance
    """

    try:
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        }

        response = requests.get(BASE_URL, params=params)
        data = response.json()

        # Convert to DataFrame
        df = pd.DataFrame(data, columns=[
            "time", "open", "high", "low", "close", "volume",
            "close_time", "qav", "trades",
            "tbbav", "tbqav", "ignore"
        ])

        # Keep only useful columns
        df = df[["time", "open", "high", "low", "close", "volume"]]

        # Convert types
        df["open"] = df["open"].astype(float)
        df["high"] = df["high"].astype(float)
        df["low"] = df["low"].astype(float)
        df["close"] = df["close"].astype(float)
        df["volume"] = df["volume"].astype(float)

        # Save CSV
        df.to_csv("market_data.csv", index=False)

        return df

    except Exception as e:
        print(f"Error fetching data: {e}")
        return None