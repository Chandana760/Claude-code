"""Daily life (redesign test): "My first reel". Same shape as the reference format (ask for honesty ->
flattery -> the real answer -> kind turn -> button), our own lines.
who, text with ElevenLabs v3 tags, shot, acting (face for Maya / motion for Claude), pause before (s)."""
SCRIPT = [
  ('M', '[nervous] Claude. Quick question. Is my first reel... good?', 'maya', 'worried', 0.5),
  ('C', '[cheerful] It is amazing! Iconic! Ten out of ten!', 'claude', 'bounce', 0.5),
  ('M', "[flatly] You haven't watched it.", 'maya', 'flat', 0.7),
  ('C', '[pause] I trust your vibe.', 'claude', 'look-away', 0.8),
  ('M', '[sighs] Okay. Actually watch it.', 'wide', 'flat', 0.7),
  ('C', '[long pause] ...Hm.', 'claude', 'squint', 1.0),
  ('M', '[worried] "Hm"? What is "hm"?', 'maya', 'surprised', 0.4),
  ('C', '[carefully] The first three seconds are you saying "um."', 'claude', 'tilt', 0.6),
  ('M', "[defensive] That's... my intro.", 'maya', 'worried', 0.7),
  ('C', '[gently] Start with the joke. Cut the um.', 'claude', 'bounce', 0.6),
  ('M', "[quietly] So it's bad.", 'maya', 'flat', 0.9),
  ('C', "[warmly] It's a first reel. Every first reel is bad. That's how you get a second one.", 'claude', 'tilt', 0.7),
  ('M', '[pause] ...Will you watch the second one?', 'maya', 'thinking', 0.9),
  ('C', "[softly] I'll watch all of them.", 'claude', 'excited', 0.7),
  ('M', '[suspicious] Even the "um" ones?', 'maya', 'wink', 0.8),
  ('C', '[long pause] ...Especially those.', 'wide', 'bounce', 1.1),
]
