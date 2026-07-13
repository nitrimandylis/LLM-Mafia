"""Smoke check for the --claude backend: one real claude -p call."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from mafia.game_master import call_claude, call_llm

messages = [
    {"role": "system", "content": "You are a player in a Mafia game. Reply in one short sentence."},
    {"role": "user", "content": "Current task: say the word 'ready' and nothing else."},
]

reply = call_claude("haiku", messages)
assert reply, "empty reply from claude -p"
assert "ready" in reply.lower(), f"unexpected reply: {reply!r}"

# call_llm must route to claude without touching the (None) client
routed = call_llm(None, "haiku", messages, use_nvidia=False, schema_key="response", use_claude=True)
assert routed, "call_llm did not route to claude"

print(f"OK — call_claude: {reply!r}")
