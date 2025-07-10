from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt
from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)
security = HTTPBearer()


async def get_db() -> Generator:
    """Database session dependency"""
    # TODO: Implement when database is set up
    pass


def verify_webhook_token(token: str) -> bool:
    """Verify TradingView webhook token"""
    return token == settings.tradingview_webhook_secret


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """Verify JWT token and return current user"""
    token = credentials.credentials
    
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=["HS256"]
        )
        return payload
    except JWTError:
        logger.warning("Invalid authentication token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def verify_webhook_auth(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> bool:
    """Verify webhook authentication"""
    token = credentials.credentials
    
    if not verify_webhook_token(token):
        logger.warning("Invalid webhook token attempt")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook authentication",
        )
    
    return True