import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Type
import pandas as pd
import numpy as np
from app.core.logger import LoggerMixin, trading_logger
from app.core.telemetry import metrics, log_execution_time
from app.core.errors import BacktestError, DataError
from app.models.backtest import (
    BacktestRequest,
    BacktestResult,
    BacktestMetrics,
    BacktestStatus,
    TradeRecord,
)
from app.services.strategies.base import BaseStrategy, TradingSignal, SignalDirection
from app.services.strategies.ema_crossover import (
    EMACrossoverStrategy,
    EMACrossoverParameters,
)


class Backtester(LoggerMixin):
    """Main backtesting engine"""

    # Strategy registry
    STRATEGIES: Dict[str, Type[BaseStrategy]] = {
        "EMA_CROSSOVER": EMACrossoverStrategy,
        "AI_ENHANCED": "app.services.strategies.ai_enhanced_strategy.AIEnhancedStrategy",
    }

    def __init__(self):
        self.active_backtests: Dict[str, BacktestResult] = {}

    @log_execution_time()
    async def run_backtest(self, request: BacktestRequest) -> BacktestResult:
        """Execute a backtest based on the request"""
        backtest_id = str(uuid.uuid4())

        # Create initial result
        result = BacktestResult(
            id=backtest_id,
            status=BacktestStatus.RUNNING,
            strategy=request.strategy,
            symbol=request.symbol,
            start_date=request.start_date,
            end_date=request.end_date,
            initial_capital=request.initial_capital,
            final_capital=request.initial_capital,
            metrics=self._empty_metrics(),
            trades=[],
        )

        self.active_backtests[backtest_id] = result

        try:
            # Load historical data
            data = await self._load_historical_data(
                request.symbol, request.start_date, request.end_date
            )

            # Initialize strategy
            strategy = self._create_strategy(request)

            # Run backtest
            backtest_results = self._execute_backtest(
                strategy=strategy,
                data=data,
                initial_capital=request.initial_capital,
                commission=request.commission,
                position_size_pct=request.position_size_pct,
                stop_loss_pct=request.stop_loss_pct,
            )

            # Calculate metrics
            metrics = self._calculate_metrics(
                trades=backtest_results["trades"],
                equity_curve=backtest_results["equity_curve"],
                initial_capital=request.initial_capital,
            )

            # Update result
            result.status = BacktestStatus.COMPLETED
            result.final_capital = backtest_results["final_capital"]
            result.metrics = metrics
            result.trades = [
                self._convert_trade_to_record(t) for t in backtest_results["trades"]
            ]
            result.equity_curve = backtest_results["equity_curve"]
            result.drawdown_curve = backtest_results["drawdown_curve"]
            result.completed_at = datetime.utcnow()

            # Log completion
            trading_logger.log_backtest_result(
                strategy=request.strategy, metrics=metrics.dict()
            )

        except Exception as e:
            self.log_error(f"Backtest failed: {str(e)}")
            result.status = BacktestStatus.FAILED
            result.error_message = str(e)
            result.completed_at = datetime.utcnow()

        return result

    def _create_strategy(self, request: BacktestRequest) -> BaseStrategy:
        """Create strategy instance from request"""
        strategy_entry = self.STRATEGIES.get(request.strategy.upper())

        if not strategy_entry:
            raise BacktestError(f"Unknown strategy: {request.strategy}")

        # Handle string imports for AI strategies
        if isinstance(strategy_entry, str):
            module_path, class_name = strategy_entry.rsplit(".", 1)
            module = __import__(module_path, fromlist=[class_name])
            strategy_class = getattr(module, class_name)
        else:
            strategy_class = strategy_entry

        # Create parameters based on strategy type
        if request.strategy.upper() == "EMA_CROSSOVER":
            params = EMACrossoverParameters(
                symbol=request.symbol,
                timeframe="1h",  # TODO: Make configurable
                lookback_period=100,
                **request.strategy_params,
            )
            return EMACrossoverStrategy(params)
        elif request.strategy.upper() == "AI_ENHANCED":
            from app.services.strategies.ai_enhanced_strategy import (
                AIEnhancedStrategy,
                AIEnhancedStrategyParameters,
            )

            params = AIEnhancedStrategyParameters(
                symbol=request.symbol,
                timeframe="1h",
                lookback_period=100,
                base_strategy="EMA_CROSSOVER",
                base_strategy_params=request.strategy_params.get(
                    "base_strategy_params", {}
                ),
                ai_confidence_threshold=request.strategy_params.get(
                    "ai_confidence_threshold", 70.0
                ),
                use_ai_risk_assessment=request.strategy_params.get(
                    "use_ai_risk_assessment", True
                ),
                ai_weight=request.strategy_params.get("ai_weight", 0.5),
            )
            return AIEnhancedStrategy(params)

        raise BacktestError(f"Strategy {request.strategy} not properly configured")

    async def _load_historical_data(
        self, symbol: str, start_date: datetime, end_date: datetime
    ) -> pd.DataFrame:
        """Load historical OHLCV data"""
        # TODO: Implement actual data loading from database or API
        # For now, generate synthetic data for testing

        dates = pd.date_range(start=start_date, end=end_date, freq="1h")

        # Generate synthetic price data
        np.random.seed(42)  # For reproducibility
        returns = np.random.normal(0.0001, 0.02, len(dates))
        prices = 100 * np.exp(np.cumsum(returns))

        data = pd.DataFrame(
            {
                "open": prices * (1 + np.random.uniform(-0.001, 0.001, len(dates))),
                "high": prices * (1 + np.random.uniform(0, 0.01, len(dates))),
                "low": prices * (1 - np.random.uniform(0, 0.01, len(dates))),
                "close": prices,
                "volume": np.random.uniform(1000, 10000, len(dates)),
            },
            index=dates,
        )

        # Ensure high is highest and low is lowest
        data["high"] = data[["open", "high", "close"]].max(axis=1)
        data["low"] = data[["open", "low", "close"]].min(axis=1)

        return data

    def _execute_backtest(
        self,
        strategy: BaseStrategy,
        data: pd.DataFrame,
        initial_capital: float,
        commission: float,
        position_size_pct: float,
        stop_loss_pct: Optional[float],
    ) -> Dict[str, Any]:
        """Execute the backtest logic"""
        # Initialize tracking variables
        capital = initial_capital
        position = None
        trades = []
        equity_curve = []

        # Calculate indicators once
        data = strategy.calculate_indicators(data)

        # Get required lookback
        lookback = strategy.get_required_lookback()

        # Iterate through data
        for i in range(lookback, len(data)):
            current_time = data.index[i]
            current_price = data.iloc[i]["close"]

            # Track equity
            current_equity = capital
            if position:
                unrealized_pnl = position["quantity"] * (
                    current_price - position["entry_price"]
                )
                current_equity += unrealized_pnl

            equity_curve.append({"timestamp": current_time, "equity": current_equity})

            # Check stop loss if in position
            if position and stop_loss_pct:
                if position["direction"] == "long":
                    stop_price = position["entry_price"] * (1 - stop_loss_pct / 100)
                    if current_price <= stop_price:
                        # Exit on stop loss
                        exit_value = position["quantity"] * current_price
                        commission_cost = exit_value * commission
                        capital += exit_value - commission_cost

                        trades.append(
                            {
                                "entry_time": position["entry_time"],
                                "exit_time": current_time,
                                "symbol": strategy.parameters.symbol,
                                "direction": position["direction"],
                                "entry_price": position["entry_price"],
                                "exit_price": current_price,
                                "quantity": position["quantity"],
                                "commission": position["entry_commission"]
                                + commission_cost,
                                "exit_reason": "stop_loss",
                            }
                        )

                        position = None
                        continue

            # Generate signal
            signal = strategy.generate_signals(data.iloc[: i + 1])

            if signal:
                if signal.direction == SignalDirection.LONG and not position:
                    # Enter long position
                    position_value = capital * (position_size_pct / 100)
                    quantity = position_value / current_price
                    commission_cost = position_value * commission

                    if commission_cost < capital:
                        capital -= position_value + commission_cost
                        position = {
                            "entry_time": current_time,
                            "entry_price": current_price,
                            "quantity": quantity,
                            "direction": "long",
                            "entry_commission": commission_cost,
                        }

                elif signal.direction == SignalDirection.NEUTRAL and position:
                    # Exit position
                    exit_value = position["quantity"] * current_price
                    commission_cost = exit_value * commission
                    capital += exit_value - commission_cost

                    trades.append(
                        {
                            "entry_time": position["entry_time"],
                            "exit_time": current_time,
                            "symbol": strategy.parameters.symbol,
                            "direction": position["direction"],
                            "entry_price": position["entry_price"],
                            "exit_price": current_price,
                            "quantity": position["quantity"],
                            "commission": position["entry_commission"]
                            + commission_cost,
                            "exit_reason": "signal",
                        }
                    )

                    position = None

        # Close any remaining position
        if position:
            final_price = data.iloc[-1]["close"]
            exit_value = position["quantity"] * final_price
            commission_cost = exit_value * commission
            capital += exit_value - commission_cost

            trades.append(
                {
                    "entry_time": position["entry_time"],
                    "exit_time": data.index[-1],
                    "symbol": strategy.parameters.symbol,
                    "direction": position["direction"],
                    "entry_price": position["entry_price"],
                    "exit_price": final_price,
                    "quantity": position["quantity"],
                    "commission": position["entry_commission"] + commission_cost,
                    "exit_reason": "end_of_data",
                }
            )

        # Calculate drawdown curve
        equity_df = pd.DataFrame(equity_curve)
        equity_df["peak"] = equity_df["equity"].cummax()
        equity_df["drawdown"] = (equity_df["equity"] - equity_df["peak"]) / equity_df[
            "peak"
        ]

        drawdown_curve = equity_df[["timestamp", "drawdown"]].to_dict("records")

        # Add PnL to trades
        for trade in trades:
            if trade["direction"] == "long":
                trade["pnl"] = (
                    trade["quantity"] * (trade["exit_price"] - trade["entry_price"])
                    - trade["commission"]
                )
            else:
                trade["pnl"] = (
                    trade["quantity"] * (trade["entry_price"] - trade["exit_price"])
                    - trade["commission"]
                )

            trade["return_pct"] = (
                trade["pnl"] / (trade["quantity"] * trade["entry_price"]) * 100
            )

        return {
            "final_capital": capital,
            "trades": trades,
            "equity_curve": equity_curve,
            "drawdown_curve": drawdown_curve,
        }

    def _calculate_metrics(
        self,
        trades: List[Dict[str, Any]],
        equity_curve: List[Dict[str, Any]],
        initial_capital: float,
    ) -> BacktestMetrics:
        """Calculate performance metrics from trades"""
        if not trades:
            return self._empty_metrics()

        # Convert to DataFrame for easier calculation
        trades_df = pd.DataFrame(trades)
        equity_df = pd.DataFrame(equity_curve)

        # Basic metrics
        total_trades = len(trades)
        winning_trades = len(trades_df[trades_df["pnl"] > 0])
        losing_trades = len(trades_df[trades_df["pnl"] < 0])
        win_rate = winning_trades / total_trades if total_trades > 0 else 0

        # Returns
        total_return = (
            equity_df["equity"].iloc[-1] - initial_capital
        ) / initial_capital
        days = (equity_df["timestamp"].iloc[-1] - equity_df["timestamp"].iloc[0]).days
        annualized_return = (
            (1 + total_return) ** (365 / max(days, 1)) - 1 if days > 0 else 0
        )
        average_trade_return = trades_df["return_pct"].mean() / 100

        # Risk metrics
        equity_df["returns"] = equity_df["equity"].pct_change()

        # Maximum drawdown
        equity_df["peak"] = equity_df["equity"].cummax()
        equity_df["drawdown"] = (equity_df["equity"] - equity_df["peak"]) / equity_df[
            "peak"
        ]
        max_drawdown = equity_df["drawdown"].min()

        # Sharpe ratio (assuming 0% risk-free rate)
        if equity_df["returns"].std() > 0:
            sharpe_ratio = (
                np.sqrt(252) * equity_df["returns"].mean() / equity_df["returns"].std()
            )
        else:
            sharpe_ratio = 0

        # Sortino ratio
        negative_returns = equity_df["returns"][equity_df["returns"] < 0]
        if len(negative_returns) > 0 and negative_returns.std() > 0:
            sortino_ratio = (
                np.sqrt(252) * equity_df["returns"].mean() / negative_returns.std()
            )
        else:
            sortino_ratio = 0

        # Calmar ratio
        calmar_ratio = annualized_return / abs(max_drawdown) if max_drawdown != 0 else 0

        # Win/loss metrics
        winning_pnls = trades_df[trades_df["pnl"] > 0]["pnl"]
        losing_pnls = trades_df[trades_df["pnl"] < 0]["pnl"]

        average_win = winning_pnls.mean() if len(winning_pnls) > 0 else 0
        average_loss = losing_pnls.mean() if len(losing_pnls) > 0 else 0
        largest_win = winning_pnls.max() if len(winning_pnls) > 0 else 0
        largest_loss = losing_pnls.min() if len(losing_pnls) > 0 else 0

        # Profit factor
        gross_profit = winning_pnls.sum() if len(winning_pnls) > 0 else 0
        gross_loss = abs(losing_pnls.sum()) if len(losing_pnls) > 0 else 0
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0

        # Time metrics
        trades_df["duration"] = pd.to_datetime(trades_df["exit_time"]) - pd.to_datetime(
            trades_df["entry_time"]
        )
        average_trade_duration = (
            trades_df["duration"].mean().total_seconds() / 3600
        )  # in hours

        # Market exposure
        total_time = (
            equity_df["timestamp"].iloc[-1] - equity_df["timestamp"].iloc[0]
        ).total_seconds()
        time_in_market = trades_df["duration"].sum().total_seconds()
        total_market_exposure = time_in_market / total_time if total_time > 0 else 0

        return BacktestMetrics(
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            win_rate=win_rate,
            total_return=total_return,
            annualized_return=annualized_return,
            average_trade_return=average_trade_return,
            max_drawdown=max_drawdown,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            calmar_ratio=calmar_ratio,
            profit_factor=profit_factor,
            average_win=average_win,
            average_loss=average_loss,
            largest_win=largest_win,
            largest_loss=largest_loss,
            average_trade_duration=average_trade_duration,
            total_market_exposure=total_market_exposure,
        )

    def _convert_trade_to_record(self, trade: Dict[str, Any]) -> TradeRecord:
        """Convert internal trade dict to TradeRecord model"""
        return TradeRecord(
            entry_time=trade["entry_time"],
            exit_time=trade["exit_time"],
            symbol=trade["symbol"],
            direction=trade["direction"],
            entry_price=trade["entry_price"],
            exit_price=trade["exit_price"],
            quantity=trade["quantity"],
            commission=trade["commission"],
            pnl=trade["pnl"],
            return_pct=trade["return_pct"],
        )

    def _empty_metrics(self) -> BacktestMetrics:
        """Return empty metrics object"""
        return BacktestMetrics(
            total_trades=0,
            winning_trades=0,
            losing_trades=0,
            win_rate=0,
            total_return=0,
            annualized_return=0,
            average_trade_return=0,
            max_drawdown=0,
            sharpe_ratio=0,
            sortino_ratio=0,
            calmar_ratio=0,
            profit_factor=0,
            average_win=0,
            average_loss=0,
            largest_win=0,
            largest_loss=0,
            average_trade_duration=0,
            total_market_exposure=0,
        )


    async def run_backtest_async(
        self, 
        request: BacktestRequest,
        progress_callback=None
    ) -> BacktestResult:
        """
        Async version of run_backtest with progress callback support.
        
        Args:
            request: Backtest request parameters
            progress_callback: Optional callback function(progress: int, message: str)
        
        Returns:
            BacktestResult with performance metrics
        """
        # This is a wrapper that adds progress callback support
        if progress_callback:
            progress_callback(0, "Loading historical data...")
        
        # Run the synchronous backtest
        # In a real implementation, this would be properly async
        result = self.run_backtest(request)
        
        if progress_callback:
            progress_callback(100, "Backtest completed")
        
        return result


# Create a singleton instance
backtester = Backtester()
