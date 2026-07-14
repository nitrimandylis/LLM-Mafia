# Pixel-art mugshots for LLM Mafia viewer avatars.
# Each face: 24x24 ASCII grid + palette. Renders a contact sheet for review.
from PIL import Image

W = H = 24
SCALE = 16
LINE_ROWS = {3, 9, 15, 21}  # mugshot height-chart lines behind the figure

BG = "#2e3644"
BGLINE = "#3a4356"
OUT = "#12141c"

# ---------------- RICO — hotheaded, spiky hair, stubble, scowl ----------------
RICO_PAL = {
    "#": OUT, "H": "#1f232b", "S": "#c98d68", "D": "#a96f4f",
    "E": "#e8e4da", "P": "#1a1c24", "M": "#5e3028", "X": "#9c6a4c",
    "C": "#4f5747", "c": "#434a3c",
}
RICO = [
    "........................",
    "......#...#....#........",
    ".....###.###..###.......",
    "....###H###H###H##......",
    "....#HHHHHHHHHHHH#......",
    "....#HHHHHHHHHHHH#......",
    "....#HHSSSSSSSSHH#......",
    "....#HSSSSSSSSSSH#......",
    "....#SSSSSSSSSSSS#......",
    "....#SS##SSSS##SS#......",
    "....#S#EP#SS#PE#S#......",
    "....#SSSSSSSSSSSS#......",
    "....#DSSSS#DSSSSD#......",
    "....#DSSSS#DSSSSD#......",
    "....#XSSSSSSSSSSX#......",
    "....#XSSS####SSSX#......",
    "....#XXXSMMMMSXXX#......",
    ".....#XXXXXXXXXX#.......",
    "......#DSSSSSSD#........",
    ".......##DSSD##.........",
    "....####CDSSDC####......",
    "..##CCCCc#SS#cCCCC##....",
    ".#CCCCCCc#SS#cCCCCCC#...",
    ".#CCCCCCCCCCCCCCCCCC#...",
]

# ---------------- PIP — nervous newcomer, messy hair, big worried eyes ----------------
PIP_PAL = {
    "#": OUT, "H": "#b98d4f", "h": "#a37a40", "S": "#e3b48e", "D": "#c69672",
    "E": "#f4f1e8", "P": "#2a2d38", "M": "#8a5a4a",
    "C": "#55617a", "c": "#47516a",
}
PIP = [
    "........................",
    "........................",
    "......#.##..#.#.........",
    ".....###H##H#H##........",
    ".....#HHHHhHHHHh#.......",
    ".....#HhHHHHHhHH#.......",
    ".....#HSSSSSSSSH#.......",
    ".....#SSSSSSSSSS#.......",
    ".....#S##SSSS##S#.......",
    ".....#SSSSSSSSSS#.......",
    ".....#SEPESSEPES#.......",
    ".....#SEEESSEEES#.......",
    ".....#SDSSSSSSDS#.......",
    ".....#SSSS#DSSSS#.......",
    ".....#DSSSSSSSSD#.......",
    ".....#SSS#MM#SSS#.......",
    ".....#SSSSSSSSSS#.......",
    "......#SSSSSSSS#........",
    ".......##DSSD##.........",
    "........#DSSD#..........",
    ".....####CSSC####.......",
    "...##CCCCc##cCCCC##.....",
    "...#CCCCCc##cCCCCC#.....",
    "...#CCcCCCCCCCCcCC#.....",
]

# ---------------- DR. VANCE — scientist, gray side-part, glasses, lab coat ----------------
VANCE_PAL = {
    "#": OUT, "H": "#9aa1a8", "h": "#7d848c", "S": "#c9a184", "D": "#a8815f",
    "E": "#e8e4da", "P": "#20242c", "M": "#6e4638",
    "G": "#14161e", "L": "#54617c",
    "W": "#dfe2e6", "w": "#b9bec8", "C": "#3a4150",
}
VANCE = [
    "........................",
    "........................",
    "........................",
    ".....###########........",
    "....#HHHHHHHHHHH#.......",
    "....#HHhHHHHHHHH#.......",
    "....#HhSSSSSSSHH#.......",
    "....#HhSSSSSSSSH#.......",
    "....#HSSSSSSSSSH#.......",
    "....#HSSSSSSSSSH#.......",
    "....#SGGGGSGGGGS#.......",
    "....#SGLPLGLPLGS#.......",
    "....#SSSSS#DSSSS#.......",
    "....#SSSSS#DSSSS#.......",
    "....#DSSSS#DSSSD#.......",
    "....#DSSSSSSSSSD#.......",
    "....#DSSS####SSS#.......",
    ".....#SSSSSSSSS#........",
    "......#DSSSSSD#.........",
    ".......##DSSD##.........",
    "....#W##WDSSDW##W#......",
    "..##WWWW#SSSS#WWWW##....",
    ".#WWWWWw#CCCC#wWWWWW#...",
    ".#WWWWw#CCCCCC#wWWWW#...",
]

