import React from "react";
import { AbsoluteFill, Img, staticFile } from "remotion";
import type { Brand, Thumb } from "./types";
import { INTER_FONT, OSWALD_FONT, SERIF_FONT, TITLE_FONTS, UI_FONT } from "./fonts";

// Miniature 1080x1920 : grande image du jeu en haut, accroche XXL en bas, habillage neon de la marque.
export const NeonThumb: React.FC<{ brand: Brand; thumb: Thumb }> = ({ brand, thumb }) => {
  if (thumb.style === "mission" || thumb.style === "postcard" || thumb.style === "gps") return <GameThumb brand={brand} thumb={thumb} />;
  if (thumb.style && thumb.style !== "neon") return <PremiumThumb brand={brand} thumb={thumb} />;
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

// --- Styles "premium" : photo plein cadre, typo soignee, couleur de marque en accent seulement ---------
const PremiumThumb: React.FC<{ brand: Brand; thumb: Thumb }> = ({ brand, thumb }) => {
  const c = brand.colors;
  const st = thumb.style!;
  const grad = `linear-gradient(90deg, ${c.secondary} 0%, ${c.primary} 100%)`;
  const accentText: React.CSSProperties = { background: grad, WebkitBackgroundClip: "text", backgroundClip: "text", color: "transparent" };
  const left = st !== "cinema";
  const font = st === "editorial" ? SERIF_FONT : st === "cinema" ? OSWALD_FONT : INTER_FONT;
  const weight = st === "editorial" ? 400 : st === "cinema" ? 700 : 900;
  return (
    <AbsoluteFill style={{ background: "#07070c" }}>
      {/* image sur les 2/3 du haut (une capture 16:9 en plein cadre vertical est trop zoomee) */}
      <Img src={staticFile(thumb.image)} style={{ position: "absolute", left: 0, top: 0, width: "100%", height: 1260, objectFit: "cover", objectPosition: thumb.focus ?? "50% 50%", filter: "saturate(0.95) contrast(1.05)" }} />
      {/* degrade : fondu de l'image dans le noir, le texte se lit sans halo */}
      <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(7,7,12,0.5) 0%, rgba(7,7,12,0) 16%, rgba(7,7,12,0) 40%, rgba(7,7,12,0.75) 56%, #07070c 66%)" }} />
      <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 40%, rgba(0,0,0,0) 55%, rgba(0,0,0,0.45) 100%)" }} />
      {thumb.credit && (
        <div style={{ position: "absolute", top: 70, right: 60, fontFamily: INTER_FONT, fontWeight: 500, fontSize: 22, letterSpacing: 1, color: "rgba(255,255,255,0.7)" }}>{thumb.credit}</div>
      )}
      <AbsoluteFill style={{ justifyContent: "flex-end", alignItems: left ? "flex-start" : "center", padding: "0 80px 330px" }}>
        {thumb.kicker && (
          st === "minimal" ? (
            <div style={{ display: "flex", alignItems: "center", gap: 14, padding: "12px 26px", borderRadius: 40, background: "rgba(255,255,255,0.10)", border: "1.5px solid rgba(255,255,255,0.28)", fontFamily: INTER_FONT, fontWeight: 700, fontSize: 26, letterSpacing: 4, color: "#fff", marginBottom: 34 }}>
              <span style={{ width: 12, height: 12, borderRadius: 6, background: c.secondary, boxShadow: `0 0 10px ${c.secondary}` }} />{thumb.kicker}
            </div>
          ) : st === "cinema" ? (
            <div style={{ fontFamily: INTER_FONT, fontWeight: 700, fontSize: 26, letterSpacing: 10, color: "rgba(255,255,255,0.85)", border: "1.5px solid rgba(255,255,255,0.45)", padding: "10px 28px", marginBottom: 34 }}>{thumb.kicker}</div>
          ) : (
            <div style={{ display: "flex", alignItems: "center", gap: 18, fontFamily: INTER_FONT, fontWeight: 700, fontSize: 26, letterSpacing: 9, color: "rgba(255,255,255,0.85)", marginBottom: 30 }}>
              <span style={{ width: 64, height: 3, background: grad }} />{thumb.kicker}
            </div>
          )
        )}
        {st === "cinema" && <div style={{ width: 120, height: 2, background: grad, marginBottom: 26 }} />}
        {thumb.lines.map((l, i) => {
          const accent = l.color === "primary" || l.color === "secondary";
          const italic = st === "editorial" && (thumb.italic ?? []).includes(i);
          return (
            <div key={i} style={{
              fontFamily: font, fontWeight: weight, fontStyle: italic ? "italic" : "normal", fontSize: l.size ?? 140,
              lineHeight: st === "editorial" ? 1.0 : 0.98, letterSpacing: st === "minimal" ? -4 : st === "cinema" ? 4 : 0,
              textTransform: st === "editorial" ? "none" : "uppercase", textAlign: left ? "left" : "center", whiteSpace: "nowrap",
              color: "#fff", textShadow: accent ? "none" : "0 4px 24px rgba(0,0,0,0.55)", paddingBottom: 6, ...(accent ? accentText : {}),
            }}>{l.text}</div>
          );
        })}
        {st === "cinema" && <div style={{ width: 120, height: 2, background: grad, marginTop: 30 }} />}
        <div style={{ marginTop: 34, fontFamily: INTER_FONT, fontWeight: 500, fontSize: 30, letterSpacing: 2, color: "rgba(255,255,255,0.72)" }}>@{brand.name}</div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// --- Styles "jeu video" (26/11) : meme typo premium, habillage emprunte au vocabulaire du jeu -------
// mission = HUD (minimap, etoiles, objectif) ; postcard = carte postale de Leonida ; gps = repere + notif tel.
// Elements generiques uniquement : aucun logo ni police Rockstar.
const Star: React.FC<{ on: boolean; color: string }> = ({ on, color }) => (
  <svg width="58" height="58" viewBox="0 0 24 24"><path d="M12 2l2.9 6.3 6.9.7-5.2 4.6 1.5 6.8L12 17l-6.1 3.4 1.5-6.8L2.2 9l6.9-.7z" fill={on ? color : "rgba(0,0,0,0.35)"} stroke={on ? "#000" : "rgba(255,255,255,0.85)"} strokeWidth="1.4" strokeLinejoin="round" /></svg>
);

const GameThumb: React.FC<{ brand: Brand; thumb: Thumb }> = ({ brand, thumb }) => {
  const c = brand.colors;
  const st = thumb.style!;
  const grad = `linear-gradient(90deg, ${c.secondary} 0%, ${c.primary} 100%)`;
  const accentText: React.CSSProperties = { background: grad, WebkitBackgroundClip: "text", backgroundClip: "text", color: "transparent" };
  const font = st === "postcard" ? SERIF_FONT : st === "mission" ? OSWALD_FONT : INTER_FONT;
  const weight = st === "postcard" ? 400 : st === "mission" ? 700 : 900;
  const center = st === "mission";
  const imgH = st === "postcard" ? 0 : 1260;
  const lines = thumb.lines.map((l, i) => {
    const accent = l.color === "primary" || l.color === "secondary";
    const italic = st === "postcard" && (thumb.italic ?? []).includes(i);
    return (
      <div key={i} style={{
        fontFamily: font, fontWeight: weight, fontStyle: italic ? "italic" : "normal", fontSize: l.size ?? 140,
        lineHeight: st === "postcard" ? 1.0 : 0.98, letterSpacing: st === "gps" ? -4 : st === "mission" ? 3 : 0,
        textTransform: st === "postcard" ? "none" : "uppercase", textAlign: center ? "center" : "left", whiteSpace: "nowrap",
        color: "#fff", textShadow: accent ? "none" : "0 4px 24px rgba(0,0,0,0.6)", paddingBottom: 6, ...(accent ? accentText : {}),
      }}>{l.text}</div>
    );
  });
  const handle = <div style={{ marginTop: 30, fontFamily: INTER_FONT, fontWeight: 500, fontSize: 30, letterSpacing: 2, color: "rgba(255,255,255,0.72)" }}>@{brand.name}</div>;
  const credit = thumb.credit && (
    <div style={{ position: "absolute", top: st === "gps" ? 300 : 70, right: 60, fontFamily: INTER_FONT, fontWeight: 500, fontSize: 22, letterSpacing: 1, color: "rgba(255,255,255,0.7)", textShadow: "0 1px 4px #000" }}>{thumb.credit}</div>
  );
  const obj = (thumb.objective ?? "").split("*").map((p, i) => <span key={i} style={{ color: i % 2 ? c.badge : "#fff" }}>{p}</span>);

  if (st === "postcard") {
    return (
      <AbsoluteFill style={{ background: `radial-gradient(ellipse at 50% 0%, ${c.secondary}55 0%, rgba(0,0,0,0) 60%), linear-gradient(180deg, #120b24 0%, #07070c 70%)` }}>
        {/* tirage photo a bord blanc, legerement penche */}
        <div style={{ position: "absolute", left: 70, top: 140, width: 940, height: 850, background: "#f4f1ea", padding: 26, paddingBottom: 90, transform: "rotate(-3deg)", boxShadow: "0 30px 60px rgba(0,0,0,0.6)" }}>
          <Img src={staticFile(thumb.image)} style={{ width: "100%", height: "100%", objectFit: "cover", objectPosition: thumb.focus ?? "50% 50%", filter: "saturate(1.05) contrast(1.05)" }} />
          <div style={{ position: "absolute", left: 30, bottom: 22, fontFamily: SERIF_FONT, fontStyle: "italic", fontSize: 44, color: "#1b1530" }}>{thumb.kicker ?? "Souvenir de Leonida"}</div>
          {thumb.credit && <div style={{ position: "absolute", right: 30, bottom: 32, fontFamily: INTER_FONT, fontWeight: 500, fontSize: 20, color: "rgba(27,21,48,0.6)" }}>{thumb.credit}</div>}
        </div>
        {/* timbre + tampon */}
        <div style={{ position: "absolute", right: 70, top: 100, width: 190, height: 230, background: "#f4f1ea", padding: 10, transform: "rotate(6deg)", boxShadow: "0 10px 24px rgba(0,0,0,0.5)", outline: "6px dotted #f4f1ea", outlineOffset: 2 }}>
          <div style={{ width: "100%", height: "100%", background: grad, display: "flex", flexDirection: "column", justifyContent: "space-between", padding: 14, boxSizing: "border-box" }}>
            <div style={{ fontFamily: INTER_FONT, fontWeight: 800, fontSize: 22, letterSpacing: 3, color: "#fff" }}>{thumb.stamp ?? "LEONIDA"}</div>
            <svg viewBox="0 0 100 70" width="140"><circle cx="50" cy="52" r="26" fill="#fff" opacity="0.9" />{[0, 1, 2].map((k) => <rect key={k} x="0" y={44 + k * 8} width="100" height="3" fill={c.secondary} />)}</svg>
            <div style={{ fontFamily: SERIF_FONT, fontSize: 40, color: "#fff", textAlign: "right" }}>$1</div>
          </div>
        </div>
        <svg width="200" height="200" viewBox="0 0 100 100" style={{ position: "absolute", right: 40, top: 300, opacity: 0.5, transform: "rotate(-14deg)" }}>
          <circle cx="50" cy="50" r="44" fill="none" stroke="#fff" strokeWidth="2.5" /><circle cx="50" cy="50" r="34" fill="none" stroke="#fff" strokeWidth="1.5" />
          <text x="50" y="47" textAnchor="middle" fontFamily={INTER_FONT} fontWeight="800" fontSize="11" fill="#fff" letterSpacing="1">VICE CITY</text>
          <text x="50" y="62" textAnchor="middle" fontFamily={INTER_FONT} fontWeight="600" fontSize="8" fill="#fff">GTA 6</text>
        </svg>
        <AbsoluteFill style={{ justifyContent: "flex-end", alignItems: "flex-start", padding: "0 80px 330px" }}>{lines}{handle}</AbsoluteFill>
      </AbsoluteFill>
    );
  }

  return (
    <AbsoluteFill style={{ background: "#07070c" }}>
      <Img src={staticFile(thumb.image)} style={{ position: "absolute", left: 0, top: 0, width: "100%", height: imgH, objectFit: "cover", objectPosition: thumb.focus ?? "50% 50%", filter: "saturate(0.95) contrast(1.05)" }} />
      <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(7,7,12,0.55) 0%, rgba(7,7,12,0) 18%, rgba(7,7,12,0) 42%, rgba(7,7,12,0.75) 57%, #07070c 66%)" }} />
      {credit}

      {st === "mission" && (<>
        {/* etoiles de recherche, en haut a droite comme dans un HUD */}
        <div style={{ position: "absolute", top: 120, right: 50, display: "flex", gap: 4, filter: "drop-shadow(0 2px 4px rgba(0,0,0,.7))" }}>{[0, 1, 2, 3, 4].map((k) => <Star key={k} on={k < 3} color={c.badge} />)}</div>
        {/* minimap ronde, en bas a gauche de l'image */}
        <div style={{ position: "absolute", left: 50, top: 560, width: 230, height: 230, borderRadius: 115, overflow: "hidden", border: "6px solid rgba(0,0,0,0.75)", boxShadow: "0 0 0 2px rgba(255,255,255,0.35), 0 10px 30px rgba(0,0,0,.6)", background: "#1a2230" }}>
          <svg viewBox="0 0 100 100" width="230" height="230">
            <rect width="100" height="100" fill="#22304a" /><path d="M-5 70 Q30 55 55 62 T110 40" stroke="#3b4d6e" strokeWidth="9" fill="none" />
            <path d="M40 -5 L46 110" stroke="#56657f" strokeWidth="5" /><path d="M-5 30 L110 36" stroke="#56657f" strokeWidth="4" /><path d="M70 -5 L62 110" stroke="#56657f" strokeWidth="3" />
            <path d="M43 50 L64 30" stroke={c.secondary} strokeWidth="3.5" strokeDasharray="3 2" />
            <circle cx="66" cy="28" r="9" fill={c.secondary} stroke="#fff" strokeWidth="2" /><text x="66" y="32" textAnchor="middle" fontFamily={INTER_FONT} fontWeight="900" fontSize="12" fill="#fff">?</text>
            <path d="M43 44 L48 55 L43 52 L38 55 Z" fill="#fff" />
          </svg>
        </div>
      </>)}

      {st === "gps" && thumb.pin && (<>
        <svg width="1080" height="1260" style={{ position: "absolute", left: 0, top: 0 }}>
          <path d={`M 250 1010 C 300 880, ${thumb.pin.x - 220} ${thumb.pin.y + 420}, ${thumb.pin.x} ${thumb.pin.y + 150}`} stroke={c.secondary} strokeWidth="14" fill="none" strokeLinecap="round" strokeDasharray="2 26" opacity="0.95" />
        </svg>
        <div style={{ position: "absolute", left: thumb.pin.x - 55, top: thumb.pin.y + 10, width: 110, height: 140, filter: "drop-shadow(0 8px 14px rgba(0,0,0,.6))" }}>
          <svg viewBox="0 0 40 52" width="110" height="140"><path d="M20 51 C20 51 3 31 3 19 A17 17 0 0 1 37 19 C37 31 20 51 20 51 Z" fill={c.secondary} stroke="#fff" strokeWidth="2.5" /><text x="20" y="26" textAnchor="middle" fontFamily={INTER_FONT} fontWeight="900" fontSize="18" fill="#fff">?</text></svg>
        </div>
        {thumb.pin.label && (
          <div style={{ position: "absolute", left: thumb.pin.x + 70, top: thumb.pin.y + 40, padding: "10px 20px", borderRadius: 14, background: "rgba(10,10,18,0.85)", border: "1.5px solid rgba(255,255,255,0.25)", fontFamily: INTER_FONT, fontWeight: 700, fontSize: 28, color: "#fff", whiteSpace: "nowrap" }}>{thumb.pin.label}</div>
        )}
      </>)}
      {st === "gps" && thumb.notif && (
        <div style={{ position: "absolute", top: 120, left: 60, right: 60, display: "flex", gap: 22, alignItems: "center", padding: "22px 28px", borderRadius: 34, background: "rgba(20,20,30,0.72)", border: "1.5px solid rgba(255,255,255,0.18)", boxShadow: "0 16px 40px rgba(0,0,0,0.5)" }}>
          <div style={{ width: 76, height: 76, borderRadius: 18, background: grad, flexShrink: 0 }} />
          <div style={{ fontFamily: INTER_FONT, color: "#fff" }}>
            <div style={{ fontWeight: 700, fontSize: 24, opacity: 0.7, letterSpacing: 1 }}>{thumb.notif.app.toUpperCase()} · maintenant</div>
            <div style={{ fontWeight: 700, fontSize: 36, marginTop: 4 }}>{thumb.notif.text}</div>
          </div>
        </div>
      )}

      <AbsoluteFill style={{ justifyContent: "flex-end", alignItems: center ? "center" : "flex-start", padding: "0 80px 330px" }}>
        {st === "mission" && thumb.kicker && (
          <div style={{ display: "flex", alignItems: "center", gap: 20, fontFamily: INTER_FONT, fontWeight: 700, fontSize: 26, letterSpacing: 10, color: "rgba(255,255,255,0.85)", marginBottom: 26 }}>
            <span style={{ width: 70, height: 2, background: grad }} />{thumb.kicker}<span style={{ width: 70, height: 2, background: grad }} />
          </div>
        )}
        {st === "gps" && thumb.kicker && (
          <div style={{ fontFamily: INTER_FONT, fontWeight: 700, fontSize: 26, letterSpacing: 6, color: "rgba(255,255,255,0.8)", marginBottom: 26 }}>{thumb.kicker}</div>
        )}
        {lines}
        {st === "mission" && thumb.objective && (
          <div style={{ marginTop: 30, padding: "12px 26px", background: "rgba(0,0,0,0.55)", fontFamily: INTER_FONT, fontWeight: 700, fontSize: 34, color: "#fff" }}>{obj}</div>
        )}
        {handle}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
