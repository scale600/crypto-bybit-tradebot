import os
import sys
import time
import pandas as pd
from dotenv import load_dotenv
from src.utils.logger import setup_logger
from src.data.market_data import MarketData
from src.ai.analysis import MarketAnalysis

class PaperTradingBot:
    """
    Paper trading bot for testing strategies without real money
    """
    def __init__(self):
        self.logger = setup_logger('paper_trade', 'paper_trade')
        self.market_data = MarketData()
        self.analysis = MarketAnalysis()
        
        # Initialize paper trading state
        self.balance = 10000  # Initial balance in USDT
        self.position = None
        self.trades = []
        self.last_trade_time = 0
        
    def run(self, duration_hours=24, check_interval=60):
        """
        Run paper trading simulation
        
        Args:
            duration_hours (int): Duration of the simulation in hours
            check_interval (int): Interval between checks in seconds
        """
        self.logger.info(f"Starting paper trading simulation for {duration_hours} hours")
        self.logger.info(f"Initial balance: {self.balance} USDT")
        
        start_time = time.time()
        end_time = start_time + (duration_hours * 3600)
        
        while time.time() < end_time:
            try:
                # Get market data
                market_data = self.market_data.fetch_ohlcv(limit=100)
                if market_data is None or market_data.empty:
                    self.logger.warning("Failed to fetch market data")
                    time.sleep(5)
                    continue
                    
                # Get current price
                current_price = self.market_data.get_current_price()
                if not current_price:
                    self.logger.warning("Failed to get current price")
                    time.sleep(5)
                    continue
                    
                # Check if we have an open position
                if self.position:
                    self._handle_existing_position(current_price, market_data)
                else:
                    # Look for new trading opportunities
                    self._look_for_opportunities(current_price, market_data)
                    
                # Print status
                self._print_status(current_price)
                
                # Sleep for the configured interval
                time.sleep(check_interval)
                
            except Exception as e:
                self.logger.error(f"Error in paper trading loop: {str(e)}")
                time.sleep(5)
                
        # Print final results
        self._print_final_results()
        
    def _handle_existing_position(self, current_price, market_data):
        """
        Handle existing position (check for exit conditions)
        """
        try:
            # Get AI analysis
            action, analysis = self.analysis.get_trading_decision(market_data)
            
            # Check if we should close the position
            should_close = False
            
            if self.position['side'] == 'long' and action == 'short':
                should_close = True
            elif self.position['side'] == 'short' and action == 'long':
                should_close = True
                
            if should_close and analysis['confidence'] >= 70:
                # Calculate P&L
                if self.position['side'] == 'long':
                    pnl = (current_price - self.position['entry_price']) * self.position['size']
                else:
                    pnl = (self.position['entry_price'] - current_price) * self.position['size']
                    
                # Update balance
                self.balance += pnl
                
                # Record trade
                self.trades.append({
                    'type': 'close',
                    'side': self.position['side'],
                    'price': current_price,
                    'size': self.position['size'],
                    'pnl': pnl,
                    'balance': self.balance,
                    'reason': analysis['reason']
                })
                
                self.logger.info(f"Closed {self.position['side']} position at ${current_price:,.2f}, P&L: ${pnl:,.2f}")
                self.position = None
                
        except Exception as e:
            self.logger.error(f"Error handling existing position: {str(e)}")
            
    def _look_for_opportunities(self, current_price, market_data):
        """
        Look for new trading opportunities
        """
        try:
            # Get AI analysis
            action, analysis = self.analysis.get_trading_decision(market_data)
            
            if action == 'none':
                return
                
            # Calculate position size (10% of balance)
            position_size = min(self.balance * 0.1, 1000) / current_price
            
            # Record trade
            self.trades.append({
                'type': 'open',
                'side': action,
                'price': current_price,
                'size': position_size,
                'balance': self.balance,
                'reason': analysis['reason']
            })
            
            self.logger.info(f"Opened {action} position at ${current_price:,.2f}, size: {position_size:.4f}")
            
            # Update position
            self.position = {
                'side': action,
                'size': position_size,
                'entry_price': current_price
            }
            
        except Exception as e:
            self.logger.error(f"Error looking for opportunities: {str(e)}")
            
    def _print_status(self, current_price):
        """
        Print current trading status
        """
        if self.position:
            # Calculate unrealized P&L
            if self.position['side'] == 'long':
                unrealized_pnl = (current_price - self.position['entry_price']) * self.position['size']
            else:
                unrealized_pnl = (self.position['entry_price'] - current_price) * self.position['size']
                
            print(f"\nCurrent Status:")
            print(f"Balance: ${self.balance:,.2f}")
            print(f"Position: {self.position['side']} {self.position['size']:.4f} @ ${self.position['entry_price']:,.2f}")
            print(f"Current Price: ${current_price:,.2f}")
            print(f"Unrealized P&L: ${unrealized_pnl:,.2f}")
        else:
            print(f"\nCurrent Status:")
            print(f"Balance: ${self.balance:,.2f}")
            print(f"Position: None")
            print(f"Current Price: ${current_price:,.2f}")
            
    def _print_final_results(self):
        """
        Print final trading results
        """
        print("\n===== PAPER TRADING RESULTS =====")
        print(f"Initial Balance: $10,000.00")
        print(f"Final Balance: ${self.balance:,.2f}")
        print(f"Total P&L: ${self.balance - 10000:,.2f} ({(self.balance - 10000) / 100:,.2f}%)")
        print(f"Total Trades: {len([t for t in self.trades if t['type'] == 'close'])}")
        
        # Calculate win rate
        winning_trades = len([t for t in self.trades if t['type'] == 'close' and t['pnl'] > 0])
        total_closed_trades = len([t for t in self.trades if t['type'] == 'close'])
        
        if total_closed_trades > 0:
            win_rate = winning_trades / total_closed_trades * 100
            print(f"Win Rate: {win_rate:.2f}%")
            
def main():
    # Load environment variables
    load_dotenv()
    
    # Check for required environment variables
    required_vars = ['OPENAI_API_KEY', 'BINANCE_API_KEY', 'BINANCE_SECRET_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these variables in your .env file")
        sys.exit(1)
        
    # Create and run paper trading bot
    bot = PaperTradingBot()
    bot.run(duration_hours=24, check_interval=60)

if __name__ == "__main__":
    main() 