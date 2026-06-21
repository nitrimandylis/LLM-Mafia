import { readFile } from "node:fs/promises";
import path from "node:path";
import { NextResponse } from "next/server";

// The bridge between the engine and the viewer. The Python game writes
// ../game_log.json (repo root); this route reads it fresh on every request and
// falls back to the bundled sample so the viewer always has something to show.
export const dynamic = "force-dynamic";

async function tryRead(p: string) {
  try {
    const json = JSON.parse(await readFile(p, "utf8"));
    if (Array.isArray(json.events) && json.events.length > 0) return json;
  } catch {
    /* missing or malformed — fall through */
  }
  return null;
}

export async function GET() {
  const root = path.join(process.cwd(), "..", "game_log.json");
  const sample = path.join(process.cwd(), "public", "logs", "sample.json");

  const game = await tryRead(root);
  if (game) return NextResponse.json({ source: "game", log: game });

  const fallback = await tryRead(sample);
  if (fallback) return NextResponse.json({ source: "sample", log: fallback });

  return NextResponse.json({ source: "none", log: null }, { status: 404 });
}
