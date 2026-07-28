import Link from "next/link";

export const GITHUB = "https://github.com/nitrimandylis/LLM-Mafia";

// Shared across the landing, /rules and /about, all three render inside .lp,
// so the styles come from landing.css.
export default function SiteFooter() {
  return (
    <footer className="lp-footer">
      <div className="fmark">
        <span className="l1">LLM</span>
        <span className="l2">MAFIA</span>
      </div>
      <div className="fnav">
        <Link href="/rules">Rules</Link>
        <span className="sep">│</span>
        <Link href="/about">About</Link>
        <span className="sep">│</span>
        <a href="https://github.com/nitrimandylis" target="_blank" rel="noreferrer">
          Nick Trimandylis
        </a>
        <span className="sep">│</span>
        <span className="mit">MIT licensed</span>
        <span className="sep">│</span>
        <span className="slogan">LLMS LIE. PROVED IT.</span>
      </div>
    </footer>
  );
}
