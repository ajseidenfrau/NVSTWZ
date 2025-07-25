#!/usr/bin/env python3
"""
Test web scraping approach for Yahoo Finance.
"""
import asyncio
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.market_data import MarketDataEngine

async def test_scraping():
    print("Testing web scraping approach...")
    
    engine = MarketDataEngine()
    
    try:
        # Test single symbol
        print("Testing AAPL...")
        data = await engine.get_real_time_price('AAPL')
        if data:
            print(f"✅ AAPL: ${data.price:.2f} ({data.change_percent:+.2f}%)")
        else:
            print("❌ Failed to get AAPL data")
        
        await asyncio.sleep(3)
        
        # Test multiple symbols
        print("\nTesting multiple symbols...")
        symbols = ['MSFT', 'GOOGL']
        for symbol in symbols:
            data = await engine.get_real_time_price(symbol)
            if data:
                print(f"✅ {symbol}: ${data.price:.2f} ({data.change_percent:+.2f}%)")
            else:
                print(f"❌ Failed to get {symbol} data")
            await asyncio.sleep(3)
        
        # Test top movers
        print("\nTesting top movers...")
        movers = await engine.get_top_movers(3)
        print(f"Found {len(movers)} movers:")
        for mover in movers:
            print(f"  {mover.symbol}: ${mover.price:.2f} ({mover.change_percent:+.2f}%)")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await engine.close()

if __name__ == "__main__":
    asyncio.run(test_scraping()) 