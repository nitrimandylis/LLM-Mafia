# Auto-cases: unattended game production in GitHub Actions

Date: 2026-08-03
Status: approved, not built
Branch: `auto-cases`

## Problem

Producing an episode takes a laptop with the lid open. `tools/run_batch.py`
plays games unattended but only while `caffeinate` holds the machine awake, and
publishing is a separate manual step afterwards. The library grows only when
Nick sits down to grow it.

Claude Code runs in GitHub Actions on a `CLAUDE_CODE_OAUTH_TOKEN`, so the games
can be played on a runner instead. The open question was never "can it run",
it was "what stops a bad episode from shipping when nobody is watching".

## Locked decisions

1. **Claude backend**, not NVIDIA. Provenance stays consistent with the 31 of 35
   published cases that are Claude-played, and `tools/balance_report.py` never
   reads `provider`, so a parallel NVIDIA stream would silently pool two model
   populations into the win rates that gate house-rule changes.
2. **One game per run.** The quota guard in `run_batch.py` exists because a
   batch plays N games back to back and running out mid-game wastes everything
   already spent. At one game per run its job is nearly gone: the worst case is
   losing that single game. Cron supplies the batching, spread across weeks.
   This deletes the Keychain problem rather than solving it.
3. **Weekly cadence**, early morning, clock-guarded.
4. **Claude reviews and merges.** A PR per game, auto-merged when the reviewer
   approves. The PR is the diff, the verdict record, and the revert button.
5. **A weak card does not kill a good game.** The reviewer rewrites a flat
   title or tagline instead of rejecting the episode behind it.
6. **ntfy on every run that plays a game**, including success. A clock-guard
   bail plays nothing and stays silent.

## Why one job and not two

A pull request opened by `GITHUB_TOKEN` does not trigger other workflows.
GitHub blocks it to prevent recursion. A "workflow opens PR, review workflow
fires" split therefore needs a personal access token and a second workflow file.
One job that plays, publishes, opens the PR and merges it uses the default token
and has no cross-workflow trigger at all.

## Design

`.github/workflows/case.yml`, one job, weekly cron plus `workflow_dispatch`.

### Steps

1. Checkout. `setup-python`, `pip install -r requirements.txt` (openai,
   python-dotenv, pillow). `npm install -g @anthropic-ai/claude-code`.
2. **Clock guard.** Exit clean if the current Athens hour is outside 03:00 to
   07:00. GitHub delays scheduled runs under load, and a game that starts at
   09:00 spends a five-hour window Nick is trying to use. A skipped week costs
   one episode. Manual `workflow_dispatch` runs skip the guard.
3. `python tools/run_batch.py --games 1 --no-wait --mafia 3`, writing to the
   gitignored `runs/`. Three mafia is the config the trusted-person buff is
   being measured on.
4. **Deterministic floor.** `smells_wrong()` from `run_batch.py`, unchanged:
   fallback lines, no `game_over` event, or a game that ended on day 1. Any
   reason and the run stops here. The log uploads as a workflow artifact, ntfy
   fires, the job exits clean, and no PR is opened. A mechanically broken game
   is not an editorial decision and Claude is never asked about one.
5. **Review.** One `claude -p` call over the log (roughly 77 KB, about 20k
   tokens, negligible beside the game that produced it). Returns JSON, validated
   before use. Criteria below.
6. Apply any metadata rewrite to the log, then shell out to
   `tools/publish_game.py runs/<file> --claude`.
7. Branch `case/<date>`, commit the published log and the manifest change,
   `gh pr create` with the verdict in the body.
8. On approval, `gh pr merge --squash --delete-branch`. Vercel deploys from
   `main`.
9. ntfy.

Steps 4 through 9 all live in `tools/ci_case.py`, invoked once by the workflow
after the game finishes. The workflow file stays a thin wrapper: install, guard,
play, hand off. `publish_game.py` is called as a subprocess and is not modified.

### Reviewer contract

The reviewer sees the log and the GM's existing `episode` block. It judges
three things, in this order:

- **Was the deception real?** Did the mafia actually mislead the town, and was
  there a point where the reading of the room flipped? A game where the town
  simply guesses correctly is a transcript, not an episode.
- **Did the argument have substance?** Did players reason about evidence and
  about each other, or restate a position and vote? This is the criterion
  `smells_wrong()` cannot express: a game can be mechanically perfect and dull.
- **Is the card good?** Dry noir per the brand, and spoiler-free. This one never
  rejects the game. It rewrites.

