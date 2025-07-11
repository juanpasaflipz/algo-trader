"""User profiling and risk assessment endpoints."""
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from app.core.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


class RiskQuestionnaireResponse(BaseModel):
    """Individual response to a risk questionnaire question"""
    question_id: str
    answer: str
    score: int = Field(..., ge=0, le=10)


class RiskQuestionnaire(BaseModel):
    """Complete risk questionnaire submission"""
    responses: List[RiskQuestionnaireResponse]
    
    
class RiskProfile(BaseModel):
    """User's risk profile based on questionnaire"""
    profile_id: str
    risk_score: float = Field(..., ge=0, le=100)
    risk_category: str  # "conservative", "moderate", "aggressive"
    investment_horizon: str  # "short", "medium", "long"
    max_drawdown_tolerance: float  # percentage
    preferred_assets: List[str]
    created_at: datetime
    
    
class TradingPreferences(BaseModel):
    """User's trading preferences"""
    preferred_timeframe: str  # "1m", "5m", "1h", "1d", etc.
    max_position_size: float  # percentage of portfolio
    max_concurrent_positions: int
    stop_loss_percentage: float
    take_profit_percentage: float
    use_trailing_stop: bool = False
    
    
class StrategyRecommendation(BaseModel):
    """Recommended strategy based on profile"""
    strategy_name: str
    match_score: float = Field(..., ge=0, le=100)
    reasoning: str
    expected_return: float
    expected_risk: float
    recommended_parameters: Dict[str, Any]


# Mock database
user_profiles: Dict[str, RiskProfile] = {}
user_preferences: Dict[str, TradingPreferences] = {}


@router.post("/profile/risk-assessment", response_model=RiskProfile)
async def submit_risk_assessment(questionnaire: RiskQuestionnaire) -> RiskProfile:
    """
    Submit risk assessment questionnaire and get risk profile
    
    Questions evaluate:
    - Risk tolerance
    - Investment experience
    - Financial goals
    - Time horizon
    - Loss aversion
    """
    # Calculate risk score from responses
    total_score = sum(r.score for r in questionnaire.responses)
    max_score = len(questionnaire.responses) * 10
    risk_score = (total_score / max_score) * 100
    
    # Determine risk category
    if risk_score < 33:
        risk_category = "conservative"
        max_drawdown = 0.1  # 10%
        preferred_assets = ["USDT", "USDC", "BTC"]
    elif risk_score < 66:
        risk_category = "moderate"
        max_drawdown = 0.2  # 20%
        preferred_assets = ["BTC", "ETH", "BNB", "SOL"]
    else:
        risk_category = "aggressive"
        max_drawdown = 0.3  # 30%
        preferred_assets = ["BTC", "ETH", "ALT", "DeFi"]
    
    # Determine investment horizon based on specific questions
    # (This is simplified - in production, map specific questions)
    investment_horizon = "medium"
    
    profile = RiskProfile(
        profile_id=f"profile_{datetime.utcnow().timestamp()}",
        risk_score=risk_score,
        risk_category=risk_category,
        investment_horizon=investment_horizon,
        max_drawdown_tolerance=max_drawdown,
        preferred_assets=preferred_assets,
        created_at=datetime.utcnow()
    )
    
    # Store profile (in production, associate with user)
    user_profiles[profile.profile_id] = profile
    
    logger.info(
        "Risk profile created",
        profile_id=profile.profile_id,
        risk_category=risk_category,
        risk_score=risk_score
    )
    
    return profile


@router.put("/profile/preferences", response_model=TradingPreferences)
async def update_trading_preferences(preferences: TradingPreferences) -> TradingPreferences:
    """
    Update user's trading preferences
    
    These preferences control:
    - Position sizing
    - Risk management rules
    - Trading timeframes
    """
    # Validate preferences
    if preferences.max_position_size > 0.5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum position size cannot exceed 50% of portfolio"
        )
    
    if preferences.stop_loss_percentage < 0.01:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stop loss must be at least 1%"
        )
    
    # Store preferences (in production, associate with user)
    user_id = "current_user"  # Mock user ID
    user_preferences[user_id] = preferences
    
    logger.info("Trading preferences updated", user_id=user_id)
    
    return preferences


