# Reel playbook (from the reference account's 40 latest reels)

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
