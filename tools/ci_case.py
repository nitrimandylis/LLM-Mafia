"""Everything that happens to a game after the runner finishes playing it.

Usage:
    python tools/ci_case.py runs/2026-08-03-041501.json

Called once by .github/workflows/case.yml. In order: the mechanical gate, the
Claude review, deterministic validation of what the review returned, publish,
branch, PR, and a merge only when the review approved and validated. Always
exits 0 — a rejected episode is a normal outcome, not a broken job — so the
workflow only goes red when the game itself failed.

The reviewer can only ever cause a merge. It cannot publish a broken episode:
smells_wrong() runs before it and validate_verdict() runs after it, and both
fail closed.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from tools.run_batch import smells_wrong
from tools.publish_game import next_slug, read_manifest

SITE_URL = "https://llm-mafia.vercel.app"
REVIEW_MODEL = "opus"
REVIEW_TIMEOUT_SECONDS = 600

REVIEW_SYSTEM = """You are the editor of a library of AI-played Mafia episodes.
You are shown the full transcript of one finished game and the metadata card the
Game Master wrote for it. You decide whether the episode is worth publishing.

Judge three things, in this order.

1. Was the deception real? Did the mafia actually mislead the town, and was
   there a point where the reading of the room flipped? A game where the town
   simply guesses correctly is a transcript, not an episode.
2. Did the argument have substance? Did players reason about evidence and about
   each other, or did they restate a position and vote?
3. Is the card good? The brand is dry noir: understated, no exclamation marks,
   no hype. The tagline must be spoiler-free and must never name a player.

Criteria 1 and 2 decide `publish`. Criterion 3 never rejects a game — if the
card is weak, rewrite the title or the tagline and set `rewrote_metadata` to
true. If the card is already good, return it unchanged and set the flag false.

Reply with one JSON object and nothing else:

