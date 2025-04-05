import os
from dotenv import load_dotenv
from typing import Dict, Any

class Config:
    """
    Configuration management class
    """
    def __init__(self):
        load_dotenv()
        
        # API Keys
        self.api_keys = {
            'openai': os.getenv('OPENAI_API_KEY'),
            'bybit': {
                'api_key': os.getenv('BYBIT_API_KEY'),
                'secret_key': os.getenv('BYBIT_SECRET_KEY')
            }
        }
        
        # Trading Parameters
        self.trading_params = {
            'trading_pair': os.getenv('TRADING_PAIR', 'BTCUSDT'),
            'leverage': int(os.getenv('LEVERAGE', '5')),
            'position_size': float(os.getenv('POSITION_SIZE', '100')),
            'stop_loss_percent': float(os.getenv('STOP_LOSS_PERCENT', '0.5')),
            'take_profit_percent': float(os.getenv('TAKE_PROFIT_PERCENT', '0.5')),
            'timeframe': os.getenv('TIMEFRAME', '15')
        }
        
        # AI Configuration
        self.ai_config = {
            'model': os.getenv('AI_MODEL', 'gpt-4'),
            'temperature': float(os.getenv('AI_TEMPERATURE', '0.7'))
        }
        
        # Risk Management
        self.risk_params = {
            'max_position_size': float(os.getenv('MAX_POSITION_SIZE', '1000')),
            'min_trade_interval': int(os.getenv('MIN_TRADE_INTERVAL', '300')),
            'check_interval': int(os.getenv('CHECK_INTERVAL', '60')),
            'confidence_threshold': float(os.getenv('CONFIDENCE_THRESHOLD', '70'))
        }
        
    def validate(self) -> bool:
        """
        Validate required environment variables
        """
        required_vars = [
            'OPENAI_API_KEY',
            'BYBIT_API_KEY',
            'BYBIT_SECRET_KEY'
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            print(f"Missing required environment variables: {', '.join(missing_vars)}")
            return False
        return True
        
    def get_exchange_config(self) -> Dict[str, Any]:
        """
        Get exchange configuration
        """
        return {
            'api_key': self.api_keys['bybit']['api_key'],
            'secret_key': self.api_keys['bybit']['secret_key'],
            'trading_pair': self.trading_params['trading_pair'],
            'leverage': self.trading_params['leverage'],
            'timeframe': self.trading_params['timeframe']
        }
        
    def get_trading_params(self) -> Dict[str, Any]:
        """
        Get trading parameters
        """
        return self.trading_params
        
    def get_ai_config(self) -> Dict[str, Any]:
        """
        Get AI configuration
        """
        return self.ai_config
        
    def get_risk_params(self) -> Dict[str, Any]:
        """
        Get risk management parameters
        """
        return self.risk_params 