"use client";

// Synthesized stings for the episode player — no audio assets, one shared
// AudioContext. Browsers only allow audio after a user gesture, so
// unlockAudio() is called from the cold-open BEGIN click (and Play).
// ponytail: plain oscillators with decay envelopes; swap for samples only if
// the synth ever feels cheap.

let ctx: AudioContext | null = null;

const KEY = "mafia-viewer-sound";

export function soundMuted(): boolean {
  if (typeof window === "undefined") return true;
  return localStorage.getItem(KEY) === "muted";
}

export function setSoundMuted(muted: boolean) {
  if (typeof window !== "undefined") {
    localStorage.setItem(KEY, muted ? "muted" : "on");
  }
}

export function unlockAudio() {
  if (typeof window === "undefined") return;
  if (!ctx) {
    const AC = window.AudioContext ?? (window as unknown as { webkitAudioContext?: typeof AudioContext }).webkitAudioContext;
    if (!AC) return; // no WebAudio — episodes just play silently
    ctx = new AC();
  }
  void ctx.resume();
}

// One note: oscillator -> gain envelope -> out. Frequency can glide.
function tone(
  freq: number,
  opts: { type?: OscillatorType; at?: number; dur?: number; vol?: number; glideTo?: number } = {}
) {
  if (!ctx) return;
  const { type = "sine", at = 0, dur = 0.3, vol = 0.08, glideTo } = opts;
  const t0 = ctx.currentTime + at;
  const osc = ctx.createOscillator();
  const gain = ctx.createGain();
  osc.type = type;
  osc.frequency.setValueAtTime(freq, t0);
  if (glideTo) osc.frequency.exponentialRampToValueAtTime(glideTo, t0 + dur);
  gain.gain.setValueAtTime(vol, t0);
  gain.gain.exponentialRampToValueAtTime(0.0001, t0 + dur);
  osc.connect(gain).connect(ctx.destination);
  osc.start(t0);
  osc.stop(t0 + dur + 0.05);
}

export type StingKind = "begin" | "vote" | "night" | "kill" | "save" | "reveal";

export function sting(kind: StingKind) {
  if (soundMuted() || !ctx || ctx.state !== "running") return;
  switch (kind) {
    case "begin": // low curtain-up pad
      tone(82, { dur: 1.4, vol: 0.07 });
      tone(164, { dur: 1.4, vol: 0.04 });
      break;
    case "vote": // dry ballot tick
      tone(720, { type: "square", dur: 0.05, vol: 0.025 });
      break;
    case "night": // slow swell as the lights go down
      tone(110, { dur: 1.8, vol: 0.06 });
      tone(163, { dur: 1.8, vol: 0.03 });
      break;
    case "kill": // detuned pair falling into the dark
      tone(196, { type: "sawtooth", dur: 1.3, vol: 0.05, glideTo: 62 });
      tone(202, { type: "sawtooth", dur: 1.3, vol: 0.05, glideTo: 65 });
      break;
    case "save": // small upward relief
      tone(330, { dur: 0.35, vol: 0.05, glideTo: 440 });
      break;
    case "reveal": // final chord, held
      tone(220, { dur: 2.2, vol: 0.06 });
      tone(277, { at: 0.08, dur: 2.1, vol: 0.05 });
      tone(330, { at: 0.16, dur: 2.0, vol: 0.05 });
      break;
  }
}
