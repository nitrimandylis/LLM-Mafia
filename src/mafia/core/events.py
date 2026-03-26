"""All GameEvent frozen dataclasses and EventType enum."""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

# Avoid circular import — PlayerSnapshot is defined in core.player
if TYPE_CHECKING:
    from src.mafia.core.player import PlayerSnapshot


class EventType(str, Enum):
    GAME_STARTED = "game_started"
    ROLES_ASSIGNED = "roles_assigned"
    PHASE_CHANGED = "phase_changed"
    PLAYER_SPEECH = "player_speech"
    VOTE_CAST = "vote_cast"
    VOTE_TALLY = "vote_tally"
    PLAYER_ELIMINATED = "player_eliminated"
    NIGHT_KILL = "night_kill"
    INVESTIGATION_RESULT = "investigation_result"
    GAME_ENDED = "game_ended"
    LLM_QUERY_STARTED = "llm_query_started"
    LLM_QUERY_COMPLETED = "llm_query_completed"
    LLM_QUERY_FAILED = "llm_query_failed"
    REPLAY_TICK = "replay_tick"


def _new_event_id() -> str:
    return str(uuid.uuid4())


def _now() -> float:
    return time.time()


@dataclass(frozen=True)
class GameEvent:
    """Base class for all game events."""

    event_id: str
    timestamp: float
    is_public: bool = True


# ---------------------------------------------------------------------------
# Concrete events
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class GameStarted(GameEvent):
    """Emitted once when the game begins."""

    game_id: str = ""
    # Tuple of PlayerSnapshot objects (immutable)
    players: tuple = ()  # tuple[PlayerSnapshot, ...]

    @classmethod
    def create(cls, game_id: str, players: tuple) -> "GameStarted":
        return cls(
            event_id=_new_event_id(),
            timestamp=_now(),
            is_public=True,
            game_id=game_id,
            players=players,
        )


@dataclass(frozen=True)
class RolesAssigned(GameEvent):
    """Emitted after roles have been distributed. Private — not shown publicly."""

    # tuple of (player_name, role_value) pairs
    assignments: tuple[tuple[str, str], ...] = ()

    @classmethod
    def create(cls, assignments: tuple[tuple[str, str], ...]) -> "RolesAssigned":
        return cls(
            event_id=_new_event_id(),
            timestamp=_now(),
            is_public=False,
            assignments=assignments,
        )


@dataclass(frozen=True)
class PhaseChanged(GameEvent):
    """Emitted when the game phase transitions (day/night/voting)."""

    phase: str = ""
    day_number: int = 0

    @classmethod
    def create(cls, phase: str, day_number: int) -> "PhaseChanged":
        return cls(
            event_id=_new_event_id(),
            timestamp=_now(),
            is_public=True,
            phase=phase,
            day_number=day_number,
        )


@dataclass(frozen=True)
class PlayerSpeech(GameEvent):
    """Emitted when a player speaks. is_public varies by speech_type."""

    player_name: str = ""
    content: str = ""
    speech_type: str = ""
    is_public: bool = True  # override base default; caller sets this

    @classmethod
    def create(
        cls,
        player_name: str,
        content: str,
        speech_type: str,
        is_public: bool = True,
    ) -> "PlayerSpeech":
        return cls(
            event_id=_new_event_id(),
            timestamp=_now(),
            is_public=is_public,
            player_name=player_name,
            content=content,
            speech_type=speech_type,
        )


@dataclass(frozen=True)
class VoteCast(GameEvent):
    """Emitted when a player casts a vote."""

    voter_name: str = ""
    target_name: str = ""

    @classmethod
    def create(cls, voter_name: str, target_name: str) -> "VoteCast":
        return cls(
            event_id=_new_event_id(),
            timestamp=_now(),
            is_public=True,
            voter_name=voter_name,
            target_name=target_name,
        )


@dataclass(frozen=True)
class VoteTally(GameEvent):
    """Emitted with the final vote counts."""

    # tuple of (player_name, vote_count) pairs
    tally: tuple[tuple[str, int], ...] = ()

    @classmethod
    def create(cls, tally: tuple[tuple[str, int], ...]) -> "VoteTally":
        return cls(
            event_id=_new_event_id(),
            timestamp=_now(),
            is_public=True,
            tally=tally,
        )


