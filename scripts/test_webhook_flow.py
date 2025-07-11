#!/usr/bin/env python3
"""
Test script to demonstrate the complete TradingView webhook flow:
1. Receive webhook signal
2. Process with strategy
3. Run backtest
4. Display results
"""

import asyncio
import json
from datetime import datetime, timedelta
import httpx
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

console = Console()

# Test webhook payloads
WEBHOOK_PAYLOADS = {
    "buy_signal": {
        "strategy": "EMA_Crossover",
        "symbol": "BTCUSDT",
        "signal": "buy",
        "price": 50000.0,
        "quantity": 0.1,
        "stop_loss": 49000.0,
        "take_profit": 52000.0,
        "message": "EMA12 crossed above EMA26",
    },
    "sell_signal": {
        "strategy": "EMA_Crossover",
        "symbol": "BTCUSDT",
        "signal": "sell",
        "price": 51000.0,
        "quantity": 0.1,
        "stop_loss": 52000.0,
        "take_profit": 49000.0,
        "message": "EMA12 crossed below EMA26",
    },
}

# Configuration
BASE_URL = "http://localhost:8000"
WEBHOOK_SECRET = "your-webhook-secret"  # Should match .env


async def test_health_check():
    """Test if the API is running"""
    console.print("\n[bold blue]1. Testing Health Check...[/bold blue]")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/api/v1/health")
            if response.status_code == 200:
                console.print("[green]✓ API is healthy[/green]")
                console.print(f"Response: {response.json()}")
                return True
            else:
                console.print(
                    f"[red]✗ Health check failed: {response.status_code}[/red]"
                )
                return False
        except Exception as e:
            console.print(f"[red]✗ Cannot connect to API: {e}[/red]")
            console.print(
                "[yellow]Make sure the API is running: python main.py[/yellow]"
            )
            return False


async def test_webhook_endpoint(payload: dict):
    """Test sending a webhook signal"""
    console.print(f"\n[bold blue]2. Testing Webhook Endpoint...[/bold blue]")
    console.print(f"Sending {payload['signal']} signal for {payload['symbol']}")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {WEBHOOK_SECRET}",
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{BASE_URL}/api/v1/webhook/tradingview", json=payload, headers=headers
            )

            if response.status_code == 200:
                console.print("[green]✓ Webhook processed successfully[/green]")
                result = response.json()
                console.print(f"Alert ID: {result.get('alert_id')}")
                return True
            else:
                console.print(f"[red]✗ Webhook failed: {response.status_code}[/red]")
                console.print(f"Response: {response.text}")
                return False

        except Exception as e:
            console.print(f"[red]✗ Error sending webhook: {e}[/red]")
            return False


async def test_backtest():
    """Run a backtest with the EMA strategy"""
    console.print("\n[bold blue]3. Running Backtest...[/bold blue]")

    # Prepare backtest request
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)

    backtest_request = {
        "strategy": "EMA_CROSSOVER",
        "symbol": "BTCUSDT",
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "initial_capital": 100000,
        "strategy_params": {
            "fast_ema_period": 12,
            "slow_ema_period": 26,
            "use_volume_filter": True,
        },
    }

    console.print(f"Testing period: {start_date.date()} to {end_date.date()}")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{BASE_URL}/api/v1/backtest",
                json=backtest_request,
                timeout=30.0,  # Longer timeout for backtest
            )

            if response.status_code == 200:
                console.print("[green]✓ Backtest completed successfully[/green]")
                return response.json()
            else:
                console.print(f"[red]✗ Backtest failed: {response.status_code}[/red]")
                console.print(f"Response: {response.text}")
                return None

        except Exception as e:
            console.print(f"[red]✗ Error running backtest: {e}[/red]")
            return None


