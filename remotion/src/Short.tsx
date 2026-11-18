import React from "react";
import {
  AbsoluteFill,
  Easing,
  OffthreadVideo,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { Captions } from "./Captions";
import { COLORS, SAFE_TOP, TEXT_SHADOW } from "./theme";
import { FONT_FAMILY } from "./fonts";

export type ShortProps = {
  id: string;
  src: string;
  captions: string;
  hook: string;
  cta: string;
  punches: number[];
  ctaStart: number;
  durationInSeconds: number;
};

const HOOK_DURATION = 2.6; // s : le hook doit être lu avant 2 s
const PUNCH_RISE = 0.18;
const PUNCH_HOLD = 1.9;
const PUNCH_FALL = 0.55;
const PUNCH_AMOUNT = 0.1;

/** Enveloppe 0..1 d'un punch-in : montée rapide, tenue, retour doux. */
const punchEnvelope = (t: number, punch: number): number => {
  const d = t - punch;
  if (d < 0) return 0;
  if (d < PUNCH_RISE) {
    return interpolate(d, [0, PUNCH_RISE], [0, 1], {
      easing: Easing.out(Easing.cubic),
    });
  }
  if (d < PUNCH_RISE + PUNCH_HOLD) return 1;
  const fallEnd = PUNCH_RISE + PUNCH_HOLD + PUNCH_FALL;
  if (d < fallEnd) {
    return interpolate(d, [PUNCH_RISE + PUNCH_HOLD, fallEnd], [1, 0], {
      easing: Easing.inOut(Easing.cubic),
    });
  }
  return 0;
};

/** Secousse courte à l'impact, amortie sur 0,28 s. */
const shakeAt = (t: number, punches: number[]): { x: number; y: number } => {
  let x = 0;
  let y = 0;
  for (const p of punches) {
    const d = t - p;
    if (d >= 0 && d < 0.28) {
      const decay = 1 - d / 0.28;
      x += Math.sin(d * 78) * 7 * decay;
      y += Math.cos(d * 61) * 5 * decay;
    }
  }
  return { x, y };
};

export const Short: React.FC<ShortProps> = ({
  src,
  captions,
  hook,
  cta,
  punches,
  ctaStart,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;

  const env = punches.reduce((acc, p) => Math.max(acc, punchEnvelope(t, p)), 0);
  const scale = 1 + PUNCH_AMOUNT * env;
  const { x: shakeX, y: shakeY } = shakeAt(t, punches);

  // Hook : entre en 0,25 s, sort à HOOK_DURATION
  const hookIn = interpolate(t, [0, 0.25], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  const hookOut = interpolate(
    t,
    [HOOK_DURATION - 0.3, HOOK_DURATION],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );
  const hookOpacity = hookIn * hookOut;
  const hookY = interpolate(hookIn, [0, 1], [-40, 0]);

  // CTA : apparaît sur les dernières secondes
  const ctaIn = interpolate(t, [ctaStart, ctaStart + 0.35], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  const ctaVisible = ctaIn > 0.01;

  // Pendant le CTA, les sous-titres remontent pour ne pas se chevaucher
  const captionBottom = ctaVisible ? 560 : 380;

  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      {/* Gameplay : recadrage 9:16 plein cadre (object-fit cover) */}
      <AbsoluteFill style={{ overflow: "hidden" }}>
        <OffthreadVideo
          src={staticFile(src)}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
            transform: `scale(${scale}) translate(${shakeX}px, ${shakeY}px)`,
            filter: "saturate(1.09) contrast(1.05) brightness(1.01)",
          }}
          // Le son du jeu est la bande-son : pas de musique ajoutée
          volume={1}
        />
      </AbsoluteFill>

      {/* Vignettage léger : fait ressortir le texte */}
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(ellipse at 50% 45%, rgba(0,0,0,0) 52%, rgba(0,0,0,0.38) 100%)",
          pointerEvents: "none",
        }}
      />

      {/* Voiles dégradés : le texte reste lisible même sur un fond blanc pur
          (flash de la cinématique de mort) ou sur du sable surexposé. */}
      <AbsoluteFill
        style={{
          background:
            "linear-gradient(to bottom, rgba(0,0,0,0.55) 0%, rgba(0,0,0,0.18) 13%, rgba(0,0,0,0) 26%)",
          pointerEvents: "none",
        }}
      />
      <AbsoluteFill
        style={{
          background:
            "linear-gradient(to top, rgba(0,0,0,0.68) 0%, rgba(0,0,0,0.42) 12%, rgba(0,0,0,0.12) 24%, rgba(0,0,0,0) 38%)",
          pointerEvents: "none",
        }}
      />

      {/* Hook */}
      {hookOpacity > 0.01 ? (
        <AbsoluteFill
          style={{
            justifyContent: "flex-start",
            alignItems: "center",
            paddingTop: SAFE_TOP + 80,
            paddingLeft: 60,
            paddingRight: 60,
            opacity: hookOpacity,
            transform: `translateY(${hookY}px)`,
          }}
        >
          <div
            style={{
              width: "100%",
              maxWidth: 920,
              margin: "0 auto",
              fontFamily: FONT_FAMILY,
              fontWeight: 800,
              fontSize: 84,
              lineHeight: 1.08,
              color: COLORS.text,
              textAlign: "center",
              textTransform: "uppercase",
              letterSpacing: -2,
              textShadow: TEXT_SHADOW,
              WebkitTextStroke: "4px rgba(0,0,0,0.85)",
            }}
          >
            {hook}
          </div>
        </AbsoluteFill>
      ) : null}

      {/* Sous-titres mot par mot */}
      <Captions src={captions} bottom={captionBottom} />

      {/* CTA de fin */}
      {ctaVisible ? (
        <AbsoluteFill
          style={{
            justifyContent: "flex-end",
            alignItems: "center",
            paddingBottom: 340,
            opacity: ctaIn,
            transform: `translateY(${interpolate(ctaIn, [0, 1], [50, 0])}px)`,
          }}
        >
          <div
            style={{
              backgroundColor: COLORS.ctaBg,
              borderRadius: 28,
              padding: "24px 38px",
              maxWidth: 940,
              borderBottom: `8px solid ${COLORS.accent}`,
            }}
          >
            <div
              style={{
                fontFamily: FONT_FAMILY,
                fontWeight: 800,
                fontSize: 46,
                color: COLORS.text,
                textAlign: "center",
                textTransform: "uppercase",
                letterSpacing: -1,
              }}
            >
              {cta}
            </div>
          </div>
        </AbsoluteFill>
      ) : null}
    </AbsoluteFill>
  );
};
