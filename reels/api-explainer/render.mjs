// Render the reel frame by frame.
//   node render.mjs stills 1,6,9 [outdir] [WxH]   -> JPEG stills for checking
//   node render.mjs video out.mp4 [WxH] [from] [to] -> silent H.264 video (30 fps)
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { spawn } from 'node:child_process';
import { createRequire } from 'node:module';
const { chromium } = createRequire(import.meta.url)('playwright');

const root = path.dirname(new URL(import.meta.url).pathname);
const types = { '.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript' };
const server = http.createServer((req, res) => {
  const p = path.join(root, decodeURIComponent(req.url.split('?')[0]));
  if (!p.startsWith(root) || !fs.existsSync(p) || fs.statSync(p).isDirectory()) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'Content-Type': types[path.extname(p)] || 'application/octet-stream' });
  fs.createReadStream(p).pipe(res);
}).listen(0);
const port = server.address().port;

const [mode, arg, a3, a4, a5, a6] = process.argv.slice(2);
const size = (mode === 'stills' ? a4 : a3) || '1080x1920';
const [W, H] = size.split('x').map(Number);

const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: W, height: H } });
page.on('console', m => { if (m.type() === 'error') console.error('page:', m.text()); });
page.on('pageerror', e => console.error('pageerror:', e.message));
await page.goto(`http://localhost:${port}/scene.html?w=${W}&h=${H}`);
await page.waitForFunction(() => window.READY === true, null, { timeout: 120000 });
const frame = async t => Buffer.from((await page.evaluate(t => window.frameJPEG(t, 0.93), t)).split(',')[1], 'base64');

if (mode === 'glb') {
  fs.writeFileSync(arg, Buffer.from(await page.evaluate(() => window.exportGLB()), 'base64')); console.log('wrote', arg);
} else if (mode === 'stills') {
  const dir = a3 || 'stills'; fs.mkdirSync(dir, { recursive: true });
  for (const t of arg.split(',').map(Number)) { fs.writeFileSync(path.join(dir, `t${String(t).padStart(5, '0')}.jpg`), await frame(t)); console.log('still', t); }
} else {
  const dur = await page.evaluate(() => window.DURATION), fps = 30;
  const from = +(a4 || 0), to = +(a5 || dur);
  const ff = spawn('ffmpeg', ['-y', '-v', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', arg], { stdio: ['pipe', 'inherit', 'inherit'] });
  const n0 = Math.round(from * fps), n1 = Math.round(to * fps), t0 = Date.now();
  for (let n = n0; n < n1; n++) {
    const buf = await frame(n / fps);
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (n % 30 === 0) { const el = (Date.now() - t0) / 1000, done = n - n0 + 1; console.log(`frame ${n}/${n1}  ${(el / done).toFixed(2)}s/f  eta ${Math.round(el / done * (n1 - n))}s`); }
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r));
  console.log('wrote', arg);
}
await browser.close(); server.close();
