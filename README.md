# Crypto Bybit TradeBot

Automated cryptocurrency futures trading bot powered by GPT-4, built on top of the Bybit Unified Trading API.

## Overview

Crypto Bybit TradeBot is a Python-based automated trading system that combines real-time technical analysis with AI-driven decision making. It operates on a continuous loop: fetch market data → compute technical indicators → query GPT-4 for a trading decision → execute with risk controls. The bot supports both live trading and paper trading modes, with a Streamlit dashboard for monitoring.

### How It Works

1. **Market Data** — Fetches OHLCV candlestick data from Bybit and computes technical indicators (RSI, MACD, Bollinger Bands, SMA, EMA).
2. **AI Analysis** — Sends a structured market summary (price action, indicators, volume) to GPT-4, which returns a trading action (`long` / `short`), confidence score, and reasoning.
3. **Trade Execution** — If confidence exceeds the configured threshold, the bot places a market order with automatic stop-loss and take-profit brackets.
4. **Risk Management** — Position sizing is capped at 10% of available balance or the configured maximum. A minimum trade interval prevents overtrading.
5. **Position Monitoring** — While a position is open, each loop cycle re-evaluates via GPT-4 whether to close it.

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Language** | Python 3.8+ | Core runtime |
| **Exchange API** | [pybit](https://github.com/bybit-exchange/pybit) v5.6 | Bybit Unified Trading (linear futures, orders, positions) |
| **AI / LLM** | [OpenAI](https://platform.openai.com/docs) v1.12 (GPT-4) | Market analysis & trade decision generation |
| **Data** | [pandas](https://pandas.pydata.org/) v2.1, [numpy](https://numpy.org/) v1.26 | OHLCV processing & technical indicator computation |
| **Config** | [python-dotenv](https://github.com/theskumar/python-dotenv) v1.0 | Environment-based configuration via `.env` |
| **Dashboard** | [Streamlit](https://streamlit.io/) v1.32 | Real-time monitoring dashboard (optional) |
| **Visualization** | [matplotlib](https://matplotlib.org/) v3.8 | Chart rendering |
| **Technical Analysis** | Custom implementation | RSI, MACD, Bollinger Bands, SMA, EMA |

## Architecture

```
crypto-bybit-tradebot/
├── src/
│   ├── bot.py                  # TradingBot — main loop orchestrator
│   ├── config.py               # Legacy config (environment globals)
│   ├── data/
│   │   └── market_data.py      # MarketData — OHLCV fetching, indicators, position tracking
│   ├── trading/
│   │   └── exchange.py         # Exchange — order placement, leverage, balance
│   ├── ai/
│   │   └── analysis.py         # MarketAnalysis — GPT-4 integration & decision engine
│   └── utils/
│       ├── config.py           # Config — typed config accessor with validation
│       └── logger.py           # Structured logging (console + file)
├── run.py                      # Entry point with graceful shutdown (SIGINT/SIGTERM)
├── paper_trade.py              # Paper trading mode (no real orders)
├── test_bot.py                 # Test harness
├── examples/
│   └── mvp.py                  # Minimal working example
├── requirements.txt
└── .env.example
```

### Key Components

**`TradingBot`** (`src/bot.py`) — The main orchestrator. Runs an infinite loop that:
- Respects the minimum trade interval between actions
- Fetches fresh OHLCV data each cycle
- Delegates decision-making to `MarketAnalysis`
- Routes to `_handle_existing_position()` when a position is open, or `_look_for_opportunities()` when flat
- Sets stop-loss and take-profit orders after each entry

**`MarketData`** (`src/data/market_data.py`) — Data layer:
- Fetches kline (candlestick) data from Bybit via `pybit.HTTP`
- Computes technical indicators inline: RSI (14), SMA (20), EMA (20), MACD (12/26/9), Bollinger Bands (20, 2σ)
- Provides current price, position info, and account balance queries

**`Exchange`** (`src/trading/exchange.py`) — Order execution:
- Market orders, stop-loss orders, and take-profit (limit) orders
- Position size calculation: `min(10% of wallet balance, max_position_size)`
- Leverage setting, order cancellation, and order status queries

**`MarketAnalysis`** (`src/ai/analysis.py`) — AI decision engine:
- Formats market data into a structured prompt with price changes (1h, 4h, 24h) and all indicator readings
- Calls OpenAI GPT-4 with a system prompt instructing it to act as a crypto trading expert
- Parses the response (`action|confidence|reason`) and applies a confidence threshold (default: 70%)

## Quick Start

### Prerequisites

- Python 3.8+
- [Bybit account](https://www.bybit.com) with API access
- [OpenAI API key](https://platform.openai.com)

### Installation

```bash
git clone https://github.com/scale600/crypto-bybit-tradebot.git
cd crypto-bybit-tradebot
pip install -r requirements.txt
cp .env.example .env
```

### Configuration

Edit `.env` with your keys and trading parameters:

```env
# Required
OPENAI_API_KEY=sk-...
BYBIT_API_KEY=...
BYBIT_SECRET_KEY=...

# Trading
TRADING_PAIR=BTCUSDT
LEVERAGE=5
POSITION_SIZE=100
STOP_LOSS_PERCENT=0.5
TAKE_PROFIT_PERCENT=0.5
TIMEFRAME=15

# AI
AI_MODEL=gpt-4
AI_TEMPERATURE=0.7

# Risk Management
MAX_POSITION_SIZE=1000
MIN_TRADE_INTERVAL=300
CHECK_INTERVAL=60
CONFIDENCE_THRESHOLD=70
```

| Parameter | Description | Default |
|---|---|---|
| `TRADING_PAIR` | Bybit linear futures symbol | `BTCUSDT` |
| `LEVERAGE` | Leverage multiplier (1–100) | `5` |
| `POSITION_SIZE` | Default position size in USDT | `100` |
| `TIMEFRAME` | Candle interval in minutes | `15` |
| `CHECK_INTERVAL` | Seconds between market checks | `60` |
| `MIN_TRADE_INTERVAL` | Minimum seconds between trades | `300` |
| `CONFIDENCE_THRESHOLD` | Minimum GPT-4 confidence to execute (0–100) | `70` |

### Run

```bash
# Live trading
python run.py

# Paper trading (simulated, no real orders)
python paper_trade.py

# Dashboard (Streamlit)
streamlit run src/dashboard.py
```

## Disclaimer

This software is for educational purposes only. Use at your own risk. The developers are not responsible for any financial losses incurred through its use.

## License

MIT
