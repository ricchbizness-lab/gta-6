import React, { useCallback, useEffect, useMemo, useState } from "react";
import {
  AbsoluteFill,
  Sequence,
  continueRender,
  delayRender,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import {
  createTikTokStyleCaptions,
  type Caption,
  type TikTokPage,
} from "@remotion/captions";
import { COLORS, TEXT_SHADOW } from "./theme";
import { FONT_FAMILY } from "./fonts";

// Les ruptures de page sont déjà posées (pageBreakAfter) par
// build_montage_data.py, aux respirations. Cette valeur n'est qu'un filet
// de sécurité pour une page anormalement longue.
const SWITCH_EVERY_MS = 2500;
// Laisse la page à l'écran un court instant après le dernier mot.
const PAGE_TAIL_MS = 220;

const Page: React.FC<{ page: TikTokPage; bottom: number }> = ({
  page,
  bottom,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const absoluteMs = page.startMs + (frame / fps) * 1000;

  return (
    <AbsoluteFill
      style={{
        justifyContent: "flex-end",
        alignItems: "center",
        paddingBottom: bottom,
        paddingLeft: 70,
        paddingRight: 70,
      }}
    >
      <div
        style={{
          width: "100%",
          maxWidth: 900,
          margin: "0 auto",
          fontFamily: FONT_FAMILY,
          fontWeight: 800,
          fontSize: 70,
          lineHeight: 1.14,
          textAlign: "center",
          whiteSpace: "pre-wrap",
          textShadow: TEXT_SHADOW,
          WebkitTextStroke: "3.5px rgba(0,0,0,0.88)",
          textTransform: "uppercase",
          letterSpacing: -1,
        }}
      >
        {page.tokens.map((token, i) => {
          const isActive =
            token.fromMs <= absoluteMs && token.toMs > absoluteMs;
          return (
            <span
              key={`${token.fromMs}-${i}`}
              style={{
                color: isActive ? COLORS.active : COLORS.text,
                display: "inline",
              }}
            >
              {token.text}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

export const Captions: React.FC<{ src: string; bottom: number }> = ({
  src,
  bottom,
}) => {
  const { fps } = useVideoConfig();
  const [captions, setCaptions] = useState<Caption[] | null>(null);
  const [handle] = useState(() => delayRender(`captions ${src}`));

  const fetchCaptions = useCallback(async () => {
    const res = await fetch(staticFile(src));
    setCaptions((await res.json()) as Caption[]);
    continueRender(handle);
  }, [handle, src]);

  useEffect(() => {
    fetchCaptions();
  }, [fetchCaptions]);

  const pages = useMemo(() => {
    if (!captions) return [];
    return createTikTokStyleCaptions({
      captions,
      combineTokensWithinMilliseconds: SWITCH_EVERY_MS,
    }).pages;
  }, [captions]);

  if (!captions) return null;

  return (
    <AbsoluteFill>
      {pages.map((page, index) => {
        const next = pages[index + 1] ?? null;
        const startFrame = (page.startMs / 1000) * fps;
        const lastTokenEndMs = page.tokens.length
          ? page.tokens[page.tokens.length - 1].toMs
          : page.startMs;
        const endFrame = Math.min(
          next ? (next.startMs / 1000) * fps : Infinity,
          ((lastTokenEndMs + PAGE_TAIL_MS) / 1000) * fps,
          startFrame + (SWITCH_EVERY_MS / 1000) * fps,
        );
        const durationInFrames = endFrame - startFrame;
        if (durationInFrames <= 0) return null;

        return (
          <Sequence
            key={index}
            from={Math.round(startFrame)}
            durationInFrames={Math.ceil(durationInFrames)}
          >
            <Page page={page} bottom={bottom} />
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
