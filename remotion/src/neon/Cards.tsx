import React from "react";
import { Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import type { Brand, Card } from "./types";
import { fmtMoney, pop } from "./anim";
import { TITLE_FONTS, UI_FONT } from "./fonts";

const W = 840; // largeur des cartes (~78 % de 1080, mesure sur la reference)

const Panel: React.FC<{ brand: Brand; children: React.ReactNode; width?: number; style?: React.CSSProperties }> = ({
  brand, children, width = W, style,
}) => (
  <div
    style={{
      width,
      background: brand.colors.panel,
      borderRadius: 34,
      border: `5px solid ${brand.colors.primary}`,
      boxShadow: `0 0 24px ${brand.colors.primary}88, 0 18px 40px rgba(0,0,0,0.55)`,
      padding: "30px 34px",
      color: brand.colors.text,
      fontFamily: UI_FONT,
      ...style,
    }}
  >
    {children}
  </div>
);

const IconTile: React.FC<{ brand: Brand; glyph: string; size?: number }> = ({ brand, glyph, size = 132 }) => (
  <div
    style={{
      width: size, height: size, borderRadius: 28, flexShrink: 0,
      background: `linear-gradient(135deg, ${brand.colors.primary}, ${brand.colors.secondary})`,
      display: "flex", alignItems: "center", justifyContent: "center",
      fontFamily: UI_FONT, fontWeight: 900, fontSize: size * 0.42, color: "#fff",
      boxShadow: `0 0 18px ${brand.colors.primary}aa`,
    }}
  >
    {glyph}
  </div>
);

const Lock: React.FC<{ color: string }> = ({ color }) => (
  <svg width="64" height="76" viewBox="0 0 64 76">
    <rect x="6" y="32" width="52" height="40" rx="9" fill={color} />
    <path d="M17 33 V21 a15 15 0 0 1 30 0 V33" stroke={color} strokeWidth="8" fill="none" />
  </svg>
);

const StateMark: React.FC<{ brand: Brand; state: "done" | "locked" | "cross" }> = ({ brand, state }) => {
  const bg = state === "done" ? brand.colors.positive : state === "cross" ? brand.colors.negative : "#3a3350";
  return (
    <div style={{ width: 62, height: 62, borderRadius: 16, background: bg, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
      <svg width="40" height="40" viewBox="0 0 40 40">
        {state === "done" && <path d="M7 21 L16 30 L33 10" stroke="#0b0b10" strokeWidth="7" fill="none" strokeLinecap="round" strokeLinejoin="round" />}
        {state === "cross" && <path d="M9 9 L31 31 M31 9 L9 31" stroke="#fff" strokeWidth="7" strokeLinecap="round" />}
        {state === "locked" && (
          <g fill="#cfc6e6"><rect x="9" y="18" width="22" height="17" rx="4" /><path d="M14 19 V13 a6 6 0 0 1 12 0 V19" stroke="#cfc6e6" strokeWidth="4" fill="none" /></g>
        )}
      </svg>
    </div>
  );
};

export const CardView: React.FC<{ brand: Brand; card: Card; localFrame: number }> = ({ brand, card, localFrame }) => {
  const { fps } = useVideoConfig();
  const frame = useCurrentFrame();
  const f = localFrame ?? frame;
  const s = pop(f, fps);
  const wrap = (node: React.ReactNode) => (
    <div style={{ transform: `scale(${0.55 + 0.45 * s})`, opacity: Math.min(1, s * 1.6) }}>{node}</div>
  );

  switch (card.type) {
    case "stat": {
      const target = card.countTo ?? 0;
      const v = card.countTo !== undefined
        ? interpolate(f, [4, 4 + 0.8 * fps], [0, target], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })
        : 0;
      return wrap(
        <Panel brand={brand}>
          <div style={{ display: "flex", gap: 30, alignItems: "center" }}>
            <IconTile brand={brand} glyph={card.icon} />
            <div style={{ flex: 1 }}>
              <div style={{ fontWeight: 900, fontSize: 50, letterSpacing: 1 }}>{card.label}</div>
              {card.sub && <div style={{ fontWeight: 700, fontSize: 34, color: brand.colors.primary, marginTop: 2 }}>{card.sub}</div>}
              {(card.value || card.countTo !== undefined) && (
                <div style={{ marginTop: 16, display: "inline-block", border: `4px solid ${brand.colors.primary}`, borderRadius: 40, padding: "6px 34px", fontWeight: 900, fontSize: 46 }}>
                  {card.countTo !== undefined ? `${card.prefix ?? "$"} ${fmtMoney(v)}` : card.value}
                </div>
              )}
            </div>
            {card.lock && <Lock color={brand.colors.badge} />}
          </div>
        </Panel>,
      );
    }
    case "compare": {
      const side = (lab: string, val: number, i: number, win: boolean) => {
        const ss = pop(f, fps, i * 4);
        const v = interpolate(f, [8, 8 + 0.9 * fps], [0, val], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
        return (
          <div style={{ transform: `scale(${0.6 + 0.4 * ss}) rotate(${win ? 3 : -2}deg)` }}>
            <Panel brand={brand} width={390} style={{ padding: "26px 22px", textAlign: "center", borderColor: win ? brand.colors.positive : brand.colors.primary }}>
              <div style={{ fontFamily: TITLE_FONTS[brand.fonts.title], fontSize: 48, color: "#fff", lineHeight: 1.05, minHeight: 104 }}>{lab}</div>
              <div style={{ marginTop: 18, border: `4px solid ${win ? brand.colors.positive : brand.colors.primary}`, borderRadius: 30, padding: "6px 10px", fontWeight: 900, fontSize: 40 }}>
                $ {fmtMoney(v)}
              </div>
            </Panel>
          </div>
        );
      };
      return (
        <div style={{ display: "flex", gap: 34, justifyContent: "center" }}>
          {side(card.left.label, card.left.value, 0, false)}
          {side(card.right.label, card.right.value, 1, true)}
        </div>
      );
    }
    case "badge": {
      const ring = (f / fps) * 40;
      const pulse = 1 + 0.06 * Math.sin((f / fps) * Math.PI * 2.4);
      return (
        <div style={{ transform: `scale(${(0.3 + 0.7 * s) * pulse})`, position: "relative", width: 420, height: 420 }}>
          <svg width="420" height="420" style={{ position: "absolute", inset: 0, transform: `rotate(${ring}deg)` }}>
            <circle cx="210" cy="210" r="196" stroke={brand.colors.primary} strokeWidth="9" strokeDasharray="22 16" fill="none" />
          </svg>
          <div
            style={{
              position: "absolute", inset: 34, borderRadius: "50%",
              background: `radial-gradient(circle at 35% 30%, ${brand.colors.secondary}, ${brand.colors.primary})`,
              border: "9px solid #fff", boxShadow: `0 0 50px ${brand.colors.primary}`,
              display: "flex", alignItems: "center", justifyContent: "center",
              fontFamily: UI_FONT, fontWeight: 900, fontSize: 220, color: "#fff",
              textShadow: "0 8px 0 rgba(0,0,0,0.35)", WebkitTextStroke: "6px #1b1028",
            }}
          >
            {card.n}
          </div>
        </div>
      );
    }
    case "checklist":
      return wrap(
        <Panel brand={brand} style={{ padding: 0, overflow: "hidden" }}>
          <div style={{ background: `linear-gradient(90deg, ${brand.colors.primary}, ${brand.colors.secondary})`, padding: "16px 30px", fontWeight: 900, fontSize: 38, letterSpacing: 1 }}>
            {card.title}
          </div>
          <div style={{ padding: "22px 30px", display: "flex", flexDirection: "column", gap: 18 }}>
            {card.items.map((it, i) => {
              const si = pop(f, fps, 5 + i * 5);
              return (
                <div key={i} style={{ display: "flex", alignItems: "center", gap: 22, opacity: Math.min(1, si * 1.5), transform: `translateX(${(1 - si) * -60}px)` }}>
                  <StateMark brand={brand} state={it.state} />
                  <div style={{ fontWeight: 800, fontSize: 44, textDecoration: it.state === "cross" ? "line-through" : "none" }}>{it.label}</div>
                </div>
              );
            })}
          </div>
        </Panel>,
      );
    case "levels": {
      const n = card.items.length;
      return wrap(
        <Panel brand={brand}>
          <div style={{ display: "flex", alignItems: "flex-end", gap: 26, height: 330, justifyContent: "center" }}>
            {card.items.map((lab, i) => {
              const g = interpolate(f, [4 + i * 5, 4 + i * 5 + 0.35 * fps], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
              const h = (80 + (230 * (i + 1)) / n) * g;
              return (
                <div key={i} style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 10 }}>
                  <div style={{ width: 120, height: h, borderRadius: 16, background: `linear-gradient(180deg, ${brand.colors.primary}, ${brand.colors.secondary})`, boxShadow: `0 0 18px ${brand.colors.primary}88`, display: "flex", justifyContent: "center", paddingTop: 10, fontWeight: 900, fontSize: 40 }}>
                    {i + 1}
                  </div>
                  <div style={{ fontWeight: 800, fontSize: 26, opacity: g }}>{lab}</div>
                </div>
              );
            })}
          </div>
        </Panel>,
      );
    }
    case "gauge": {
      const v = interpolate(f, [5, 5 + 1.0 * fps], [0, card.value], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
      return wrap(
        <Panel brand={brand}>
          <div style={{ display: "flex", justifyContent: "space-between", fontWeight: 900, fontSize: 34 }}>
            <span style={{ color: brand.colors.positive }}>{card.left}</span>
            <span style={{ color: brand.colors.negative }}>{card.right}</span>
          </div>
          <div style={{ position: "relative", height: 40, marginTop: 18, borderRadius: 20, background: `linear-gradient(90deg, ${brand.colors.positive}, #ffd54a, ${brand.colors.negative})` }}>
            <div style={{ position: "absolute", top: -12, left: `calc(${v * 100}% - 32px)`, width: 64, height: 64, borderRadius: "50%", background: brand.colors.primary, border: "7px solid #fff", boxShadow: `0 0 20px ${brand.colors.primary}` }} />
          </div>
          {card.verdict && v >= card.value * 0.98 && (
            <div style={{ marginTop: 26, textAlign: "center" }}>
              <span style={{ border: `4px solid ${brand.colors.negative}`, color: brand.colors.negative, borderRadius: 14, padding: "8px 26px", fontWeight: 900, fontSize: 40 }}>{card.verdict}</span>
            </div>
          )}
        </Panel>,
      );
    }
    case "image":
      return wrap(
        <Panel brand={brand} style={{ padding: 14 }}>
          <Img src={staticFile(card.src)} style={{ width: "100%", height: 520, objectFit: "cover", borderRadius: 22, display: "block" }} />
          {card.caption && <div style={{ textAlign: "center", fontWeight: 900, fontSize: 36, marginTop: 12 }}>{card.caption}</div>}
        </Panel>,
      );
    case "choice": {
      const b1 = pop(f, fps, 0), b2 = pop(f, fps, 8), bub = pop(f, fps, 16);
      const btn = (t: string, c: string, rot: number, sc: number) => (
        <div style={{ transform: `scale(${0.4 + 0.6 * sc}) rotate(${rot}deg)`, background: c, borderRadius: 26, border: "6px solid #fff", padding: "26px 40px", fontFamily: UI_FONT, fontWeight: 900, fontSize: 58, color: "#14101c", boxShadow: `0 0 26px ${c}99` }}>{t}</div>
      );
      return (
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 40 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 26 }}>
            {btn(card.a, brand.colors.positive, -2, b1)}
            <span style={{ fontFamily: TITLE_FONTS[brand.fonts.title], fontSize: 48, color: "#fff" }}>ou</span>
            {btn(card.b, brand.colors.negative, 3, b2)}
          </div>
          <div style={{ transform: `scale(${bub})`, background: "#fff", borderRadius: 26, padding: "18px 36px", display: "flex", gap: 18 }}>
            {[0, 1, 2].map((i) => (
              <div key={i} style={{ width: 36, height: 36, borderRadius: "50%", background: brand.colors.primary, transform: `translateY(${Math.sin(f / 5 + i) * 5}px)` }} />
            ))}
          </div>
        </div>
      );
    }
    case "icon":
      return wrap(
        <div style={{ fontFamily: UI_FONT, fontWeight: 900, fontSize: 300, color: card.color ?? brand.colors.badge, textShadow: `0 0 40px ${card.color ?? brand.colors.badge}`, lineHeight: 1 }}>
          {card.glyph}
        </div>,
      );
    case "phone": {
      // Telephone stylise : les etapes de l'appli s'allument une par une (tap + coche).
      const every = (card.stepEvery ?? 0.6) * fps;
      const active = Math.floor(Math.max(0, f - 8) / every);
      return wrap(
        <div style={{ width: 470, height: 540, borderRadius: 54, border: `8px solid ${brand.colors.primary}`, background: "#06070d", boxShadow: `0 0 34px ${brand.colors.primary}99, 0 18px 40px rgba(0,0,0,0.6)`, padding: 18, fontFamily: UI_FONT, color: "#fff", position: "relative", overflow: "hidden" }}>
          <div style={{ width: 120, height: 14, borderRadius: 8, background: "#1b1e2b", margin: "0 auto 16px" }} />
          <div style={{ borderRadius: 22, padding: "18px 22px", background: `linear-gradient(90deg, ${brand.colors.secondary}, ${brand.colors.primary})`, fontWeight: 900, fontSize: 40, letterSpacing: 1 }}>{card.app}</div>
          <div style={{ display: "flex", flexDirection: "column", gap: 14, marginTop: 18 }}>
            {card.steps.map((st, i) => {
              const on = i <= active;
              const cur = i === active;
              const sp = pop(f, fps, 8 + i * every);
              return (
                <div key={i} style={{ display: "flex", alignItems: "center", gap: 16, padding: "16px 18px", borderRadius: 20, background: cur ? `${brand.colors.primary}33` : "#11131f", border: `4px solid ${on ? brand.colors.primary : "#2a2d3d"}`, transform: `scale(${cur ? 1 + 0.04 * sp : 1})`, opacity: on ? 1 : 0.45 }}>
                  <div style={{ width: 46, height: 46, borderRadius: "50%", background: on ? brand.colors.positive : "#2a2d3d", color: "#0b0d16", fontWeight: 900, fontSize: 28, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>{i < active ? "\u2713" : i + 1}</div>
                  <div style={{ fontWeight: 800, fontSize: 36, lineHeight: 1.1 }}>{st}</div>
                </div>
              );
            })}
          </div>
        </div>,
      );
    }
    case "creator": {
      const initials = brand.name.split(/\s+/).map((w) => w[0]).join("").slice(0, 2).toUpperCase();
      return wrap(
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 26 }}>
          <div style={{ width: 300, height: 300, borderRadius: "50%", border: `9px solid ${brand.colors.primary}`, boxShadow: `0 0 40px ${brand.colors.primary}`, overflow: "hidden", background: `linear-gradient(135deg, ${brand.colors.secondary}, ${brand.colors.primary})`, display: "flex", alignItems: "center", justifyContent: "center", fontFamily: UI_FONT, fontWeight: 900, fontSize: 120, color: "#fff" }}>
            {brand.avatar ? <Img src={staticFile(brand.avatar)} style={{ width: "100%", height: "100%", objectFit: "cover" }} /> : initials}
          </div>
          <div style={{ display: "flex", gap: 18 }}>
            {brand.tags.map((t, i) => (
              <span key={i} style={{ background: brand.colors.panel, border: `4px solid ${brand.colors.primary}`, borderRadius: 30, padding: "8px 26px", fontFamily: UI_FONT, fontWeight: 900, fontSize: 32, color: "#fff" }}>{t}</span>
            ))}
          </div>
        </div>,
      );
    }
  }
};
