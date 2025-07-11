#!/usr/bin/env python3
"""
Celery worker entry point.

Start with:
    celery -A celery_worker worker --loglevel=info
    
For development with auto-reload:
    celery -A celery_worker worker --loglevel=info --autoreload
    
To run specific queues:
    celery -A celery_worker worker -Q backtest,ai_analysis --loglevel=info
"""
from app.core.celery_app import celery_app

# Import all tasks to register them
from app.workers import tasks  # noqa

if __name__ == "__main__":
    celery_app.start()