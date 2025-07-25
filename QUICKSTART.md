# Quick Start Guide

## Getting Started with NVSTWZ

This guide will help you get the NVSTWZ autonomous investment bot up and running in minutes.

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git

### Step 1: Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd NVSTWZ

# Run the setup script
python setup.py
```

### Step 2: Get API Keys

You'll need the following API keys:

1. **Alpha Vantage** (Free)
   - Visit: https://www.alphavantage.co/
   - Sign up for a free account
   - Copy your API key

2. **News API** (Free)
   - Visit: https://newsapi.org/
   - Sign up for a free account
   - Copy your API key

3. **Finnhub** (Free)
   - Visit: https://finnhub.io/
   - Sign up for a free account
   - Copy your API key

4. **Fidelity API** (Optional for now)
   - Visit: https://developer.fidelity.com
   - Apply for API access
   - Get Client ID and Secret

### Step 3: Configure Environment

Edit the `.env` file with your API keys:

```bash
# Market Data APIs (Required)
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here
NEWS_API_KEY=your_news_api_key_here
FINNHUB_API_KEY=your_finnhub_key_here

# Fidelity API (Optional - bot will run in simulation mode)
FIDELITY_CLIENT_ID=your_fidelity_client_id
FIDELITY_CLIENT_SECRET=your_fidelity_client_secret

# Bot Configuration
INITIAL_CAPITAL=10.00
MAX_DAILY_LOSS=0.00
TARGET_DAILY_RETURN=0.05
RISK_TOLERANCE=0.02

# Database (Use SQLite for simplicity)
DATABASE_URL=sqlite:///nvstwz.db
```

### Step 4: Run the Bot

```bash
# Start the bot
python main.py
```

The bot will:
- Initialize all components
- Start monitoring the market
- Generate trading signals
- Execute trades (in simulation mode)
- Log all activities

### Step 5: Monitor Performance

Check the logs to see the bot's activity:

```bash
# View real-time logs
tail -f logs/nvstwz.log

# View error logs
tail -f logs/errors.log
```

### Configuration Options

#### Trading Parameters

Edit these values in `.env`:

```bash
# Initial capital to trade with
INITIAL_CAPITAL=10.00

# Maximum daily loss (0.00 = no loss allowed)
MAX_DAILY_LOSS=0.00

# Target daily return (5% = 0.05)
TARGET_DAILY_RETURN=0.05

# Risk tolerance (2% = 0.02)
RISK_TOLERANCE=0.02
```

#### Market Hours

```bash
# Trading hours (EST)
MARKET_OPEN=09:30
MARKET_CLOSE=16:00
PRE_MARKET_OPEN=04:00
AFTER_HOURS_CLOSE=20:00
```

### Understanding the Bot's Behavior

#### Signal Generation
The bot generates trading signals based on:
- **Momentum**: Stocks with significant price movements
- **News**: Market-moving news events
- **Technical Analysis**: RSI, MACD, and other indicators

#### Risk Management
- **Position Sizing**: Maximum 20% of capital per position
- **Stop Loss**: 2% automatic stop loss
- **Profit Taking**: 5% automatic profit target
- **Daily Limits**: Maximum 20 trades per day

#### Trading Strategy
1. **Market Scanning**: Continuously monitors top movers
2. **Signal Generation**: Identifies high-probability opportunities
3. **Execution**: Places orders when confidence is high
4. **Monitoring**: Tracks positions for profit/loss targets
5. **Risk Control**: Enforces strict loss limits

### Troubleshooting

#### Common Issues

1. **"Configuration validation failed"**
   - Check that all required API keys are in `.env`
   - Ensure no extra spaces or quotes around values

2. **"Module not found" errors**
   - Run `pip install -r requirements.txt`
   - Ensure you're using Python 3.8+

3. **API rate limit errors**
   - The bot handles rate limits automatically
   - Consider upgrading to paid API tiers for higher limits

4. **No trading signals generated**
   - Check market hours
   - Verify API keys are working
   - Review logs for errors

#### Getting Help

1. **Check Logs**: Always check `logs/nvstwz.log` first
2. **Error Logs**: Look at `logs/errors.log` for specific errors
3. **API Status**: Verify your API keys are working
4. **Market Hours**: Ensure markets are open

### Next Steps

1. **Paper Trading**: Start with simulation mode to understand behavior
2. **Small Capital**: Begin with small amounts ($10-50)
3. **Monitor Closely**: Watch performance and adjust parameters
4. **Scale Up**: Gradually increase capital as you gain confidence

### Safety Notes

⚠️ **Important Warnings**:

- This bot is for educational purposes
- Start with small amounts
- Monitor performance closely
- Understand the risks involved
- Past performance doesn't guarantee future results
- Consider consulting a financial advisor

### Support

For issues and questions:
1. Check the logs first
2. Review the documentation
3. Check the troubleshooting section
4. Open an issue on GitHub

---

**Happy Trading! 🚀** 