import { Easing, interpolate, spring } from "remotion";

// Pop d'apparition avec depassement (le "pop" des cartes de la reference)
export const pop = (frame: number, fps: number, delay = 0) =>
  spring({ frame: frame - delay, fps, config: { damping: 11, stiffness: 170, mass: 0.7 } });

export const fadeIn = (frame: number, fps: number, dur = 0.2, delay = 0) =>
  interpolate(frame, [delay * fps, (delay + dur) * fps], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

// Sortie rapide en fin de scene
export const fadeOut = (frame: number, fps: number, total: number, dur = 0.12) =>
  interpolate(frame, [total - dur * fps, total], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

export const fmtMoney = (n: number) => {
  const s = Math.round(n).toString();
  return s.replace(/\B(?=(\d{3})+(?!\d))/g, " ");
};
