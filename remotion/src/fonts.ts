import { loadFont } from "@remotion/fonts";
import { staticFile } from "remotion";

export const FONT_FAMILY = "InterShorts";

export const fontPromise = Promise.all([
  loadFont({
    family: FONT_FAMILY,
    url: staticFile("fonts/Inter-ExtraBold.otf"),
    weight: "800",
  }),
  loadFont({
    family: FONT_FAMILY,
    url: staticFile("fonts/Inter-Bold.otf"),
    weight: "700",
  }),
]);
