"""
Market data engine for fetching real-time market information.
"""
import asyncio
import aiohttp
import yfinance as yf
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pandas as pd
from alpha_vantage.timeseries import TimeSeries
from newsapi import NewsApiClient
import finnhub

from .config import config
from .models import MarketData, NewsEvent, MarketSentiment
from .utils.logger import get_logger

logger = get_logger(__name__)

class MarketDataEngine:
    """Engine for fetching and managing market data."""
    
    def __init__(self):
        self.alpha_vantage = TimeSeries(key=config.api.alpha_vantage_key, output_format='pandas')
        self.news_api = NewsApiClient(api_key=config.api.news_api_key)
        self.finnhub_client = finnhub.Client(api_key=config.api.finnhub_key)
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_real_time_price(self, symbol: str) -> Optional[MarketData]:
        """Get real-time price data for a symbol."""
        try:
            # Try multiple data sources for redundancy
            data = await self._get_price_from_yfinance(symbol)
            if not data:
                data = await self._get_price_from_alpha_vantage(symbol)
            
            return data
        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {e}")
            return None
    
    async def _get_price_from_yfinance(self, symbol: str) -> Optional[MarketData]:
        """Get price data from Yahoo Finance."""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Get real-time quote
            quote = ticker.history(period="1d", interval="1m")
            if quote.empty:
                return None
                
            latest = quote.iloc[-1]
            
            return MarketData(
                symbol=symbol,
                price=float(latest['Close']),
                volume=int(latest['Volume']),
                high=float(latest['High']),
                low=float(latest['Low']),
                open=float(latest['Open']),
                previous_close=float(info.get('previousClose', latest['Close'])),
                change=float(latest['Close'] - info.get('previousClose', latest['Close'])),
                change_percent=float((latest['Close'] - info.get('previousClose', latest['Close'])) / info.get('previousClose', latest['Close']) * 100),
                timestamp=datetime.now(),
                market_cap=info.get('marketCap'),
                pe_ratio=info.get('trailingPE')
            )
        except Exception as e:
            logger.error(f"Error fetching from Yahoo Finance for {symbol}: {e}")
            return None
    
    async def _get_price_from_alpha_vantage(self, symbol: str) -> Optional[MarketData]:
        """Get price data from Alpha Vantage."""
        try:
            data, meta_data = self.alpha_vantage.get_quote_endpoint(symbol)
            
            if data.empty:
                return None
                
            quote = data.iloc[0]
            
            return MarketData(
                symbol=symbol,
                price=float(quote['05. price']),
                volume=int(quote['06. volume']),
                high=float(quote['03. high']),
                low=float(quote['04. low']),
                open=float(quote['02. open']),
                previous_close=float(quote['08. previous close']),
                change=float(quote['09. change']),
                change_percent=float(quote['10. change percent'].rstrip('%')),
                timestamp=datetime.now()
            )
        except Exception as e:
            logger.error(f"Error fetching from Alpha Vantage for {symbol}: {e}")
            return None
    
    async def get_market_news(self, symbols: List[str] = None, hours_back: int = 24) -> List[NewsEvent]:
        """Get market news that could impact trading."""
        try:
            news_events = []
            
            # Get general market news
            if symbols:
                for symbol in symbols:
                    symbol_news = await self._get_news_for_symbol(symbol, hours_back)
                    news_events.extend(symbol_news)
            
            # Get general market news
            general_news = await self._get_general_market_news(hours_back)
            news_events.extend(general_news)
            
            # Remove duplicates and sort by impact
            unique_news = self._deduplicate_news(news_events)
            return sorted(unique_news, key=lambda x: x.impact_score, reverse=True)
            
        except Exception as e:
            logger.error(f"Error fetching market news: {e}")
            return []
    
    async def _get_news_for_symbol(self, symbol: str, hours_back: int) -> List[NewsEvent]:
        """Get news for a specific symbol."""
        try:
            # Use NewsAPI
            from_date = datetime.now() - timedelta(hours=hours_back)
            news = self.news_api.get_everything(
                q=symbol,
                from_param=from_date.isoformat(),
                language='en',
                sort_by='relevancy'
            )
            
            events = []
            for article in news.get('articles', [])[:10]:  # Limit to top 10
                sentiment = await self._analyze_sentiment(article['title'] + " " + article['description'])
                
                event = NewsEvent(
                    title=article['title'],
                    description=article['description'],
                    source=article['source']['name'],
                    url=article['url'],
                    published_at=datetime.fromisoformat(article['publishedAt'].replace('Z', '+00:00')),
                    sentiment=sentiment,
                    confidence=0.8,  # Placeholder
                    symbols=[symbol],
                    impact_score=self._calculate_impact_score(article, sentiment)
                )
                events.append(event)
            
            return events
            
        except Exception as e:
            logger.error(f"Error fetching news for {symbol}: {e}")
            return []
    
    async def _get_general_market_news(self, hours_back: int) -> List[NewsEvent]:
        """Get general market news."""
        try:
            from_date = datetime.now() - timedelta(hours=hours_back)
            news = self.news_api.get_everything(
                q="stock market OR trading OR investment",
                from_param=from_date.isoformat(),
                language='en',
                sort_by='relevancy'
            )
            
            events = []
            for article in news.get('articles', [])[:5]:  # Limit to top 5
                sentiment = await self._analyze_sentiment(article['title'] + " " + article['description'])
                
                event = NewsEvent(
                    title=article['title'],
                    description=article['description'],
                    source=article['source']['name'],
                    url=article['url'],
                    published_at=datetime.fromisoformat(article['publishedAt'].replace('Z', '+00:00')),
                    sentiment=sentiment,
                    confidence=0.7,
                    symbols=[],
                    impact_score=self._calculate_impact_score(article, sentiment)
                )
                events.append(event)
            
            return events
            
        except Exception as e:
            logger.error(f"Error fetching general market news: {e}")
            return []
    
    async def _analyze_sentiment(self, text: str) -> MarketSentiment:
        """Analyze sentiment of news text."""
        # Simple keyword-based sentiment analysis
        # In production, use a proper NLP model
        bullish_keywords = ['bullish', 'surge', 'rally', 'gain', 'positive', 'up', 'higher', 'profit']
        bearish_keywords = ['bearish', 'drop', 'fall', 'decline', 'negative', 'down', 'lower', 'loss']
        
        text_lower = text.lower()
        bullish_count = sum(1 for keyword in bullish_keywords if keyword in text_lower)
        bearish_count = sum(1 for keyword in bearish_keywords if keyword in text_lower)
        
        if bullish_count > bearish_count:
            return MarketSentiment.BULLISH
        elif bearish_count > bullish_count:
            return MarketSentiment.BEARISH
        else:
            return MarketSentiment.NEUTRAL
    
    def _calculate_impact_score(self, article: dict, sentiment: MarketSentiment) -> float:
        """Calculate impact score for news article."""
        base_score = 0.5
        
        # Source credibility
        credible_sources = ['Reuters', 'Bloomberg', 'CNBC', 'MarketWatch', 'Yahoo Finance']
        if article['source']['name'] in credible_sources:
            base_score += 0.3
        
        # Sentiment impact
        if sentiment == MarketSentiment.BULLISH:
            base_score += 0.2
        elif sentiment == MarketSentiment.BEARISH:
            base_score += 0.1
        
        # Recency bonus
        hours_old = (datetime.now() - datetime.fromisoformat(article['publishedAt'].replace('Z', '+00:00'))).total_seconds() / 3600
        if hours_old < 1:
            base_score += 0.2
        elif hours_old < 6:
            base_score += 0.1
        
        return min(base_score, 1.0)
    
    def _deduplicate_news(self, news_events: List[NewsEvent]) -> List[NewsEvent]:
        """Remove duplicate news events."""
        seen_titles = set()
        unique_events = []
        
        for event in news_events:
            if event.title not in seen_titles:
                seen_titles.add(event.title)
                unique_events.append(event)
        
        return unique_events
    
    async def get_top_movers(self, limit: int = 50) -> List[MarketData]:
        """Get top movers (biggest gainers and losers)."""
        try:
            # Get S&P 500 symbols for analysis
            sp500_symbols = await self._get_sp500_symbols()
            
            movers = []
            for symbol in sp500_symbols[:limit]:
                data = await self.get_real_time_price(symbol)
                if data and abs(data.change_percent) > 2:  # Only significant movers
                    movers.append(data)
            
            # Sort by absolute change percentage
            return sorted(movers, key=lambda x: abs(x.change_percent), reverse=True)
            
        except Exception as e:
            logger.error(f"Error fetching top movers: {e}")
            return []
    
    async def _get_sp500_symbols(self) -> List[str]:
        """Get S&P 500 symbols."""
        try:
            # Use a simple list for now - in production, fetch from a reliable source
            sp500_symbols = [
                'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'BRK-B', 'JNJ', 'V',
                'PG', 'JPM', 'UNH', 'HD', 'MA', 'DIS', 'PYPL', 'BAC', 'ADBE', 'CRM',
                'NFLX', 'CMCSA', 'PFE', 'ABT', 'KO', 'TMO', 'AVGO', 'COST', 'DHR', 'ACN'
            ]
            return sp500_symbols
        except Exception as e:
            logger.error(f"Error fetching S&P 500 symbols: {e}")
            return []
    
    async def get_market_status(self) -> Dict:
        """Get overall market status."""
        try:
            # Check if market is open
            now = datetime.now()
            market_open = datetime.strptime(config.trading.market_open, "%H:%M").time()
            market_close = datetime.strptime(config.trading.market_close, "%H:%M").time()
            
            is_market_open = market_open <= now.time() <= market_close
            
            return {
                "is_market_open": is_market_open,
                "current_time": now,
                "market_open": market_open,
                "market_close": market_close,
                "next_market_open": self._get_next_market_open()
            }
        except Exception as e:
            logger.error(f"Error getting market status: {e}")
            return {"is_market_open": False}
    
    def _get_next_market_open(self) -> datetime:
        """Get next market open time."""
        now = datetime.now()
        market_open = datetime.strptime(config.trading.market_open, "%H:%M").time()
        
        if now.time() < market_open:
            # Market opens today
            return datetime.combine(now.date(), market_open)
        else:
            # Market opens tomorrow
            tomorrow = now.date() + timedelta(days=1)
            return datetime.combine(tomorrow, market_open) 