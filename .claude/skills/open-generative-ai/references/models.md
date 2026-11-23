# MuAPI model catalog

Extracted from Open-Generative-AI `packages/studio/src/models.js` (snapshot 2026-11-23). POST to `https://api.muapi.ai/api/v1/<endpoint>`. Columns: id · endpoint · name · extra input fields (image/video field names, enum inputs). The authoritative, current schema is `https://api.muapi.ai/openapi.json`.


## Text → Image — 88 models

| id | endpoint | name | notes |
|---|---|---|---|
| `nano-banana` | `nano-banana` | Nano Banana | inputs: aspect_ratio |
| `flux-dev` | `flux-dev-image` | FLUX.1 Dev | inputs: width, height, num_images |
| `flux-kontext-dev-t2i` | `flux-kontext-dev-t2i` | FLUX.1 Kontext Dev | inputs: aspect_ratio, num_images |
| `hidream-i1-fast` | `hidream_i1_fast_image` | HiDream I1 Fast | inputs: width, height, num_images |
| `hidream-i1-dev` | `hidream_i1_dev_image` | HiDream I1 Dev | inputs: width, height, num_images |
| `hidream-i1-full` | `hidream_i1_full_image` | HiDream I1 Full | inputs: width, height, num_images |
| `ai-anime-generator` | `ai-anime-generator` | Ai Anime Generator | inputs: width, height |
| `wan2.1-text-to-image` | `wan2.1-text-to-image` | Wan 2.1 | inputs: width, height |
| `flux-kontext-pro-t2i` | `flux-kontext-pro-t2i` | FLUX.1 Kontext Pro | inputs: aspect_ratio |
| `flux-kontext-max-t2i` | `flux-kontext-max-t2i` | FLUX.1 Kontext Max | inputs: aspect_ratio |
| `gpt4o-text-to-image` | `gpt4o-text-to-image` | GPT-4o | inputs: aspect_ratio, num_images |
| `flux-schnell` | `flux-schnell-image` | FLUX.1 Schnell | inputs: width, height, num_images |
| `bytedance-seedream-v3` | `bytedance-seedream-image` | Seedream 3.0 | inputs: aspect_ratio |
| `qwen-image` | `qwen-image` | Qwen Image | inputs: aspect_ratio, num_images |
| `flux-pulid` | `flux-pulid` | Flux Pulid | inputs: image_url, aspect_ratio |
| `ideogram-v3-t2i` | `ideogram-v3-t2i` | Ideogram 3.0 | inputs: render_speed, style, aspect_ratio, num_images |
| `google-imagen4` | `google-imagen4` | Imagen 4 | inputs: aspect_ratio, num_images |
| `google-imagen4-fast` | `google-imagen4-fast` | Imagen 4 Fast | inputs: aspect_ratio, num_images |
| `google-imagen4-ultra` | `google-imagen4-ultra` | Imagen 4 Ultra | inputs: aspect_ratio |
| `sdxl-image` | `sdxl-image` | Stable Diffusion XL 1.0 | inputs: width, height |
| `bytedance-seedream-v4` | `bytedance-seedream-v4` | Seedream 4.0 | inputs: aspect_ratio, resolution, num_images |
| `hunyuan-image-2.1` | `hunyuan-image-2.1` | Hunyuan Image 2.1 | inputs: width, height |
| `chroma-image` | `chroma-image` | Chroma Image | inputs: width, height |
| `flux-redux` | `flux-redux` | FLUX.1 Redux Dev | inputs: image_url, aspect_ratio, num_images |
| `flux-krea-dev` | `flux-krea-dev` | FLUX.1 Krea Dev | inputs: aspect_ratio, num_images |
| `perfect-pony-xl` | `perfect-pony-xl` | Perfect Pony Xl | inputs: width, height |
| `neta-lumina` | `neta-lumina` | Neta Lumina | inputs: width, height |
| `wan2.5-text-to-image` | `wan2.5-text-to-image` | Wan 2.5 | inputs: width, height |
| `hunyuan-image-3.0` | `hunyuan-image-3.0` | Hunyuan Image 3.0 | inputs: width, height |
| `leonardoai-phoenix-1.0` | `leonardoai-phoenix-1.0` | Leonardo Phoenix 1.0 | inputs: aspect_ratio |
| `leonardoai-lucid-origin` | `leonardoai-lucid-origin` | Lucid Origin | inputs: aspect_ratio |
| `reve-text-to-image` | `reve-text-to-image` | Reve Image | inputs: aspect_ratio |
| `grok-imagine-text-to-image` | `grok-imagine-text-to-image` | Grok Imagine Image | inputs: aspect_ratio |
| `nano-banana-pro` | `nano-banana-pro` | Nano Banana Pro | inputs: aspect_ratio, resolution |
| `kling-o1-text-to-image` | `kling-o1-text-to-image` | Kling Image O1 | inputs: aspect_ratio, resolution, num_images |
| `z-image-turbo` | `z-image-turbo` | Z Image Turbo | inputs: width, height |
| `flux-2-dev` | `flux-2-dev` | FLUX.2 Dev | inputs: width, height |
| `flux-2-flex` | `flux-2-flex` | FLUX.2 Flex | inputs: aspect_ratio, resolution |
| `flux-2-pro` | `flux-2-pro` | FLUX.2 Pro | inputs: aspect_ratio, resolution |
| `vidu-q2-text-to-image` | `vidu-q2-text-to-image` | Vidu Q2 Image | inputs: aspect_ratio, resolution |
| `bytedance-seedream-v4.5` | `bytedance-seedream-v4.5` | Seedream 4.5 | inputs: aspect_ratio, quality |
| `gpt-image-1.5` | `gpt-image-1.5` | GPT Image 1.5 | inputs: aspect_ratio, quality |
| `gpt-image-2` | `gpt-image-2-text-to-image` | GPT Image 2 | inputs: aspect_ratio, resolution |
| `wan2.6-text-to-image` | `wan2.6-text-to-image` | Wan 2.6 | inputs: width, height |
| `qwen-text-to-image-2512` | `qwen-text-to-image-2512` | Qwen Image 2512 | inputs: width, height |
| `flux-2-klein-4b` | `flux-2-klein-4b` | FLUX.2 Klein 4B | inputs: aspect_ratio |
| `flux-2-klein-9b` | `flux-2-klein-9b` | FLUX.2 Klein 9B | inputs: aspect_ratio |
| `flux-3-klein-text-to-image` | `flux-3-klein-text-to-image` | FLUX 3 Klein Text to Image | inputs: aspect_ratio, resolution, output_format, num_images, seed, enhance_prompt |
| `z-image-base` | `z-image-base` | Z Image Base | inputs: image_url, aspect_ratio, strength |
| `nano-banana-2` | `nano-banana-2` | Nano Banana 2 | inputs: aspect_ratio, resolution, google_search, output_format |
| `nano-banana-2-1` | `nano-banana-2-1` | Nano Banana 2.1 | inputs: aspect_ratio, resolution, output_format |
| `seedream-5.0` | `seedream-5.0` | Seedream 5.0 | inputs: aspect_ratio, quality |
| `bytedance-seedream-v5.0` | `seedream-5.0` | Seedream 5.0 | inputs: aspect_ratio, quality |
| `z-image-p` | `z-image-p` | Z-Image P | inputs: negative_prompt, width, height, seed, flow_shift, batch_size |
| `qwen-image-2.0` | `qwen-image-2.0` | Qwen Image 2.0 | inputs: aspect_ratio |
| `qwen-image-2.0-pro` | `qwen-image-2.0-pro` | Qwen Image 2.0 Pro | inputs: aspect_ratio |
| `flux-2-klein-4b-turbo` | `flux-2-klein-4b-turbo` | Flux 2 Klein 4B Turbo | inputs: aspect_ratio |
| `flux-2-klein-9b-turbo` | `flux-2-klein-9b-turbo` | Flux 2 Klein 9B Turbo | inputs: aspect_ratio |
| `wan2.7-text-to-image` | `wan2.7-text-to-image` | Wan 2.7 Image | inputs: aspect_ratio, thinking_mode |
| `wan2.7-text-to-image-pro` | `wan2.7-text-to-image-pro` | Wan 2.7 Image Pro | inputs: thinking_mode, aspect_ratio |
| `midjourney-v7` | `midjourney-v7` | Midjourney V7 | inputs: image_url, aspect_ratio, stylize, chaos, weird, negative_prompt, seed |
| `midjourney-v8` | `midjourney-v8` | Midjourney V8 | inputs: image_url, aspect_ratio, stylize, chaos, weird, negative_prompt, seed |
| `midjourney-niji` | `midjourney-niji` | Midjourney Niji | inputs: image_url, aspect_ratio, stylize, chaos, weird, negative_prompt, seed |
| `grok-imagine-text-to-image-quality` | `grok-imagine-text-to-image-quality` | Grok Imagine Image Quality | inputs: aspect_ratio |
| `flux-2-klein-4b-text-to-image-lora` | `flux-2-klein-4b-text-to-image-lora` | Flux 2 Klein 4B LoRA | inputs: lora_list, aspect_ratio |
| `flux-2-klein-9b-text-to-image-lora` | `flux-2-klein-9b-text-to-image-lora` | Flux 2 Klein 9B LoRA | inputs: lora_list, aspect_ratio |
| `kling-o3-image` | `kling-o3-image` | Kling O3 Image | inputs: aspect_ratio, resolution, num_images |
| `nano-banana-2-lite` | `nano-banana-2-lite` | Nano Banana 2 Lite | inputs: aspect_ratio |
| `bytedance-seedream-5.0-pro` | `seedream-5.0-pro` | Seedream 5.0 Pro | inputs: aspect_ratio, resolution |
| `qwen3-text-to-image` | `qwen3-text-to-image` | Qwen Image 3.0 | inputs: resolution, aspect_ratio, output_format, prompt_extend, negative_prompt |
| `qwen3-pro-text-to-image` | `qwen3-pro-text-to-image` | Qwen Image 3.0 Pro | inputs: resolution, aspect_ratio, output_format, prompt_extend, negative_prompt |
| `z-image-base-text-to-image-lora` | `z-image-base-text-to-image-lora` | Z-Image Base LoRA | inputs: image_url, loras, aspect_ratio, strength, output_format |
| `z-image-turbo-text-to-image-lora` | `z-image-turbo-text-to-image-lora` | Z-Image Turbo LoRA | inputs: loras, aspect_ratio, output_format |
| `grok-imagine-image-2` | `grok-imagine-image-2` | Grok Imagine Image 2.0 | inputs: aspect_ratio |
| `flux-1-dev-style-lora-inference` | `flux-1-dev-style-lora-inference` | Flux Dev Style LoRA Inference | inputs: lora_url, lora_weight, aspect_ratio |
| `krea-v2-turbo` | `krea-v2-turbo` | Krea 2 Turbo | inputs: image_url, aspect_ratio, resolution, strength, seed |
| `krea-v2-turbo-lora` | `krea-v2-turbo-lora` | Krea 2 Turbo LoRA | inputs: image_url, loras, aspect_ratio, resolution, strength, seed |
| `muse-image-text-to-image` | `muse-image-text-to-image` | Muse Image | inputs: aspect_ratio, output_format |
| `qwen-image-text-to-image-lora` | `qwen-image-text-to-image-lora` | Qwen Image LoRA | inputs: aspect_ratio, loras, output_format |
| `qwen-image-text-to-image-2512-lora` | `qwen-image-text-to-image-2512-lora` | Qwen Image 2512 LoRA | inputs: aspect_ratio, loras, output_format |
| `gpt-image-2.5-flare-text-to-image` | `gpt-image-2.5-flare-text-to-image` | GPT Image 2.5 Flare Text to Image | inputs: aspect_ratio, resolution, quality |
| `gpt-image-2.5-sunburst-text-to-image` | `gpt-image-2.5-sunburst-text-to-image` | GPT Image 2.5 Sunburst Text to Image | inputs: aspect_ratio, resolution, quality |
| `qwen2-1-text-to-image` | `qwen2-1-text-to-image` | Qwen2 1 Text to Image | inputs: aspect_ratio, resolution, background, output_format, enhance_prompt, seed |
| `seedream-5.0-flash` | `seedream-5.0-flash` | Seedream 5.0 Flash | inputs: aspect_ratio, resolution, output_format |
| `ideogram-v4` | `ideogram-v4` | Ideogram 4.0 | inputs: aspect_ratio, resolution |
| `seedream-5.5` | `seedream-5.5` | 5.5 | category=Text to Image; inputs: aspect_ratio, resolution, output_format, background |
| `minimax-h3-image-text-to-image` | `minimax-h3-image-text-to-image` | H3 Image | category=Text to Image; inputs: aspect_ratio, resolution, output_format |
| `minimax-h3-image-highspeed-text-to-image` | `minimax-h3-image-highspeed-text-to-image` | H3 Image Highspeed | category=Text to Image; inputs: aspect_ratio, resolution, output_format |

## Text → Video — 117 models

