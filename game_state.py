"""
Builds structured day-phase summaries for player context.
Replaces raw public_log slicing with digestible fact summaries.
"""
from typing import Dict, List, Optional


def build_day_summary(
    day: int,
    alive_names: List[str],
    vote_history: List[Dict],
    night_kill_history: List[Dict],
    max_events: int = 8,
) -> str:
    """
    Build a structured summary of game events for use as player context.

    Returns a text block with:
    - Night kills (most recent first, up to max_events)
    - Vote eliminations (most recent first, up to max_events)
    - Current alive players
    """
    lines: List[str] = []

    # Night kills
    kills = [k for k in night_kill_history if not k["saved"]]
    saves = [k for k in night_kill_history if k["saved"]]

    if kills:
        lines.append("=== NIGHT KILLS ===")
        for k in reversed(kills[-max_events:]):
            lines.append(f"  Night {k['night']}: {k['victim']} was killed by mafia (was {k['role']})")

    if saves:
        for s in reversed(saves[-2:]):
            lines.append(f"  Night {s['night']}: {s['victim']} was targeted by mafia but SAVED by doctor")

    # Vote eliminations
    if vote_history:
        lines.append("=== VOTE ELIMINATIONS ===")
        for v in reversed(vote_history[-max_events:]):
            lines.append(f"  Day {v['day']}: Town voted out {v['eliminated']} (was {v['role']})")

    # Current alive players
    lines.append(f"=== ALIVE PLAYERS ({len(alive_names)}) ===")
    lines.append(f"  {', '.join(alive_names)}")

    if not kills and not vote_history:
        lines.append("(No deaths yet — this is the start of the game)")

    return "\n".join(lines)
