from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, validator


class Settings(BaseSettings):
    # Application
    app_name: str = Field(default="Algo Trader")
    app_version: str = Field(default="0.1.0")
    environment: str = Field(default="development")
    debug: bool = Field(default=True)
    log_level: str = Field(default="INFO")

    # API Configuration
    api_v1_prefix: str = Field(default="/api/v1")
    allowed_hosts: List[str] = Field(default=["localhost", "127.0.0.1"])
    secret_key: str = Field(..., description="Secret key for JWT encoding")

    # Database
    database_url: str = Field(..., description="PostgreSQL connection URL")
    redis_url: str = Field(default="redis://localhost:6379")

    # TradingView
    tradingview_webhook_secret: str = Field(
        ..., description="Secret for webhook authentication"
    )

    # Binance
    binance_api_key: Optional[str] = Field(default=None)
    binance_api_secret: Optional[str] = Field(default=None)
    binance_testnet: bool = Field(default=True)

    # Interactive Brokers
    ibkr_host: str = Field(default="127.0.0.1")
    ibkr_port: int = Field(default=7497)  # 7497 for paper, 7496 for live
    ibkr_client_id: int = Field(default=1)

    # Alpaca
    alpaca_api_key: Optional[str] = Field(default=None)
    alpaca_secret_key: Optional[str] = Field(default=None)
    alpaca_base_url: str = Field(default="https://paper-api.alpaca.markets")

    # Risk Management
    max_position_size_percent: float = Field(default=2.0, ge=0.1, le=10.0)
    default_stop_loss_percent: float = Field(default=1.0, ge=0.1, le=5.0)
    max_daily_trades: int = Field(default=10, ge=1, le=100)

    # Backtesting
    backtest_start_date: str = Field(default="2022-01-01")
    backtest_end_date: str = Field(default="2023-12-31")
    backtest_initial_capital: float = Field(default=100000.0, ge=1000.0)
    backtest_commission: float = Field(default=0.001, ge=0.0, le=0.01)

    # Monitoring
    enable_metrics: bool = Field(default=True)
    metrics_port: int = Field(default=9090)

    # AI Configuration
    anthropic_api_key: Optional[str] = Field(default=None)
    claude_model: str = Field(default="claude-3-5-sonnet-20241022")
    ai_max_tokens: int = Field(default=4096)
    ai_temperature: float = Field(default=0.7, ge=0.0, le=1.0)
    enable_ai_analysis: bool = Field(default=True)

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False
    )

    @validator("environment")
    def validate_environment(cls, v):
        allowed = ["development", "staging", "production"]
        if v not in allowed:
            raise ValueError(f"environment must be one of {allowed}")
        return v

    @validator("log_level")
    def validate_log_level(cls, v):
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v = v.upper()
        if v not in allowed:
            raise ValueError(f"log_level must be one of {allowed}")
        return v

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        return self.environment == "development"

    @property
    def binance_base_url(self) -> str:
        if self.binance_testnet:
            return "https://testnet.binance.vision"
        return "https://api.binance.com"

    @property
    def database_url_sync(self) -> str:
        """Return synchronous database URL for Alembic"""
        return self.database_url.replace("postgresql+asyncpg://", "postgresql://")


# Global settings instance
settings = Settings()
