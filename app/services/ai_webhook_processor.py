from typing import Dict, Any, Optional
from app.core.logger import LoggerMixin
from app.core.config import settings
from app.models.tradingview import TradingViewAlert, SignalType
from app.services.ai_service import get_ai_service, AIAnalysisError
from app.services.strategies.ai_enhanced_strategy import (
    AIEnhancedStrategy,
    AIEnhancedStrategyParameters,
)


class AIWebhookProcessor(LoggerMixin):
    """
    AI-enhanced webhook processor that analyzes incoming signals
    before execution
    """

    def __init__(self):
        self.ai_service = get_ai_service() if settings.enable_ai_analysis else None

    async def process_webhook_with_ai(
        self, alert: TradingViewAlert, account_balance: float = 100000.0
    ) -> Dict[str, Any]:
        """
        Process webhook signal with AI analysis

        Returns:
            Dict containing:
            - should_execute: bool
            - ai_analysis: Dict with AI insights
            - modified_alert: TradingViewAlert with AI adjustments
            - risk_assessment: Dict with risk metrics
        """

        result = {
            "should_execute": True,
            "ai_analysis": None,
            "modified_alert": alert,
            "risk_assessment": None,
        }

        if not self.ai_service:
            self.log_warning("AI service not available, processing without AI")
            return result

        try:
            # 1. Get AI trade analysis
            market_context = await self._gather_market_context(alert.symbol)
            ai_analysis = await self.ai_service.analyze_trade_signal(
                alert, market_context
            )
            result["ai_analysis"] = ai_analysis

            # 2. Check if AI approves the trade
            ai_confidence = ai_analysis.get("confidence", 0)
            if ai_confidence < 50:  # Below 50% confidence, reject
                result["should_execute"] = False
                self.log_warning(
                    f"AI rejected trade due to low confidence: {ai_confidence}%",
                    symbol=alert.symbol,
                    signal=alert.signal,
                )
                return result

            # 3. Perform risk assessment if we have position details
            if alert.quantity and alert.stop_loss:
                risk_assessment = await self._assess_trade_risk(alert, account_balance)
                result["risk_assessment"] = risk_assessment

                if not risk_assessment.get("approved", False):
                    result["should_execute"] = False
                    self.log_warning(
                        "AI rejected trade due to risk assessment",
                        symbol=alert.symbol,
                        risk_rating=risk_assessment.get("risk_rating"),
                    )
                    return result

            # 4. Apply AI recommendations to modify the alert
            modified_alert = self._apply_ai_recommendations(
                alert, ai_analysis, result.get("risk_assessment")
            )
            result["modified_alert"] = modified_alert

            # 5. Log successful AI processing
            self.log_event(
                "AI webhook processing completed",
                symbol=alert.symbol,
                signal=alert.signal,
                ai_confidence=ai_confidence,
                modifications_made=modified_alert != alert,
            )

        except AIAnalysisError as e:
            self.log_error(f"AI analysis failed: {e}")
            # On AI failure, we can choose to proceed with original signal
            # or reject it based on configuration
            result["should_execute"] = settings.get("allow_trades_without_ai", True)

        return result

    async def _gather_market_context(self, symbol: str) -> Dict[str, Any]:
        """Gather market context for AI analysis"""
        # In production, this would fetch real market data
        # For now, return mock context
        return {
            "market_sentiment": "neutral",
            "volatility": "medium",
            "trend": "upward",
            "volume": "average",
            "news_sentiment": "positive",
            "technical_score": 7.5,
        }

    async def _assess_trade_risk(
        self, alert: TradingViewAlert, account_balance: float
    ) -> Dict[str, Any]:
        """Perform AI risk assessment"""
        if not alert.price or not alert.stop_loss:
            return {"approved": True, "risk_rating": "UNKNOWN"}

        position_value = alert.quantity * alert.price
        stop_loss_distance = abs(alert.price - alert.stop_loss)

        assessment = await self.ai_service.assess_risk_parameters(
            position_size=position_value,
            stop_loss=stop_loss_distance,
            take_profit=abs(alert.take_profit - alert.price)
            if alert.take_profit
            else stop_loss_distance * 2,
            account_balance=account_balance,
            symbol_volatility=alert.price * 0.02,  # Mock 2% volatility
        )

        return assessment

    def _apply_ai_recommendations(
        self,
        alert: TradingViewAlert,
        ai_analysis: Dict[str, Any],
        risk_assessment: Optional[Dict[str, Any]],
    ) -> TradingViewAlert:
        """Apply AI recommendations to modify the alert"""
        modified_alert = alert.copy()

        recommendations = ai_analysis.get("recommendations", [])

        for rec in recommendations:
            rec_lower = rec.lower()

            # Adjust position size
            if "reduce position" in rec_lower and modified_alert.quantity:
                reduction_factor = 0.8  # Reduce by 20%
                modified_alert.quantity *= reduction_factor
                self.log_event("AI reduced position size", factor=reduction_factor)

            # Tighten stop loss
            elif "tighten stop" in rec_lower and modified_alert.stop_loss:
                if modified_alert.signal == SignalType.BUY:
                    # Move stop loss closer (reduce risk)
                    distance = modified_alert.price - modified_alert.stop_loss
                    modified_alert.stop_loss = modified_alert.price - (distance * 0.8)
                elif modified_alert.signal == SignalType.SELL:
                    distance = modified_alert.stop_loss - modified_alert.price
                    modified_alert.stop_loss = modified_alert.price + (distance * 0.8)
                self.log_event("AI tightened stop loss")

            # Adjust take profit
            elif "extend target" in rec_lower and modified_alert.take_profit:
                if modified_alert.signal == SignalType.BUY:
                    distance = modified_alert.take_profit - modified_alert.price
                    modified_alert.take_profit = modified_alert.price + (distance * 1.2)
                elif modified_alert.signal == SignalType.SELL:
                    distance = modified_alert.price - modified_alert.take_profit
                    modified_alert.take_profit = modified_alert.price - (distance * 1.2)
                self.log_event("AI extended take profit target")

        # Apply risk assessment modifications
        if risk_assessment and risk_assessment.get("risk_rating") == "HIGH":
            if modified_alert.quantity:
                modified_alert.quantity *= 0.5  # Halve position for high risk
                self.log_event("AI halved position due to high risk")

        # Add AI metadata
        if not modified_alert.metadata:
            modified_alert.metadata = {}

        modified_alert.metadata["ai_processed"] = True
        modified_alert.metadata["ai_confidence"] = ai_analysis.get("confidence")
        modified_alert.metadata["ai_modifications"] = recommendations

        return modified_alert


# Global processor instance
ai_webhook_processor = None


def get_ai_webhook_processor() -> AIWebhookProcessor:
    """Get or create AI webhook processor instance"""
    global ai_webhook_processor
    if ai_webhook_processor is None:
        ai_webhook_processor = AIWebhookProcessor()
    return ai_webhook_processor
