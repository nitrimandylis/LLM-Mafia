import { readFile } from "node:fs/promises";
import path from "node:path";
import { notFound } from "next/navigation";
import type { Metadata } from "next";
import type { GameEvent } from "@/lib/events";
import { EPISODES, episodeAfter, caseNumber, type EpisodeMeta } from "@/lib/episodes";
import EpisodePlayer from "@/components/EpisodePlayer";

// Every episode is rendered at build time from the committed logs, the
// deployed site ships no server code for this route.
export const dynamicParams = false;

export function generateStaticParams() {
  return EPISODES.map((e) => ({ slug: e.slug }));
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  const card = EPISODES.find((e) => e.slug === slug);
  if (!card) return {};
  return {
    // caseNumber shouts ("CASE 009"); the tab wants sentence case.
    title: `LLM Mafia, ${caseNumber(slug).replace("CASE", "Case")}`,
    description: card.tagline,
  };
}

async function loadLog(
  slug: string
): Promise<{ events: GameEvent[]; episode: EpisodeMeta; roles: Record<string, string> } | null> {
  try {
    const p = path.join(process.cwd(), "public", "logs", `${slug}.json`);
    const log = JSON.parse(await readFile(p, "utf8"));
    if (!Array.isArray(log.events) || log.events.length === 0) return null;
    // Every log records the final roles in stats, revealed or not. game_start
    // only carries them on --reveal-secrets runs, so read stats instead: the
    // cold open can state the difficulty and the recap can name everybody.
    const stats: Record<string, { role?: string }> = log.stats?.players ?? {};
    const roles = Object.fromEntries(
      Object.entries(stats).map(([name, p]) => [name, p.role ?? "?"])
    );
    return {
      events: log.events,
      roles,
      episode: {
        title: log.episode?.title ?? slug,
        tagline: log.episode?.tagline ?? "",
        recap: log.episode?.recap ?? "",
      },
    };
  } catch {
    return null;
  }
}

export default async function EpisodePage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const card = EPISODES.find((e) => e.slug === slug);
  const log = card ? await loadLog(slug) : null;
  if (!card || !log) notFound();

  return (
    <EpisodePlayer
      events={log.events}
      episode={log.episode}
      roles={log.roles}
      card={card}
      next={episodeAfter(slug)}
    />
  );
}