# ---------------- ARIA — manipulator, sleek bob, smirk, earrings ----------------
ARIA_PAL = {
    "#": OUT, "H": "#23202b", "h": "#3a3547", "S": "#d8a67c", "D": "#b8875f",
    "E": "#ece8de", "P": "#241f2b", "M": "#b03a4a", "R": "#d4a53c",
    "C": "#2e2333", "c": "#251c29",
}
ARIA = [
    "........................",
    "........................",
    ".....############.......",
    "....#HHHHHHHHHHHH#......",
    "....#HHHHHHHHHHHH#......",
    "....#HhHHHHHHHHhH#......",
    "....#HHHHHHHHHHHH#......",
    "....#HHSSSSSSSSHH#......",
    "....#HHSSSSSSSSHH#......",
    "....#HHS##SS##SHH#......",
    "....#HH#EPSSPE#HH#......",
    "....#HHSSSSSSSSHH#......",
    "....#HHSSS#DSSSHH#......",
    "....#HHSSSSSSSSHH#......",
    "....#HHS#MMM#SSHH#......",
    "....#RHSSSSSSSSHR#......",
    ".....##DSSSSSSD##.......",
    "......##DSSSSD##........",
    ".......##SSSS##.........",
    "........#SSSS#..........",
    "....####CSSSSC####......",
    "..##CCCCc#SS#cCCCC##....",
    ".#CCCCCCc#SS#cCCCCCC#...",
    ".#CCCCCCCC##CCCCCCCC#...",
]

# ---------------- SAGE — analyst, tight bun, focused ----------------
SAGE_PAL = {
    "#": OUT, "H": "#4a3627", "S": "#d4a077", "D": "#b3835c",
    "E": "#eae6dc", "P": "#26221c", "M": "#7a4a3c",
    "C": "#37474a", "c": "#2e3c3f",
}
SAGE = [
    "........................",
    "..........####..........",
    ".........#HHHH#.........",
    ".....####HHHH####.......",
    "....#HHHHHHHHHHHH#......",
    "....#HHHHHHHHHHHH#......",
    "....#HSSSSSSSSSSH#......",
    "....#SSSSSSSSSSSS#......",
    "....#SSSSSSSSSSSS#......",
    "....#SS##SSSS##SS#......",
    "....#S#EP#SS#PE#S#......",
    "....#SSSSSSSSSSSS#......",
    "....#DSSSS#DSSSSD#......",
    "....#SSSSS#DSSSSS#......",
    "....#DSSSSSSSSSSD#......",
    "....#SSSS####SSSS#......",
    "....#DSSSSSSSSSSD#......",
    ".....#DSSSSSSSSD#.......",
    "......##DSSSSD##........",
    "......#CCCCCCCC#........",
    "...##CCCCCCCCCCCC##.....",
    "..#CCCCCCCCCCCCCCCC#....",
    ".#CCCCCCCCCCCCCCCCCC#...",
    ".#CCcCCCCCCCCCCCCcCC#...",
]

# ---------------- HOLMES — deductive, flat cap, strong brows, tweed ----------------
HOLMES_PAL = {
    "#": OUT, "A": "#6b5138", "a": "#57422d", "H": "#3a2f24",
    "S": "#cf9a70", "D": "#ad7c52", "E": "#e8e4da", "P": "#1c1e26",
    "M": "#6e4638", "C": "#5a4f3e", "c": "#4a4133",
}
HOLMES = [
    "........................",
    "........................",
    ".....############.......",
    "....#AAAAAAAAAAAA#......",
    "....#AAAAAAAAAAAA#......",
    "...##aaaaaaaaaaaa##.....",
    "....#DSSSSSSSSSSD#......",
    "....#SSSSSSSSSSSS#......",
    "....#HSSSSSSSSSSH#......",
    "....#S###SSSS###S#......",
    "....#S#EP#SS#PE#S#......",
    "....#SSSSSSSSSSSS#......",
    "....#DSSSS#DSSSSD#......",
    "....#SSSSS#DSSSSS#......",
    "....#DSSSSSSSSSSD#......",
    "....#SSSS####SSSS#......",
    "....#DSSSSSSSSSSD#......",
    ".....#DSSSSSSSSD#.......",
    "......##DSSSSD##........",
    ".......##DSSD##.........",
    "....####CDSSDC####......",
    "..##CCCCC#SS#CCCCC##....",
    ".#CCcCCCc#SS#cCCCcCC#...",
    ".#CCCCCCCC####CCCCCC#...",
]

