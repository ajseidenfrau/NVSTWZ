#!/usr/bin/env python3
"""
Test Yahoo Finance connectivity.
"""
import yfinance as yf
import time

def test_yahoo():
    print("Testing Yahoo Finance...")
    
    try:
        # Test 1: Simple download
        print("Test 1: Downloading AAPL data...")
        data = yf.download('AAPL', period='1d', progress=False)
        print(f"Data shape: {data.shape}")
        if not data.empty:
            print(f"Latest price: ${data.iloc[-1]['Close']:.2f}")
        else:
            print("No data received")
        
        time.sleep(2)
        
        # Test 2: Ticker object
        print("\nTest 2: Using Ticker object...")
        ticker = yf.Ticker('AAPL')
        info = ticker.info
        print(f"Company name: {info.get('longName', 'N/A')}")
        
        time.sleep(2)
        
        # Test 3: Multiple symbols
        print("\nTest 3: Multiple symbols...")
        symbols = ['AAPL', 'MSFT', 'GOOGL']
        for symbol in symbols:
            print(f"Testing {symbol}...")
            data = yf.download(symbol, period='1d', progress=False)
            if not data.empty:
                print(f"  {symbol}: ${data.iloc[-1]['Close']:.2f}")
            else:
                print(f"  {symbol}: No data")
            time.sleep(1)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_yahoo() 