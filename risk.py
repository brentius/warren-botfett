#risk.py

#import
from typing import Dict

max_position = 0.2
min_trade = 30
max_total_positions = 5
max_total_allocation = 0.7

def calculate_position_size(signal, cash, volatility = 0.02):
    confidence = signal.get("confidence", 0.5)

    if confidence >= 0.9:
        base_size = 0.2
    elif confidence >= 0.8:
        base_size = 0.1
    elif confidence >= 0.7:
        base_size = 0.05
    else:
        base_size = 0.02

    adjusted_size = base_size * (1 - volatility) #lower = safer = higher position
    cash_amount = adjusted_size * cash

    return cash_amount if cash_amount >= min_trade else 0

def is_allowed(symbol, positions):
    return symbol not in positions and len(positions) < max_total_positions

def check_exposure(symbol, positions, equity, max_total_allocation):
    risk = sum(positions.values())
    return risk / equity < max_total_allocation

def stop_loss(entry_price, threshold):
    return entry_price * (1 - threshold)