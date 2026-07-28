"""Check every quote on the About page against the log it cites.

    python tools/check_about_quotes.py

The page tells readers the quotes are verbatim, so this makes that claim
testable: each entry's text must appear in the named case log, spoken by the
named player, on the named day, and their role must match stats.players.
An ellipsis marks a trim, so text is matched piece by piece rather than whole.
"""

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGE = ROOT / "viewer" / "app" / "about" / "page.tsx"
LOGS = ROOT / "viewer" / "public" / "logs"

# Each quote object in FAILURES, in source order.
ENTRY = re.compile(
    r'slug:\s*"(?P<slug>[^"]+)",\s*'
    r'day:\s*(?P<day>\d+),\s*'
    r'who:\s*"(?P<who>[^"]+)",\s*'
    r'role:\s*"(?P<role>[^"]+)",\s*'
    r'text:\s*"(?P<text>(?:[^"\\]|\\.)*)"',
    re.S,
)


def main() -> int:
    entries = [m.groupdict() for m in ENTRY.finditer(PAGE.read_text())]
    if not entries:
        print("no quotes found — did the FAILURES shape change?")
        return 1

    failures = []
    for e in entries:
        log = json.loads((LOGS / f"{e['slug']}.json").read_text())
        where = f"{e['slug']} {e['who']} day {e['day']}"

        role = log.get("stats", {}).get("players", {}).get(e["who"], {}).get("role")
        if role != e["role"]:
            failures.append(f"{where}: page says {e['role']}, log says {role}")

        said = [
            ev.get("text", "")
            for ev in log["events"]
            if ev.get("actor") == e["who"] and ev.get("day") == int(e["day"])
        ]
        # Unescape the TS string literal, then require every un-trimmed run to
        # sit in one single utterance.
        text = e["text"].replace('\\"', '"').replace("\\\\", "\\")
        runs = [r.strip() for r in text.split("…") if r.strip()]
        if not any(all(run in utterance for run in runs) for utterance in said):
            failures.append(f"{where}: no utterance contains {runs[0][:60]!r}")

    for f in failures:
        print("MISMATCH:", f)
    print(f"{len(entries)} quotes checked, {len(failures)} mismatched")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
