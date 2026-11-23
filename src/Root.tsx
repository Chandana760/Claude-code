import React from 'react';
import { Composition } from 'remotion';
import { HelloReel } from './HelloReel';

// 9:16 vertical reel, 30 fps
export const RemotionRoot: React.FC = () => (
  <Composition id="HelloReel" component={HelloReel} durationInFrames={90} fps={30} width={1080} height={1920} />
);
