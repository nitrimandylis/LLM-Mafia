"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

export default function TopBar() {
  const path = usePathname();
  return (
    <header className="topbar">
      <Link href="/" className="brand" style={{ textDecoration: "none" }}>
        LLM <span className="accent">MAFIA</span> · REPLAY
      </Link>
      <nav>
        <Link href="/" className={path === "/" ? "active" : ""}>
          Viewer
        </Link>
        <Link href="/settings" className={path === "/settings" ? "active" : ""}>
          Settings
        </Link>
      </nav>
    </header>
  );
}
