#risk.py

#import
from typing import Dict

max_position = 0.2
min_trade = 30
max_total_positions = 5
max_total_allocation = 0.7

def calculate_position_size(equity: float, symbol: str, live_price: Dict[str, float], positions: Dict[str, dict]) -> float:
    if len(positions) >= max_total_positions:
        return 0

    if symbol not in live_price or live_price[symbol] <= 0:
        return 0

    price = live_price[symbol]
    max_allocation = equity * max_position

    current_total_allocation = sum(pos["market_value"] for pos in positions.values()) / equity
    remaining_allocation = max_total_allocation - current_total_allocation
    if remaining_allocation <= 0:
        return 0

    allocation = min(max_allocation, equity * remaining_allocation)

    shares = allocation // price
    if shares * price < min_trade:
        return 0

    return shares

def is_allowed(symbol, positions):
    return symbol not in positions and len(positions) < max_total_positions

def stop_loss(entry_price, current_price, threshold):
    return current_price < entry_price * (1 - threshold)

def check_exposure(symbol, positions, equity, max_total_allocation):
    if symbol not in positions:
        return True  # Not yet invested, go ahead
    current_value = positions[symbol]["market_value"]
    return (current_value / equity) < max_total_allocation