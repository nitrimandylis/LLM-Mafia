"use client";

import { useEffect, useRef, useState } from "react";

// Lights the record strip's neon when it scrolls into view.
//
// This is JS rather than animation-timeline: view() because a scroll timeline
// scrubs rather than plays: the flicker runs at whatever speed you happen to
// scroll, so a trackpad flick collapses eight keyframes into three frames and
// reads as a pop. A class swap lets the warm-up run on its own clock, the same
// 900ms every time. Its children are rendered on the server; this only adds the
// class, so with JS off the numbers are simply already lit.
export default function NeonOnView({ children }: { children: React.ReactNode }) {
  const ref = useRef<HTMLDivElement>(null);
  const [lit, setLit] = useState(false);

  useEffect(() => {
    const strip = ref.current;
    if (!strip) return;

    const observer = new IntersectionObserver(
      (entries) => {
        if (!entries[0].isIntersecting) return;
        setLit(true);
        // The sign only warms up once; after that it just hums.
        observer.disconnect();
      },
      // "Any part of it has risen into the top 75% of the screen", not "how
      // much of it is showing". A percentage-visible threshold would depend on
      // the strip's own height, and on a short landscape viewport a stacked
      // strip taller than the root would never reach it and never light up.
      { threshold: 0, rootMargin: "0px 0px -25% 0px" },
    );

    observer.observe(strip);
    return () => observer.disconnect();
  }, []);

  return (
    <div ref={ref} className={lit ? "lp-stats lit" : "lp-stats"}>
      {children}
    </div>
  );
}
