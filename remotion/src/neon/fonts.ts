import { loadFont } from "@remotion/fonts";
import { staticFile } from "remotion";

export const TITLE_FONTS = {
  kaushan: "NeonKaushan",
  pacifico: "NeonPacifico",
  bebas: "NeonBebas",
} as const;
export const UI_FONT = "NeonMontserrat";

export const neonFontsReady = Promise.all([
  loadFont({ family: TITLE_FONTS.kaushan, url: staticFile("neon/fonts/kaushan-script-latin-400-normal.woff2") }),
  loadFont({ family: TITLE_FONTS.pacifico, url: staticFile("neon/fonts/pacifico-latin-400-normal.woff2") }),
  loadFont({ family: TITLE_FONTS.bebas, url: staticFile("neon/fonts/bebas-neue-latin-400-normal.woff2") }),
  loadFont({ family: UI_FONT, url: staticFile("neon/fonts/montserrat-latin-700-normal.woff2"), weight: "700" }),
  loadFont({ family: UI_FONT, url: staticFile("neon/fonts/montserrat-latin-800-normal.woff2"), weight: "800" }),
  loadFont({ family: UI_FONT, url: staticFile("neon/fonts/montserrat-latin-900-normal.woff2"), weight: "900" }),
]);
