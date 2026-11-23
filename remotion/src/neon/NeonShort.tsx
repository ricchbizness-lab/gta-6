import React, { useEffect, useMemo, useState } from "react";
import {
  AbsoluteFill, Audio, OffthreadVideo, Sequence, continueRender, delayRender, interpolate,
  staticFile, useCurrentFrame, useVideoConfig,
} from "remotion";
import { createTikTokStyleCaptions, type Caption, type TikTokPage } from "@remotion/captions";
import type { Brand, NeonProps, Scene } from "./types";
import { CardView } from "./Cards";
import { pop } from "./anim";
import { TITLE_FONTS, UI_FONT } from "./fonts";

// --- Grille synthwave en perspective, defilement continu ---------------------------
const SynthGrid: React.FC<{ color: string }> = ({ color }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const H = 380, W = 1080, vx = 540;
  const phase = ((frame / fps) * 0.9) % 1;
  const rows = Array.from({ length: 10 }, (_, i) => {
    const t = (i + phase) / 10;
    return H * t * t; // espacement croissant vers le spectateur
  });
  const cols = Array.from({ length: 23 }, (_, i) => (i - 11) * 160);
  return (
    <svg width={W} height={H} style={{ position: "absolute", bottom: 0, left: 0, opacity: 0.85 }}>
      <defs>
        <linearGradient id="gfade" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#000" stopOpacity="1" />
          <stop offset="0.35" stopColor="#000" stopOpacity="0" />
        </linearGradient>
      </defs>
      <g stroke={color} strokeWidth="2.5" style={{ filter: `drop-shadow(0 0 6px ${color})` }}>
        {rows.map((y, i) => <line key={`r${i}`} x1="0" x2={W} y1={y} y2={y} />)}
        {cols.map((dx, i) => <line key={`c${i}`} x1={vx} y1={0} x2={vx + dx * 4} y2={H} />)}
      </g>
      <rect width={W} height={H} fill="url(#gfade)" />
    </svg>
  );
};

// --- Pastille de chapitre ------------------------------------------------------------
const ChapterPill: React.FC<{ brand: Brand; n: number }> = ({ brand, n }) => (
  <div style={{ display: "flex", alignItems: "center", gap: 18, background: "rgba(14,11,20,0.92)", border: `5px solid ${brand.colors.primary}`, borderRadius: 60, padding: "10px 46px 10px 12px", boxShadow: `0 0 22px ${brand.colors.primary}88` }}>
    <div style={{ width: 74, height: 74, borderRadius: "50%", background: brand.colors.badge, display: "flex", alignItems: "center", justifyContent: "center", fontFamily: UI_FONT, fontWeight: 900, fontSize: 46, color: "#14101c" }}>{n}</div>
    <div style={{ fontFamily: UI_FONT, fontWeight: 900, fontSize: 46, color: "#fff", letterSpacing: 1 }}>{brand.chapterLabel} {n}</div>
  </div>
);

// --- Titre neon, ecrit lettre par lettre ---------------------------------------------
const NeonTitle: React.FC<{ brand: Brand; text: string; localFrame: number }> = ({ brand, text, localFrame }) => {
  const { fps } = useVideoConfig();
  const n = Math.ceil(interpolate(localFrame, [0, 0.35 * fps], [0, text.length], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }));
  const c = brand.colors.primary;
  const big = brand.fonts.title === "bebas";
  return (
    <div style={{ fontFamily: TITLE_FONTS[brand.fonts.title], fontSize: big ? 150 : 118, lineHeight: 1.08, color: "#fff", textAlign: "center", maxWidth: 940, whiteSpace: "pre-wrap", WebkitTextStroke: `3px ${c}`, textShadow: `0 0 8px ${c}, 0 0 22px ${c}, 0 0 44px ${c}aa, 0 6px 0 rgba(0,0,0,0.35)` }}>
      {text.slice(0, n)}
    </div>
  );
};

