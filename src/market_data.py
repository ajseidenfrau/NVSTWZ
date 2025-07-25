"""
Market Data Engine for NVSTWZ investment bot.
Simulation mode for testing without external API dependencies.
"""
import asyncio
import random
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from loguru import logger
from .models import MarketData, NewsEvent, MarketSentiment
from .config import config

class MarketDataEngine:
    """Market data engine in simulation mode for testing."""
    
    def __init__(self):
        self.cache = {}
        self.cache_duration = 60  # 1 minute cache
        self.base_prices = {
            'AAPL': 150.0,
            'MSFT': 300.0,
            'GOOGL': 2800.0,
            'AMZN': 3300.0,
            'TSLA': 700.0,
            'META': 350.0,
            'NVDA': 500.0
        }
        self.price_history = {symbol: [price] for symbol, price in self.base_prices.items()}
        
    def _simulate_price_movement(self, symbol: str) -> tuple:
        """Simulate realistic price movement."""
        base_price = self.base_prices[symbol]
        
        # Get recent price history
        if symbol in self.price_history and len(self.price_history[symbol]) > 0:
            current_price = self.price_history[symbol][-1]
        else:
            current_price = base_price
        
        # Simulate price movement (random walk with some trend)
        volatility = 0.02  # 2% daily volatility
        trend = random.uniform(-0.01, 0.01)  # Slight trend
        
        # Calculate new price
        change_pct = random.gauss(trend, volatility)
        new_price = current_price * (1 + change_pct)
        
        # Ensure price doesn't go negative
        new_price = max(new_price, base_price * 0.5)
        
        # Update price history
        if symbol not in self.price_history:
            self.price_history[symbol] = []
        self.price_history[symbol].append(new_price)
        
        # Keep only last 100 prices
        if len(self.price_history[symbol]) > 100:
            self.price_history[symbol] = self.price_history[symbol][-100:]
        
        # Calculate change
        price_change = new_price - current_price
        price_change_pct = (price_change / current_price) * 100
        
        return new_price, price_change, price_change_pct
    
    async def get_real_time_price(self, symbol: str) -> Optional[MarketData]:
        """Get simulated real-time price data."""
        try:
            # Check cache first
            cache_key = f"price_{symbol}"
            if cache_key in self.cache:
                cached_data, timestamp = self.cache[cache_key]
                if (datetime.now() - timestamp).seconds < self.cache_duration:
                    logger.debug(f"Using cached data for {symbol}")
                    return cached_data
            
            # Simulate a small delay
            await asyncio.sleep(0.1)
            
            logger.info(f"Fetching price for {symbol}")
            
            # Simulate price movement
            current_price, price_change, price_change_pct = self._simulate_price_movement(symbol)
            
            # Simulate volume
            volume = random.randint(1000000, 10000000)
            
            # Calculate additional required fields
            high = current_price * (1 + random.uniform(0, 0.05))
            low = current_price * (1 - random.uniform(0, 0.05))
            open_price = current_price * (1 + random.uniform(-0.02, 0.02))
            previous_close = current_price - price_change
            
            market_data = MarketData(
                symbol=symbol,
                price=current_price,
                volume=volume,
                high=high,
                low=low,
                open=open_price,
                previous_close=previous_close,
                change=price_change,
                change_percent=price_change_pct,
                timestamp=datetime.now(),
                market_cap=current_price * volume * 0.1,  # Rough estimate
                pe_ratio=random.uniform(15, 30)
            )
            
            # Cache the result
            self.cache[cache_key] = (market_data, datetime.now())
            
            logger.info(f"Successfully fetched {symbol}: ${current_price:.2f} ({price_change_pct:+.2f}%)")
            return market_data
            
        except Exception as e:
            logger.error(f"Error in get_real_time_price for {symbol}: {e}")
            return None
    
    async def get_top_movers(self, limit: int = 3) -> List[MarketData]:
        """Get top moving stocks."""
        try:
            # Use a small list for testing
            major_stocks = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA']
            
            results = []
            
            # Process all symbols
            for symbol in major_stocks[:limit]:
                data = await self.get_real_time_price(symbol)
                if data:
                    results.append(data)
            
            # Sort by absolute price change percentage
            results.sort(key=lambda x: abs(x.change_percent), reverse=True)
            
            logger.info(f"Successfully fetched {len(results)} stock prices")
            return results
            
        except Exception as e:
            logger.error(f"Error fetching top movers: {e}")
            return []
    
    async def get_market_news(self, symbols: List[str] = None, hours_back: int = 24) -> List[NewsEvent]:
        """Get simulated market news."""
        # Generate some simulated news events
        news_events = []
        
        if symbols:
            for symbol in symbols[:3]:  # Limit to 3 symbols
                # Simulate news based on price movement
                data = await self.get_real_time_price(symbol)
                if data and abs(data.change_percent) > 1:
                    sentiment = "bullish" if data.change_percent > 0 else "bearish"
                    
                    news_event = NewsEvent(
                        title=f"{symbol} shows {'strong' if abs(data.change_percent) > 3 else 'moderate'} movement",
                        description=f"{symbol} is trading at ${data.price:.2f} with {data.change_percent:+.2f}% change",
                        source="Simulated News",
                        url="",
                        published_at=datetime.now(),
                        sentiment=sentiment,
                        confidence=0.7,
                        symbols=[symbol],
                        impact_score=min(0.9, abs(data.change_percent) / 10)
                    )
                    news_events.append(news_event)
        
        logger.info(f"Generated {len(news_events)} simulated news events")
        return news_events
    
    async def get_market_sentiment(self, symbol: str) -> MarketSentiment:
        """Get market sentiment for a symbol based on price movement."""
        try:
            data = await self.get_real_time_price(symbol)
            if not data:
                return MarketSentiment(symbol=symbol, sentiment="neutral", confidence=0.5)
            
            # Simple sentiment logic based on price movement
            if data.change_percent > 2:
                sentiment = "bullish"
                confidence = min(0.9, abs(data.change_percent) / 10)
            elif data.change_percent < -2:
                sentiment = "bearish"
                confidence = min(0.9, abs(data.change_percent) / 10)
            else:
                sentiment = "neutral"
                confidence = 0.5
            
            return MarketSentiment(
                symbol=symbol,
                sentiment=sentiment,
                confidence=confidence,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error getting sentiment for {symbol}: {e}")
            return MarketSentiment(symbol=symbol, sentiment="neutral", confidence=0.5)
    
    def _deduplicate_news(self, news_events: List[NewsEvent]) -> List[NewsEvent]:
        """Remove duplicate news events."""
        seen = set()
        unique_news = []
        
        for event in news_events:
            key = f"{event.title}_{event.timestamp}"
            if key not in seen:
                seen.add(key)
                unique_news.append(event)
        
        return unique_news
    
    def clear_cache(self):
        """Clear the cache."""
        self.cache.clear()
        logger.info("Market data cache cleared")
    
    async def close(self):
        """Close the engine."""
        logger.info("Market data engine closed") 