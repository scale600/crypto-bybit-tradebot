from openai import OpenAI
import pandas as pd
from typing import Dict, Tuple
from ..utils.logger import setup_logger
from ..utils.config import Config

class MarketAnalysis:
    """
    Handles AI-based market analysis
    """
    def __init__(self):
        self.config = Config()
        self.logger = setup_logger(__name__, 'ai_analysis')
        self.client = OpenAI()
        self.ai_config = self.config.get_ai_config()
        
    def analyze_market(self, market_data: pd.DataFrame) -> Tuple[str, Dict]:
        """
        Analyze market data using OpenAI GPT-4
        
        Args:
            market_data (pd.DataFrame): DataFrame with market data and indicators
            
        Returns:
            Tuple[str, Dict]: (action, confidence_scores)
        """
        try:
            # Prepare market data summary
            market_summary = self._prepare_market_summary(market_data)
            
            # Get AI analysis
            response = self.client.chat.completions.create(
                model=self.ai_config['model'],
                messages=[
                    {
                        "role": "system",
                        "content": """You are a cryptocurrency trading expert. 
                        Analyze the market data and provide:
                        1. Trading action (only 'long' or 'short')
                        2. Confidence score (0-100)
                        3. Brief reasoning for the decision
                        Format: action|confidence|reason"""
                    },
                    {
                        "role": "user",
                        "content": market_summary
                    }
                ],
                temperature=self.ai_config['temperature']
            )
            
            # Parse response
            result = response.choices[0].message.content.strip().split('|')
            action = result[0].lower()
            confidence = float(result[1])
            reason = result[2]
            
            self.logger.info(f"AI Analysis - Action: {action}, Confidence: {confidence}%, Reason: {reason}")
            
            return action, {
                'confidence': confidence,
                'reason': reason
            }
            
        except Exception as e:
            self.logger.error(f"Error in market analysis: {str(e)}")
            raise
            
    def _prepare_market_summary(self, df: pd.DataFrame) -> str:
        """
        Prepare market data summary for AI analysis
        
        Args:
            df (pd.DataFrame): DataFrame with market data and indicators
            
        Returns:
            str: Formatted market summary
        """
        try:
            # Get latest data point
            latest = df.iloc[-1]
            
            # Calculate price changes
            price_change_1h = ((latest['close'] - df.iloc[-4]['close']) / df.iloc[-4]['close']) * 100
            price_change_4h = ((latest['close'] - df.iloc[-16]['close']) / df.iloc[-16]['close']) * 100
            price_change_24h = ((latest['close'] - df.iloc[-96]['close']) / df.iloc[-96]['close']) * 100
            
            # Prepare summary
            summary = f"""
            Current Market Conditions:
            - Price: ${latest['close']:,.2f}
            - 1h Change: {price_change_1h:.2f}%
            - 4h Change: {price_change_4h:.2f}%
            - 24h Change: {price_change_24h:.2f}%
            
            Technical Indicators:
            - RSI: {latest['rsi']:.2f}
            - MACD: {latest['macd']:.2f}
            - Signal: {latest['signal']:.2f}
            - Bollinger Bands:
              * Upper: ${latest['bollinger_upper']:,.2f}
              * Middle: ${latest['sma']:,.2f}
              * Lower: ${latest['bollinger_lower']:,.2f}
            
            Volume:
            - Current: {latest['volume']:,.2f}
            - Average (24h): {df['volume'].mean():,.2f}
            """
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error preparing market summary: {str(e)}")
            raise
            
    def get_trading_decision(self, market_data: pd.DataFrame) -> Tuple[str, Dict]:
        """
        Get trading decision based on market analysis
        
        Args:
            market_data (pd.DataFrame): DataFrame with market data and indicators
            
        Returns:
            Tuple[str, Dict]: (action, analysis)
        """
        try:
            action, analysis = self.analyze_market(market_data)
            
            if action not in ['long', 'short']:
                raise ValueError(f"Invalid trading action: {action}")
                
            # Apply confidence threshold
            if analysis['confidence'] < 70:
                self.logger.info("Confidence too low, skipping trade")
                return 'none', analysis
                
            return action, analysis
            
        except Exception as e:
            self.logger.error(f"Error getting trading decision: {str(e)}")
            raise 