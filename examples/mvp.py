import time
from datetime import datetime
from src.data.market_data import MarketData
from src.trading.exchange import Exchange
from src.ai.analysis import MarketAnalysis
from src.config import STOP_LOSS_PERCENT, TAKE_PROFIT_PERCENT

def main():
    market_data = MarketData()
    exchange = Exchange()
    analysis = MarketAnalysis()
    
    print("\n=== Bitcoin Trading Bot Started ===")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Trading Pair: BTC/USDT")
    print("Leverage: 5x")
    print("SL/TP: ±0.5%")
    print("===================================\n")
    
    while True:
        try:
            # Get current market data
            current_time = datetime.now().strftime('%H:%M:%S')
            current_price = market_data.get_current_price()
            print(f"\n[{current_time}] Current BTC Price: ${current_price:,.2f}")
            
            # Check current position
            position = market_data.get_position_info()
            if position:
                print(f"Current Position: {position['side'].upper()} {position['amount']} BTC")
                time.sleep(60)
                continue
                
            # Cancel any existing orders
            exchange.cancel_all_orders()
            
            # Get market data for analysis
            df = market_data.fetch_ohlcv()
            
            # Get AI trading decision
            action = analysis.get_trading_decision(df)
            print(f"AI Decision: {action.upper()}")
            
            # Calculate position size
            amount = exchange.calculate_position_size(current_price)
            print(f"Order Amount: {amount} BTC")
            
            # Execute trade
            order = exchange.create_market_order(action, amount)
            entry_price = current_price
            
            # Calculate SL/TP prices
            if action == 'long':
                sl_price = round(entry_price * (1 - STOP_LOSS_PERCENT/100), 2)
                tp_price = round(entry_price * (1 + TAKE_PROFIT_PERCENT/100), 2)
            else:
                sl_price = round(entry_price * (1 + STOP_LOSS_PERCENT/100), 2)
                tp_price = round(entry_price * (1 - TAKE_PROFIT_PERCENT/100), 2)
            
            # Place SL/TP orders
            exchange.create_stop_loss_order(action, amount, sl_price)
            exchange.create_take_profit_order(action, amount, tp_price)
            
            print(f"\n=== {action.upper()} Position Opened ===")
            print(f"Entry: ${entry_price:,.2f}")
            print(f"Stop Loss: ${sl_price:,.2f}")
            print(f"Take Profit: ${tp_price:,.2f}")
            print("============================")
            
            time.sleep(60)
            
        except Exception as e:
            print(f"Error: {str(e)}")
            time.sleep(60)

if __name__ == "__main__":
    main() 