#strategy.py
#trading logic

#imports
import pandas as pd
import numpy as np
import ta
from typing import Dict, Any

"PLANS: use multiple strategies, which strategy used: determine by ranking"

#evaluate strategy
def evaluate(history_data):
    signals = {}
    return signals