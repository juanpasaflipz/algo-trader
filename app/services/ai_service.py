from typing import Dict, Any, List, Optional
from datetime import datetime
import json
from anthropic import Anthropic
from app.core.config import settings
from app.core.logger import LoggerMixin
from app.core.errors import AlgoTraderError
from app.models.backtest import BacktestResult, BacktestMetrics
from app.models.tradingview import TradingViewAlert
import pandas as pd


class AIAnalysisError(AlgoTraderError):
    """Raised when AI analysis fails"""
    pass


class AIService(LoggerMixin):
    """Service for AI-powered trading analysis using Claude"""
    
    def __init__(self):
        if not settings.anthropic_api_key:
            raise AIAnalysisError("Anthropic API key not configured")
        
        self.client = Anthropic(api_key=settings.anthropic_api_key)
        self.model = settings.claude_model
        
    async def analyze_trade_signal(
        self,
        alert: TradingViewAlert,
        market_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Analyze a trading signal and provide recommendations"""
        
        try:
            prompt = f"""You are an expert algorithmic trading analyst. Analyze this trading signal and provide recommendations.

Trading Signal:
- Strategy: {alert.strategy}
- Symbol: {alert.symbol}
- Signal: {alert.signal}
- Price: {alert.price}
- Quantity: {alert.quantity}
- Stop Loss: {alert.stop_loss}
- Take Profit: {alert.take_profit}

{f"Market Context: {json.dumps(market_context, indent=2)}" if market_context else ""}

Please analyze:
1. Signal validity and strength
2. Risk/reward ratio
3. Market conditions alignment
4. Recommended adjustments (if any)
5. Confidence level (0-100%)

Provide your analysis in JSON format with keys: signal_strength, risk_reward, market_alignment, recommendations, confidence, reasoning."""

            response = self.client.messages.create(
                model=self.model,
                max_tokens=settings.ai_max_tokens,
                temperature=settings.ai_temperature,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Extract JSON from response
            analysis = self._parse_json_response(response.content[0].text)
            
            self.log_event(
                "AI trade signal analysis completed",
                symbol=alert.symbol,
                confidence=analysis.get("confidence", 0)
            )
            
            return analysis
            
        except Exception as e:
            self.log_error(f"AI analysis failed: {str(e)}")
            raise AIAnalysisError(f"Failed to analyze trade signal: {str(e)}")
    
    async def analyze_backtest_results(
        self,
        backtest_result: BacktestResult
    ) -> Dict[str, Any]:
        """Provide AI-powered insights on backtest results"""
        
        try:
            metrics = backtest_result.metrics
            prompt = f"""You are an expert quantitative analyst. Analyze these backtest results and provide insights.

Strategy: {backtest_result.strategy}
Symbol: {backtest_result.symbol}
Period: {backtest_result.start_date} to {backtest_result.end_date}

Performance Metrics:
- Total Return: {metrics.total_return:.2%}
- Win Rate: {metrics.win_rate:.2%}
- Sharpe Ratio: {metrics.sharpe_ratio:.2f}
- Max Drawdown: {metrics.max_drawdown:.2%}
- Total Trades: {metrics.total_trades}
- Profit Factor: {metrics.profit_factor:.2f}
- Average Trade Duration: {metrics.average_trade_duration:.1f} hours

Please provide:
1. Overall strategy assessment
2. Strengths and weaknesses
3. Risk analysis
4. Suggestions for improvement
5. Market conditions where this strategy would excel/fail
6. Recommended parameter adjustments

Format your response as JSON with keys: assessment, strengths, weaknesses, risk_analysis, improvements, market_conditions, parameter_suggestions."""

            response = self.client.messages.create(
                model=self.model,
                max_tokens=settings.ai_max_tokens,
                temperature=settings.ai_temperature,
                messages=[{"role": "user", "content": prompt}]
            )
            
            analysis = self._parse_json_response(response.content[0].text)
            
            self.log_event(
                "AI backtest analysis completed",
                strategy=backtest_result.strategy,
                total_return=metrics.total_return
            )
            
            return analysis
            
        except Exception as e:
            self.log_error(f"Backtest analysis failed: {str(e)}")
            raise AIAnalysisError(f"Failed to analyze backtest results: {str(e)}")
    
    async def generate_market_commentary(
        self,
        symbol: str,
        timeframe: str,
        price_data: pd.DataFrame,
        indicators: Dict[str, Any]
    ) -> str:
        """Generate human-readable market commentary"""
        
        try:
            # Prepare data summary
            current_price = price_data['close'].iloc[-1]
            price_change = (price_data['close'].iloc[-1] / price_data['close'].iloc[-2] - 1) * 100
            
            prompt = f"""You are a professional market analyst. Generate a concise market commentary for traders.

Symbol: {symbol}
Timeframe: {timeframe}
Current Price: ${current_price:.2f}
24h Change: {price_change:.2f}%

Technical Indicators:
{json.dumps(indicators, indent=2)}

Recent Price Action:
- High (24h): ${price_data['high'].tail(24).max():.2f}
- Low (24h): ${price_data['low'].tail(24).min():.2f}
- Volume (24h avg): {price_data['volume'].tail(24).mean():.0f}

Generate a 2-3 paragraph commentary covering:
1. Current market structure and trend
2. Key technical levels to watch
3. Potential trading opportunities or risks

Keep it professional, actionable, and under 200 words."""

            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.content[0].text
            
        except Exception as e:
            self.log_error(f"Market commentary generation failed: {str(e)}")
            return f"Unable to generate market commentary: {str(e)}"
    
    async def assess_risk_parameters(
        self,
        position_size: float,
        stop_loss: float,
        take_profit: float,
        account_balance: float,
        symbol_volatility: float
    ) -> Dict[str, Any]:
        """AI-powered risk assessment for a potential trade"""
        
        try:
            risk_amount = position_size * stop_loss
            risk_percentage = (risk_amount / account_balance) * 100
            reward_amount = position_size * take_profit
            risk_reward_ratio = reward_amount / risk_amount if risk_amount > 0 else 0
            
            prompt = f"""You are a risk management expert. Assess the risk parameters for this trade.

Trade Parameters:
- Position Size: ${position_size:.2f}
- Stop Loss: ${stop_loss:.2f}
- Take Profit: ${take_profit:.2f}
- Account Balance: ${account_balance:.2f}
- Risk Amount: ${risk_amount:.2f} ({risk_percentage:.1f}% of account)
- Risk/Reward Ratio: {risk_reward_ratio:.2f}
- Symbol Volatility (ATR): {symbol_volatility:.2f}

Assess:
1. Is the position size appropriate?
2. Are the stop loss and take profit levels reasonable?
3. Overall risk rating (LOW/MEDIUM/HIGH)
4. Recommendations for adjustment

Provide response as JSON with keys: position_size_assessment, stop_loss_assessment, take_profit_assessment, risk_rating, recommendations, approved (boolean)."""

            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                temperature=0.3,  # Lower temperature for risk assessment
                messages=[{"role": "user", "content": prompt}]
            )
            
            assessment = self._parse_json_response(response.content[0].text)
            
            self.log_event(
                "AI risk assessment completed",
                risk_rating=assessment.get("risk_rating", "UNKNOWN"),
                approved=assessment.get("approved", False)
            )
            
            return assessment
            
        except Exception as e:
            self.log_error(f"Risk assessment failed: {str(e)}")
            raise AIAnalysisError(f"Failed to assess risk parameters: {str(e)}")
    
    async def optimize_strategy_parameters(
        self,
        strategy_name: str,
        current_params: Dict[str, Any],
        recent_performance: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Suggest parameter optimizations based on recent performance"""
        
        try:
            prompt = f"""You are a quantitative strategy optimization expert. Suggest parameter adjustments for better performance.

Strategy: {strategy_name}
Current Parameters: {json.dumps(current_params, indent=2)}

Recent Performance (last 10 trades):
{json.dumps(recent_performance, indent=2)}

Based on the performance data:
1. Identify patterns in winning vs losing trades
2. Suggest parameter adjustments
3. Explain the reasoning
4. Estimate potential improvement

Provide response as JSON with keys: pattern_analysis, suggested_parameters, reasoning, expected_improvement_percent."""

            response = self.client.messages.create(
                model=self.model,
                max_tokens=settings.ai_max_tokens,
                temperature=0.5,
                messages=[{"role": "user", "content": prompt}]
            )
            
            optimization = self._parse_json_response(response.content[0].text)
            
            return optimization
            
        except Exception as e:
            self.log_error(f"Strategy optimization failed: {str(e)}")
            raise AIAnalysisError(f"Failed to optimize strategy parameters: {str(e)}")
    
    def _parse_json_response(self, text: str) -> Dict[str, Any]:
        """Parse JSON from Claude's response"""
        try:
            # Try to find JSON in the response
            import re
            json_match = re.search(r'\{[\s\S]*\}', text)
            if json_match:
                return json.loads(json_match.group())
            else:
                # If no JSON found, try to parse the entire response
                return json.loads(text)
        except json.JSONDecodeError:
            self.log_warning("Failed to parse JSON from AI response")
            # Return a structured response even if parsing fails
            return {
                "error": "Failed to parse AI response",
                "raw_response": text[:500]  # First 500 chars
            }


# Global AI service instance
ai_service = None

def get_ai_service() -> AIService:
    """Get or create AI service instance"""
    global ai_service
    if ai_service is None and settings.enable_ai_analysis:
        ai_service = AIService()
    return ai_service