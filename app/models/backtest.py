from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, validator
from enum import Enum


class BacktestStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class BacktestRequest(BaseModel):
    """Request model for initiating a backtest"""

    strategy: str = Field(..., description="Strategy name to test")
    symbol: str = Field(..., description="Trading symbol")
    start_date: datetime = Field(..., description="Backtest start date")
    end_date: datetime = Field(..., description="Backtest end date")

    # Strategy parameters
    strategy_params: Dict[str, Any] = Field(default_factory=dict)

    # Backtest configuration
    initial_capital: float = Field(default=100000.0, gt=0)
    commission: float = Field(default=0.001, ge=0, le=0.01)
    slippage: float = Field(default=0.0005, ge=0, le=0.01)

    # Risk management
    position_size_pct: float = Field(default=2.0, gt=0, le=100)
    max_positions: int = Field(default=1, ge=1, le=10)
    stop_loss_pct: Optional[float] = Field(default=2.0, gt=0, le=10)

    @validator("end_date")
    def validate_dates(cls, v, values):
        if "start_date" in values and v <= values["start_date"]:
            raise ValueError("end_date must be after start_date")
        return v


class TradeRecord(BaseModel):
    """Record of a single trade in backtest"""

    entry_time: datetime
    exit_time: datetime
    symbol: str
    direction: str  # "long" or "short"
    entry_price: float
    exit_price: float
    quantity: float
    commission: float
    pnl: float
    return_pct: float

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class BacktestMetrics(BaseModel):
    """Performance metrics from backtest"""

    # Basic metrics
    total_trades: int = Field(ge=0)
    winning_trades: int = Field(ge=0)
    losing_trades: int = Field(ge=0)
    win_rate: float = Field(ge=0, le=1)

    # Returns
    total_return: float
    annualized_return: float
    average_trade_return: float

    # Risk metrics
    max_drawdown: float
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float

    # Other metrics
    profit_factor: float = Field(ge=0)
    average_win: float
    average_loss: float
    largest_win: float
    largest_loss: float

    # Time metrics
    average_trade_duration: float  # in hours
    total_market_exposure: float  # percentage of time in market


class BacktestResult(BaseModel):
    """Complete backtest result"""

    id: str = Field(..., description="Unique backtest ID")
    status: BacktestStatus
    strategy: str
    symbol: str

    # Time period
    start_date: datetime
    end_date: datetime

    # Configuration
    initial_capital: float
    final_capital: float

    # Results
    metrics: BacktestMetrics
    trades: List[TradeRecord]

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

    # Performance chart data
    equity_curve: Optional[List[Dict[str, Any]]] = None
    drawdown_curve: Optional[List[Dict[str, Any]]] = None

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class BacktestSummary(BaseModel):
    """Summary of a backtest for listing"""

    id: str
    strategy: str
    symbol: str
    status: BacktestStatus
    total_return: float
    win_rate: float
    sharpe_ratio: float
    created_at: datetime

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
