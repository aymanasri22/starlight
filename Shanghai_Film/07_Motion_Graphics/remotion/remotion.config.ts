import { Config } from "@remotion/cli/config";

// Use the container's pre-installed Chromium headless shell (no download).
// On another machine, delete this line and Remotion fetches its own browser.
const HEADLESS = "/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell";
Config.setBrowserExecutable(process.env.REMOTION_BROWSER ?? HEADLESS);
Config.setConcurrency(4);
Config.setVideoImageFormat("png");
