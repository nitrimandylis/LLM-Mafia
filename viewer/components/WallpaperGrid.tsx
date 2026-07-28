"use client";

import { useState } from "react";
import Image from "next/image";

// The gallery body for /wallpapers. Client-side only for the device toggle;
// everything it renders is handed down as plain data by the page, which does
// the filesystem work.

type File = { file: string; bytes: number; width: number; height: number };
type Tile = { palette: string; mac: File; macbook: File; iphone: File };
export type Group = { design: string; blurb: string; tiles: Tile[] };

type Device = "mac" | "macbook" | "iphone";

const DEVICE_LABEL: Record<Device, string> = { mac: "MONITOR", macbook: "LAPTOP", iphone: "PHONE" };

export default function WallpaperGrid({ groups }: { groups: Group[] }) {
  // Always desktop on first paint: matching the visitor's own device would
  // mean a hydration flip, and with it a set of previews fetched and thrown
  // away on exactly the connection least able to afford it.
  const [device, setDevice] = useState<Device>("mac");

  return (
    <>
      <div className="wp-bar">
        {(["mac", "macbook", "iphone"] as Device[]).map((d) => (
          <button
            key={d}
            className={`wp-tab${device === d ? " on" : ""}`}
            aria-pressed={device === d}
            onClick={() => setDevice(d)}
          >
            {DEVICE_LABEL[d]}
          </button>
        ))}
      </div>

      {groups.map((group) => (
        <section key={group.design} className="wp-group">
          <div className="lp-label">
            <div className="lp-label-dot" />
            <span>// {group.design}</span>
          </div>
          <p className="wp-blurb">{group.blurb}</p>

          <div className={`wp-tiles${device === "iphone" ? " phone" : ""}`}>
            {group.tiles.map((tile) => {
              const f = tile[device];
              return (
                <figure key={tile.palette} className="wp-tile">
                  <a href={`/wallpapers/${f.file}`} target="_blank" rel="noreferrer" className="wp-shot">
                    {/* Only the selected device's ten are in the tree, so the
                        other set is never fetched. `sizes` keeps next/image
                        from serving a variant wider than the tile. */}
                    <Image
                      src={`/wallpapers/${f.file}`}
                      width={f.width}
                      height={f.height}
                      sizes={device === "iphone" ? "260px" : "(max-width: 860px) 90vw, 44vw"}
                      alt={`${group.design} wallpaper, ${tile.palette} palette, ${DEVICE_LABEL[device].toLowerCase()}`}
                    />
                  </a>
                  <figcaption className="wp-cap">
                    <span className="wp-pal">{tile.palette}</span>
                    <span className="wp-meta">
                      {f.width}×{f.height} · {Math.round(f.bytes / 1024)} KB
                    </span>
                    <a href={`/wallpapers/${f.file}`} download className="wp-dl">
                      ↓ DOWNLOAD
                    </a>
                  </figcaption>
                </figure>
              );
            })}
          </div>
        </section>
      ))}
    </>
  );
}
