"""
Main bot orchestrator for NVSTWZ autonomous investment bot.
"""
import asyncio
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import signal
import sys

from .config import config
from .models import BotStatus, Portfolio, Trade, Position, TradingSignal
from .market_data import MarketDataEngine
from .strategy import StrategyEngine
from .utils.logger import get_logger

logger = get_logger(__name__)

class NVSTWZBot:
    """Main autonomous investment bot."""
    
    def __init__(self):
        self.is_running = False
        self.market_data = None
        self.strategy = None
        self.portfolio = None
        self.current_positions = []
        self.daily_pnl = 0.0
        self.total_pnl = 0.0
        self.initial_capital = config.trading.initial_capital
        self.current_capital = self.initial_capital
        self.daily_trades = 0
        self.last_heartbeat = datetime.now()
        self.errors = []
        self.warnings = []
        
        # Trading state
        self.active_trades = []
        self.pending_orders = []
        
        # Performance tracking
        self.daily_start_value = self.initial_capital
        self.last_reset_date = datetime.now().date()
    
    async def start(self):
        """Start the bot."""
        try:
            logger.info("Starting NVSTWZ Autonomous Investment Bot...")
            
            # Initialize components
            await self._initialize_components()
            
            # Validate configuration
            if not config.validate():
                logger.error("Configuration validation failed")
                return False
            
            # Set up signal handlers
            self._setup_signal_handlers()
            
            # Start the main trading loop
            self.is_running = True
            logger.info(f"Bot started with initial capital: ${self.initial_capital:.2f}")
            
            await self._main_loop()
            
        except Exception as e:
            logger.error(f"Error starting bot: {e}")
            self.errors.append(str(e))
            return False
    
    async def stop(self):
        """Stop the bot."""
        logger.info("Stopping NVSTWZ Bot...")
        self.is_running = False
        
        # Close any open positions if needed
        await self._close_all_positions()
        
        logger.info("Bot stopped successfully")
    
    async def _initialize_components(self):
        """Initialize all bot components."""
        try:
            # Initialize market data engine
            self.market_data = MarketDataEngine()
            
            # Initialize strategy engine
            self.strategy = StrategyEngine(self.market_data)
            
            # Initialize portfolio
            self.portfolio = Portfolio(
                total_value=self.initial_capital,
                cash_balance=self.initial_capital,
                invested_amount=0.0,
                daily_pnl=0.0,
                total_pnl=0.0,
                daily_return=0.0,
                total_return=0.0,
                last_updated=datetime.now()
            )
            
            logger.info("All components initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing components: {e}")
            raise
    
    def _setup_signal_handlers(self):
        """Set up signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, shutting down gracefully...")
            asyncio.create_task(self.stop())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def _main_loop(self):
        """Main trading loop."""
        logger.info("Entering main trading loop...")
        
        while self.is_running:
            try:
                # Update daily counters
                self._reset_daily_counters()
                
                # Get market status
                market_status = await self.market_data.get_market_status()
                
                # Update portfolio
                await self._update_portfolio()
                
                # Check risk limits
                if not self._check_risk_limits():
                    logger.warning("Risk limits exceeded, pausing trading")
                    await asyncio.sleep(300)  # Wait 5 minutes
                    continue
                
                # Generate trading signals
                signals = await self.strategy.generate_signals(self.current_positions)
                
                # Execute trades
                for signal in signals:
                    if await self._execute_signal(signal):
                        self.daily_trades += 1
                        self.strategy.update_trade_count()
                
                # Monitor existing positions
                await self._monitor_positions()
                
                # Log status
                await self._log_status()
                
                # Wait before next iteration
                await asyncio.sleep(30)  # 30-second intervals
                
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                self.errors.append(str(e))
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    async def _execute_signal(self, signal: TradingSignal) -> bool:
        """Execute a trading signal."""
        try:
            # Validate signal
            if not await self.strategy.validate_signal(signal):
                logger.info(f"Signal validation failed for {signal.symbol}")
                return False
            
            # Check if we have enough capital
            if not self._check_capital_availability(signal):
                logger.info(f"Insufficient capital for {signal.symbol}")
                return False
            
            # Calculate position size
            position_size = self._calculate_position_size(signal)
            
            # Create trade
            trade = Trade(
                symbol=signal.symbol,
                order_type=signal.signal_type,
                quantity=position_size,
                price=signal.price_target,  # Use target price as estimate
                timestamp=datetime.now(),
                notes=signal.reasoning
            )
            
            # Simulate trade execution (replace with actual Fidelity API call)
            success = await self._execute_trade(trade)
            
            if success:
                logger.info(f"Executed {signal.signal_type.value} order for {signal.symbol}: {position_size} shares")
                self.active_trades.append(trade)
                return True
            else:
                logger.warning(f"Trade execution failed for {signal.symbol}")
                return False
                
        except Exception as e:
            logger.error(f"Error executing signal for {signal.symbol}: {e}")
            return False
    
    async def _execute_trade(self, trade: Trade) -> bool:
        """Execute a trade (placeholder for Fidelity API integration)."""
        try:
            # TODO: Replace with actual Fidelity API integration
            # For now, simulate successful execution
            
            # Update portfolio
            if trade.order_type.value == "BUY":
                cost = trade.quantity * trade.price
                if self.portfolio.cash_balance >= cost:
                    self.portfolio.cash_balance -= cost
                    self.portfolio.invested_amount += cost
                    
                    # Add to positions
                    position = Position(
                        symbol=trade.symbol,
                        quantity=trade.quantity,
                        average_price=trade.price,
                        current_price=trade.price,
                        market_value=cost,
                        unrealized_pnl=0.0,
                        realized_pnl=0.0,
                        last_updated=datetime.now()
                    )
                    self.portfolio.positions.append(position)
                    self.current_positions.append(trade.symbol)
                    
                    trade.status = "FILLED"
                    return True
                else:
                    return False
            else:  # SELL
                # Find position to sell
                for position in self.portfolio.positions:
                    if position.symbol == trade.symbol:
                        if position.quantity >= trade.quantity:
                            proceeds = trade.quantity * trade.price
                            self.portfolio.cash_balance += proceeds
                            self.portfolio.invested_amount -= proceeds
                            
                            # Update position
                            position.quantity -= trade.quantity
                            if position.quantity == 0:
                                self.portfolio.positions.remove(position)
                                self.current_positions.remove(trade.symbol)
                            
                            trade.status = "FILLED"
                            return True
                        else:
                            return False
                
                return False
                
        except Exception as e:
            logger.error(f"Error executing trade: {e}")
            return False
    
    def _check_capital_availability(self, signal: TradingSignal) -> bool:
        """Check if we have enough capital for the trade."""
        # Simple check - ensure we have at least 10% of capital available
        min_capital = self.current_capital * 0.1
        return self.portfolio.cash_balance >= min_capital
    
    def _calculate_position_size(self, signal: TradingSignal) -> float:
        """Calculate position size based on risk management rules."""
        # Simple position sizing - use 20% of available capital
        available_capital = self.portfolio.cash_balance
        position_value = available_capital * 0.2
        
        # Get current price estimate
        current_price = signal.price_target  # Use target as estimate
        
        # Calculate shares
        shares = position_value / current_price
        
        # Round down to whole shares
        return int(shares)
    
    async def _monitor_positions(self):
        """Monitor existing positions for profit taking or stop loss."""
        try:
            for position in self.portfolio.positions[:]:  # Copy list to avoid modification during iteration
                # Get current market data
                market_data = await self.market_data.get_real_time_price(position.symbol)
                if not market_data:
                    continue
                
                # Update position
                position.current_price = market_data.price
                position.market_value = position.quantity * market_data.price
                position.unrealized_pnl = (market_data.price - position.average_price) * position.quantity
                position.last_updated = datetime.now()
                
                # Check stop loss (2% loss)
                stop_loss_price = position.average_price * 0.98
                if market_data.price <= stop_loss_price:
                    logger.info(f"Stop loss triggered for {position.symbol}")
                    await self._close_position(position, "Stop loss")
                
                # Check profit target (5% gain)
                profit_target_price = position.average_price * 1.05
                if market_data.price >= profit_target_price:
                    logger.info(f"Profit target reached for {position.symbol}")
                    await self._close_position(position, "Profit target")
                
        except Exception as e:
            logger.error(f"Error monitoring positions: {e}")
    
    async def _close_position(self, position: Position, reason: str):
        """Close a position."""
        try:
            trade = Trade(
                symbol=position.symbol,
                order_type="SELL",
                quantity=position.quantity,
                price=position.current_price,
                timestamp=datetime.now(),
                notes=f"Closing position: {reason}"
            )
            
            success = await self._execute_trade(trade)
            if success:
                logger.info(f"Closed position in {position.symbol}: {reason}")
            else:
                logger.error(f"Failed to close position in {position.symbol}")
                
        except Exception as e:
            logger.error(f"Error closing position: {e}")
    
    async def _close_all_positions(self):
        """Close all open positions."""
        logger.info("Closing all positions...")
        
        for position in self.portfolio.positions[:]:
            await self._close_position(position, "Bot shutdown")
    
    async def _update_portfolio(self):
        """Update portfolio values and P&L."""
        try:
            total_value = self.portfolio.cash_balance
            
            for position in self.portfolio.positions:
                # Get current price
                market_data = await self.market_data.get_real_time_price(position.symbol)
                if market_data:
                    position.current_price = market_data.price
                    position.market_value = position.quantity * market_data.price
                    position.unrealized_pnl = (market_data.price - position.average_price) * position.quantity
                
                total_value += position.market_value
            
            # Update portfolio
            self.portfolio.total_value = total_value
            self.portfolio.invested_amount = total_value - self.portfolio.cash_balance
            
            # Calculate P&L
            self.total_pnl = total_value - self.initial_capital
            self.daily_pnl = total_value - self.daily_start_value
            
            self.portfolio.total_pnl = self.total_pnl
            self.portfolio.daily_pnl = self.daily_pnl
            self.portfolio.total_return = (self.total_pnl / self.initial_capital) * 100
            self.portfolio.daily_return = (self.daily_pnl / self.daily_start_value) * 100
            self.portfolio.last_updated = datetime.now()
            
            self.current_capital = total_value
            
        except Exception as e:
            logger.error(f"Error updating portfolio: {e}")
    
    def _check_risk_limits(self) -> bool:
        """Check if we're within risk limits."""
        # Check daily loss limit
        if self.daily_pnl < -self.initial_capital * config.trading.max_daily_loss:
            logger.warning("Daily loss limit exceeded")
            return False
        
        # Check total loss limit
        if self.total_pnl < -self.initial_capital * 0.5:  # 50% total loss limit
            logger.warning("Total loss limit exceeded")
            return False
        
        return True
    
    def _reset_daily_counters(self):
        """Reset daily counters if it's a new day."""
        today = datetime.now().date()
        if today > self.last_reset_date:
            self.daily_trades = 0
            self.daily_start_value = self.current_capital
            self.daily_pnl = 0.0
            self.last_reset_date = today
            logger.info("Daily counters reset")
    
    async def _log_status(self):
        """Log current bot status."""
        self.last_heartbeat = datetime.now()
        
        status = BotStatus(
            is_running=self.is_running,
            last_heartbeat=self.last_heartbeat,
            active_trades=len(self.active_trades),
            daily_trades=self.daily_trades,
            current_capital=self.current_capital,
            daily_pnl=self.daily_pnl,
            errors=self.errors[-5:],  # Last 5 errors
            warnings=self.warnings[-5:]  # Last 5 warnings
        )
        
        logger.info(f"Bot Status - Capital: ${self.current_capital:.2f}, Daily P&L: ${self.daily_pnl:.2f}, "
                   f"Daily Trades: {self.daily_trades}, Active Positions: {len(self.portfolio.positions)}")
    
    def get_status(self) -> BotStatus:
        """Get current bot status."""
        return BotStatus(
            is_running=self.is_running,
            last_heartbeat=self.last_heartbeat,
            active_trades=len(self.active_trades),
            daily_trades=self.daily_trades,
            current_capital=self.current_capital,
            daily_pnl=self.daily_pnl,
            errors=self.errors[-5:],
            warnings=self.warnings[-5:]
        ) 