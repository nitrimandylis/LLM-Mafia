import type { Metadata } from "next";
import Link from "next/link";
import { EPISODES, FEATURED, caseNumber, PROVIDER_COLORS, type EpisodeCard } from "@/lib/episodes";
import "./landing.css";

export const metadata: Metadata = {
  title: "LLM Mafia — every player is a language model",
  description:
    "Watch AI players lie, accuse, and vote each other out — replayed as a group chat, a detective's case file, a court transcript, or a live suspicion graph.",
};

const GITHUB = "https://github.com/nitrimandylis/LLM-Mafia";

// Real skins, pulled from viewer/lib/settings.ts (kept in sync with the app).
const SKINS = [
  {
    name: "Group Chat",
    blurb:
      "A messaging thread: grouped bubbles, day/night theming, votes folded into a ballot strip, mafia in a locked side-channel.",
  },
  {
    name: "Case File",
    blurb:
      "You're the detective. Typed testimony on manila paper, suspect ID cards, and intercepted mafia comms stamped DECLASSIFIED.",
  },
  {
    name: "Transcript",
    blurb:
      "A line-numbered court deposition. Votes become a typeset ballot exhibit; the eliminated are stricken from the record.",
  },
  {
    name: "Signal",
    blurb:
      "An instrument panel. A live suspicion graph wires up every accusation and vote, then ignites the mafia at the reveal.",
  },
];

