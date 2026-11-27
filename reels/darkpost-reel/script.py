"""Desk life: "What is a dark post?" (standard desk set: render with --set desk).
who, text with ElevenLabs v3 tags, shot (maya|claude|wide), acting
(Maya: worried|flat|surprised|thinking|wink|sleepy|chin|gesture,
 Claude: bounce|look-away|squint|tilt|excited), pause before (s)."""
SCRIPT = [
  ('M', "[whispering, a little embarrassed] Claude, don't tell anyone I asked this.", 'maya', 'worried', 0.15),
  ('C', "[matter-of-fact] I can't. [lightly] I won't remember.", 'claude', 'tilt', 0.4),
  ('M', "[hesitant, quietly] What is a dark post?", 'maya', 'thinking', 0.45),
  ('C', "[helpfully] It's an ad that doesn't appear on your public profile.", 'claude', 'bounce', 0.4),
  ('M', "[quickly, a bit defensive] I know. [genuinely confused] Why call it dark if my audience can see it?", 'maya', 'flat', 0.35),
  ('C', "[simply] It's dark to your profile, not your audience.", 'wide', 'tilt', 0.4),
  ('M', "[stunned] That's it?", 'maya', 'surprised', 0.35),
  ('C', "[cheerfully] That's it.", 'claude', 'bounce', 0.3),
  ('M', "[groans, mortified] I've been saying it for six years.", 'wide', 'gesture', 0.4),
  ('C', "[reassuring] Everyone says it.", 'claude', 'tilt', 0.35),
  ('M', "[casually, like it's obvious] Everyone knows what it means.", 'maya', 'flat', 0.3),
  ('C', "[gently] Everyone uses it.", 'claude', 'squint', 0.35),
  ('M', "[slowly, suspicious] Isn't that the same thing?", 'maya', 'thinking', 0.4),
  ('C', "[dryly] Not quite.", 'claude', 'look-away', 0.35),
  ('M', "[pleading, dramatic] Please tell me I'm not alone.", 'wide', 'worried', 0.45),
  ('C', "[warmly] Nine people asked me today.", 'claude', 'bounce', 0.4),
  ('M', "[hopeful, quick] Interns?", 'maya', 'surprised', 0.4),
  ('C', "[deadpan] Mostly marketing heads.", 'claude', 'squint', 0.45),
  ('M', "[leaning in, eager whisper] Who?", 'maya', 'thinking', 0.35),
  ('C', "[innocently] I don't remember them either.", 'maya', 'tilt', 0.4),
  ('M', "[slowly realising] So, everybody asks.", 'maya', 'thinking', 0.45),
  ('C', "[quietly, knowingly] And nobody says.", 'claude', 'look-away', 0.4),
  ('M', "[exhales] Okay. [bracing herself] One more.", 'maya', 'flat', 0.5),
  ('C', "[eager] Go.", 'claude', 'bounce', 0.3),
  ('M', "[nervous, small voice] Promise you won't judge me?", 'maya', 'chin', 0.4),
  ('C', "[sincerely] I don't judge. [pause] [dryly, playful] I do keep a very long context window.", 'wide', 'look-away', 0.45),
]
# lines voiced with ElevenLabs v3 'Creative' stability for stronger emotion
STABILITY = {0: 0.0, 4: 0.0, 6: 0.0, 8: 0.0, 12: 0.0, 14: 0.0, 16: 0.0, 18: 0.0, 20: 0.0, 22: 0.0, 24: 0.0, 25: 0.0}
# camera moves: (line index, camera, lens at start, lens at end) - the ending pulls back like the reference
CAM_MOVES = [(25, 'Cam_Wide', 30, 25)]
# dusk sky like the reference: warm peach horizon up into soft blue (bottom -> top)
SKY_STOPS = [(0.52, (1.00, 0.42, 0.12)), (0.61, (1.00, 0.33, 0.32)), (0.70, (0.42, 0.36, 0.88)), (0.80, (0.08, 0.20, 0.85))]
EXPOSURE = -1.1

# camera framing matched to the reference reel: (location, aim point, lens mm, f-stop)
CAMS = {"Cam_Human": ((0.34, -0.80, 1.36), (0.46, 0.50, 1.41), 42, 1.8),    # tight chest-up close-up, eye level
        "Cam_Mascot": ((0.20, -0.74, 0.86), (0.13, -0.20, 0.92), 35, 1.8),  # low, Claude centre, her soft at upper right
        "Cam_Wide": ((0.20, -1.45, 1.08), (0.15, 0.30, 1.13), 30, 2.8)}    # close desk wide, Claude in the foreground
