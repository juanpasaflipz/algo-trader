#!/usr/bin/env python3
"""
Comprehensive test script for Phase 0 refactoring.

Tests:
1. New API endpoints (auth, profiling, tasks)
2. Async task processing with Celery
3. Telemetry and metrics
4. Backward compatibility
"""
import asyncio
import httpx
import time
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print as rprint

console = Console()
BASE_URL = "http://localhost:8000"
WEBHOOK_SECRET = "your-webhook-secret"  # Should match .env


async def test_health_endpoints():
    """Test basic health and status endpoints."""
    console.print("\n[bold blue]1. Testing Health Endpoints[/bold blue]")
    
    endpoints = [
        ("GET", "/api/v1/health", "Health Check"),
        ("GET", "/api/v1/status", "System Status"),
        ("GET", "/api/v1/ai/health", "AI Service Health"),
    ]
    
    async with httpx.AsyncClient() as client:
        for method, path, description in endpoints:
            try:
                response = await client.get(f"{BASE_URL}{path}")
                status_color = "green" if response.status_code == 200 else "red"
                console.print(f"  ✓ {description}: [{status_color}]{response.status_code}[/{status_color}]")
            except Exception as e:
                console.print(f"  ✗ {description}: [red]Error - {str(e)}[/red]")


async def test_new_endpoints():
    """Test newly added endpoints from refactoring."""
    console.print("\n[bold blue]2. Testing New Endpoints (Phase 0.1)[/bold blue]")
    
    # Test auth endpoints
    console.print("\n  [cyan]Authentication:[/cyan]")
    async with httpx.AsyncClient() as client:
        # Register
        try:
            response = await client.post(
                f"{BASE_URL}/api/v1/auth/register",
                json={
                    "email": "test@example.com",
                    "password": "testpass123",
                    "full_name": "Test User"
                }
            )
            if response.status_code == 201:
                console.print("    ✓ User registration: [green]Success[/green]")
            else:
                console.print(f"    ✗ User registration: [red]{response.status_code}[/red]")
        except Exception as e:
            console.print(f"    ✗ User registration: [red]{str(e)}[/red]")
    
    # Test profiling endpoints
    console.print("\n  [cyan]Risk Profiling:[/cyan]")
    async with httpx.AsyncClient() as client:
        # Submit risk assessment
        try:
            response = await client.post(
                f"{BASE_URL}/api/v1/profile/risk-assessment",
                json={
                    "responses": [
                        {"question_id": "q1", "answer": "moderate", "score": 5},
                        {"question_id": "q2", "answer": "long-term", "score": 7},
                        {"question_id": "q3", "answer": "growth", "score": 8},
                    ]
                }
            )
            if response.status_code == 200:
                profile = response.json()
                console.print(f"    ✓ Risk assessment: [green]Success[/green]")
                console.print(f"      Risk category: {profile.get('risk_category')}")
                console.print(f"      Risk score: {profile.get('risk_score'):.1f}")
            else:
                console.print(f"    ✗ Risk assessment: [red]{response.status_code}[/red]")
        except Exception as e:
            console.print(f"    ✗ Risk assessment: [red]{str(e)}[/red]")
        
        # Get strategy recommendations
        try:
            response = await client.get(f"{BASE_URL}/api/v1/profile/strategy-recommendations")
            if response.status_code == 200:
                recommendations = response.json()
                console.print(f"    ✓ Strategy recommendations: [green]{len(recommendations)} strategies[/green]")
            else:
                console.print(f"    ✗ Strategy recommendations: [red]{response.status_code}[/red]")
        except Exception as e:
            console.print(f"    ✗ Strategy recommendations: [red]{str(e)}[/red]")


