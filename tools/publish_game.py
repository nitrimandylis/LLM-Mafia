"""Publish a finished game log to the viewer's static episode library.

Usage:
    python tools/publish_game.py game_log.json --slug case-005
    python tools/publish_game.py game_log1.json --slug case-001 --nvidia

What it does:
    1. Loads the log. If it has no GM-written episode metadata, makes one
       local LLM call (same backends as main.py) to backfill it.
    2. Writes a slimmed copy (events + stats + episode, no console logs)
       to viewer/public/logs/<slug>.json.
    3. Updates viewer/public/logs/manifest.json with spoiler-free card data.

Then commit and push — Vercel deploys the new episode.
"""

import argparse
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from dotenv import load_dotenv
from openai import OpenAI

from mafia.game_master import GameMaster, episode_inputs_from_events
from mafia.game import LM_STUDIO_URL, NVIDIA_API_URL, DEFAULT_MODEL, DEFAULT_NVIDIA_MODEL

LOGS_DIR = REPO_ROOT / "viewer" / "public" / "logs"


def fallback_episode(inputs: dict, slug: str) -> dict:
    """Formulaic, spoiler-free packaging when no LLM is available."""
    number = "".join(ch for ch in slug if ch.isdigit()) or "?"
    return {
        "title": f"Case {number}",
        "tagline": (
            f"{len(inputs['cast'])} AI players, {inputs['days']} day(s), "
            f"and somebody in the room is lying."
        ),
        "recap": "",
    }


def backfill_episode(log: dict, args: argparse.Namespace, slug: str) -> dict:
    inputs = episode_inputs_from_events(log["events"])
    if inputs is None:
        raise SystemExit("Log has no finished game (missing game_start/game_over).")

    if args.no_llm:
        return fallback_episode(inputs, slug)

    if args.nvidia:
        key = args.nvidia_key or os.environ.get("NVIDIA_API_KEY")
        if not key:
            raise SystemExit("--nvidia needs an API key via --nvidia-key or NVIDIA_API_KEY.")
        client = OpenAI(base_url=NVIDIA_API_URL, api_key=key)
        model = args.model or DEFAULT_NVIDIA_MODEL
    else:
        client = OpenAI(base_url=args.lm_studio_url, api_key="lm-studio")
        model = args.model or DEFAULT_MODEL

    gm = GameMaster(client=client, model=model, use_nvidia=args.nvidia)
    episode = gm.write_episode(**inputs)
    if not episode.get("title"):
        print("⚠️  GM call returned nothing — using formulaic metadata.")
        episode = fallback_episode(inputs, slug)
    return episode


def manifest_entry(log: dict, slug: str) -> dict:
    """Spoiler-free card data: never the winner, never anyone's role."""
    events = log["events"]
    start = next(e for e in events if e["type"] == "game_start")
    deaths = sum(
        1 for e in events
        if e["type"] == "elimination" or (e["type"] == "night_kill" and not e.get("saved"))
    )
    # --reveal-secrets logs carry private events and roles in game_start; the
    # homepage tags them so viewers know they'll see the mafia's side-channel.
    revealed = any(
        e["type"] in ("mafia_chat", "investigation", "protection") for e in events
    ) or any(p.get("role") for p in start["players"])
    return {
        "slug": slug,
        "title": log["episode"]["title"],
        "tagline": log["episode"]["tagline"],
        "cast": [{"name": p["name"], "color": p["color"]} for p in start["players"]],
        "days": log.get("day") or max((e.get("day") or 1) for e in events),
        "deaths": deaths,
        "revealed": revealed,
        **({"provider": start["provider"]} if start.get("provider") else {}),
    }


def main():
    parser = argparse.ArgumentParser(description="Publish a game log as a viewer episode")
    parser.add_argument("log", help="Path to a finished game_log.json")
    parser.add_argument("--slug", required=True, help="Episode slug, e.g. case-001")
    parser.add_argument("--nvidia", action="store_true", help="Backfill metadata via NVIDIA NIM")
    parser.add_argument("--nvidia-key", default=None)
    parser.add_argument("--lm-studio-url", default=LM_STUDIO_URL)
    parser.add_argument("--model", default=None)
    parser.add_argument("--no-llm", action="store_true", help="Skip LLM backfill, use formulaic metadata")
    args = parser.parse_args()

    load_dotenv()
    log = json.load(open(args.log))

    if not log.get("episode", {}).get("title"):
        print("📝 No episode metadata in log — backfilling...")
        log["episode"] = backfill_episode(log, args, args.slug)
    print(f"🎬 {log['episode']['title']} — {log['episode']['tagline']}")

    # Slim copy: the viewer only reads events/day/stats/episode; the raw
    # console logs are dev noise and double the file size.
    published = {k: log[k] for k in ("events", "day", "stats", "episode") if k in log}
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = LOGS_DIR / f"{args.slug}.json"
    with open(out_path, "w") as f:
        json.dump(published, f, indent=1)

    manifest_path = LOGS_DIR / "manifest.json"
    manifest = json.load(open(manifest_path)) if manifest_path.exists() else {"episodes": []}
    manifest["episodes"] = [e for e in manifest["episodes"] if e["slug"] != args.slug]
    manifest["episodes"].append(manifest_entry(published, args.slug))
    manifest["episodes"].sort(key=lambda e: e["slug"])
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=1)

    print(f"✅ Published {out_path.relative_to(REPO_ROOT)} ({out_path.stat().st_size // 1024} KB)")
    print(f"✅ Manifest now lists {len(manifest['episodes'])} episode(s). Commit + push to deploy.")


if __name__ == "__main__":
    main()