# ---------------- MARSHAL — enforcer, buzz cut, walrus mustache, tie ----------------
MARSHAL_PAL = {
    "#": OUT, "H": "#2e2a24", "S": "#b98056", "D": "#996547",
    "E": "#e8e4da", "P": "#1a1c24", "U": "#241f1a",
    "C": "#2f3a52", "T": "#6b1f28", "R": "#c9a13c",
}
MARSHAL = [
    "........................",
    "........................",
    "........................",
    "....##############......",
    "....#HHHHHHHHHHHH#......",
    "....#HSSSSSSSSSSH#......",
    "....#SSSSSSSSSSSS#......",
    "....#SSSSSSSSSSSS#......",
    "....#SSSSSSSSSSSS#......",
    "....#S###SSSS###S#......",
    "....#S#EP#SS#PE#S#......",
    "....#SSSSSSSSSSSS#......",
    "....#DSSSS#DSSSSD#......",
    "....#SSSSS#DSSSSS#......",
    "....#SUUUUUUUUUUS#......",
    "....#SSSSSSSSSSSS#......",
    "....#DSSSSSSSSSSD#......",
    "....##DSSSSSSSSD##......",
    "......#DSSSSSSD#........",
    ".......##SSSS##.........",
    "....####CDSSDC####......",
    "..##CCCCC#TT#CCCCC##....",
    ".#CCRCCCC#TT#CCCCCCC#...",
    ".#CCCCCCC#TT#CCCCCCC#...",
]

# ---------------- SOCRATES — philosopher, bald, white beard, bushy brows ----------------
SOCRATES_PAL = {
    "#": OUT, "H": "#b8bcc2", "B": "#c9cdd3", "b": "#a7abb3",
    "S": "#c9a184", "D": "#a8815f", "E": "#e6e2d8", "P": "#23262e",
    "M": "#5e3a30", "C": "#4a4437", "c": "#3d382d",
}
SOCRATES = [
    "........................",
    "........................",
    "........................",
    ".....############.......",
    "....#SSSSSSSSSSSS#......",
    "....#SSSSSSSSSSSS#......",
    "....#HSSSSSSSSSSH#......",
    "....#HSSSSSSSSSSH#......",
    "....#HSSSSSSSSSSH#......",
    "....#HBBBSSSSBBBH#......",
    "....#S#EP#SS#PE#S#......",
    "....#SSSSSSSSSSSS#......",
    "....#DSSSS#DSSSSD#......",
    "....#BSSSS#DSSSSB#......",
    "....#BBSSSSSSSSBB#......",
    "....#BBBB#MM#BBBB#......",
    "....#BBBBBBBBBBBB#......",
    "....#bBBBBBBBBBBb#......",
    ".....#bBBBBBBBBb#.......",
    "......#BBBBBBBB#........",
    "...##CCC#BBBB#CCC##.....",
    "..#CCCCCC#BB#CCCCCC#....",
    ".#CCCCCCCcBBcCCCCCCC#...",
    ".#CCCCCCCCccCCCCCCCC#...",
]

# ---------------- CHEN — investigator, straight black fringe, sharp eyes ----------------
CHEN_PAL = {
    "#": OUT, "H": "#14161c", "h": "#262a34", "S": "#e0b087", "D": "#bd9066",
    "E": "#ece8de", "P": "#16181e", "M": "#7a4a3c",
    "C": "#414b5e", "c": "#363f50", "W": "#cfd3da",
}
CHEN = [
    "........................",
    "........................",
    ".....############.......",
    "....#HHHHHHHHHHHH#......",
    "....#HHHHHHHHHHHH#......",
    "....#HHHHHHHHHHHH#......",
    "....#HhHHHHHHHHhH#......",
    "....#HSSSSSSSSSSH#......",
    "....#HS##SSSS##SH#......",
    "....#H#EP#SS#PE#H#......",
    "....#HSSSSSSSSSSH#......",
    "....#SSSSS#DSSSSS#......",
    "....#DSSSS#DSSSSD#......",
    "....#DSSSSSSSSSSD#......",
    "....#SSSS#MM#SSSS#......",
    "....#DSSSSSSSSSSD#......",
    ".....#DSSSSSSSSD#.......",
    "......##DSSSSD##........",
    ".......#DSSSSD#.........",
    ".......#WSSSSW#.........",
    "....####WDSSDW####......",
    "..##CCCCC#WW#CCCCC##....",
    ".#CCCCCCC#WW#CCCCCCC#...",
    ".#CCCCCCCC####CCCCCC#...",
]

# ---------------- AMBASSADOR SILVA — diplomat, silver slick-back, suit, smile ----------------
SILVA_PAL = {
    "#": OUT, "H": "#c2c7cd", "h": "#9ba1a9", "S": "#b9825a", "D": "#986747",
    "E": "#eae6dc", "P": "#1e2028", "M": "#6e4234",
    "C": "#23262e", "c": "#2e323c", "W": "#e8e8ea", "T": "#7c2430",
}
SILVA = [
    "........................",
    "........................",
    ".....############.......",
    "....#HHHHHHHHHHHH#......",
    "....#HhHHHHHHHhHH#......",
    "....#HHhHHHHHHHHH#......",
    "....#HSSSSSSSSSSH#......",
    "....#HSSSSSSSSSSH#......",
    "....#SSSSSSSSSSSS#......",
    "....#SS##SSSS##SS#......",
    "....#S#EP#SS#PE#S#......",
    "....#SSSSSSSSSSSS#......",
    "....#DSSSS#DSSSSD#......",
    "....#SSSSS#DSSSSS#......",
    "....#DSS#SSSS#SSD#......",
    "....#SSSSMMMMSSSS#......",
    "....#DSSSSSSSSSSD#......",
    ".....#DSSSSSSSSD#.......",
    "......##DSSSSD##........",
    ".......#DSSSSD#.........",
    "....####WDSSDW####......",
    "..##cCCCC#TT#CCCCc##....",
    ".#CcCCCCC#TT#CCCCCcC#...",
    ".#CCCCCCC#TT#CCCCCCC#...",
]

FACES = [
    ("rico", RICO, RICO_PAL), ("aria", ARIA, ARIA_PAL), ("sage", SAGE, SAGE_PAL),
    ("holmes", HOLMES, HOLMES_PAL), ("marshal", MARSHAL, MARSHAL_PAL),
    ("socrates", SOCRATES, SOCRATES_PAL), ("vance", VANCE, VANCE_PAL),
    ("pip", PIP, PIP_PAL), ("chen", CHEN, CHEN_PAL), ("silva", SILVA, SILVA_PAL),
]


def hex_to_rgb(s):
    s = s.lstrip("#")
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def render(grid, pal, scale):
    img = Image.new("RGB", (W * scale, H * scale))
    px = img.load()
    for y, row in enumerate(grid):
        assert len(row) == W, f"row {y} has {len(row)} cols"
        for x, ch in enumerate(row):
            if ch == ".":
                color = BGLINE if y in LINE_ROWS else BG
            else:
                color = pal[ch]
            r, g, b = hex_to_rgb(color)
            for dy in range(scale):
                for dx in range(scale):
                    px[x * scale + dx, y * scale + dy] = (r, g, b)
    return img


def emit_svg(grid, pal, path):
    # One rect per horizontal run of same-colored pixels.
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" shape-rendering="crispEdges">',
        f'<rect width="{W}" height="{H}" fill="{BG}"/>',
    ]
    for y in LINE_ROWS:
        parts.append(f'<rect y="{y}" width="{W}" height="1" fill="{BGLINE}"/>')
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
    assert all(len(g) == H for _, g, _ in FACES)
    pad = 24
    cols = 5
    big = [render(g, p, 12) for _, g, p in FACES]
    small = [render(g, p, 2) for _, g, p in FACES]  # 48px — stamp size check
    bw = W * 12
    rows = -(-len(FACES) // cols)
    sheet = Image.new(
        "RGB",
        (pad + (bw + pad) * cols, pad + (bw + pad) * rows + 48 + pad),
        hex_to_rgb("#191c24"),
    )
    for i, im in enumerate(big):
        sheet.paste(im, (pad + (i % cols) * (bw + pad), pad + (i // cols) * (bw + pad)))
    for i, im in enumerate(small):
        sheet.paste(im, (pad + i * (48 + pad // 2), pad + (bw + pad) * rows))
    out = "/private/tmp/claude-501/-Users-nick-Developer-LLM-Mafia/73ff8f13-721a-4b58-8f22-3e70174d5909/scratchpad/sheet.png"
    sheet.save(out)
    print("wrote", out)

    import os
    avdir = "/Users/nick/Developer/LLM-Mafia/viewer/public/avatars"
    os.makedirs(avdir, exist_ok=True)
    for name, g, p in FACES:
        emit_svg(g, p, f"{avdir}/{name}.svg")
    print("wrote", len(FACES), "svgs to", avdir)


if __name__ == "__main__":
    main()
