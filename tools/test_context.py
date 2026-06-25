"""
Self-check for the public/private context split (Approach A).

Constructs a game offline (OpenAI client construction makes no network call),
emits a day's worth of public events plus a private detective result, then
asserts the public transcript is shared by all and private knowledge is not.

    python tools/test_context.py
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from mafia.game import MafiaGame  # noqa: E402


def main():
    game = MafiaGame(reveal_secrets=False, player_count=8)
    game.day = 1
    alive = game.get_alive_players()
    a, b = alive[0], alive[1]

    # A public exchange on day 1.
    game.emit("statement", day=1, actor=a.name, text="I think B is hiding something.")
    game.emit("question", day=1, actor=b.name, target=a.name, text="Why me specifically?")
    game.emit("answer", day=1, actor=a.name, target=b.name, text="Your timing was off.")
    game.emit("accusation", day=1, actor=b.name, target=a.name, text="A is deflecting.")
    # A private detective finding (only A should ever see this).
    game.add_private_note(a, "Night 1: Investigated B - MAFIA")

    transcript = game.render_public_transcript(1)
    assert a.name in transcript and "hiding something" in transcript, "statement missing"
    assert f"{b.name} → {a.name}" in transcript, "question arrow missing"
    assert "(to " in transcript, "answer target missing"
    assert "accuses" in transcript, "accusation missing"
    assert "MAFIA" not in transcript, "private note leaked into public transcript"

    # Day-scoping: an event on another day must not appear in day 1's transcript.
    game.emit("statement", day=2, actor=a.name, text="A day-two remark.")
    assert "day-two remark" not in game.render_public_transcript(1), "transcript not day-scoped"

    # Everyone sees today's discussion; only A sees A's private finding.
    ctx_b = game.build_context_for_player(b, base_context="FACTS")
    ctx_a = game.build_context_for_player(a, base_context="FACTS")
    assert "hiding something" in ctx_b, "B can't see public discussion"
    assert "FACTS" in ctx_b, "base_context dropped"
    assert "MAFIA" not in ctx_b, "B leaked A's private finding"
    assert "MAFIA" in ctx_a, "A can't see own private finding"

    # Budget: transcript caps at the last K lines.
    for i in range(60):
        game.emit("statement", day=1, actor=a.name, text=f"line {i}")
    lines = game.render_public_transcript(1).splitlines()
    assert len(lines) <= game.TRANSCRIPT_MAX_LINES, "transcript exceeds budget"

    print(f"OK: context split holds ({len(lines)} transcript lines, capped at {game.TRANSCRIPT_MAX_LINES})")


if __name__ == "__main__":
    main()
