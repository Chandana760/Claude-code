---
name: open-generative-ai
description: >
  Generate AI images, videos, audio and lip-sync clips through MuAPI, the 600+ model API behind the
  open-source Open-Generative-AI studio (Nano Banana, GPT Image, FLUX, Seedream, Kling, Veo, Sora,
  Seedance, Hailuo, Wan and more). Use when the user asks to generate or edit an image, make a video
  from text or an image, animate a photo, upscale or restyle a video, lip-sync a portrait to audio,
  or generate music/speech — and mentions MuAPI, Open-Generative-AI, or one of those model names,
  or has a MUAPI_API_KEY. Requires a MuAPI API key with credits; every generation costs money.
metadata:
  homepage: https://github.com/Anil-matcha/Open-Generative-AI
  api: https://api.muapi.ai
---

# Open Generative AI (MuAPI)

Open-Generative-AI is a web/desktop studio; all of its generation goes through one HTTP API,
MuAPI. This skill drives that API directly with `scripts/muapi.py` (Python stdlib only), using the
same request pattern as the app's `src/lib/muapi.js`.

## Prerequisites (check first)

1. **API key**: `MUAPI_API_KEY` must be set (key from https://muapi.ai). Never ask the user to paste
   it into chat; in a cloud session, request it as a credential for host `api.muapi.ai`
   (header `x-api-key`, no prefix). If the proxy injects it, set `MUAPI_API_KEY=dummy` so the
   script starts.
2. **Network**: `api.muapi.ai` must be reachable (a 403 from the agent proxy means the host is not
   allowed — ask the user to allow it). Output files are served from CDN hosts that may also need
   allowing; if downloads fail, give the user the output URLs instead.
3. **Cost**: generations spend credits (video especially). Confirm model + settings with the user
   before batch or expensive runs; don't retry failures in a loop.

## The API in one paragraph

`POST https://api.muapi.ai/api/v1/<endpoint>` with header `x-api-key` and a JSON body → returns
`{"request_id": ...}`. Poll `GET /api/v1/predictions/<request_id>/result` every 2 s until `status`
is `completed`/`succeeded` (outputs in `outputs[]`) or `failed`. Local files must first go through
`POST /api/v1/upload_file` (multipart field `file`) which returns a hosted `url` to pass as
`image_url`, `video_url`, `audio_url`, etc. Errors: 401/403 bad key, 402 out of credits.

## Workflow

1. **Pick a model.** Search the bundled catalog (617 models, grouped by task):
   ```bash
   python3 .claude/skills/open-generative-ai/scripts/muapi.py models seedance
   ```
   Use the **endpoint** column (it can differ from the id, e.g. `gpt-image-2` →
   `gpt-image-2-text-to-image`). The notes column lists the model's extra inputs and, for
   image/video-input models, which field the media goes in (`imageField=images_list` means pass a
   JSON array). Full catalog: `references/models.md`. If an input's valid values are unclear, fetch
   `https://api.muapi.ai/openapi.json` for the authoritative schema.

   Good defaults if the user doesn't care: image `nano-banana-2` or `gpt-image-2-text-to-image`;
   image edit `nano-banana-2-edit` (inputs go in `images_list`); video `seedance-v2.0-t2v`, `veo3.1-fast-text-to-video`,
   `kling-v2.6-pro-t2v`; image→video `kling`/`seedance` i2v entries. Verify the exact endpoint
   with `models` before calling.

2. **Upload inputs** (only for local files; public URLs can be passed directly):
   ```bash
   python3 .claude/skills/open-generative-ai/scripts/muapi.py upload ./photo.jpg
   ```

3. **Run and download:**
   ```bash
   python3 .claude/skills/open-generative-ai/scripts/muapi.py run nano-banana-2 \
     -p prompt="a lighthouse at dusk, cinematic" -p aspect_ratio=16:9 --out ./outputs
   ```
   ```bash
   python3 .claude/skills/open-generative-ai/scripts/muapi.py run seedance-v2.0-i2v \
     -p prompt="slow push-in, waves crashing" -p image_url=https://... -p duration=5 --out ./outputs
   ```
   `-p` values are parsed as JSON when possible (`-p images_list='["https://a","https://b"]'`,
   `-p duration=5`); `--json '{...}'` sets the whole body. Prints
   `{request_id, status, outputs, files}`. Videos can take minutes — run long jobs in the
   background. If polling times out, resume with `muapi.py result <request_id> --out ./outputs`.

4. **Report** the output file paths (or URLs) and the model used. Show images/videos to the user
   when the surface can render them.

## Payload conventions (from the app's client)

- Text→image: `prompt`, `aspect_ratio` (or `width`/`height` for some models), optional
  `resolution`, `quality`, `seed`, `num_images`.
- Image→image: `prompt` + media in the model's `imageField` (`image_url` default, or
  `images_list` array); some accept `strength`.
- Text/image→video: `prompt`, `aspect_ratio`, `duration`, `resolution`, `quality`, `mode`; start
  frame in `imageField`, optional end frame in `lastImageField` (e.g. `last_image`,
  `end_image_url`). Effect-style models (`generate_wan_ai_effects`) take `name` = effect name.
- Video→video: media in `videoField` (default `video_url`); motion-control models also take
  `image_url` and `prompt`.
- Lip sync: `audio_url` plus `image_url` (portrait) or `video_url`; optional `prompt`,
  `resolution`, `seed`.

Only send inputs the model lists; unknown fields can cause 4xx errors.
