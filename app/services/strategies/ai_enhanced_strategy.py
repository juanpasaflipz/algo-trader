from typing import Optional, Dict, Any
import pandas as pd
from dataclasses import dataclass
from app.services.strategies.base import (
    BaseStrategy,
    StrategyParameters,
    TradingSignal,
    SignalDirection,
)
from app.services.strategies.ema_crossover import (
    EMACrossoverStrategy,
    EMACrossoverParameters,
)
from app.services.ai_service import get_ai_service, AIAnalysisError
from app.models.tradingview import TradingViewAlert
from app.core.logger import get_logger

logger = get_logger(__name__)


@dataclass
class AIEnhancedStrategyParameters(StrategyParameters):
    """Parameters for AI-enhanced strategy wrapper"""

    base_strategy: str = "EMA_CROSSOVER"  # Base strategy to enhance
    base_strategy_params: Dict[str, Any] = None
    ai_confidence_threshold: float = 70.0  # Minimum AI confidence to accept signal
    use_ai_risk_assessment: bool = True
    use_ai_market_context: bool = True
    ai_weight: float = 0.5  # Weight of AI analysis vs base strategy (0-1)


class AIEnhancedStrategy(BaseStrategy):
    """
    AI-Enhanced Trading Strategy

    This strategy wraps any base strategy and enhances it with Claude's analysis:
    - Validates signals with AI before execution
    - Adjusts position sizing based on AI risk assessment
    - Incorporates market context analysis
    - Can override or modify base strategy signals
    """

    def __init__(self, parameters: AIEnhancedStrategyParameters):
        super().__init__(parameters)
        self.params: AIEnhancedStrategyParameters = parameters

        # Initialize base strategy
        if self.params.base_strategy == "EMA_CROSSOVER":
            base_params = EMACrossoverParameters(
                symbol=parameters.symbol,
                timeframe=parameters.timeframe,
                lookback_period=parameters.lookback_period,
                **(parameters.base_strategy_params or {}),
            )
            self.base_strategy = EMACrossoverStrategy(base_params)
        else:
            raise ValueError(f"Unknown base strategy: {self.params.base_strategy}")

        # Initialize AI service
        try:
            self.ai_service = get_ai_service()
            self.ai_enabled = self.ai_service is not None
        except Exception as e:
            logger.warning(f"AI service not available: {e}")
            self.ai_enabled = False

    def get_required_lookback(self) -> int:
        """Use base strategy's lookback requirement"""
        return self.base_strategy.get_required_lookback()

    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate base strategy indicators plus AI-specific ones"""
        # Calculate base strategy indicators
        data = self.base_strategy.calculate_indicators(data)

        # Add AI-specific indicators
        if self.ai_enabled and self.params.use_ai_market_context:
            # Calculate volatility for AI context
            data["volatility"] = data["close"].pct_change().rolling(20).std()
            data["volume_trend"] = data["volume"].rolling(20).mean()

        return data

    async def generate_signals_async(
        self, data: pd.DataFrame
    ) -> Optional[TradingSignal]:
        """Async version for AI-enhanced signal generation"""
        # Get base strategy signal
        base_signal = self.base_strategy.generate_signals(data)

        if not base_signal:
            return None

        if not self.ai_enabled:
            logger.warning("AI not enabled, using base strategy signal only")
            return base_signal

        try:
            # Prepare market context
            market_context = self._prepare_market_context(data)

            # Create alert for AI analysis
            alert = TradingViewAlert(
                strategy=self.params.base_strategy,
                symbol=self.params.symbol,
                signal=self._convert_signal_direction(base_signal.direction),
                price=base_signal.entry_price,
                stop_loss=base_signal.stop_loss,
                take_profit=base_signal.take_profit,
            )

            # Get AI analysis
            ai_analysis = await self.ai_service.analyze_trade_signal(
                alert, market_context
            )

            # Check AI confidence
            ai_confidence = ai_analysis.get("confidence", 0)
            if ai_confidence < self.params.ai_confidence_threshold:
                logger.info(
                    f"AI confidence too low: {ai_confidence}% < {self.params.ai_confidence_threshold}%",
                    symbol=self.params.symbol,
                )
                return None

            # Enhance signal with AI insights
            enhanced_signal = self._enhance_signal_with_ai(base_signal, ai_analysis)

            return enhanced_signal

        except AIAnalysisError as e:
            logger.error(f"AI analysis failed: {e}")
            # Fall back to base strategy if AI fails
            return base_signal if self.params.ai_weight < 0.5 else None

    def generate_signals(self, data: pd.DataFrame) -> Optional[TradingSignal]:
        """Synchronous wrapper for compatibility"""
        # For now, we'll use base strategy only in sync mode
        # In production, you'd want to handle async properly
        base_signal = self.base_strategy.generate_signals(data)

        if not base_signal or not self.ai_enabled:
            return base_signal

        # Apply basic AI confidence adjustment
        # In production, this should be async
        base_signal.strength *= (
            1 - self.params.ai_weight
        ) + self.params.ai_weight * 0.8

        return base_signal

    def _prepare_market_context(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Prepare market context for AI analysis"""
        last_row = data.iloc[-1]

        context = {
            "current_price": float(last_row["close"]),
            "24h_high": float(data["high"].tail(24).max()),
            "24h_low": float(data["low"].tail(24).min()),
            "24h_volume": float(data["volume"].tail(24).sum()),
            "volatility": float(last_row.get("volatility", 0)),
            "trend": self._determine_trend(data),
            "support_levels": self._find_support_resistance(data, "support"),
            "resistance_levels": self._find_support_resistance(data, "resistance"),
        }

        # Add base strategy indicators
        if "ema_fast" in data.columns:
            context["ema_fast"] = float(last_row["ema_fast"])
            context["ema_slow"] = float(last_row["ema_slow"])

        return context

    def _determine_trend(self, data: pd.DataFrame) -> str:
        """Determine market trend"""
        sma_20 = data["close"].rolling(20).mean()
        sma_50 = data["close"].rolling(50).mean()

        if len(sma_20) < 50:
            return "insufficient_data"

        current_price = data["close"].iloc[-1]

        if current_price > sma_20.iloc[-1] > sma_50.iloc[-1]:
            return "strong_uptrend"
        elif current_price > sma_20.iloc[-1]:
            return "uptrend"
        elif current_price < sma_20.iloc[-1] < sma_50.iloc[-1]:
            return "strong_downtrend"
        elif current_price < sma_20.iloc[-1]:
            return "downtrend"
        else:
            return "sideways"

    def _find_support_resistance(self, data: pd.DataFrame, level_type: str) -> list:
        """Find support or resistance levels"""
        # Simple implementation - find recent highs/lows
        if level_type == "support":
            levels = data["low"].tail(50).nsmallest(3).tolist()
        else:
            levels = data["high"].tail(50).nlargest(3).tolist()

        return [float(level) for level in levels]

    def _convert_signal_direction(self, direction: SignalDirection) -> str:
        """Convert strategy signal direction to TradingView format"""
        if direction == SignalDirection.LONG:
            return "buy"
        elif direction == SignalDirection.SHORT:
            return "sell"
        else:
            return "close"

    def _enhance_signal_with_ai(
        self, base_signal: TradingSignal, ai_analysis: Dict[str, Any]
    ) -> TradingSignal:
        """Enhance base signal with AI insights"""
        # Adjust signal strength based on AI confidence
        ai_confidence = ai_analysis.get("confidence", 50) / 100
        base_weight = 1 - self.params.ai_weight
        ai_weight = self.params.ai_weight

        enhanced_strength = (
            base_signal.strength * base_weight
            + ai_analysis.get("signal_strength", 50) / 100 * ai_weight
        )

        # Update signal
        base_signal.strength = min(enhanced_strength, 1.0)

        # Add AI insights to metadata
        if not base_signal.metadata:
            base_signal.metadata = {}

        base_signal.metadata.update(
            {
                "ai_confidence": ai_analysis.get("confidence"),
                "ai_signal_strength": ai_analysis.get("signal_strength"),
                "ai_risk_reward": ai_analysis.get("risk_reward"),
                "ai_recommendations": ai_analysis.get("recommendations", []),
                "ai_market_alignment": ai_analysis.get("market_alignment"),
            }
        )

        # Adjust stop loss/take profit based on AI recommendations
        recommendations = ai_analysis.get("recommendations", [])
        for rec in recommendations:
            if "tighten stop loss" in rec.lower() and base_signal.stop_loss:
                # Tighten stop loss by 10%
                if base_signal.direction == SignalDirection.LONG:
                    base_signal.stop_loss = base_signal.entry_price - (
                        (base_signal.entry_price - base_signal.stop_loss) * 0.9
                    )
            elif "widen take profit" in rec.lower() and base_signal.take_profit:
                # Widen take profit by 20%
                if base_signal.direction == SignalDirection.LONG:
                    base_signal.take_profit = base_signal.entry_price + (
                        (base_signal.take_profit - base_signal.entry_price) * 1.2
                    )

        return base_signal
