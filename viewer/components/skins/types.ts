import type { ReplayState } from "@/lib/useReplay";

export type SkinProps = { state: ReplayState };

export function initials(name: string): string {
  // "DR. VANCE" -> "DV", "HOLMES" -> "H"
  const words = name.replace(/[^\w\s]/g, "").trim().split(/\s+/);
  if (words.length >= 2) return (words[0][0] + words[1][0]).toUpperCase();
  return name[0]?.toUpperCase() ?? "?";
}
