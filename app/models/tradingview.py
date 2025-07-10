from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum


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


class TradingViewAlert(BaseModel):
    """TradingView webhook payload model"""
    
    # Required fields
    strategy: str = Field(..., description="Strategy name that generated the signal")
    symbol: str = Field(..., description="Trading symbol (e.g., BTCUSDT, AAPL)")
    signal: SignalType = Field(..., description="Trading signal type")
    
    # Optional fields
    price: Optional[float] = Field(None, description="Current price or target price")
    quantity: Optional[float] = Field(None, description="Position size")
    order_type: OrderType = Field(default=OrderType.MARKET)
    stop_loss: Optional[float] = Field(None, description="Stop loss price")
    take_profit: Optional[float] = Field(None, description="Take profit price")
    
    # Metadata
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    message: Optional[str] = Field(None, description="Additional message from Pine Script")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    @validator("symbol")
    def validate_symbol(cls, v):
        """Ensure symbol is uppercase"""
        return v.upper()
    
    @validator("quantity")
    def validate_quantity(cls, v):
        """Ensure quantity is positive"""
        if v is not None and v <= 0:
            raise ValueError("Quantity must be positive")
        return v
    
    @validator("price", "stop_loss", "take_profit")
    def validate_prices(cls, v):
        """Ensure prices are positive"""
        if v is not None and v <= 0:
            raise ValueError("Price must be positive")
        return v
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class WebhookResponse(BaseModel):
    """Response model for webhook endpoints"""
    
    success: bool
    message: str
    alert_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AlertValidation(BaseModel):
    """Alert validation result"""
    
    is_valid: bool
    errors: Optional[Dict[str, str]] = None
    warnings: Optional[Dict[str, str]] = None