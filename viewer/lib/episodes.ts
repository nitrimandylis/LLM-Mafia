import manifest from "@/public/logs/manifest.json";

// Spoiler-free card data written by tools/publish_game.py — never the winner,
// never anyone's role.
export type EpisodeCard = {
  slug: string;
  title: string;
  tagline: string;
  cast: { name: string; color: string }[];
  days: number;
  deaths: number;
  // true when the game was recorded with --reveal-secrets (mafia comms and
  // detective checks are in the replay)
  revealed?: boolean;
  // which backend played the game ("nvidia" | "claude" | "lm-studio")
  provider?: string;
};

// Each provider's signature neon, tuned for the noir chrome.
export const PROVIDER_COLORS: Record<string, string> = {
  nvidia: "#76b900",
  claude: "#d97757",
  "lm-studio": "#8a7ff0",
};

// GM-written packaging baked into each published log. The recap spoils —
// it's only shown on the end-of-replay card.
export type EpisodeMeta = { title: string; tagline: string; recap: string };

// Sorted by slug (case-001 … case-00N); the newest case is the feature.
export const EPISODES: EpisodeCard[] = manifest.episodes;

export const FEATURED: EpisodeCard | undefined = EPISODES[EPISODES.length - 1];

export function episodeAfter(slug: string): EpisodeCard | undefined {
  const i = EPISODES.findIndex((e) => e.slug === slug);
  // wrap around so "next case" always leads somewhere
  return EPISODES.length > 1 ? EPISODES[(i + 1) % EPISODES.length] : undefined;
}

export function caseNumber(slug: string): string {
  const digits = slug.replace(/\D/g, "");
  return digits ? `CASE ${digits}` : slug.toUpperCase();
}
