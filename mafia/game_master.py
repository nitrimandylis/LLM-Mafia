import json
import random
import re
import subprocess
import threading
import time
from typing import Callable, Dict, List, Optional

from openai import OpenAI

# ponytail: one global min-spacing for all NVIDIA calls (players + GM share the
# free-tier rate limit). ~1.5s ≈ 40 req/min; raise if you still see 429s.
NVIDIA_MIN_INTERVAL = 1.5
_nvidia_throttle = threading.Lock()
_nvidia_last_call = [0.0]


def nvidia_pace():
    with _nvidia_throttle:
        wait = NVIDIA_MIN_INTERVAL - (time.time() - _nvidia_last_call[0])
        if wait > 0:
            time.sleep(wait)
        _nvidia_last_call[0] = time.time()

_SYSTEM_PROMPT = """You are the Game Master of a Mafia party game. You narrate key moments with dramatic flair — eliminations, night kills, day openings, and the final outcome. You are impartial and theatrical. Keep every narration to 2-3 sentences. Never reveal hidden roles."""

def _schema(key: str) -> dict:
    """Strict single-string-field JSON schema, keyed by `key`."""
    return {
        "type": "json_schema",
        "json_schema": {
            "name": key,
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {key: {"type": "string"}},
                "required": [key],
                "additionalProperties": False,
            },
        },
    }


def call_claude(model: str, messages: List[Dict]) -> str:
    """One `claude -p` subprocess call, billed to the Claude subscription.
    Fully isolated: no tools, no settings/CLAUDE.md/hooks, no MCP — a pure
    text generator. Raises on nonzero exit; callers decide whether to swallow."""
    # haiku sometimes replied with just a header like "**Discussion:**",
    # tripping the empty/short retry — ban markdown outright
    system = messages[0]["content"] + (
        "\n\nNever use markdown formatting: no headers, no bold, no bullet points. "
        "Reply in plain sentences only."
    )
    user = messages[-1]["content"]
    # ponytail: temperature/max_tokens have no CLI equivalent — prompts
    # already ask for short replies, good enough for the experiment
    result = subprocess.run(
        [
            "claude", "-p", user,
            "--model", model,
            "--system-prompt", system,
            "--tools", "",
            "--setting-sources", "",
            "--strict-mcp-config",
        ],
        capture_output=True, text=True, timeout=180,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"claude exited {result.returncode}")
    return result.stdout.strip()


def call_llm(
    client: OpenAI,
    model: str,
    messages: List[Dict],
    use_nvidia: bool,
    schema_key: str,
    temperature: float = 0.7,
    max_tokens: int = 512,
    on_retry: Optional[Callable[[float], None]] = None,
    private_reasoning: bool = False,
    use_claude: bool = False,
) -> str:
    """One chat completion with 429 backoff. NVIDIA gets no response_format
    (unsupported) and the raw text back; everyone else gets a strict
    single-field JSON schema, unwrapped by `schema_key`. Raises on exhaustion
    or non-429 errors — callers decide whether to swallow."""
    if use_claude:
        return call_claude(model, messages)
    kwargs: Dict = dict(model=model, messages=messages, temperature=temperature, max_tokens=max_tokens)
    if not use_nvidia:
        kwargs["response_format"] = _schema(schema_key)

    for attempt in range(5):
        try:
            if use_nvidia:
                nvidia_pace()
            response = client.chat.completions.create(**kwargs)
            msg = response.choices[0].message
            content = (msg.content or "").strip()
            reasoning = (getattr(msg, "reasoning_content", None) or "").strip()
            # private_reasoning: the model's thinking channel is a secret
            # scratchpad (mafia scheming, role knowledge) — NEVER emit it,
            # even when content is empty
            raw = content if (content or private_reasoning) else reasoning
            if not use_nvidia:
                try:
                    return json.loads(raw).get(schema_key, raw)
                except (json.JSONDecodeError, AttributeError):
                    return raw
            return raw
        except Exception as e:
            # 429 = rate limit, 5xx = gateway flake (504s seen when reasoning
            # runs long) — both are transient, both get the backoff
            if re.search(r"\b(429|5\d\d)\b", str(e)) and attempt < 4:
                wait = 2 ** attempt * 5 + random.uniform(0, 5)  # jitter desyncs workers
                if on_retry:
                    on_retry(wait)
                time.sleep(wait)
            else:
                raise
    return ""


