from pybit.unified_trading import HTTP
import pandas as pd
import numpy as np
from typing import Dict, Optional
from ..utils.logger import setup_logger
from ..utils.config import Config

class MarketData:
    """
    Handles market data operations
    """
    def __init__(self):
        self.config = Config()
        self.logger = setup_logger(__name__, 'market_data')
        self.session = self._initialize_session()
        
    def _initialize_session(self) -> HTTP:
        """
        Initialize the Bybit session
        """
        try:
            exchange_config = self.config.get_exchange_config()
            session = HTTP(
                testnet=False,
                api_key=exchange_config['api_key'],
                api_secret=exchange_config['secret_key']
            )
            
            # Set leverage
            try:
                session.set_leverage(
                    category="linear",
                    symbol=exchange_config['trading_pair'],
                    buyLeverage=str(exchange_config['leverage']),
                    sellLeverage=str(exchange_config['leverage'])
                )
            except Exception as e:
                self.logger.warning(f"Could not set leverage: {str(e)}")
            
            self.logger.info(f"Session initialized with {exchange_config['trading_pair']} at {exchange_config['leverage']}x leverage")
            return session
            
        except Exception as e:
            self.logger.error(f"Error initializing session: {str(e)}")
            raise
            
    def fetch_ohlcv(self, limit: int = 100) -> Optional[pd.DataFrame]:
        """
        Fetch OHLCV data from the exchange
        
        Args:
            limit (int): Number of candles to fetch
            
        Returns:
            pd.DataFrame: DataFrame with OHLCV data and technical indicators
        """
        try:
            exchange_config = self.config.get_exchange_config()
            klines = self.session.get_kline(
                category="linear",
                symbol=exchange_config['trading_pair'],
                interval=exchange_config['timeframe'],
                limit=limit
            )
            
            if klines['retCode'] == 0:
                data = klines['result']['list']
                df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'turnover'])
                df['timestamp'] = pd.to_datetime(df['timestamp'].astype(int), unit='ms')
                df.set_index('timestamp', inplace=True)
                
                # Convert string values to float
                for col in ['open', 'high', 'low', 'close', 'volume']:
                    df[col] = df[col].astype(float)
                
                # Add technical indicators
                df = self._add_technical_indicators(df)
                
                self.logger.info(f"Fetched {len(df)} candles for {exchange_config['trading_pair']}")
                return df
            else:
                self.logger.error(f"Error fetching klines: {klines['retMsg']}")
                return None
            
        except Exception as e:
            self.logger.error(f"Error fetching OHLCV data: {str(e)}")
            return None
            
    def _add_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add technical indicators to the DataFrame
        
        Args:
            df (pd.DataFrame): DataFrame with OHLCV data
            
        Returns:
            pd.DataFrame: DataFrame with added technical indicators
        """
        try:
            # RSI
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['rsi'] = 100 - (100 / (1 + rs))
            
            # Moving Averages
            df['sma'] = df['close'].rolling(window=20).mean()
            df['ema'] = df['close'].ewm(span=20, adjust=False).mean()
            
            # MACD
            exp1 = df['close'].ewm(span=12, adjust=False).mean()
            exp2 = df['close'].ewm(span=26, adjust=False).mean()
            df['macd'] = exp1 - exp2
            df['signal'] = df['macd'].ewm(span=9, adjust=False).mean()
            
            # Bollinger Bands
            df['bollinger_middle'] = df['close'].rolling(window=20).mean()
            df['bollinger_std'] = df['close'].rolling(window=20).std()
            df['bollinger_upper'] = df['bollinger_middle'] + (df['bollinger_std'] * 2)
            df['bollinger_lower'] = df['bollinger_middle'] - (df['bollinger_std'] * 2)
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error adding technical indicators: {str(e)}")
            return df
            
    def get_current_price(self) -> Optional[float]:
        """
        Get the current price of the trading pair
        
        Returns:
            float: Current price
        """
        try:
            exchange_config = self.config.get_exchange_config()
            tickers = self.session.get_tickers(
                category="linear",
                symbol=exchange_config['trading_pair']
            )
            
            if tickers['retCode'] == 0:
                return float(tickers['result']['list'][0]['lastPrice'])
            else:
                self.logger.error(f"Error getting ticker: {tickers['retMsg']}")
                return None
            
        except Exception as e:
            self.logger.error(f"Error getting current price: {str(e)}")
            return None
            
    def get_position(self) -> Optional[Dict]:
        """
        Get current position information
        
        Returns:
            Dict: Position information
        """
        try:
            exchange_config = self.config.get_exchange_config()
            positions = self.session.get_positions(
                category="linear",
                symbol=exchange_config['trading_pair']
            )
            
            if positions['retCode'] == 0 and positions['result']['list']:
                position = positions['result']['list'][0]
                if float(position['size']) > 0:
                    return {
                        'side': 'long' if position['side'] == 'Buy' else 'short',
                        'size': float(position['size']),
                        'entry_price': float(position['avgPrice']),
                        'leverage': float(position['leverage']),
                        'unrealized_pnl': float(position['unrealisedPnl'])
                    }
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting position: {str(e)}")
            return None

    def get_account_balance(self) -> Dict:
        """
        Get account balance information
        """
        try:
            wallet = self.session.get_wallet_balance(accountType="UNIFIED")
            if wallet['retCode'] == 0:
                usdt_balance = wallet['result']['list'][0]['coin'][0]
                return {
                    'total': float(usdt_balance['walletBalance']),
                    'used': float(usdt_balance['lockedBalance']),
                    'free': float(usdt_balance['availableToWithdraw'])
                }
            else:
                self.logger.error(f"Error getting wallet balance: {wallet['retMsg']}")
                raise Exception(wallet['retMsg'])
                
        except Exception as e:
            self.logger.error(f"Error fetching account balance: {str(e)}")
            raise
            
    def get_market_summary(self) -> Dict:
        """
        Get a summary of current market conditions
        """
        try:
            df = self.fetch_ohlcv(limit=1)
            current_price = self.get_current_price()
            
            return {
                'current_price': current_price,
                'rsi': df['rsi'].iloc[-1],
                'macd': df['macd'].iloc[-1],
                'signal': df['signal'].iloc[-1],
                'bollinger_upper': df['bollinger_upper'].iloc[-1],
                'bollinger_lower': df['bollinger_lower'].iloc[-1],
                'volume': df['volume'].iloc[-1]
            }
            
        except Exception as e:
            self.logger.error(f"Error getting market summary: {str(e)}")
            raise 