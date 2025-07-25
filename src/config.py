"""
Configuration management for NVSTWZ investment bot.
"""
import os
from typing import Optional
from pydantic import BaseSettings, Field
from dotenv import load_dotenv

load_dotenv()

class TradingConfig(BaseSettings):
    """Trading configuration settings."""
    initial_capital: float = Field(default=10.00, env="INITIAL_CAPITAL")
    max_daily_loss: float = Field(default=0.00, env="MAX_DAILY_LOSS")
    target_daily_return: float = Field(default=0.05, env="TARGET_DAILY_RETURN")
    risk_tolerance: float = Field(default=0.02, env="RISK_TOLERANCE")
    max_daily_trades: int = Field(default=50, env="MAX_DAILY_TRADES")
    
    # Trading hours (EST)
    market_open: str = Field(default="09:30", env="MARKET_OPEN")
    market_close: str = Field(default="16:00", env="MARKET_CLOSE")
    pre_market_open: str = Field(default="04:00", env="PRE_MARKET_OPEN")
    after_hours_close: str = Field(default="20:00", env="AFTER_HOURS_CLOSE")

class APIConfig(BaseSettings):
    """API configuration settings."""
    # Fidelity API
    fidelity_client_id: str = Field(env="FIDELITY_CLIENT_ID")
    fidelity_client_secret: str = Field(env="FIDELITY_CLIENT_SECRET")
    fidelity_redirect_uri: str = Field(default="http://localhost:8000/callback", env="FIDELITY_REDIRECT_URI")
    
    # Market Data APIs
    alpha_vantage_key: str = Field(env="ALPHA_VANTAGE_API_KEY")
    news_api_key: str = Field(env="NEWS_API_KEY")
    finnhub_key: str = Field(env="FINNHUB_API_KEY")

class DatabaseConfig(BaseSettings):
    """Database configuration settings."""
    database_url: str = Field(env="DATABASE_URL")

class RedisConfig(BaseSettings):
    """Redis configuration settings."""
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")

class LoggingConfig(BaseSettings):
    """Logging configuration settings."""
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="logs/nvstwz.log", env="LOG_FILE")

class Config:
    """Main configuration class."""
    def __init__(self):
        self.trading = TradingConfig()
        self.api = APIConfig()
        self.database = DatabaseConfig()
        self.redis = RedisConfig()
        self.logging = LoggingConfig()
    
    def validate(self) -> bool:
        """Validate that all required configuration is present."""
        required_fields = [
            self.api.fidelity_client_id,
            self.api.fidelity_client_secret,
            self.api.alpha_vantage_key,
            self.api.news_api_key,
            self.api.finnhub_key,
            self.database.database_url
        ]
        
        missing_fields = [field for field in required_fields if not field]
        if missing_fields:
            print(f"Missing required configuration: {missing_fields}")
            return False
        return True

# Global configuration instance
config = Config() 