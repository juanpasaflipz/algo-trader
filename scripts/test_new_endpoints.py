#!/usr/bin/env python3
"""Quick test to verify all endpoints are accessible after restructuring."""
import httpx
import asyncio
from rich.console import Console
from rich.table import Table

console = Console()
BASE_URL = "http://localhost:8000"


async def test_endpoints():
    """Test all API endpoints to ensure they're accessible."""
    
    # Define endpoints to test
    endpoints = [
        # Status
        ("GET", "/api/v1/health", None, "Health Check"),
        ("GET", "/api/v1/status", None, "System Status"),
        
        # Auth (new)
        ("POST", "/api/v1/auth/register", {"email": "test@example.com", "password": "test123", "full_name": "Test User"}, "User Registration"),
        ("GET", "/api/v1/auth/me", None, "Get Current User (requires auth)"),
        
        # Profiling (new)
        ("POST", "/api/v1/profile/risk-assessment", {"responses": []}, "Risk Assessment"),
        ("GET", "/api/v1/profile/preferences", None, "Trading Preferences"),
        ("GET", "/api/v1/profile/strategy-recommendations", None, "Strategy Recommendations"),
        
        # Webhooks (renamed from tradingview_webhook)
        ("GET", "/api/v1/webhook/test", None, "Webhook Test (requires auth)"),
        
        # Strategies (renamed from backtest)
        ("GET", "/api/v1/strategies", None, "List Strategies"),
        
        # Execution (renamed from trade_controller)
        ("GET", "/api/v1/trading/status", None, "Trading Status"),
        ("GET", "/api/v1/trading/positions", None, "Open Positions"),
        
        # AI Analysis
        ("GET", "/api/v1/ai/health", None, "AI Service Health"),
    ]
    
    # Create results table
    table = Table(title="Endpoint Test Results", show_header=True)
    table.add_column("Method", style="cyan")
    table.add_column("Path", style="blue")
    table.add_column("Status", style="green")
    table.add_column("Description")
    
    async with httpx.AsyncClient() as client:
        for method, path, data, description in endpoints:
            try:
                if method == "GET":
                    response = await client.get(f"{BASE_URL}{path}")
                else:
                    response = await client.post(f"{BASE_URL}{path}", json=data)
                
                status_style = "green" if response.status_code < 400 else "red"
                table.add_row(
                    method,
                    path,
                    f"[{status_style}]{response.status_code}[/{status_style}]",
                    description
                )
            except Exception as e:
                table.add_row(
                    method,
                    path,
                    "[red]ERROR[/red]",
                    f"{description} - {str(e)}"
                )
    
    console.print(table)
    console.print("\n[bold]Legend:[/bold]")
    console.print("✅ 2xx = Success")
    console.print("🔐 401 = Authentication required (expected)")
    console.print("❌ 4xx/5xx = Error")
    console.print("\n[yellow]Note: Some endpoints require authentication, which is expected to fail in this test.[/yellow]")


if __name__ == "__main__":
    console.print("[bold blue]Testing API Endpoints After Restructuring[/bold blue]\n")
    asyncio.run(test_endpoints())