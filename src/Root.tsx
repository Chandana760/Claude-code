import React from 'react';
import { Composition, Still } from 'remotion';
import { HelloReel } from './HelloReel';
import { FirstReel, FirstReelCover, FIRST_REEL_FPS, FIRST_REEL_FRAMES } from './first-reel/FirstReel';

// All reels are 9:16 vertical (1080x1920)
export const RemotionRoot: React.FC = () => (
  <>
    <Composition id="FirstReel" component={FirstReel} durationInFrames={FIRST_REEL_FRAMES} fps={FIRST_REEL_FPS} width={1080} height={1920} />
    <Still id="FirstReelCover" component={FirstReelCover} width={1080} height={1920} />
    <Composition id="HelloReel" component={HelloReel} durationInFrames={90} fps={30} width={1080} height={1920} />
  </>
);
