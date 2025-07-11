from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from enum import Enum
from app.models.base import (
    BaseAnalysisResponse,
    BaseTradingSignal,
    BaseModelConfig,
    validate_positive_number,
    validate_percentage,
)


class RiskRating(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    EXTREME = "EXTREME"


class TradeAnalysisRequest(BaseTradingSignal):
    """Request model for AI trade analysis.

    OPTIMIZATION: Extends BaseTradingSignal to reuse common trading fields.
    """

    strategy: str
    signal_type: str  # Alias for signal field
    market_context: Optional[Dict[str, Any]] = Field(default_factory=dict)


class TradeAnalysisResponse(BaseAnalysisResponse):
    """AI analysis response for a trade signal.

    OPTIMIZATION: Extends BaseAnalysisResponse for common fields.
    """

    signal_strength: float = Field(
        ..., ge=0, le=100, description="Signal strength 0-100"
    )
    risk_reward: float = Field(..., description="Risk/reward ratio")
    market_alignment: str = Field(
        ..., description="How well aligned with market conditions"
    )
    recommendations: List[str] = Field(..., description="Specific recommendations")


class BacktestAnalysisRequest(BaseModel):
    """Request model for backtest analysis"""

    backtest_id: str = Field(..., description="ID of the backtest to analyze")
    include_trade_analysis: bool = Field(
        default=False, description="Include individual trade analysis"
    )


class BacktestAnalysisResponse(BaseAnalysisResponse):
    """AI analysis of backtest results.

    OPTIMIZATION: Extends BaseAnalysisResponse.
    """

    assessment: str = Field(..., description="Overall strategy assessment")
    strengths: List[str] = Field(..., description="Strategy strengths")
    weaknesses: List[str] = Field(..., description="Strategy weaknesses")
    risk_analysis: str = Field(..., description="Risk profile analysis")
    improvements: List[str] = Field(..., description="Suggested improvements")
    market_conditions: Dict[str, str] = Field(
        ..., description="Favorable/unfavorable conditions"
    )
    parameter_suggestions: Dict[str, Any] = Field(
        ..., description="Parameter adjustments"
    )


class MarketCommentaryRequest(BaseModel):
    """Request model for market commentary"""

    symbol: str
    timeframe: str = Field(default="1h", description="Timeframe for analysis")
    include_indicators: List[str] = Field(
        default_factory=list, description="Technical indicators to include"
    )


class MarketCommentaryResponse(BaseAnalysisResponse):
    """AI-generated market commentary.

    OPTIMIZATION: Extends BaseAnalysisResponse, overrides reasoning with commentary.
    """

    symbol: str
    timeframe: str
    commentary: str  # Alias for reasoning
    key_levels: Dict[str, float] = Field(
        default_factory=dict, description="Support/resistance levels"
    )
    sentiment: str = Field(..., description="Market sentiment: bullish/bearish/neutral")

    @property
    def reasoning(self):
        return self.commentary


class RiskAssessmentRequest(BaseModel):
    """Request model for risk assessment"""

    symbol: str
    position_size: float = Field(..., gt=0)
    entry_price: float = Field(..., gt=0)
    stop_loss: float = Field(..., gt=0)
    take_profit: float = Field(..., gt=0)
    account_balance: float = Field(..., gt=0)
    leverage: float = Field(default=1.0, ge=1.0)


class RiskAssessmentResponse(BaseAnalysisResponse):
    """AI risk assessment response.

    OPTIMIZATION: Extends BaseAnalysisResponse.
    """

    position_size_assessment: str
    stop_loss_assessment: str
    take_profit_assessment: str
    risk_rating: RiskRating
    risk_percentage: float = Field(..., description="Percentage of account at risk")
    risk_reward_ratio: float
    recommendations: List[str]
    approved: bool = Field(..., description="Whether the trade meets risk criteria")


class StrategyOptimizationRequest(BaseModel):
    """Request model for strategy optimization"""

    strategy_name: str
    current_parameters: Dict[str, Any]
    performance_window: int = Field(
        default=10, description="Number of recent trades to analyze"
    )


class StrategyOptimizationResponse(BaseAnalysisResponse):
    """AI strategy optimization suggestions.

    OPTIMIZATION: Extends BaseAnalysisResponse - saves 3 duplicate fields.
    """

    pattern_analysis: str = Field(..., description="Patterns found in performance")
    suggested_parameters: Dict[str, Any] = Field(
        ..., description="Optimized parameters"
    )
    expected_improvement_percent: float = Field(
        ..., description="Expected performance improvement"
    )

    # Map confidence_level to base confidence field
    @property
    def confidence_level(self):
        return self.confidence
