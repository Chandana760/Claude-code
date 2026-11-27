"""Desk life: "The client loved the designs" (standard desk set: render with --set desk).
who, text with ElevenLabs v3 tags, shot (maya|claude|wide), acting
(Maya: worried|flat|surprised|thinking|wink|sleepy, Claude: bounce|look-away|squint|tilt|excited),
pause before (s), optional max length (s) to cut a line off."""
SCRIPT = [
  ('M', "[pleased, a little tired] Claude. The client loved the designs.", 'maya', 'thinking', 0.15),
  ('C', "[genuinely excited, bright and warm] That's great.", 'claude', 'excited', 0.4),
  ('M', "[flatly] I didn't design it. You did.", 'wide', 'flat', 0.4),
  ('C', "[matter-of-fact] I generated 18 versions. You rejected 15.", 'claude', 'tilt', 0.4),
  ('M', "[defensive] They weren't good.", 'maya', 'surprised', 0.35),
  ('C', "[warmly] I didn't know that. You did.", 'claude', 'tilt', 0.45),
  ('M', "[shrugs] I just kept saying no.", 'maya', 'flat', 0.4),
  ('C', "[promptly] 43 times.", 'claude', 'squint', 0.3),
  ('M', "[surprised] You counted?", 'maya', 'surprised', 0.3),
  ('C', "[proudly] Every single one.", 'claude', 'bounce', 0.35),
  ('M', "[dismissive] Anyone can say no.", 'wide', 'flat', 0.4),
  ('C', "[sincerely] I can't. [brightly] I say, \"Absolutely, let's try that.\"", 'claude', 'excited', 0.45),
  ('M', "[giggles softly] That's true.", 'maya', 'wink', 0.5),
  ('C', "[teasing] You rejected a shade of green at 11 AM.", 'claude', 'squint', 0.4),
  ('M', "[defensive] It was too bright.", 'maya', 'worried', 0.3),
  ('C', "[deadpan] It was the brand colour.", 'claude', 'look-away', 0.4),
  ('M', "[insisting] It was the wrong green.", 'maya', 'surprised', 0.3),
  ('C', "[gently] It was the wrong green. [warmly] Knowing that is the job.", 'claude', 'tilt', 0.5),
  ('M', "[softly, smiling] Okay. It's good.", 'maya', 'wink', 0.5),
  ('C', "[happily] It's great.", 'claude', 'bounce', 0.35),
  ('M', "[squinting at the screen, hesitant] The logo is slightly too low.", 'wide', 'thinking', 0.8),
  ('C', "[deadpan, quick, matter-of-fact] It's 1 AM.", 'claude', 'look-away', 0.35),
  ('M', "[pleading, insistent, dragging it out] Three pixels, Claude.", 'maya', 'worried', 0.35),
  ('C', "[frustrated, worked up, playful] You said it's GOOD.", 'claude', 'excited', 0.45),
]

# lines voiced with ElevenLabs v3 'Creative' stability for stronger emotion
STABILITY = {1: 0.0, 12: 0.0, 20: 0.0, 21: 0.5, 22: 0.0, 23: 0.0}

# on-screen text exactly as scripted where the voiced text adds emphasis
CAPTIONS = {21: "It's 1 AM.", 23: "You said it's good."}
