import React from 'react';
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';

export const HelloReel: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const pop = spring({ frame, fps, config: { damping: 12 } });
  const fade = interpolate(frame, [0, 15], [0, 1], { extrapolateRight: 'clamp' });
  return (
    <AbsoluteFill style={{ background: '#141b33', justifyContent: 'center', alignItems: 'center' }}>
      <div style={{ opacity: fade, transform: `scale(${pop})`, color: 'white', fontFamily: 'Inter, sans-serif', fontWeight: 900, fontSize: 120 }}>
        Remotion works
      </div>
    </AbsoluteFill>
  );
};
