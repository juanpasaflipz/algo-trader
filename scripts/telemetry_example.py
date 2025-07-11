#!/usr/bin/env python3
"""
Example of using centralized telemetry in algo-trader.

This script demonstrates:
1. Structured logging
2. Metrics collection
3. Execution timing
4. Distributed tracing
"""
import asyncio
import random
from app.core.telemetry import get_logger, metrics, log_execution_time, trace

# Get a logger for this module
logger = get_logger(__name__)


@log_execution_time("example_processing_time")
async def process_trading_signal(symbol: str, signal: str, price: float):
    """Example async function with telemetry."""
    
    # Use structured logging
    logger.info(
        "Processing trading signal",
        symbol=symbol,
        signal=signal,
        price=price
    )
    
    # Simulate processing time
    await asyncio.sleep(random.uniform(0.1, 0.5))
    
    # Update metrics
    metrics.trades_executed.labels(
        symbol=symbol,
        action=signal,
        strategy="example"
    ).inc()
    
    # Simulate trade execution
    if random.random() > 0.5:
        pnl = random.uniform(-100, 200)
        metrics.trade_pnl.labels(
            symbol=symbol,
            strategy="example"
        ).observe(pnl)
        
        logger.info(
            "Trade executed successfully",
            symbol=symbol,
            signal=signal,
            pnl=pnl
        )
        return {"status": "success", "pnl": pnl}
    else:
        logger.warning(
            "Trade execution failed",
            symbol=symbol,
            signal=signal,
            reason="Insufficient liquidity"
        )
        metrics.error_rate.labels(
            error_type="InsufficientLiquidity",
            component="trading"
        ).inc()
        return {"status": "failed", "reason": "Insufficient liquidity"}


def demonstrate_tracing():
    """Demonstrate distributed tracing context."""
    
    with trace("analyze_market", asset_class="crypto") as t:
        logger.info("Starting market analysis")
        
        # Add tags dynamically
        t.add_tag("exchange", "binance")
        t.add_tag("timeframe", "1h")
        
        # Simulate analysis
        import time
        time.sleep(0.2)
        
        # Nested trace
        with trace("fetch_data", source="api"):
            logger.info("Fetching market data")
            time.sleep(0.1)
        
        logger.info("Market analysis completed")


async def main():
    """Run telemetry examples."""
    
    print("🔍 Telemetry Examples\n")
    
    # Example 1: Basic logging
    print("1. Basic structured logging:")
    logger.info("Application started", environment="development")
    logger.warning("Low balance detected", balance=1000, threshold=5000)
    logger.error("Connection failed", service="redis", retry_count=3)
    
    # Example 2: Metrics
    print("\n2. Updating metrics:")
    metrics.webhooks_received.labels(source="tradingview", signal_type="buy").inc()
    metrics.ai_confidence_score.labels(analysis_type="trade_signal").observe(0.85)
    metrics.active_positions.labels(symbol="BTCUSDT", strategy="ema_crossover").set(3)
    
    # Example 3: Async function with timing
    print("\n3. Timed async execution:")
    result = await process_trading_signal("BTCUSDT", "buy", 50000.0)
    print(f"   Result: {result}")
    
    # Example 4: Distributed tracing
    print("\n4. Distributed tracing:")
    demonstrate_tracing()
    
    # Example 5: Batch operations with metrics
    print("\n5. Batch operations:")
    signals = [
        ("ETHUSDT", "buy", 3000),
        ("BNBUSDT", "sell", 500),
        ("SOLUSDT", "buy", 100),
    ]
    
    for symbol, signal, price in signals:
        await process_trading_signal(symbol, signal, price)
    
    print("\n✅ All examples completed!")
    print("\nTo view metrics:")
    print("  - Logs are written to stdout (console format)")
    print("  - Prometheus metrics available at http://localhost:9090/metrics")
    print("  - In production, logs would be in JSON format")


if __name__ == "__main__":
    asyncio.run(main())