// The five wallpaper designs, each in two palettes and two device layouts.
// Rendered by the route next door; see tools/wallpapers.py for how the PNGs
// get saved. Palettes are copied from globals.css so the wallpapers stay in
// step with the skins they quote.

export type Device = "mac" | "iphone";
export type Design = "terminal" | "transcript" | "poster" | "mugshots" | "chat";
export type Palette = "shell" | "skin" | "day" | "night";

// Which palettes each design actually has. Four designs pair the shell's
// red-on-black against the skin they quote; chat instead reuses the skin's own
// day/night duality, since a shell-versus-chat pair would be two near-identical
// near-black fields. The route and tools/wallpapers.py both walk this map.
export const PALETTES: Record<Design, Palette[]> = {
  terminal: ["shell", "skin"],
  transcript: ["shell", "skin"],
  poster: ["shell", "skin"],
  mugshots: ["shell", "skin"],
  chat: ["day", "night"],
};

/** One cast member: the inlined avatar SVG and the name printed under it. */
export type Face = { src: string; name: string };

export const SIZES: Record<Device, { width: number; height: number }> = {
  mac: { width: 3840, height: 2160 },
  iphone: { width: 1170, height: 2532 },
};

// Type scale per device. Explicit rather than derived from width: a phone is
// held at arm's length and needs proportionally larger text than a 4K monitor.
const TYPE = {
  mac: { label: 96, body: 44, mono: 56, lead: 90, logo: 300, tag: 54, face: 380, num: 34, name: 28 },
  iphone: { label: 44, body: 26, mono: 30, lead: 52, logo: 132, tag: 26, face: 176, num: 20, name: 14 },
};

// Satori silently drops repeating-linear-gradient, so every repeating texture
// on these wallpapers is drawn as explicit bars. This is also why the
// feTurbulence phosphor grain from globals.css cannot be reproduced at all.
// tools/wallpapers.py probes the output for the expected period.
export const SCAN_PITCH = 6; // scanlines: the site's 3px CSS pitch at 2x
export const RULE_PITCH = 54; // ruled paper lines on the two light skins

const FILL = { position: "absolute" as const, top: 0, left: 0, width: "100%", height: "100%" };

function hLines(height: number, pitch: number, thickness: number, color: string) {
  return Array.from({ length: Math.ceil(height / pitch) }, (_, i) => (
    <div
      key={i}
      style={{ position: "absolute", left: 0, top: i * pitch, width: "100%", height: thickness, background: color }}
    />
  ));
}

function vLines(width: number, pitch: number, thickness: number, color: string) {
  return Array.from({ length: Math.ceil(width / pitch) }, (_, i) => (
    <div
      key={i}
      style={{ position: "absolute", top: 0, left: i * pitch, width: thickness, height: "100%", background: color }}
    />
  ));
}

// Where the content sits. Mac clears the right third and the centre for icons
// and windows; iPhone clears the top third for the clock and the bottom for
// the lock-screen buttons, so its content lives in a middle band.
function cluster(device: Device) {
  return device === "mac"
    ? { position: "absolute" as const, left: 220, bottom: 200, display: "flex", flexDirection: "column" as const }
    : { position: "absolute" as const, left: 90, top: 920, display: "flex", flexDirection: "column" as const };
}

// ---------------------------------------------------------------- palettes

const SHELL = { bg: "#050609", ink: "#e7e9ee", muted: "#8b8f9c", brand: "#c41e1e", neon: "#ff2a2a" };
const SIGNAL = { bg: "#050505", ink: "#e0e0e0", muted: "#b5b5bd", brand: "#c41e1e", accent: "#c8762e", edge: "#50505a" };
const BONE = { bg: "#f2ede3", ink: "#22201b", muted: "#6b614a", brand: "#6e1a1a", seal: "#9a6b1e" };
const MANILA = { bg: "#e4dac1", ink: "#211c15", muted: "#675c43", brand: "#a6261c" };
const WALL = { bg: "#2e3644", line: "#3a4356", ink: "#e7e9ee", muted: "#9aa3b4", brand: "#c41e1e" };

// The two chat palettes, taken from the `.chat` and `.chat.night` rules.
const CHAT_DAY = {
  bg: "#0a0b10",
  card: "#17171c",
  border: "rgba(255,255,255,.09)",
  ink: "#c9cfdb",
  muted: "#8b93a3",
  brand: "#c41e1e",
  presence: "#ff2a2a",
  presenceGlow: "0 0 20px rgba(255,42,42,.45)",
};
const CHAT_NIGHT = {
  bg: "#030304",
  card: "#17171c",
  border: "rgba(196,30,30,.18)",
  ink: "#c9cfdb",
  muted: "#8b93a3",
  brand: "#c41e1e",
  presence: "#9aa0aa",
  presenceGlow: "none",
};

