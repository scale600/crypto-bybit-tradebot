import time
import pandas as pd
from typing import Dict, Optional
from .data.market_data import MarketData
from .trading.exchange import Exchange
from .ai.analysis import MarketAnalysis
from .utils.config import Config
from .utils.logger import setup_logger

class TradingBot:
    """
    Main trading bot implementation
    """
    def __init__(self):
        self.config = Config()
        self.logger = setup_logger(__name__, 'trading_bot')
        self.market_data = MarketData()
        self.exchange = Exchange()
        self.analysis = MarketAnalysis()
        
        # Initialize trading state
        self.current_position: Optional[Dict] = None
        self.last_trade_time = 0
        
    def run(self):
        """
        Main trading loop
        """
        self.logger.info("Starting trading bot...")
        
        while True:
            try:
                # Check if enough time has passed since last trade
                if time.time() - self.last_trade_time < self.config.get_trading_params()['min_trade_interval']:
                    time.sleep(1)
                    continue
                    
                # Get market data
                market_data = self.market_data.fetch_ohlcv()
                if market_data is None or market_data.empty:
                    self.logger.warning("Failed to fetch market data")
                    time.sleep(5)
                    continue
                    
                # Get current position
                position = self.market_data.get_position()
                
                # If we have an open position, check for exit conditions
                if position and position['size'] != 0:
                    self._handle_existing_position(position, market_data)
                else:
                    # Look for new trading opportunities
                    self._look_for_opportunities(market_data)
                    
                # Sleep for the configured interval
                time.sleep(self.config.get_trading_params()['check_interval'])
                
            except Exception as e:
                self.logger.error(f"Error in main trading loop: {str(e)}")
                time.sleep(5)
                
    def _handle_existing_position(self, position: Dict, market_data: pd.DataFrame):
        """
        Handle existing position (check for exit conditions)
        
        Args:
            position (Dict): Current position information
            market_data (pd.DataFrame): Market data with indicators
        """
        try:
            # Get market analysis
            action, analysis = self.analysis.get_trading_decision(market_data)
            
            # Check if we should close the position
            should_close = False
            
            if position['side'] == 'long' and action == 'short':
                should_close = True
            elif position['side'] == 'short' and action == 'long':
                should_close = True
                
            if should_close and analysis['confidence'] >= 70:
                self.logger.info(f"Closing position based on AI analysis: {analysis['reason']}")
                self.exchange.create_market_order(
                    side='sell' if position['side'] == 'long' else 'buy',
                    amount=abs(position['size'])
                )
                self.current_position = None
                self.last_trade_time = time.time()
                
        except Exception as e:
            self.logger.error(f"Error handling existing position: {str(e)}")
            
    def _look_for_opportunities(self, market_data: pd.DataFrame):
        """
        Look for new trading opportunities
        
        Args:
            market_data (pd.DataFrame): Market data with indicators
        """
        try:
            # Get AI analysis
            action, analysis = self.analysis.get_trading_decision(market_data)
            
            if action == 'none':
                return
                
            # Calculate position size
            position_size = self.exchange.calculate_position_size()
            
            # Create market order
            order = self.exchange.create_market_order(
                side='buy' if action == 'long' else 'sell',
                amount=position_size
            )
            
            if order:
                self.current_position = {
                    'side': action,
                    'size': position_size,
                    'entry_price': order['price']
                }
                self.last_trade_time = time.time()
                
                # Set stop loss and take profit
                self._set_risk_management_orders(order)
                
        except Exception as e:
            self.logger.error(f"Error looking for opportunities: {str(e)}")
            
    def _set_risk_management_orders(self, entry_order: Dict):
        """
        Set stop loss and take profit orders
        
        Args:
            entry_order (Dict): Entry order information
        """
        try:
            risk_params = self.config.get_risk_params()
            entry_price = entry_order['price']
            
            # Calculate stop loss and take profit prices
            if self.current_position['side'] == 'long':
                stop_loss = entry_price * (1 - risk_params['stop_loss_pct'])
                take_profit = entry_price * (1 + risk_params['take_profit_pct'])
            else:
                stop_loss = entry_price * (1 + risk_params['stop_loss_pct'])
                take_profit = entry_price * (1 - risk_params['take_profit_pct'])
                
            # Create stop loss order
            self.exchange.create_stop_loss_order(
                side='sell' if self.current_position['side'] == 'long' else 'buy',
                amount=self.current_position['size'],
                price=stop_loss
            )
            
            # Create take profit order
            self.exchange.create_take_profit_order(
                side='sell' if self.current_position['side'] == 'long' else 'buy',
                amount=self.current_position['size'],
                price=take_profit
            )
            
        except Exception as e:
            self.logger.error(f"Error setting risk management orders: {str(e)}")
            
    def stop(self):
        """
        Stop the trading bot
        """
        self.logger.info("Stopping trading bot...")
        # Cancel all open orders
        self.exchange.cancel_all_orders()
        self.logger.info("Trading bot stopped") 