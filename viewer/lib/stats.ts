import fs from "node:fs";
import path from "node:path";
import { EPISODES } from "./episodes";

// Totals for the landing page's record strip, counted once per server process
// (module scope, not per request) over every published log.
//
// exclude_from_stats is deliberately ignored here. That flag exists so a
// hand-edited log can't skew the win rate in tools/balance_report.py; none of
// these numbers is a win rate, and the case is listed on the page either way.

const LOGS_DIR = path.join(process.cwd(), "public", "logs");

// What a player says out loud, plus the mafia's private channel.
const SPEECH = ["statement", "question", "answer", "accusation", "mafia_chat"];

type Event = {
  type: string;
  target?: string;
  role?: string;
  text?: string;
};

function countStats() {
  let words = 0;
  let bodies = 0;
  let hangings = 0;
  let innocentsHanged = 0;
  const accusations = new Map<string, number>();

  for (const episode of EPISODES) {
    const file = path.join(LOGS_DIR, `${episode.slug}.json`);
    const log = JSON.parse(fs.readFileSync(file, "utf8"));
    const events: Event[] = log.events;

    for (const event of events) {
      if (SPEECH.includes(event.type)) {
        words += (event.text ?? "").split(/\s+/).filter(Boolean).length;
      } else if (event.type === "elimination") {
        bodies += 1;
        hangings += 1;
        if (event.role !== "Mafia") {
          innocentsHanged += 1;
        }
      } else if (event.type === "night_kill") {
        bodies += 1;
      }

      // Counted separately from the elimination branch: an accusation is a
      // speech act, and most of them never lead to a hanging.
      if (event.type === "accusation" && event.target) {
        accusations.set(event.target, (accusations.get(event.target) ?? 0) + 1);
      }
    }
  }

  // The running gag, whoever it currently is. SOCRATES leads today; RICO is
  // four accusations behind, so this name can change on its own.
  let mostAccused = "";
  let mostAccusedCount = 0;
  for (const [name, count] of accusations) {
    if (count > mostAccusedCount) {
      mostAccused = name;
      mostAccusedCount = count;
    }
  }

  return {
    cases: EPISODES.length,
    humans: 0,
    words,
    bodies,
    wordsPerCorpse: Math.round(words / bodies),
    innocentsHanged,
    hangings,
    mostAccused,
    mostAccusedCount,
  };
}

export const STATS = countStats();
