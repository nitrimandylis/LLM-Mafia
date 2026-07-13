import type { SkinId } from "@/lib/settings";

// One glyph per view: a speech bubble, a case folder, a deposition page, a
// suspicion network. Stroke uses currentColor so it follows the tab's state.
export default function SkinIcon({ id }: { id: SkinId }) {
  const p = {
    width: 18, height: 18, viewBox: "0 0 16 16", fill: "none",
    stroke: "currentColor", strokeWidth: 1.4,
    strokeLinecap: "round" as const, strokeLinejoin: "round" as const,
    "aria-hidden": true,
  };
  switch (id) {
    case "chat":
      return <svg {...p}><path d="M2.5 3.5h11v6.5h-7L4 12.5V10H2.5z" /></svg>;
    case "casefile":
      return <svg {...p}><path d="M2 4.5h4l1.3 1.5H14v6.5H2z" /></svg>;
    case "transcript":
      return <svg {...p}><path d="M4 2.2h5L12 5v8.8H4z" /><path d="M6 7.5h4M6 10h3" /></svg>;
    case "signal":
      return (
        <svg {...p}>
          <path d="M4.4 4.8 8 11M11.6 5.4 8 11" />
          <circle cx="3.5" cy="4" r="1.3" /><circle cx="12.5" cy="4.5" r="1.3" /><circle cx="8" cy="12" r="1.6" />
        </svg>
      );
  }
}
