"""
Logging utilities for NVSTWZ investment bot.
"""
import os
import sys
from datetime import datetime
from loguru import logger
from pathlib import Path

from ..config import config

def setup_logger():
    """Setup logging configuration."""
    # Remove default logger
    logger.remove()
    
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Console logging
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=config.logging.log_level,
        colorize=True
    )
    
    # File logging
    logger.add(
        config.logging.log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        rotation="1 day",
        retention="30 days",
        compression="zip"
    )
    
    # Error logging to separate file
    logger.add(
        "logs/errors.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="ERROR",
        rotation="1 day",
        retention="90 days",
        compression="zip"
    )

def get_logger(name: str):
    """Get a logger instance for a module."""
    return logger.bind(name=name)

# Setup logger when module is imported
setup_logger() 