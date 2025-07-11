"""
Centralized telemetry for logging, metrics, and tracing.

This module provides a unified interface for:
- Structured logging with structlog
- Metrics collection with Prometheus
- Distributed tracing with OpenTelemetry (future)

Usage:
    from app.core.telemetry import get_logger, metrics, trace
    
    logger = get_logger(__name__)
    logger.info("Processing trade", symbol="BTCUSDT", action="buy")
    
    metrics.counter("trades_processed").inc()
    metrics.histogram("trade_latency").observe(0.123)
"""
import time
from functools import wraps
from typing import Dict, Any, Optional, Callable
from contextvars import ContextVar
from prometheus_client import Counter, Histogram, Gauge, Summary
import structlog
from structlog.contextvars import bind_contextvars, clear_contextvars

# Context variable for request tracking
request_id_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)


class TelemetryMetrics:
    """Centralized metrics collection."""
    
    def __init__(self):
        # API Metrics
        self.http_requests = Counter(
            "http_requests_total",
            "Total HTTP requests",
            ["method", "endpoint", "status"]
        )
        self.http_request_duration = Histogram(
            "http_request_duration_seconds",
            "HTTP request duration",
            ["method", "endpoint"]
        )
        
        # Trading Metrics
        self.trades_executed = Counter(
            "trades_executed_total",
            "Total trades executed",
            ["symbol", "action", "strategy"]
        )
        self.trade_pnl = Summary(
            "trade_pnl_dollars",
            "Trade profit and loss",
            ["symbol", "strategy"]
        )
        self.active_positions = Gauge(
            "active_positions",
            "Number of active positions",
            ["symbol", "strategy"]
        )
        
        # Webhook Metrics
        self.webhooks_received = Counter(
            "webhooks_received_total",
            "Total webhooks received",
            ["source", "signal_type"]
        )
        self.webhook_processing_time = Histogram(
            "webhook_processing_seconds",
            "Webhook processing time",
            ["source"]
        )
        
        # Backtest Metrics
        self.backtests_run = Counter(
            "backtests_run_total",
            "Total backtests executed",
            ["strategy", "status"]
        )
        self.backtest_duration = Histogram(
            "backtest_duration_seconds",
            "Backtest execution time",
            ["strategy"]
        )
        
        # AI Metrics
        self.ai_analyses = Counter(
            "ai_analyses_total",
            "Total AI analyses performed",
            ["analysis_type", "status"]
        )
        self.ai_response_time = Histogram(
            "ai_response_time_seconds",
            "AI service response time",
            ["analysis_type"]
        )
        self.ai_confidence_score = Histogram(
            "ai_confidence_score",
            "AI analysis confidence scores",
            ["analysis_type"],
            buckets=(0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99)
        )
        
        # Task Queue Metrics
        self.celery_tasks_created = Counter(
            "celery_tasks_created_total",
            "Total Celery tasks created",
            ["task_name"]
        )
        self.celery_task_duration = Histogram(
            "celery_task_duration_seconds",
            "Celery task execution time",
            ["task_name", "status"]
        )
        
        # System Metrics
        self.system_health = Gauge(
            "system_health",
            "Overall system health (0=unhealthy, 1=healthy)",
            ["component"]
        )
        self.error_rate = Counter(
            "errors_total",
            "Total errors",
            ["error_type", "component"]
        )


# Global metrics instance
metrics = TelemetryMetrics()


def configure_logging(
    log_level: str = "INFO",
    log_format: str = "json",
    add_timestamp: bool = True
) -> None:
    """
    Configure structured logging for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_format: Output format ("json" or "console")
        add_timestamp: Whether to add timestamp to logs
    """
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
    ]
    
    if add_timestamp:
        processors.append(structlog.processors.TimeStamper(fmt="iso"))
    
    if log_format == "json":
        processors.extend([
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()
        ])
    else:
        processors.extend([
            structlog.processors.format_exc_info,
            structlog.dev.ConsoleRenderer()
        ])
    
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """
    Get a logger instance with the given name.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Configured logger instance
    """
    return structlog.get_logger(name)


def set_request_id(request_id: str) -> None:
    """Set request ID for context tracking."""
    request_id_var.set(request_id)
    bind_contextvars(request_id=request_id)


def clear_request_id() -> None:
    """Clear request ID from context."""
    request_id_var.set(None)
    clear_contextvars()


def log_execution_time(metric_name: Optional[str] = None):
    """
    Decorator to log and measure function execution time.
    
    Args:
        metric_name: Optional Prometheus histogram metric name
        
    Example:
        @log_execution_time("backtest_duration_seconds")
        async def run_backtest(...):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            logger = get_logger(func.__module__)
            start_time = time.time()
            
            try:
                logger.info(
                    f"Starting {func.__name__}",
                    function=func.__name__,
                    args_count=len(args),
                    kwargs_count=len(kwargs)
                )
                
                result = await func(*args, **kwargs)
                
                duration = time.time() - start_time
                logger.info(
                    f"Completed {func.__name__}",
                    function=func.__name__,
                    duration_seconds=duration,
                    success=True
                )
                
                if metric_name:
                    metrics.__dict__.get(metric_name, lambda: None).observe(duration)
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                logger.error(
                    f"Failed {func.__name__}",
                    function=func.__name__,
                    duration_seconds=duration,
                    error=str(e),
                    success=False
                )
                metrics.error_rate.labels(
                    error_type=type(e).__name__,
                    component=func.__module__
                ).inc()
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            logger = get_logger(func.__module__)
            start_time = time.time()
            
            try:
                logger.info(
                    f"Starting {func.__name__}",
                    function=func.__name__,
                    args_count=len(args),
                    kwargs_count=len(kwargs)
                )
                
                result = func(*args, **kwargs)
                
                duration = time.time() - start_time
                logger.info(
                    f"Completed {func.__name__}",
                    function=func.__name__,
                    duration_seconds=duration,
                    success=True
                )
                
                if metric_name:
                    metrics.__dict__.get(metric_name, lambda: None).observe(duration)
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                logger.error(
                    f"Failed {func.__name__}",
                    function=func.__name__,
                    duration_seconds=duration,
                    error=str(e),
                    success=False
                )
                metrics.error_rate.labels(
                    error_type=type(e).__name__,
                    component=func.__module__
                ).inc()
                raise
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


class TraceContext:
    """Context manager for distributed tracing (placeholder for OpenTelemetry)."""
    
    def __init__(self, operation_name: str, tags: Optional[Dict[str, Any]] = None):
        self.operation_name = operation_name
        self.tags = tags or {}
        self.logger = get_logger(__name__)
    
    def __enter__(self):
        self.start_time = time.time()
        self.logger.info(
            f"Starting trace: {self.operation_name}",
            operation=self.operation_name,
            tags=self.tags
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        if exc_type:
            self.logger.error(
                f"Trace failed: {self.operation_name}",
                operation=self.operation_name,
                duration_seconds=duration,
                error=str(exc_val),
                tags=self.tags
            )
        else:
            self.logger.info(
                f"Trace completed: {self.operation_name}",
                operation=self.operation_name,
                duration_seconds=duration,
                tags=self.tags
            )
    
    def add_tag(self, key: str, value: Any):
        """Add a tag to the current trace."""
        self.tags[key] = value
        bind_contextvars(**{key: value})


def trace(operation_name: str, **tags):
    """
    Create a trace context for the given operation.
    
    Example:
        with trace("process_webhook", source="tradingview", symbol="BTCUSDT"):
            # Process webhook
            pass
    """
    return TraceContext(operation_name, tags)


# Configure logging on module import
configure_logging()