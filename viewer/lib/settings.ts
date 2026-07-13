export type SkinId = "chat" | "casefile" | "transcript" | "signal";

export type SkinMeta = {
  id: SkinId;
  name: string;
  tag: string; // short descriptor for the switcher
  blurb: string; // tooltip line on the switcher tabs
  // Three colors that preview this design's world: [background, accent, ink].
  swatch: [string, string, string];
};

// Single source of truth for the four designs — drives the switcher and homepage.
export const SKINS: SkinMeta[] = [
  {
    id: "chat",
    name: "Group Chat",
    tag: "the thread",
    blurb: "A messaging thread: grouped bubbles, day/night theming, votes folded into a ballot strip, mafia in a locked side-channel.",
    swatch: ["#0a0b10", "#c41e1e", "#e0e0e0"],
  },
  {
    id: "casefile",
    name: "Case File",
    tag: "the board",
    blurb: "You're the detective. Typed testimony on manila paper, suspect ID cards, and intercepted mafia comms stamped DECLASSIFIED.",
    swatch: ["#e3d9c0", "#a6261c", "#211c15"],
  },
  {
    id: "transcript",
    name: "Transcript",
    tag: "the record",
    blurb: "A line-numbered court deposition. Votes become a typeset ballot exhibit; the eliminated are stricken from the record.",
    swatch: ["#f2ede3", "#6e1a1a", "#22201b"],
  },
  {
    id: "signal",
    name: "Signal",
    tag: "the network",
    blurb: "An instrument panel. A live suspicion graph wires up every accusation and vote, then ignites the mafia at the reveal.",
    swatch: ["#050505", "#c41e1e", "#b5b5bd"],
  },
];
