"""Celery application configuration."""
from celery import Celery
from app.core.config import settings

# Create Celery instance
celery_app = Celery(
    "algo_trader",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.workers.tasks"],  # Auto-discover tasks in this module
)

# Configure Celery
celery_app.conf.update(
    # Task settings
    task_serializer="json",
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    task_acks_late=True,
    
    # Result settings
    result_serializer="json",
    result_backend=settings.celery_result_backend,
    result_expires=3600,  # 1 hour
    
    # Worker settings
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
    worker_disable_rate_limits=False,
    
    # Beat schedule (for periodic tasks)
    beat_schedule={
        # Example: Check strategy health every 5 minutes
        "check-strategy-health": {
            "task": "app.workers.tasks.check_strategy_health",
            "schedule": 300.0,  # 5 minutes
        },
        # Example: Clean up old backtest results daily
        "cleanup-old-results": {
            "task": "app.workers.tasks.cleanup_old_results",
            "schedule": 86400.0,  # 24 hours
        },
    },
    
    # Queue routing
    task_routes={
        "app.workers.tasks.run_backtest": {"queue": "backtest"},
        "app.workers.tasks.analyze_trade_with_ai": {"queue": "ai_analysis"},
        "app.workers.tasks.process_webhook": {"queue": "webhooks"},
        "app.workers.tasks.*": {"queue": "default"},
    },
    
    # Error handling
    task_reject_on_worker_lost=True,
    task_ignore_result=False,
)

# Set timezone
celery_app.conf.timezone = "UTC"


def get_celery_app() -> Celery:
    """Get the Celery application instance."""
    return celery_app