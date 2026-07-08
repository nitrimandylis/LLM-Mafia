"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

export default function TopBar() {
  const path = usePathname();
  // Landing page (/) has its own full-bleed chrome — no viewer top bar.
  if (path === "/") return null;
  return (
    <header className="topbar">
      <Link href="/" className="brand">
        <span className="mark">MAFIA</span>
        <span className="rest">LLM REPLAY</span>
      </Link>
      <nav>
        <Link href="/watch" className={path.startsWith("/watch") ? "active" : ""}>
          Viewer
        </Link>
        <Link href="/settings" className={path === "/settings" ? "active" : ""}>
          Settings
        </Link>
      </nav>
    </header>
  );
}
