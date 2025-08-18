from alpaca.trading.client import TradingClient
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.live import StockDataStream
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from dotenv import load_dotenv
import os
import backtrader as bt
from data import fetch_historical_data, parse, fetch_live_data
from strategy import strategy, test

#TO GO LIVE - SET ALL TO FALSE
paper = True
backtest = True
opt = False

load_dotenv()
api_key = os.getenv("alpaca_paper_key" if paper == True else "alpaca_live_key")
api_secret = os.getenv("alpaca_paper_secret" if paper == True else "alpaca_live_secret")
base_url = os.getenv("alpaca_base_url")

tradeclient = TradingClient(api_key, api_secret, paper = paper)
dataclient = StockHistoricalDataClient(api_key, api_secret)
liveclient = StockDataStream(api_key, api_secret)

symbols = ["AAPL", "MSFT", "NVDA", "GOOG", "JPM", "BA"] #TRADE THESE

historical_data = fetch_historical_data(dataclient, symbols)
live_data = fetch_live_data(dataclient, symbols)

cerebro = bt.Cerebro()
for i, (stock, df) in enumerate(historical_data.items()):
    data_feed = parse(df)
    cerebro.adddata(data_feed, name = stock)
    if i == 0:
        master_feed = data_feed  # first feed = master
    else:
        data_feed.plotinfo.plotmaster = master_feed
        data_feed.plotinfo.sameaxis = True

cerebro.addstrategy(test) #strategy

if backtest == True and opt == False:
    print(f"Starting Portfolio Value: {cerebro.broker.getvalue():.2f}")
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')

    results = cerebro.run()

    sharpe = results[0].analyzers.sharpe.get_analysis()
    drawdown = results[0].analyzers.drawdown.get_analysis()
    print(f"Final Portfolio Value: {cerebro.broker.getvalue():.2f}")
    print(f"Sharpe Ratio: {sharpe['sharperatio']}")
    print(f"Max Drawdown: {drawdown['max']['drawdown']:.2f}%")
    cerebro.plot()

elif backtest == False and opt == False:
    live_strategy = strategy()
    account_value = float(tradeclient.get_account().equity)
    close_data = {sym: df["close"] for sym, df in historical_data.items()}
    results = live_strategy.evaluate(close_data, account_value)

    for sym, info in results.items():
        if "size" in info:
            try:
                pos = tradeclient.get_position(sym)
                current_qty = int(pos.qty)
            except:
                current_qty = 0

            if info["signal"] == 1 and current_qty == 0:
                print(f"BUY {info['size']} {sym}")
                order = MarketOrderRequest(
                    symbol=sym,
                    qty=info["size"],
                    side=OrderSide.BUY,
                    time_in_force=TimeInForce.DAY
                )
                tradeclient.submit_order(order)
            elif info["signal"] == -1 and current_qty > 0:
                print(f"SELL {current_qty} {sym}")
                order = MarketOrderRequest(
                    symbol=sym,
                    qty=current_qty,
                    side=OrderSide.SELL,
                    time_in_force=TimeInForce.DAY
                )
                tradeclient.submit_order(order)

elif opt == True:
    cerebro.optstrategy(
        test,
        fast=range(10, 20),  # MACD fast period from 10 to 19
        slow=range(20, 40),  # slow period from 20 to 39
        signal=range(5, 10)
    )
    results = cerebro.run(maxcpus=1)
    for strat in results:
        print(f'Params: fast={strat.params.fast}, slow={strat.params.slow}, Sharpe={strat.analyzers.sharpe.get_analysis()}')