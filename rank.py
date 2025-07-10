def rank_buy(signals, top_n, conf_threshold):
    #remove holds
    filtered_signals = {
        symbol: signal for symbol, signal in signals.items()
        if signal["action"] == "BUY" and signal["confidence"] >= conf_threshold 
    }

    ranked = sorted( #inbuilt "sorted" function
        filtered_signals.items(),
        key = lambda x: x[1]["confidence"], #sort by confidence
        reverse = True #descending order
    )

    return(ranked[:top_n])

def rank_sell(signals, top_n, conf_threshold):
    #remove holds
    filtered_signals = {
        symbol: signal for symbol, signal in signals.items()
        if signal["action"] == "SELL" and signal["confidence"] >= conf_threshold 
    }

    ranked = sorted( #inbuilt "sorted" function
        filtered_signals.items(),
        key = lambda x: x[1]["confidence"], #sort by confidence
        reverse = True #descending order
    )

    return(ranked[:top_n])