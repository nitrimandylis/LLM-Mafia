# Favicon candidates for the LLM Mafia viewer — 16x16 pixel grids.
from PIL import Image

W = H = 16
BG = "#0a0a0c"

# A — red fedora on dark
FEDORA_PAL = {"R": "#e02222", "B": "#7d1414"}
FEDORA = [
    "................",
    "................",
    "................",
    "................",
    ".....RRRRRR.....",
    "....RRRRRRRR....",
    "....RRRRRRRR....",
    "....RRRRRRRR....",
    "....BBBBBBBB....",
    "..RRRRRRRRRRRR..",
    ".RRRRRRRRRRRRRR.",
    "................",
    "................",
    "................",
    "................",
    "................",
]

# B — anonymous suspect: dark silhouette + red fedora on booking wall
SUSPECT_PAL = {"R": "#e02222", "B": "#7d1414", "H": "#14161c", ",": "#3a4356"}
SUSPECT_BG = "#2e3644"
SUSPECT = [
    "................",
    ",,,,,,,,,,,,,,,,",
    ".....RRRRRR.....",
    ".....RRRRRR.....",
    "...RRRBBBBRRR...",
    ".....HHHHHH.....",
    ",,,,,HHHHHH,,,,,",
    ".....HHHHHH.....",
    "......HHHH......",
    "......HHHH......",
    "....HHHHHHHH....",
    ",,.HHHHHHHHHH.,,",
    ".HHHHHHHHHHHHHH.",
    ".HHHHHHHHHHHHHH.",
    ".HHHHHHHHHHHHHH.",
    "................",
]

# C — domino mask, red with dark eyeholes
MASK_PAL = {"R": "#e02222", "#": "#0a0a0c", "B": "#7d1414"}
MASK = [
    "................",
    "................",
    "................",
    "................",
    "..RRRRRRRRRRRR..",
    ".RRRRRRRRRRRRRR.",
    ".RR##RRRRRR##RR.",
    ".RR##RRRRRR##RR.",
    "..RRRRRBBRRRRR..",
    "...RRRR..RRRR...",
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
]

# D — magnifying glass over height-chart lines
GLASS_PAL = {"R": "#e02222", "L": "#4a5468", ",": "#3a4356", "W": "#8fa0c0"}
GLASS_BG = "#2e3644"
GLASS = [
    "................",
    ",,,,,,,,,,,,,,,,",
    "....RRRR........",
    "...R....R.......",
    "..R......R......",
    "..R.W.....R.....",
    ",,R,,,,,,,R,,,,,",
    "..R......R......",
    "...R....R.......",
    "....RRRR........",
    ".......RR.......",
    ",,,,,,,,,RR,,,,,",
    ".........RR.....",
    "..........RR....",
    "................",
    "................",
]

ICONS = [
    ("fedora", FEDORA, FEDORA_PAL, BG),
    ("suspect", SUSPECT, SUSPECT_PAL, SUSPECT_BG),
    ("mask", MASK, MASK_PAL, BG),
    ("glass", GLASS, GLASS_PAL, GLASS_BG),
]


def hex_to_rgb(s):
    s = s.lstrip("#")
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def render(grid, pal, bg, scale):
    img = Image.new("RGB", (W * scale, H * scale))
    px = img.load()
    for y, row in enumerate(grid):
        assert len(row) == W, f"row {y}: {len(row)}"
        for x, ch in enumerate(row):
            color = bg if ch == "." else pal[ch]
            r, g, b = hex_to_rgb(color)
            for dy in range(scale):
                for dx in range(scale):
                    px[x * scale + dx, y * scale + dy] = (r, g, b)
    return img


def emit_svg(grid, pal, bg, path):
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" shape-rendering="crispEdges">',
        f'<rect width="{W}" height="{H}" rx="3" fill="{bg}"/>',
    ]
    for y, row in enumerate(grid):
        x = 0
        while x < W:
            ch = row[x]
            if ch == ".":
                x += 1
                continue
            run = 1
            while x + run < W and row[x + run] == ch:
                run += 1
            parts.append(f'<rect x="{x}" y="{y}" width="{run}" height="1" fill="{pal[ch]}"/>')
            x += run
    parts.append("</svg>")
    with open(path, "w") as f:
        f.write("\n".join(parts) + "\n")


def main():
    pad = 20
    sizes = [10, 2, 1]  # 160px look, 32px, 16px true favicon size
    row_h = [W * s for s in sizes]
    sheet = Image.new(
        "RGB",
        (pad + (W * 10 + pad) * len(ICONS), pad + sum(h + pad for h in row_h)),
        hex_to_rgb("#191c24"),
    )
    for i, (name, grid, pal, bg) in enumerate(ICONS):
        y = pad
        for s in sizes:
            sheet.paste(render(grid, pal, bg, s), (pad + i * (W * 10 + pad), y))
            y += W * s + pad
        emit_svg(grid, pal, bg, f"/private/tmp/claude-501/-Users-nick-Developer-LLM-Mafia/73ff8f13-721a-4b58-8f22-3e70174d5909/scratchpad/icon-{name}.svg")
    out = "/private/tmp/claude-501/-Users-nick-Developer-LLM-Mafia/73ff8f13-721a-4b58-8f22-3e70174d5909/scratchpad/favicons.png"
    sheet.save(out)
    print("wrote", out)


if __name__ == "__main__":
    main()
