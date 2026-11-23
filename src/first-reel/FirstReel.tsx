import React from 'react';
import {
  AbsoluteFill, Audio, Img, interpolate, Sequence, spring, staticFile, useCurrentFrame, useVideoConfig,
} from 'remotion';
import EP from './lines.json';

// "Daily life" redesign: our own script in the reference's format (alternating close-ups, caption pills,
// emotional turn at the end), drawn from the character-sheet art. Voices + mouth envelopes come from lines.json.

type Line = { t: number; d: number; who: 'M' | 'C'; text: string; shot: 'maya' | 'claude' | 'wide'; act: string; env: number[] };
const LINES = EP.lines as Line[];
export const FIRST_REEL_FPS = 30;
export const FIRST_REEL_FRAMES = Math.ceil(EP.duration * FIRST_REEL_FPS);
const ENV_FPS = EP.fps;

const clamp = (x: number, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const lineAt = (t: number) => { let L = LINES[0]; for (const l of LINES) if (t >= l.t - 0.25) L = l; return L; };
const envAt = (t: number, who: 'M' | 'C') => {
  for (const l of LINES) if (l.who === who && t >= l.t && t < l.t + l.d) return l.env[Math.min(l.env.length - 1, Math.floor((t - l.t) * ENV_FPS))] ?? 0;
  return 0;
};
const env = (t: number, who: 'M' | 'C') => (envAt(t - 1 / ENV_FPS, who) + 2 * envAt(t, who) + envAt(t + 1 / ENV_FPS, who)) / 4;

const FACE: Record<string, string> = { worried: 'worried', flat: 'flat', surprised: 'surprised', thinking: 'thinking', wink: 'wink' };
const mayaFace = (L: Line, prev?: Line) => {
  const src = L.who === 'M' ? L : prev && prev.who === 'M' ? prev : L;
  return FACE[src.act] ?? 'flat';
};

// ---------------------------------------------------------------- pieces
const Backdrop: React.FC<{ t: number; shift: number; blur: number; dim: number }> = ({ t, shift, blur, dim }) => (
  <AbsoluteFill style={{ overflow: 'hidden', background: '#0d1020' }}>
    <Img src={staticFile('chars/scene_desk2.jpg')} style={{
      position: 'absolute', height: '100%', left: '50%', top: 0,
      transform: `translateX(calc(-50% + ${shift + Math.sin(t * 0.2) * 12}px)) scale(1.3)`,
      filter: `blur(${blur}px) brightness(${dim}) saturate(1.1)`,
    }} />
    <AbsoluteFill style={{ background: 'radial-gradient(ellipse at 50% 45%, rgba(0,0,0,0) 35%, rgba(5,6,18,0.75) 100%)' }} />
  </AbsoluteFill>
);

// Maya: a cut-out face from the sheet + a small mouth driven by her voice
const Maya: React.FC<{ face: string; talk: number; t: number; height: number; x: number; y: number; blur?: number; tilt?: number }> =
  ({ face, talk, t, height, x, y, blur = 0, tilt = 0 }) => {
    const w = height * 615 / 635;
    x = x - (0.715 - 0.5) * w;   // the face sits right of the image centre (hair fans out left)
    const breathe = 1 + Math.sin(t * 1.6) * 0.008;
    // lip flap: while she speaks, flick to the sheet's open-mouth face on loud syllables (held on twos)
    const speaking = talk > 0.3 && Math.floor(t * 12) % 2 === 0 && face !== 'thinking';
    const rot = Math.sin(t * 0.7) * 1.2 + tilt + talk * Math.sin(t * 9) * 0.8;
    return (
      <div style={{
        position: 'absolute', left: x - w / 2, top: y - height, width: w, height,
        transform: `rotate(${rot}deg) scale(${breathe})`, transformOrigin: '50% 90%', filter: blur ? `blur(${blur}px)` : undefined,
      }}>
        <Img src={staticFile(`chars/maya_${speaking ? 'talk' : face}.png`)} style={{ width: '100%', height: '100%' }} />
      </div>
    );
  };

// Claude: cut-out mascot that squashes / bounces with his voice
const Claude: React.FC<{ L: Line; since: number; talk: number; t: number; height: number; x: number; y: number; blur?: number }> =
  ({ L, since, talk, t, height, x, y, blur = 0 }) => {
    const mine = L.who === 'C';
    let hop = Math.abs(Math.sin(t * 2.2)) * 4 + talk * 26;
    if (mine && L.act === 'excited') hop += Math.abs(Math.sin(since * 10)) * 70 * clamp(1 - since / 1.4);
    if (mine && L.act === 'bounce') hop += Math.abs(Math.sin(since * 8)) * 24 * clamp(1 - since / 0.8);
    const sq = 1 + talk * 0.07 + Math.sin(t * 2.2) * 0.012;
    let rot = Math.sin(t * 1.3) * 1.5;
    if (mine && L.act === 'tilt') rot += 9 * clamp(since / 0.4);
    const away = mine && L.act === 'look-away' && since > 0.2 && since < L.d + 0.3;
    const squint = mine && L.act === 'squint' ? 1 - 0.1 * clamp(since / 0.3) : 1;
    const src = away ? 'claude_three_quarter.png' : 'claude_front.png';
    const w = height * (away ? 362 : 395) / 419;
    return (
      <div style={{
        position: 'absolute', left: x - w / 2, top: y - height - hop, width: w, height,
        transform: `rotate(${rot}deg) scale(${(away ? -1 : 1) / Math.sqrt(sq)}, ${sq * squint})`, transformOrigin: '50% 100%',
        filter: blur ? `blur(${blur}px)` : 'drop-shadow(0 18px 18px rgba(0,0,0,0.45))',
      }}>
        <Img src={staticFile(`chars/${src}`)} style={{ width: '100%', height: '100%' }} />
      </div>
    );
  };

const Desk: React.FC<{ top: number; cx: number }> = ({ top, cx }) => (
  <>
    <div style={{
      position: 'absolute', left: -60, right: -60, top, bottom: -60,
      background: 'linear-gradient(180deg, #3b2418 0%, #6e4630 3%, #5a3825 20%, #3d2519 70%, #24150e 100%)',
    }} />
    <div style={{ position: 'absolute', left: -60, right: -60, top, height: 260,
      background: 'radial-gradient(ellipse at 70% 0%, rgba(255,200,140,0.25) 0%, rgba(0,0,0,0) 60%)' }} />
    {/* blurred props, like the sheet's desk */}
    <div style={{ position: 'absolute', left: 40, top: top - 150, width: 140, height: 170, borderRadius: '10px 10px 24px 24px', background: '#efe9df', filter: 'blur(10px)', opacity: 0.85 }} />
    <div style={{ position: 'absolute', left: 20, top: top + 10, width: 190, height: 26, borderRadius: 6, background: '#f2c230', filter: 'blur(8px)', opacity: 0.8 }} />
    <div style={{ position: 'absolute', left: cx - 170, top: top + 60, width: 340, height: 50, borderRadius: '50%', background: 'rgba(0,0,0,0.55)', filter: 'blur(14px)' }} />
  </>
);

const Caption: React.FC<{ text: string; age: number }> = ({ text, age }) => {
  const { fps } = useVideoConfig();
  const pop = spring({ frame: Math.round(age * fps), fps, config: { damping: 14, stiffness: 180 } });
  return (
    <div style={{ position: 'absolute', top: 300, left: 0, right: 0, display: 'flex', justifyContent: 'center' }}>
      <div style={{
        maxWidth: 720, padding: '18px 30px', borderRadius: 22, background: 'rgba(20,20,32,0.78)',
        color: 'white', fontFamily: 'Inter, sans-serif', fontWeight: 700, fontSize: 46, lineHeight: 1.22, textAlign: 'center',
        transform: `scale(${0.85 + 0.15 * pop})`, opacity: pop,
      }}>{text}</div>
    </div>
  );
};

// ---------------------------------------------------------------- shots
export const FirstReel: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const L = lineAt(t); const i = LINES.indexOf(L); const since = t - L.t;
  const start = i === 0 ? 0 : L.t - 0.25;
  const end = i + 1 < LINES.length ? LINES[i + 1].t - 0.25 : EP.duration;
  const u = clamp((t - start) / (end - start));
  const push = 1 + 0.05 * u;                                   // slow push-in inside each shot
  const face = mayaFace(L, LINES[i - 1]);
  const mTalk = env(t, 'M'); const cTalk = env(t, 'C');
  const capOn = t >= L.t - 0.05 && t <= L.t + L.d + 0.2;

  let shot: React.ReactNode;
  if (L.shot === 'maya') {
    shot = (
      <AbsoluteFill style={{ transform: `scale(${push})` }}>
        <Backdrop t={t} shift={60} blur={14} dim={0.55} />
        <Maya face={face} talk={mTalk} t={t} height={1300} x={540} y={1930} tilt={L.act === 'thinking' ? -3 : 0} />
      </AbsoluteFill>
    );
  } else if (L.shot === 'claude') {
    shot = (
      <AbsoluteFill style={{ transform: `scale(${push})` }}>
        <Backdrop t={t} shift={-80} blur={16} dim={0.5} />
        <Maya face={face} talk={mTalk} t={t} height={1250} x={330} y={1440} blur={14} />
        <Desk top={1400} cx={600} />
        <Claude L={L} since={since} talk={cTalk} t={t} height={640} x={600} y={1480} />
      </AbsoluteFill>
    );
  } else {
    const z = 1.06 + 0.06 * u;
    shot = (
      <AbsoluteFill>
        <Backdrop t={t} shift={0} blur={22} dim={0.45} />
        <div style={{ position: 'absolute', left: 0, right: 0, top: 520, height: 920, overflow: 'hidden', borderRadius: 0 }}>
          <Img src={staticFile('chars/scene_desk2.jpg')} style={{
            position: 'absolute', height: '100%', left: '50%', transform: `translateX(-50%) scale(${z})`, filter: 'brightness(0.95)',
          }} />
          <AbsoluteFill style={{ background: 'linear-gradient(180deg, rgba(5,6,18,0.6) 0%, rgba(0,0,0,0) 18%, rgba(0,0,0,0) 82%, rgba(5,6,18,0.6) 100%)' }} />
        </div>
      </AbsoluteFill>
    );
  }
  const fadeIn = interpolate(frame, [0, 8], [0, 1], { extrapolateRight: 'clamp' });
  const fadeOut = interpolate(t, [EP.duration - 0.8, EP.duration], [1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  return (
    <AbsoluteFill style={{ background: '#0d1020' }}>
      <AbsoluteFill style={{ opacity: fadeIn * fadeOut }}>{shot}</AbsoluteFill>
      {capOn && <Caption key={i} text={L.text} age={t - (L.t - 0.05)} />}
      <Sequence><Audio src={staticFile('first-reel/mix.wav')} /></Sequence>
    </AbsoluteFill>
  );
};

// Grid cover: a frame + series tag pill + a heavy title with one accent word
export const FirstReelCover: React.FC = () => (
  <AbsoluteFill style={{ background: '#0d1020' }}>
    <Backdrop t={0} shift={60} blur={14} dim={0.55} />
    <Maya face="worried" talk={0} t={0} height={1300} x={540} y={1650} />
    <AbsoluteFill style={{ background: 'linear-gradient(180deg, rgba(0,0,0,0) 45%, rgba(8,8,14,0.92) 78%)' }} />
    <div style={{ position: 'absolute', left: 80, bottom: 200, right: 80, fontFamily: 'Inter, sans-serif' }}>
      <div style={{ display: 'inline-block', background: '#f2b632', color: '#16161e', fontWeight: 800, fontSize: 34, padding: '10px 20px', borderRadius: 12, marginBottom: 28 }}>
        DAILY LIFE · EP 2
      </div>
      <div style={{ color: 'white', fontWeight: 900, fontSize: 118, lineHeight: 1.04 }}>
        Is my first reel <span style={{ color: '#f2b632' }}>good?</span>
      </div>
    </div>
  </AbsoluteFill>
);