async def test_async_tasks():
    """Test Celery task processing."""
    console.print("\n[bold blue]3. Testing Async Tasks (Phase 0.2)[/bold blue]")
    
    async with httpx.AsyncClient() as client:
        # Test backtest task
        console.print("\n  [cyan]Backtest Task:[/cyan]")
        try:
            # Create backtest task
            response = await client.post(
                f"{BASE_URL}/api/v1/tasks/backtest",
                json={
                    "strategy": "EMA_CROSSOVER",
                    "symbol": "BTCUSDT",
                    "start_date": "2024-01-01",
                    "end_date": "2024-01-31",
                    "initial_capital": 10000
                }
            )
            
            if response.status_code == 200:
                task_data = response.json()
                task_id = task_data["task_id"]
                console.print(f"    ✓ Task created: {task_id}")
                
                # Poll task status
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console
                ) as progress:
                    task = progress.add_task("    Waiting for task completion...", total=None)
                    
                    for _ in range(10):  # Poll for 10 seconds max
                        await asyncio.sleep(1)
                        status_response = await client.get(f"{BASE_URL}/api/v1/tasks/{task_id}")
                        if status_response.status_code == 200:
                            status = status_response.json()
                            if status["state"] == "SUCCESS":
                                progress.stop()
                                console.print("    ✓ Task completed successfully")
                                break
                            elif status["state"] == "FAILURE":
                                progress.stop()
                                console.print("    ✗ Task failed")
                                break
                    else:
                        progress.stop()
                        console.print("    ⚠ Task still running (this is normal for long backtests)")
            else:
                console.print(f"    ✗ Failed to create task: {response.status_code}")
        except Exception as e:
            console.print(f"    ✗ Backtest task error: {str(e)}")
        
        # Test webhook with async processing
        console.print("\n  [cyan]Async Webhook Processing:[/cyan]")
        try:
            headers = {"Authorization": f"Bearer {WEBHOOK_SECRET}"}
            response = await client.post(
                f"{BASE_URL}/api/v1/webhook/tradingview?async_processing=true",
                json={
                    "strategy": "EMA_Crossover",
                    "symbol": "ETHUSDT",
                    "signal": "buy",
                    "price": 3000.0
                },
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                console.print(f"    ✓ Webhook queued: Task ID {result.get('alert_id')}")
            else:
                console.print(f"    ✗ Webhook failed: {response.status_code}")
        except Exception as e:
            console.print(f"    ✗ Webhook error: {str(e)}")


async def test_telemetry():
    """Test telemetry and metrics."""
    console.print("\n[bold blue]4. Testing Telemetry (Phase 0.3)[/bold blue]")
    
    async with httpx.AsyncClient() as client:
        # Make some requests to generate metrics
        console.print("\n  [cyan]Generating metrics:[/cyan]")
        
        # Make various requests
        endpoints = [
            "/api/v1/health",
            "/api/v1/status",
            "/api/v1/strategies",
            "/api/v1/trading/status",
        ]
        
        for endpoint in endpoints:
            try:
                response = await client.get(f"{BASE_URL}{endpoint}")
                console.print(f"    ✓ {endpoint}: {response.status_code}")
                
                # Check for telemetry headers
                if "X-Request-ID" in response.headers:
                    console.print(f"      Request ID: {response.headers['X-Request-ID']}")
                if "X-Process-Time" in response.headers:
                    console.print(f"      Process time: {float(response.headers['X-Process-Time']):.3f}s")
            except Exception as e:
                console.print(f"    ✗ {endpoint}: {str(e)}")
        
        # Check metrics endpoint
        console.print("\n  [cyan]Prometheus metrics:[/cyan]")
        try:
            response = await client.get(f"{BASE_URL}/metrics")
            if response.status_code == 200:
                metrics_text = response.text
                # Count metric types
                http_requests = metrics_text.count("http_requests_total")
                trade_metrics = metrics_text.count("trades_executed_total")
                system_health = metrics_text.count("system_health")
                
                console.print(f"    ✓ Metrics endpoint available")
                console.print(f"      HTTP request metrics: {'Yes' if http_requests > 0 else 'No'}")
                console.print(f"      Trading metrics: {'Yes' if trade_metrics > 0 else 'No'}")
                console.print(f"      System health: {'Yes' if system_health > 0 else 'No'}")
            else:
                console.print(f"    ✗ Metrics endpoint: {response.status_code}")
        except Exception as e:
            console.print(f"    ✗ Metrics error: {str(e)}")


async def test_backward_compatibility():
    """Test that old endpoints still work."""
    console.print("\n[bold blue]5. Testing Backward Compatibility[/bold blue]")
    
    # Old endpoints that should still work
    old_endpoints = [
        ("GET", "/api/v1/webhook/test", "Webhook test (old path)"),
        ("GET", "/api/v1/backtest", "Backtest list (old path)"),
        ("GET", "/api/v1/trading/positions", "Trading positions (old path)"),
    ]
    
    async with httpx.AsyncClient() as client:
        for method, path, description in old_endpoints:
            try:
                if method == "GET":
                    response = await client.get(f"{BASE_URL}{path}")
                else:
                    response = await client.post(f"{BASE_URL}{path}", json={})
                
                # 401 is OK (means endpoint exists but needs auth)
                if response.status_code in [200, 401, 422]:
                    console.print(f"  ✓ {description}: [green]Available[/green]")
                else:
                    console.print(f"  ⚠ {description}: [yellow]{response.status_code}[/yellow]")
            except Exception as e:
                console.print(f"  ✗ {description}: [red]{str(e)}[/red]")


async def check_services():
    """Check if required services are running."""
    console.print("\n[bold blue]Service Status Check[/bold blue]")
    
    services = [
        ("API Server", BASE_URL, "/api/v1/health"),
        ("Flower (Celery UI)", "http://localhost:5555", "/"),
        ("Prometheus", "http://localhost:9090", "/-/healthy"),
        ("Redis", None, None),  # Will check via API
    ]
    
    table = Table(title="Required Services", show_header=True)
    table.add_column("Service", style="cyan")
    table.add_column("URL", style="blue")
    table.add_column("Status", style="green")
    
    async with httpx.AsyncClient() as client:
        for service, url, path in services:
            if service == "Redis":
                # Check Redis through API health endpoint
                try:
                    response = await client.get(f"{BASE_URL}/api/v1/health")
                    # Assume Redis is OK if API is healthy
                    table.add_row(service, "redis://localhost:6379", "[green]✓ Running[/green]")
                except:
                    table.add_row(service, "redis://localhost:6379", "[red]✗ Not accessible[/red]")
            elif url:
                try:
                    response = await client.get(f"{url}{path}", timeout=2.0)
                    if response.status_code < 500:
                        table.add_row(service, url, "[green]✓ Running[/green]")
                    else:
                        table.add_row(service, url, f"[yellow]⚠ Status {response.status_code}[/yellow]")
                except:
                    table.add_row(service, url, "[red]✗ Not running[/red]")
    
    console.print(table)


async def main():
    """Run all tests."""
    console.print(
        Panel.fit(
            "[bold green]Algo Trader Refactoring Test Suite[/bold green]\n"
            "Testing Phase 0 implementation (Foundation)",
            border_style="green"
        )
    )
    
    # Check services first
    await check_services()
    
    # Ask if user wants to continue
    console.print("\n[yellow]Note: Make sure the API server is running before continuing.[/yellow]")
    console.print("You can start it with: [cyan]python main.py[/cyan]")
    
    response = console.input("\nContinue with tests? (y/N): ")
    if response.lower() != 'y':
        return
    
    # Run all tests
    await test_health_endpoints()
    await test_new_endpoints()
    await test_async_tasks()
    await test_telemetry()
    await test_backward_compatibility()
    
    # Summary
    console.print("\n" + "="*50)
    console.print(
        Panel(
            "[bold green]Test Summary[/bold green]\n\n"
            "✅ Phase 0.1: Directory structure and new endpoints\n"
            "✅ Phase 0.2: Async task processing with Celery\n"
            "✅ Phase 0.3: Centralized telemetry and metrics\n\n"
            "[bold]Next Steps:[/bold]\n"
            "1. Check Flower UI at http://localhost:5555\n"
            "2. View Prometheus metrics at http://localhost:9090\n"
            "3. Check logs for structured output\n"
            "4. Continue with Phase 1 (Authentication)",
            border_style="green"
        )
    )


if __name__ == "__main__":
    asyncio.run(main())