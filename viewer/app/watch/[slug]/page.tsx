import { readFile } from "node:fs/promises";
import path from "node:path";
import { notFound } from "next/navigation";
import type { Metadata } from "next";
import type { GameEvent } from "@/lib/events";
import { EPISODES, episodeAfter, type EpisodeMeta } from "@/lib/episodes";
import EpisodePlayer from "@/components/EpisodePlayer";

// Every episode is rendered at build time from the committed logs — the
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
    title: `${card.title} — LLM Mafia`,
    description: card.tagline,
  };
}

async function loadLog(slug: string): Promise<{ events: GameEvent[]; episode: EpisodeMeta } | null> {
  try {
    const p = path.join(process.cwd(), "public", "logs", `${slug}.json`);
    const log = JSON.parse(await readFile(p, "utf8"));
    if (!Array.isArray(log.events) || log.events.length === 0) return null;
    return {
      events: log.events,
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
      card={card}
      next={episodeAfter(slug)}
    />
  );
}
