"""Celery tasks for async processing."""
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from celery import Task
from celery.exceptions import SoftTimeLimitExceeded
from app.core.celery_app import celery_app
from app.core.logger import get_logger
from app.services.backtester import Backtester
from app.services.ai_service import AIService
from app.models.tradingview import TradingViewAlert
from app.models.backtest import BacktestRequest, BacktestResult

logger = get_logger(__name__)


class AsyncTask(Task):
    """Base task that properly handles async functions."""
    
    def run(self, *args, **kwargs):
        """Run the async task in an event loop."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self._async_run(*args, **kwargs))
        finally:
            loop.close()
    
    async def _async_run(self, *args, **kwargs):
        """Override this method in subclasses."""
        raise NotImplementedError


@celery_app.task(base=AsyncTask, bind=True, name="app.workers.tasks.run_backtest")
async def run_backtest(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run a backtest asynchronously.
    
    This task:
    1. Validates the backtest request
    2. Runs the backtest using the backtester service
    3. Stores results in the database
    4. Returns the backtest results
    """
    task_id = self.request.id
    logger.info("Starting backtest task", task_id=task_id, request=request_data)
    
    try:
        # Convert dict to BacktestRequest model
        backtest_request = BacktestRequest(**request_data)
        
        # Update task state
        self.update_state(
            state="PROGRESS",
            meta={
                "current": 0,
                "total": 100,
                "status": "Initializing backtest..."
            }
        )
        
        # Run the backtest
        backtester = Backtester()
        
        # Progress callback
        def update_progress(progress: int, message: str):
            self.update_state(
                state="PROGRESS",
                meta={
                    "current": progress,
                    "total": 100,
                    "status": message
                }
            )
        
        result = await backtester.run_backtest_async(
            backtest_request,
            progress_callback=update_progress
        )
        
        logger.info(
            "Backtest completed",
            task_id=task_id,
            total_trades=result.metrics.total_trades,
            total_return=result.metrics.total_return
        )
        
        # Return serializable result
        return result.model_dump()
        
    except SoftTimeLimitExceeded:
        logger.error("Backtest task exceeded time limit", task_id=task_id)
        raise
    except Exception as e:
        logger.error("Backtest task failed", task_id=task_id, error=str(e))
        raise


