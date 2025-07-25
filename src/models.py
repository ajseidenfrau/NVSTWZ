"""
Data models for NVSTWZ investment bot.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum

class OrderType(str, Enum):
    """Order types."""
    BUY = "BUY"
    SELL = "SELL"
    BUY_TO_COVER = "BUY_TO_COVER"
    SELL_SHORT = "SELL_SHORT"

class OrderStatus(str, Enum):
    """Order status."""
    PENDING = "PENDING"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"

class AssetType(str, Enum):
    """Asset types."""
    STOCK = "STOCK"
    ETF = "ETF"
    BOND = "BOND"
    OPTION = "OPTION"
    CRYPTO = "CRYPTO"

class MarketSentiment(str, Enum):
    """Market sentiment."""
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"

class Trade(BaseModel):
    """Trade record model."""
    id: Optional[int] = None
    symbol: str
    order_type: OrderType
    quantity: float
    price: float
    timestamp: datetime
    status: OrderStatus = OrderStatus.PENDING
    order_id: Optional[str] = None
    commission: float = 0.0
    notes: Optional[str] = None

class Position(BaseModel):
    """Portfolio position model."""
    id: Optional[int] = None
    symbol: str
    quantity: float
    average_price: float
    current_price: float
    market_value: float
    unrealized_pnl: float
    realized_pnl: float
    last_updated: datetime

class MarketData(BaseModel):
    """Market data model."""
    symbol: str
    price: float
    volume: int
    high: float
    low: float
    open: float
    previous_close: float
    change: float
    change_percent: float
    timestamp: datetime
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None

class NewsEvent(BaseModel):
    """News event model."""
    id: Optional[int] = None
    title: str
    description: str
    source: str
    url: str
    published_at: datetime
    sentiment: MarketSentiment
    confidence: float
    symbols: List[str] = []
    impact_score: float = 0.0

class Portfolio(BaseModel):
    """Portfolio model."""
    id: Optional[int] = None
    total_value: float
    cash_balance: float
    invested_amount: float
    daily_pnl: float
    total_pnl: float
    daily_return: float
    total_return: float
    last_updated: datetime
    positions: List[Position] = []

class TradingSignal(BaseModel):
    """Trading signal model."""
    id: Optional[int] = None
    symbol: str
    signal_type: OrderType
    confidence: float
    price_target: float
    stop_loss: float
    reasoning: str
    timestamp: datetime
    news_events: List[NewsEvent] = []
    technical_indicators: dict = {}

class RiskMetrics(BaseModel):
    """Risk metrics model."""
    id: Optional[int] = None
    portfolio_id: int
    sharpe_ratio: float
    max_drawdown: float
    volatility: float
    var_95: float  # Value at Risk 95%
    beta: float
    alpha: float
    timestamp: datetime

class BotStatus(BaseModel):
    """Bot status model."""
    is_running: bool
    last_heartbeat: datetime
    active_trades: int
    daily_trades: int
    current_capital: float
    daily_pnl: float
    errors: List[str] = []
    warnings: List[str] = [] 