def display_backtest_results(results: dict):
    """Display backtest results in a nice format"""
    if not results:
        return

    console.print("\n[bold blue]4. Backtest Results[/bold blue]")

    metrics = results.get("metrics", {})

    # Create performance summary table
    table = Table(title="Performance Summary", show_header=True)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Total Trades", str(metrics.get("total_trades", 0)))
    table.add_row("Win Rate", f"{metrics.get('win_rate', 0):.1%}")
    table.add_row("Total Return", f"{metrics.get('total_return', 0):.2%}")
    table.add_row("Sharpe Ratio", f"{metrics.get('sharpe_ratio', 0):.2f}")
    table.add_row("Max Drawdown", f"{metrics.get('max_drawdown', 0):.2%}")
    table.add_row("Profit Factor", f"{metrics.get('profit_factor', 0):.2f}")

    console.print(table)

    # Show recent trades
    trades = results.get("trades", [])
    if trades:
        console.print(f"\n[bold]Last 5 Trades:[/bold]")
        trades_table = Table(show_header=True)
        trades_table.add_column("Entry Time")
        trades_table.add_column("Direction")
        trades_table.add_column("Entry Price")
        trades_table.add_column("Exit Price")
        trades_table.add_column("P&L")
        trades_table.add_column("Return %")

        for trade in trades[-5:]:
            pnl_color = "green" if trade["pnl"] > 0 else "red"
            trades_table.add_row(
                trade["entry_time"].split("T")[0],
                trade["direction"],
                f"${trade['entry_price']:.2f}",
                f"${trade['exit_price']:.2f}",
                f"[{pnl_color}]${trade['pnl']:.2f}[/{pnl_color}]",
                f"[{pnl_color}]{trade['return_pct']:.2f}%[/{pnl_color}]",
            )

        console.print(trades_table)


async def test_ai_analysis(signal_payload: dict):
    """Test AI analysis of a trade signal"""
    console.print("\n[bold blue]5. Testing AI Analysis (Optional)...[/bold blue]")

    analysis_request = {
        "symbol": signal_payload["symbol"],
        "strategy": signal_payload["strategy"],
        "signal_type": signal_payload["signal"],
        "price": signal_payload["price"],
        "quantity": signal_payload.get("quantity"),
        "stop_loss": signal_payload.get("stop_loss"),
        "take_profit": signal_payload.get("take_profit"),
        "market_context": {
            "trend": "upward",
            "volatility": "medium",
            "volume": "average",
        },
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{BASE_URL}/api/v1/ai/analyze-trade",
                json=analysis_request,
                timeout=30.0,
            )

            if response.status_code == 200:
                console.print("[green]✓ AI Analysis completed[/green]")
                result = response.json()

                # Display AI insights
                ai_panel = Panel(
                    f"""[bold]AI Analysis Results[/bold]
                    
Signal Strength: {result.get('signal_strength', 0):.1f}/100
Risk/Reward: {result.get('risk_reward', 0):.2f}
Market Alignment: {result.get('market_alignment', 'Unknown')}
Confidence: {result.get('confidence', 0):.1f}%

[bold]Recommendations:[/bold]
{chr(10).join('• ' + rec for rec in result.get('recommendations', ['No recommendations']))}

[bold]Reasoning:[/bold]
{result.get('reasoning', 'No reasoning provided')}
""",
                    title="Claude AI Analysis",
                    border_style="blue",
                )
                console.print(ai_panel)
                return True
            elif response.status_code == 503:
                console.print(
                    "[yellow]ℹ AI Analysis not available (API key not configured)[/yellow]"
                )
                return False
            else:
                console.print(
                    f"[red]✗ AI Analysis failed: {response.status_code}[/red]"
                )
                return False

        except Exception as e:
            console.print(f"[yellow]ℹ AI Analysis skipped: {e}[/yellow]")
            return False


async def main():
    """Run the complete test flow"""
    console.print(
        Panel.fit(
            "[bold green]TradingView → Webhook → Backtest Flow Test[/bold green]\n"
            "This script tests the complete trading signal flow",
            border_style="green",
        )
    )

    # Step 1: Health check
    if not await test_health_check():
        return

    # Step 2: Test webhook with buy signal
    buy_payload = WEBHOOK_PAYLOADS["buy_signal"]
    await test_webhook_endpoint(buy_payload)

    # Step 3: Run backtest
    backtest_results = await test_backtest()

    # Step 4: Display results
    display_backtest_results(backtest_results)

    # Step 5: Test AI analysis (optional)
    await test_ai_analysis(buy_payload)

    console.print("\n[bold green]✅ Test flow completed![/bold green]")
    console.print("\n[bold]Next Steps:[/bold]")
    console.print("1. Configure a real TradingView alert to send to your webhook")
    console.print("2. Add your exchange API keys to .env")
    console.print("3. Test with paper trading before going live")
    console.print("4. Monitor logs in the 'logs' directory")


if __name__ == "__main__":
    asyncio.run(main())