const NEON_GLOW = "0 0 30px rgba(255,42,42,.55), 0 0 80px rgba(196,30,30,.4)";

/** True for the two paper skins, which get ruled lines instead of scanlines. */
export function isPaper(design: Design, palette: Palette) {
  return palette === "skin" && (design === "transcript" || design === "poster");
}

export function texturePitch(design: Design, palette: Palette) {
  return isPaper(design, palette) ? RULE_PITCH : SCAN_PITCH;
}

// ----------------------------------------------------------------- designs

// The pixel fedora from app/icon.svg. [gridX, gridY, cellsWide, tone]
// tone "a" is the crown, "b" the band; the palette decides the actual colours.
const FEDORA: [number, number, number, "a" | "b"][] = [
  [5, 4, 6, "a"],
  [4, 5, 8, "a"],
  [4, 6, 8, "a"],
  [4, 7, 8, "a"],
  [4, 8, 8, "b"],
  [2, 9, 12, "a"],
  [1, 10, 14, "a"],
];

function fedora(px: number, crown: string, band: string) {
  return (
    <div style={{ display: "flex", position: "relative", width: 14 * px, height: 7 * px }}>
      {FEDORA.map(([x, y, w, tone], i) => (
        <div
          key={i}
          style={{
            position: "absolute",
            left: (x - 1) * px,
            top: (y - 4) * px,
            width: w * px,
            height: px,
            background: tone === "a" ? crown : band,
          }}
        />
      ))}
    </div>
  );
}

// A night-phase exchange. Invented, not read from a log: these are fixed
// compositions, so nothing here should be mistaken for a real case.
const EXCHANGE: [string, string][] = [
  ["MARSHAL", "you went quiet the night pip died."],
  ["ARIA", "i was listening. you were talking."],
  ["MARSHAL", "about what."],
  ["ARIA", "about who to kill."],
  ["SILVA", "that is not a denial."],
  ["ARIA", "it is not a confession either."],
];

function terminal(device: Device, palette: Palette) {
  const t = TYPE[device];
  const c = palette === "shell" ? SHELL : SIGNAL;
  const glow = palette === "shell" ? NEON_GLOW : "0 0 24px rgba(200,118,46,.4)";
  const cursor = palette === "shell" ? SHELL.neon : SIGNAL.accent;

  return (
    <>
      {palette === "shell" ? (
        <div style={{ ...FILL, display: "flex", background: "radial-gradient(ellipse at 18% 82%, #16090b, #050505 70%)" }} />
      ) : (
        // Signal's 26px instrument grid, at 2x for device pixels. The skin uses
        // .05 alpha over its own panels; on a bare near-black field that is
        // invisible, so the wallpaper carries it heavier to stay distinct from
        // the shell variant.
        <div style={{ ...FILL, display: "flex" }}>
          {hLines(SIZES[device].height, 52, 2, "rgba(196,30,30,.20)")}
          {vLines(SIZES[device].width, 52, 2, "rgba(196,30,30,.20)")}
        </div>
      )}

      <div style={cluster(device)}>
        <div style={{ display: "flex", fontSize: t.label, letterSpacing: t.label / 5, color: palette === "shell" ? c.brand : SIGNAL.ink, textShadow: glow }}>
          [ LLM MAFIA ]
        </div>
        <div style={{ display: "flex", marginTop: t.body, fontSize: t.body, letterSpacing: t.body / 5, color: c.muted }}>
          NO HUMANS. PURE MODEL-VS-MODEL DECEPTION.
        </div>
        <div style={{ display: "flex", alignItems: "center", marginTop: t.lead }}>
          <div style={{ display: "flex", fontSize: t.mono, color: c.brand, marginRight: t.mono / 2 }}>$</div>
          <div style={{ width: t.mono * 0.6, height: t.mono * 1.1, background: cursor, boxShadow: `0 0 26px ${cursor}99` }} />
        </div>
      </div>
    </>
  );
}

