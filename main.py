#!/usr/bin/env python3
"""
Main entry point for NVSTWZ Autonomous Investment Bot.
"""
import asyncio
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.bot import NVSTWZBot
from src.config import config
from src.utils.logger import get_logger

logger = get_logger(__name__)

async def main():
    """Main function to run the bot."""
    try:
        logger.info("=" * 60)
        logger.info("NVSTWZ Autonomous Investment Bot")
        logger.info("=" * 60)
        
        # Check if configuration is valid
        if not config.validate():
            logger.error("Configuration validation failed. Please check your .env file.")
            logger.error("Required environment variables:")
            logger.error("- FIDELITY_CLIENT_ID")
            logger.error("- FIDELITY_CLIENT_SECRET") 
            logger.error("- ALPHA_VANTAGE_API_KEY")
            logger.error("- NEWS_API_KEY")
            logger.error("- FINNHUB_API_KEY")
            logger.error("- DATABASE_URL")
            return 1
        
        # Create and start the bot
        bot = NVSTWZBot()
        
        # Start the bot
        success = await bot.start()
        
        if not success:
            logger.error("Bot failed to start properly")
            return 1
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
        return 0
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1

def run_bot():
    """Run the bot with proper error handling."""
    try:
        # Run the async main function
        return asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        return 0
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        return 1

if __name__ == "__main__":
    exit_code = run_bot()
    sys.exit(exit_code) 