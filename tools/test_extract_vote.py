"""
Regression check for extract_vote's prefer_first mode.

The five accusation texts below are verbatim from a real game
(no-secret-claude, 2026-07-13) where the last-mention heuristic recorded the
wrong target in the event log. Accusations lead with the accused's name, so
they parse with prefer_first=True; votes keep the default (last mention).

    python tools/test_extract_vote.py
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from mafia.game import MafiaGame  # noqa: E402

TARGETS = [
    "RICO", "ARIA", "SAGE", "HOLMES", "MARSHAL",
    "SOCRATES", "DR. VANCE", "PIP", "CHEN", "AMBASSADOR SILVA",
]

# (accusation text, intended target) — each was mis-parsed before prefer_first
ACCUSATIONS = [
    ("SOCRATES has spent the entire discussion deflecting direct questions with "
     "attacks on his accusers, and now with CHEN, HOLMES, RICO, and myself all "
     "converging on him, he's the safest and most consensus-backed vote to lock "
     "in today.", "SOCRATES"),
    ("RICO stays my vote, because his first-round certainty against the very man "
     "who named him, paired with a whole round of just repeating \"MARSHAL's "
     "guilty\" without a shred of new evidence, is exactly the bandwagon-forcing "
     "of someone who needed SOCRATES buried and now needs a townsfolk pinned "
     "fast.", "RICO"),
    ("MARSHAL, since he still hasn't answered the gut-feeling contradiction and "
     "just keeps redirecting to SAGE instead.", "MARSHAL"),
    ("MARSHAL got caught contradicting himself and now he's just deflecting to "
     "SAGE instead of defending his own hypocrisy—that's Mafia behavior.", "MARSHAL"),
    ("MARSHAL's contradiction—criticizing gut accusations while casting one "
     "himself, then deflecting to SAGE rather than defending that logical "
     "inconsistency—is the clearest pattern the evidence shows, and his "
     "refusal to address it directly marks him as the most suspicious player "
     "alive.", "MARSHAL"),
    # Explicit vote phrasing must still win over an earlier mention
    ("MARSHAL remains the clearest unresolved contradiction today. I'm voting "
     "MARSHAL.", "MARSHAL"),
    # Game 2, day 2: third-person ballot talk ("he voted HOLMES instead") must
    # not read as vote intent — the accused leads the sentence
    ("MARSHAL, since his unexplained divergence between building the case "
     "against RICO and then voting HOLMES instead remains the biggest "
     "unresolved contradiction on the table.", "MARSHAL"),
    ("I've confirmed through my own investigation that MARSHAL is Mafia, and "
     "the table's independent reasoning about his abandoned \"quick accuser\" "
     "logic and his divergent vote for HOLMES lines up perfectly with that "
     "read, so the evidence and my private knowledge converge cleanly today. "
     "MARSHAL.", "MARSHAL"),
    ("MARSHAL — his own \"quick accuser\" logic against RICO never got applied "
     "to himself, and he still hasn't given a real reason for abandoning it to "
     "vote HOLMES instead.", "MARSHAL"),
    ("MARSHAL — his own logic against RICO's timing was sound enough to "
     "convict, yet he voted HOLMES instead, and his explanation about "
     "\"withholding\" doesn't outweigh the case he built himself; that "
     "unresolved contradiction is the strongest data point on the table.", "MARSHAL"),
    ("Okay, um, I think I have to go with MARSHAL — his own logic against "
     "RICO's \"quick accuser\" pattern should've pointed him to RICO, but he "
     "voted HOLMES instead and never really cleared that up for me. AMBASSADOR "
     "SILVA and DR. VANCE both landed there too, so that's not just me being "
     "swayed this time, I think? MARSHAL, that's my vote.", "MARSHAL"),
    # ...but first-person intent still beats a leading mention of someone else
    ("I'm voting HOLMES today. The pattern of his calm non-commitment on Day 1 "
     "combined with his own vote landing exactly where mine and SAGE's did, "
     "plus his refusal to give a real read early on, still outweighs the "
     "unresolved gap in my own vote that others keep circling back to. "
     "Procedure says the biggest unknown gets scrutinized first, and that's "
     "HOLMES.", "HOLMES"),
    ("Given the momentum, the table is converging hard on MARSHAL, but that "
     "reasoning rests entirely on a vote-pattern coincidence while HOLMES has "
     "an actual documented deflection in his own words at 2:47. I'll push to "
     "eliminate HOLMES today since his rationalized non-commitment is a "
     "content-based red flag, not just a ballot artifact like MARSHAL's.", "HOLMES"),
]

# Vote replies keep the default last-mention behavior
VOTES = [
    ("I've thought about MARSHAL all day, but my vote is SAGE.", "SAGE"),
    ("DR. VANCE", "DR. VANCE"),
    ("I say we eliminate RICO.", "RICO"),
]


def main():
    game = MafiaGame(gm_enabled=False)
    for text, want in ACCUSATIONS:
        got = game.extract_vote(text, TARGETS, prefer_first=True)
        assert got == want, f"prefer_first: got {got!r}, want {want!r} for: {text[:60]}..."
    for text, want in VOTES:
        got = game.extract_vote(text, TARGETS)
        assert got == want, f"vote: got {got!r}, want {want!r} for: {text[:60]}..."
    print(f"test_extract_vote OK ({len(ACCUSATIONS)} accusations, {len(VOTES)} votes)")


if __name__ == "__main__":
    main()
