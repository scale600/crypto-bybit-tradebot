from pybit.unified_trading import HTTP
import math
from typing import Dict, Optional, List
from ..utils.logger import setup_logger
from ..utils.config import Config

class Exchange:
    """
    Handles exchange operations
    """
    def __init__(self):
        self.config = Config()
        self.logger = setup_logger(__name__, 'exchange')
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
            
    def set_leverage(self, leverage: int) -> bool:
        """
        Set leverage for the trading pair
        
        Args:
            leverage (int): Leverage multiplier
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            exchange_config = self.config.get_exchange_config()
            response = self.session.set_leverage(
                category="linear",
                symbol=exchange_config['trading_pair'],
                buyLeverage=str(leverage),
                sellLeverage=str(leverage)
            )
            
            if response['retCode'] == 0:
                self.logger.info(f"Leverage set to {leverage}x for {exchange_config['trading_pair']}")
                return True
            else:
                self.logger.error(f"Error setting leverage: {response['retMsg']}")
                return False
            
        except Exception as e:
            self.logger.error(f"Error setting leverage: {str(e)}")
            return False
            
    def calculate_position_size(self) -> float:
        """
        Calculate position size based on account balance and risk parameters
        
        Returns:
            float: Position size in USDT
        """
        try:
            # Get account balance
            wallet = self.session.get_wallet_balance(accountType="UNIFIED")
            if wallet['retCode'] == 0:
                usdt_balance = float(wallet['result']['list'][0]['coin'][0]['walletBalance'])
                
                # Get risk parameters
                risk_params = self.config.get_risk_params()
                position_size = min(
                    usdt_balance * 0.1,  # Use at most 10% of balance
                    risk_params['max_position_size']
                )
                
                self.logger.info(f"Calculated position size: {position_size} USDT")
                return position_size
            else:
                self.logger.error(f"Error getting wallet balance: {wallet['retMsg']}")
                return 0.0
            
        except Exception as e:
            self.logger.error(f"Error calculating position size: {str(e)}")
            return 0.0
            
    def create_market_order(self, side: str, amount: float) -> Optional[Dict]:
        """
        Create a market order
        
        Args:
            side (str): 'Buy' or 'Sell'
            amount (float): Amount to trade in USDT
            
        Returns:
            Dict: Order information
        """
        try:
            exchange_config = self.config.get_exchange_config()
            response = self.session.place_order(
                category="linear",
                symbol=exchange_config['trading_pair'],
                side=side,
                orderType="Market",
                qty=str(amount),
                timeInForce="GTC"
            )
            
            if response['retCode'] == 0:
                self.logger.info(f"Created {side} market order: {response['result']['orderId']}")
                return response['result']
            else:
                self.logger.error(f"Error creating market order: {response['retMsg']}")
                return None
            
        except Exception as e:
            self.logger.error(f"Error creating market order: {str(e)}")
            return None
            
    def create_stop_loss_order(self, side: str, amount: float, price: float) -> Optional[Dict]:
        """
        Create a stop loss order
        
        Args:
            side (str): 'Buy' or 'Sell'
            amount (float): Amount to trade in USDT
            price (float): Stop loss price
            
        Returns:
            Dict: Order information
        """
        try:
            exchange_config = self.config.get_exchange_config()
            response = self.session.place_order(
                category="linear",
                symbol=exchange_config['trading_pair'],
                side=side,
                orderType="Stop",
                qty=str(amount),
                price=str(price),
                stopPrice=str(price),
                timeInForce="GTC"
            )
            
            if response['retCode'] == 0:
                self.logger.info(f"Created {side} stop loss order at {price}: {response['result']['orderId']}")
                return response['result']
            else:
                self.logger.error(f"Error creating stop loss order: {response['retMsg']}")
                return None
            
        except Exception as e:
            self.logger.error(f"Error creating stop loss order: {str(e)}")
            return None
            
    def create_take_profit_order(self, side: str, amount: float, price: float) -> Optional[Dict]:
        """
        Create a take profit order
        
        Args:
            side (str): 'Buy' or 'Sell'
            amount (float): Amount to trade in USDT
            price (float): Take profit price
            
        Returns:
            Dict: Order information
        """
        try:
            exchange_config = self.config.get_exchange_config()
            response = self.session.place_order(
                category="linear",
                symbol=exchange_config['trading_pair'],
                side=side,
                orderType="Limit",
                qty=str(amount),
                price=str(price),
                timeInForce="GTC"
            )
            
            if response['retCode'] == 0:
                self.logger.info(f"Created {side} take profit order at {price}: {response['result']['orderId']}")
                return response['result']
            else:
                self.logger.error(f"Error creating take profit order: {response['retMsg']}")
                return None
            
        except Exception as e:
            self.logger.error(f"Error creating take profit order: {str(e)}")
            return None
            
    def cancel_all_orders(self) -> bool:
        """
        Cancel all open orders
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            exchange_config = self.config.get_exchange_config()
            response = self.session.cancel_all_orders(
                category="linear",
                symbol=exchange_config['trading_pair']
            )
            
            if response['retCode'] == 0:
                self.logger.info("Cancelled all open orders")
                return True
            else:
                self.logger.error(f"Error cancelling orders: {response['retMsg']}")
                return False
            
        except Exception as e:
            self.logger.error(f"Error cancelling orders: {str(e)}")
            return False
            
    def get_open_orders(self) -> list:
        """
        Get all open orders
        
        Returns:
            list: List of open orders
        """
        try:
            exchange_config = self.config.get_exchange_config()
            response = self.session.get_open_orders(
                category="linear",
                symbol=exchange_config['trading_pair']
            )
            
            if response['retCode'] == 0:
                self.logger.info(f"Fetched {len(response['result']['list'])} open orders")
                return response['result']['list']
            else:
                self.logger.error(f"Error fetching open orders: {response['retMsg']}")
                return []
            
        except Exception as e:
            self.logger.error(f"Error fetching open orders: {str(e)}")
            return []
            
    def get_order_status(self, order_id: str) -> Optional[Dict]:
        """
        Get status of a specific order
        
        Args:
            order_id (str): Order ID
            
        Returns:
            Dict: Order status
        """
        try:
            exchange_config = self.config.get_exchange_config()
            response = self.session.get_order_history(
                category="linear",
                symbol=exchange_config['trading_pair'],
                orderId=order_id
            )
            
            if response['retCode'] == 0 and response['result']['list']:
                order = response['result']['list'][0]
                self.logger.info(f"Order {order_id} status: {order['orderStatus']}")
                return order
            else:
                self.logger.error(f"Error fetching order status: {response['retMsg']}")
                return None
            
        except Exception as e:
            self.logger.error(f"Error fetching order status: {str(e)}")
            return None 