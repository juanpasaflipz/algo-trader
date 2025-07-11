from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from app.core.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


class StrategyControl(BaseModel):
    """Model for strategy control commands"""

    strategy: str
    symbol: str
    action: str  # "start", "stop", "pause", "resume"
    parameters: Dict[str, Any] = {}


class PositionInfo(BaseModel):
    """Model for position information"""

    symbol: str
    side: str  # "long" or "short"
    quantity: float
    entry_price: float
    current_price: float
    pnl: float
    pnl_percent: float


class TradingStatus(BaseModel):
    """Model for overall trading status"""

    is_active: bool
    active_strategies: List[Dict[str, Any]]
    open_positions: List[PositionInfo]
    daily_pnl: float
    total_balance: float


# In-memory state (in production, this would be in a database)
active_strategies: Dict[str, Dict[str, Any]] = {}
positions: List[PositionInfo] = []


@router.post("/trading/control")
async def control_strategy(control: StrategyControl) -> dict:
    """
    Control trading strategies (start, stop, pause, resume)

    Example:
    {
        "strategy": "EMA_CROSSOVER",
        "symbol": "BTCUSDT",
        "action": "start",
        "parameters": {
            "position_size": 0.1,
            "max_positions": 3
        }
    }
    """
    strategy_key = f"{control.strategy}_{control.symbol}"

    if control.action == "start":
        if strategy_key in active_strategies:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Strategy {control.strategy} already running for {control.symbol}",
            )

        active_strategies[strategy_key] = {
            "strategy": control.strategy,
            "symbol": control.symbol,
            "status": "running",
            "parameters": control.parameters,
            "started_at": "2024-01-01T00:00:00",  # Would use datetime.utcnow() in production
        }

        logger.info(
            "Strategy started", strategy=control.strategy, symbol=control.symbol
        )

        return {"message": f"Strategy {control.strategy} started for {control.symbol}"}

    elif control.action == "stop":
        if strategy_key not in active_strategies:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Strategy {control.strategy} not found for {control.symbol}",
            )

        del active_strategies[strategy_key]

        logger.info(
            "Strategy stopped", strategy=control.strategy, symbol=control.symbol
        )

        return {"message": f"Strategy {control.strategy} stopped for {control.symbol}"}

    elif control.action == "pause":
        if strategy_key not in active_strategies:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Strategy {control.strategy} not found for {control.symbol}",
            )

        active_strategies[strategy_key]["status"] = "paused"

        return {"message": f"Strategy {control.strategy} paused for {control.symbol}"}

    elif control.action == "resume":
        if strategy_key not in active_strategies:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Strategy {control.strategy} not found for {control.symbol}",
            )

        active_strategies[strategy_key]["status"] = "running"

        return {"message": f"Strategy {control.strategy} resumed for {control.symbol}"}

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid action: {control.action}. Must be one of: start, stop, pause, resume",
        )


@router.get("/trading/status", response_model=TradingStatus)
async def get_trading_status() -> TradingStatus:
    """Get current trading status including active strategies and positions"""

    # Convert active strategies to list format
    strategies_list = [
        {"key": key, **strategy} for key, strategy in active_strategies.items()
    ]

    # Calculate mock PnL (in production, this would come from real data)
    daily_pnl = sum(pos.pnl for pos in positions)
    total_balance = 100000 + daily_pnl  # Mock balance

    return TradingStatus(
        is_active=len(active_strategies) > 0,
        active_strategies=strategies_list,
        open_positions=positions,
        daily_pnl=daily_pnl,
        total_balance=total_balance,
    )


@router.get("/trading/positions", response_model=List[PositionInfo])
async def get_positions(symbol: str = None) -> List[PositionInfo]:
    """Get current open positions, optionally filtered by symbol"""
    if symbol:
        return [pos for pos in positions if pos.symbol == symbol]
    return positions


@router.post("/trading/positions/close")
async def close_position(symbol: str, quantity: float = None) -> dict:
    """
    Close a position for a given symbol

    If quantity is not specified, closes the entire position
    """
    position_index = None
    for i, pos in enumerate(positions):
        if pos.symbol == symbol:
            position_index = i
            break

    if position_index is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No open position found for {symbol}",
        )

    position = positions[position_index]

    if quantity is None or quantity >= position.quantity:
        # Close entire position
        positions.pop(position_index)
        logger.info(
            "Position closed",
            symbol=symbol,
            quantity=position.quantity,
            pnl=position.pnl,
        )
        return {
            "message": f"Closed entire position for {symbol}",
            "quantity": position.quantity,
            "pnl": position.pnl,
        }
    else:
        # Partial close
        position.quantity -= quantity
        logger.info(
            "Position partially closed",
            symbol=symbol,
            quantity=quantity,
            remaining=position.quantity,
        )
        return {
            "message": f"Partially closed position for {symbol}",
            "quantity_closed": quantity,
            "quantity_remaining": position.quantity,
        }


@router.post("/trading/emergency-stop")
async def emergency_stop() -> dict:
    """Emergency stop - closes all positions and stops all strategies"""

    # Stop all strategies
    strategies_stopped = len(active_strategies)
    active_strategies.clear()

    # Close all positions
    positions_closed = len(positions)
    total_pnl = sum(pos.pnl for pos in positions)
    positions.clear()

    logger.warning(
        "Emergency stop activated",
        strategies_stopped=strategies_stopped,
        positions_closed=positions_closed,
        total_pnl=total_pnl,
    )

    return {
        "message": "Emergency stop completed",
        "strategies_stopped": strategies_stopped,
        "positions_closed": positions_closed,
        "total_pnl": total_pnl,
    }