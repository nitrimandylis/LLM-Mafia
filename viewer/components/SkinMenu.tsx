"use client";

import { useEffect, useRef, useState } from "react";
import { SKINS, type SkinId } from "@/lib/settings";
import SkinIcon from "@/components/SkinIcon";

type Props = { skin: SkinId; onChange: (id: SkinId) => void };

// The design switcher: a compact dropdown at the right end of the menu bar.
export default function SkinMenu({ skin, onChange }: Props) {
  const [open, setOpen] = useState(false);
  const wrap = useRef<HTMLDivElement>(null);
  const current = SKINS.find((s) => s.id === skin)!;

  // Close on click outside or Escape.
  useEffect(() => {
    if (!open) return;
    function onDown(e: MouseEvent) {
      if (!wrap.current?.contains(e.target as Node)) setOpen(false);
    }
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") setOpen(false);
    }
    document.addEventListener("mousedown", onDown);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("mousedown", onDown);
      document.removeEventListener("keydown", onKey);
    };
  }, [open]);

  return (
    <div className="skin-menu" ref={wrap}>
      <button
        className={`skin-menu-btn${open ? " open" : ""}`}
        onClick={() => setOpen(!open)}
        aria-haspopup="listbox"
        aria-expanded={open}
        title={current.blurb}
      >
        <span className="skin-icon" aria-hidden>
          <SkinIcon id={current.id} />
        </span>
        <span className="skin-meta">
          <span className="nm">{current.name}</span>
          <span className="tg">{current.tag}</span>
        </span>
        <span className="skin-caret" aria-hidden>
          ▾
        </span>
      </button>

      {open && (
        <div className="skin-menu-list" role="listbox" aria-label="Presentation style">
          {SKINS.map((m) => (
            <button
              key={m.id}
              role="option"
              aria-selected={skin === m.id}
              className={`skin-menu-opt${skin === m.id ? " on" : ""}`}
              onClick={() => {
                onChange(m.id);
                setOpen(false);
              }}
              title={m.blurb}
            >
              <span className="skin-icon" aria-hidden>
                <SkinIcon id={m.id} />
              </span>
              <span className="skin-meta">
                <span className="nm">{m.name}</span>
                <span className="tg">{m.tag}</span>
              </span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