| id | endpoint | name | notes |
|---|---|---|---|
| `seedance-lite-t2v` | `seedance-lite-t2v` | Seedance 1.0 Lite | inputs: aspect_ratio, duration, resolution |
| `seedance-pro-t2v` | `seedance-pro-t2v` | Seedance 1.0 Pro | inputs: aspect_ratio, duration, resolution |
| `seedance-pro-t2v-fast` | `seedance-pro-t2v-fast` | Seedance 1.0 Pro Fast | inputs: aspect_ratio, duration, resolution |
| `seedance-v1.5-pro-t2v` | `seedance-v1.5-pro-t2v` | Seedance 1.5 Pro | inputs: aspect_ratio, duration, resolution |
| `seedance-v1.5-pro-t2v-fast` | `seedance-v1.5-pro-t2v-fast` | Seedance v1.5 Pro Fast | inputs: aspect_ratio, duration, resolution |
| `seedance-v2.0-t2v` | `seedance-v2.0-t2v` | Seedance 2.0 | inputs: aspect_ratio, duration, quality |
| `seedance-v2.0-extend` | `seedance-v2.0-extend` | Seedance 2.0 Extend | inputs: request_id, images_list, video_files, duration, quality |
| `kling-v2.1-master-t2v` | `kling-v2.1-master-t2v` | Kling 2.1 Master | inputs: aspect_ratio, duration |
| `kling-v2.5-turbo-pro-t2v` | `kling-v2.5-turbo-pro-t2v` | Kling 2.5 Turbo Pro | inputs: aspect_ratio, duration |
| `kling-v2.6-pro-t2v` | `kling-v2.6-pro-t2v` | Kling 2.6 Pro | inputs: aspect_ratio, duration |
| `kling-o1-text-to-video` | `kling-o1-text-to-video` | Kling O1 Pro | inputs: aspect_ratio, duration |
| `kling-v3.0-pro-text-to-video` | `kling-v3.0-pro-text-to-video` | Kling 3.0 Pro | inputs: aspect_ratio, duration |
| `kling-v3.0-standard-text-to-video` | `kling-v3.0-standard-text-to-video` | Kling 3.0 Standard | inputs: aspect_ratio, duration |
| `veo3-text-to-video` | `veo3-text-to-video` | Veo 3 | inputs: aspect_ratio |
| `veo3-fast-text-to-video` | `veo3-fast-text-to-video` | Veo 3 Fast | inputs: aspect_ratio |
| `veo3.1-text-to-video` | `veo3.1-text-to-video` | Veo 3.1 | inputs: aspect_ratio, duration, resolution |
| `veo3.1-fast-text-to-video` | `veo3.1-fast-text-to-video` | Veo 3.1 Fast | inputs: aspect_ratio, duration, resolution |
| `veo3.1-lite-text-to-video` | `veo3.1-lite-text-to-video` | Veo 3.1 Lite | inputs: aspect_ratio, duration, resolution |
| `runway-text-to-video` | `runway-text-to-video` | Runway Gen-3 | inputs: aspect_ratio, duration, resolution |
| `wan2.1-text-to-video` | `wan2.1-text-to-video` | Wan 2.1 | inputs: aspect_ratio, duration, resolution, quality |
| `wan2.2-text-to-video` | `wan2.2-text-to-video` | Wan 2.2 | inputs: aspect_ratio, duration, resolution, quality |
| `wan2.2-5b-fast-t2v` | `wan2.2-5b-fast-t2v` | Wan 2.2 Fast | inputs: aspect_ratio, resolution |
| `wan2.5-text-to-video` | `wan2.5-text-to-video` | Wan 2.5 | inputs: aspect_ratio, duration, resolution |
| `wan2.5-text-to-video-fast` | `wan2.5-text-to-video-fast` | Wan 2.5 Fast | inputs: aspect_ratio, duration, resolution |
| `wan2.6-text-to-video` | `wan2.6-text-to-video` | Wan 2.6 | inputs: shot_type, aspect_ratio, duration, resolution |
| `hunyuan-text-to-video` | `hunyuan-text-to-video` | Hunyuan | inputs: aspect_ratio |
| `hunyuan-fast-text-to-video` | `hunyuan-fast-text-to-video` | Hunyuan Fast | inputs: aspect_ratio |
| `pixverse-v4.5-t2v` | `pixverse-v4.5-t2v` | PixVerse V4.5 | inputs: aspect_ratio, duration, resolution |
| `pixverse-v5-t2v` | `pixverse-v5-t2v` | PixVerse V5 | inputs: aspect_ratio, duration, resolution |
| `pixverse-v5.5-t2v` | `pixverse-v5.5-t2v` | PixVerse V5.5 | inputs: aspect_ratio, duration, resolution |
| `minimax-hailuo-02-standard-t2v` | `minimax-hailuo-02-standard-t2v` | MiniMax Hailuo 02 Standard | inputs: duration, resolution |
| `minimax-hailuo-02-pro-t2v` | `minimax-hailuo-02-pro-t2v` | MiniMax Hailuo 02 Pro | inputs: duration, resolution |
| `minimax-hailuo-2.3-pro-t2v` | `minimax-hailuo-2.3-pro-t2v` | MiniMax Hailuo 2.3 Pro | inputs: resolution |
| `minimax-hailuo-2.3-standard-t2v` | `minimax-hailuo-2.3-standard-t2v` | MiniMax Hailuo 2.3 Standard | inputs: duration |
| `openai-sora` | `openai-sora` | Sora | inputs: aspect_ratio, resolution |
| `openai-sora-2-text-to-video` | `openai-sora-2-text-to-video` | Sora 2 | inputs: aspect_ratio, duration |
| `openai-sora-2-pro-text-to-video` | `openai-sora-2-pro-text-to-video` | Sora 2 Pro | inputs: aspect_ratio, duration, resolution |
| `vidu-v2.0-t2v` | `vidu-v2.0-t2v` | Vidu 2.0 | inputs: aspect_ratio, duration, resolution |
| `ovi-text-to-video` | `ovi-text-to-video` | Ovi | inputs: aspect_ratio |
| `grok-imagine-text-to-video` | `grok-imagine-text-to-video` | Grok Imagine | inputs: aspect_ratio |
| `ltx-2-pro-text-to-video` | `ltx-2-pro-text-to-video` | LTX 2 Pro | inputs: duration |
| `ltx-2-fast-text-to-video` | `ltx-2-fast-text-to-video` | LTX 2 Fast | inputs: duration |
| `ltx-2-19b-text-to-video` | `ltx-2-19b-text-to-video` | LTX 2 19B | inputs: aspect_ratio, duration, resolution |
| `veo3.1-extend-video` | `veo3.1-extend-video` | Veo 3.1 Extend | inputs: request_id |
| `veo3.1-4k-video` | `veo3.1-4k-video` | Veo 3.1 4K | inputs: request_id |
| `seedance-2-t2v` | `seedance-v2.0-t2v` | Seedance 2 T2V | inputs: aspect_ratio, duration, quality |
| `seedance-2-extend` | `seedance-v2.0-extend` | Seedance 2 Extend | inputs: request_id, images_list, video_files, audio_files, aspect_ratio, duration, quality |
| `ltx-2.3-text-to-video` | `ltx-2.3-text-to-video` | LTX 2.3 | inputs: duration, aspect_ratio, resolution, seed |
| `seedance-2-new-t2v` | `seedance-2.0-new-t2v` | Seedance 2 New T2V | inputs: aspect_ratio, quality, duration |
| `grok-imagine-extend` | `grok-imagine-extend` | Grok Imagine Extend | inputs: request_id, extend_times |
| `pixverse-v6-t2v` | `pixverse-v6-t2v` | PixVerse V6 | inputs: aspect_ratio, resolution, duration, generate_audio_switch |
| `wan2.7-text-to-video` | `wan2.7-text-to-video` | Wan2.7 | inputs: audio_url, aspect_ratio, resolution, duration, negative_prompt |
| `seedance-2-t2v-480p` | `seedance-2.0-t2v-480p` | Seedance 2 T2V 480P | inputs: aspect_ratio, duration, quality |
| `seedance-2-text-to-video` | `seedance-2-text-to-video` | Seedance 2 | inputs: aspect_ratio, duration |
| `seedance-2-text-to-video-fast` | `seedance-2-text-to-video-fast` | Seedance 2.0 Fast | inputs: aspect_ratio, duration |
| `seedance-2-vip-text-to-video` | `seedance-2-vip-text-to-video` | Seedance 2 VIP | inputs: aspect_ratio, duration, high_bitrate |
| `seedance-2-vip-text-to-video-fast` | `seedance-2-vip-text-to-video-fast` | Seedance 2 VIP Text to Video Fast | inputs: aspect_ratio, duration, high_bitrate |
| `happy-horse-1-text-to-video-1080p` | `happy-horse-1-text-to-video-1080p` | HappyHorse 1.0 1080P | inputs: aspect_ratio, duration |
| `happy-horse-1-text-to-video-720p` | `happy-horse-1-text-to-video-720p` | HappyHorse 1.0 720P | inputs: aspect_ratio, duration |
| `veo-4-text-to-video` | `veo-4-text-to-video` | Veo 4 | inputs: aspect_ratio, duration |
| `seedance-2-vip-text-to-video-1080p` | `sd-2-vip-text-to-video-1080p` | Seedance 2 VIP Text to Video 1080P | inputs: aspect_ratio, duration |
| `seedance-2-vip-text-to-video-fast-1080p` | `sd-2-vip-text-to-video-fast-1080p` | Seedance 2 VIP Text to Video Fast 1080P | inputs: aspect_ratio, duration |
| `kling-v3.0-4k-text-to-video` | `kling-v3.0-4k-text-to-video` | Kling 3.0 4K | inputs: aspect_ratio, duration |
| `vidu-q3-pro-text-to-video` | `vidu-q3-pro-text-to-video` | Vidu Q3 Pro | inputs: resolution, aspect_ratio, duration, audio |
| `vidu-q3-turbo-text-to-video` | `vidu-q3-turbo-text-to-video` | Vidu Q3 Turbo | inputs: resolution, aspect_ratio, duration, audio |
| `vidu-q2-pro-text-to-video` | `vidu-q2-pro-text-to-video` | Vidu Q2 Pro | inputs: resolution, aspect_ratio, duration, movement_amplitude |
| `vidu-q2-turbo-text-to-video` | `vidu-q2-turbo-text-to-video` | Vidu Q2 Turbo | inputs: resolution, aspect_ratio, duration, movement_amplitude |
| `seedance-2-vip-extend` | `sd-2-vip-extend` | Seedance 2 VIP Extend | inputs: request_id, images_list, video_files, audio_files, aspect_ratio, duration, quality |
| `seedance-2-vip-extend-1080p` | `sd-2-vip-extend-1080p` | Seedance 2 VIP Extend 1080P | inputs: request_id, images_list, video_files, audio_files, aspect_ratio, duration, quality |
| `kling-v3.0-omni-standard-text-to-video` | `kling-v3.0-omni-standard-text-to-video` | Kling 3.0 Omni Standard | inputs: aspect_ratio, duration, generate_audio |
| `kling-v3.0-omni-pro-text-to-video` | `kling-v3.0-omni-pro-text-to-video` | Kling 3.0 Omni Pro | inputs: aspect_ratio, duration, generate_audio |
| `kling-v3.0-omni-4k-text-to-video` | `kling-v3.0-omni-4k-text-to-video` | Kling 3.0 Omni 4K | inputs: aspect_ratio, duration |
| `gemini-omni-text-to-video` | `gemini-omni-text-to-video` | Gemini Omni Flash | inputs: duration, resolution, aspect_ratio, audio_ids, seed, character_ids |
| `kling-v3-turbo-standard-text-to-video` | `kling-v3-turbo-standard-text-to-video` | Kling 3.0 Turbo Standard | inputs: aspect_ratio, duration |
| `kling-v3-turbo-pro-text-to-video` | `kling-v3-turbo-pro-text-to-video` | Kling 3.0 Turbo Pro | inputs: aspect_ratio, duration, duration, seed, high_bitrate, duration, seed, high_bitrate |
| `seedance-2-mini-text-to-video` | `seedance-2-mini-text-to-video` | Seedance 2.0 Mini | inputs: aspect_ratio, resolution, duration, generate_audio, high_bitrate |
| `happy-horse-1.1-text-to-video-1080p` | `happy-horse-1.1-text-to-video-1080p` | HappyHorse 1.1 1080P | inputs: aspect_ratio, duration |
| `happy-horse-1.1-text-to-video-720p` | `happy-horse-1.1-text-to-video-720p` | HappyHorse 1.1 720P | inputs: aspect_ratio, duration |
| `seedance-2-mini-omni-reference` | `seedance-2-mini-omni-reference` | Seedance 2 Mini Omni Reference | inputs: images_list, video_files, audio_files, aspect_ratio, resolution, duration, generate_audio, high_bitrate |
| `seedance-2-vip-text-to-video-4k` | `sd-2-vip-text-to-video-4k` | Seedance 2 VIP Text to Video 4K | inputs: aspect_ratio, duration, duration, high_bitrate |
| `seedance-2-spicy-text-to-video` | `seedance-2-spicy-text-to-video` | Seedance 2 Spicy | inputs: aspect_ratio, duration, high_bitrate |
| `seedance-2-spicy-text-to-video-fast` | `seedance-2-spicy-text-to-video-fast` | Seedance 2 Spicy Text to Video Fast | inputs: aspect_ratio, duration, high_bitrate |
| `seedance-2-mini-spicy-text-to-video` | `seedance-2-mini-spicy-text-to-video` | Seedance 2 Mini Spicy | inputs: aspect_ratio, resolution, duration, generate_audio, high_bitrate |
| `minimax-h3-text-to-video` | `minimax-h3-text-to-video` | MiniMax H3 | inputs: aspect_ratio, resolution, duration |
| `minimax-h3-open-text-to-video` | `minimax-h3-open-text-to-video` | MiniMax H3 Base FL2VA | inputs: aspect_ratio, resolution, duration |
| `flux-3-text-to-video` | `flux-3-text-to-video` | FLUX 3 | inputs: aspect_ratio, resolution, duration, generate_audio |
| `wan3.0-text-to-video` | `wan3.0-text-to-video` | Wan 3.0 | inputs: resolution, aspect_ratio, duration, thinking_mode, enable_audio, seed |
| `wan3.0-spicy-text-to-video` | `wan3.0-spicy-text-to-video` | Wan 3.0 Spicy | inputs: resolution, aspect_ratio, duration, thinking_mode, enable_audio, seed |
| `seedance-2.5-text-to-video-1080p` | `seedance-2.5-text-to-video-1080p` | Seedance 2.5 1080p | inputs: duration, seed, high_bitrate |
| `seedance-2.5-text-to-video-4k` | `seedance-2.5-text-to-video-4k` | Seedance 2.5 4K | inputs: duration, seed, high_bitrate |
| `seedance-2.5-intl-text-to-video` | `seedance-2.5-intl-text-to-video` | Seedance 2.5 Intl | inputs: duration, seed, high_bitrate |
| `seedance-2.5-intl-text-to-video-480p` | `seedance-2.5-intl-text-to-video-480p` | Seedance 2.5 Intl 480p | inputs: duration, seed, high_bitrate |
| `seedance-2.5-spicy-text-to-video-480p` | `seedance-2.5-spicy-text-to-video-480p` | Seedance 2.5 Spicy 480p | inputs: duration, seed, high_bitrate |
| `seedance-2.5-intl-text-to-video-1080p` | `seedance-2.5-intl-text-to-video-1080p` | Seedance 2.5 Intl 1080p | inputs: duration, seed, high_bitrate |
| `seedance-2.5-spicy-text-to-video-1080p` | `seedance-2.5-spicy-text-to-video-1080p` | Seedance 2.5 Spicy 1080p | inputs: duration, seed, high_bitrate |
| `seedance-2.5-intl-text-to-video-4k` | `seedance-2.5-intl-text-to-video-4k` | Seedance 2.5 Intl 4K | inputs: duration, seed, high_bitrate |
| `seedance-2.5-spicy-text-to-video-4k` | `seedance-2.5-spicy-text-to-video-4k` | Seedance 2.5 Spicy 4K | inputs: duration, seed, high_bitrate |
| `minimax-h3-text-to-video-lora` | `minimax-h3-text-to-video-lora` | MiniMax H3 Text to Video LoRA | inputs: aspect_ratio, resolution, duration, seed, loras |
| `ltx-2.5-text-to-video` | `ltx-2.5-text-to-video` | LTX 2.5 | inputs: duration, aspect_ratio, resolution, seed |
| `wan3.0-prime-text-to-video` | `wan3.0-prime-text-to-video` | Wan 3.0 Prime | inputs: resolution, aspect_ratio, duration, thinking_mode, enable_audio, seed |
| `flux-3-text-to-video-draft` | `flux-3-text-to-video-draft` | FLUX 3 Text to Video Draft | inputs: aspect_ratio, duration, generate_audio |
| `gemini-omni-flash-1-1-text-to-video` | `gemini-omni-flash-1-1-text-to-video` | Gemini Omni 1.1 Flash | inputs: image_urls, video_url, trim_start, trim_end, audio_ids, character_ids, duration, aspect_ratio, resolution, seed |
| `gemini-omni-flash-1-2-text-to-video` | `gemini-omni-flash-1-2-text-to-video` | Gemini Omni 1.2 Flash | inputs: duration, aspect_ratio, resolution, seed |
| `openai-sora-2-pro-storyboard` | `openai-sora-2-pro-storyboard` | OpenAI Sora 2 Pro Storyboard | imageField=images_list; inputs: shots, duration, images_list, aspect_ratio |
| `happy-horse-1-text-to-video` | `happy-horse-1-text-to-video` | Happy Horse 1 Text to Video | inputs: resolution, aspect_ratio, duration |
| `happy-horse-1.1-text-to-video` | `happy-horse-1.1-text-to-video` | Happy Horse 1.1 Text to Video | inputs: resolution, aspect_ratio, duration |
| `minimax-h3-max-text-to-video` | `minimax-h3-max-text-to-video` | MiniMax H3 Max Text to Video | inputs: aspect_ratio, resolution, duration, prompt_expansion_mode |
| `minimax-h3-max-turbo-text-to-video` | `minimax-h3-max-turbo-text-to-video` | MiniMax H3 Max Turbo Text to Video | inputs: aspect_ratio, resolution, duration, prompt_expansion_mode |
| `seedance-2-mini-spicy-omni-reference` | `seedance-2-mini-spicy-omni-reference` | Seedance 2 Mini Spicy Omni Reference | imageField=images_list; category={; inputs: images_list, video_files, audio_files, aspect_ratio, resolution, duration, generate_audio, high_bitrate, items, items |
| `minimax-h3-max-spicy-text-to-video` | `minimax-h3-max-spicy-text-to-video` | MiniMax H3 Max Spicy Text to Video | inputs: aspect_ratio, resolution, duration |
| `minimax-h3-max-turbo-spicy-text-to-video` | `minimax-h3-max-turbo-spicy-text-to-video` | MiniMax H3 Max Turbo Spicy Text to Video | inputs: aspect_ratio, resolution, duration |
| `ltx-2.5-fast-text-to-video` | `ltx-2.5-fast-text-to-video` | LTX 2.5 Fast | inputs: resolution, fps, duration, aspect_ratio, seed |
| `ltx-2.5-pro-text-to-video` | `ltx-2.5-pro-text-to-video` | LTX 2.5 Pro | inputs: resolution, fps, duration, aspect_ratio, seed |
| `minimax-h3-text-to-video-spicy` | `minimax-h3-text-to-video-spicy` | MiniMax H3 Spicy Text to Video | category=Text to Video; inputs: aspect_ratio, resolution, duration, aigc_watermark |
| `seedance-2.5-flash-text-to-video` | `seedance-2.5-flash-text-to-video` | Text to Video | category=Text to Video; inputs: aspect_ratio, duration, resolution, generate_audio, seed |
| `seedance-2.5-flash-spicy-text-to-video` | `seedance-2.5-flash-spicy-text-to-video` | Spicy Text to Video | category=Text to Video; inputs: aspect_ratio, duration, resolution, generate_audio, seed |
| `seedance-2.5-flash-intl-text-to-video` | `seedance-2.5-flash-intl-text-to-video` | Intl Text to Video | category=Text to Video; inputs: aspect_ratio, duration, resolution, generate_audio, seed |

## Image → Image (edit / reference) — 93 models

| id | endpoint | name | notes |
|---|---|---|---|
| `ai-image-upscaler` | `ai-image-upscale` | AI Image Upscaler | imageField=image_url |
| `ai-image-face-swap` | `ai-image-face-swap` | AI Image Face Swap | imageField=image_url; inputs: target_index |
| `ai-dress-change` | `ai-dress-change` | AI Dress Change | imageField=model_image_url |
| `ai-background-remover` | `ai-background-remover` | AI Background Remover | imageField=image_url |
| `ai-image-extension` | `ai-image-extension` | AI Image Extension | imageField=image_url |
| `ai-product-shot` | `ai-product-shot` | AI Product Shot | imageField=image_url; inputs: scene_description |
| `ai-skin-enhancer` | `ai-skin-enhancer` | AI Skin Enhancer | imageField=image_url |
| `ai-color-photo` | `ai-color-photo` | AI Color Photo | imageField=image_url |
| `flux-kontext-dev-i2i` | `flux-kontext-dev-i2i` | Flux Kontext Dev I2I | imageField=images_list; inputs: aspect_ratio, num_images |
| `ai-product-photography` | `ai-product-photography` | AI Product Photography | imageField=person_image_url |
| `ai-ghibli-style` | `ai-ghibli-style` | AI Ghibli Style | imageField=image_url |
| `ai-object-eraser` | `ai-object-eraser` | AI Object Eraser | imageField=image_url |
| `flux-kontext-pro-i2i` | `flux-kontext-pro-i2i` | Flux Kontext Pro I2I | imageField=images_list; inputs: aspect_ratio |
| `flux-kontext-max-i2i` | `flux-kontext-max-i2i` | Flux Kontext Max I2I | imageField=images_list; inputs: aspect_ratio |
| `gpt4o-image-to-image` | `gpt4o-image-to-image` | GPT-4o Image To Image | imageField=images_list; inputs: aspect_ratio, num_images |
| `gpt4o-edit` | `gpt4o-edit` | GPT-4o Mask Edit | imageField=image_url; inputs: aspect_ratio, num_images |
| `bytedance-seededit-v3` | `bytedance-seededit-image` | SeedEdit 3.0 | imageField=image_url |
| `minimax-image-01-subject-reference` | `minimax-01-subject-reference` | MiniMax Image 01 Subject Reference | imageField=image_url; inputs: aspect_ratio, num_images |
| `ideogram-character` | `ideogram-character` | Ideogram 3.0 Character Reference | imageField=image_url; inputs: render_speed, style, aspect_ratio, num_images |
| `flux-pulid` | `flux-pulid` | Flux Pulid | imageField=image_url; inputs: aspect_ratio |
| `qwen-image-edit` | `qwen-image-edit` | Qwen Image Edit | imageField=image_url; inputs: aspect_ratio |
| `image-effects` | `image-effects` | Image Effects | imageField=image_url; inputs: name |
| `nano-banana-edit` | `nano-banana-edit` | Nano Banana | imageField=images_list; inputs: aspect_ratio |
| `ideogram-v3-reframe` | `ideogram-v3-reframe` | Ideogram 3.0 Reframe | imageField=image_url; inputs: aspect_ratio, render_speed, style, num_images |
| `bytedance-seedream-edit-v4` | `bytedance-seedream-edit-v4` | Bytedance Seedream Edit v4 | imageField=images_list; inputs: aspect_ratio, resolution, num_images |
| `nano-banana-effects` | `nano-banana-effects` | Nano Banana Effects | imageField=image_url; inputs: name, aspect_ratio |
| `flux-kontext-effects` | `flux-kontext-effects` | Flux Kontext Effects | imageField=image_url; inputs: name |
| `flux-redux` | `flux-redux` | Flux Redux | imageField=image_url; inputs: aspect_ratio, num_images |
| `qwen-image-edit-plus` | `qwen-image-edit-plus` | Qwen Image Edit Plus | imageField=images_list; inputs: width, height |
| `wan2.5-image-edit` | `wan2.5-image-edit` | Wan2.5 Image Edit | imageField=images_list; inputs: width, height |
| `reve-image-edit` | `reve-image-edit` | Reve Image Edit | imageField=image_url |
| `topaz-image-upscale` | `topaz-image-upscale` | Topaz Image Upscale | imageField=image_url; inputs: upscale_factor |
| `seedvr2-image-upscale` | `seedvr2-image-upscale` | Seedvr2 Image Upscale | imageField=image_url; inputs: resolution |
| `qwen-image-edit-plus-lora` | `qwen-image-edit-plus-lora` | Qwen Image Edit Plus Lora | imageField=images_list; inputs: rotate_right_left, move_forward, vertical_angle, wide_angle_lens, width, height |
| `nano-banana-pro-edit` | `nano-banana-pro-edit` | Nano Banana Pro | imageField=images_list; inputs: aspect_ratio, resolution |
| `image-passthrough` | `image-passthrough` | Image Passthrough | imageField=image_url; inputs: make_input |
| `kling-o1-edit-image` | `kling-o1-edit-image` | Kling O1 Edit Image | imageField=images_list; inputs: aspect_ratio, resolution |
| `flux-2-dev-edit` | `flux-2-dev-edit` | Flux 2 Dev Edit | imageField=images_list; inputs: width, height |
| `flux-2-flex-edit` | `flux-2-flex-edit` | Flux 2 Flex Edit | imageField=images_list; inputs: aspect_ratio, resolution |
| `flux-2-pro-edit` | `flux-2-pro-edit` | Flux 2 Pro Edit | imageField=images_list; inputs: aspect_ratio, resolution |
| `vidu-q2-reference-to-image` | `vidu-q2-reference-to-image` | Vidu Q2 Reference | imageField=images_list; inputs: aspect_ratio, resolution |
| `bytedance-seedream-v4.5-edit` | `bytedance-seedream-v4.5-edit` | Bytedance Seedream v4.5 Edit | imageField=images_list; inputs: aspect_ratio, quality |
| `qwen-image-edit-2511` | `qwen-image-edit-2511` | Qwen Image Edit 2511 | imageField=images_list; inputs: width, height |
| `wan2.6-image-edit` | `wan2.6-image-edit` | Wan2.6 Image Edit | imageField=images_list |
| `qwen-text-to-image-2512` | `qwen-text-to-image-2512` | Qwen Text To Image 2512 | inputs: width, height |
| `gpt-image-2-edit` | `gpt-image-2-image-to-image` | GPT Image 2 Edit | imageField=images_list; inputs: aspect_ratio, resolution |
| `gpt-image-1.5-edit` | `gpt-image-1.5-edit` | GPT Image 1.5 Edit | imageField=images_list; inputs: aspect_ratio, quality |
| `grok-imagine-image-to-image` | `grok-imagine-image-to-image` | Grok Imagine Image To Image | imageField=image_url |
| `Api Node` | `Api Node` | Api Node | imageField=image_url; inputs: model_url, api_key |
| `flux-2-klein-4b-edit` | `flux-2-klein-4b-edit` | Flux 2 Klein 4b Edit | imageField=images_list; inputs: aspect_ratio |
| `flux-2-klein-9b-edit` | `flux-2-klein-9b-edit` | Flux 2 Klein 9b Edit | imageField=images_list; inputs: aspect_ratio |
| `flux-3-klein-edit-image` | `flux-3-klein-edit-image` | FLUX 3 Klein Image Edit | imageField=images_list; inputs: images_list, aspect_ratio, resolution, output_format, num_images, seed, enhance_prompt |
| `add-image-watermark` | `add-image-watermark` | Add Image Watermark | imageField=image_url; inputs: position, opacity, scale |
| `nano-banana-2-edit` | `nano-banana-2-edit` | Nano Banana 2 | imageField=images_list; inputs: aspect_ratio, resolution, google_search, output_format |
| `nano-banana-2-1-edit` | `nano-banana-2-1-edit` | Nano Banana 2.1 Edit | imageField=images_list; inputs: aspect_ratio, resolution, output_format |
| `seedream-5.0-edit` | `seedream-5.0-edit` | Seedream 5.0 Edit | imageField=images_list; inputs: aspect_ratio, quality |
| `bytedance-seedream-v4-edit` | `bytedance-seedream-edit-v4` | Seedream 4 Edit | imageField=images_list; inputs: images_list, aspect_ratio, resolution, num_images |
| `bytedance-seedream-v5.0-edit` | `seedream-5.0-edit` | Seedream 5.0 Edit | imageField=images_list; inputs: images_list, aspect_ratio, quality |
| `qwen-image-2.0-edit` | `qwen-image-2.0-edit` | Qwen Image 2.0 | imageField=images_list; inputs: images_list, aspect_ratio |
| `qwen-image-2.0-pro-edit` | `qwen-image-2.0-pro-edit` | Qwen Image 2.0 Pro | imageField=images_list; inputs: images_list, aspect_ratio |
| `flux-2-klein-4b-turbo-edit` | `flux-2-klein-4b-turbo-edit` | Flux 2 Klein 4B Turbo Edit | imageField=images_list; inputs: images_list, aspect_ratio |
| `flux-2-klein-9b-turbo-edit` | `flux-2-klein-9b-turbo-edit` | Flux 2 Klein 9B Turbo Edit | imageField=images_list; inputs: images_list, aspect_ratio |
| `portrait-stylist` | `portrait-stylist` | AI Portrait Stylist | inputs: image_url, name, aspect_ratio |
| `seedance-2-character` | `seedance-2-character` | Seedance 2 Character | imageField=images_list; inputs: images_list, character_name |
| `wan2.7-image-edit` | `wan2.7-image-edit` | Wan 2.7 Image Edit | imageField=images_list; inputs: images_list, aspect_ratio |
| `wan2.7-image-edit-pro` | `wan2.7-image-edit-pro` | Wan 2.7 Image Edit Pro | imageField=images_list; inputs: images_list, aspect_ratio |
| `flux-2-klein-4b-edit-lora` | `flux-2-klein-4b-edit-lora` | Flux 2 Klein 4B Edit LoRA | imageField=images_list; inputs: images_list, lora_list, aspect_ratio |
| `flux-2-klein-9b-edit-lora` | `flux-2-klein-9b-edit-lora` | Flux 2 Klein 9B Edit LoRA | imageField=images_list; inputs: images_list, lora_list, aspect_ratio |
| `kling-o3-image-edit` | `kling-o3-image-edit` | Kling O3 Image Edit | imageField=images_list; inputs: images_list, aspect_ratio, resolution, num_images |
| `nano-banana-2-lite-edit` | `nano-banana-2-lite-edit` | Nano Banana 2 Lite | imageField=images_list; inputs: images_list, aspect_ratio |
| `bytedance-seedream-5.0-pro-edit` | `seedream-5.0-pro-edit` | Seedream 5.0 Pro | imageField=images_list; inputs: images_list, aspect_ratio, resolution |
| `qwen3-image-to-image` | `qwen3-image-to-image` | Qwen 3 Image to Image | imageField=images_list; inputs: images_list, resolution, aspect_ratio, output_format, prompt_extend, negative_prompt |
| `qwen3-pro-image-to-image` | `qwen3-pro-image-to-image` | Qwen 3 Pro Image to Image | imageField=images_list; inputs: images_list, resolution, aspect_ratio, output_format, prompt_extend, negative_prompt |
| `z-image-turbo-image-to-image-lora` | `z-image-turbo-image-to-image-lora` | Z-Image Turbo Image to Image LoRA | imageField=image_url; inputs: image_url, loras, aspect_ratio, strength, output_format |
| `qwen-image-edit-2511-lora` | `qwen-image-edit-2511-lora` | Qwen Image Edit 2511 LoRA | imageField=images_list; inputs: images_list, aspect_ratio, loras, output_format |
| `qwen-image-edit-lora` | `qwen-image-edit-lora` | Qwen Image Edit LoRA | imageField=image_url; inputs: image_url, aspect_ratio, loras, output_format |
| `face-expression-change` | `face-expression-change` | Face Expression Change | imageField=images_list; inputs: images_list, aspect_ratio, rotate_right_left, move_forward, vertical_angle, wide_angle_lens, output_format |
| `muse-image-edit` | `muse-image-edit` | Muse Image Edit | imageField=images_list; inputs: images_list, aspect_ratio, output_format |
| `gemini-omni-character` | `gemini-omni-character` | Gemini Omni Character | imageField=images_list; inputs: descriptions, images_list, character_name, audio_ids |
| `bytedance-seedream-5.0-pro-layer` | `bytedance-seedream-5.0-pro-layer` | Bytedance Seedream 5.0 Pro Layer | imageField=image_url; inputs: image_url, resolution, output_format |
| `grok-imagine-image-2-edit` | `grok-imagine-image-2-edit` | Grok Imagine Image 2 Edit | inputs: request_id, mask_indexs |
| `gpt-image-2.5-flare-image-to-image` | `gpt-image-2.5-flare-image-to-image` | GPT Image 2.5 Flare Image to Image | imageField=images_list; inputs: images_list, aspect_ratio, resolution, quality |
| `gpt-image-2.5-sunburst-image-to-image` | `gpt-image-2.5-sunburst-image-to-image` | GPT Image 2.5 Sunburst Image to Image | imageField=images_list; inputs: images_list, aspect_ratio, resolution, quality |
| `topaz-upscale-image-creative` | `topaz-upscale-image-creative` | Topaz Upscale Image Creative | imageField=image_url; inputs: image_url, model, upscale_factor, autoprompt, creativity, color_preservation, crop_to_fill, output_format |
| `topaz-upscale-image-generative` | `topaz-upscale-image-generative` | Topaz Upscale Image Generative | imageField=image_url; inputs: image_url, model, upscale_factor, crop_to_fill, output_format, subject_detection, face_enhancement, face_enhancement_strength, face_enhancement_creativity, enhancement_strength, creativity, texture, autoprompt, sharpen, denoise, detail |
| `topaz-upscale-image-precision` | `topaz-upscale-image-precision` | Topaz Upscale Image Precision | imageField=image_url; inputs: image_url, model, upscale_factor, output_format, crop_to_fill, subject_detection, face_enhancement, face_enhancement_creativity, face_enhancement_strength, sharpen, denoise, fix_compression, strength |
| `qwen2-1-image-to-image` | `qwen2-1-image-to-image` | Qwen2 1 Image to Image | imageField=images_list; inputs: images_list, mask_url, aspect_ratio, resolution, background, output_format, enhance_prompt, seed |
| `seedream-5.0-flash-edit` | `seedream-5.0-flash-edit` | Seedream 5.0 Flash Edit | imageField=images_list; inputs: images_list, aspect_ratio, resolution, output_format |
| `seedream-5.0-flash-layerize` | `seedream-5.0-flash-layerize` | Seedream 5.0 Flash Layerize | imageField=image_url; category={; inputs: image_url, resolution, output_format, items, items, items |
| `seedream-5.5-edit` | `seedream-5.5-edit` | 5.5 Edit | category=Image to Image; inputs: images_list, aspect_ratio, resolution, output_format, background |
| `seedream-5.5-layer` | `seedream-5.5-layer` | 5.5 Layer Decomposition | category=Image to Image; inputs: image_url, resolution, max_images, output_format |
| `minimax-h3-image-edit` | `minimax-h3-image-edit` | H3 Image Edit | category=Image to Image; inputs: images_list, resolution, output_format |
| `minimax-h3-image-highspeed-edit` | `minimax-h3-image-highspeed-edit` | H3 Image Highspeed Edit | category=Image to Image; inputs: images_list, resolution, output_format |

## Image → Video — 193 models

| id | endpoint | name | notes |
|---|---|---|---|
| `ai-video-effects` | `generate_wan_ai_effects` | AI Video Effects | imageField=image_url; inputs: name, aspect_ratio, resolution, quality, duration |
| `motion-controls` | `generate_wan_ai_effects` | Motion Controls | imageField=image_url; inputs: name, aspect_ratio, resolution, quality, duration |
| `vfx` | `generate_wan_ai_effects` | VFX | imageField=image_url; inputs: name, aspect_ratio, resolution, quality, duration |
| `veo3-image-to-video` | `veo3-image-to-video` | Veo 3 | imageField=images_list; inputs: aspect_ratio |
| `veo3-fast-image-to-video` | `veo3-fast-image-to-video` | Veo 3 Fast | imageField=images_list; inputs: aspect_ratio |
| `runway-image-to-video` | `runway-image-to-video` | Runway Image To Video | imageField=image_url; inputs: aspect_ratio, resolution, duration |
| `wan2.1-image-to-video` | `wan2.1-image-to-video` | Wan2.1 Image To Video | imageField=image_url; inputs: aspect_ratio, resolution, quality, duration |
| `hunyuan-image-to-video` | `hunyuan-image-to-video` | Hunyuan Image To Video | imageField=image_url; inputs: aspect_ratio |
| `kling-v2.1-master-i2v` | `kling-v2.1-master-i2v` | Kling v2.1 Master I2V | imageField=image_url; inputs: aspect_ratio, duration |
| `kling-v2.1-standard-i2v` | `kling-v2.1-standard-i2v` | Kling 2.1 Standard | imageField=image_url; inputs: aspect_ratio, duration |
| `kling-v2.1-pro-i2v` | `kling-v2.1-pro-i2v` | Kling 2.1 Pro | imageField=image_url; lastImageField=last_image; inputs: aspect_ratio, duration |
| `wan2.2-image-to-video` | `wan2.2-image-to-video` | Wan2.2 Image To Video | imageField=image_url; lastImageField=last_image; inputs: aspect_ratio, resolution, quality, duration |
| `runway-act-two-i2v` | `runway-act-two-i2v` | Runway Act-Two | imageField=image_url; inputs: aspect_ratio |
| `pixverse-v4.5-i2v` | `pixverse-v4.5-i2v` | Pixverse v4.5 I2V | imageField=images_list; lastImageField=images_list; inputs: aspect_ratio, resolution, duration |
| `vidu-v2.0-i2v` | `vidu-v2.0-i2v` | Vidu v2.0 I2V | imageField=images_list; lastImageField=images_list; inputs: aspect_ratio, resolution, duration |
| `vidu-q1-reference` | `vidu-q1-reference` | Vidu Q1 Reference | imageField=images_list; inputs: aspect_ratio |
| `minimax-hailuo-02-standard-i2v` | `minimax-hailuo-02-standard-i2v` | Minimax Hailuo 02 Standard I2V | imageField=image_url; lastImageField=end_image_url; inputs: duration, resolution |
| `minimax-hailuo-02-pro-i2v` | `minimax-hailuo-02-pro-i2v` | Minimax Hailuo 02 Pro I2V | imageField=image_url; lastImageField=end_image_url; inputs: duration, resolution |
| `video-effects` | `video-effects` | Video Effects | imageField=image_url; inputs: name |
| `seedance-lite-i2v` | `seedance-lite-i2v` | Seedance Lite I2V | imageField=image_url; lastImageField=last_image; inputs: resolution, duration, camera_fixed |
| `seedance-pro-i2v` | `seedance-pro-i2v` | Seedance Pro I2V | imageField=image_url; inputs: resolution, duration, camera_fixed |
| `pixverse-v5-i2v` | `pixverse-v5-i2v` | Pixverse v5 I2V | imageField=images_list; lastImageField=images_list; inputs: aspect_ratio, resolution, duration |
| `seedance-lite-reference-video` | `seedance-lite-reference-to-video` | Seedance 1.0 Lite Reference | imageField=images_list; inputs: resolution, duration |
| `wan2.1-reference-video` | `wan2.1-reference-video` | Wan2.1 Reference Video | imageField=images_list; inputs: resolution, aspect_ratio, duration |
| `kling-v2.5-turbo-pro-i2v` | `kling-v2.5-turbo-pro-i2v` | Kling v2.5 Turbo Pro I2V | imageField=image_url; inputs: duration |
| `wan2.5-image-to-video` | `wan2.5-image-to-video` | Wan2.5 Image To Video | imageField=image_url; inputs: resolution, duration |
| `wan2.5-image-to-video-fast` | `wan2.5-image-to-video-fast` | Wan2.5 Image To Video Fast | imageField=image_url; inputs: resolution, duration |
| `openai-sora-2-image-to-video` | `openai-sora-2-image-to-video` | Sora 2 | imageField=images_list; inputs: aspect_ratio, duration |
| `ovi-image-to-video` | `ovi-image-to-video` | Ovi Image To Video | imageField=image_url |
| `openai-sora-2-pro-image-to-video` | `openai-sora-2-pro-image-to-video` | Sora 2 Pro | imageField=images_list; inputs: aspect_ratio, duration, resolution |
| `leonardoai-motion-2.0` | `leonardoai-motion-2.0` | Motion 2.0 | imageField=image_url; inputs: aspect_ratio |
| `veo3.1-image-to-video` | `veo3.1-image-to-video` | Veo 3.1 | imageField=image_url; lastImageField=last_image; inputs: aspect_ratio, duration, resolution |
| `veo3.1-fast-image-to-video` | `veo3.1-fast-image-to-video` | Veo 3.1 Fast | imageField=image_url; lastImageField=last_image; inputs: aspect_ratio, duration, resolution |
| `veo3.1-lite-image-to-video` | `veo3.1-lite-image-to-video` | Veo 3.1 Lite | imageField=image_url; lastImageField=last_image; inputs: aspect_ratio, duration, resolution |
| `veo3.1-reference-to-video` | `veo3.1-reference-to-video` | Veo 3.1 Reference | imageField=images_list; inputs: resolution, duration, generate_audio |
| `seedance-pro-i2v-fast` | `seedance-pro-i2v-fast` | Seedance Pro I2V Fast | imageField=image_url; inputs: resolution, duration, camera_fixed |
| `ltx-2-pro-image-to-video` | `ltx-2-pro-image-to-video` | LTX 2 Pro | imageField=image_url; inputs: duration |
| `ltx-2-fast-image-to-video` | `ltx-2-fast-image-to-video` | LTX 2 Fast | imageField=image_url; inputs: duration |
| `vidu-q2-reference` | `vidu-q2-reference` | Vidu Q2 Reference | imageField=images_list; inputs: resolution, aspect_ratio, duration, movement_amplitude |
| `vidu-q2-turbo-start-end-video` | `vidu-q2-turbo-start-end-video` | Vidu Q2 Turbo Start End | imageField=image_url; lastImageField=last_image; inputs: resolution, duration, bgm, movement_amplitude |
| `vidu-q2-pro-start-end-video` | `vidu-q2-pro-start-end-video` | Vidu Q2 Pro Start End | imageField=image_url; lastImageField=last_image; inputs: resolution, duration, bgm, movement_amplitude |
| `minimax-hailuo-2.3-pro-i2v` | `minimax-hailuo-2.3-pro-i2v` | Minimax Hailuo 2.3 Pro I2V | imageField=image_url; inputs: resolution |
| `minimax-hailuo-2.3-standard-i2v` | `minimax-hailuo-2.3-standard-i2v` | Minimax Hailuo 2.3 Standard I2V | imageField=image_url; inputs: duration |
| `minimax-hailuo-2.3-fast` | `minimax-hailuo-2.3-fast` | MiniMax Hailuo 2.3 Fast | imageField=image_url; inputs: duration, go_fast |
| `kling-v2.5-turbo-std-i2v` | `kling-v2.5-turbo-std-i2v` | Kling 2.5 Turbo Standard | imageField=image_url; inputs: duration |
| `grok-imagine-image-to-video` | `grok-imagine-image-to-video` | Grok Imagine Image To Video | imageField=images_list; inputs: aspect_ratio, mode |
| `kling-o1-image-to-video` | `kling-o1-image-to-video` | Kling O1 Pro | imageField=image_url; lastImageField=last_image; inputs: aspect_ratio, duration |
| `kling-o1-reference-to-video` | `kling-o1-reference-to-video` | Kling O1 Pro Reference | imageField=images_list; videoField=video_url; inputs: images_list, aspect_ratio, duration |
| `kling-v2.6-pro-i2v` | `kling-v2.6-pro-i2v` | Kling v2.6 Pro I2V | imageField=image_url; inputs: duration |
| `pixverse-v5.5-i2v` | `pixverse-v5.5-i2v` | Pixverse v5.5 I2V | imageField=images_list; lastImageField=images_list; inputs: aspect_ratio, resolution, duration |
| `wan2.2-spicy-image-to-video` | `wan2.2-spicy-image-to-video` | Wan2.2 Spicy Image To Video | imageField=image_url; inputs: resolution, duration |
| `wan2.6-image-to-video` | `wan2.6-image-to-video` | Wan2.6 Image To Video | imageField=image_url; inputs: resolution, duration, shot_type |
| `kling-o1-standard-image-to-video` | `kling-o1-standard-image-to-video` | Kling O1 Standard | imageField=image_url; lastImageField=last_image; inputs: duration |
| `kling-o1-standard-reference-to-video` | `kling-o1-standard-reference-to-video` | Kling O1 Standard Reference | imageField=images_list; inputs: images_list, aspect_ratio, duration |
| `seedance-v1.5-pro-i2v` | `seedance-v1.5-pro-i2v` | Seedance v1.5 Pro I2V | imageField=image_url; lastImageField=last_image; inputs: aspect_ratio, resolution, duration, generate_audio, camera_fixed |
| `seedance-v1.5-pro-i2v-fast` | `seedance-v1.5-pro-i2v-fast` | Seedance v1.5 Pro I2V Fast | imageField=image_url; lastImageField=last_image; inputs: aspect_ratio, resolution, duration, generate_audio, camera_fixed |
| `ltx-2-19b-image-to-video` | `ltx-2-19b-image-to-video` | LTX 2 19B | imageField=image_url; inputs: resolution, duration |
| `kling-v3.0-omni-standard-image-to-video` | `kling-v3.0-omni-standard-image-to-video` | Kling v3.0 Omni Standard Image To Video | imageField=images_list; inputs: aspect_ratio, duration, generate_audio |
| `kling-v3.0-omni-pro-image-to-video` | `kling-v3.0-omni-pro-image-to-video` | Kling v3.0 Omni Pro Image To Video | imageField=images_list; inputs: aspect_ratio, duration, generate_audio |
| `kling-v3.0-omni-4k-image-to-video` | `kling-v3.0-omni-4k-image-to-video` | Kling v3.0 Omni 4K Image To Video | imageField=images_list; inputs: aspect_ratio, duration |
| `kling-v3.0-pro-image-to-video` | `kling-v3.0-pro-image-to-video` | Kling v3.0 Pro Image To Video | imageField=image_url; lastImageField=last_image; inputs: duration |
| `kling-v3.0-standard-image-to-video` | `kling-v3.0-standard-image-to-video` | Kling v3.0 Standard Image To Video | imageField=image_url; lastImageField=last_image; inputs: duration |
| `seedance-v2.0-i2v` | `seedance-v2.0-i2v` | Seedance 2.0 I2V | imageField=images_list; inputs: aspect_ratio, duration, quality |
| `seedance-2-i2v` | `seedance-v2.0-i2v` | Seedance 2 I2V | imageField=images_list; inputs: images_list, aspect_ratio, duration, quality |
| `ltx-2.3-image-to-video` | `ltx-2.3-image-to-video` | LTX 2.3 | imageField=image_url; inputs: image_url, duration, resolution, seed |
| `seedance-2-new-first-last` | `seedance-2.0-new-first-last` | Seedance 2 New First Last | imageField=images_list; inputs: images_list, aspect_ratio, quality, duration |
| `seedance-2-omni-reference` | `seedance-2.0-omni-reference` | Seedance 2 Omni Reference | imageField=images_list; inputs: images_list, video_files, audio_files, aspect_ratio, quality, duration |
| `pixverse-v6-i2v` | `pixverse-v6-i2v` | Pixverse v6 I2V | imageField=images_list; inputs: images_list, resolution, duration, thinking_type, generate_audio_switch |
| `pixverse-v6-transition` | `pixverse-v6-transition` | PixVerse V6 Transition | imageField=image_url; lastImageField=last_image; inputs: image_url, last_image, aspect_ratio, resolution, duration, thinking_type, style, negative_prompt, generate_audio_switch |
| `wan2.7-image-to-video` | `wan2.7-image-to-video` | Wan2.7 | imageField=image_url; lastImageField=last_image; inputs: image_url, last_image, audio_url, resolution, duration, negative_prompt |
| `wan2.7-reference-to-video` | `wan2.7-reference-to-video` | Wan 2.7 Reference | imageField=images_list; inputs: images_list, videos_list, image_url, aspect_ratio, resolution, duration, negative_prompt |
| `seedance-2-i2v-480p` | `seedance-2.0-i2v-480p` | Seedance 2 I2V 480P | imageField=images_list; inputs: images_list, aspect_ratio, duration, quality |
| `seedance-2-omni-reference-480p` | `seedance-2.0-omni-reference-480p` | Seedance 2 Omni Reference 480P | imageField=images_list; inputs: images_list, video_files, audio_files, aspect_ratio, quality, duration |
| `seedance-2-image-to-video` | `seedance-2-image-to-video` | Seedance 2 | imageField=images_list; inputs: images_list, aspect_ratio, duration |
| `seedance-2-image-to-video-fast` | `seedance-2-image-to-video-fast` | Seedance 2 Image to Video Fast | imageField=images_list; inputs: images_list, aspect_ratio, duration |
| `seedance-2-first-last-frame` | `seedance-2-first-last-frame` | Seedance 2 First Last Frame | imageField=images_list; inputs: images_list, aspect_ratio, duration |
| `seedance-2-first-last-frame-fast` | `seedance-2-first-last-frame-fast` | Seedance 2 First Last Frame Fast | imageField=images_list; lastImageField=images_list; inputs: images_list, aspect_ratio, duration |
| `seedance-2-omni-reference-no-video` | `seedance-2-omni-reference-no-video` | Seedance 2 Omni Reference No Video | imageField=images_list; inputs: images_list, audio_files, aspect_ratio, duration |
| `seedance-2-omni-reference-no-video-fast` | `seedance-2-omni-reference-no-video-fast` | Seedance 2 Omni Reference No Video Fast | imageField=images_list; inputs: images_list, audio_files, aspect_ratio, duration |
| `seedance-2-vip-image-to-video` | `seedance-2-vip-image-to-video` | Seedance 2 VIP | imageField=images_list; inputs: images_list, aspect_ratio, duration, high_bitrate |
| `seedance-2-vip-image-to-video-fast` | `seedance-2-vip-image-to-video-fast` | Seedance 2 VIP Image to Video Fast | imageField=images_list; inputs: images_list, aspect_ratio, duration, high_bitrate |
| `seedance-2-vip-first-last-frame` | `seedance-2-vip-first-last-frame` | Seedance 2 VIP First Last Frame | imageField=images_list; lastImageField=images_list; inputs: images_list, aspect_ratio, duration, high_bitrate |
| `seedance-2-vip-first-last-frame-fast` | `seedance-2-vip-first-last-frame-fast` | Seedance 2 VIP First Last Frame Fast | imageField=images_list; lastImageField=images_list; inputs: images_list, aspect_ratio, duration, high_bitrate |
| `seedance-2-vip-omni-reference` | `seedance-2-vip-omni-reference` | Seedance 2 VIP Omni Reference | imageField=images_list; inputs: images_list, video_files, audio_files, aspect_ratio, duration |
| `seedance-2-vip-omni-reference-fast` | `seedance-2-vip-omni-reference-fast` | Seedance 2 VIP Omni Reference Fast | imageField=images_list; inputs: images_list, video_files, audio_files, aspect_ratio, duration |
| `happy-horse-1-image-to-video-1080p` | `happy-horse-1-image-to-video-1080p` | Happy Horse 1 Image to Video 1080P | imageField=images_list; inputs: images_list, aspect_ratio, duration |
| `happy-horse-1-image-to-video-720p` | `happy-horse-1-image-to-video-720p` | Happy Horse 1 Image to Video 720P | imageField=images_list; inputs: images_list, aspect_ratio, duration |
| `veo-4-image-to-video` | `veo-4-image-to-video` | Veo 4 | imageField=images_list; inputs: images_list, aspect_ratio, duration |
| `seedance-2-vip-image-to-video-1080p` | `sd-2-vip-image-to-video-1080p` | Seedance 2 VIP Image to Video 1080P | imageField=images_list; inputs: images_list, aspect_ratio, duration |
| `seedance-2-vip-image-to-video-fast-1080p` | `sd-2-vip-image-to-video-fast-1080p` | Seedance 2 VIP Image to Video Fast 1080P | imageField=images_list; inputs: images_list, aspect_ratio, duration |
| `seedance-2-vip-omni-reference-1080p` | `sd-2-vip-omni-reference-1080p` | Seedance 2 VIP Omni Reference 1080P | imageField=images_list; inputs: images_list, video_files, audio_files, aspect_ratio, duration |
| `seedance-2-vip-omni-reference-fast-1080p` | `sd-2-vip-omni-reference-fast-1080p` | Seedance 2 VIP Omni Reference Fast 1080P | imageField=images_list; inputs: images_list, video_files, audio_files, aspect_ratio, duration |
| `seedance-2-vip-first-last-frame-1080p` | `sd-2-vip-first-last-frame-1080p` | Seedance 2 VIP First Last Frame 1080P | imageField=images_list; inputs: images_list, aspect_ratio, duration |
| `kling-v3.0-4k-image-to-video` | `kling-v3.0-4k-image-to-video` | Kling v3.0 4K | imageField=image_url; lastImageField=last_image; inputs: image_url, last_image, duration |
| `vidu-q3-pro-image-to-video` | `vidu-q3-pro-image-to-video` | Vidu Q3 Pro | imageField=image_url; inputs: image_url, resolution, aspect_ratio, duration, audio |
| `vidu-q3-pro-first-last-frames` | `vidu-q3-pro-first-last-frames` | Vidu Q3 Pro First Last Frames | imageField=image_url; lastImageField=last_image; inputs: image_url, last_image, resolution, aspect_ratio, duration, audio |
| `vidu-q3-turbo-image-to-video` | `vidu-q3-turbo-image-to-video` | Vidu Q3 Turbo | imageField=image_url; inputs: image_url, resolution, aspect_ratio, duration, audio |
| `vidu-q3-turbo-first-last-frames` | `vidu-q3-turbo-first-last-frames` | Vidu Q3 Turbo First Last Frames | imageField=image_url; lastImageField=last_image; inputs: image_url, last_image, resolution, aspect_ratio, duration, audio |
| `vidu-q4-image-to-video` | `vidu-q4-image-to-video` | Vidu Q4 | imageField=image_url; inputs: image_url, resolution, duration, audio |
| `vidu-q4-reference-to-video` | `vidu-q4-reference-to-video` | Vidu Q4 Reference | imageField=images_list; inputs: images_list, aspect_ratio, resolution, duration, audio |
| `vidu-q2-pro-image-to-video` | `vidu-q2-pro-image-to-video` | Vidu Q2 Pro | imageField=image_url; inputs: image_url, resolution, aspect_ratio, duration, movement_amplitude |
| `vidu-q2-turbo-image-to-video` | `vidu-q2-turbo-image-to-video` | Vidu Q2 Turbo | imageField=image_url; inputs: image_url, resolution, aspect_ratio, duration, movement_amplitude |
| `happy-horse-1-reference-to-video-1080p` | `happy-horse-1-reference-to-video-1080p` | HappyHorse 1.0 Reference 1080P | imageField=images_list; inputs: images_list, aspect_ratio, duration |
| `happy-horse-1-reference-to-video-720p` | `happy-horse-1-reference-to-video-720p` | HappyHorse 1.0 Reference 720P | imageField=images_list; inputs: images_list, aspect_ratio, duration |
| `gemini-omni-image-to-video` | `gemini-omni-image-to-video` | Gemini Omni | imageField=image_urls; inputs: image_urls, duration, resolution, aspect_ratio, audio_ids, seed, character_ids, aspect_ratio, duration |
| `kling-v3-turbo-standard-image-to-video` | `kling-v3-turbo-standard-image-to-video` | Kling v3 Turbo Standard | imageField=image_url; inputs: image_url, duration |
| `kling-v3-turbo-pro-image-to-video` | `kling-v3-turbo-pro-image-to-video` | Kling v3 Turbo Pro | imageField=image_url; inputs: image_url, duration, image_url, duration, seed, high_bitrate |
| `seedance-2-mini-image-to-video` | `seedance-2-mini-image-to-video` | Seedance 2 Mini | imageField=images_list; inputs: images_list, aspect_ratio, resolution, duration, generate_audio, high_bitrate |
| `happy-horse-1.1-image-to-video-1080p` | `happy-horse-1.1-image-to-video-1080p` | Happy Horse 1.1 Image to Video 1080P | imageField=images_list; inputs: images_list, aspect_ratio, duration |
| `happy-horse-1.1-image-to-video-720p` | `happy-horse-1.1-image-to-video-720p` | Happy Horse 1.1 Image to Video 720P | imageField=images_list; inputs: images_list, aspect_ratio, duration |
| `happy-horse-1.1-reference-to-video-1080p` | `happy-horse-1.1-reference-to-video-1080p` | HappyHorse 1.1 Reference 1080P | imageField=images_list; inputs: images_list, aspect_ratio, duration |
| `happy-horse-1.1-reference-to-video-720p` | `happy-horse-1.1-reference-to-video-720p` | HappyHorse 1.1 Reference 720P | imageField=images_list; inputs: images_list, aspect_ratio, duration |
| `seedance-2-vip-image-to-video-4k` | `sd-2-vip-image-to-video-4k` | Seedance 2 VIP Image to Video 4K | imageField=images_list; inputs: images_list, aspect_ratio, duration |
| `seedance-2-vip-first-last-frame-4k` | `sd-2-vip-first-last-frame-4k` | Seedance 2 VIP First Last Frame 4K | imageField=images_list; inputs: images_list, aspect_ratio, duration |
| `seedance-2-vip-omni-reference-4k` | `sd-2-vip-omni-reference-4k` | Seedance 2 VIP Omni Reference 4K | imageField=images_list; lastImageField=last_image; inputs: images_list, video_files, audio_files, aspect_ratio, duration, image_url, duration, high_bitrate, image_url, duration, seed, high_bitrate, images_list, duration, seed, high_bitrate, images_list, duration, seed, high_bitrate, images_list, videos_list, audios_list, duration, seed, omni_reference_task_type, high_bitrate, images_list, videos_list, audios_list, duration, seed, omni_reference_task_type, high_bitrate |
| `seedance-2-spicy-image-to-video` | `seedance-2-spicy-image-to-video` | Seedance 2 Spicy | imageField=images_list; inputs: images_list, aspect_ratio, duration, high_bitrate |
| `seedance-2-spicy-image-to-video-fast` | `seedance-2-spicy-image-to-video-fast` | Seedance 2 Spicy Image to Video Fast | imageField=images_list; inputs: images_list, aspect_ratio, duration, high_bitrate |
| `seedance-2-mini-spicy-image-to-video` | `seedance-2-mini-spicy-image-to-video` | Seedance 2 Mini Spicy | imageField=images_list; inputs: images_list, aspect_ratio, resolution, duration, generate_audio, high_bitrate |
| `minimax-h3-image-to-video` | `minimax-h3-image-to-video` | MiniMax H3 Image to Video | imageField=image_url; lastImageField=last_image_url; inputs: image_url, last_image_url, resolution, duration |
| `minimax-h3-reference-to-video` | `minimax-h3-reference-to-video` | MiniMax H3 Reference | imageField=reference_images; inputs: reference_images, reference_videos, reference_audios, aspect_ratio, resolution, duration |
| `minimax-h3-open-image-to-video` | `minimax-h3-open-image-to-video` | MiniMax H3 Open Image to Video | imageField=image_url; lastImageField=last_image; inputs: image_url, last_image, resolution, duration |
| `minimax-h3-open-reference-to-video` | `minimax-h3-open-reference-to-video` | MiniMax H3 Base Ref2VA | imageField=images_list; inputs: images_list, videos_list, audios_list, aspect_ratio, resolution, duration |
| `flux-3-image-to-video` | `flux-3-image-to-video` | FLUX 3 | imageField=image_url; inputs: image_url, aspect_ratio, resolution, duration, generate_audio |
| `wan3.0-image-to-video` | `wan3.0-image-to-video` | Wan 3.0 | imageField=image_url; lastImageField=last_image; inputs: image_url, last_image, resolution, aspect_ratio, duration, thinking_mode, enable_audio, seed |
| `wan3.0-spicy-image-to-video` | `wan3.0-spicy-image-to-video` | Wan 3.0 Spicy | imageField=image_url; lastImageField=last_image; inputs: image_url, last_image, resolution, aspect_ratio, duration, thinking_mode, enable_audio, seed |
| `seedance-2.5-image-to-video-1080p` | `seedance-2.5-image-to-video-1080p` | Seedance 2.5 Image to Video 1080p | imageField=image_url; inputs: image_url, duration, seed, high_bitrate |
| `seedance-2.5-image-to-video-4k` | `seedance-2.5-image-to-video-4k` | Seedance 2.5 Image to Video 4K | imageField=image_url; inputs: image_url, duration, seed, high_bitrate |
| `seedance-2.5-first-last-frame-1080p` | `seedance-2.5-first-last-frame-1080p` | Seedance 2.5 First Last Frame 1080p | imageField=images_list; inputs: images_list, duration, seed, high_bitrate |
| `seedance-2.5-first-last-frame-4k` | `seedance-2.5-first-last-frame-4k` | Seedance 2.5 First Last Frame 4K | imageField=images_list; inputs: images_list, duration, seed, high_bitrate |
| `seedance-2.5-omni-reference-1080p` | `seedance-2.5-omni-reference-1080p` | Seedance 2.5 Omni Reference 1080p | imageField=images_list; inputs: images_list, videos_list, audios_list, duration, seed, omni_reference_task_type, high_bitrate |
| `seedance-2.5-omni-reference-4k` | `seedance-2.5-omni-reference-4k` | Seedance 2.5 Omni Reference 4K | imageField=images_list; inputs: images_list, videos_list, audios_list, duration, seed, omni_reference_task_type, high_bitrate |
| `seedance-2.5-intl-image-to-video` | `seedance-2.5-intl-image-to-video` | Seedance 2.5 Intl | imageField=image_url; inputs: image_url, duration, seed, high_bitrate |
| `seedance-2.5-intl-image-to-video-480p` | `seedance-2.5-intl-image-to-video-480p` | Seedance 2.5 Intl Image to Video 480p | imageField=image_url; inputs: image_url, duration, seed, high_bitrate |
| `seedance-2.5-spicy-image-to-video-480p` | `seedance-2.5-spicy-image-to-video-480p` | Seedance 2.5 Spicy Image to Video 480p | imageField=image_url; inputs: image_url, duration, seed, high_bitrate |
| `seedance-2.5-intl-image-to-video-1080p` | `seedance-2.5-intl-image-to-video-1080p` | Seedance 2.5 Intl Image to Video 1080p | imageField=image_url; inputs: image_url, duration, seed, high_bitrate |
| `seedance-2.5-spicy-image-to-video-1080p` | `seedance-2.5-spicy-image-to-video-1080p` | Seedance 2.5 Spicy Image to Video 1080p | imageField=image_url; inputs: image_url, duration, seed, high_bitrate |
| `seedance-2.5-intl-image-to-video-4k` | `seedance-2.5-intl-image-to-video-4k` | Seedance 2.5 Intl Image to Video 4K | imageField=image_url; inputs: image_url, duration, seed, high_bitrate |
| `seedance-2.5-spicy-image-to-video-4k` | `seedance-2.5-spicy-image-to-video-4k` | Seedance 2.5 Spicy Image to Video 4K | imageField=image_url; inputs: image_url, duration, seed, high_bitrate |
| `seedance-2.5-intl-first-last-frame` | `seedance-2.5-intl-first-last-frame` | Seedance 2.5 Intl First Last Frame | imageField=images_list; inputs: images_list, duration, seed, high_bitrate |
| `seedance-2.5-spicy-first-last-frame` | `seedance-2.5-spicy-first-last-frame` | Seedance 2.5 Spicy First Last Frame | imageField=images_list; inputs: images_list, duration, seed, high_bitrate |
| `seedance-2.5-intl-first-last-frame-480p` | `seedance-2.5-intl-first-last-frame-480p` | Seedance 2.5 Intl First Last Frame 480p | imageField=images_list; inputs: images_list, duration, seed, high_bitrate |
| `seedance-2.5-spicy-first-last-frame-480p` | `seedance-2.5-spicy-first-last-frame-480p` | Seedance 2.5 Spicy First Last Frame 480p | imageField=images_list; inputs: images_list, duration, seed, high_bitrate |
| `seedance-2.5-intl-first-last-frame-1080p` | `seedance-2.5-intl-first-last-frame-1080p` | Seedance 2.5 Intl First Last Frame 1080p | imageField=images_list; inputs: images_list, duration, seed, high_bitrate |
| `seedance-2.5-spicy-first-last-frame-1080p` | `seedance-2.5-spicy-first-last-frame-1080p` | Seedance 2.5 Spicy First Last Frame 1080p | imageField=images_list; inputs: images_list, duration, seed, high_bitrate |
| `seedance-2.5-intl-first-last-frame-4k` | `seedance-2.5-intl-first-last-frame-4k` | Seedance 2.5 Intl First Last Frame 4K | imageField=images_list; inputs: images_list, duration, seed, high_bitrate |
| `seedance-2.5-spicy-first-last-frame-4k` | `seedance-2.5-spicy-first-last-frame-4k` | Seedance 2.5 Spicy First Last Frame 4K | imageField=images_list; inputs: images_list, duration, seed, high_bitrate |
| `seedance-2.5-intl-omni-reference` | `seedance-2.5-intl-omni-reference` | Seedance 2.5 Intl Omni Reference | imageField=images_list; inputs: images_list, videos_list, audios_list, duration, seed, omni_reference_task_type, high_bitrate |
| `seedance-2.5-spicy-omni-reference` | `seedance-2.5-spicy-omni-reference` | Seedance 2.5 Spicy Omni Reference | imageField=images_list; inputs: images_list, videos_list, audios_list, duration, seed, omni_reference_task_type, high_bitrate |
| `seedance-2.5-intl-omni-reference-480p` | `seedance-2.5-intl-omni-reference-480p` | Seedance 2.5 Intl Omni Reference 480p | imageField=images_list; inputs: images_list, videos_list, audios_list, duration, seed, omni_reference_task_type, high_bitrate |
| `seedance-2.5-spicy-omni-reference-480p` | `seedance-2.5-spicy-omni-reference-480p` | Seedance 2.5 Spicy Omni Reference 480p | imageField=images_list; inputs: images_list, videos_list, audios_list, duration, seed, omni_reference_task_type, high_bitrate |
| `seedance-2.5-intl-omni-reference-1080p` | `seedance-2.5-intl-omni-reference-1080p` | Seedance 2.5 Intl Omni Reference 1080p | imageField=images_list; inputs: images_list, videos_list, audios_list, duration, seed, omni_reference_task_type, high_bitrate |
| `seedance-2.5-spicy-omni-reference-1080p` | `seedance-2.5-spicy-omni-reference-1080p` | Seedance 2.5 Spicy Omni Reference 1080p | imageField=images_list; inputs: images_list, videos_list, audios_list, duration, seed, omni_reference_task_type, high_bitrate |
| `seedance-2.5-intl-omni-reference-4k` | `seedance-2.5-intl-omni-reference-4k` | Seedance 2.5 Intl Omni Reference 4K | imageField=images_list; inputs: images_list, videos_list, audios_list, duration, seed, omni_reference_task_type, high_bitrate |
| `seedance-2.5-spicy-omni-reference-4k` | `seedance-2.5-spicy-omni-reference-4k` | Seedance 2.5 Spicy Omni Reference 4K | imageField=images_list; inputs: images_list, videos_list, audios_list, duration, seed, omni_reference_task_type, high_bitrate |
| `wan2.7-image-to-video-spicy` | `wan2.7-image-to-video-spicy` | Wan 2.7 Spicy | imageField=image_url; inputs: image_url, negative_prompt, audio_url, resolution, duration, shot_type, enable_prompt_expansion, seed |
| `wan2.6-image-to-video-spicy` | `wan2.6-image-to-video-spicy` | Wan 2.6 Spicy | imageField=image_url; inputs: image_url, negative_prompt, audio_url, resolution, duration, shot_type, enable_prompt_expansion, seed |
| `minimax-h3-image-to-video-lora` | `minimax-h3-image-to-video-lora` | MiniMax H3 Image to Video LoRA | imageField=image_url; lastImageField=last_image; inputs: image_url, last_image, resolution, duration, seed, loras |
| `minimax-h3-reference-to-video-lora` | `minimax-h3-reference-to-video-lora` | MiniMax H3 Reference to Video LoRA | imageField=images_list; inputs: images_list, videos_list, audios_list, aspect_ratio, resolution, duration, seed, loras |
| `ltx-2.5-image-to-video` | `ltx-2.5-image-to-video` | LTX 2.5 | imageField=image_url; lastImageField=last_image; inputs: image_url, last_image, duration, resolution, seed |
| `wan3.0-reference-to-video` | `wan3.0-reference-to-video` | Wan 3.0 Reference to Video | imageField=images_list; inputs: images_list, videos_list, audios_list, resolution, aspect_ratio, duration, thinking_mode, enable_audio, seed |
| `wan3.0-prime-image-to-video` | `wan3.0-prime-image-to-video` | Wan 3.0 Prime | imageField=image_url; lastImageField=last_image; inputs: image_url, last_image, resolution, aspect_ratio, duration, thinking_mode, enable_audio, seed |
| `wan3.0-prime-reference-to-video` | `wan3.0-prime-reference-to-video` | Wan 3.0 Prime Reference to Video | imageField=images_list; inputs: images_list, videos_list, audios_list, resolution, aspect_ratio, duration, thinking_mode, enable_audio, seed |
| `wan3.0-spicy-reference-to-video` | `wan3.0-spicy-reference-to-video` | Wan 3.0 Spicy Reference to Video | imageField=images_list; inputs: images_list, videos_list, audios_list, resolution, aspect_ratio, duration, thinking_mode, enable_audio, seed |
| `flux-3-start-end-to-video` | `flux-3-start-end-to-video` | FLUX 3 Start End to Video | imageField=image_url; lastImageField=end_image_url; inputs: image_url, end_image_url, aspect_ratio, resolution, duration, generate_audio |
| `gemini-omni-flash-1-1-image-to-video` | `gemini-omni-flash-1-1-image-to-video` | Gemini Omni Flash 1.1 | imageField=first_frame_url; lastImageField=last_frame_url; inputs: first_frame_url, last_frame_url, duration, aspect_ratio, resolution, seed |
| `gemini-omni-flash-1-2-image-to-video` | `gemini-omni-flash-1-2-image-to-video` | Gemini Omni 1.2 Flash Image to Video | imageField=first_frame_url; lastImageField=last_frame_url; inputs: first_frame_url, last_frame_url, duration, aspect_ratio, resolution, seed |
| `gemini-omni-flash-1-1-reference-to-video` | `gemini-omni-flash-1-1-reference-to-video` | Gemini Omni 1.1 Flash Reference | imageField=image_urls; inputs: image_urls, reference_video_urls, aspect_ratio, resolution, duration |
| `gemini-omni-flash-1-2-reference-to-video` | `gemini-omni-flash-1-2-reference-to-video` | Gemini Omni 1.2 Flash Reference to Video | imageField=image_urls; inputs: image_urls, duration, aspect_ratio, resolution, seed |
| `minimax-h3-image-to-video-spicy` | `minimax-h3-image-to-video-spicy` | MiniMax H3 Spicy | imageField=image_url; lastImageField=last_image; inputs: image_url, last_image, resolution, duration, seed |
| `happy-horse-1-image-to-video` | `happy-horse-1-image-to-video` | Happy Horse 1 Image to Video | imageField=images_list; inputs: resolution, images_list, aspect_ratio, duration |
| `happy-horse-1-reference-to-video` | `happy-horse-1-reference-to-video` | Happy Horse 1 Reference to Video | imageField=images_list; inputs: resolution, images_list, aspect_ratio, duration, seed |
| `happy-horse-1.1-image-to-video` | `happy-horse-1.1-image-to-video` | Happy Horse 1.1 Image to Video | imageField=images_list; inputs: resolution, images_list, aspect_ratio, duration |
| `happy-horse-1.1-reference-to-video` | `happy-horse-1.1-reference-to-video` | Happy Horse 1.1 Reference to Video | imageField=images_list; inputs: resolution, images_list, aspect_ratio, duration, seed |
| `minimax-h3-max-image-to-video` | `minimax-h3-max-image-to-video` | MiniMax H3 Max Image to Video | imageField=image_url; inputs: image_url, end_image_url, resolution, duration, prompt_expansion_mode |
| `minimax-h3-max-reference-to-video` | `minimax-h3-max-reference-to-video` | MiniMax H3 Max Reference to Video | imageField=reference_images; videoField=reference_videos; inputs: reference_images, reference_videos, reference_audios, aspect_ratio, resolution, duration, prompt_expansion_mode |
| `minimax-h3-max-turbo-image-to-video` | `minimax-h3-max-turbo-image-to-video` | MiniMax H3 Max Turbo Image to Video | imageField=image_url; inputs: image_url, end_image_url, resolution, duration, prompt_expansion_mode |
| `seedance-2-spicy-omni-reference` | `seedance-2-spicy-omni-reference` | Seedance 2 Spicy Omni Reference | imageField=images_list; inputs: resolution, images_list, video_files, audio_files, aspect_ratio, duration, high_bitrate |
| `seedance-2-spicy-omni-reference-fast` | `seedance-2-spicy-omni-reference-fast` | Seedance 2 Spicy Omni Reference Fast | imageField=images_list; inputs: resolution, images_list, video_files, audio_files, aspect_ratio, duration, high_bitrate, items, items, items, items, items, items, items, items, items, items, items, items |
| `minimax-h3-max-spicy-image-to-video` | `minimax-h3-max-spicy-image-to-video` | MiniMax H3 Max Spicy Image to Video | imageField=image_url; inputs: image_url, end_image_url, resolution, duration |
| `minimax-h3-max-spicy-reference-to-video` | `minimax-h3-max-spicy-reference-to-video` | MiniMax H3 Max Spicy Reference to Video | imageField=reference_images; videoField=reference_videos; inputs: reference_images, reference_videos, reference_audios, aspect_ratio, resolution, duration |
| `minimax-h3-max-turbo-spicy-image-to-video` | `minimax-h3-max-turbo-spicy-image-to-video` | MiniMax H3 Max Turbo Spicy Image to Video | imageField=image_url; inputs: image_url, end_image_url, resolution, duration |
| `ltx-2.5-fast-image-to-video` | `ltx-2.5-fast-image-to-video` | LTX 2.5 Fast | imageField=image_url; inputs: image_url, resolution, fps, duration, seed |
| `ltx-2.5-pro-image-to-video` | `ltx-2.5-pro-image-to-video` | LTX 2.5 Pro | imageField=image_url; inputs: image_url, resolution, fps, duration, seed |
| `minimax-h3-reference-to-video-spicy` | `minimax-h3-reference-to-video-spicy` | MiniMax H3 Spicy Reference to Video | category=Image to Video; inputs: reference_images, reference_videos, reference_audios, aspect_ratio, resolution, duration, aigc_watermark |
| `seedance-2.5-flash-image-to-video` | `seedance-2.5-flash-image-to-video` | Image to Video | category=Image to Video; inputs: image_url, duration, resolution, generate_audio, seed |
| `seedance-2.5-flash-first-last-frame` | `seedance-2.5-flash-first-last-frame` | First & Last Frame | category=Image to Video; inputs: images_list, duration, resolution, generate_audio, seed |
| `seedance-2.5-flash-reference-to-video` | `seedance-2.5-flash-reference-to-video` | Reference to Video | category=Image to Video; inputs: images_list, videos_list, audios_list, aspect_ratio, duration, resolution, generate_audio, seed |
| `seedance-2.5-flash-spicy-image-to-video` | `seedance-2.5-flash-spicy-image-to-video` | Spicy Image to Video | category=Image to Video; inputs: image_url, duration, resolution, generate_audio, seed |
| `seedance-2.5-flash-spicy-first-last-frame` | `seedance-2.5-flash-spicy-first-last-frame` | Spicy First & Last Frame | category=Image to Video; inputs: images_list, duration, resolution, generate_audio, seed |
| `seedance-2.5-flash-spicy-reference-to-video` | `seedance-2.5-flash-spicy-reference-to-video` | Spicy Reference to Video | category=Image to Video; inputs: images_list, videos_list, audios_list, aspect_ratio, duration, resolution, generate_audio, seed |
| `seedance-2.5-flash-intl-image-to-video` | `seedance-2.5-flash-intl-image-to-video` | Intl Image to Video | category=Image to Video; inputs: image_url, duration, resolution, generate_audio, seed |
| `seedance-2.5-flash-intl-first-last-frame` | `seedance-2.5-flash-intl-first-last-frame` | Intl First & Last Frame | category=Image to Video; inputs: images_list, duration, resolution, generate_audio, seed |
| `seedance-2.5-flash-intl-reference-to-video` | `seedance-2.5-flash-intl-reference-to-video` | Intl Reference to Video | category=Image to Video; inputs: images_list, videos_list, audios_list, aspect_ratio, duration, resolution, generate_audio, seed |

## Video → Video (edit, upscale, motion control, tools) — 89 models

| id | endpoint | name | notes |
|---|---|---|---|
| `video-watermark-remover` | `video-watermark-remover` | AI Video Watermark Remover | videoField=video_url |
| `kling-v2.6-std-motion-control` | `kling-v2.6-std-motion-control` | Kling 2.6 Standard Motion Control | imageField=image_url; videoField=video_url |
| `kling-v3.0-std-motion-control` | `kling-v3.0-std-motion-control` | Kling 3.0 Standard Motion Control | imageField=image_url; videoField=video_url |
| `kling-v3.0-pro-motion-control` | `kling-v3.0-pro-motion-control` | Kling 3.0 Pro Motion Control | imageField=image_url; videoField=video_url |
| `ai-video-face-swap` | `ai-video-face-swap` | AI Video Face Swap | imageField=image_url; videoField=video_url |
| `mmaudio-v2-video-to-video` | `mmaudio-v2/video-to-video` | MMAudio v2 | videoField=video_url |
| `runway-aleph-v2v` | `runway-aleph-v2v` | Runway Aleph | videoField=video_url |
| `ai-dance-effects` | `ai-dance-effects` | AI Dance Effects | imageField=image_url; videoField=video_url |
| `ai-video-upscaler` | `ai-video-upscaler` | AI Video Upscaler | videoField=video_url |
| `wan2.2-edit-video` | `wan2.2-edit-video` | Wan2.2 Edit Video | videoField=video_url |
| `heygen-video-translate` | `heygen-video-translate` | HeyGen Video Translate | videoField=video_url |
| `topaz-video-upscale` | `topaz-video-upscale` | Topaz Video Upscale | videoField=video_url |
| `ai-video-upscaler-pro` | `ai-video-upscaler-pro` | AI Video Upscaler Pro | videoField=video_url |
| `remix-video` | `remix-video` | Remix Video | videoField=video_url |
| `kling-o1-video-edit` | `kling-o1-video-edit` | Kling O1 Pro Edit | imageField=images_list; videoField=video_url |
| `kling-o1-video-edit-fast` | `kling-o1-video-edit-fast` | Kling O1 Pro Edit Fast | imageField=images_list; videoField=video_url |
| `kling-o1-standard-video-edit` | `kling-o1-standard-video-edit` | Kling O1 Standard Edit | imageField=images_list; videoField=video_url |
| `wan2.2-spicy-video-extend` | `wan2.2-spicy-video-extend` | Wan2.2 Spicy Video Extend | videoField=video_url; inputs: duration |
| `seedance-v1.5-pro-video-extend` | `seedance-v1.5-pro-video-extend` | Seedance v1.5 Pro Video Extend | videoField=video_url |
| `seedance-v1.5-pro-video-extend-fast` | `seedance-v1.5-pro-video-extend-fast` | Seedance v1.5 Pro Video Extend Fast | videoField=video_url; inputs: resolution |
| `add-video-watermark` | `add-video-watermark` | Add Video Watermark | imageField=watermark_image_url; videoField=video_url |
| `seedance-2-watermark-remover` | `seedance-2.0-watermark-remover` | Seedance 2 Watermark Remover | videoField=video_url |
| `ai-captions` | `ai-captions` | AI Captions | videoField=video_url |
| `ltx-2.3-video-extend` | `ltx-2.3-video-extend` | LTX 2.3 Extend | videoField=video_url; inputs: duration |
| `seedance-2-video-watermark-remover-pro` | `seedance-2-video-watermark-remover-pro` | Seedance 2 Video Watermark Remover Pro | videoField=video_url |
| `pixverse-v6-extend` | `pixverse-v6-extend` | PixVerse V6 Extend | videoField=video_url; inputs: resolution, duration, generate_audio_switch, negative_prompt, style |
| `wan2.7-video-extend` | `wan2.7-video-extend` | Wan 2.7 Extend | videoField=video_url; inputs: duration |
| `wan2.7-video-edit` | `wan2.7-video-edit` | Wan 2.7 Edit | imageField=images_list; videoField=video_url; inputs: duration, audio_setting |
| `happy-horse-1-video-edit-1080p` | `happy-horse-1-video-edit-1080p` | HappyHorse 1.0 Edit 1080P | imageField=images_list; videoField=video_url |
| `happy-horse-1-video-edit-720p` | `happy-horse-1-video-edit-720p` | HappyHorse 1.0 Edit 720P | imageField=images_list; videoField=video_url |
| `happy-horse-1.1-video-edit-1080p` | `happy-horse-1.1-video-edit-1080p` | Happy Horse 1.1 Video Edit 1080P | imageField=images_list; videoField=video_url |
| `happy-horse-1.1-video-edit-720p` | `happy-horse-1.1-video-edit-720p` | Happy Horse 1.1 Video Edit 720P | imageField=images_list; videoField=video_url |
| `gemini-omni-video-edit` | `gemini-omni-video-edit` | Gemini Omni Video Edit | imageField=image_urls; videoField=video_url |
| `video-background-remover` | `video-background-remover` | Video Background Remover | videoField=video_url |
| `kling-v2.6-pro-motion-control` | `kling-v2.6-pro-motion-control` | Kling 2.6 Pro Motion Control | imageField=image_url; videoField=video_url |
| `infinitetalk-video-to-video` | `infinitetalk-video-to-video` | InfiniteTalk | videoField=video_url; inputs: video_url, audio_url, resolution |
| `wan2.2-animate` | `wan2.2-animate` | Wan2.2 Animate | imageField=image_url; videoField=video_url; inputs: image_url, video_url, mode, resolution |
| `volcengine-video-to-video-lip-sync` | `volcengine-video-to-video-lip-sync` | Volcengine Lipsync | videoField=video_url; inputs: mode, video_url, audio_url, separate_vocal, open_scenedet, align_audio, align_audio_reverse, templ_start_seconds |
| `seedance-2.5-video-edit` | `seedance-2.5-video-edit` | Seedance 2.5 Video Edit | imageField=images_list; videoField=video_url; inputs: video_url, images_list, audios_list, duration, generate_audio, seed, high_bitrate |
| `seedance-2.5-video-edit-480p` | `seedance-2.5-video-edit-480p` | Seedance 2.5 Video Edit 480p | imageField=images_list; videoField=video_url; inputs: video_url, images_list, audios_list, duration, generate_audio, seed, high_bitrate |
| `seedance-2.5-video-edit-1080p` | `seedance-2.5-video-edit-1080p` | Seedance 2.5 Video Edit 1080p | imageField=images_list; videoField=video_url; inputs: video_url, images_list, audios_list, duration, generate_audio, seed, high_bitrate |
| `seedance-2.5-video-edit-4k` | `seedance-2.5-video-edit-4k` | Seedance 2.5 Video Edit 4K | imageField=images_list; videoField=video_url; inputs: video_url, images_list, audios_list, duration, generate_audio, seed, high_bitrate |
| `seedance-2.5-video-extend` | `seedance-2.5-video-extend` | Seedance 2.5 Video Extend | imageField=last_image; lastImageField=last_image; videoField=video_url; inputs: video_url, last_image, duration, generate_audio, seed, high_bitrate |
| `seedance-2.5-video-extend-480p` | `seedance-2.5-video-extend-480p` | Seedance 2.5 Video Extend 480p | imageField=last_image; lastImageField=last_image; videoField=video_url; inputs: video_url, last_image, duration, generate_audio, seed, high_bitrate |
| `seedance-2.5-video-extend-1080p` | `seedance-2.5-video-extend-1080p` | Seedance 2.5 Video Extend 1080p | imageField=last_image; lastImageField=last_image; videoField=video_url; inputs: video_url, last_image, duration, generate_audio, seed, high_bitrate |
| `seedance-2.5-video-extend-4k` | `seedance-2.5-video-extend-4k` | Seedance 2.5 Video Extend 4K | imageField=last_image; lastImageField=last_image; videoField=video_url; inputs: video_url, last_image, duration, generate_audio, seed, high_bitrate |
| `seedance-2.5-intl-video-edit` | `seedance-2.5-intl-video-edit` | Seedance 2.5 Intl Video Edit | imageField=images_list; videoField=video_url; inputs: video_url, images_list, audios_list, duration, generate_audio, seed, high_bitrate |
| `seedance-2.5-spicy-video-edit` | `seedance-2.5-spicy-video-edit` | Seedance 2.5 Spicy Video Edit | imageField=images_list; videoField=video_url; inputs: video_url, images_list, audios_list, duration, generate_audio, seed, high_bitrate |
| `seedance-2.5-intl-video-edit-480p` | `seedance-2.5-intl-video-edit-480p` | Seedance 2.5 Intl Video Edit 480p | imageField=images_list; videoField=video_url; inputs: video_url, images_list, audios_list, duration, generate_audio, seed, high_bitrate |
| `seedance-2.5-spicy-video-edit-480p` | `seedance-2.5-spicy-video-edit-480p` | Seedance 2.5 Spicy Video Edit 480p | imageField=images_list; videoField=video_url; inputs: video_url, images_list, audios_list, duration, generate_audio, seed, high_bitrate |
| `seedance-2.5-intl-video-edit-1080p` | `seedance-2.5-intl-video-edit-1080p` | Seedance 2.5 Intl Video Edit 1080p | imageField=images_list; videoField=video_url; inputs: video_url, images_list, audios_list, duration, generate_audio, seed, high_bitrate |
| `seedance-2.5-spicy-video-edit-1080p` | `seedance-2.5-spicy-video-edit-1080p` | Seedance 2.5 Spicy Video Edit 1080p | imageField=images_list; videoField=video_url; inputs: video_url, images_list, audios_list, duration, generate_audio, seed, high_bitrate |
| `seedance-2.5-intl-video-edit-4k` | `seedance-2.5-intl-video-edit-4k` | Seedance 2.5 Intl Video Edit 4K | imageField=images_list; videoField=video_url; inputs: video_url, images_list, audios_list, duration, generate_audio, seed, high_bitrate |
| `seedance-2.5-spicy-video-edit-4k` | `seedance-2.5-spicy-video-edit-4k` | Seedance 2.5 Spicy Video Edit 4K | imageField=images_list; videoField=video_url; inputs: video_url, images_list, audios_list, duration, generate_audio, seed, high_bitrate |
| `seedance-2.5-intl-video-extend` | `seedance-2.5-intl-video-extend` | Seedance 2.5 Intl Video Extend | imageField=last_image; lastImageField=last_image; videoField=video_url; inputs: video_url, last_image, duration, generate_audio, seed, high_bitrate |
| `seedance-2.5-spicy-video-extend` | `seedance-2.5-spicy-video-extend` | Seedance 2.5 Spicy Video Extend | imageField=last_image; lastImageField=last_image; videoField=video_url; inputs: video_url, last_image, duration, generate_audio, seed, high_bitrate |
| `seedance-2.5-intl-video-extend-480p` | `seedance-2.5-intl-video-extend-480p` | Seedance 2.5 Intl Video Extend 480p | imageField=last_image; lastImageField=last_image; videoField=video_url; inputs: video_url, last_image, duration, generate_audio, seed, high_bitrate |
| `seedance-2.5-spicy-video-extend-480p` | `seedance-2.5-spicy-video-extend-480p` | Seedance 2.5 Spicy Video Extend 480p | imageField=last_image; lastImageField=last_image; videoField=video_url; inputs: video_url, last_image, duration, generate_audio, seed, high_bitrate |
| `seedance-2.5-intl-video-extend-1080p` | `seedance-2.5-intl-video-extend-1080p` | Seedance 2.5 Intl Video Extend 1080p | imageField=last_image; lastImageField=last_image; videoField=video_url; inputs: video_url, last_image, duration, generate_audio, seed, high_bitrate |
| `seedance-2.5-spicy-video-extend-1080p` | `seedance-2.5-spicy-video-extend-1080p` | Seedance 2.5 Spicy Video Extend 1080p | imageField=last_image; lastImageField=last_image; videoField=video_url; inputs: video_url, last_image, duration, generate_audio, seed, high_bitrate |
| `seedance-2.5-intl-video-extend-4k` | `seedance-2.5-intl-video-extend-4k` | Seedance 2.5 Intl Video Extend 4K | imageField=last_image; lastImageField=last_image; videoField=video_url; inputs: video_url, last_image, duration, generate_audio, seed, high_bitrate |
| `seedance-2.5-spicy-video-extend-4k` | `seedance-2.5-spicy-video-extend-4k` | Seedance 2.5 Spicy Video Extend 4K | imageField=last_image; lastImageField=last_image; videoField=video_url; inputs: video_url, last_image, duration, generate_audio, seed, high_bitrate |
| `flux-3-video-extend` | `flux-3-video-extend` | FLUX 3 Video Extend | videoField=video_url; inputs: video_url, aspect_ratio, resolution, duration, generate_audio |
| `flux-3-video-upscaler` | `flux-3-video-upscaler` | FLUX Video Upscale | videoField=video_url; inputs: video_url, upscale_factor, creativity |
| `flux-3-video-extend-draft` | `flux-3-video-extend-draft` | FLUX 3 Video Extend Draft | videoField=video_url; inputs: video_url, aspect_ratio, duration, generate_audio |
| `gemini-omni-flash-1-1-edit` | `gemini-omni-flash-1-1-edit` | Gemini Omni 1.1 Flash Edit | videoField=video_url; inputs: video_url, resolution |
| `gemini-omni-flash-1-2-edit` | `gemini-omni-flash-1-2-edit` | Gemini Omni 1.2 Flash Edit | videoField=video_url; inputs: video_url, aspect_ratio, resolution |
| `depth-anything` | `depth-anything` | Depth Anything V2 | imageField=image_url; videoField=video_url; inputs: video_url, image_url |
| `runway-act-two-v2v` | `runway-act-two-v2v` | Runway Act Two V2V | videoField=video_url; inputs: video_url, reference_video_url, aspect_ratio |
| `luma-flash-reframe` | `luma-flash-reframe` | Luma Flash Reframe | imageField=image_url; videoField=video_url; inputs: video_url, aspect_ratio, image_url, duration |
| `seedance-2-video-edit` | `seedance-v2.0-video-edit` | Seedance 2 Video Edit | imageField=images_list; videoField=video_urls; inputs: video_urls, images_list, audio_files, aspect_ratio, quality, duration |
| `happy-horse-1-video-edit` | `happy-horse-1-video-edit` | Happy Horse 1 Video Edit | imageField=images_list; videoField=video_url; inputs: resolution, video_url, images_list, audio_setting, seed |
| `happy-horse-1.1-video-edit` | `happy-horse-1.1-video-edit` | Happy Horse 1.1 Video Edit | imageField=images_list; videoField=video_url; inputs: resolution, video_url, images_list, audio_setting, seed |
| `topaz-upscale-video-creative` | `topaz-upscale-video-creative` | Topaz Upscale Video Creative | videoField=video_url; inputs: video_url, creativity, realism, sharp, upscale_factor, target_fps, H264_output |
| `topaz-upscale-video-generative` | `topaz-upscale-video-generative` | Topaz Upscale Video Generative | videoField=video_url; inputs: video_url, model, upscale_factor, target_fps, softness, H264_output |
| `topaz-upscale-video-precision` | `topaz-upscale-video-precision` | Topaz Upscale Video Precision | videoField=video_url; inputs: video_url, model, upscale_factor, target_fps, compression, noise, halo, grain, recover_detail, H264_output, items |
| `video-passthrough` | `video-passthrough` | Video to Video | category=Video to Video; inputs: video_url, make_input |
| `motion-graphics-edit` | `motion-graphics-edit` | Motion Graphics Edit | category=Video to Video; inputs: request_id, edit_prompt, duration_seconds, aspect_ratio |
| `seedance-2-motion-control` | `seedance-2-motion-control` | Seedance 2 Motion Control | category=Video to Video; inputs: video_url, images_list, aspect_ratio, duration, quality, generate_audio |
| `seedance-2.5-motion-control` | `seedance-2.5-motion-control` | Seedance 2.5 Motion Control | category=Video to Video; inputs: video_url, images_list, aspect_ratio, duration, seed, high_bitrate, generate_audio |
| `seedance-2-spicy-motion-control` | `seedance-2-spicy-motion-control` | Seedance 2 Spicy Motion Control | category=Video to Video; inputs: video_url, images_list, aspect_ratio, duration, quality, generate_audio |
| `gemini-omni-flash-1-2-video-edit` | `gemini-omni-flash-1-2-video-edit` | 1.2 Flash | category=Video to Video; inputs: video_url, images_list, character_ids, aspect_ratio, resolution |
| `gemini-omni-flash-1-2-extend` | `gemini-omni-flash-1-2-extend` | 1.2 Flash | category=Video to Video; inputs: request_id, duration, images_list |
| `seedance-2.5-flash-video-edit` | `seedance-2.5-flash-video-edit` | Video Edit | category=Video to Video; inputs: video_url, images_list, audios_list, resolution, generate_audio |
| `seedance-2.5-flash-video-extend` | `seedance-2.5-flash-video-extend` | Video Extend | category=Video to Video; inputs: video_url, duration, resolution, generate_audio |
| `seedance-2.5-flash-spicy-video-edit` | `seedance-2.5-flash-spicy-video-edit` | Spicy Video Edit | category=Video to Video; inputs: video_url, images_list, audios_list, resolution, generate_audio |
| `seedance-2.5-flash-spicy-video-extend` | `seedance-2.5-flash-spicy-video-extend` | Spicy Video Extend | category=Video to Video; inputs: video_url, duration, resolution, generate_audio |
| `seedance-2.5-flash-intl-video-edit` | `seedance-2.5-flash-intl-video-edit` | Intl Video Edit | category=Video to Video; inputs: video_url, images_list, audios_list, resolution, generate_audio |
| `seedance-2.5-flash-intl-video-extend` | `seedance-2.5-flash-intl-video-extend` | Intl Video Extend | category=Video to Video; inputs: video_url, duration, resolution, generate_audio |

## Lip sync (image/video + audio → video) — 16 models

| id | endpoint | name | notes |
|---|---|---|---|
| `infinitetalk-image-to-video` | `infinitetalk-image-to-video` | Infinite Talk | category=image; inputs: resolution |
| `wan2.2-speech-to-video` | `wan2.2-speech-to-video` | Wan 2.2 Speech to Video | category=image; inputs: resolution |
| `ltx-2.3-lipsync` | `ltx-2.3-lipsync` | LTX 2.3 Lipsync | category=image; inputs: resolution |
| `ltx-2-19b-lipsync` | `ltx-2-19b-lipsync` | LTX 2 19B Lipsync | category=image; inputs: resolution |
| `sync-lipsync` | `sync-lipsync` | Sync Lipsync | category=video |
| `latent-sync` | `latentsync-video` | LatentSync | category=video |
| `creatify-lipsync` | `creatify-lipsync` | Creatify Lipsync | category=video |
| `veed-lipsync` | `veed-lipsync` | Veed Lipsync | category=video |
| `infinitetalk-video-to-video` | `infinitetalk-video-to-video` | Infinite Talk V2V | category=video; inputs: resolution |
| `volcengine-video-to-video-lip-sync` | `volcengine-video-to-video-lip-sync` | Volcengine Video to Video Lip Sync | category=video; inputs: mode |
| `kling-v1-avatar-standard` | `kling-v1-avatar-standard` | Kling v1 Avatar Standard | category=image |
| `kling-v1-avatar-pro` | `kling-v1-avatar-pro` | Kling v1 Avatar Pro | category=image |
| `kling-v2-avatar-standard` | `kling-v2-avatar-standard` | Kling v2 Avatar Standard | category=image |
| `kling-v2-avatar-pro` | `kling-v2-avatar-pro` | Kling v2 Avatar Pro | category=image |
| `omnihuman-1-5` | `omnihuman-1-5` | Omnihuman 1 5 | category=image; inputs: output_resolution |
| `ltx-2.5-fast-audio-to-video` | `ltx-2.5-fast-audio-to-video` | LTX 2.5 Fast Audio to Video | category=image; inputs: resolution, fps |

## Recast — 3 models

| id | endpoint | name | notes |
|---|---|---|---|
| `kling-v3.0-pro-recast` | `kling-v3.0-pro-motion-control` | Kling 3.0 Pro Motion Control | imageField=image_url; videoField=video_url |
| `runway-act-two-recast` | `runway-act-two-i2v` | Runway Act Two | imageField=image_url; videoField=video_url; inputs: aspect_ratio |
| `wan2.2-animate-recast` | `wan2.2-animate` | Wan2.2 Animate | imageField=image_url; videoField=video_url |

## Motion control — 2 models

| id | endpoint | name | notes |
|---|---|---|---|
| `seedance-2.5-intl-motion-control` | `seedance-2.5-intl-motion-control` | Seedance 2.5 Intl Motion Control |  |
| `seedance-2.5-spicy-motion-control` | `seedance-2.5-spicy-motion-control` | Seedance 2.5 Spicy Motion Control |  |

## Audio (music, speech, SFX) — 24 models

| id | endpoint | name | notes |
|---|---|---|---|
| `suno-create-music` | `suno-create-music` | Suno Create Music | inputs: style, model, custom_mode, title, persona_id, persona_model, instrumental, negative_tags, vocal_gender, style_weight, weirdness_constraint, audio_weight |
| `suno-remix-music` | `suno-remix-music` | Suno Remix Music | inputs: audio_url, style, model, custom_mode, title, persona_id, persona_model, instrumental, negative_tags, vocal_gender, style_weight, weirdness_constraint, audio_weight |
| `suno-extend-music` | `suno-extend-music` | Suno Extend Music | inputs: audio_url, style, model, custom_mode, title, persona_id, persona_model, continue_at, instrumental, negative_tags, vocal_gender, style_weight, weirdness_constraint, audio_weight |
| `suno-generate-sounds` | `suno-generate-sounds` | Suno Generate Sounds | inputs: model, sound_loop, sound_tempo, sound_key, grab_lyrics |
| `suno-add-vocals` | `suno-add-vocals` | Suno Add Vocals | inputs: audio_url, style, negative_tags, model, vocal_gender, style_weight, weirdness_constraint, audio_weight, title |
| `suno-generate-mashup` | `suno-generate-mashup` | Suno Geneate Mashup | inputs: audios_list, style, instrumental, model, vocal_gender, style_weight, weirdness_constraint, audio_weight, title |
| `suno-add-instrumental` | `suno-add-instrumental` | Suno Add Instrumental | inputs: audio_url, tags, negative_tags, model, vocal_gender, style_weight, weirdness_constraint, audio_weight, title |
| `suno-voice-clone` | `suno-voice-clone` | Suno Voice Cloning | inputs: audio_url, voice_name, description, style, language, vocal_start_s, vocal_end_s |
| `minimax-voice-clone` | `minimax-voice-clone` | Minimax Voice Clone | inputs: audio_url, custom_voice_id, model, need_noise_reduction, need_volume_normalization, accuracy |
| `minimax-speech-2.6-hd` | `minimax-speech-2.6-hd` | Minimax Speech HD | inputs: voice_id, speed, volume, pitch, emotion, english_normalization, sample_rate, bitrate, channel, format, language_boost |
| `minimax-speech-2.6-turbo` | `minimax-speech-2.6-turbo` | Minimax Speech Turbo | inputs: voice_id, speed, volume, pitch, emotion, english_normalization, sample_rate, bitrate, channel, format, language_boost, duration |
| `elevenlabs-text-to-dialogue-v3` | `elevenlabs-text-to-dialogue-v3` | ElevenLabs Text to Dialogue V3 | inputs: dialogue, stability, language_code |
| `suno-convert-to-wav` | `suno-convert-to-wav` | Suno Convert to WAV | inputs: task_id, audio_id |
| `gemini-3-1-flash-tts` | `gemini-3-1-flash-tts` | Gemini 3.1 Flash TTS | inputs: speakers, dialogue_turns, scene, sample_context, temperature |
| `gemini-2-5-pro-tts` | `gemini-2-5-pro-tts` | Gemini 2.5 Pro TTS | inputs: speakers, dialogue_turns, scene, sample_context, temperature |
| `elevenlabs-tts-turbo-2-5` | `elevenlabs-tts-turbo-2-5` | ElevenLabs TTS Turbo 2.5 | inputs: voice_id, stability, similarity_boost, speed, language_code |
| `minimax-music-3.0` | `minimax-music-3.0` | MiniMax Music 3.0 | inputs: lyrics, bitrate, sample_rate, is_instrumental |
| `elevenlabs-v4` | `elevenlabs-v4` | Eleven v4 | inputs: voice_id |
| `fish-s2-1-pro` | `fish-s2-1-pro` | Fish Audio S2.1 Pro | inputs: voice_id |
| `lyria-3-pro` | `lyria-3-pro` | Lyria 3 Pro |  |
| `lyria-3` | `lyria-3` | Lyria 3 |  |
| `lyria-2` | `lyria-2` | Lyria 2 | inputs: items, items, items, items |
| `audio-passthrough` | `audio-passthrough` | Text to Audio | category=Text to Audio; inputs: audio_url, make_input |
| `suno-speech` | `suno-speech` | Suno Speech | category=Text to Audio; inputs: custom_mode, script, tone, variety, vocal_gender, background_music |