def episode_inputs_from_events(events: List[Dict]) -> Optional[Dict]:
    """Derive write_episode kwargs from a finished game's event list.
    Shared by the live game and tools/publish_game.py (backfilling old logs).
    Returns None when the log isn't a completed town/mafia game."""
    start = next((e for e in events if e["type"] == "game_start"), None)
    over = next((e for e in events if e["type"] == "game_over"), None)
    if not start or not over or over.get("winner") not in ("town", "mafia"):
        return None
    cast = [f"{p['name']} ({p['role']})" for p in start["players"]]
    days = 1
    timeline = []
    for e in events:
        days = max(days, e.get("day") or 1)
        if e["type"] == "elimination":
            timeline.append(f"Day {e['day']}: the town voted out {e['target']} — they were {e['role']}.")
        elif e["type"] == "night_kill" and not e.get("saved"):
            timeline.append(f"Night {e['day']}: the mafia killed {e['target']} — they were {e['role']}.")
        elif e["type"] == "save" or (e["type"] == "night_kill" and e.get("saved")):
            timeline.append(f"Night {e['day']}: the mafia struck, but the Doctor saved {e['target']}.")
        elif e["type"] == "night_no_kill":
            timeline.append(f"Night {e['day']}: nobody died.")
    timeline.append(f"The {over['winner']} won. Survivors: {', '.join(over['survivors'])}.")
    return {"winner": over["winner"], "days": days, "cast": cast, "timeline": timeline}