Returns:

```json
{
  "publish": true,
  "reasons": ["one line per criterion"],
  "title": "...",
  "tagline": "...",
  "rewrote_metadata": false
}
```

Validation, all of it deterministic and all of it failing closed:

- `publish` is a boolean, `reasons` is a non-empty list of strings.
- `title` and `tagline` are non-empty strings.
- If `rewrote_metadata` is true, at least one of them differs from the GM's.
- **`tagline` contains no player's name.** Checked against the `game_start`
  cast. Verified against the library: 0 of 35 published taglines name a player,
  so this catches the realistic spoiler without a classifier. Titles are exempt,
  since published titles do reference roles ("The Doctor's Last Rounds").
- Anything failing validation is treated as a rejection, never as an approval.

A rewritten tagline does not earn `exclude_from_stats`. That flag marks games
whose gameplay text was edited, so the outcome was decided by us rather than the
players. A card is not gameplay text.

### Failure modes

| What happened | Result |
| --- | --- |
| Clock guard bailed | Silent, visible in the Actions tab only |
| Game aborted, exit 2 | Job fails, ntfy, nothing published |
| `smells_wrong` returned reasons | Artifact plus ntfy, no PR |
| Reviewer returned `publish: false` | PR open, labeled `rejected`, not merged |
| Verdict failed validation | PR open, labeled `unverified`, not merged |
| Reviewer approved | PR merged, episode live, ntfy |

The reviewer can only ever cause a merge. It has no path to publishing a broken
episode, because the mechanical gate runs before it and the validator runs after
it. This mirrors the managebac classifier in `siren`, where a rejected verdict
files untriaged and the deterministic path is the floor.

### Notifications

One push per run to the existing `jobs-` class topic, tagged `mafia`. Per the
standing rule, payloads are pointers: a title and a URL, never contents. Success
sends the episode title and the site URL; every other path sends the reason and
the PR or run URL.

## What gets built

| File | Change |
| --- | --- |
| `.github/workflows/case.yml` | New. The job above. |
| `tools/ci_case.py` | New. Review, validate, rewrite, publish, PR, merge. JSON validation in shell is misery, so this is Python. |
| `tools/claude_usage.py` | Three lines. See below. |
| `.gitignore` | `docs/` becomes `docs/*` plus `!docs/specs/`. |

### The `claude_usage.py` bug

`read_access_token()` calls `subprocess.run(["security", ...])` with no
exception handling. On a Linux runner there is no `security` binary, so this
raises `FileNotFoundError` instead of returning `None`, and it takes
`run_batch.py` down with it before a single game is played. The function's
docstring already promises `None` when the Keychain entry is missing; this makes
that true when the Keychain itself is missing. Catch `FileNotFoundError` and
return `None`.

### Check left behind

Assertions in `ci_case.py` under `__main__`, matching the pattern
`claude_usage.py` already uses: the verdict validator accepts a well-formed
approval, and rejects each of a non-boolean `publish`, an empty `reasons`, an
empty `title`, and a tagline naming a cast member. No framework, no fixtures.

## Known limits, accepted rather than solved

- **The reviewer reads the log, not the episode.** Pacing is Design Principle 3
  and the reviewer cannot see it: no dwell times, no death beats, no stings. It
  judges a transcript. A game that reads well and plays slowly still ships.
- **Slug collision.** `publish_game.py` takes the next free slug from the
  manifest on `main`. A rejected PR left open for a week means the following run
  claims the same slug and git reports a conflict at merge time. The fix is to
  close rejected PRs. Slug reservation is not worth building for a weekly job.
- **Game length is unmeasured.** Roughly 250 `claude -p` calls at up to 180
  seconds each is a wide range. `timeout-minutes: 180`, well under the six-hour
  job ceiling. The first real run replaces this guess with a number.
- **Quota contention is designed around, not eliminated.** One game costs 16 to
  33 percent of a five-hour window. A 04:00 run has reset by 09:00. The clock
  guard is what keeps that true when cron drifts.

## Secrets and permissions

Nick sets both secrets himself.

- `CLAUDE_CODE_OAUTH_TOKEN` from `claude setup-token`. Expires after a year and
  dies silently. Never set `ANTHROPIC_API_KEY` in the same job: it takes
  precedence and would be sent as an `X-Api-Key` header.
- `NTFY_TOPIC`, the existing `jobs-` class topic.

Workflow permissions: `contents: write`, `pull-requests: write`.
