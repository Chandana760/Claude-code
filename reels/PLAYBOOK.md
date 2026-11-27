# Reel playbook (from the reference account's 40 latest reels)

## Character lock (never change)

Maya and Claude look identical in every episode. Never change her face, hair (near-black,
sleek, middle-parted fringe to the glasses), glasses, lavender open jacket + dark tee,
hands, or Claude's shape, colour and eyes. Only the background / set, props, camera
framing and poses may change between episodes. Any set-specific tweak (e.g. the sofa
set's `HAIR_FRAME` / `HAIR_FALL`) must stay gated to that set and never leak into the
standard look.

Reference reels are for pacing, shot types and framing ideas only: build our own scene
with our characters, never copy the reference's characters, layout or look.

## Captions (Instagram-safe)

Caption pills sit at y = 290 px (`CAP_Y` in make_reel.py): below the Reels header and
inside the 3:4 profile-grid crop (which cuts 240 px off the top and bottom of a
1080x1920 reel). Frame every shot with enough headroom that captions sit on the
background, not on faces.

## Content buckets
Ranked by plays in the scraped dataset.

| Bucket | Share | Typical plays | Format |
|---|---|---|---|
| **Daily life · EP n**: relatable work skits | ~35% | 20k–2.1M (top: "she said no sixty-one times") | Desk, no board. Maya asks, Claude answers kindly or deadpan. The emotional turn comes in the last 2 lines. |
| **Explain like I'm 5 · part n**: one tech word | ~20% | 20k–2.4M (top: "what's an API?") | Whiteboard behind them. Claude points with a stick, uses a real-world metaphor (waiter, doorbell, open-book test) and ends on a twist. |
| **AI vs AI**: other assistants as characters | ~10% | 50k–1.5M ("pick your assistant") | Several mascots on the desk; the joke is the personalities. |
| **Topical / news**: outages, launches | ~10% | 15k–55k | Short (17–30 s) and posted the same day. |
| **Sponsored tool**: "comment WORD and we'll DM you" | ~25% | 1k–90k | A skit set-up, then the tool solves it. CTA in caption and last line. |

The evergreen buckets (daily life, ELI5) beat the sponsored ones by 10–100×. Keep sponsored to roughly 1 in 4.

## Episode formula
- **Length:** 30–55 s, 8–16 lines, one line per shot.
- **Lines:** short, with pauses that do the acting (`[long pause]`, `...`).
- **Shots:**
  - Maya close-up (chest up, soft background);
  - Claude close-up (Maya blurred behind);
  - wide desk shot for scene resets and the ending.
- **Captions:** a small white bold line in a dark rounded pill at the top third.
- **Cover:** a series tag pill (e.g. `DAILY LIFE · EP 3`), then a 2–4 word hook in heavy type with one accent-coloured word.
- **Caption copy:**
  - Start with "send this to the ___ who ___."
  - Add a one-line recap and a question to drive comments.
  - End with 5 hashtags.

## Sets
One desk, many moods. Only the window changes:

| Set | Window | Use |
|---|---|---|
| `--set daily` | sunset city | daily life |
| `--set sheet` | night city + whiteboard | explainers |

Day and rain variants are the next two to add.

## Our characters (not the reference's)
- **Maya:** teal jacket, plum wavy hair, round glasses (from our character sheet).
- **Claude:** orange faceted cloud mascot.

## Pipeline
1. Put `script.py` in the episode folder.
2. Run `python3 ../blender-episode/voices_el.py`. It uses ElevenLabs v3 and writes `lines.json` and `dialogue.wav`.
3. Render with `bl/bin/python ../blender-episode/build.py -- --ep . --set daily --render frames --step 2`.
4. Mix music with `gen_audio.py`, then sidechain it under the dialogue to make `mix.wav`.
5. Run `captions.py`, then `assemble.py frames out.mp4`.
6. Make the cover with `cover.py frame.jpg "DAILY LIFE · EP 1" "Inbox *zero.*" cover.jpg`.


## Standard set and characters (default for every episode)
Every episode reuses this setup unless the episode says otherwise. It is built by
`blender/cozy_desk_studio.py` (set) and `blender/desk_characters.py` (characters).

| Part | Default |
|---|---|
| Window | Big window with thick black frame bars; pink-magenta-to-purple sunset with an orange glow; close dark city blocks with a few lit windows; no moon or stars |
| Desk | Dark brown wood; monitor with code on the left; white mug; white paper with an orange sticky note; keyboard; small lamp on the right |
| Maya | Chibi head (smooth), dot eyes with glints, big thin black round glasses, sleek near-black straight hair with a fringe, lavender jacket open over a dark tee (`NECKLINE = "open"`), arms crossed on the desk |
| Claude | Wide, flat orange (#D9531E) beveled-cube mascot, tall black eyes, stubby feet; hops at line starts, slight vibration while talking, eyes flex and blink to squares |
| Shots | `maya` close-up with headroom for captions, `claude` close-up with Maya still and blurred behind, `wide` desk shot with the monitor in frame |
| Captions | Small white bold text in a dark pill, high in frame (over the window, never on a face) |
| Audio | Voices + soft piano bed only (`idea-reel/soft_music.py`): no caption pops, drums or crackle; every line levelled to the same loudness; tight gaps, no dead air |

### Changing the set for one episode
Set changes live in the build scripts, so an episode that needs a different look should
pass its own values rather than editing the defaults:
- Sky/time of day: the colour stops in `sky_mat()` (`cozy_desk_studio.py`).
- Props: the `build_desk_and_props()` section (mug, paper and note, plant, lamp).
- Outfit: `OUTFIT` / `NECKLINE` switches in `desk_characters.py`.
- Shots: the `cams` table in `first-reel-lowpoly/style_for_episode()`.
Keep the defaults as above and note any per-episode change in that episode's `script.py`.

### Making an episode
1. `mkdir reels/<episode>`; write `script.py` (who, text with ElevenLabs v3 tags, shot, acting, pause, optional cut-off length).
2. `python3 ../idea-reel/voices.py` (levelled voices) -> `lines.json`, `dialogue.wav`.
3. `python3 ../idea-reel/soft_music.py <duration>`, then duck it under the dialogue into `mix.wav` (see `idea-reel`).
4. `python3 ../first-reel-lowpoly/animate.py -- --ep . --blend episode.blend`
5. `python3 ../first-reel-lowpoly/animate.py -- --ep . --frames frames --step 2` (render; resumable)
6. `python3 ../first-reel-lowpoly/make_reel.py frames <out.mp4> .`