export default function Landing() {
  return (
    <div className="lp">
      {/* ── HERO ── */}
      <section className="lp-hero">
        <div className="lp-col">
          <div className="lp-logo">
            <span className="l1">LLM</span>
            <br />
            <span className="l2">MAFIA</span>
          </div>

          <div className="lp-tagline">NO HUMANS. PURE MODEL-VS-MODEL DECEPTION.</div>

          <p className="lp-desc">
            Watch AI players lie, accuse, and vote each other out — replayed as a tense
            group chat, a detective&apos;s case file, a court transcript, or a live
            suspicion graph.
          </p>

          <div className="lp-cta">
            <Link
              href={FEATURED ? `/watch/${FEATURED.slug}` : "/watch"}
              className="lp-btn lp-btn-primary"
            >
              ▸ WATCH A REPLAY
            </Link>
            <a href={GITHUB} target="_blank" rel="noreferrer" className="lp-btn lp-btn-ghost">
              VIEW ON GITHUB
            </a>
          </div>
        </div>

        {/* terminal preview */}
        <div className="lp-term-wrap">
          <div className="lp-term">
            <div className="lp-term-bar">
              <div className="lp-dot on" />
              <div className="lp-dot" />
              <div className="lp-dot" />
              <span className="file">game_log.json — viewer</span>
            </div>
            <div className="lp-term-body">
              <div className="cmt">// replay — day 2 town meeting</div>
              <div>
                <span className="lp-n-red">HOLMES</span>
                <span className="meta"> › </span>
                <span className="said">ARIA&apos;s defense of RICO felt too rehearsed.</span>
              </div>
              <div>
                <span className="lp-n-blue">SOCRATES</span>
                <span className="meta"> → PIP › </span>
                <span className="said">Why did you change your vote?</span>
              </div>
              <div>
                <span className="lp-n-amber">MARSHAL</span>
                <span className="meta"> › </span>
                <span className="said">Voting ARIA. The pattern doesn&apos;t add up.</span>
              </div>
              <div>
                <span className="lp-n-red">SAGE</span>
                <span className="meta"> › </span>
                <span className="said">I agree with HOLMES — something is off.</span>
              </div>
              <div style={{ marginTop: 4 }}>
                <span className="meta">❯</span>
                <span className="lp-cursor"> █</span>
              </div>
            </div>
          </div>

          <div className="lp-float lp-float-roles">
            <span className="lp-n-red">● MAFIA</span>
            <span className="lp-n-blue">● DETECTIVE</span>
            <span style={{ color: "#6be88a" }}>● DOCTOR</span>
            <span style={{ color: "#999" }}>● VILLAGER</span>
          </div>

          <div className="lp-float lp-float-votes">
            <span style={{ color: "#888" }}>VOTES</span>
            <span style={{ color: "var(--accent)", fontWeight: 700 }}>ARIA ████░ 4</span>
            <span style={{ color: "#999" }}>PIP ██░░░ 2</span>
          </div>
        </div>
      </section>

      {/* ── EPISODES — the case files ── */}
      <section className="lp-section" id="cases">
        <div className="lp-label">
          <div className="lp-label-dot" />
          <span>// the case files — {EPISODES.length} on record</span>
        </div>

        {FEATURED && (
          <Link href={`/watch/${FEATURED.slug}`} className="lp-ep-featured">
            <div className="lp-ep-left">
              <div className="lp-ep-no">
                {caseNumber(FEATURED.slug)} <em>· LATEST</em>
                {FEATURED.hard && <HardTag />}
                {FEATURED.revealed && <RevealedTag />}
              </div>
              <h3 className="lp-ep-title">{FEATURED.title}</h3>
              <p className="lp-ep-tag">{FEATURED.tagline}</p>
              <span className="lp-ep-watch">▸ WATCH THE CASE</span>
            </div>
            <div className="lp-ep-right">
              <div className="lp-ep-castlist">
                {FEATURED.cast.map((p) => (
                  <span key={p.name} className="lp-ep-cast-chip">
                    <span className="dot" style={{ background: p.color }} />
                    {p.name}
                  </span>
                ))}
              </div>
              <EpisodeMetaLine ep={FEATURED} />
            </div>
          </Link>
        )}

        <div className="lp-ep-grid">
          {EPISODES.slice(0, -1)
            .reverse()
            .map((ep) => (
              <Link key={ep.slug} href={`/watch/${ep.slug}`} className="lp-ep">
                <div className="lp-ep-no">
                  {caseNumber(ep.slug)}
                  {ep.hard && <HardTag />}
                  {ep.revealed && <RevealedTag />}
                </div>
                <h3 className="lp-ep-title">{ep.title}</h3>
                <p className="lp-ep-tag">{ep.tagline}</p>
                <EpisodeMetaLine ep={ep} />
              </Link>
            ))}
        </div>
      </section>

      {/* ── SKINS ── */}
      <section className="lp-section">
        <div className="lp-label">
          <div className="lp-label-dot" />
          <span>// Four ways to watch</span>
        </div>

        <div className="lp-skins">
          <SkinCard skin={SKINS[0]}>
            <div className="lp-card-preview pv-chat">
              <div><span className="who-red">HOLMES:</span> <span className="msg">I suspect ARIA.</span></div>
              <div><span className="who-blue">PIP:</span> <span className="msg">That&apos;s baseless.</span></div>
              <div><span className="who-amber">MARSHAL:</span> <span className="msg">I&apos;m with HOLMES.</span></div>
              <div><span className="who-red">SAGE:</span> <span className="msg">Let&apos;s not rush.</span></div>
            </div>
          </SkinCard>

          <SkinCard skin={SKINS[1]}>
            <div className="lp-card-preview pv-case">
              <div className="stamp">DECLASSIFIED</div>
              <div className="line">SUSPECT: <b>ARIA</b></div>
              <div className="line">Testimony inconsistent across Day 1–2.</div>
              <div className="line">Detective check: <b>pending</b></div>
            </div>
          </SkinCard>

          <SkinCard skin={SKINS[2]}>
            <div className="lp-card-preview pv-tx">
              <div className="row"><span className="ln">041</span><span><span className="q">Q.</span> Where were you on night one?</span></div>
              <div className="row"><span className="ln">042</span><span>A. Asleep. I have no role to hide.</span></div>
              <div className="row"><span className="ln">043</span><span className="strike">PIP voted out — struck.</span></div>
              <div className="row"><span className="ln">044</span><span>BALLOT EXHIBIT C — ARIA: 4</span></div>
            </div>
          </SkinCard>

          <SkinCard skin={SKINS[3]}>
            <div className="lp-card-preview pv-sig">
              <svg viewBox="0 0 260 150" preserveAspectRatio="xMidYMid meet" aria-hidden="true">
                <g stroke="#0e7c86" strokeWidth="1.2" opacity="0.55">
                  <line x1="60" y1="40" x2="150" y2="70" />
                  <line x1="200" y1="35" x2="150" y2="70" />
                  <line x1="70" y1="115" x2="150" y2="70" />
                  <line x1="205" y1="110" x2="150" y2="70" />
                  <line x1="60" y1="40" x2="70" y2="115" />
                </g>
                <g fill="#0e7c86">
                  <circle cx="60" cy="40" r="5" />
                  <circle cx="200" cy="35" r="5" />
                  <circle cx="70" cy="115" r="5" />
                  <circle cx="205" cy="110" r="5" />
                </g>
                <circle cx="150" cy="70" r="8" fill="#c41e1e" />
              </svg>
              <div className="label">Suspicion graph · live</div>
            </div>
          </SkinCard>
        </div>
      </section>

      {/* ── PIPELINE ── */}
      {/* No eyebrow here — the big statement heading leads the section itself. */}
      <section className="lp-section pipeline">
        <div className="lp-pipe-grid">
          <div>
            <div className="lp-pipe-h">
              The engine plays.
              <br />
              The viewer dramatizes.
            </div>
            <p className="lp-pipe-p">
              A Python engine runs the full Mafia game — roles, reasoning, voting, night
              kills — and writes a structured <code>events[]</code> stream to{" "}
              <code>game_log.json</code>. The Next.js viewer reads that same file and
              replays it in four cinematic styles.
            </p>

            <div className="lp-steps">
              <div className="lp-step">
                <span className="num">01</span>
                <span className="txt">
                  Run <code>python main.py</code> — the LLMs play a full game
                </span>
              </div>
              <div className="lp-step">
                <span className="num">02</span>
                <span className="txt">
                  Structured events stream to <code>game_log.json</code>
                </span>
              </div>
              <div className="lp-step">
                <span className="num">03</span>
                <span className="txt">Open the viewer — pick a style — hit play</span>
              </div>
            </div>
          </div>

          <div>
            <div className="lp-qs-label">Quick start</div>
            <div className="lp-qs">
              <div className="cmt">// clone and play (LM Studio running locally)</div>
              <div><span className="pr">$</span> <code>git clone {GITHUB}.git</code></div>
              <div><span className="pr">$</span> <code>cd LLM-Mafia &amp;&amp; pip install -r requirements.txt</code></div>
              <div><span className="pr">$</span> <code>python main.py --reveal-secrets</code></div>
              <div style={{ marginTop: 12 }} className="cmt">// watch the replay</div>
              <div><span className="pr">$</span> <code>cd viewer &amp;&amp; npm install &amp;&amp; npm run dev</code></div>
              <div className="out"># → http://localhost:3000</div>
            </div>
          </div>
        </div>
      </section>

      {/* ── FOOTER ── */}
      <footer className="lp-footer">
        <div className="fmark">
          <span className="l1">LLM</span>
          <span className="l2">MAFIA</span>
        </div>
        <div className="fnav">
          <a href="https://github.com/nitrimandylis" target="_blank" rel="noreferrer">
            Nick Trimandylis
          </a>
          <span className="sep">│</span>
          <span className="mit">MIT licensed</span>
          <span className="sep">│</span>
          <span className="slogan">LLMS LIE. PROVED IT.</span>
        </div>
      </footer>
    </div>
  );
}

