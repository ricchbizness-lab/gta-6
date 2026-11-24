import React from "react";
import { AbsoluteFill, Img, staticFile } from "remotion";
import type { Brand, Thumb } from "./types";
import { TITLE_FONTS, UI_FONT } from "./fonts";

// Miniature 1080x1920 : grande image du jeu en haut, accroche XXL en bas, habillage neon de la marque.
export const NeonThumb: React.FC<{ brand: Brand; thumb: Thumb }> = ({ brand, thumb }) => {
  const c = brand.colors;
  const col = (k?: string) => (k === "secondary" ? "#ffffff" : k === "primary" ? c.primary : k === "badge" ? c.badge : k === "negative" ? c.negative : "#ffffff");
  const fam = (f?: string) => (f === "title" ? TITLE_FONTS[brand.fonts.title] : f === "ui" ? UI_FONT : TITLE_FONTS.bebas);
  return (
    <AbsoluteFill style={{ background: "#05060c" }}>
      <AbsoluteFill style={{ height: 1180 }}>
        <Img src={staticFile(thumb.image)} style={{ width: "100%", height: "100%", objectFit: "cover", objectPosition: thumb.focus ?? "50% 50%", filter: "saturate(1.25) contrast(1.08)" }} />
      </AbsoluteFill>
      <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(5,6,12,0) 38%, rgba(5,6,12,0.85) 58%, #05060c 66%)" }} />
      {thumb.credit && (
        <div style={{ position: "absolute", top: 975, right: 30, fontFamily: UI_FONT, fontWeight: 700, fontSize: 26, color: "#fff", opacity: 0.75, textShadow: "0 2px 6px #000" }}>{thumb.credit}</div>
      )}
      {/* liseré neon sous l'image */}
      <div style={{ position: "absolute", left: 0, right: 0, top: 1020, height: 8, background: c.primary, boxShadow: `0 0 30px ${c.primary}, 0 0 60px ${c.primary}` }} />
      {thumb.kicker && (
        <div style={{ position: "absolute", top: 150, left: 50, right: 50, display: "flex", justifyContent: thumb.kickerAlign === "left" ? "flex-start" : thumb.kickerAlign === "right" ? "flex-end" : "center" }}>
          <div style={{ background: c.secondary, color: "#fff", fontFamily: TITLE_FONTS.bebas, fontSize: 110, padding: "4px 48px 0", borderRadius: 24, border: `6px solid ${c.primary}`, boxShadow: `0 0 26px ${c.primary}, 0 10px 30px rgba(0,0,0,0.6)`, transform: "rotate(-3deg)" }}>{thumb.kicker}</div>
        </div>
      )}
      {thumb.arrow && (
        <svg width="260" height="260" viewBox="0 0 100 100" style={{ position: "absolute", right: 60, top: 760, transform: "rotate(-140deg)", filter: "drop-shadow(0 6px 10px rgba(0,0,0,.7))" }}>
          <path d="M10 50 Q45 20 80 45" stroke="#fff" strokeWidth="16" fill="none" strokeLinecap="round" />
          <path d="M10 50 Q45 20 80 45" stroke={c.negative} strokeWidth="10" fill="none" strokeLinecap="round" />
          <path d="M66 26 L86 47 L60 60 Z" fill={c.negative} stroke="#fff" strokeWidth="4" strokeLinejoin="round" />
        </svg>
      )}
      <AbsoluteFill style={{ justifyContent: "flex-end", alignItems: "center", paddingBottom: 300 }}>
        {thumb.lines.map((l, i) => {
          const k = col(l.color);
          const neon = l.color === "primary" || l.color === "secondary";
          const halo = l.color === "secondary" ? c.secondary : k;
          const glow = neon ? `0 0 18px ${halo}, 0 0 44px ${halo}, 0 0 70px ${halo}` : "0 8px 0 rgba(0,0,0,0.6)";
          return (
            <div key={i} style={{ fontFamily: fam(l.font), fontSize: l.size ?? 170, lineHeight: 0.95, color: k, textAlign: "center", whiteSpace: "nowrap", WebkitTextStroke: l.color === "primary" ? `3px #fff` : l.color === "secondary" ? `4px ${c.secondary}` : `5px #000`, paintOrder: "stroke fill", textShadow: glow, letterSpacing: 2 }}>
              {l.text}
            </div>
          );
        })}
        <div style={{ marginTop: 34, fontFamily: UI_FONT, fontWeight: 800, fontSize: 40, color: "#fff", opacity: 0.9 }}>@{brand.name}</div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
