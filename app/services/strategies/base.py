from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from datetime import datetime
import pandas as pd
from enum import Enum
from app.core.logger import LoggerMixin
from app.models.base import BaseTradingSignal


class SignalDirection(str, Enum):
    LONG = "long"
    SHORT = "short"
    NEUTRAL = "neutral"


@dataclass
class TradingSignal:
    """Represents a trading signal from a strategy.
    
    OPTIMIZATION: Consider migrating to use BaseTradingSignal from models.base
    to reduce duplication. Keeping for now to avoid breaking changes.
    """
    timestamp: datetime
    symbol: str
    direction: SignalDirection
    strength: float  # 0.0 to 1.0
    entry_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_base_signal(self) -> Dict[str, Any]:
        """Convert to BaseTradingSignal compatible format."""
        return {
            'symbol': self.symbol,
            'signal': 'buy' if self.direction == SignalDirection.LONG else 'sell',
            'price': self.entry_price,
            'quantity': None,  # To be determined by position sizing
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit
        }


@dataclass
class StrategyParameters:
    """Base parameters that all strategies should have"""
    symbol: str
    timeframe: str  # e.g., "1h", "4h", "1d"
    lookback_period: int  # Number of candles to look back


class BaseStrategy(ABC, LoggerMixin):
    """Abstract base class for all trading strategies"""
    
    def __init__(self, parameters: StrategyParameters):
        self.parameters = parameters
        self.name = self.__class__.__name__
        self._is_initialized = False
        
    @abstractmethod
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate strategy-specific indicators
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            DataFrame with indicators added
        """
        pass
    
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> Optional[TradingSignal]:
        """
        Generate trading signals based on indicators
        
        Args:
            data: DataFrame with OHLCV data and indicators
            
        Returns:
            TradingSignal if conditions are met, None otherwise
        """
        pass
    
    @abstractmethod
    def get_required_lookback(self) -> int:
        """
        Get the minimum number of candles required for the strategy
        
        Returns:
            Number of candles needed
        """
        pass
    
    def validate_data(self, data: pd.DataFrame) -> Tuple[bool, Optional[str]]:
        """
        Validate that the data has required columns and enough history
        
        Args:
            data: DataFrame to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        
        # Check for required columns
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            return False, f"Missing required columns: {missing_columns}"
        
        # Check for enough data
        required_lookback = self.get_required_lookback()
        if len(data) < required_lookback:
            return False, f"Insufficient data: need {required_lookback} candles, got {len(data)}"
        
        # Check for NaN values
        if data[required_columns].isnull().any().any():
            return False, "Data contains NaN values"
        
        return True, None
    
    def calculate_position_size(
        self,
        signal: TradingSignal,
        account_balance: float,
        risk_per_trade: float = 0.02
    ) -> float:
        """
        Calculate position size based on risk management rules
        
        Args:
            signal: Trading signal with entry and stop loss
            account_balance: Current account balance
            risk_per_trade: Percentage of account to risk per trade
            
        Returns:
            Position size
        """
        if not signal.stop_loss or not signal.entry_price:
            # Use default 1% stop loss if not provided
            risk_amount = account_balance * risk_per_trade
            return risk_amount / (signal.entry_price * 0.01)
        
        # Calculate position size based on stop loss
        risk_amount = account_balance * risk_per_trade
        stop_loss_pct = abs(signal.entry_price - signal.stop_loss) / signal.entry_price
        
        position_size = risk_amount / (signal.entry_price * stop_loss_pct)
        
        return position_size
    
    def backtest(
        self,
        data: pd.DataFrame,
        initial_capital: float = 100000,
        commission: float = 0.001
    ) -> Dict[str, Any]:
        """
        Run a simple backtest of the strategy
        
        Args:
            data: Historical OHLCV data
            initial_capital: Starting capital
            commission: Commission rate per trade
            
        Returns:
            Dictionary with backtest results
        """
        # Validate data
        is_valid, error_msg = self.validate_data(data)
        if not is_valid:
            raise ValueError(f"Data validation failed: {error_msg}")
        
        # Calculate indicators
        data = self.calculate_indicators(data)
        
        # Initialize backtest variables
        positions = []
        trades = []
        capital = initial_capital
        position = None
        
        # Generate signals for each candle
        for i in range(self.get_required_lookback(), len(data)):
            current_data = data.iloc[:i+1]
            signal = self.generate_signals(current_data)
            
            if signal:
                current_price = data.iloc[i]['close']
                
                # Handle signal
                if signal.direction == SignalDirection.LONG and position is None:
                    # Open long position
                    position_size = self.calculate_position_size(signal, capital)
                    cost = position_size * current_price * (1 + commission)
                    
                    if cost <= capital:
                        position = {
                            'entry_time': data.index[i],
                            'entry_price': current_price,
                            'size': position_size,
                            'direction': 'long',
                            'stop_loss': signal.stop_loss,
                            'take_profit': signal.take_profit
                        }
                        capital -= cost
                        
                elif signal.direction == SignalDirection.NEUTRAL and position:
                    # Close position
                    exit_price = current_price
                    pnl = position['size'] * (exit_price - position['entry_price'])
                    proceeds = position['size'] * exit_price * (1 - commission)
                    capital += proceeds
                    
                    trades.append({
                        'entry_time': position['entry_time'],
                        'exit_time': data.index[i],
                        'entry_price': position['entry_price'],
                        'exit_price': exit_price,
                        'size': position['size'],
                        'pnl': pnl,
                        'return': pnl / (position['size'] * position['entry_price'])
                    })
                    
                    position = None
        
        # Calculate metrics
        total_trades = len(trades)
        winning_trades = len([t for t in trades if t['pnl'] > 0])
        losing_trades = len([t for t in trades if t['pnl'] < 0])
        
        if total_trades > 0:
            win_rate = winning_trades / total_trades
            avg_return = sum(t['return'] for t in trades) / total_trades
            total_return = (capital - initial_capital) / initial_capital
        else:
            win_rate = 0
            avg_return = 0
            total_return = 0
        
        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'avg_return_per_trade': avg_return,
            'total_return': total_return,
            'final_capital': capital,
            'trades': trades
        }