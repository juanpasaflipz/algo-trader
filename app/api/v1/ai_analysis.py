from fastapi import APIRouter, HTTPException, status, Depends
from typing import Dict, Any
from app.core.logger import get_logger
from app.core.config import settings
from app.models.ai_analysis import (
    TradeAnalysisRequest,
    TradeAnalysisResponse,
    BacktestAnalysisRequest,
    BacktestAnalysisResponse,
    MarketCommentaryRequest,
    MarketCommentaryResponse,
    RiskAssessmentRequest,
    RiskAssessmentResponse,
    StrategyOptimizationRequest,
    StrategyOptimizationResponse
)
from app.models.tradingview import TradingViewAlert
from app.services.ai_service import get_ai_service, AIAnalysisError
from app.services.backtester import backtester
import pandas as pd
import numpy as np

router = APIRouter()
logger = get_logger(__name__)


def check_ai_enabled():
    """Dependency to check if AI analysis is enabled"""
    if not settings.enable_ai_analysis:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI analysis is not enabled"
        )
    if not settings.anthropic_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service not configured"
        )


@router.post(
    "/ai/analyze-trade",
    response_model=TradeAnalysisResponse,
    dependencies=[Depends(check_ai_enabled)]
)
async def analyze_trade_signal(request: TradeAnalysisRequest) -> TradeAnalysisResponse:
    """
    Get AI analysis for a trading signal
    
    This endpoint uses Claude to analyze trading signals and provide:
    - Signal strength assessment
    - Risk/reward analysis
    - Market condition alignment
    - Specific recommendations
    """
    try:
        ai_service = get_ai_service()
        
        # Convert request to TradingViewAlert format for analysis
        alert = TradingViewAlert(
            strategy=request.strategy,
            symbol=request.symbol,
            signal=request.signal_type,
            price=request.price,
            quantity=request.quantity,
            stop_loss=request.stop_loss,
            take_profit=request.take_profit
        )
        
        # Get AI analysis
        analysis = await ai_service.analyze_trade_signal(alert, request.market_context)
        
        # Convert to response model
        return TradeAnalysisResponse(
            signal_strength=analysis.get("signal_strength", 0),
            risk_reward=analysis.get("risk_reward", 0),
            market_alignment=analysis.get("market_alignment", "unknown"),
            recommendations=analysis.get("recommendations", []),
            confidence=analysis.get("confidence", 0),
            reasoning=analysis.get("reasoning", "")
        )
        
    except AIAnalysisError as e:
        logger.error("AI analysis failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post(
    "/ai/analyze-backtest",
    response_model=BacktestAnalysisResponse,
    dependencies=[Depends(check_ai_enabled)]
)
async def analyze_backtest(request: BacktestAnalysisRequest) -> BacktestAnalysisResponse:
    """
    Get AI analysis of backtest results
    
    Provides insights on:
    - Strategy performance assessment
    - Strengths and weaknesses
    - Risk analysis
    - Improvement suggestions
    """
    try:
        # Get backtest result
        if request.backtest_id not in backtester.active_backtests:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Backtest {request.backtest_id} not found"
            )
        
        backtest_result = backtester.active_backtests[request.backtest_id]
        
        # Get AI analysis
        ai_service = get_ai_service()
        analysis = await ai_service.analyze_backtest_results(backtest_result)
        
        return BacktestAnalysisResponse(
            assessment=analysis.get("assessment", ""),
            strengths=analysis.get("strengths", []),
            weaknesses=analysis.get("weaknesses", []),
            risk_analysis=analysis.get("risk_analysis", ""),
            improvements=analysis.get("improvements", []),
            market_conditions=analysis.get("market_conditions", {}),
            parameter_suggestions=analysis.get("parameter_suggestions", {})
        )
        
    except AIAnalysisError as e:
        logger.error("Backtest analysis failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post(
    "/ai/market-commentary",
    response_model=MarketCommentaryResponse,
    dependencies=[Depends(check_ai_enabled)]
)
async def get_market_commentary(request: MarketCommentaryRequest) -> MarketCommentaryResponse:
    """
    Get AI-generated market commentary
    
    Provides professional market analysis including:
    - Current market structure
    - Key technical levels
    - Trading opportunities
    """
    try:
        ai_service = get_ai_service()
        
        # Generate synthetic data for demo (in production, fetch real data)
        dates = pd.date_range(end=pd.Timestamp.now(), periods=100, freq='1h')
        price_data = pd.DataFrame({
            'open': np.random.uniform(45000, 50000, 100),
            'high': np.random.uniform(45500, 50500, 100),
            'low': np.random.uniform(44500, 49500, 100),
            'close': np.random.uniform(45000, 50000, 100),
            'volume': np.random.uniform(1000, 10000, 100)
        }, index=dates)
        
        # Calculate basic indicators
        indicators = {
            "sma_20": float(price_data['close'].rolling(20).mean().iloc[-1]),
            "sma_50": float(price_data['close'].rolling(50).mean().iloc[-1]),
            "rsi": 50.0,  # Placeholder
            "volume_avg": float(price_data['volume'].mean())
        }
        
        # Get AI commentary
        commentary = await ai_service.generate_market_commentary(
            request.symbol,
            request.timeframe,
            price_data,
            indicators
        )
        
        # Determine sentiment based on recent price action
        price_change = (price_data['close'].iloc[-1] / price_data['close'].iloc[-24] - 1) * 100
        sentiment = "bullish" if price_change > 1 else "bearish" if price_change < -1 else "neutral"
        
        return MarketCommentaryResponse(
            symbol=request.symbol,
            timeframe=request.timeframe,
            commentary=commentary,
            key_levels={
                "resistance_1": float(price_data['high'].tail(24).max()),
                "support_1": float(price_data['low'].tail(24).min()),
                "pivot": float(price_data['close'].iloc[-1])
            },
            sentiment=sentiment
        )
        
    except Exception as e:
        logger.error("Market commentary generation failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post(
    "/ai/assess-risk",
    response_model=RiskAssessmentResponse,
    dependencies=[Depends(check_ai_enabled)]
)
async def assess_trade_risk(request: RiskAssessmentRequest) -> RiskAssessmentResponse:
    """
    Get AI-powered risk assessment for a potential trade
    
    Evaluates:
    - Position sizing appropriateness
    - Stop loss and take profit levels
    - Overall risk rating
    - Specific recommendations
    """
    try:
        ai_service = get_ai_service()
        
        # Calculate basic risk metrics
        risk_amount = request.position_size * (request.entry_price - request.stop_loss)
        risk_percentage = (risk_amount / request.account_balance) * 100
        reward_amount = request.position_size * (request.take_profit - request.entry_price)
        risk_reward_ratio = reward_amount / risk_amount if risk_amount > 0 else 0
        
        # Estimate volatility (in production, use real ATR)
        symbol_volatility = request.entry_price * 0.02  # 2% placeholder
        
        # Get AI assessment
        assessment = await ai_service.assess_risk_parameters(
            request.position_size,
            request.stop_loss,
            request.take_profit,
            request.account_balance,
            symbol_volatility
        )
        
        return RiskAssessmentResponse(
            position_size_assessment=assessment.get("position_size_assessment", ""),
            stop_loss_assessment=assessment.get("stop_loss_assessment", ""),
            take_profit_assessment=assessment.get("take_profit_assessment", ""),
            risk_rating=assessment.get("risk_rating", "MEDIUM"),
            risk_percentage=risk_percentage,
            risk_reward_ratio=risk_reward_ratio,
            recommendations=assessment.get("recommendations", []),
            approved=assessment.get("approved", False)
        )
        
    except AIAnalysisError as e:
        logger.error("Risk assessment failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post(
    "/ai/optimize-strategy",
    response_model=StrategyOptimizationResponse,
    dependencies=[Depends(check_ai_enabled)]
)
async def optimize_strategy_parameters(
    request: StrategyOptimizationRequest
) -> StrategyOptimizationResponse:
    """
    Get AI suggestions for strategy parameter optimization
    
    Analyzes recent performance and suggests:
    - Parameter adjustments
    - Expected improvements
    - Reasoning for changes
    """
    try:
        ai_service = get_ai_service()
        
        # Generate mock performance data (in production, fetch from database)
        recent_performance = [
            {
                "trade_id": i,
                "pnl": np.random.uniform(-100, 200),
                "return_pct": np.random.uniform(-2, 4),
                "duration_hours": np.random.uniform(1, 48),
                "entry_signal_strength": np.random.uniform(0.5, 1.0)
            }
            for i in range(request.performance_window)
        ]
        
        # Get AI optimization suggestions
        optimization = await ai_service.optimize_strategy_parameters(
            request.strategy_name,
            request.current_parameters,
            recent_performance
        )
        
        return StrategyOptimizationResponse(
            pattern_analysis=optimization.get("pattern_analysis", ""),
            suggested_parameters=optimization.get("suggested_parameters", {}),
            reasoning=optimization.get("reasoning", ""),
            expected_improvement_percent=optimization.get("expected_improvement_percent", 0),
            confidence_level=optimization.get("confidence_level", 50)
        )
        
    except AIAnalysisError as e:
        logger.error("Strategy optimization failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )