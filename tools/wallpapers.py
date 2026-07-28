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
DEVICES = ["mac", "macbook", "iphone"]

SIZES = {"mac": (3840, 2160), "macbook": (3024, 1964), "iphone": (1170, 2532)}

# Texture period in device px, must match designs.tsx. The two paper skins get
# widely spaced ruled lines; everything else gets CRT scanlines.
SCAN_PITCH = 6
RULE_PITCH = 54


def expected_pitch(design, palette):
    if palette == "skin" and design in ("transcript", "poster"):
        return RULE_PITCH
    return SCAN_PITCH


# A wallpaper is set per Space, not per display, so the 16:10 laptop file is
# also what the 16:9 monitor shows: scaled to cover, with this much cut off the
# top and bottom. designs.tsx places the macbook cluster against the surviving
# band; ink_rows is what proves it still does.
MB_BAND = round(SIZES["macbook"][0] * 9 / 16)
MB_CROP = round((SIZES["macbook"][1] - MB_BAND) / 2)
# Clearing the band is not enough. The first attempt put the tagline 11px inside
# it, which passed a not-clipped test and still looked broken on the monitor, so
# the floor is a visible margin: 6% of the band, against the mac file's own 9.3%.
MB_MARGIN = round(0.06 * MB_BAND)


def ink_rows(im):
    """First and last row carrying content, ignoring the full-bleed texture.

    Every row is compared against the same row in an empty right-hand column,
    so the scanlines and any background gradient cancel out and only the
    cluster registers. Works on the light paper skins too: the test is on the
    size of the difference, not its sign.
    """
    px = im.convert("RGB").load()
    ref_x = im.width - 40
    top = bot = None
    for y in range(im.height):
        ref = sum(px[ref_x, y])
        for x in range(120, int(im.width * 0.62), 4):
            if abs(sum(px[x, y]) - ref) > 90:
                if top is None:
                    top = y
                bot = y
                break
    return top, bot


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

                if device == "macbook":
                    top, bot = ink_rows(im)
                    lo, hi = MB_CROP + MB_MARGIN, im.height - MB_CROP - MB_MARGIN
                    assert lo <= top and bot <= hi, (
                        f"{path.name}: ink {top}..{bot} is outside {lo}..{hi}, "
                        f"the 16:9 crop band less its {MB_MARGIN}px margin; it "
                        f"would sit on the edge of the monitor"
                    )

                file_count += 1
                print(f"{path.name:44} {im.width}x{im.height}  {len(data) // 1024} KB")
    print(f"\n{file_count} files, {total // 1024} KB total")


if __name__ == "__main__":
    main()
