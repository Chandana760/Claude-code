import React from 'react';
import { AbsoluteFill, Audio, Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from 'remotion';
import EP from './lines.json';
import PLATES from './plates.json';

// Blender + Remotion: Blender renders the 3D desk set per camera as two layers (room behind / desk in front),
// and exports where the characters stand on screen. Remotion stacks: room -> Maya (sheet cut-out) -> desk -> Claude,
// and does the acting, lip flap, captions and audio from lines.json.

type Line = { t: number; d: number; who: 'M' | 'C'; text: string; shot: 'maya' | 'claude' | 'wide'; act: string; env: number[] };
type Pt = { x: number; y: number; depth: number; px_per_m: number };
const LINES = EP.lines as Line[];
const SHOTS = PLATES.shots as Record<string, { maya_face: Pt; claude_feet: Pt; desk_y: number }>;
export const REEL3D_FPS = 30;
export const REEL3D_FRAMES = Math.ceil(EP.duration * REEL3D_FPS);

const clamp = (x: number, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const lineAt = (t: number) => { let L = LINES[0]; for (const l of LINES) if (t >= l.t - 0.25) L = l; return L; };
const envAt = (t: number, who: 'M' | 'C') => {
  for (const l of LINES) if (l.who === who && t >= l.t && t < l.t + l.d) return l.env[Math.min(l.env.length - 1, Math.floor((t - l.t) * EP.fps))] ?? 0;
  return 0;
};
const env = (t: number, who: 'M' | 'C') => (envAt(t - 1 / EP.fps, who) + 2 * envAt(t, who) + envAt(t + 1 / EP.fps, who)) / 4;
const FACE: Record<string, string> = { worried: 'worried', flat: 'flat', surprised: 'surprised', thinking: 'thinking', wink: 'wink' };

// sheet art scale: the Maya bust image is 615x635 px for ~0.615 m; her face centre sits at (70%, 48%) of it
const MAYA_M = 0.615, FACE_U = 0.70, FACE_V = 0.48;
const CLAUDE_H = 0.2; // metres

const Plate: React.FC<{ src: string }> = ({ src }) => (
  <Img src={staticFile(`plates/${src}`)} style={{ position: 'absolute', inset: 0, width: '100%', height: '100%' }} />
);

const Maya: React.FC<{ face: string; talk: number; t: number; fx: number; fy: number; ppm: number; blur?: number; tilt?: number }> =
  ({ face, talk, t, fx, fy, ppm, blur = 0, tilt = 0 }) => {
    const w = MAYA_M * ppm, h = w * 635 / 615;
    const speaking = talk > 0.3 && Math.floor(t * 12) % 2 === 0 && face !== 'thinking';
    const rot = Math.sin(t * 0.7) * 1.2 + tilt + talk * Math.sin(t * 9) * 0.8;
    return (
      <div style={{
        position: 'absolute', left: fx - FACE_U * w, top: fy - FACE_V * h, width: w, height: h,
        transform: `rotate(${rot}deg) scale(${1 + Math.sin(t * 1.6) * 0.008})`, transformOrigin: `${FACE_U * 100}% 95%`,
        filter: `${blur ? `blur(${blur}px) ` : ''}brightness(0.95) saturate(1.05)`,
      }}>
        <Img src={staticFile(`chars/maya_${speaking ? 'talk' : face}.png`)} style={{ width: '100%', height: '100%' }} />
      </div>
    );
  };

const Claude: React.FC<{ L: Line; since: number; talk: number; t: number; x: number; y: number; ppm: number; blur?: number }> =
  ({ L, since, talk, t, x, y, ppm, blur = 0 }) => {
    const mine = L.who === 'C';
    const hgt = CLAUDE_H * ppm;
    let hop = (Math.abs(Math.sin(t * 2.2)) * 0.002 + talk * 0.012) * ppm;
    if (mine && L.act === 'excited') hop += Math.abs(Math.sin(since * 10)) * 0.05 * ppm * clamp(1 - since / 1.4);
    if (mine && L.act === 'bounce') hop += Math.abs(Math.sin(since * 8)) * 0.015 * ppm * clamp(1 - since / 0.8);
    const sq = 1 + talk * 0.07 + Math.sin(t * 2.2) * 0.012;
    let rot = Math.sin(t * 1.3) * 1.5;
    if (mine && L.act === 'tilt') rot += 9 * clamp(since / 0.4);
    const away = mine && L.act === 'look-away' && since > 0.2 && since < L.d + 0.3;
    const squint = mine && L.act === 'squint' ? 1 - 0.1 * clamp(since / 0.3) : 1;
    const w = hgt * (away ? 362 : 395) / 419;
    return (
      <>
        <div style={{ position: 'absolute', left: x - w * 0.55, top: y - hgt * 0.06, width: w * 1.1, height: hgt * 0.14, borderRadius: '50%',
          background: 'rgba(20,8,4,0.55)', filter: `blur(${hgt * 0.04}px)`, opacity: 1 - clamp(hop / (0.06 * ppm)) * 0.6 }} />
        <div style={{
          position: 'absolute', left: x - w / 2, top: y - hgt - hop, width: w, height: hgt,
          transform: `rotate(${rot}deg) scale(${(away ? -1 : 1) / Math.sqrt(sq)}, ${sq * squint})`, transformOrigin: '50% 100%',
          filter: blur ? `blur(${blur}px)` : 'brightness(0.97)',
        }}>
          <Img src={staticFile(`chars/${away ? 'claude_three_quarter.png' : 'claude_front.png'}`)} style={{ width: '100%', height: '100%' }} />
        </div>
      </>
    );
  };

const Caption: React.FC<{ text: string; age: number }> = ({ text, age }) => {
  const { fps } = useVideoConfig();
  const pop = spring({ frame: Math.round(age * fps), fps, config: { damping: 14, stiffness: 180 } });
  return (
    <div style={{ position: 'absolute', top: 300, left: 0, right: 0, display: 'flex', justifyContent: 'center' }}>
      <div style={{
        maxWidth: 720, padding: '18px 30px', borderRadius: 22, background: 'rgba(20,20,32,0.78)', color: 'white',
        fontFamily: 'Inter, sans-serif', fontWeight: 700, fontSize: 46, lineHeight: 1.22, textAlign: 'center',
        transform: `scale(${0.85 + 0.15 * pop})`, opacity: pop,
      }}>{text}</div>
    </div>
  );
};

export const FirstReel3D: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const L = lineAt(t); const i = LINES.indexOf(L); const since = t - L.t;
  const start = i === 0 ? 0 : L.t - 0.25;
  const end = i + 1 < LINES.length ? LINES[i + 1].t - 0.25 : EP.duration;
  const u = clamp((t - start) / (end - start));
  const prev = LINES[i - 1];
  const faceSrc = L.who === 'M' ? L : prev && prev.who === 'M' ? prev : L;
  const face = FACE[faceSrc.act] ?? 'flat';
  const mTalk = env(t, 'M'), cTalk = env(t, 'C');
  const S = SHOTS[L.shot];
  const push = 1 + (L.shot === 'wide' ? 0.04 : 0.06) * u;            // slow push-in, the whole stack together

  const m = S.maya_face, c = S.claude_feet;
  let layers: React.ReactNode;
  if (L.shot === 'maya') {
    layers = <>
      <Plate src="maya_bg.png" />
      <Maya face={face} talk={mTalk} t={t} fx={m.x} fy={Math.max(m.y, 1920 - 0.53 * MAYA_M * m.px_per_m * 635 / 615)} ppm={m.px_per_m} tilt={L.act === 'thinking' ? -3 : 0} />
      <Plate src="maya_fg.png" />
    </>;
  } else if (L.shot === 'claude') {
    layers = <>
      <Plate src="claude_bg.png" />
      {/* Maya is off to the left of this camera; nudge her into the edge of frame, out of focus like the room */}
      <Maya face={face} talk={mTalk} t={t} fx={Math.max(m.x, 170)} fy={m.y + 80} ppm={m.px_per_m} blur={16} />
      <Plate src="claude_fg.png" />
      <Claude L={L} since={since} talk={cTalk} t={t} x={c.x} y={c.y} ppm={c.px_per_m} />
    </>;
  } else {
    const sink = 0.12 * m.px_per_m;   // seat her a little lower so the desk hides where the bust ends
    layers = <>
      <Plate src="wide_bg.png" />
      <Maya face={face} talk={mTalk} t={t} fx={m.x} fy={m.y + sink} ppm={m.px_per_m} />
      <Plate src="wide_fg.png" />
      <Claude L={L} since={since} talk={cTalk} t={t} x={c.x} y={c.y} ppm={c.px_per_m} />
    </>;
  }
  const fade = interpolate(frame, [0, 8], [0, 1], { extrapolateRight: 'clamp' })
    * interpolate(t, [EP.duration - 0.8, EP.duration], [1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const capOn = t >= L.t - 0.05 && t <= L.t + L.d + 0.2;
  return (
    <AbsoluteFill style={{ background: '#0b0d18' }}>
      <AbsoluteFill style={{ opacity: fade, transform: `scale(${push})` }}>{layers}</AbsoluteFill>
      <AbsoluteFill style={{ background: 'radial-gradient(ellipse at 50% 45%, rgba(0,0,0,0) 55%, rgba(4,5,14,0.55) 100%)' }} />
      {capOn && <Caption key={i} text={L.text} age={t - (L.t - 0.05)} />}
      <Audio src={staticFile('first-reel/mix.wav')} />
    </AbsoluteFill>
  );
};
