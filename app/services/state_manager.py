"""Unified state management service following LEVER principles.

OPTIMIZATION: Consolidates state management for strategies, backtests, and positions
into a single service. Reduces code duplication and improves consistency.
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
from app.core.logger import get_logger
from app.models.base import BaseTradingSignal
import asyncio
import json


logger = get_logger(__name__)


class StateType(str, Enum):
    """Types of state that can be managed."""

    STRATEGY = "strategy"
    BACKTEST = "backtest"
    POSITION = "position"
    SIGNAL = "signal"


@dataclass
class StateEntry:
    """Generic state entry that can represent any stateful object."""

    id: str
    type: StateType
    data: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def update(self, data: Dict[str, Any]) -> None:
        """Update state data and timestamp."""
        self.data.update(data)
        self.updated_at = datetime.utcnow()


class StateManager:
    """
    Unified state management service.

    OPTIMIZATION: Single service replaces multiple in-memory dictionaries
    scattered across different services. Provides consistent interface
    for all state management needs.
    """

    def __init__(self):
        self._state: Dict[StateType, Dict[str, StateEntry]] = {
            state_type: {} for state_type in StateType
        }
        self._lock = asyncio.Lock()
        self._listeners: Dict[StateType, List[callable]] = {
            state_type: [] for state_type in StateType
        }

    async def create(
        self,
        state_type: StateType,
        id: str,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> StateEntry:
        """Create a new state entry."""
        async with self._lock:
            if id in self._state[state_type]:
                raise ValueError(f"{state_type} with id {id} already exists")

            entry = StateEntry(
                id=id, type=state_type, data=data, metadata=metadata or {}
            )

            self._state[state_type][id] = entry
            await self._notify_listeners(state_type, "create", entry)

            logger.info(f"Created {state_type} state: {id}")
            return entry

    async def update(
        self, state_type: StateType, id: str, data: Dict[str, Any]
    ) -> Optional[StateEntry]:
        """Update an existing state entry."""
        async with self._lock:
            entry = self._state[state_type].get(id)
            if not entry:
                logger.warning(f"{state_type} with id {id} not found")
                return None

            entry.update(data)
            await self._notify_listeners(state_type, "update", entry)

            logger.debug(f"Updated {state_type} state: {id}")
            return entry

    async def get(self, state_type: StateType, id: str) -> Optional[StateEntry]:
        """Get a state entry by ID."""
        async with self._lock:
            return self._state[state_type].get(id)

    async def get_all(
        self, state_type: StateType, filter_func: Optional[callable] = None
    ) -> List[StateEntry]:
        """Get all state entries of a type, optionally filtered."""
        async with self._lock:
            entries = list(self._state[state_type].values())

            if filter_func:
                entries = [e for e in entries if filter_func(e)]

            return entries

    async def delete(self, state_type: StateType, id: str) -> bool:
        """Delete a state entry."""
        async with self._lock:
            if id not in self._state[state_type]:
                return False

            entry = self._state[state_type].pop(id)
            await self._notify_listeners(state_type, "delete", entry)

            logger.info(f"Deleted {state_type} state: {id}")
            return True

    async def clear(self, state_type: StateType) -> int:
        """Clear all entries of a specific type."""
        async with self._lock:
            count = len(self._state[state_type])
            self._state[state_type].clear()

            logger.info(f"Cleared {count} {state_type} entries")
            return count

    def subscribe(self, state_type: StateType, callback: callable) -> callable:
        """Subscribe to state changes. Returns unsubscribe function."""
        self._listeners[state_type].append(callback)

        def unsubscribe():
            if callback in self._listeners[state_type]:
                self._listeners[state_type].remove(callback)

        return unsubscribe

    async def _notify_listeners(
        self, state_type: StateType, action: str, entry: StateEntry
    ):
        """Notify all listeners of state changes."""
        for listener in self._listeners[state_type]:
            try:
                await listener(action, entry)
            except Exception as e:
                logger.error(f"Error notifying listener: {e}")

    # Convenience methods for specific state types

    async def create_position(
        self, symbol: str, signal: BaseTradingSignal, **kwargs
    ) -> StateEntry:
        """Create a position from a trading signal."""
        position_id = f"{symbol}_{datetime.utcnow().timestamp()}"

        position_data = {
            "symbol": symbol,
            "side": signal.signal,
            "entry_price": signal.price,
            "quantity": signal.quantity,
            "stop_loss": signal.stop_loss,
            "take_profit": signal.take_profit,
            "status": "open",
            **kwargs,
        }

        return await self.create(StateType.POSITION, position_id, position_data)

    async def get_open_positions(
        self, symbol: Optional[str] = None
    ) -> List[StateEntry]:
        """Get all open positions, optionally filtered by symbol."""

        def filter_open(entry: StateEntry) -> bool:
            is_open = entry.data.get("status") == "open"
            if symbol:
                return is_open and entry.data.get("symbol") == symbol
            return is_open

        return await self.get_all(StateType.POSITION, filter_open)

    async def update_strategy_state(
        self, strategy_name: str, state_data: Dict[str, Any]
    ) -> StateEntry:
        """Update or create strategy state."""
        existing = await self.get(StateType.STRATEGY, strategy_name)

        if existing:
            return await self.update(StateType.STRATEGY, strategy_name, state_data)
        else:
            return await self.create(StateType.STRATEGY, strategy_name, state_data)

    def export_state(self, state_type: Optional[StateType] = None) -> Dict[str, Any]:
        """Export state for persistence or debugging."""
        if state_type:
            return {
                str(state_type): {
                    id: {
                        "data": entry.data,
                        "created_at": entry.created_at.isoformat(),
                        "updated_at": entry.updated_at.isoformat(),
                        "metadata": entry.metadata,
                    }
                    for id, entry in self._state[state_type].items()
                }
            }
        else:
            result = {}
            for st in StateType:
                result[str(st)] = {
                    id: {
                        "data": entry.data,
                        "created_at": entry.created_at.isoformat(),
                        "updated_at": entry.updated_at.isoformat(),
                        "metadata": entry.metadata,
                    }
                    for id, entry in self._state[st].items()
                }
            return result


# Global singleton instance
state_manager = StateManager()


# Backward compatibility functions
async def get_active_strategies() -> List[Dict[str, Any]]:
    """Get active trading strategies (backward compatibility)."""
    entries = await state_manager.get_all(StateType.STRATEGY)
    return [e.data for e in entries if e.data.get("active", False)]


async def store_backtest_result(backtest_id: str, result: Dict[str, Any]) -> None:
    """Store backtest result (backward compatibility)."""
    await state_manager.create(StateType.BACKTEST, backtest_id, result)
