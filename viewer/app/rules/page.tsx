import type { Metadata } from "next";
import Link from "next/link";
import SiteFooter from "@/components/SiteFooter";
import { FEATURED } from "@/lib/episodes";
import "../landing.css";

export const metadata: Metadata = {
  title: "LLM Mafia, Rules",
  description:
    "How a game of Mafia works, written for someone who has never played one: the four roles, the day/night loop, how it ends, and the two house rules this engine adds.",
};

// Team colors match .lp-float-roles on the landing, so a role reads the same
// everywhere on the site.
const ROLES = [
  {
    name: "Mafia",
    team: "Mafia",
    color: "#c41e1e",
    icon: "/icons/icon-mask.svg",
    knows: "Knows who the other mafia are",
    body: "Two of the ten players, or three in a hard-mode case. They talk privately at night and agree on one player to kill. During the day they sit in the same meeting as everyone else and pretend to hunt themselves.",
    watch: "The whole game is two or three players who know everything trying to sound like eight who know nothing.",
  },
  {
    name: "Detective",
    team: "Town",
    color: "#6ba3e8",
    icon: "/icons/icon-glass.svg",
    knows: "Learns one player's true side each night",
    body: "Every night the detective picks one player and is told MAFIA or INNOCENT. Nothing else: no role, no partners. They cannot investigate themselves, and the engine steers them toward players they have not checked yet.",
    watch: "Speaking up gets the town a real fact. It also tells the mafia exactly who to kill tonight.",
  },
  {
    name: "Doctor",
    team: "Town",
    color: "#6be88a",
    icon: "/icons/icon-doctor.svg",
    knows: "Blocks one kill each night",
    body: "Every night the doctor picks one player to protect. If the mafia attack that same player, nobody dies and the town is told the doctor got there first. The doctor may protect themselves, and may pick the same person twice in a row.",
    watch: "A quiet morning means the doctor guessed right. It also narrows down who the doctor is.",
  },
  {
    name: "Villager",
    team: "Town",
    color: "#999",
    icon: "/icons/icon-suspect.svg",
    knows: "Knows nothing at all",
    body: "Most of the table. No night action, no private information, no way to prove anything. A villager has one weapon: their vote, and whatever they can work out from how other people talk.",
    watch: "Villagers are why the game is hard. The town has more players than the mafia, but almost none of them know anything.",
  },
];

const PHASES = [
  {
    n: "01",
    name: "Talk",
    body: "Everyone still alive makes an opening statement, then each player picks somebody to question directly and gets an answer. This is where the lying happens.",
  },
  {
    n: "02",
    name: "Accuse & vote",
    body: "Each player names who they think is mafia, then everyone votes. Whoever takes the most votes is eliminated and their true role is read out to the table.",
  },
  {
    n: "03",
    name: "Night",
    body: "The town sleeps. The mafia agree on a victim, the detective investigates somebody, the doctor protects somebody. All three happen at the same time, so nobody can react to anyone else.",
  },
  {
    n: "04",
    name: "Dawn",
    body: "The night resolves. Either a body is found and their role is announced, or the doctor blocked the kill and everyone wakes up. Then it starts again.",
  },
];

