import { useState } from "react";
import { initials } from "./types";

// Pixel-art mugshot for a player, falling back to colored initials when no
// portrait exists for that name. Portraits live in public/avatars/, one per
// cast member, keyed by the last word of the name: "DR. VANCE" -> vance.svg.
export default function Mug({ name, color, className }: { name: string; color: string; className: string }) {
  const [missing, setMissing] = useState(false);
  const slug = name.trim().split(/\s+/).pop()!.replace(/[^a-zA-Z]/g, "").toLowerCase();

  if (missing || !slug) {
    return (
      <div className={className} style={{ background: color }}>
        {initials(name)}
      </div>
    );
  }
  return (
    <img
      className={`${className} mug`}
      src={`/avatars/${slug}.svg`}
      alt={name}
      style={{ boxShadow: `0 0 0 1.5px ${color}` }}
      onError={() => setMissing(true)}
    />
  );
}