@dataclass(frozen=True)
class PlayerEliminated(GameEvent):
    """Emitted when a player is eliminated by vote."""

    player_name: str = ""
    role: str = ""
    method: str = ""
    was_saved: bool = False

    @classmethod
    def create(
        cls,
        player_name: str,
        role: str,
        method: str,
        was_saved: bool = False,
    ) -> "PlayerEliminated":
        return cls(
            event_id=_new_event_id(),
            timestamp=_now(),
            is_public=True,
            player_name=player_name,
            role=role,
            method=method,
            was_saved=was_saved,
        )


@dataclass(frozen=True)
class NightKill(GameEvent):
    """Emitted at the end of a night phase."""

    victim_name: str = ""
    role: str = ""
    saved: bool = False
    night_number: int = 0

    @classmethod
    def create(
        cls,
        victim_name: str,
        role: str,
        saved: bool,
        night_number: int,
    ) -> "NightKill":
        return cls(
            event_id=_new_event_id(),
            timestamp=_now(),
            is_public=True,
            victim_name=victim_name,
            role=role,
            saved=saved,
            night_number=night_number,
        )


@dataclass(frozen=True)
class InvestigationResult(GameEvent):
    """Emitted when the detective investigates a target. Private."""

    detective_name: str = ""
    target_name: str = ""
    result: str = ""

    @classmethod
    def create(
        cls,
        detective_name: str,
        target_name: str,
        result: str,
    ) -> "InvestigationResult":
        return cls(
            event_id=_new_event_id(),
            timestamp=_now(),
            is_public=False,
            detective_name=detective_name,
            target_name=target_name,
            result=result,
        )


@dataclass(frozen=True)
class GameEnded(GameEvent):
    """Emitted when the game concludes."""

    winner: str = ""
    # tuple of (player_name, role_value) pairs
    final_roles: tuple[tuple[str, str], ...] = ()
    total_days: int = 0

    @classmethod
    def create(
        cls,
        winner: str,
        final_roles: tuple[tuple[str, str], ...],
        total_days: int,
    ) -> "GameEnded":
        return cls(
            event_id=_new_event_id(),
            timestamp=_now(),
            is_public=True,
            winner=winner,
            final_roles=final_roles,
            total_days=total_days,
        )


@dataclass(frozen=True)
class LLMQueryStarted(GameEvent):
    """Emitted when an LLM query begins."""

    player_name: str = ""
    model: str = ""

    @classmethod
    def create(cls, player_name: str, model: str) -> "LLMQueryStarted":
        return cls(
            event_id=_new_event_id(),
            timestamp=_now(),
            is_public=True,
            player_name=player_name,
            model=model,
        )


@dataclass(frozen=True)
class LLMQueryCompleted(GameEvent):
    """Emitted when an LLM query completes successfully."""

    player_name: str = ""
    model: str = ""
    elapsed_s: float = 0.0
    tps: float = 0.0

    @classmethod
    def create(
        cls,
        player_name: str,
        model: str,
        elapsed_s: float,
        tps: float,
    ) -> "LLMQueryCompleted":
        return cls(
            event_id=_new_event_id(),
            timestamp=_now(),
            is_public=True,
            player_name=player_name,
            model=model,
            elapsed_s=elapsed_s,
            tps=tps,
        )


@dataclass(frozen=True)
class LLMQueryFailed(GameEvent):
    """Emitted when an LLM query fails."""

    player_name: str = ""
    model: str = ""
    error: str = ""

    @classmethod
    def create(cls, player_name: str, model: str, error: str) -> "LLMQueryFailed":
        return cls(
            event_id=_new_event_id(),
            timestamp=_now(),
            is_public=True,
            player_name=player_name,
            model=model,
            error=error,
        )


@dataclass(frozen=True)
class ReplayTick(GameEvent):
    """Emitted during replay to signal progress."""

    event_index: int = 0
    total_events: int = 0
    speed_multiplier: float = 1.0

    @classmethod
    def create(
        cls,
        event_index: int,
        total_events: int,
        speed_multiplier: float = 1.0,
    ) -> "ReplayTick":
        return cls(
            event_id=_new_event_id(),
            timestamp=_now(),
            is_public=True,
            event_index=event_index,
            total_events=total_events,
            speed_multiplier=speed_multiplier,
        )