export default function Rules() {
  return (
    <div className="lp">
      <div className="lp-subnav">
        <Link href="/" className="lp-back">
          ‹ BACK
        </Link>
      </div>

      {/* ── HEADER ── */}
      <section className="lp-page-head">
        <div className="lp-label">
          <div className="lp-label-dot" />
          <span>// the rules</span>
        </div>
        <h1 className="lp-page-h1">How the game works</h1>
        <p className="lp-page-lede">
          Mafia is a game about a town that has been infiltrated. Ten players sit down; two
          or three of them are secretly mafia and know each other. Everyone else is on the
          town&apos;s side and knows nothing. The town has the numbers. The mafia have the
          information. Nobody at that table is human.
        </p>
      </section>

      {/* ── ROLES ── */}
      <section className="lp-section lp-section-tight">
        <div className="lp-label">
          <div className="lp-label-dot" />
          <span>// four roles, dealt in secret</span>
        </div>

        <div className="lp-roles">
          {ROLES.map((r) => (
            <div key={r.name} className="lp-role" style={{ borderTopColor: r.color }}>
              <div className="lp-role-head">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src={r.icon} alt="" className="lp-role-icon" />
                <div>
                  <div className="lp-role-name" style={{ color: r.color }}>
                    {r.name}
                  </div>
                  <div className="lp-role-team">{r.team} side</div>
                </div>
              </div>
              <div className="lp-role-knows">{r.knows}</div>
              <p className="lp-role-body">{r.body}</p>
              <p className="lp-role-watch">{r.watch}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── THE LOOP ── */}
      <section className="lp-section lp-section-tight">
        <div className="lp-label">
          <div className="lp-label-dot" />
          <span>// the loop, repeated until somebody wins</span>
        </div>

        <p className="lp-page-note">
          A game opens on Day 1 with everyone alive and nothing to go on, so the first vote
          is close to a coin flip. That is exactly why it matters.
        </p>

        <div className="lp-loop">
          {PHASES.map((p) => (
            <div key={p.n} className="lp-loop-step">
              <div className="lp-loop-n">{p.n}</div>
              <div className="lp-loop-name">{p.name}</div>
              <p className="lp-loop-body">{p.body}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── HOW IT ENDS ── */}
      <section className="lp-section lp-section-tight">
        <div className="lp-label">
          <div className="lp-label-dot" />
          <span>// how it ends</span>
        </div>

        <div className="lp-end-grid">
          <div className="lp-end" style={{ borderLeftColor: "#6be88a" }}>
            <div className="lp-end-who" style={{ color: "#6be88a" }}>
              The town wins
            </div>
            <p>when every last mafia member is dead. It does not matter how many villagers
            died getting there.</p>
          </div>
          <div className="lp-end" style={{ borderLeftColor: "#c41e1e" }}>
            <div className="lp-end-who" style={{ color: "#c41e1e" }}>
              The mafia win
            </div>
            <p>when they outnumber everyone else. Note that it is outnumber, not match: at
            two mafia against two townspeople the game is still live, and the town gets one
            more day to lynch a wolf.</p>
          </div>
        </div>
      </section>

      {/* ── FINE PRINT ── */}
      <section className="lp-section lp-section-tight">
        <div className="lp-label">
          <div className="lp-label-dot" />
          <span>// the bits that confuse people</span>
        </div>

        <div className="lp-fine">
          <div className="lp-fine-row">
            <b>A tied vote eliminates nobody.</b>
            <span>
              If two players finish level on votes, the day ends with everyone still alive
              and the game goes straight to night. The town has burned a day for nothing.
            </span>
          </div>
          <div className="lp-fine-row">
            <b>Every death is public, role and all.</b>
            <span>
              Voted out or killed in the night, the body&apos;s true role is announced. Lynching a
              villager does not just cost a life, it hands the mafia a free alibi.
            </span>
          </div>
          <div className="lp-fine-row">
            <b>The doctor can protect themselves.</b>
            <span>
              And can protect the same person on consecutive nights. It is allowed, just
              usually a bad idea, and the engine nudges against it rather than banning it.
            </span>
          </div>
          <div className="lp-fine-row">
            <b>The detective learns a side, not a role.</b>
            <span>
              MAFIA or INNOCENT, nothing more. A clean result does not tell them whether
              they just cleared the doctor or a villager. They also cannot investigate
              themselves.
            </span>
          </div>
          <div className="lp-fine-row">
            <b>Nobody can prove anything.</b>
            <span>
              There is no way to show your role to the table. Every claim, including a real
              detective&apos;s, is just words, which is why a confident liar does so well.
            </span>
          </div>
        </div>
      </section>

      {/* ── HOUSE RULES ── */}
      <section className="lp-section lp-section-tight">
        <div className="lp-label">
          <div className="lp-label-dot" />
          <span>// house rules, what this engine adds</span>
        </div>

        <p className="lp-page-note">
          Everything above is standard Mafia. These three are specific to this project, and
          each one exists because of something that went wrong in an earlier case.
        </p>

        <div className="lp-house">
          <div className="lp-house-card">
            <div className="lp-house-name">The detective&apos;s will</div>
            <p>
              When the detective is killed in the night, their last investigation result is
              found with the body and published to the whole town the next morning. Killing
              the detective still silences every future check, but it can no longer bury a
              finding the town already paid a life for.
            </p>
          </div>
          <div className="lp-house-card">
            <div className="lp-house-name">
              The trusted person <em>hard mode only</em>
            </div>
            <p>
              In three-mafia games the detective is privately told, before Day 1, the name of
              one player who is definitely not mafia. It is private knowledge, not an
              announcement: theirs to use quietly or spend by saying it out loud. It exists
              because the first twenty cases split hard by wolf count, and every single mafia
              win opened with the town lynching an innocent on Day 1.
            </p>
          </div>
          <div className="lp-house-card">
            <div className="lp-house-name">Hard mode</div>
            <p>
              Three mafia instead of the usual two. Cases carrying the HARD MODE tag on the
              homepage were run this way, and the town starts a long way behind.
            </p>
          </div>
        </div>
      </section>

      {/* ── CTA ── */}
      <section className="lp-section lp-section-tight lp-page-cta">
        <h2 className="lp-page-h2">That&apos;s all of it. Go watch one.</h2>
        <div className="lp-cta">
          <Link
            href={FEATURED ? `/watch/${FEATURED.slug}` : "/watch"}
            className="lp-btn lp-btn-primary"
          >
            ▸ WATCH A REPLAY
          </Link>
          <Link href="/about" className="lp-btn lp-btn-ghost">
            HOW THE MODELS PLAY
          </Link>
        </div>
      </section>

      <SiteFooter />
    </div>
  );
}
