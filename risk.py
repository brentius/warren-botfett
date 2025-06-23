#risk.py

#import
from typing import Dict

max_position = 0.2
min_trade = 30
max_total_positions = 5
max_total_allocation = 0.7

def calculate_position_size(signal, cash, volatility = 0.8):