# API Integration Guide

## Fidelity API Integration

### Overview
The NVSTWZ bot is designed to integrate with Fidelity's trading platform. Currently, the bot uses a simulated trading environment, but this guide will help you set up real Fidelity API integration.

### Fidelity API Setup

#### 1. Fidelity Developer Account
- Visit [Fidelity Developer Portal](https://developer.fidelity.com)
- Create a developer account
- Apply for API access (may require approval)

#### 2. OAuth 2.0 Authentication
Fidelity uses OAuth 2.0 for authentication. You'll need:
- Client ID
- Client Secret
- Redirect URI

#### 3. API Endpoints
Key endpoints you'll need to implement:
- Account information
- Portfolio positions
- Order placement
- Order status
- Market data

### Implementation Steps

#### Step 1: Create Fidelity API Client
```python
# src/fidelity_client.py
import requests
from typing import Dict, List, Optional

class FidelityClient:
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.base_url = "https://api.fidelity.com"  # Replace with actual URL
    
    async def authenticate(self):
        """Authenticate with Fidelity API."""
        # Implement OAuth 2.0 flow
        pass
    
    async def get_account_info(self) -> Dict:
        """Get account information."""
        pass
    
    async def get_positions(self) -> List[Dict]:
        """Get current positions."""
        pass
    
    async def place_order(self, order: Dict) -> Dict:
        """Place a trading order."""
        pass
    
    async def get_order_status(self, order_id: str) -> Dict:
        """Get order status."""
        pass
```

#### Step 2: Update Bot to Use Real API
Replace the simulated trading in `src/bot.py` with real API calls:

```python
# In src/bot.py, replace _execute_trade method
async def _execute_trade(self, trade: Trade) -> bool:
    """Execute a trade using Fidelity API."""
    try:
        # Create order payload
        order_payload = {
            "symbol": trade.symbol,
            "quantity": trade.quantity,
            "side": trade.order_type.value,
            "type": "MARKET",  # or "LIMIT"
            "time_in_force": "DAY"
        }
        
        # Place order via Fidelity API
        result = await self.fidelity_client.place_order(order_payload)
        
        if result.get("status") == "FILLED":
            trade.order_id = result.get("order_id")
            trade.status = "FILLED"
            return True
        else:
            trade.status = "REJECTED"
            return False
            
    except Exception as e:
        logger.error(f"Error executing trade: {e}")
        return False
```

### Market Data APIs

#### Alpha Vantage
- **Purpose**: Real-time and historical market data
- **Setup**: Get free API key from [Alpha Vantage](https://www.alphavantage.co/)
- **Rate Limits**: 5 calls per minute (free tier)

#### News API
- **Purpose**: Market news and sentiment analysis
- **Setup**: Get API key from [NewsAPI](https://newsapi.org/)
- **Rate Limits**: 1,000 requests per day (free tier)

#### Finnhub
- **Purpose**: Real-time market data and news
- **Setup**: Get API key from [Finnhub](https://finnhub.io/)
- **Rate Limits**: 60 calls per minute (free tier)

### Environment Configuration

Update your `.env` file with all API keys:

```bash
# Fidelity API
FIDELITY_CLIENT_ID=your_fidelity_client_id
FIDELITY_CLIENT_SECRET=your_fidelity_client_secret
FIDELITY_REDIRECT_URI=http://localhost:8000/callback

# Market Data APIs
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
NEWS_API_KEY=your_news_api_key
FINNHUB_API_KEY=your_finnhub_key
```

### Testing API Integration

#### 1. Test Market Data
```python
# Test market data APIs
async def test_market_data():
    market_data = MarketDataEngine()
    
    # Test price data
    price = await market_data.get_real_time_price("AAPL")
    print(f"AAPL Price: ${price.price}")
    
    # Test news
    news = await market_data.get_market_news(["AAPL"], hours_back=24)
    print(f"Found {len(news)} news articles")
```

#### 2. Test Trading Signals
```python
# Test strategy engine
async def test_strategy():
    market_data = MarketDataEngine()
    strategy = StrategyEngine(market_data)
    
    signals = await strategy.generate_signals()
    print(f"Generated {len(signals)} trading signals")
```

### Security Considerations

1. **API Key Security**
   - Never commit API keys to version control
   - Use environment variables
   - Rotate keys regularly

2. **Rate Limiting**
   - Implement proper rate limiting
   - Cache responses when possible
   - Handle API errors gracefully

3. **Error Handling**
   - Implement retry logic
   - Log all API errors
   - Have fallback data sources

### Troubleshooting

#### Common Issues

1. **Authentication Errors**
   - Check client ID and secret
   - Verify redirect URI
   - Ensure OAuth flow is correct

2. **Rate Limit Errors**
   - Implement exponential backoff
   - Cache frequently requested data
   - Use multiple API keys if available

3. **Order Execution Errors**
   - Validate order parameters
   - Check account balance
   - Verify symbol is tradeable

### Next Steps

1. **Implement Real Fidelity API Client**
2. **Add Comprehensive Error Handling**
3. **Implement Order Management System**
4. **Add Position Tracking**
5. **Create Performance Monitoring**

### Resources

- [Fidelity Developer Documentation](https://developer.fidelity.com)
- [Alpha Vantage Documentation](https://www.alphavantage.co/documentation/)
- [News API Documentation](https://newsapi.org/docs)
- [Finnhub Documentation](https://finnhub.io/docs/api) 