# Crypto Bybit Trading Bot

A cryptocurrency trading bot that uses Bybit's API for automated trading with AI-powered analysis.

## Features

- Real-time market data analysis
- Automated trading on Bybit exchange
- AI-powered market analysis using OpenAI's GPT models
- Technical analysis with multiple indicators
- Risk management system
- Web-based dashboard for monitoring
- Comprehensive logging system

## Prerequisites

- Python 3.8+
- Bybit account with API access
- OpenAI API key
- Sufficient funds in your Bybit account

## API Key Setup

### Bybit API Key Setup

1. Log in to your Bybit account at [https://www.bybit.com](https://www.bybit.com)
2. Go to Account Settings > API Management
3. Click "Create New Key"
4. Configure API key permissions:
   - Enable "Contract" for futures trading
   - Enable "Wallet" for balance checking
   - Enable "Order" for order management
   - Set IP restrictions if needed
5. Save your API Key and Secret Key securely
6. Add the keys to your `.env` file:
   ```
   BYBIT_API_KEY=your_api_key_here
   BYBIT_SECRET_KEY=your_secret_key_here
   ```

### OpenAI API Key Setup

1. Visit [https://platform.openai.com](https://platform.openai.com)
2. Sign up or log in to your account
3. Go to API Keys section
4. Click "Create new secret key"
5. Copy the generated API key
6. Add the key to your `.env` file:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/crypto-bybit-tradebot.git
cd crypto-bybit-tradebot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file from the example:
```bash
cp .env.example .env
```

4. Configure your environment variables in `.env`:
```
# API Keys
OPENAI_API_KEY=your_openai_api_key_here
BYBIT_API_KEY=your_api_key_here
BYBIT_SECRET_KEY=your_secret_key_here

# Trading Configuration
TRADING_PAIR=BTCUSDT
LEVERAGE=5
POSITION_SIZE=100
STOP_LOSS_PERCENT=0.5
TAKE_PROFIT_PERCENT=0.5
TIMEFRAME=15

# AI Configuration
AI_MODEL=gpt-4
AI_TEMPERATURE=0.7

# Risk Management
MAX_POSITION_SIZE=1000
MIN_TRADE_INTERVAL=300  # 5 minutes in seconds
CHECK_INTERVAL=60  # 1 minute in seconds
CONFIDENCE_THRESHOLD=70  # Minimum confidence score to execute trades
```

## Project Structure

```
crypto-bybit-tradebot/
├── src/
│   ├── data/
│   │   └── market_data.py      # Market data handling
│   ├── trading/
│   │   └── exchange.py         # Bybit exchange operations
│   ├── ai/
│   │   └── analysis.py         # AI analysis module
│   ├── utils/
│   │   ├── config.py           # Configuration management
│   │   └── logger.py           # Logging utility
│   └── main.py                 # Main application
├── tests/                      # Test files
├── logs/                       # Log files
├── .env.example               # Example environment variables
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## Usage

1. Start the trading bot:
```bash
python src/main.py
```

2. Monitor the dashboard:
```bash
streamlit run src/dashboard.py
```

## Configuration

### Trading Parameters

- `TRADING_PAIR`: Trading pair (e.g., BTCUSDT)
- `LEVERAGE`: Leverage multiplier (1-100)
- `POSITION_SIZE`: Default position size in USDT
- `STOP_LOSS_PERCENT`: Stop loss percentage
- `TAKE_PROFIT_PERCENT`: Take profit percentage
- `TIMEFRAME`: Candlestick timeframe (e.g., 15 for 15-minute)

### Risk Management

- `MAX_POSITION_SIZE`: Maximum position size in USDT
- `MIN_TRADE_INTERVAL`: Minimum time between trades
- `CHECK_INTERVAL`: Market check interval
- `CONFIDENCE_THRESHOLD`: Minimum AI confidence for trades

## Features in Detail

### Market Data Analysis
- Real-time price monitoring
- Technical indicators (RSI, MACD, Bollinger Bands)
- Volume analysis
- Market trend detection

### Trading Strategy
- AI-powered entry/exit signals
- Risk management rules
- Position sizing based on account balance
- Stop-loss and take-profit orders

### AI Analysis
- GPT-4 powered market analysis
- Sentiment analysis
- Pattern recognition
- Risk assessment

### Risk Management
- Position size limits
- Maximum drawdown protection
- Trading frequency limits
- Market volatility adaptation

## Logging

Logs are stored in the `logs/` directory with the following structure:
- `trading.log`: Trading operations
- `market_data.log`: Market data operations
- `ai.log`: AI analysis operations
- `error.log`: Error messages

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This trading bot is for educational purposes only. Use at your own risk. The developers are not responsible for any financial losses incurred through the use of this software.

