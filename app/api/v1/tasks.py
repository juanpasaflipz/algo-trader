"""Task management endpoints for async operations."""
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from app.core.logger import get_logger
from app.workers.tasks import (
    run_backtest,
    analyze_trade_with_ai,
    process_webhook,
    batch_analyze_signals,
    get_task_status
)

router = APIRouter()
logger = get_logger(__name__)


class TaskResponse(BaseModel):
    """Response model for task creation"""
    task_id: str
    status: str
    message: str


class TaskStatus(BaseModel):
    """Task status response"""
    task_id: str
    state: str
    current: int
    total: int
    status: str
    result: Any = None
    error: bool = False


@router.post("/tasks/backtest", response_model=TaskResponse)
async def create_backtest_task(request_data: Dict[str, Any]) -> TaskResponse:
    """
    Create an async backtest task.
    
    Returns task ID that can be used to check status.
    """
    try:
        # Queue the backtest task
        task = run_backtest.delay(request_data)
        
        logger.info("Backtest task created", task_id=task.id)
        
        return TaskResponse(
            task_id=task.id,
            status="PENDING",
            message="Backtest task queued successfully"
        )
    except Exception as e:
        logger.error("Failed to create backtest task", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create backtest task"
        )


@router.post("/tasks/ai-analysis", response_model=TaskResponse)
async def create_ai_analysis_task(trade_data: Dict[str, Any]) -> TaskResponse:
    """
    Create an async AI analysis task.
    
    Returns task ID that can be used to check status.
    """
    try:
        # Queue the AI analysis task
        task = analyze_trade_with_ai.delay(trade_data)
        
        logger.info("AI analysis task created", task_id=task.id)
        
        return TaskResponse(
            task_id=task.id,
            status="PENDING",
            message="AI analysis task queued successfully"
        )
    except Exception as e:
        logger.error("Failed to create AI analysis task", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create AI analysis task"
        )


@router.post("/tasks/webhook", response_model=TaskResponse)
async def create_webhook_task(alert_data: Dict[str, Any]) -> TaskResponse:
    """
    Process webhook asynchronously.
    
    Returns task ID that can be used to check status.
    """
    try:
        # Queue the webhook processing task
        task = process_webhook.delay(alert_data)
        
        logger.info("Webhook task created", task_id=task.id)
        
        return TaskResponse(
            task_id=task.id,
            status="PENDING",
            message="Webhook processing task queued successfully"
        )
    except Exception as e:
        logger.error("Failed to create webhook task", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create webhook task"
        )


@router.post("/tasks/batch-signals", response_model=TaskResponse)
async def create_batch_signals_task(signals: List[Dict[str, Any]]) -> TaskResponse:
    """
    Analyze multiple signals in batch.
    
    Returns task ID that can be used to check status.
    """
    if not signals:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No signals provided"
        )
    
    if len(signals) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 100 signals per batch"
        )
    
    try:
        # Queue the batch analysis task
        task = batch_analyze_signals.delay(signals)
        
        logger.info("Batch signals task created", task_id=task.id, count=len(signals))
        
        return TaskResponse(
            task_id=task.id,
            status="PENDING",
            message=f"Batch analysis task queued for {len(signals)} signals"
        )
    except Exception as e:
        logger.error("Failed to create batch signals task", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create batch signals task"
        )


@router.get("/tasks/{task_id}", response_model=TaskStatus)
async def get_task_status_endpoint(task_id: str) -> TaskStatus:
    """
    Get the status of an async task.
    
    States:
    - PENDING: Task is waiting in queue
    - PROGRESS: Task is currently running
    - SUCCESS: Task completed successfully
    - FAILURE: Task failed with error
    """
    try:
        status_info = get_task_status(task_id)
        return TaskStatus(**status_info)
    except Exception as e:
        logger.error("Failed to get task status", task_id=task_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get task status"
        )


@router.delete("/tasks/{task_id}")
async def cancel_task(task_id: str) -> Dict[str, str]:
    """
    Cancel a running task.
    
    Note: Task may have already completed by the time cancel is called.
    """
    try:
        from celery.result import AsyncResult
        from app.core.celery_app import celery_app
        
        result = AsyncResult(task_id, app=celery_app)
        result.revoke(terminate=True)
        
        logger.info("Task cancelled", task_id=task_id)
        
        return {
            "task_id": task_id,
            "status": "CANCELLED",
            "message": "Task cancellation requested"
        }
    except Exception as e:
        logger.error("Failed to cancel task", task_id=task_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel task"
        )


@router.get("/tasks", response_model=List[TaskStatus])
async def list_active_tasks() -> List[TaskStatus]:
    """
    List all active tasks.
    
    Note: This only shows tasks that are currently in the system.
    Completed tasks may be purged based on result expiration settings.
    """
    try:
        from app.core.celery_app import celery_app
        
        # Get active tasks
        active_tasks = celery_app.control.inspect().active()
        
        task_statuses = []
        if active_tasks:
            for worker, tasks in active_tasks.items():
                for task in tasks:
                    task_statuses.append(
                        TaskStatus(
                            task_id=task["id"],
                            state="PROGRESS",
                            current=0,
                            total=100,
                            status=f"Running on {worker}",
                            result=None,
                            error=False
                        )
                    )
        
        return task_statuses
    except Exception as e:
        logger.error("Failed to list active tasks", error=str(e))
        return []