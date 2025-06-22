#ranking.py
#ranks stocks based on signals (from strategy.py)

#imports
import pandas as pd
from typing import Dict, Any

#rank stocks function
def rank(signals, top_n = 3, min_confidence = 0.8):

    #remove HOLD / SELL + any BUY with confidence below threshold
    filtered_signals = {
        symbol: signal for symbol, signal in signals.items()
        if signal["action"] == "BUY" and signal["confidence"] >= min_confidence 
    }

    #convert filtered_signals -> list of tuples + sort
    ranked = sorted( #inbuild "sorted" function
        filtered_signals.items(),
        key = lambda x: x[1]["confidence"], #sort by confidence
        reverse = True #descending order
    )

    top_ranked = ranked[:top_n]

    return[
        {
            "symbol": symbol,
            "confidence": signal["confidence"],
            "position_size": signal.get("position_size", 0.1)
        }
        for symbol, signal in top_ranked
    ]