# Saves the wallpaper PNGs the viewer renders. Start `bun run dev` in viewer/,
# then run this; it fetches each variant and writes it into
# viewer/public/wallpapers/ to be committed. Nothing renders in production.
import sys
from collections import Counter
import urllib.error
import urllib.request
from pathlib import Path

from PIL import Image

BASE = "http://localhost:3000/wallpapers"
OUT = Path(__file__).resolve().parent.parent / "viewer" / "public" / "wallpapers"

# Each design and the palettes it has. Four designs pair the shell's
# red-on-black against the skin they quote; chat instead reuses the skin's own
# day/night duality. Must match PALETTES in viewer/app/wallpapers/designs.tsx.
PALETTES = {
    "terminal": ["shell", "skin"],
    "transcript": ["shell", "skin"],
    "poster": ["shell", "skin"],
    "mugshots": ["shell", "skin"],
    "chat": ["day", "night"],
}
DEVICES = ["mac", "iphone"]

SIZES = {"mac": (3840, 2160), "iphone": (1170, 2532)}

# Texture period in device px, must match designs.tsx. The two paper skins get
# widely spaced ruled lines; everything else gets CRT scanlines.
SCAN_PITCH = 6
RULE_PITCH = 54


def expected_pitch(design, palette):
    if palette == "skin" and design in ("transcript", "poster"):
        return RULE_PITCH
    return SCAN_PITCH


def texture_period(im, pitch):
    """Vertical period of the texture bars in an empty column, or 0 if flat.

    Satori silently ignores styles it cannot render: repeating-linear-gradient
    dropped without an error and the first spike came out a flat field. This is
    the check that catches that happening again.
    """
    px = im.convert("RGB").load()
    x = im.width - 40  # right edge, past every design's content and its glow
    # Sum the channels rather than read one: chat's night field is #030304, dark
    # enough that a 28%-black bar over it rounds away in red but not in blue.
    rows = [sum(px[x, y]) for y in range(200, 200 + pitch * 8)]
    if min(rows) == max(rows):
        return 0  # flat field: the texture did not render
    # Measure between light-to-dark transitions, not between every dark row: a
    # 2px bar makes its own rows adjacent and would read as a period of 1.
    # Taking the most common gap tolerates a background gradient drifting a
    # level or two across the sampled window.
    edges = [i for i in range(1, len(rows)) if rows[i] < rows[i - 1]]
    if len(edges) < 2:
        return 0
    gaps = [b - a for a, b in zip(edges, edges[1:])]
    return Counter(gaps).most_common(1)[0][0]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    total = 0
    file_count = 0
    for design, palettes in PALETTES.items():
        for palette in palettes:
            for device in DEVICES:
                url = f"{BASE}/{design}/{palette}/{device}"
                try:
                    data = urllib.request.urlopen(url, timeout=180).read()
                except urllib.error.URLError as e:
                    sys.exit(f"{url} failed: {e}\nIs `bun run dev` running in viewer/?")

                path = OUT / f"mafia-{design}-{palette}-{device}.png"
                path.write_bytes(data)
                total += len(data)

                im = Image.open(path)
                assert im.size == SIZES[device], f"{path.name}: got {im.size}, want {SIZES[device]}"
                want = expected_pitch(design, palette)
                got = texture_period(im, want)
                assert got == want, f"{path.name}: texture period {got}, want {want}"
                file_count += 1
                print(f"{path.name:44} {im.width}x{im.height}  {len(data) // 1024} KB")
    print(f"\n{file_count} files, {total // 1024} KB total")


if __name__ == "__main__":
    main()
