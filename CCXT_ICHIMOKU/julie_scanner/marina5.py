#python marina5.py --timeframe 4h --candle-color green
#[2024-07-23 15:20:57] TRX/USDT (BINANCE:TRXUSDT) Current price: 0.1325, Candle color: green, Price evolution: 0.08%
#[2024-07-23 15:20:57] BCHABC/USDT (BINANCE:BCHABCUSDT) Current price: 220.0800, Candle color: green, Price evolution: 0.40%
#[2024-07-23 15:20:57] BSV/USDT (BINANCE:BSVUSDT) Current price: 58.9000, Candle color: green, Price evolution: 6.59%
#[2024-07-23 15:20:57] WAVES/USDT (BINANCE:WAVESUSDT) Current price: 1.0760, Candle color: green, Price evolution: 4.06%
#[2024-07-23 15:20:57] BTT/USDT (BINANCE:BTTUSDT) Current price: 0.0028, Candle color: green, Price evolution: 3.74%

import ccxt
import sys
import os
import argparse
import time
from datetime import datetime
import pytz
import re

def fetch_markets(exchange, filter_assets):
    try:
        # Fetch markets from the exchange
        markets = exchange.fetch_markets()
        # Apply the filter pattern to the symbols
        pattern = re.compile(filter_assets.replace('*', '.*'), re.IGNORECASE)
        symbols = [market['symbol'] for market in markets if pattern.match(market['symbol']) and market['spot']]
        return symbols
    except (ccxt.ExchangeError, ccxt.NetworkError, ccxt.DDoSProtection) as e:
        print(f"Exchange error: {str(e)}")
        os.kill(os.getpid(), 9)
        sys.exit(-999)

def fetch_ohlcv(exchange, symbol, timeframe, limit):
    try:
        return exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
    except Exception as e:
        print(f"Error fetching OHLCV data for {symbol}: {str(e)}")
        return []

def convert_to_tradingview_symbol(ccxt_symbol):
    # Convert the ccxt symbol format "BASE/QUOTE" to TradingView format "BINANCE:BASEQUOTE"
    base, quote = ccxt_symbol.split('/')
    return f"BINANCE:{base}{quote}"

def scan_and_display_assets(exchange, symbols, timeframe, output_file, candle_color_filter):
    # Get current time in Paris time zone
    paris_tz = pytz.timezone('Europe/Paris')
    current_time = datetime.now(paris_tz).strftime('%Y-%m-%d %H:%M:%S')
    header = f"Scan results at {current_time} (Paris time):\n"
    print(header.strip())
    
    limit = 1  # We only need the latest candle
    for symbol in symbols:
        ohlcv = fetch_ohlcv(exchange, symbol, timeframe, limit)
        if ohlcv:
            current_candle = ohlcv[-1]
            current_open = current_candle[1]
            current_close = current_candle[4]
            
            # Determine the color of the current candle
            if current_close > current_open:
                candle_color = "green"
                evolution = ((current_close - current_open) / current_open) * 100
            else:
                candle_color = "red"
                evolution = ((current_open - current_close) / current_open) * 100
            
            # Apply candle color filter
            if candle_color_filter and candle_color != candle_color_filter:
                continue
            
            result = (
                f"[{current_time}] {symbol} ({convert_to_tradingview_symbol(symbol)}) "
                f"Current price: {current_close:.4f}, Candle color: {candle_color}, "
                f"Price evolution: {evolution:.2f}%\n"
            )
            print(result.strip())
            with open(output_file, 'a') as f:
                f.write(result)
    
    print("Scan complete.")

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Scan assets for current price and candlestick color.')
    parser.add_argument('--interval', type=int, default=600, help='Interval between scans in seconds.')
    parser.add_argument('--output', type=str, default='scan_results.txt', help='Output file for results.')
    parser.add_argument('--filter', type=str, default='*USDT', help='Filter pattern for symbols to scan (e.g., *USDT to scan only USDT pairs).')
    parser.add_argument('--timeframe', type=str, default='15m', help='Timeframe to scan (e.g., 1m, 5m, 15m, 1h).')
    parser.add_argument('--list-timeframes', action='store_true', help='List available timeframes and exit.')
    parser.add_argument('--candle-color', type=str, choices=['green', 'red'], help='Filter by candle color (green or red).')
    args = parser.parse_args()

    exchange_name = "binance"  # Change to your exchange
    filter_pattern = args.filter
    timeframe = args.timeframe
    interval = args.interval
    output_file = args.output
    candle_color_filter = args.candle_color

    # Initialize the exchange
    exchange = getattr(ccxt, exchange_name)()

    if args.list_timeframes:
        print("Available timeframes:", ', '.join(exchange.timeframes))
        sys.exit(0)

    print("Fetching markets...")
    symbols = fetch_markets(exchange, filter_pattern)
    if not symbols:
        print(f"No symbols found for filter pattern {filter_pattern} in the spot market. Exiting.")
        sys.exit(-1)

    # Print the number of symbols to be scanned
    print(f"Number of symbols to be tracked: {len(symbols)}")

    while True:
        scan_and_display_assets(exchange, symbols, timeframe, output_file, candle_color_filter)
        print(f"Waiting for {interval} seconds before the next scan...")
        time.sleep(interval)

if __name__ == "__main__":
    main()
