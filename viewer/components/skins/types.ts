import { useEffect, useRef } from "react";
import type { ReplayState } from "@/lib/useReplay";

export type SkinProps = { state: ReplayState; active: boolean };

export function initials(name: string): string {
  // "DR. VANCE" -> "DV", "HOLMES" -> "H"
  const words = name.replace(/[^\w\s]/g, "").trim().split(/\s+/);
  if (words.length >= 2) return (words[0][0] + words[1][0]).toUpperCase();
  return name[0]?.toUpperCase() ?? "?";
}

// Per-view scroll behaviour. While the view is visible it follows new content to
// the bottom; while hidden it freezes, and on return it restores the exact spot
// you left. This is what gives the four designs independent scroll memory across
// tab switches (they all stay mounted; only the active one is shown).
export function useStageScroll<T extends HTMLElement>(active: boolean, dep: number) {
  const ref = useRef<T>(null);
  const saved = useRef(0);
  const wasActive = useRef(false);

  // Follow live content to the bottom — only for the view that's on screen.
  useEffect(() => {
    if (!active) return;
    const el = ref.current;
    if (el) el.scrollTop = el.scrollHeight;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [dep]);

  // On re-show (hidden -> visible), restore the remembered position rather than
  // snapping to top or bottom. Skipped on first mount so the feed starts live.
  useEffect(() => {
    const el = ref.current;
    if (active && !wasActive.current && el && saved.current > 0) {
      el.scrollTop = saved.current;
    }
    wasActive.current = active;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [active]);

  const onScroll = (e: React.UIEvent<T>) => {
    saved.current = e.currentTarget.scrollTop;
  };

  return { ref, onScroll };
}
