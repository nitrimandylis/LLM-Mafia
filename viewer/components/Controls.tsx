"use client";

import type { ReplayState, Speed } from "@/lib/useReplay";

const SPEEDS: { id: Speed; label: string }[] = [
  { id: 1, label: "1×" },
  { id: 2, label: "2×" },
  { id: "instant", label: "Skip" },
];

export default function Controls({ state }: { state: ReplayState }) {
  const { playing, speed, cursor, total, controls } = state;
  const done = cursor >= total;

  return (
    <div className="controls">
      <button
        className="primary"
        onClick={() => (done ? controls.restart() : controls.toggle())}
      >
        {done ? "↻ Replay" : playing ? "⏸ Pause" : "▶ Play"}
      </button>

      <div className="speeds">
        {SPEEDS.map((s) => (
          <button
            key={String(s.id)}
            className={speed === s.id ? "on" : ""}
            onClick={() => controls.setSpeed(s.id)}
          >
            {s.label}
          </button>
        ))}
      </div>

      <input
        className="scrub"
        type="range"
        min={0}
        max={total}
        value={cursor}
        onChange={(e) => controls.scrubTo(Number(e.target.value))}
      />
      <div className="count mono">
        {cursor} / {total}
      </div>
    </div>
  );
}
