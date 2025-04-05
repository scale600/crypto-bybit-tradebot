import os
import sys
import time
from dotenv import load_dotenv
from src.utils.logger import setup_logger
from src.data.market_data import MarketData
from src.ai.analysis import MarketAnalysis

def test_market_data():
    """Test market data functionality"""
    logger = setup_logger('test', 'test')
    logger.info("Testing market data functionality...")
    
    try:
        # Initialize market data
        market_data = MarketData()
        
        # Test fetching OHLCV data
        df = market_data.fetch_ohlcv(limit=10)
        if df is not None and not df.empty:
            logger.info(f"Successfully fetched {len(df)} candles")
            logger.info(f"Latest price: ${df['close'].iloc[-1]:,.2f}")
            logger.info(f"RSI: {df['rsi'].iloc[-1]:.2f}")
        else:
            logger.error("Failed to fetch OHLCV data")
            
        # Test getting current price
        price = market_data.get_current_price()
        if price:
            logger.info(f"Current price: ${price:,.2f}")
        else:
            logger.error("Failed to get current price")
            
        # Test getting position
        position = market_data.get_position()
        if position:
            logger.info(f"Current position: {position}")
        else:
            logger.info("No open position")
            
        return True
        
    except Exception as e:
        logger.error(f"Error testing market data: {str(e)}")
        return False

def test_ai_analysis():
    """Test AI analysis functionality"""
    logger = setup_logger('test', 'test')
    logger.info("Testing AI analysis functionality...")
    
    try:
        # Initialize market data and analysis
        market_data = MarketData()
        analysis = MarketAnalysis()
        
        # Get market data
        df = market_data.fetch_ohlcv(limit=100)
        if df is None or df.empty:
            logger.error("Failed to fetch market data for analysis")
            return False
            
        # Test AI analysis
        action, result = analysis.analyze_market(df)
        logger.info(f"AI Analysis - Action: {action}, Confidence: {result['confidence']}%, Reason: {result['reason']}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error testing AI analysis: {str(e)}")
        return False

def main():
    """Run tests"""
    # Load environment variables
    load_dotenv()
    
    # Check for required environment variables
    required_vars = ['OPENAI_API_KEY', 'BINANCE_API_KEY', 'BINANCE_SECRET_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these variables in your .env file")
        sys.exit(1)
        
    # Run tests
    print("Running tests...")
    
    # Test market data
    market_data_success = test_market_data()
    print(f"Market data test: {'Success' if market_data_success else 'Failed'}")
    
    # Test AI analysis
    ai_analysis_success = test_ai_analysis()
    print(f"AI analysis test: {'Success' if ai_analysis_success else 'Failed'}")
    
    # Summary
    if market_data_success and ai_analysis_success:
        print("\nAll tests passed! The bot is ready to run.")
    else:
        print("\nSome tests failed. Please check the logs for details.")

if __name__ == "__main__":
    main() 