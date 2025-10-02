import yfinance as yf
import pandas as pd

ftse = yf.Ticker("^FTSE")

data = yf.download("^FTSE", start="2015-01-01", end="2025-01-01")

print(data.head())