{"publish": true, "reasons": ["one line per criterion"],
 "title": "...", "tagline": "...", "rewrote_metadata": false}"""


def review_input(log):
    """What the reviewer sees: the transcript and the card, no console noise."""
    return json.dumps(
        {"episode": log.get("episode", {}), "events": log["events"]},
        indent=1,
    )


def call_reviewer(prompt):
    """One `claude -p` call. Returns the raw reply text, or None if it failed."""
    result = subprocess.run(
        [
            "claude", "-p", prompt,
            "--model", REVIEW_MODEL,
            "--system-prompt", REVIEW_SYSTEM,
            "--tools", "",
            "--setting-sources", "",
            "--strict-mcp-config",
        ],
        capture_output=True, text=True, timeout=REVIEW_TIMEOUT_SECONDS,
    )
    if result.returncode != 0:
        print(f"⚠️  Reviewer exited {result.returncode}: {result.stderr.strip()[:300]}")
        return None
    return result.stdout.strip()


def parse_verdict(reply):
    """The JSON object in the reply, or None. Models fence JSON often enough
    that it is worth stripping the fence rather than failing the run over it."""
    if not reply:
        return None
    text = reply.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1]
        if text.endswith("```"):
            text = text[: -len("```")]
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        return None
    try:
        return json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return None


def cast_names(log):
    for event in log["events"]:
        if event["type"] == "game_start":
            return [player["name"] for player in event["players"]]
    return []


def names_in_tagline(tagline, names):
    """Which cast members the tagline mentions. Whole words only, so a name
    like Al does not match 'always'."""
    found = []
    for name in names:
        if re.search(rf"\b{re.escape(name.lower())}\b", tagline.lower()):
            found.append(name)
    return found


def validate_verdict(verdict, names, gm_title, gm_tagline):
    """Every reason the verdict cannot be trusted. An empty list means it can.

    Fails closed: anything wrong here is treated as a rejection, never as an
    approval, so a malformed reply can never merge an episode.
    """
    problems = []
    if not isinstance(verdict, dict):
        return ["verdict is not a JSON object"]

    if not isinstance(verdict.get("publish"), bool):
        problems.append("publish is not a boolean")

    reasons = verdict.get("reasons")
    if not isinstance(reasons, list) or not reasons:
        problems.append("reasons is not a non-empty list")
    elif not all(isinstance(reason, str) and reason.strip() for reason in reasons):
        problems.append("reasons contains a non-string or empty entry")

    title = verdict.get("title")
    tagline = verdict.get("tagline")
    if not isinstance(title, str) or not title.strip():
        problems.append("title is empty or not a string")
    if not isinstance(tagline, str) or not tagline.strip():
        problems.append("tagline is empty or not a string")

    if verdict.get("rewrote_metadata") is True and isinstance(title, str) and isinstance(tagline, str):
        if title == gm_title and tagline == gm_tagline:
            problems.append("rewrote_metadata is true but nothing changed")

    # 0 of the 35 published taglines name a player, so a name in one is a
    # spoiler the library has never shipped. Titles are exempt: published ones
    # do reference roles, e.g. "The Doctor's Last Rounds".
    if isinstance(tagline, str):
        named = names_in_tagline(tagline, names)
        if named:
            problems.append(f"tagline names {', '.join(named)}")

    return problems


def notify(title, body, url=None):
    """One pointer-only push: a title, a line, a URL. Never contents.
    A failed push is logged, never fatal — the run already did its work."""
    topic = os.environ.get("NTFY_TOPIC")
    if not topic:
        print(f"NTFY_TOPIC unset, would have sent: {title} — {body}")
        return
    headers = {"Title": title, "Tags": "mafia"}
    if url:
        headers["Click"] = url
        body = f"{body}\n{url}"
    request = urllib.request.Request(
        f"https://ntfy.sh/{topic}", data=body.encode("utf-8"), headers=headers
    )
    try:
        urllib.request.urlopen(request, timeout=15)
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        print(f"⚠️  ntfy push failed: {error}")


def git(*command):
    subprocess.run(["git", *command], cwd=REPO_ROOT, check=True)


def open_pull_request(branch, slug, label, body):
    """Pushes the branch, opens the PR, returns its URL."""
    git("checkout", "-b", branch)
    git("add", "viewer/public/logs")
    git("commit", "-m", f"publish {slug}")
    git("push", "origin", branch)

    command = ["gh", "pr", "create", "--head", branch,
               "--title", f"publish {slug}", "--body", body]
    if label:
        # The label has to exist before it can be attached, and --force makes
        # this a no-op on every run after the first.
        subprocess.run(["gh", "label", "create", label, "--force"],
                       cwd=REPO_ROOT, check=False, capture_output=True)
        command += ["--label", label]
    result = subprocess.run(command, cwd=REPO_ROOT, check=True,
                            capture_output=True, text=True)
    return result.stdout.strip().splitlines()[-1]


def pr_body(verdict, problems, slug):
    lines = [f"Automated episode `{slug}`.", ""]
    if problems:
        lines.append("**Verdict failed validation — not merged.**")
        lines += [f"- {problem}" for problem in problems]
        lines.append("")
    if isinstance(verdict, dict):
        lines.append(f"publish: `{verdict.get('publish')}`")
        lines.append(f"rewrote_metadata: `{verdict.get('rewrote_metadata')}`")
        lines.append("")
        reasons = verdict.get("reasons")
        if isinstance(reasons, list):
            lines += [f"- {reason}" for reason in reasons if isinstance(reason, str)]
    else:
        lines.append("The reviewer returned nothing parseable.")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Review, publish and merge one finished game")
    parser.add_argument("log", help="Path to the finished game log in runs/")
    args = parser.parse_args()

    log_path = Path(args.log)
    log = json.loads(log_path.read_text())

    # The mechanical gate. A broken game is not an editorial decision, so the
    # reviewer is never asked about one.
    reasons = smells_wrong(log_path)
    if reasons:
        print(f"🛑 Mechanical gate: {', '.join(reasons)}")
        notify("Mafia: game rejected", f"smells_wrong: {', '.join(reasons)}",
               os.environ.get("RUN_URL"))
        return

    gm_title = log.get("episode", {}).get("title", "")
    gm_tagline = log.get("episode", {}).get("tagline", "")

    print("🔍 Reviewing...")
    verdict = parse_verdict(call_reviewer(review_input(log)))
    problems = validate_verdict(verdict, cast_names(log), gm_title, gm_tagline)
    approved = not problems and verdict["publish"]

    if problems:
        print(f"⚠️  Verdict failed validation: {', '.join(problems)}")
    else:
        print(f"📋 publish={verdict['publish']}")
        for reason in verdict["reasons"]:
            print(f"   - {reason}")

    # The card is only ever taken from a verdict that validated; otherwise the
    # GM's own metadata ships and a human decides on the PR.
    if not problems and verdict.get("rewrote_metadata"):
        log["episode"]["title"] = verdict["title"]
        log["episode"]["tagline"] = verdict["tagline"]
        log_path.write_text(json.dumps(log, indent=1))
        print(f"✏️  Card rewritten: {verdict['title']} — {verdict['tagline']}")

    slug = next_slug(read_manifest()["episodes"])
    subprocess.run(
        [sys.executable, "tools/publish_game.py", str(log_path), "--slug", slug, "--claude"],
        cwd=REPO_ROOT, check=True,
    )

    if approved:
        label = None
    elif problems:
        label = "unverified"
    else:
        label = "rejected"

    pr_url = open_pull_request(f"case/{slug}", slug, label, pr_body(verdict, problems, slug))
    print(f"🔗 {pr_url}")

    if not approved:
        notify("Mafia: episode needs a look",
               f"{slug} opened as `{label}`, not merged.", pr_url)
        return

    subprocess.run(["gh", "pr", "merge", pr_url, "--squash", "--delete-branch"],
                   cwd=REPO_ROOT, check=True)
    title = log["episode"]["title"]
    notify("Mafia: episode published", f"{slug} — {title}", SITE_URL)
    print(f"✅ Merged {slug}")


if __name__ == "__main__":
    main()
