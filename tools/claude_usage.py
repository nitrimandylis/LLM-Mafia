"""How much of the Claude subscription's 5-hour window is used up.

There is no `claude usage` subcommand, so this reads the same OAuth token the
CLI stores in the macOS Keychain and asks the endpoint the /usage view uses.
Undocumented, so every caller must handle None: callers fall back to the
consecutive-failure guard in mafia/game.py, which catches a spent quota
whether or not this works.
"""

import json
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

USAGE_URL = "https://api.anthropic.com/api/oauth/usage"
KEYCHAIN_SERVICE = "Claude Code-credentials"

# The endpoint 429s if asked more than every couple of minutes, and a statusline
# may be polling it too. Cache so we ask rarely, and keep serving the last good
# reading through a 429 — a few-minute-old number still guards better than None.
CACHE_PATH = Path(tempfile.gettempdir()) / "llm-mafia-claude-usage.json"
CACHE_FRESH_SECONDS = 120
CACHE_STALE_SECONDS = 900


def read_access_token():
    """The CLI's OAuth access token, or None if the Keychain entry is missing.
    Never printed or logged anywhere."""
    try:
        result = subprocess.run(
            ["security", "find-generic-password", "-s", KEYCHAIN_SERVICE, "-w"],
            capture_output=True, text=True,
        )
    except FileNotFoundError:
        return None  # no `security` binary at all, e.g. a Linux CI runner
    if result.returncode != 0:
        return None
    try:
        credentials = json.loads(result.stdout)
    except json.JSONDecodeError:
        return None
    return credentials.get("claudeAiOauth", {}).get("accessToken")


def read_usage():
    """Returns {"utilization": 0-100, "resets_at": unix seconds} or None.

    Cached, because the endpoint throttles. None means "could not tell" — a
    missing token, a network failure, or a 429 with no recent enough reading to
    fall back on. Never means "quota is fine"."""
    cached = read_cache()
    if cached and time.time() - cached["fetched_at"] < CACHE_FRESH_SECONDS:
        return cached["usage"]

    usage = fetch_usage()
    if usage is None:
        if cached and time.time() - cached["fetched_at"] < CACHE_STALE_SECONDS:
            return cached["usage"]
        return None

    write_cache(usage)
    return usage


def read_cache():
    """The last stored reading as {"fetched_at": ..., "usage": ...}, or None.
    A corrupt or missing cache is just a cache miss, never an error."""
    try:
        cached = json.loads(CACHE_PATH.read_text())
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(cached.get("usage"), dict) or "fetched_at" not in cached:
        return None
    return cached


def write_cache(usage):
    try:
        CACHE_PATH.write_text(json.dumps({"fetched_at": time.time(), "usage": usage}))
    except OSError:
        pass  # a cache we cannot write is slower, not broken


def fetch_usage():
    """One uncached call to the endpoint. None on any failure."""
    token = read_access_token()
    if token is None:
        return None

    request = urllib.request.Request(
        USAGE_URL,
        headers={
            "Authorization": f"Bearer {token}",
            "anthropic-beta": "oauth-2025-04-20",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            payload = json.load(response)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return None

    window = payload.get("five_hour")
    if not isinstance(window, dict):
        return None

    utilization = window.get("utilization")
    resets_at = window.get("resets_at")
    if utilization is None or resets_at is None:
        return None

    return {"utilization": float(utilization), "resets_at": parse_resets_at(resets_at)}


def parse_resets_at(value):
    """The endpoint has returned this as unix seconds in some builds and as an
    ISO timestamp in others, so accept both rather than guessing wrong at 3am."""
    if isinstance(value, (int, float)):
        return float(value)
    import datetime

    text = str(value).replace("Z", "+00:00")
    return datetime.datetime.fromisoformat(text).timestamp()


if __name__ == "__main__":
    # ponytail: doubles as the self-check — the parser is the only real logic here.
    assert parse_resets_at(1785258600) == 1785258600.0
    assert parse_resets_at("2026-07-28T17:10:01Z") == parse_resets_at(
        "2026-07-28T17:10:01+00:00"
    )

    saved = CACHE_PATH.read_text() if CACHE_PATH.exists() else None
    sample = {"utilization": 12.0, "resets_at": 1785258600.0}
    write_cache(sample)
    assert read_cache()["usage"] == sample
    CACHE_PATH.write_text("not json")
    assert read_cache() is None  # corrupt cache is a miss, not a crash
    if saved is None:
        CACHE_PATH.unlink()
    else:
        CACHE_PATH.write_text(saved)  # the checks must not cost a real reading

    usage = read_usage()
    if usage is None:
        print("usage: unavailable (no token, network error, or 429)")
    else:
        left = max(0, int((usage["resets_at"] - time.time()) // 60))
        print(f"{usage['utilization']:.0f}% used, resets in {left // 60}h{left % 60:02d}m")
