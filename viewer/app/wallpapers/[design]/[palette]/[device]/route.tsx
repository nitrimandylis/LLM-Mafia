import { readFile } from "fs/promises";
import { join } from "path";
import { ImageResponse } from "next/og";
import { PALETTES, SIZES, wallpaper, type Design, type Device, type Palette } from "../../../designs";

// Wallpaper generator. Rendered locally by tools/wallpapers.py, which fetches
// these URLs off `bun run dev` and saves the PNGs into public/wallpapers/ to be
// committed. Nothing in production links here; the site serves the files.

/** Avatar file for a cast name, the same rule Mug.tsx uses: "DR. VANCE" -> vance.svg. */
function slug(name: string) {
  return name.trim().split(/\s+/).pop()!.replace(/[^a-zA-Z]/g, "").toLowerCase();
}

/** The cast in players.json order, each avatar SVG inlined: Satori has no filesystem.
 *  players.json sits at the repo root, one level above the deployed viewer, so this
 *  only resolves locally. That is fine: the generator is the only caller. */
async function loadCast() {
  const raw = await readFile(join(process.cwd(), "..", "players.json"), "utf8");
  const players: { name: string }[] = JSON.parse(raw);
  return Promise.all(
    players.map(async ({ name }) => {
      const svg = await readFile(join(process.cwd(), "public/avatars", `${slug(name)}.svg`));
      return { src: `data:image/svg+xml;base64,${svg.toString("base64")}`, name };
    })
  );
}

export async function GET(
  _req: Request,
  { params }: { params: Promise<{ design: string; palette: string; device: string }> }
) {
  const { design, palette, device } = await params;
  // Each design has its own palette names, so validate against its own list.
  const palettes = PALETTES[design as Design];
  if (!palettes || !palettes.includes(palette as Palette) || !(device in SIZES)) {
    return new Response("unknown variant", { status: 404 });
  }

  const mono = await readFile(join(process.cwd(), "assets/JetBrainsMono-Regular.ttf"));
  const grotesk = await readFile(join(process.cwd(), "assets/SpaceGrotesk-Bold.ttf"));

  let faces: Awaited<ReturnType<typeof loadCast>> = [];
  // Chat uses mugshots as its notification icons, so it needs the cast too.
  if (design === "mugshots" || design === "chat") {
    try {
      faces = await loadCast();
    } catch {
      return new Response("cast unavailable: run this from a full checkout", { status: 404 });
    }
  }

  return new ImageResponse(
    wallpaper(design as Design, palette as Palette, device as Device, faces),
    {
      ...SIZES[device as Device],
      fonts: [
        { name: "JetBrains Mono", data: mono, weight: 400, style: "normal" },
        { name: "Space Grotesk", data: grotesk, weight: 700, style: "normal" },
      ],
    }
  );
}