@router.get("/profile/preferences", response_model=TradingPreferences)
async def get_trading_preferences() -> TradingPreferences:
    """Get current user's trading preferences"""
    user_id = "current_user"  # Mock user ID
    
    if user_id not in user_preferences:
        # Return default preferences
        return TradingPreferences(
            preferred_timeframe="1h",
            max_position_size=0.1,
            max_concurrent_positions=3,
            stop_loss_percentage=0.02,
            take_profit_percentage=0.05,
            use_trailing_stop=False
        )
    
    return user_preferences[user_id]


@router.get("/profile/strategy-recommendations", response_model=List[StrategyRecommendation])
async def get_strategy_recommendations(
    profile_id: Optional[str] = None
) -> List[StrategyRecommendation]:
    """
    Get personalized strategy recommendations based on risk profile
    
    Matches strategies to user's:
    - Risk tolerance
    - Investment horizon
    - Preferred assets
    - Trading experience
    """
    # Get user's risk profile
    if profile_id and profile_id in user_profiles:
        profile = user_profiles[profile_id]
    else:
        # Use a default moderate profile
        profile = RiskProfile(
            profile_id="default",
            risk_score=50,
            risk_category="moderate",
            investment_horizon="medium",
            max_drawdown_tolerance=0.2,
            preferred_assets=["BTC", "ETH"],
            created_at=datetime.utcnow()
        )
    
    recommendations = []
    
    # Conservative profile recommendations
    if profile.risk_category == "conservative":
        recommendations.extend([
            StrategyRecommendation(
                strategy_name="EMA_CROSSOVER",
                match_score=85,
                reasoning="Low-risk trend following strategy suitable for conservative traders",
                expected_return=0.15,  # 15% annual
                expected_risk=0.08,    # 8% volatility
                recommended_parameters={
                    "fast_ema": 20,
                    "slow_ema": 50,
                    "position_size": 0.05,
                    "stop_loss": 0.02
                }
            ),
            StrategyRecommendation(
                strategy_name="RSI_MEAN_REVERSION",
                match_score=75,
                reasoning="Mean reversion with tight risk controls",
                expected_return=0.12,
                expected_risk=0.06,
                recommended_parameters={
                    "rsi_period": 14,
                    "oversold": 30,
                    "overbought": 70,
                    "position_size": 0.03
                }
            )
        ])
    
    # Moderate profile recommendations
    elif profile.risk_category == "moderate":
        recommendations.extend([
            StrategyRecommendation(
                strategy_name="MACD_MOMENTUM",
                match_score=90,
                reasoning="Balanced momentum strategy for medium-term trends",
                expected_return=0.25,
                expected_risk=0.15,
                recommended_parameters={
                    "fast_period": 12,
                    "slow_period": 26,
                    "signal_period": 9,
                    "position_size": 0.1
                }
            ),
            StrategyRecommendation(
                strategy_name="BREAKOUT_STRATEGY",
                match_score=80,
                reasoning="Captures strong moves with defined risk",
                expected_return=0.30,
                expected_risk=0.18,
                recommended_parameters={
                    "lookback_period": 20,
                    "breakout_threshold": 1.02,
                    "position_size": 0.08
                }
            )
        ])
    
    # Aggressive profile recommendations
    else:
        recommendations.extend([
            StrategyRecommendation(
                strategy_name="SCALPING_STRATEGY",
                match_score=95,
                reasoning="High-frequency trading for experienced traders",
                expected_return=0.50,
                expected_risk=0.30,
                recommended_parameters={
                    "timeframe": "1m",
                    "position_size": 0.15,
                    "max_positions": 5,
                    "quick_exit": True
                }
            ),
            StrategyRecommendation(
                strategy_name="GRID_TRADING",
                match_score=85,
                reasoning="Capitalize on volatility with grid positions",
                expected_return=0.40,
                expected_risk=0.25,
                recommended_parameters={
                    "grid_levels": 10,
                    "grid_spacing": 0.01,
                    "position_size": 0.2
                }
            )
        ])
    
    # Sort by match score
    recommendations.sort(key=lambda x: x.match_score, reverse=True)
    
    return recommendations


@router.get("/profile/risk-profile/{profile_id}", response_model=RiskProfile)
async def get_risk_profile(profile_id: str) -> RiskProfile:
    """Get a specific risk profile by ID"""
    if profile_id not in user_profiles:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Risk profile {profile_id} not found"
        )
    
    return user_profiles[profile_id]