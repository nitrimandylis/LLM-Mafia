import { statSync } from "fs";
import { join } from "path";
import type { Metadata } from "next";
import Link from "next/link";
import SiteFooter from "@/components/SiteFooter";
import WallpaperGrid, { type Group } from "@/components/WallpaperGrid";
import { PALETTES, SIZES, type Design, type Device } from "./designs";
import "../landing.css";

export const metadata: Metadata = {
  title: "LLM Mafia, Wallpapers",
  description:
    "Thirty desktop and phone wallpapers from the LLM Mafia viewer: five designs, two palettes each, composed separately for 3840x2160, 3024x1964 and 1170x2532.",
};

// One line per design, read on the page under its eyebrow.
const BLURBS: Record<Design, string> = {
  terminal: "the shell prompt, with the centre left clear",
  transcript: "a night-phase exchange, six lines of it",
  poster: "the fedora and the logotype, full size",
  mugshots: "the booking wall, all ten faces",
  chat: "the group chat, arriving as notifications",
};

/** One variant: its filename, its size on disk so the download link can say
 *  what it costs, and its pixel dimensions. */
function file(design: Design, palette: string, device: Device) {
  const name = `mafia-${design}-${palette}-${device}.png`;
  return {
    file: name,
    bytes: statSync(join(process.cwd(), "public/wallpapers", name)).size,
    ...SIZES[device],
  };
}

// Built here rather than in the grid because the grid is a client component:
// it can neither read the filesystem nor pull in designs.tsx, which would drag
// every wallpaper composition into the browser bundle.
const GROUPS: Group[] = (Object.keys(PALETTES) as Design[]).map((design) => ({
  design,
  blurb: BLURBS[design],
  tiles: PALETTES[design].map((palette) => ({
    palette,
    mac: file(design, palette, "mac"),
    macbook: file(design, palette, "macbook"),
    iphone: file(design, palette, "iphone"),
  })),
}));

export default function Wallpapers() {
  return (
    <div className="lp">
      <div className="lp-subnav">
        <Link href="/" className="lp-back">
          ‹ BACK
        </Link>
      </div>

      <section className="lp-page-head">
        <div className="lp-label">
          <div className="lp-label-dot" />
          <span>// wallpapers</span>
        </div>
        <h1 className="lp-page-h1">Thirty wallpapers. Five designs, two palettes, three devices.</h1>
        <p className="lp-page-lede">
          Each device gets its own composition rather than a crop, which is why the 16:9
          monitor and the 16:10 laptop are separate files. The desktop files keep the
          icon column and the centre of the screen clear; the phone files clear the top
          third for the clock and the bottom for the lock-screen buttons. Click a
          preview to open the full image, or take the file straight from the link under
          it.
        </p>
      </section>

      <WallpaperGrid groups={GROUPS} />

      <SiteFooter />
    </div>
  );
}
