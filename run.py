import signal
import sys
from src.bot import TradingBot
from src.utils.logger import setup_logger

def main():
    # Setup logger
    logger = setup_logger('main', 'main')
    
    # Create bot instance
    bot = TradingBot()
    
    # Handle graceful shutdown
    def signal_handler(signum, frame):
        logger.info("Received shutdown signal")
        bot.stop()
        sys.exit(0)
        
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start the bot
    try:
        logger.info("Starting trading bot...")
        bot.run()
    except Exception as e:
        logger.error(f"Error running bot: {str(e)}")
        bot.stop()
        sys.exit(1)

if __name__ == "__main__":
    main() 