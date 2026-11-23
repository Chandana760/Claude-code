import fs from 'node:fs';
import { Config } from '@remotion/cli/config';

Config.setVideoImageFormat('jpeg');

// In the Claude cloud container Remotion can't download its browser, so use the pre-installed one.
// On your own computer this path doesn't exist and Remotion uses its normal browser.
const local = process.env.REMOTION_CHROMIUM
  ?? '/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell';
if (fs.existsSync(local)) Config.setBrowserExecutable(local);
