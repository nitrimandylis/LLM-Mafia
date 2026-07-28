import { readFile } from "fs/promises";
import { join } from "path";
import { ImageResponse } from "next/og";
import { SIZES, wallpaper, type Design, type Device, type Palette } from "../../../designs";

// Wallpaper generator. Rendered locally by tools/wallpapers.py, which fetches
// these URLs off `bun run dev` and saves the PNGs into public/wallpapers/ to be
// committed. Nothing in production links here; the site serves the files.

const DESIGNS = ["terminal", "transcript", "poster", "mugshots"];
const PALETTES = ["shell", "skin"];

// Cast order matches the booking wall, five to a row.
const CAST = ["aria", "chen", "holmes", "marshal", "pip", "rico", "sage", "silva", "socrates", "vance"];

export async function GET(
  _req: Request,
  { params }: { params: Promise<{ design: string; palette: string; device: string }> }
) {
  const { design, palette, device } = await params;
  if (!DESIGNS.includes(design) || !PALETTES.includes(palette) || !(device in SIZES)) {
    return new Response("unknown variant", { status: 404 });
  }

  const mono = await readFile(join(process.cwd(), "assets/JetBrainsMono-Regular.ttf"));
  const grotesk = await readFile(join(process.cwd(), "assets/SpaceGrotesk-Bold.ttf"));

  // The existing 24x24 avatar SVGs, inlined: Satori has no filesystem access.
  const faces = await Promise.all(
    CAST.map(async (name) => {
      const svg = await readFile(join(process.cwd(), "public/avatars", `${name}.svg`));
      return `data:image/svg+xml;base64,${svg.toString("base64")}`;
    })
  );

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
