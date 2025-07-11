"""Base models and mixins for common patterns across the application.

Following LEVER optimization principles to reduce code duplication.
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, validator


class BaseModelConfig:
    """Base configuration for all models with common JSON encoders."""

    json_encoders = {datetime: lambda v: v.isoformat()}


class TimestampMixin:
    """Mixin for models that need timestamp fields."""

    timestamp: datetime = Field(default_factory=datetime.utcnow)


class BaseResponse(BaseModel):
    """Base response model for all API responses."""

    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config(BaseModelConfig):
        pass


class BaseAnalysisResponse(BaseResponse):
    """Base response for all AI analysis endpoints."""

    confidence: float = Field(..., ge=0, le=100, description="Confidence score 0-100")
    reasoning: str = Field(..., description="Explanation of the analysis")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class BaseTradingSignal(BaseModel):
    """Base model for all trading signals across the application."""

    symbol: str
    signal: str  # buy, sell, close
    price: float = Field(..., gt=0)
    quantity: Optional[float] = Field(None, gt=0)
    stop_loss: Optional[float] = Field(None, gt=0)
    take_profit: Optional[float] = Field(None, gt=0)

    @validator("signal")
    def validate_signal(cls, v):
        """Validate signal is one of the allowed values."""
        allowed = {"buy", "sell", "close", "hold"}
        if v.lower() not in allowed:
            raise ValueError(f"Signal must be one of {allowed}")
        return v.lower()

    @validator("stop_loss")
    def validate_stop_loss(cls, v, values):
        """Validate stop loss is below buy price, above sell price."""
        if v is None or "signal" not in values or "price" not in values:
            return v

        signal = values.get("signal")
        price = values.get("price")

        if signal == "buy" and v >= price:
            raise ValueError("Stop loss must be below buy price")
        elif signal == "sell" and v <= price:
            raise ValueError("Stop loss must be above sell price")

        return v

    @validator("take_profit")
    def validate_take_profit(cls, v, values):
        """Validate take profit is above buy price, below sell price."""
        if v is None or "signal" not in values or "price" not in values:
            return v

        signal = values.get("signal")
        price = values.get("price")

        if signal == "buy" and v <= price:
            raise ValueError("Take profit must be above buy price")
        elif signal == "sell" and v >= price:
            raise ValueError("Take profit must be below sell price")

        return v

    class Config(BaseModelConfig):
        pass


# Common field validators that can be reused
def validate_positive_number(field_name: str):
    """Create a validator for positive numbers."""

    def validator(v):
        if v is not None and v <= 0:
            raise ValueError(f"{field_name} must be positive")
        return v

    return validator


def validate_percentage(field_name: str):
    """Create a validator for percentage fields (0-100)."""

    def validator(v):
        if v is not None and not 0 <= v <= 100:
            raise ValueError(f"{field_name} must be between 0 and 100")
        return v

    return validator


def validate_symbol(v: str) -> str:
    """Validate trading symbol format."""
    if not v or not v.strip():
        raise ValueError("Symbol cannot be empty")
    # Add more symbol validation as needed
    return v.upper().strip()
