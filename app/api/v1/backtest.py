from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Query
from app.core.logger import get_logger
from app.models.backtest import (
    BacktestRequest,
    BacktestResult,
    BacktestSummary,
    BacktestStatus
)
from app.services.backtester import Backtester

router = APIRouter()
logger = get_logger(__name__)

# Global backtester instance (in production, this would be a proper service)
backtester = Backtester()


@router.post("/backtest", response_model=BacktestResult)
async def run_backtest(request: BacktestRequest) -> BacktestResult:
    """
    Run a backtest for a given strategy and configuration
    
    Example request:
    {
        "strategy": "EMA_CROSSOVER",
        "symbol": "BTCUSDT",
        "start_date": "2023-01-01T00:00:00",
        "end_date": "2023-12-31T23:59:59",
        "initial_capital": 100000,
        "strategy_params": {
            "fast_ema_period": 12,
            "slow_ema_period": 26
        }
    }
    """
    try:
        logger.info(
            "Starting backtest",
            strategy=request.strategy,
            symbol=request.symbol,
            start_date=request.start_date.isoformat(),
            end_date=request.end_date.isoformat()
        )
        
        # Run the backtest
        result = await backtester.run_backtest(request)
        
        if result.status == BacktestStatus.FAILED:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Backtest failed: {result.error_message}"
            )
        
        return result
        
    except Exception as e:
        logger.error("Backtest execution failed", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Backtest execution failed: {str(e)}"
        )


@router.get("/backtest/{backtest_id}", response_model=BacktestResult)
async def get_backtest(backtest_id: str) -> BacktestResult:
    """Get a specific backtest result by ID"""
    if backtest_id not in backtester.active_backtests:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Backtest {backtest_id} not found"
        )
    
    return backtester.active_backtests[backtest_id]


@router.get("/backtests", response_model=List[BacktestSummary])
async def list_backtests(
    strategy: Optional[str] = Query(None, description="Filter by strategy"),
    symbol: Optional[str] = Query(None, description="Filter by symbol"),
    status: Optional[BacktestStatus] = Query(None, description="Filter by status")
) -> List[BacktestSummary]:
    """List all backtests with optional filters"""
    summaries = []
    
    for backtest_id, result in backtester.active_backtests.items():
        # Apply filters
        if strategy and result.strategy != strategy:
            continue
        if symbol and result.symbol != symbol:
            continue
        if status and result.status != status:
            continue
        
        # Create summary
        summary = BacktestSummary(
            id=result.id,
            strategy=result.strategy,
            symbol=result.symbol,
            status=result.status,
            total_return=result.metrics.total_return if result.metrics else 0,
            win_rate=result.metrics.win_rate if result.metrics else 0,
            sharpe_ratio=result.metrics.sharpe_ratio if result.metrics else 0,
            created_at=result.created_at
        )
        summaries.append(summary)
    
    return summaries


@router.get("/strategies", response_model=List[str])
async def list_strategies() -> List[str]:
    """List all available strategies"""
    return list(backtester.STRATEGIES.keys())


@router.delete("/backtest/{backtest_id}")
async def delete_backtest(backtest_id: str) -> dict:
    """Delete a backtest result"""
    if backtest_id not in backtester.active_backtests:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Backtest {backtest_id} not found"
        )
    
    del backtester.active_backtests[backtest_id]
    
    return {"message": f"Backtest {backtest_id} deleted successfully"}