class GameMaster:
    def __init__(self, client: OpenAI, model: str, use_nvidia: bool = False, enabled: bool = True, use_claude: bool = False):
        self._client = client
        self._model = model
        self._use_nvidia = use_nvidia
        self._use_claude = use_claude
        self._enabled = enabled

    def _call(self, prompt: str, max_tokens: int = 150) -> str:
        if not self._enabled:
            return ""
        messages = [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]
        try:
            return call_llm(
                self._client, self._model, messages,
                use_nvidia=self._use_nvidia, schema_key="narration",
                temperature=0.9, max_tokens=max_tokens,
                use_claude=self._use_claude,
            )
        except Exception:
            return ""  # narration is optional flavor — never crash the game over it

    def narrate_day_start(
        self,
        day: int,
        alive_names: List[str],
        last_kill: Optional[Dict],
        last_vote: Optional[Dict],
    ) -> str:
        if day == 1:
            prompt = (
                f"Narrate the opening of Day 1 in a Mafia game. "
                f"{len(alive_names)} players are gathered: {', '.join(alive_names)}. "
                f"No one has died yet. Set an ominous, foreboding scene."
            )
        else:
            events = []
            if last_kill:
                if last_kill["saved"]:
                    events.append(f"{last_kill['victim']} was targeted by the Mafia but survived thanks to the Doctor")
                else:
                    events.append(f"{last_kill['victim']} was murdered by the Mafia under cover of darkness")
            if last_vote:
                events.append(f"{last_vote['eliminated']} was voted out by the town")
            event_str = " and ".join(events) if events else "the night passed without incident"
            prompt = (
                f"Narrate the opening of Day {day} in a Mafia game. "
                f"Since yesterday: {event_str}. "
                f"{len(alive_names)} players remain: {', '.join(alive_names)}. "
                f"Capture the tension and suspicion in the room."
            )
        return self._call(prompt)

    def narrate_elimination(
        self, eliminated_name: str, role: str, vote_counts: Dict[str, int]
    ) -> str:
        top = sorted(vote_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        vote_str = ", ".join(f"{n} ({v} vote{'s' if v > 1 else ''})" for n, v in top)
        prompt = (
            f"Narrate the dramatic elimination of {eliminated_name} from a Mafia game. "
            f"Vote tally: {vote_str}. "
            f"Their true role was {role} — reveal this in the narration as their fate is sealed. "
            f"Make it theatrical and final."
        )
        return self._call(prompt)

    def narrate_night_kill(self, victim: str, saved: bool) -> str:
        if saved:
            prompt = (
                f"Narrate the tense morning discovery that {victim} survived a Mafia assassination attempt — "
                f"the Doctor's protection intervened just in time. "
                f"2 sentences: relief mixed with dread."
            )
        else:
            prompt = (
                f"Narrate the grim dawn discovery that {victim} was killed by the Mafia during the night. "
                f"Do not reveal their role. "
                f"2 sentences: dark, foreboding, the town is shaken."
            )
        return self._call(prompt)

    def narrate_no_kill(self) -> str:
        prompt = "Narrate the surprising morning in a Mafia game where no one was killed overnight. The town is unsettled — why did the Mafia hold back? 2 sentences."
        return self._call(prompt)

    def narrate_day_summary(self, day: int, statements: List[str]) -> str:
        if not statements:
            return ""
        condensed = "\n".join(statements[:24])
        prompt = (
            f"Summarize Day {day} of a Mafia game in 3-4 sentences. "
            f"Focus on who accused whom, who defended themselves, and what suspicion patterns emerged. "
            f"Be factual and concise — no dramatic flair here, just a clear recap a player could use to reason.\n\n"
            f"Statements from this day:\n{condensed}"
        )
        return self._call(prompt, max_tokens=300)

    def write_episode(self, winner: str, days: int, cast: List[str], timeline: List[str]) -> Dict[str, str]:
        """Episode packaging for the replay viewer, written at game end.
        `cast` is "NAME (Role)" strings, `timeline` is short beat lines.
        Returns {} when the GM is disabled or every call comes back empty."""
        base = (
            f"A finished Mafia party game played entirely by AI players. "
            f"It lasted {days} day(s) and the {winner} won.\n"
            f"Cast: {', '.join(cast)}.\n"
            f"What happened:\n" + "\n".join(timeline)
        )
        title = self._call(
            "Write a pulpy noir episode title for this game: 2-5 words, no quotes, "
            "no colons, don't reveal the winner.\n\n" + base,
            max_tokens=150,
        )
        tagline = self._call(
            "Write ONE teaser sentence for this game, shown before anyone watches it. "
            "STRICTLY spoiler-free: do not reveal who wins, who dies, or anyone's role.\n\n" + base,
            max_tokens=200,
        )
        recap = self._call(
            "Write a 3-5 sentence dramatic recap of this game, shown AFTER viewers finish "
            "watching. Spoilers welcome: name the mafia, the turning point, and how it ended.\n\n" + base,
            max_tokens=300,
        )
        episode = {"title": title, "tagline": tagline, "recap": recap}
        return episode if any(episode.values()) else {}

    def narrate_game_over(self, winner: str, survivors: List[str], day: int) -> str:
        if winner == "town":
            prompt = (
                f"Narrate the town's victory in a Mafia game that lasted {day} days. "
                f"Survivors: {', '.join(survivors)}. The Mafia has been eliminated. "
                f"Triumphant but weary — justice was hard-won."
            )
        else:
            prompt = (
                f"Narrate the Mafia's victory in a Mafia game that lasted {day} days. "
                f"The Mafia has taken control. Survivors: {', '.join(survivors)}. "
                f"Dark, menacing — the innocent never stood a chance."
            )
        return self._call(prompt)
