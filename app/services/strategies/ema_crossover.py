from typing import Optional
import pandas as pd
import numpy as np
from dataclasses import dataclass
from app.services.strategies.base import (
    BaseStrategy,
    StrategyParameters,
    TradingSignal,
    SignalDirection
)


@dataclass
class EMACrossoverParameters(StrategyParameters):
    """Parameters specific to EMA Crossover strategy"""
    fast_ema_period: int = 12
    slow_ema_period: int = 26
    signal_ema_period: int = 9  # For MACD-like signal smoothing
    use_volume_filter: bool = True
    volume_threshold: float = 1.5  # Volume must be X times average


class EMACrossoverStrategy(BaseStrategy):
    """
    Exponential Moving Average (EMA) Crossover Strategy
    
    Generates signals based on:
    - Fast EMA crossing above Slow EMA = BUY
    - Fast EMA crossing below Slow EMA = SELL
    - Optional volume filter for confirmation
    """
    
    def __init__(self, parameters: EMACrossoverParameters):
        super().__init__(parameters)
        self.params: EMACrossoverParameters = parameters
        
    def get_required_lookback(self) -> int:
        """Return the number of candles needed for calculations"""
        return self.params.slow_ema_period + self.params.signal_ema_period
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate EMAs and related indicators"""
        df = data.copy()
        
        # Calculate EMAs
        df['ema_fast'] = df['close'].ewm(
            span=self.params.fast_ema_period,
            adjust=False
        ).mean()
        
        df['ema_slow'] = df['close'].ewm(
            span=self.params.slow_ema_period,
            adjust=False
        ).mean()
        
        # Calculate MACD-like indicators
        df['ema_diff'] = df['ema_fast'] - df['ema_slow']
        df['signal_line'] = df['ema_diff'].ewm(
            span=self.params.signal_ema_period,
            adjust=False
        ).mean()
        
        # Calculate crossover signals
        df['crossover'] = 0
        df.loc[df['ema_diff'] > df['signal_line'], 'crossover'] = 1
        df.loc[df['ema_diff'] < df['signal_line'], 'crossover'] = -1
        
        # Detect actual crossover points
        df['signal'] = df['crossover'].diff()
        
        # Volume analysis
        if self.params.use_volume_filter:
            df['volume_sma'] = df['volume'].rolling(
                window=20,
                min_periods=1
            ).mean()
            df['volume_ratio'] = df['volume'] / df['volume_sma']
        
        return df
    
    def generate_signals(self, data: pd.DataFrame) -> Optional[TradingSignal]:
        """Generate trading signal based on current data"""
        # Calculate indicators if not already done
        if 'ema_fast' not in data.columns:
            data = self.calculate_indicators(data)
        
        # Get the last row
        last_row = data.iloc[-1]
        prev_row = data.iloc[-2] if len(data) > 1 else None
        
        # Check for crossover signal
        signal_value = last_row['signal']
        
        # No signal if no crossover
        if pd.isna(signal_value) or signal_value == 0:
            return None
        
        # Apply volume filter if enabled
        if self.params.use_volume_filter:
            if last_row['volume_ratio'] < self.params.volume_threshold:
                self.log_event(
                    "Signal filtered due to low volume",
                    symbol=self.params.symbol,
                    volume_ratio=last_row['volume_ratio']
                )
                return None
        
        # Determine signal direction
        if signal_value > 0:  # Bullish crossover
            direction = SignalDirection.LONG
            strength = min(abs(signal_value), 1.0)
            
            # Calculate stop loss and take profit
            atr = self._calculate_atr(data, period=14)
            stop_loss = last_row['close'] - (2 * atr)
            take_profit = last_row['close'] + (3 * atr)
            
        elif signal_value < 0:  # Bearish crossover
            direction = SignalDirection.SHORT
            strength = min(abs(signal_value), 1.0)
            
            # Calculate stop loss and take profit
            atr = self._calculate_atr(data, period=14)
            stop_loss = last_row['close'] + (2 * atr)
            take_profit = last_row['close'] - (3 * atr)
            
        else:
            return None
        
        # Create trading signal
        signal = TradingSignal(
            timestamp=last_row.name if hasattr(last_row, 'name') else pd.Timestamp.now(),
            symbol=self.params.symbol,
            direction=direction,
            strength=strength,
            entry_price=last_row['close'],
            stop_loss=stop_loss,
            take_profit=take_profit,
            metadata={
                'strategy': self.name,
                'ema_fast': last_row['ema_fast'],
                'ema_slow': last_row['ema_slow'],
                'ema_diff': last_row['ema_diff'],
                'volume_ratio': last_row.get('volume_ratio', 1.0)
            }
        )
        
        self.log_event(
            "Signal generated",
            signal=signal.direction.value,
            symbol=signal.symbol,
            strength=signal.strength
        )
        
        return signal
    
    def _calculate_atr(self, data: pd.DataFrame, period: int = 14) -> float:
        """Calculate Average True Range for stop loss/take profit"""
        high = data['high']
        low = data['low']
        close = data['close']
        
        # Calculate True Range
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        # Calculate ATR
        atr = tr.rolling(window=period, min_periods=1).mean()
        
        return atr.iloc[-1] if not pd.isna(atr.iloc[-1]) else (high.iloc[-1] - low.iloc[-1])