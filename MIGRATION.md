# Algo Trader Refactoring Migration Guide

This document tracks the incremental refactoring from the current architecture to the new plugin-based, scalable architecture.

## Overview

We're performing an incremental refactoring to transform the algo-trader codebase while maintaining full functionality throughout the process.

### Migration Principles
1. **No breaking changes** - The system remains operational at all times
2. **Feature flags** - New implementations can be toggled on/off
3. **Incremental changes** - One component at a time
4. **Backward compatibility** - Old code continues to work until fully migrated
5. **Continuous testing** - All tests must pass after each change

## Phase 0: Foundation (Current)

### 0.1 Directory Restructuring ✅
**Status**: Completed
**Goal**: Align directory structure with new architecture while preserving functionality

#### Changes:
- [x] Create `app/workers/` directory for async tasks
- [x] Reorganize `app/services/` into subdirectories:
  - [x] `app/services/data/` - Market data fetching and caching
  - [x] `app/services/strategies/` - Already exists ✓
  - [x] `app/services/execution/` - Broker adapters and trade execution
- [x] Create `scripts/` directory with CLI tool
- [x] Rename API endpoints to match new structure:
  - [x] `tradingview_webhook.py` → `webhooks.py`
  - [x] `trade_controller.py` → `execution.py`
  - [x] Create `auth.py` for authentication endpoints
  - [x] Create `profiling.py` for risk assessment
  - [x] Rename `backtest.py` → `strategies.py` (includes backtest endpoints)

#### Migration Steps:
1. Create new directories ✅
2. Copy files to new locations (keep originals) ✅
3. Update imports to use new paths ✅
4. Test everything works ✅
5. Remove old files ⏳ (keeping for now to ensure backward compatibility)
6. Update all references ✅

### 0.2 Task Queue Implementation ✅
**Status**: Completed
**Goal**: Add Celery + Redis for async operations

#### Changes:
- [x] Added Celery to dependencies in pyproject.toml
- [x] Created `app/core/celery_app.py` with Celery configuration
- [x] Updated config.py with Celery broker/backend settings
- [x] Created `app/workers/tasks.py` with async tasks:
  - [x] `run_backtest` - Async backtest execution with progress tracking
  - [x] `analyze_trade_with_ai` - AI analysis in background
  - [x] `process_webhook` - Webhook processing queue
  - [x] `batch_analyze_signals` - Batch signal processing
  - [x] Periodic tasks for health checks and cleanup
- [x] Created `celery_worker.py` entry point
- [x] Updated docker-compose.yml with:
  - [x] Celery worker service
  - [x] Celery beat service for periodic tasks
  - [x] Flower service for task monitoring (port 5555)
- [x] Created `app/api/v1/tasks.py` for task management endpoints
- [x] Updated webhook endpoint to support async processing flag

#### New Capabilities:
- Long-running backtests don't block API requests
- AI analysis can be queued for batch processing
- Webhook processing can be made async for high throughput
- Task progress tracking with real-time updates
- Task cancellation support
- Flower UI for monitoring tasks at http://localhost:5555

### 0.3 Centralized Telemetry ✅
**Status**: Completed
**Goal**: Single source for logging, metrics, and tracing

#### Changes:
- [x] Created `app/core/telemetry.py` with unified telemetry interface
- [x] Integrated structlog for structured logging
- [x] Added comprehensive Prometheus metrics:
  - [x] HTTP request metrics (count, duration)
  - [x] Trading metrics (trades, PnL, positions)
  - [x] Webhook metrics (received, processing time)
  - [x] Backtest metrics (runs, duration)
  - [x] AI analysis metrics (analyses, response time, confidence)
  - [x] Task queue metrics (tasks created, duration)
  - [x] System health and error metrics
- [x] Created telemetry middleware for automatic request tracking
- [x] Added execution timing decorator `@log_execution_time()`
- [x] Implemented distributed tracing context (placeholder for OpenTelemetry)
- [x] Updated existing logger module to use centralized telemetry
- [x] Added request ID tracking for correlation
- [x] Created example script demonstrating telemetry usage

#### New Capabilities:
- Structured JSON logging in production
- Automatic request/response tracking with timing
- Comprehensive metrics for all operations
- Error tracking with component attribution
- Execution time measurement for any function
- Context propagation for distributed tracing
- Request correlation with X-Request-ID headers

## Phase 1: Core Improvements 🔜

### 1.1 Authentication Layer
- JWT-based authentication
- User models and management
- API key management

### 1.2 Plugin Architecture
- Strategy discovery via entry points
- Dynamic strategy loading
- Strategy registry

### 1.3 CLI Development
- Typer-based CLI
- Commands for backtest, trade, optimize

## Phase 2: Feature Migration 🔜

### 2.1 Enhanced Webhooks
- Async processing with Celery
- Better error handling
- Webhook validation

### 2.2 Data Service Layer
- Abstract data providers
- Caching implementation
- Multiple data source support

### 2.3 Profiling System
- Risk questionnaire API
- Strategy selection algorithm
- User preference storage

## Phase 3: New Features 🔜

### 3.1 Broker Adapters
- Binance paper trading
- Alpaca sandbox
- Common broker interface

### 3.2 Enhanced Monitoring
- Prometheus metrics
- Structured logging
- Alert system

## Rollback Procedures

Each phase includes rollback steps:

1. **Git tags** at each stable point: `pre-phase-0`, `post-phase-0`, etc.
2. **Feature flags** in config to disable new features
3. **Database migrations** are reversible
4. **Old code** kept until new code is proven

## Testing Strategy

- Run full test suite after each change
- Add tests for new functionality
- Performance benchmarks to ensure no regression
- Integration tests for critical paths

## Progress Tracking

| Phase | Component | Status | Started | Completed | Notes |
|-------|-----------|--------|---------|-----------|-------|
| 0.1 | Directory Structure | ✅ Completed | 2025-01-11 | 2025-01-11 | New structure in place, old files preserved |
| 0.2 | Task Queue | ✅ Completed | 2025-01-11 | 2025-01-11 | Celery + Redis implemented with task management |
| 0.3 | Telemetry | ✅ Completed | 2025-01-11 | 2025-01-11 | Centralized logging, metrics, and tracing |
| 1.1 | Authentication | 🔜 Pending | - | - | - |
| 1.2 | Plugin Architecture | 🔜 Pending | - | - | - |
| 1.3 | CLI | 🔜 Pending | - | - | - |
| 2.1 | Enhanced Webhooks | 🔜 Pending | - | - | - |
| 2.2 | Data Service | 🔜 Pending | - | - | - |
| 2.3 | Profiling | 🔜 Pending | - | - | - |
| 3.1 | Brokers | 🔜 Pending | - | - | - |
| 3.2 | Monitoring | 🔜 Pending | - | - | - |

## Breaking Changes Log

Document any breaking changes here (there should be none during incremental refactoring):

- None yet

## Deprecation Notices

List deprecated features and their removal timeline:

- None yet

---

Last Updated: 2025-01-11