// --- Sous-titres : 1 a 3 mots, le mot prononce s'allume -------------------------------
const NeonCaptions: React.FC<{ src: string }> = ({ src }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const [caps, setCaps] = useState<Caption[] | null>(null);
  const [h] = useState(() => delayRender("neon captions"));
  useEffect(() => {
    fetch(staticFile(src)).then((r) => r.json()).then((d) => { setCaps(d); continueRender(h); });
  }, [h, src]);
  const pages: TikTokPage[] = useMemo(() => (caps ? createTikTokStyleCaptions({ captions: caps, combineTokensWithinMilliseconds: 2500 }).pages : []), [caps]);
  if (!caps) return null;
  const ms = (frame / fps) * 1000;
  const page = pages.filter((p) => p.startMs <= ms).pop();
  if (!page) return null;
  const last = page.tokens[page.tokens.length - 1];
  if (ms > last.toMs + 250) return null;
  return (
    <AbsoluteFill style={{ justifyContent: "flex-end", alignItems: "center", paddingBottom: 430 }}>
      <div style={{ fontFamily: UI_FONT, fontWeight: 800, fontSize: 68, color: "#fff", whiteSpace: "pre", textShadow: "0 4px 14px rgba(0,0,0,0.8), 0 0 2px #000" }}>
        {page.tokens.map((t, i) => (
          <span key={i} style={{ opacity: t.fromMs <= ms ? 1 : 0.35 }}>{t.text}</span>
        ))}
      </div>
    </AbsoluteFill>
  );
};

// --- Scene : pastille + titre + carte --------------------------------------------------
const SceneView: React.FC<{ brand: Brand; scene: Scene }> = ({ brand, scene }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const total = (scene.end - scene.start) * fps;
  const out = interpolate(frame, [total - 3, total], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ opacity: out }}>
      {scene.title && (
        <AbsoluteFill style={{ alignItems: "center", paddingTop: 470 }}>
          <NeonTitle brand={brand} text={scene.title} localFrame={frame} />
        </AbsoluteFill>
      )}
      {scene.card && (
        <AbsoluteFill style={{ alignItems: "center", justifyContent: "flex-start", paddingTop: scene.card.type === "badge" ? 760 : 820 }}>
          <CardView brand={brand} card={scene.card} localFrame={frame} />
        </AbsoluteFill>
      )}
    </AbsoluteFill>
  );
};

// --- Flash de transition (3 images : blanc puis couleur) --------------------------------
const Flash: React.FC<{ color: string }> = ({ color }) => {
  const frame = useCurrentFrame();
  const c = frame < 1 ? "#ffffff" : color;
  const o = interpolate(frame, [0, 4], [1, 0], { extrapolateRight: "clamp" });
  return <AbsoluteFill style={{ background: c, opacity: o }} />;
};

export const NeonShort: React.FC<NeonProps> = ({ brand, scenes, backgrounds, voice, captions, music, musicVolume = 0.18, sfx }) => {
  const { fps } = useVideoConfig();
  const frame = useCurrentFrame();
  const t = frame / fps;
  const cur = scenes.find((s) => s.start <= t && t < s.end) ?? scenes[scenes.length - 1];
  const chap = cur?.chapter ?? 0;
  const pillPop = pop(frame - Math.round((scenes.find((s) => s.chapter === chap)?.start ?? 0) * fps), fps);
  const F = (s: number) => Math.round(s * fps);
  return (
    <AbsoluteFill style={{ background: "#0b0910" }}>
      {backgrounds.map((b, i) => (
        <Sequence key={i} from={F(b.from)} durationInFrames={Math.max(1, F(b.to - b.from))}>
          <OffthreadVideo src={staticFile(b.src)} muted style={{ width: "100%", height: "100%", objectFit: "cover" }} />
        </Sequence>
      ))}
      <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 40%, rgba(10,8,16,0.25), rgba(10,8,16,0.7))" }} />
      <SynthGrid color={brand.colors.grid} />

      {chap > 0 && (
        <AbsoluteFill style={{ alignItems: "center", paddingTop: 190 }}>
          <div style={{ transform: `scale(${0.6 + 0.4 * pillPop})` }}><ChapterPill brand={brand} n={chap} /></div>
        </AbsoluteFill>
      )}

      {scenes.map((s, i) => (
        <Sequence key={i} from={F(s.start)} durationInFrames={Math.max(1, F(s.end - s.start))}>
          <SceneView brand={brand} scene={s} />
          {sfx && s.card && <Audio src={staticFile(s.card.type === "badge" ? "neon/sfx/impact.wav" : "neon/sfx/pop.wav")} volume={s.card.type === "badge" ? 0.9 : 0.45} />}
          {s.flash && (
            <Sequence durationInFrames={5}>
              <Flash color={brand.colors.primary} />
              {sfx && <Audio src={staticFile("neon/sfx/whoosh.wav")} volume={0.6} />}
            </Sequence>
          )}
        </Sequence>
      ))}

      <NeonCaptions src={captions} />
      <Audio src={staticFile(voice)} />
      {music && <Audio src={staticFile(music)} volume={musicVolume} loop />}
    </AbsoluteFill>
  );
};
