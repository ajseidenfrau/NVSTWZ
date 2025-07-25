"""
Strategy engine for generating trading signals and making investment decisions.
"""
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import pandas as pd
import numpy as np
from dataclasses import dataclass

from .models import TradingSignal, OrderType, MarketData, NewsEvent, MarketSentiment
from .market_data import MarketDataEngine
from .utils.logger import get_logger

logger = get_logger(__name__)

@dataclass
class StrategyConfig:
    """Configuration for trading strategy."""
    min_confidence: float = 0.7
    max_position_size: float = 0.3  # Max 30% in single position
    min_volume: int = 1000000  # Minimum volume for liquidity
    max_daily_trades: int = 20
    profit_target: float = 0.05  # 5% profit target
    stop_loss: float = 0.02  # 2% stop loss
    momentum_threshold: float = 0.03  # 3% price movement threshold

class StrategyEngine:
    """Engine for generating trading signals and making investment decisions."""
    
    def __init__(self, market_data_engine: MarketDataEngine):
        self.market_data = market_data_engine
        self.config = StrategyConfig()
        self.daily_trades = 0
        self.last_reset = datetime.now().date()
    
    async def generate_signals(self, current_positions: List[str] = None) -> List[TradingSignal]:
        """Generate trading signals based on market analysis."""
        try:
            # Reset daily trade counter if it's a new day
            self._reset_daily_counter()
            
            if self.daily_trades >= self.config.max_daily_trades:
                logger.info("Maximum daily trades reached")
                return []
            
            signals = []
            
            # Get market data
            top_movers = await self.market_data.get_top_movers(limit=100)
            news_events = await self.market_data.get_market_news(hours_back=6)
            
            # Generate signals based on different strategies
            momentum_signals = await self._generate_momentum_signals(top_movers)
            news_signals = await self._generate_news_signals(news_events)
            technical_signals = await self._generate_technical_signals(top_movers)
            
            # Combine and filter signals
            all_signals = momentum_signals + news_signals + technical_signals
            filtered_signals = self._filter_signals(all_signals, current_positions)
            
            # Sort by confidence and return top signals
            sorted_signals = sorted(filtered_signals, key=lambda x: x.confidence, reverse=True)
            
            # Limit number of signals based on remaining daily trades
            max_signals = min(len(sorted_signals), self.config.max_daily_trades - self.daily_trades)
            return sorted_signals[:max_signals]
            
        except Exception as e:
            logger.error(f"Error generating signals: {e}")
            return []
    
    async def _generate_momentum_signals(self, market_data: List[MarketData]) -> List[TradingSignal]:
        """Generate signals based on price momentum."""
        signals = []
        
        for data in market_data:
            if abs(data.change_percent) < self.config.momentum_threshold * 100:
                continue
            
            if data.volume < self.config.min_volume:
                continue
            
            # Calculate momentum score
            momentum_score = self._calculate_momentum_score(data)
            
            if momentum_score > self.config.min_confidence:
                signal_type = OrderType.BUY if data.change_percent > 0 else OrderType.SELL
                
                signal = TradingSignal(
                    symbol=data.symbol,
                    signal_type=signal_type,
                    confidence=momentum_score,
                    price_target=data.price * (1 + (data.change_percent / 100) * 0.5),
                    stop_loss=data.price * (1 - self.config.stop_loss),
                    reasoning=f"Momentum signal: {data.change_percent:.2f}% change with {data.volume:,} volume",
                    timestamp=datetime.now(),
                    technical_indicators={
                        "momentum_score": momentum_score,
                        "price_change": data.change_percent,
                        "volume": data.volume
                    }
                )
                signals.append(signal)
        
        return signals
    
    async def _generate_news_signals(self, news_events: List[NewsEvent]) -> List[TradingSignal]:
        """Generate signals based on news sentiment."""
        signals = []
        
        for event in news_events:
            if event.impact_score < 0.7:  # Only high-impact news
                continue
            
            if not event.symbols:  # Skip general market news
                continue
            
            for symbol in event.symbols:
                # Get current market data for the symbol
                market_data = await self.market_data.get_real_time_price(symbol)
                if not market_data:
                    continue
                
                # Calculate news-based confidence
                confidence = self._calculate_news_confidence(event, market_data)
                
                if confidence > self.config.min_confidence:
                    signal_type = OrderType.BUY if event.sentiment == MarketSentiment.BULLISH else OrderType.SELL
                    
                    # Calculate price targets based on sentiment
                    if event.sentiment == MarketSentiment.BULLISH:
                        price_target = market_data.price * (1 + self.config.profit_target)
                    else:
                        price_target = market_data.price * (1 - self.config.profit_target)
                    
                    signal = TradingSignal(
                        symbol=symbol,
                        signal_type=signal_type,
                        confidence=confidence,
                        price_target=price_target,
                        stop_loss=market_data.price * (1 - self.config.stop_loss),
                        reasoning=f"News signal: {event.title[:50]}...",
                        timestamp=datetime.now(),
                        news_events=[event]
                    )
                    signals.append(signal)
        
        return signals
    
    async def _generate_technical_signals(self, market_data: List[MarketData]) -> List[TradingSignal]:
        """Generate signals based on technical analysis."""
        signals = []
        
        for data in market_data:
            # Simple technical analysis based on price action
            technical_score = self._calculate_technical_score(data)
            
            if technical_score > self.config.min_confidence:
                # Determine signal type based on technical indicators
                signal_type = OrderType.BUY if technical_score > 0.8 else OrderType.SELL
                
                signal = TradingSignal(
                    symbol=data.symbol,
                    signal_type=signal_type,
                    confidence=technical_score,
                    price_target=data.price * (1 + self.config.profit_target),
                    stop_loss=data.price * (1 - self.config.stop_loss),
                    reasoning="Technical analysis signal",
                    timestamp=datetime.now(),
                    technical_indicators={
                        "technical_score": technical_score,
                        "rsi": self._calculate_rsi(data),
                        "macd": self._calculate_macd(data)
                    }
                )
                signals.append(signal)
        
        return signals
    
    def _calculate_momentum_score(self, data: MarketData) -> float:
        """Calculate momentum score for a stock."""
        # Base score from price change
        base_score = min(abs(data.change_percent) / 10, 1.0)  # Normalize to 0-1
        
        # Volume factor
        volume_factor = min(data.volume / 10000000, 1.0)  # Normalize volume
        
        # Volatility factor
        volatility = (data.high - data.low) / data.open
        volatility_factor = min(volatility * 10, 1.0)
        
        # Combine factors
        momentum_score = (base_score * 0.5 + volume_factor * 0.3 + volatility_factor * 0.2)
        
        return min(momentum_score, 1.0)
    
    def _calculate_news_confidence(self, event: NewsEvent, market_data: MarketData) -> float:
        """Calculate confidence based on news event."""
        # Base confidence from impact score
        base_confidence = event.impact_score
        
        # Sentiment alignment with price action
        sentiment_alignment = 0.0
        if event.sentiment == MarketSentiment.BULLISH and market_data.change_percent > 0:
            sentiment_alignment = 0.2
        elif event.sentiment == MarketSentiment.BEARISH and market_data.change_percent < 0:
            sentiment_alignment = 0.2
        
        # Recency factor
        hours_old = (datetime.now() - event.published_at).total_seconds() / 3600
        recency_factor = max(0, 1 - hours_old / 24)  # Decay over 24 hours
        
        # Source credibility
        credible_sources = ['Reuters', 'Bloomberg', 'CNBC', 'MarketWatch']
        credibility_factor = 0.1 if event.source in credible_sources else 0.0
        
        total_confidence = base_confidence + sentiment_alignment + recency_factor + credibility_factor
        return min(total_confidence, 1.0)
    
    def _calculate_technical_score(self, data: MarketData) -> float:
        """Calculate technical analysis score."""
        # Simple technical indicators
        rsi = self._calculate_rsi(data)
        macd = self._calculate_macd(data)
        
        # RSI signals
        rsi_score = 0.0
        if rsi < 30:  # Oversold
            rsi_score = 0.3
        elif rsi > 70:  # Overbought
            rsi_score = 0.3
        
        # MACD signals
        macd_score = 0.0
        if macd > 0:  # Bullish
            macd_score = 0.2
        elif macd < 0:  # Bearish
            macd_score = 0.2
        
        # Price action
        price_score = 0.0
        if data.change_percent > 5:  # Strong upward momentum
            price_score = 0.3
        elif data.change_percent < -5:  # Strong downward momentum
            price_score = 0.3
        
        return min(rsi_score + macd_score + price_score, 1.0)
    
    def _calculate_rsi(self, data: MarketData) -> float:
        """Calculate RSI (simplified)."""
        # Simplified RSI calculation
        if data.previous_close == 0:
            return 50.0
        
        change = data.price - data.previous_close
        if change > 0:
            return 60.0  # Bullish
        else:
            return 40.0  # Bearish
    
    def _calculate_macd(self, data: MarketData) -> float:
        """Calculate MACD (simplified)."""
        # Simplified MACD calculation
        if data.previous_close == 0:
            return 0.0
        
        return (data.price - data.previous_close) / data.previous_close
    
    def _filter_signals(self, signals: List[TradingSignal], current_positions: List[str] = None) -> List[TradingSignal]:
        """Filter and rank trading signals."""
        filtered = []
        current_positions = current_positions or []
        
        for signal in signals:
            # Skip if already have position in this symbol
            if signal.symbol in current_positions:
                continue
            
            # Skip low confidence signals
            if signal.confidence < self.config.min_confidence:
                continue
            
            # Skip signals with extreme price targets
            if signal.price_target > signal.stop_loss * 2:  # Unrealistic profit target
                continue
            
            filtered.append(signal)
        
        return filtered
    
    def _reset_daily_counter(self):
        """Reset daily trade counter if it's a new day."""
        today = datetime.now().date()
        if today > self.last_reset:
            self.daily_trades = 0
            self.last_reset = today
    
    def update_trade_count(self):
        """Update the daily trade counter."""
        self.daily_trades += 1
    
    async def validate_signal(self, signal: TradingSignal) -> bool:
        """Validate a trading signal before execution."""
        try:
            # Get current market data
            market_data = await self.market_data.get_real_time_price(signal.symbol)
            if not market_data:
                return False
            
            # Check if price is still reasonable
            current_price = market_data.price
            if signal.signal_type == OrderType.BUY:
                if current_price > signal.price_target:
                    logger.info(f"Price {current_price} exceeds target {signal.price_target} for {signal.symbol}")
                    return False
            else:  # SELL
                if current_price < signal.price_target:
                    logger.info(f"Price {current_price} below target {signal.price_target} for {signal.symbol}")
                    return False
            
            # Check volume
            if market_data.volume < self.config.min_volume:
                logger.info(f"Insufficient volume {market_data.volume} for {signal.symbol}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating signal: {e}")
            return False 