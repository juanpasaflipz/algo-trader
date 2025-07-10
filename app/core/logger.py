import logging
import sys
from pathlib import Path
from typing import Any, Dict
import structlog
from structlog.stdlib import LoggerFactory
from app.core.config import settings


def setup_logging() -> None:
    """Configure structured logging for the application"""
    
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level),
    )
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.CallsiteParameterAdder(
                parameters=[
                    structlog.processors.CallsiteParameter.FILENAME,
                    structlog.processors.CallsiteParameter.LINENO,
                    structlog.processors.CallsiteParameter.FUNC_NAME,
                ]
            ),
            structlog.processors.dict_tracebacks,
            structlog.dev.ConsoleRenderer() if settings.is_development else structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger instance"""
    return structlog.get_logger(name)


class LoggerMixin:
    """Mixin class to add logging capability to any class"""
    
    @property
    def logger(self) -> structlog.BoundLogger:
        if not hasattr(self, "_logger"):
            self._logger = get_logger(self.__class__.__module__)
        return self._logger
    
    def log_event(self, event: str, **kwargs: Any) -> None:
        """Log an event with context"""
        self.logger.info(event, **kwargs)
    
    def log_error(self, error: str, exc_info: bool = True, **kwargs: Any) -> None:
        """Log an error with context"""
        self.logger.error(error, exc_info=exc_info, **kwargs)
    
    def log_warning(self, warning: str, **kwargs: Any) -> None:
        """Log a warning with context"""
        self.logger.warning(warning, **kwargs)


class TradingLogger(LoggerMixin):
    """Specialized logger for trading events"""
    
    def log_trade(self, action: str, symbol: str, quantity: float, price: float, **kwargs: Any) -> None:
        """Log a trade execution"""
        self.log_event(
            "trade_executed",
            action=action,
            symbol=symbol,
            quantity=quantity,
            price=price,
            **kwargs
        )
    
    def log_signal(self, strategy: str, symbol: str, signal: str, **kwargs: Any) -> None:
        """Log a trading signal"""
        self.log_event(
            "signal_generated",
            strategy=strategy,
            symbol=symbol,
            signal=signal,
            **kwargs
        )
    
    def log_backtest_result(self, strategy: str, metrics: Dict[str, Any]) -> None:
        """Log backtest results"""
        self.log_event(
            "backtest_completed",
            strategy=strategy,
            **metrics
        )
    
    def log_risk_violation(self, violation_type: str, details: Dict[str, Any]) -> None:
        """Log risk management violations"""
        self.log_warning(
            "risk_violation",
            violation_type=violation_type,
            **details
        )


# Initialize logging when module is imported
setup_logging()

# Export a default logger instance
logger = get_logger(__name__)
trading_logger = TradingLogger()