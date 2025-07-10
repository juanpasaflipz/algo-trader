from typing import Any, Dict, Optional


class AlgoTraderError(Exception):
    """Base exception for all algo trader errors"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ConfigurationError(AlgoTraderError):
    """Raised when there's a configuration issue"""
    pass


class ValidationError(AlgoTraderError):
    """Raised when data validation fails"""
    pass


class StrategyError(AlgoTraderError):
    """Base exception for strategy-related errors"""
    pass


class SignalGenerationError(StrategyError):
    """Raised when signal generation fails"""
    pass


class InsufficientDataError(StrategyError):
    """Raised when there's not enough data for strategy calculations"""
    pass


class BrokerError(AlgoTraderError):
    """Base exception for broker/exchange-related errors"""
    pass


class ConnectionError(BrokerError):
    """Raised when broker connection fails"""
    pass


class AuthenticationError(BrokerError):
    """Raised when broker authentication fails"""
    pass


class OrderError(BrokerError):
    """Raised when order placement/modification fails"""
    pass


class InsufficientFundsError(OrderError):
    """Raised when account has insufficient funds for order"""
    pass


class PositionError(BrokerError):
    """Raised when position management fails"""
    pass


class RiskManagementError(AlgoTraderError):
    """Base exception for risk management violations"""
    pass


class PositionSizeError(RiskManagementError):
    """Raised when position size exceeds limits"""
    pass


class DailyLimitError(RiskManagementError):
    """Raised when daily trade limit is exceeded"""
    pass


class StopLossError(RiskManagementError):
    """Raised when stop loss configuration is invalid"""
    pass


class BacktestError(AlgoTraderError):
    """Base exception for backtesting errors"""
    pass


class DataError(BacktestError):
    """Raised when historical data is invalid or missing"""
    pass


class WebhookError(AlgoTraderError):
    """Base exception for webhook-related errors"""
    pass


class WebhookAuthError(WebhookError):
    """Raised when webhook authentication fails"""
    pass


class WebhookParseError(WebhookError):
    """Raised when webhook payload parsing fails"""
    pass