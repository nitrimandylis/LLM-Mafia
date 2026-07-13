"use client";

import type { Speed } from "./useReplay";

export type SkinId = "chat" | "casefile" | "transcript" | "signal";

export type SkinMeta = {
  id: SkinId;
  name: string;
  tag: string; // short descriptor for the switcher
  blurb: string; // longer line for the settings page
  // Three colors that preview this design's world: [background, accent, ink].
  swatch: [string, string, string];
};

// Single source of truth for the four designs — drives the menu and settings.
export const SKINS: SkinMeta[] = [
  {
    id: "chat",
    name: "Group Chat",
    tag: "the thread",
    blurb: "A messaging thread: grouped bubbles, day/night theming, votes folded into a ballot strip, mafia in a locked side-channel.",
    swatch: ["#0a0b10", "#c41e1e", "#e0e0e0"],
  },
  {
    id: "casefile",
    name: "Case File",
    tag: "the board",
    blurb: "You're the detective. Typed testimony on manila paper, suspect ID cards, and intercepted mafia comms stamped DECLASSIFIED.",
    swatch: ["#e3d9c0", "#a6261c", "#211c15"],
  },
  {
    id: "transcript",
    name: "Transcript",
    tag: "the record",
    blurb: "A line-numbered court deposition. Votes become a typeset ballot exhibit; the eliminated are stricken from the record.",
    swatch: ["#f2ede3", "#6e1a1a", "#22201b"],
  },
  {
    id: "signal",
    name: "Signal",
    tag: "the network",
    blurb: "An instrument panel. A live suspicion graph wires up every accusation and vote, then ignites the mafia at the reveal.",
    swatch: ["#050505", "#c41e1e", "#b5b5bd"],
  },
];

const SKIN_IDS = new Set(SKINS.map((s) => s.id));

// Chrome themes style the frame (top bar, switcher, transport) — not the skins.
export type ChromeThemeId = "signature" | "adaptive" | "quiet";

export type ChromeThemeMeta = {
  id: ChromeThemeId;
  name: string;
  blurb: string;
  // [bar, accent, ink] preview of the frame this theme paints.
  swatch: [string, string, string];
};

export const CHROME_THEMES: ChromeThemeMeta[] = [
  {
    id: "signature",
    name: "Signature",
    blurb: "The house style: a neon-noir frame — cold night bars, a buzzing red neon wordmark, scanlines, and a faint phosphor grain.",
    swatch: ["#0a0b10", "#ff2a2a", "#e7e9ee"],
  },
  {
    id: "adaptive",
    name: "Adaptive",
    blurb: "The frame borrows the accent of whichever design you're watching, so the chrome and the canvas read as one piece.",
    swatch: ["#101216", "#5b8cff", "#e7e9ee"],
  },
  {
    id: "quiet",
    name: "Quiet",
    blurb: "A restrained neutral frame that stays out of the way and lets each design's world do the talking.",
    swatch: ["#101216", "#7a818d", "#e7e9ee"],
  },
];

const CHROME_IDS = new Set(CHROME_THEMES.map((c) => c.id));

export type Settings = { skin: SkinId; speed: Speed; chromeTheme: ChromeThemeId };

const KEY = "mafia-viewer-settings";
export const DEFAULTS: Settings = { skin: "chat", speed: 1, chromeTheme: "signature" };

export function loadSettings(): Settings {
  if (typeof window === "undefined") return DEFAULTS;
  try {
    const merged = { ...DEFAULTS, ...JSON.parse(localStorage.getItem(KEY) || "{}") };
    // Guard against stale ids from an older build (e.g. skin "table").
    if (!SKIN_IDS.has(merged.skin)) merged.skin = DEFAULTS.skin;
    if (!CHROME_IDS.has(merged.chromeTheme)) merged.chromeTheme = DEFAULTS.chromeTheme;
    return merged;
  } catch {
    return DEFAULTS;
  }
}

export function saveSettings(s: Settings) {
  if (typeof window !== "undefined") localStorage.setItem(KEY, JSON.stringify(s));
}
