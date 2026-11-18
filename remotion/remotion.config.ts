/**
 * Note: When using the Node.JS APIs, the config file
 * doesn't apply. Instead, pass options directly to the APIs.
 *
 * All configuration options: https://remotion.dev/docs/config
 */

import { Config } from "@remotion/cli/config";

Config.setRspack(true);
Config.setVideoImageFormat("jpeg");
Config.setOverwriteOutput(true);
Config.setDefaultPremountInSeconds(2);

// Chromium déjà présent dans l'image : évite le téléchargement de Remotion
Config.setBrowserExecutable("/opt/pw-browsers/chromium_headless_shell");
Config.setChromiumOpenGlRenderer("swangle");
Config.setConcurrency(2);
Config.setCrf(20);
Config.setCodec("h264");
