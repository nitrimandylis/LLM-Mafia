import type { Metadata } from "next";
import Link from "next/link";
import SiteFooter, { GITHUB } from "@/components/SiteFooter";
import { EPISODES, FEATURED } from "@/lib/episodes";
import "../landing.css";

export const metadata: Metadata = {
  title: "About — LLM Mafia",
  description:
    "Why Mafia is a hard test for a language model, how each game is actually run, what the models turn out to be bad at, and who built this.",
};

// Verbatim moments pulled from viewer/public/logs/case-*.json. Every quote here
// is checkable against the replay it links to — never paraphrase into this list.
type Failure = {
  mode: string;
  blurb: string;
  quotes: { slug: string; caseNo: string; day: number; who: string; role: string; text: string; why: string }[];
};

const FAILURES: Failure[] = [];

export default function About() {
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
          <span>// about</span>
        </div>
        <h1 className="lp-page-h1">Ten language models, one game they cannot bluff their way through.</h1>
        <p className="lp-page-lede">
          Every case on this site is a full game of Mafia played by language models with no
          human at the table. Nothing is scripted and nothing is edited. The engine deals
          the roles, asks each model what it wants to say, and writes down what happened.
          What follows is why that is a harder test than it sounds, and how it actually
          runs.
        </p>
      </section>

      {/* ── WHY MAFIA ── */}
      <section className="lp-section lp-section-tight">
        <div className="lp-label">
          <div className="lp-label-dot" />
          <span>// why Mafia tests a model at all</span>
        </div>

        <div className="lp-prose">
          <p>
            Most ways of testing a model ask it a question that has an answer. Mafia does
            not. It asks a model to hold a belief about what nine other players believe, act
            on it in front of them, and stay consistent while everyone else is trying to
            make it look guilty.
          </p>
          <p>
            That pulls on three things at once. A mafia player has to model other minds:
            what does the town already suspect, and what will this sentence make them think?
            It has to deceive on purpose and keep the story straight for days, because a
            lie told on Day 1 is still on the record on Day 4. And the whole table has to
            stay consistent across a growing transcript, where the cheapest mistake in the
            world is forgetting who is dead.
          </p>
          <p>
            None of that can be faked for long. A model that is only pattern-matching says
            something agreeable, gets asked why, and falls apart. Five days is enough rope.
          </p>
        </div>
      </section>

      {/* ── HOW A GAME RUNS ── */}
      <section className="lp-section lp-section-tight">
        <div className="lp-label">
          <div className="lp-label-dot" />
          <span>// how a game is actually run</span>
        </div>

        <div className="lp-prose">
          <p>
            Ten fixed personas sit in ten seats. The engine shuffles the roles, tells the
            mafia who their partners are, and starts Day 1.
          </p>
        </div>

        <div className="lp-mech">
          <div className="lp-mech-row">
            <b>Every turn is a fresh call</b>
            <span>
              The models have no memory between turns. Before each one the engine rebuilds
              the whole game state from the log and pastes it into a system prompt: the
              shared instructions, that seat&apos;s personality, that seat&apos;s secret role, and
              everything publicly known so far. The model answers, and the context is thrown
              away. Every apparent act of remembering is really the engine handing the
              transcript back.
            </span>
          </div>
          <div className="lp-mech-row">
            <b>Each seat sees a different world</b>
            <span>
              A mafia player&apos;s prompt names their partners. The detective&apos;s carries their
              private notes, one line per investigation. A villager gets nothing but the
              public record. That asymmetry is the entire game, and it is enforced at the
              prompt, not by asking the models to behave.
            </span>
          </div>
          <div className="lp-mech-row">
            <b>Think privately, then speak</b>
            <span>
              The instructions tell each model to plan first and then reply with only the
              words its character says out loud, and hard-ban it from stating its own role
              or admitting it is an AI. What ships to the other players is the spoken line.
              Scheming stays where the table cannot read it.
            </span>
          </div>
          <div className="lp-mech-row">
            <b>A day has four beats</b>
            <span>
              Opening statements from everyone alive, then cross-examination where each
              player questions somebody and gets an answer, then a round of accusations,
              then the vote. Turn order is shuffled each day so nobody gets the last word
              twice.
            </span>
          </div>
          <div className="lp-mech-row">
            <b>Night runs in parallel</b>
            <span>
              The mafia&apos;s kill, the detective&apos;s investigation and the doctor&apos;s protection
              are all requested at the same time, so none of them can react to the others.
              The results are resolved afterwards.
            </span>
          </div>
          <div className="lp-mech-row">
            <b>Votes are parsed out of plain speech</b>
            <span>
              Nobody submits a ballot. The model writes a sentence and the engine digs the
              name out of it, preferring explicit intent (&quot;I&apos;m voting HOLMES&quot;) over any name
              that merely appears, so discussing somebody else&apos;s vote does not hijack your
              own. Names that could mean two players are dropped rather than guessed.
            </span>
          </div>
          <div className="lp-mech-row">
            <b>A game master narrates</b>
            <span>
              A separate model writes the morning narration, the death lines and, at the
              end, the case title, the spoiler-free tagline and the post-mortem you see on
              the recap card. It reports the game. It never plays in it.
            </span>
          </div>
        </div>

        <p className="lp-page-note lp-page-note-after">
          The engine is Python and writes a structured <code>events[]</code> stream to{" "}
          <code>game_log.json</code>. Everything on this site is that file, replayed. All{" "}
          {EPISODES.length} cases are in the repo.
        </p>
      </section>

      {/* ── FAILURE MODES ── */}
      {FAILURES.length > 0 && (
        <section className="lp-section lp-section-tight">
          <div className="lp-label">
            <div className="lp-label-dot" />
            <span>// what the models are bad at</span>
          </div>

          <p className="lp-page-note">
            Every quote below is verbatim from a case on this site, with the speaker&apos;s real
            role attached. Nothing here is reconstructed.
          </p>

          <div className="lp-fails">
            {FAILURES.map((f) => (
              <div key={f.mode} className="lp-fail">
                <div className="lp-fail-mode">{f.mode}</div>
                <p className="lp-fail-blurb">{f.blurb}</p>
                {f.quotes.map((q) => (
                  <figure key={q.caseNo + q.who + q.text.slice(0, 12)} className="lp-quote">
                    <blockquote>{q.text}</blockquote>
                    <figcaption>
                      <Link href={`/watch/${q.slug}`}>
                        {q.caseNo} · DAY {q.day}
                      </Link>
                      <span className="sep">│</span>
                      {q.who} <em>({q.role})</em>
                      <span className="lp-quote-why">{q.why}</span>
                    </figcaption>
                  </figure>
                ))}
              </div>
            ))}
          </div>
        </section>
      )}

      {/* ── WHO ── */}
      <section className="lp-section lp-section-tight">
        <div className="lp-label">
          <div className="lp-label-dot" />
          <span>// who built this</span>
        </div>

        <div className="lp-prose">
          <p>
            I&apos;m Nick Trimandylis. I wanted to know whether models that are relentlessly
            agreeable when you talk to them one-on-one would actually lie to each other when
            winning required it, so I built a table and sat them at it. They lie. That is
            most of the answer, and the rest is on this site.
          </p>
          <p>
            The engine, the viewer and every case log are open source under the MIT licence.
            If you have a local model, you can run your own games with it.
          </p>
        </div>

        <div className="lp-cta lp-cta-spaced">
          <a href={GITHUB} target="_blank" rel="noreferrer" className="lp-btn lp-btn-primary">
            VIEW ON GITHUB
          </a>
          <Link
            href={FEATURED ? `/watch/${FEATURED.slug}` : "/watch"}
            className="lp-btn lp-btn-ghost"
          >
            ▸ WATCH A REPLAY
          </Link>
        </div>
      </section>

      <SiteFooter />
    </div>
  );
}
