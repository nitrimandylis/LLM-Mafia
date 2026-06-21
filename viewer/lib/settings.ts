"use client";

import type { Speed } from "./useReplay";

export type SkinId = "chat" | "table" | "broadcast";

export type Settings = { skin: SkinId; speed: Speed };

const KEY = "mafia-viewer-settings";
export const DEFAULTS: Settings = { skin: "chat", speed: 1 };

export function loadSettings(): Settings {
  if (typeof window === "undefined") return DEFAULTS;
  try {
    return { ...DEFAULTS, ...JSON.parse(localStorage.getItem(KEY) || "{}") };
  } catch {
    return DEFAULTS;
  }
}

export function saveSettings(s: Settings) {
  if (typeof window !== "undefined") localStorage.setItem(KEY, JSON.stringify(s));
}
