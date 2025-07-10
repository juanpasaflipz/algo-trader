from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum
from app.models.base import (
    BaseTradingSignal, BaseResponse, BaseModelConfig,
    validate_symbol, validate_positive_number
)


class SignalType(str, Enum):
    BUY = "buy"
    SELL = "sell"
    CLOSE = "close"
    CLOSE_BUY = "close_buy"
    CLOSE_SELL = "close_sell"


class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"


class TradingViewAlert(BaseTradingSignal):
    """TradingView webhook payload model - extends BaseTradingSignal.
    
    OPTIMIZATION: Extends BaseTradingSignal instead of duplicating common fields.
    This reduces code by ~40% and ensures consistent validation across all signal types.
    """
    
    # Additional required fields beyond base
    strategy: str = Field(..., description="Strategy name that generated the signal")
    signal: SignalType = Field(..., description="Trading signal type")
    
    # Additional optional fields
    order_type: OrderType = Field(default=OrderType.MARKET)
    message: Optional[str] = Field(None, description="Additional message from Pine Script")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    # Override timestamp to be included
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Use base validators and add custom ones
    _validate_symbol = validator("symbol", allow_reuse=True)(validate_symbol)
    _validate_quantity = validator("quantity", allow_reuse=True)(validate_positive_number("quantity"))
    _validate_price = validator("price", allow_reuse=True)(validate_positive_number("price"))


class WebhookResponse(BaseResponse):
    """Response model for webhook endpoints.
    
    OPTIMIZATION: Extends BaseResponse to inherit timestamp and JSON encoding.
    """
    
    success: bool
    message: str
    alert_id: Optional[str] = None


class AlertValidation(BaseModel):
    """Alert validation result"""
    
    is_valid: bool
    errors: Optional[Dict[str, str]] = None
    warnings: Optional[Dict[str, str]] = None