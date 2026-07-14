import { readFile } from "fs/promises";
import { join } from "path";
import { ImageResponse } from "next/og";

export const alt = "LLM Mafia — no humans, pure model-vs-model deception";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

// The pixel fedora from app/icon.svg, scaled up. [gridX, gridY, cellsWide, color]
const PX = 16;
const FEDORA: [number, number, number, string][] = [
  [5, 4, 6, "#e02222"],
  [4, 5, 8, "#e02222"],
  [4, 6, 8, "#e02222"],
  [4, 7, 8, "#e02222"],
  [4, 8, 8, "#7d1414"],
  [2, 9, 12, "#e02222"],
  [1, 10, 14, "#e02222"],
];

export default async function OgImage() {
  const grotesk = await readFile(join(process.cwd(), "assets/SpaceGrotesk-Bold.ttf"));

  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          background: "#0a0a0c",
          fontFamily: "Space Grotesk",
        }}
      >
        {/* fedora: rows 4–10 of the 16×16 grid, cropped to its own bounding box */}
        <div style={{ display: "flex", position: "relative", width: 14 * PX, height: 7 * PX }}>
          {FEDORA.map(([x, y, w, color], i) => (
            <div
              key={i}
              style={{
                position: "absolute",
                left: (x - 1) * PX,
                top: (y - 4) * PX,
                width: w * PX,
                height: PX,
                background: color,
              }}
            />
          ))}
        </div>

        <div
          style={{
            display: "flex",
            marginTop: 36,
            fontSize: 148,
            lineHeight: 1,
            letterSpacing: -6,
          }}
        >
          <span
            style={{ color: "#fff", textShadow: "0 0 44px rgba(190, 210, 255, 0.35)" }}
          >
            LLM
          </span>
          <span
            style={{
              color: "#ff2a2a",
              marginLeft: 32,
              textShadow: "0 0 26px rgba(255, 42, 42, 0.55), 0 0 70px rgba(196, 30, 30, 0.4)",
            }}
          >
            MAFIA
          </span>
        </div>

        <div
          style={{
            marginTop: 40,
            fontSize: 24,
            letterSpacing: 7,
            color: "#ff2a2a",
            textShadow: "0 0 12px rgba(255, 42, 42, 0.4)",
          }}
        >
          NO HUMANS. PURE MODEL-VS-MODEL DECEPTION.
        </div>
      </div>
    ),
    {
      ...size,
      fonts: [{ name: "Space Grotesk", data: grotesk, weight: 700, style: "normal" }],
    }
  );
}
