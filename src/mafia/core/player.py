"""Immutable player dataclasses with evolve() pattern."""
from __future__ import annotations

from dataclasses import dataclass, replace
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from src.mafia.config.player_config import PlayerConfig


@dataclass(frozen=True)
class PlayerSnapshot:
    """Immutable player state captured at a point in time."""

    name: str
    model: str
    backend: str
    personality: str
    role: Optional[str] = None  # Role.value or None (not yet assigned)
    alive: bool = True


@dataclass(frozen=True)
class Player:
    """Immutable player record. Use evolve() to produce updated copies."""

    name: str
    model: str
    backend: str
    personality: str
    role: Optional[str] = None
    alive: bool = True

    def evolve(self, **kwargs) -> "Player":
        """Return a new Player with specified fields changed (immutable update)."""
        return replace(self, **kwargs)

    def to_snapshot(self) -> PlayerSnapshot:
        """Capture current state as an immutable PlayerSnapshot."""
        return PlayerSnapshot(
            name=self.name,
            model=self.model,
            backend=self.backend,
            personality=self.personality,
            role=self.role,
            alive=self.alive,
        )

    @classmethod
    def from_config(cls, config: "PlayerConfig") -> "Player":
        """Construct a Player from a validated PlayerConfig."""
        return cls(
            name=config.name,
            model=config.model,
            backend=config.backend,
            personality=config.personality,
        )