@celery_app.task(base=AsyncTask, bind=True, name="app.workers.tasks.analyze_trade_with_ai")
async def analyze_trade_with_ai(self, trade_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze a trade signal using AI.
    
    This task:
    1. Prepares the trade data for AI analysis
    2. Calls the AI service for analysis
    3. Returns AI recommendations
    """
    task_id = self.request.id
    logger.info("Starting AI analysis task", task_id=task_id)
    
    try:
        # Initialize AI service
        ai_service = AIService()
        
        # Check if AI is available
        if not await ai_service.health_check():
            logger.warning("AI service not available", task_id=task_id)
            return {
                "success": False,
                "error": "AI service not available",
                "recommendations": ["Proceed with standard risk management rules"]
            }
        
        # Analyze the trade
        result = await ai_service.analyze_trade(trade_data)
        
        logger.info(
            "AI analysis completed",
            task_id=task_id,
            confidence=result.get("confidence"),
            recommendation=result.get("recommendation")
        )
        
        return result
        
    except Exception as e:
        logger.error("AI analysis task failed", task_id=task_id, error=str(e))
        # Return a safe default response
        return {
            "success": False,
            "error": str(e),
            "recommendations": ["Use default strategy parameters"]
        }


@celery_app.task(bind=True, name="app.workers.tasks.process_webhook")
def process_webhook(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process a TradingView webhook alert asynchronously.
    
    This task:
    1. Validates the alert
    2. Checks strategy availability
    3. Executes the trade if approved
    4. Logs the result
    """
    task_id = self.request.id
    logger.info("Processing webhook", task_id=task_id, alert=alert_data)
    
    try:
        # Convert to alert model
        alert = TradingViewAlert(**alert_data)
        
        # Update task state
        self.update_state(
            state="PROGRESS",
            meta={"status": "Validating alert..."}
        )
        
        # TODO: Implement actual webhook processing
        # 1. Check if strategy is enabled
        # 2. Validate against current positions
        # 3. Apply risk management rules
        # 4. Execute trade if approved
        # 5. Store in database
        
        result = {
            "task_id": task_id,
            "alert_id": alert_data.get("alert_id"),
            "status": "processed",
            "action_taken": "simulated",
            "message": f"Alert for {alert.symbol} processed successfully"
        }
        
        logger.info("Webhook processed", task_id=task_id, result=result)
        return result
        
    except Exception as e:
        logger.error("Webhook processing failed", task_id=task_id, error=str(e))
        raise


@celery_app.task(name="app.workers.tasks.check_strategy_health")
def check_strategy_health() -> Dict[str, Any]:
    """
    Periodic task to check health of all active strategies.
    
    This task:
    1. Gets list of active strategies
    2. Checks each strategy's performance
    3. Alerts if any strategy is underperforming
    """
    logger.info("Checking strategy health")
    
    try:
        # TODO: Implement strategy health check
        # 1. Query active strategies from database
        # 2. Check recent performance metrics
        # 3. Compare against thresholds
        # 4. Send alerts if needed
        
        result = {
            "timestamp": datetime.utcnow().isoformat(),
            "strategies_checked": 0,
            "healthy": 0,
            "warnings": 0,
            "alerts": []
        }
        
        logger.info("Strategy health check completed", result=result)
        return result
        
    except Exception as e:
        logger.error("Strategy health check failed", error=str(e))
        raise


@celery_app.task(name="app.workers.tasks.cleanup_old_results")
def cleanup_old_results() -> Dict[str, Any]:
    """
    Periodic task to clean up old backtest results and logs.
    
    This task:
    1. Removes backtest results older than 30 days
    2. Archives important results
    3. Cleans up temporary files
    """
    logger.info("Starting cleanup of old results")
    
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        # TODO: Implement cleanup logic
        # 1. Query old backtest results
        # 2. Archive important ones to S3/storage
        # 3. Delete from database
        # 4. Clean up file system
        
        result = {
            "timestamp": datetime.utcnow().isoformat(),
            "results_cleaned": 0,
            "space_freed_mb": 0,
            "archived_count": 0
        }
        
        logger.info("Cleanup completed", result=result)
        return result
        
    except Exception as e:
        logger.error("Cleanup task failed", error=str(e))
        raise


@celery_app.task(bind=True, name="app.workers.tasks.batch_analyze_signals")
def batch_analyze_signals(self, signals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Analyze multiple trading signals in batch.
    
    Useful for:
    - Processing multiple alerts at once
    - Reprocessing historical signals
    - Bulk strategy testing
    """
    task_id = self.request.id
    total_signals = len(signals)
    logger.info("Starting batch signal analysis", task_id=task_id, count=total_signals)
    
    results = []
    
    for i, signal in enumerate(signals):
        try:
            # Update progress
            self.update_state(
                state="PROGRESS",
                meta={
                    "current": i + 1,
                    "total": total_signals,
                    "status": f"Processing signal {i + 1} of {total_signals}"
                }
            )
            
            # Process each signal
            # TODO: Implement actual signal processing
            result = {
                "signal_id": signal.get("id", i),
                "symbol": signal.get("symbol"),
                "status": "processed",
                "recommendation": "hold"
            }
            
            results.append(result)
            
        except Exception as e:
            logger.error(
                "Failed to process signal",
                task_id=task_id,
                signal_index=i,
                error=str(e)
            )
            results.append({
                "signal_id": signal.get("id", i),
                "status": "failed",
                "error": str(e)
            })
    
    logger.info(
        "Batch analysis completed",
        task_id=task_id,
        total=total_signals,
        successful=sum(1 for r in results if r["status"] == "processed")
    )
    
    return results


# Task status helper
def get_task_status(task_id: str) -> Dict[str, Any]:
    """Get the status of a Celery task."""
    from celery.result import AsyncResult
    
    result = AsyncResult(task_id, app=celery_app)
    
    if result.state == "PENDING":
        return {
            "task_id": task_id,
            "state": result.state,
            "current": 0,
            "total": 100,
            "status": "Task pending..."
        }
    elif result.state == "PROGRESS":
        return {
            "task_id": task_id,
            "state": result.state,
            "current": result.info.get("current", 0),
            "total": result.info.get("total", 100),
            "status": result.info.get("status", "")
        }
    elif result.state == "SUCCESS":
        return {
            "task_id": task_id,
            "state": result.state,
            "current": 100,
            "total": 100,
            "status": "Task completed successfully",
            "result": result.result
        }
    else:  # FAILURE
        return {
            "task_id": task_id,
            "state": result.state,
            "current": 0,
            "total": 100,
            "status": str(result.info),
            "error": True
        }