function transcript(device: Device, palette: Palette) {
  const t = TYPE[device];
  const c = palette === "shell" ? SHELL : BONE;

  return (
    <>
      {palette === "shell" && (
        <div style={{ ...FILL, display: "flex", background: "radial-gradient(ellipse at 22% 78%, #16090b, #050505 72%)" }} />
      )}

      <div style={cluster(device)}>
        <div style={{ display: "flex", fontSize: t.body, letterSpacing: t.body / 4, color: palette === "shell" ? c.muted : BONE.seal, marginBottom: t.lead }}>
          DAY 2 — 03:47 — NIGHT PHASE
        </div>

        {EXCHANGE.map(([who, said], i) => (
          <div key={i} style={{ display: "flex", alignItems: "baseline", marginBottom: t.body * 0.7 }}>
            {palette === "skin" && (
              <div style={{ display: "flex", width: t.num * 2.4, fontSize: t.num, color: BONE.seal }}>{String(i + 1).padStart(2, "0")}</div>
            )}
            <div style={{ display: "flex", width: t.mono * 6.5, fontSize: t.mono, color: c.brand, letterSpacing: t.mono / 12 }}>{who}</div>
            <div style={{ display: "flex", fontSize: t.mono, color: c.ink }}>{said}</div>
          </div>
        ))}
      </div>
    </>
  );
}

function poster(device: Device, palette: Palette) {
  const t = TYPE[device];
  const shell = palette === "shell";
  const c = shell ? SHELL : MANILA;
  const px = Math.round(t.logo / 9); // fedora cell size, tuned against the logotype

  return (
    <>
      {shell && <div style={{ ...FILL, display: "flex", background: "radial-gradient(ellipse at 24% 76%, #1a090b, #050505 72%)" }} />}

      <div style={cluster(device)}>
        {fedora(px, shell ? "#e02222" : MANILA.brand, shell ? "#7d1414" : "#6d1913")}

        <div style={{ display: "flex", marginTop: t.logo / 5, fontSize: t.logo, lineHeight: 1, letterSpacing: -t.logo / 25, fontFamily: "Space Grotesk" }}>
          <div style={{ display: "flex", color: shell ? "#fff" : MANILA.ink, textShadow: shell ? "0 0 44px rgba(190,210,255,.35)" : "none" }}>LLM</div>
          {/* The negative tracking that tightens the logotype also eats the
              word gap, so the gap is set explicitly rather than with a space. */}
          <div style={{ display: "flex", marginLeft: t.logo / 3, color: shell ? SHELL.neon : MANILA.brand, textShadow: shell ? NEON_GLOW : "none" }}>MAFIA</div>
        </div>

        <div style={{ display: "flex", marginTop: t.tag, fontSize: t.tag, letterSpacing: t.tag / 5, color: shell ? SHELL.neon : MANILA.muted }}>
          NO HUMANS. PURE MODEL-VS-MODEL DECEPTION.
        </div>
      </div>
    </>
  );
}

function mugshots(device: Device, palette: Palette, faces: Face[]) {
  const t = TYPE[device];
  const shell = palette === "shell";
  const c = shell ? SHELL : WALL;
  const gap = t.face / 8;

  return (
    <>
      {shell ? (
        <div style={{ ...FILL, display: "flex", background: "radial-gradient(ellipse at 20% 80%, #16090b, #050505 70%)" }} />
      ) : (
        // The booking wall's height chart, run full bleed behind everything.
        <div style={{ ...FILL, display: "flex" }}>{hLines(SIZES[device].height, t.face / 4, 3, WALL.line)}</div>
      )}

      <div style={cluster(device)}>
        <div style={{ display: "flex", fontSize: t.label, letterSpacing: t.label / 5, color: shell ? c.brand : WALL.ink, textShadow: shell ? NEON_GLOW : "none", marginBottom: t.lead }}>
          [ THE CAST ]
        </div>

        {[0, 1].map((row) => (
          <div key={row} style={{ display: "flex", marginTop: row === 0 ? 0 : gap }}>
            {faces.slice(row * 5, row * 5 + 5).map(({ src, name }) => (
              <div key={name} style={{ display: "flex", flexDirection: "column", alignItems: "center", width: t.face, marginRight: gap }}>
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src={src} width={t.face} height={t.face} alt={name} />
                <div style={{ display: "flex", marginTop: t.name * 0.7, fontSize: t.name, letterSpacing: t.name / 14, color: shell ? c.muted : WALL.muted }}>
                  {name}
                </div>
              </div>
            ))}
          </div>
        ))}
      </div>
    </>
  );
}

