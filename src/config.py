import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_SECRET_KEY = os.getenv("BINANCE_SECRET_KEY")

# Trading Parameters
TRADING_PAIR = os.getenv("TRADING_PAIR", "BTC/USDT")
LEVERAGE = int(os.getenv("LEVERAGE", "5"))
POSITION_SIZE = float(os.getenv("POSITION_SIZE", "100"))
STOP_LOSS_PERCENT = float(os.getenv("STOP_LOSS_PERCENT", "0.5"))
TAKE_PROFIT_PERCENT = float(os.getenv("TAKE_PROFIT_PERCENT", "0.5"))
TIMEFRAME = os.getenv("TIMEFRAME", "15m")

# Exchange Configuration
EXCHANGE_CONFIG = {
    'apiKey': BINANCE_API_KEY,
    'secret': BINANCE_SECRET_KEY,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future',
        'adjustForTimeDifference': True
    }
} 