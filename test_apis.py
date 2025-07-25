#!/usr/bin/env python3
"""
Test script to verify API keys are working.
"""
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_alpha_vantage():
    """Test Alpha Vantage API."""
    try:
        from alpha_vantage.timeseries import TimeSeries
        key = os.getenv('ALPHA_VANTAGE_API_KEY')
        print(f"Testing Alpha Vantage with key: {key[:10]}...")
        
        ts = TimeSeries(key=key, output_format='pandas')
        data, meta_data = ts.get_quote_endpoint('AAPL')
        print(f"✅ Alpha Vantage working! AAPL price: ${data.iloc[0]['05. price']}")
        return True
    except Exception as e:
        print(f"❌ Alpha Vantage error: {e}")
        return False

async def test_news_api():
    """Test News API."""
    try:
        from newsapi import NewsApiClient
        key = os.getenv('NEWS_API_KEY')
        print(f"Testing News API with key: {key[:10]}...")
        
        newsapi = NewsApiClient(api_key=key)
        news = newsapi.get_everything(q='AAPL', language='en', sort_by='relevancy')
        print(f"✅ News API working! Found {len(news['articles'])} articles")
        return True
    except Exception as e:
        print(f"❌ News API error: {e}")
        return False

async def test_finnhub():
    """Test Finnhub API."""
    try:
        import finnhub
        key = os.getenv('FINNHUB_API_KEY')
        print(f"Testing Finnhub with key: {key[:10]}...")
        
        finnhub_client = finnhub.Client(api_key=key)
        quote = finnhub_client.quote('AAPL')
        print(f"✅ Finnhub working! AAPL price: ${quote['c']}")
        return True
    except Exception as e:
        print(f"❌ Finnhub error: {e}")
        return False

async def main():
    """Test all APIs."""
    print("🔍 Testing API Keys...")
    print("=" * 50)
    
    results = []
    results.append(await test_alpha_vantage())
    results.append(await test_news_api())
    results.append(await test_finnhub())
    
    print("=" * 50)
    working_apis = sum(results)
    print(f"📊 Results: {working_apis}/3 APIs working")
    
    if working_apis >= 2:
        print("✅ Ready to run the bot!")
    else:
        print("❌ Need to fix API keys before running bot")

if __name__ == "__main__":
    asyncio.run(main()) 