// A collapsed iOS notification stack: the wallpaper pretends the game is
// messaging you. Not a screenshot of the thread, which is the densest thing in
// the skin and would fill the frame the other four designs deliberately clear.
function chat(device: Device, palette: Palette, faces: Face[]) {
  const t = TYPE[device];
  const c = palette === "night" ? CHAT_NIGHT : CHAT_DAY;

  const width = device === "mac" ? 1500 : 990;
  const pad = t.mono * 0.55;
  const gap = t.mono * 0.35;
  const inset = t.mono * 0.9; // how much narrower each card behind the front one is, per side
  const peek = t.mono * 0.45; // how far the back card shows below the middle one
  const iconSize = t.mono * 1.6;
  const radius = t.mono * 1.1;

  /** One notification card: sender mugshot, app name, timestamp, one message.
   *  Heights are left to the content, so nothing here has to be measured. */
  function card(indent: number, who: string, said: string, stamp: string, front: boolean) {
    const face = faces.find((f) => f.name.endsWith(who));
    return (
      <div
        style={{
          marginTop: front ? 0 : gap,
          marginLeft: indent,
          width: width - indent * 2,
          display: "flex",
          flexDirection: "column",
          padding: pad,
          borderRadius: radius,
          background: c.card,
          border: `${Math.round(t.mono / 18)}px solid ${c.border}`,
          opacity: front ? 1 : 0.78,
        }}
      >
        <div style={{ display: "flex", alignItems: "center" }}>
          {face && (
            // eslint-disable-next-line @next/next/no-img-element
            <img src={face.src} width={iconSize} height={iconSize} alt={who} style={{ borderRadius: iconSize / 4 }} />
          )}
          <div style={{ display: "flex", marginLeft: pad * 0.6, fontSize: t.mono * 0.72, letterSpacing: t.mono / 8, color: c.ink }}>
            LLM MAFIA
          </div>
          <div
            style={{
              display: "flex",
              marginLeft: "auto",
              fontSize: t.mono * 0.62,
              color: front ? c.presence : c.muted,
              textShadow: front ? c.presenceGlow : "none",
            }}
          >
            {stamp}
          </div>
        </div>

        <div style={{ display: "flex", marginTop: t.mono * 0.45, marginLeft: iconSize + pad * 0.6 }}>
          <div style={{ display: "flex", fontSize: t.mono, color: c.brand, marginRight: t.mono / 2 }}>{who}:</div>
          <div style={{ display: "flex", fontSize: t.mono, color: c.ink }}>{said}</div>
        </div>
      </div>
    );
  }

  return (
    <>
      {palette === "night" && (
        <div style={{ ...FILL, display: "flex", background: "radial-gradient(ellipse at top, #1a0b0e, #030304)" }} />
      )}

      <div style={cluster(device)}>
        <div style={{ position: "relative", display: "flex", flexDirection: "column", width }}>
          {/* The third card comes first in the DOM so the other two paint over
              it: all that shows is its rounded edge below the middle card. */}
          <div
            style={{
              position: "absolute",
              bottom: -peek,
              left: inset * 2,
              width: width - inset * 4,
              height: peek * 3,
              display: "flex",
              borderRadius: peek,
              background: c.card,
              opacity: 0.5,
            }}
          />
          {card(0, "SILVA", "that is not a denial.", "now", true)}
          {card(inset, "MARSHAL", "about what.", "2m", false)}
        </div>
      </div>
    </>
  );
}

// ------------------------------------------------------------------ render

// Keyed by the palettes each design actually has, so the value type is a plain
// string map rather than one that would demand every palette name everywhere.
const BACKGROUNDS: Record<Design, Record<string, string>> = {
  terminal: { shell: SHELL.bg, skin: SIGNAL.bg },
  transcript: { shell: SHELL.bg, skin: BONE.bg },
  poster: { shell: SHELL.bg, skin: MANILA.bg },
  mugshots: { shell: SHELL.bg, skin: WALL.bg },
  chat: { day: CHAT_DAY.bg, night: CHAT_NIGHT.bg },
};

export function wallpaper(design: Design, palette: Palette, device: Device, faces: Face[]) {
  const size = SIZES[device];
  const paper = isPaper(design, palette);

  const body =
    design === "terminal" ? terminal(device, palette)
    : design === "transcript" ? transcript(device, palette)
    : design === "poster" ? poster(device, palette)
    : design === "chat" ? chat(device, palette, faces)
    : mugshots(device, palette, faces);

  return (
    <div style={{ ...FILL, display: "flex", background: BACKGROUNDS[design][palette], fontFamily: "JetBrains Mono" }}>
      {body}
      {/* Texture goes on top of the art but under nothing: on a real tube the
          scanlines cross the picture. Paper skins get ruled lines instead. */}
      <div style={{ ...FILL, display: "flex" }}>
        {paper
          ? hLines(size.height, RULE_PITCH, 2, "rgba(120,100,60,.10)")
          : hLines(size.height, SCAN_PITCH, 2, "rgba(0,0,0,.28)")}
      </div>
    </div>
  );
}
