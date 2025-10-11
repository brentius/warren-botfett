import yfinance as yf

ftse = yf.Ticker("FTSE^")
ftse_historical = ftse.history(start = "2025-01-01", end = "2025-10-11", interval = "1d")
print(ftse_historical)