import React from "react";
import { Composition } from "remotion";
import { Short, type ShortProps } from "./Short";
import { FPS, HEIGHT, WIDTH } from "./theme";
import { fontPromise } from "./fonts";
import meta from "../public/clips-meta.json";
import kaiMeta from "../public/kai-meta.json";

type ClipMeta = {
  id: string;
  src: string;
  captions: string;
  durationInSeconds: number;
  hook: string;
  cta: string;
  punches: number[];
  ctaStart: number;
  layout?: "fullbleed" | "stacked";
};

const clips = [...(meta as ClipMeta[]), ...(kaiMeta as ClipMeta[])];

export const RemotionRoot: React.FC = () => {
  return (
    <>
      {clips.map((clip) => (
        <Composition
          key={clip.id}
          id={clip.id}
          component={Short}
          width={WIDTH}
          height={HEIGHT}
          fps={FPS}
          durationInFrames={Math.floor(clip.durationInSeconds * FPS)}
          defaultProps={clip satisfies ShortProps}
          calculateMetadata={async () => {
            // Garantit que la police est chargée avant le premier rendu
            await fontPromise;
            return {};
          }}
        />
      ))}
    </>
  );
};