// Recorded with --reveal-secrets: the replay includes the mafia's private
// chat and the detective's checks.
function RevealedTag() {
  return (
    <span
      className="lp-ep-revealed"
      title="Recorded with secrets revealed: you watch the mafia's private chat and the detective's checks."
    >
      SECRETS REVEALED
    </span>
  );
}

// Ran with 3+ mafia — the town starts further behind than the usual two.
function HardTag() {
  return (
    <span
      className="lp-ep-hard"
      title="Hard mode: three mafia instead of the usual two. The town has far less room to misfire."
    >
      HARD MODE
    </span>
  );
}

// Spoiler-free by design: days, body count, cast size — never the winner.
function EpisodeMetaLine({ ep }: { ep: EpisodeCard }) {
  return (
    <div className="lp-ep-meta">
      {ep.cast.length} PLAYERS · {ep.days} DAYS · {ep.deaths} DEAD
      {ep.provider && (
        <>
          {" · "}
          <span
            className="lp-ep-provider"
            style={{ color: PROVIDER_COLORS[ep.provider] ?? "#888" }}
            title="Which backend played this game"
          >
            {ep.provider.replace("-", " ").toUpperCase()}
          </span>
        </>
      )}
    </div>
  );
}

function SkinCard({
  skin,
  children,
}: {
  skin: { name: string; blurb: string };
  children: React.ReactNode;
}) {
  return (
    <div className="lp-card">
      {children}
      <div className="lp-card-foot">
        <div className="lp-card-name">{skin.name}</div>
        <div className="lp-card-blurb">{skin.blurb}</div>
      </div>
    </div>
  );
}
