import { loadFont } from "@remotion/fonts";
import { staticFile } from "remotion";

export const TITLE_FONTS = {
  kaushan: "NeonKaushan",
  pacifico: "NeonPacifico",
  bebas: "NeonBebas",
} as const;
export const UI_FONT = "NeonMontserrat";
// Polices "premium" (miniatures)
export const SERIF_FONT = "NeonSerif";
export const INTER_FONT = "NeonInter";
export const OSWALD_FONT = "NeonOswald";

export const neonFontsReady = Promise.all([
  loadFont({ family: TITLE_FONTS.kaushan, url: staticFile("neon/fonts/kaushan-script-latin-400-normal.woff2") }),
  loadFont({ family: TITLE_FONTS.pacifico, url: staticFile("neon/fonts/pacifico-latin-400-normal.woff2") }),
  loadFont({ family: TITLE_FONTS.bebas, url: staticFile("neon/fonts/bebas-neue-latin-400-normal.woff2") }),
  loadFont({ family: UI_FONT, url: staticFile("neon/fonts/montserrat-latin-700-normal.woff2"), weight: "700" }),
  loadFont({ family: UI_FONT, url: staticFile("neon/fonts/montserrat-latin-800-normal.woff2"), weight: "800" }),
  loadFont({ family: UI_FONT, url: staticFile("neon/fonts/montserrat-latin-900-normal.woff2"), weight: "900" }),
  loadFont({ family: SERIF_FONT, url: staticFile("neon/fonts/dm-serif-display-latin-400-normal.woff2") }),
  loadFont({ family: SERIF_FONT, url: staticFile("neon/fonts/dm-serif-display-latin-400-italic.woff2"), style: "italic" }),
  ...["500", "700", "800", "900"].map((w) => loadFont({ family: INTER_FONT, url: staticFile(`neon/fonts/inter-latin-${w}-normal.woff2`), weight: w })),
  ...["500", "600", "700"].map((w) => loadFont({ family: OSWALD_FONT, url: staticFile(`neon/fonts/oswald-latin-${w}-normal.woff2`), weight: w })),
]);
