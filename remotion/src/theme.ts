// Zones sûres plateformes (px sur un canvas 1080x1920)
export const SAFE_TOP = 150;
export const SAFE_BOTTOM = 320;

export const WIDTH = 1080;
export const HEIGHT = 1920;
export const FPS = 30;

export const COLORS = {
  text: "#FFFFFF",
  active: "#FFD400", // mot en cours
  hookBg: "rgba(10,10,14,0.72)",
  ctaBg: "rgba(10,10,14,0.80)",
  accent: "#FF2D6F",
};

// Ombre portée épaisse : lisible sur sable clair comme sur eau sombre
export const TEXT_SHADOW = [
  "0 0 18px rgba(0,0,0,0.85)",
  "0 6px 14px rgba(0,0,0,0.75)",
  "0 2px 0 rgba(0,0,0,0.9)",
].join(", ");
