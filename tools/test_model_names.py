"""Check that a finished game stamps the build that played, not the alias.

    python tools/test_model_names.py

No model is called: the resolved-alias map is filled by hand, the way
call_claude fills it from the CLI's "modelUsage" field.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from mafia.game import MafiaGame, short_model_name  # noqa: E402
from mafia.game_master import RESOLVED_CLAUDE_MODELS  # noqa: E402

SHORT_NAMES = [
    ("claude-sonnet-5", "sonnet-5"),
    ("claude-opus-4-8", "opus-4.8"),
    ("claude-haiku-4-5-20251001", "haiku-4.5"),
    # not a Claude id — left alone
    ("minimaxai/minimax-m3", "minimaxai/minimax-m3"),
]


def main():
    for model_id, want in SHORT_NAMES:
        got = short_model_name(model_id)
        assert got == want, f"short_model_name({model_id!r}) = {got!r}, want {want!r}"

    game = MafiaGame(gm_enabled=False, use_claude=True)
    game.emit(
        "game_start",
        players=[
            {"name": "RICO", "seat": 0, "color": "#7cc4ff", "model": "sonnet"},
            {"name": "ARIA", "seat": 1, "color": "#ff9a9a", "model": "opus"},
            # never spoke, so nothing resolved it — the alias must survive
            {"name": "SAGE", "seat": 2, "color": "#b9f6ca", "model": "haiku"},
        ],
        player_count=3,
        provider="claude",
    )
    RESOLVED_CLAUDE_MODELS["sonnet"] = "claude-sonnet-5"
    RESOLVED_CLAUDE_MODELS["opus"] = "claude-opus-4-8"

    game.stamp_resolved_models()

    stamped = [p["model"] for p in game.events.to_list()[0]["players"]]
    assert stamped == ["sonnet-5", "opus-4.8", "haiku"], stamped
    print("test_model_names OK")


if __name__ == "__main__":
    main()
