"""
Structured event stream for the replay viewer.

The console `log()` output is prose; this is a parallel, ordered list of typed
events that a web viewer can dramatize. One place owns the schema.

This is the source of truth. It is mirrored in `viewer/lib/events.ts`; the two
are kept in sync by `tools/make_sample_log.py` (check_schema_parity), which
fails if the event-type lists drift apart.
"""
from typing import Dict, List

# Per-seat avatar colors, assigned by seat index.
PALETTE = [
    "#7cc4ff", "#ff9a9a", "#b9f6ca", "#ffd180", "#ce93d8",
    "#80deea", "#ffab91", "#c5e1a5", "#f48fb1", "#9fa8da",
]

# Required fields per event type. Validation guards the Python↔viewer contract.
REQUIRED: Dict[str, List[str]] = {
    "game_start":    ["players", "player_count"],
    "phase":         ["day", "phase"],            # phase: "day" | "night"
    "statement":     ["day", "actor", "text"],
    "question":      ["day", "actor", "target", "text"],
    "answer":        ["day", "actor", "target", "text"],
    "accusation":    ["day", "actor", "target", "text"],
    "vote":          ["day", "actor", "target"],
    "elimination":   ["day", "target", "role", "tally"],
    "night_kill":    ["day", "target", "role", "saved"],
    "night_no_kill": ["day"],
    "save":          ["day", "target"],
    "protection":    ["day", "actor", "target"],   # private (reveal-secrets only)
    "mafia_chat":    ["day", "actor", "text"],     # private (reveal-secrets only)
    "investigation": ["day", "actor", "target", "result"],  # private
    "game_over":     ["winner", "survivors"],
}


def seat_color(seat: int) -> str:
    return PALETTE[seat % len(PALETTE)]


class EventLog:
    """Append-only ordered list of validated event dicts."""

    def __init__(self) -> None:
        self.events: List[Dict] = []

    def emit(self, type: str, **fields) -> Dict:
        if type not in REQUIRED:
            raise ValueError(f"unknown event type: {type!r}")
        missing = [k for k in REQUIRED[type] if k not in fields]
        if missing:
            raise ValueError(f"event {type!r} missing fields: {missing}")
        event = {"type": type, **fields}
        self.events.append(event)
        return event

    def to_list(self) -> List[Dict]:
        return self.events


def demo() -> None:
    """Self-check: validation accepts good events and rejects bad ones."""
    log = EventLog()
    log.emit("phase", day=1, phase="day")
    log.emit("statement", day=1, actor="HOLMES", text="hi")
    assert len(log.to_list()) == 2
    assert log.events[0]["type"] == "phase"

    for bad in (
        lambda: log.emit("nope", day=1),                       # unknown type
        lambda: log.emit("statement", day=1, actor="X"),       # missing text
    ):
        try:
            bad()
        except ValueError:
            pass
        else:
            raise AssertionError("expected ValueError")

    assert seat_color(0) == seat_color(len(PALETTE))  # wraps
    print("events.py demo OK")


if __name__ == "__main__":
    demo()
