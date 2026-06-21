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
    swatch: ["#11131a", "#5b8cff", "#e8e8ea"],
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
    swatch: ["#eef1f4", "#0e7c86", "#0e1419"],
  },
];

const SKIN_IDS = new Set(SKINS.map((s) => s.id));

export type Settings = { skin: SkinId; speed: Speed };

const KEY = "mafia-viewer-settings";
export const DEFAULTS: Settings = { skin: "chat", speed: 1 };

export function loadSettings(): Settings {
  if (typeof window === "undefined") return DEFAULTS;
  try {
    const merged = { ...DEFAULTS, ...JSON.parse(localStorage.getItem(KEY) || "{}") };
    // Guard against a stale skin id from an older build (e.g. "table").
    if (!SKIN_IDS.has(merged.skin)) merged.skin = DEFAULTS.skin;
    return merged;
  } catch {
    return DEFAULTS;
  }
}

export function saveSettings(s: Settings) {
  if (typeof window !== "undefined") localStorage.setItem(KEY, JSON.stringify(s));
}
