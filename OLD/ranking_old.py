#ranking.py
#ranks stocks based on signals (from strategy.py)
def rank(signals, top_n, min_confidence):

    #remove HOLD / SELL + any BUY with confidence below threshold
    filtered_signals = {
        symbol: signal for symbol, signal in signals.items()
        if signal["action"] == "BUY" and signal["confidence"] >= min_confidence 
    }

    #convert filtered_signals -> list of tuples + sort
    ranked = sorted( #inbuilt "sorted" function
        filtered_signals.items(),
        key = lambda x: x[1]["confidence"], #sort by confidence
        reverse = True #descending order
    )

    return(ranked[:top_n])