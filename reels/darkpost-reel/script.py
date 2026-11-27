"""Desk life: "What is a dark post?" (standard desk set: render with --set desk).
who, text with ElevenLabs v3 tags, shot (maya|claude|wide), acting
(Maya: worried|flat|surprised|thinking|wink|sleepy|chin|gesture,
 Claude: bounce|look-away|squint|tilt|excited), pause before (s)."""
SCRIPT = [
  ('M', "[whispering, a little embarrassed] Claude, don't tell anyone I asked this.", 'maya', 'chin', 0.15),
  ('C', "[matter-of-fact] I can't. [lightly] I won't remember.", 'claude', 'tilt', 0.4),
  ('M', "[hesitant, quietly] What is a dark post?", 'maya', 'thinking', 0.45),
  ('C', "[helpfully] It's an ad that doesn't appear on your public profile.", 'claude', 'bounce', 0.4),
  ('M', "[quickly, defensive] I know. [confused] Why call it dark if my audience can see it?", 'maya', 'gesture', 0.35),
  ('C', "[simply] It's dark to your profile, not your audience.", 'wide', 'tilt', 0.4),
  ('M', "[disbelief] That's it?", 'maya', 'surprised', 0.35),
  ('C', "[cheerfully] That's it.", 'wide', 'bounce', 0.3),
  ('M', "[mortified] I've been saying it for three years.", 'wide', 'gesture', 0.4),
  ('C', "[reassuring] Everyone says it.", 'claude', 'tilt', 0.35),
  ('M', "[insisting] Everyone knows what it means.", 'maya', 'flat', 0.35),
  ('C', "[gently] Everyone uses it.", 'claude', 'squint', 0.35),
  ('M', "[thinking] Isn't that the same thing?", 'maya', 'chin', 0.4),
  ('C', "[dryly] Not quite.", 'claude', 'look-away', 0.35),
  ('M', "[pleading] Please tell me I'm not alone.", 'maya', 'worried', 0.45),
  ('C', "[warmly] Eight people asked me today.", 'claude', 'bounce', 0.4),
  ('M', "[hopeful] Interns?", 'maya', 'surprised', 0.4),
  ('C', "[deadpan] Mostly marketing heads.", 'claude', 'squint', 0.45),
  ('M', "[curious, leaning in] Who?", 'maya', 'chin', 0.35),
  ('C', "[innocently] I don't remember them either.", 'maya', 'tilt', 0.4),
  ('M', "[sighs] Okay. One more.", 'maya', 'flat', 0.55),
  ('C', "[eager] Go.", 'claude', 'bounce', 0.3),
  ('M', "[nervous, quietly] Promise you won't judge me?", 'maya', 'chin', 0.4),
  ('C', "[sincerely] I don't judge. [pause] [dryly, playful] I do keep a very long context window.", 'wide', 'look-away', 0.45),
]
# lines voiced with ElevenLabs v3 'Creative' stability for stronger emotion
STABILITY = {0: 0.0, 4: 0.0, 6: 0.0, 8: 0.0, 14: 0.0, 18: 0.0, 22: 0.0, 23: 0.0}

# camera framing matched to the reference reel: (location, aim point, lens mm, f-stop)
CAMS = {"Cam_Human": ((0.34, -0.80, 1.36), (0.46, 0.50, 1.33), 42, 1.8),    # tight chest-up close-up, eye level
        "Cam_Mascot": ((0.20, -0.74, 0.86), (0.13, -0.20, 0.92), 35, 1.8),  # low, Claude centre, her soft at upper right
        "Cam_Wide": ((0.02, -1.25, 1.06), (0.40, 0.30, 1.00), 32, 2.8)}    # close desk wide, Claude in the foreground
