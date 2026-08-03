"""Checks for the batch runner: slug allocation, the quota decision, and the
consecutive-failure abort. Run directly: python tools/test_batch.py"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import mafia.game
from mafia.game import BackendUnavailable, MAX_CONSECUTIVE_FAILURES, MafiaGame
from mafia.player import Role
from tools.publish_game import next_slug
from tools.run_batch import should_start_game

HOUR = 3600


def test_next_slug():
    assert next_slug([]) == "case-001"
    assert next_slug([{"slug": "case-001"}, {"slug": "case-002"}]) == "case-003"
    # A gap must not hand out a slug that was already used.
    assert next_slug([{"slug": "case-001"}, {"slug": "case-021"}]) == "case-022"
    # Ten and up must not sort as strings.
    assert next_slug([{"slug": f"case-{n:03d}"} for n in range(1, 10)]) == "case-010"
    print("next_slug OK")


def test_should_start_game():
    now = 1000.0
    resets_at = now + 2 * HOUR
    max_wait = 12 * HOUR

    # No reading from the usage endpoint: run anyway, the failure guard covers us.
    assert should_start_game(None, 0, now, None, 0, max_wait) == "go"

    # First game (nothing measured): the fixed guard applies, reserving half a
    # window — 1.5x the worst game measured so far (33%).
    assert should_start_game(40.0, resets_at, now, None, 0, max_wait) == "go"
    assert should_start_game(50.0, resets_at, now, None, 0, max_wait) == "go"
    assert should_start_game(55.0, resets_at, now, None, 0, max_wait) == "wait"

    # Once a game has been measured, headroom is judged against its real cost.
    assert should_start_game(80.0, resets_at, now, 12.0, 0, max_wait) == "go"    # 20% left, needs 18%
    assert should_start_game(85.0, resets_at, now, 12.0, 0, max_wait) == "wait"  # 15% left, needs 18%

    # Waiting past the cap stops the batch instead.
    assert should_start_game(85.0, resets_at, now, 12.0, 11 * HOUR, max_wait) == "stop"
    # Just inside the cap still waits.
    assert should_start_game(85.0, resets_at, now, 12.0, 9 * HOUR, max_wait) == "wait"
    print("should_start_game OK")


def test_backend_failure_aborts():
    """A dead backend must abort the game rather than fill the log with
    '*X remains silent*'. Isolated failures below the threshold still fall back,
    because one bad call is a glitch and losing a whole game to it is worse."""
    game = MafiaGame(player_count=4, mafia_count=1, gm_enabled=False)
    player = game.players[0]
    player.role = Role.VILLAGER  # roles are normally dealt by run()

    def failing_call_llm(*call_args, **call_kwargs):
        raise RuntimeError("Claude usage limit reached")

    original_call_llm = mafia.game.call_llm
    mafia.game.call_llm = failing_call_llm
    try:
        for attempt in range(MAX_CONSECUTIVE_FAILURES - 1):
            response = game.query_model(player, "say something")
            assert "remains silent" in response, f"attempt {attempt} should fall back"

        aborted = False
        try:
            game.query_model(player, "say something")
        except BackendUnavailable:
            aborted = True
        assert aborted, "the game never aborted despite a dead backend"

        # One success clears the count: a live backend is not a dying one.
        game.consecutive_failures = 0
        response = game.query_model(player, "say something")
        assert "remains silent" in response
    finally:
        mafia.game.call_llm = original_call_llm
    print("backend failure abort OK")


if __name__ == "__main__":
    test_next_slug()
    test_should_start_game()
    test_backend_failure_aborts()
    print("ok")
