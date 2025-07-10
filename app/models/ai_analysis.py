from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from enum import Enum


class RiskRating(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    EXTREME = "EXTREME"


class TradeAnalysisRequest(BaseModel):
    """Request model for AI trade analysis"""
    symbol: str
    strategy: str
    signal_type: str
    price: float
    quantity: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    market_context: Optional[Dict[str, Any]] = Field(default_factory=dict)


class TradeAnalysisResponse(BaseModel):
    """AI analysis response for a trade signal"""
    signal_strength: float = Field(..., ge=0, le=100, description="Signal strength 0-100")
    risk_reward: float = Field(..., description="Risk/reward ratio")
    market_alignment: str = Field(..., description="How well aligned with market conditions")
    recommendations: List[str] = Field(..., description="Specific recommendations")
    confidence: float = Field(..., ge=0, le=100, description="AI confidence level")
    reasoning: str = Field(..., description="Detailed reasoning")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class BacktestAnalysisRequest(BaseModel):
    """Request model for backtest analysis"""
    backtest_id: str = Field(..., description="ID of the backtest to analyze")
    include_trade_analysis: bool = Field(default=False, description="Include individual trade analysis")


class BacktestAnalysisResponse(BaseModel):
    """AI analysis of backtest results"""
    assessment: str = Field(..., description="Overall strategy assessment")
    strengths: List[str] = Field(..., description="Strategy strengths")
    weaknesses: List[str] = Field(..., description="Strategy weaknesses")
    risk_analysis: str = Field(..., description="Risk profile analysis")
    improvements: List[str] = Field(..., description="Suggested improvements")
    market_conditions: Dict[str, str] = Field(..., description="Favorable/unfavorable conditions")
    parameter_suggestions: Dict[str, Any] = Field(..., description="Parameter adjustments")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class MarketCommentaryRequest(BaseModel):
    """Request model for market commentary"""
    symbol: str
    timeframe: str = Field(default="1h", description="Timeframe for analysis")
    include_indicators: List[str] = Field(default_factory=list, description="Technical indicators to include")


class MarketCommentaryResponse(BaseModel):
    """AI-generated market commentary"""
    symbol: str
    timeframe: str
    commentary: str
    key_levels: Dict[str, float] = Field(default_factory=dict, description="Support/resistance levels")
    sentiment: str = Field(..., description="Market sentiment: bullish/bearish/neutral")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class RiskAssessmentRequest(BaseModel):
    """Request model for risk assessment"""
    symbol: str
    position_size: float = Field(..., gt=0)
    entry_price: float = Field(..., gt=0)
    stop_loss: float = Field(..., gt=0)
    take_profit: float = Field(..., gt=0)
    account_balance: float = Field(..., gt=0)
    leverage: float = Field(default=1.0, ge=1.0)


class RiskAssessmentResponse(BaseModel):
    """AI risk assessment response"""
    position_size_assessment: str
    stop_loss_assessment: str
    take_profit_assessment: str
    risk_rating: RiskRating
    risk_percentage: float = Field(..., description="Percentage of account at risk")
    risk_reward_ratio: float
    recommendations: List[str]
    approved: bool = Field(..., description="Whether the trade meets risk criteria")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class StrategyOptimizationRequest(BaseModel):
    """Request model for strategy optimization"""
    strategy_name: str
    current_parameters: Dict[str, Any]
    performance_window: int = Field(default=10, description="Number of recent trades to analyze")


class StrategyOptimizationResponse(BaseModel):
    """AI strategy optimization suggestions"""
    pattern_analysis: str = Field(..., description="Patterns found in performance")
    suggested_parameters: Dict[str, Any] = Field(..., description="Optimized parameters")
    reasoning: str = Field(..., description="Explanation of changes")
    expected_improvement_percent: float = Field(..., description="Expected performance improvement")
    confidence_level: float = Field(..., ge=0, le=100)
    timestamp: datetime = Field(default_factory=datetime.utcnow)