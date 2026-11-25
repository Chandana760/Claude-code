"""Daily life: "It's been a week" (sofa set: render with --set sofa).
who, text with ElevenLabs v3 tags, shot (maya|claude|wide), acting
(Maya: worried|flat|surprised|thinking|wink, Claude: bounce|look-away|squint|tilt|excited),
pause before (s), optional max length (s) to cut a line off."""
SCRIPT = [
  ('M', "[tired, softly] Claude... [sighs] it's been a week.", 'wide', 'flat', 0.15),
  ('C', "[curious] Since the client's campaign launched?", 'claude', 'tilt', 0.4),
  ('M', '[tired, flatly] Since I slept properly.', 'maya', 'flat', 0.4),
  ('C', "[upbeat] But the campaign is live! That's good!", 'claude', 'bounce', 0.4),
  ('M', "[deadpan] It's live. It's not performing.", 'maya', 'flat', 0.45),
  ('C', '[gently] What happened today?', 'claude', 'tilt', 0.45),
  ('M', '[sighs] They asked to change the creative and copy. ...Again.', 'maya', 'worried', 0.4),
  ('C', '[calmly] The algorithm is still learning.', 'claude', 'tilt', 0.45),
  ('M', '[frustrated] I told them that!', 'wide', 'surprised', 0.3),
  ('C', '[curious] And what did they say?', 'claude', 'squint', 0.4),
  ('M', '[mimicking the client, airy] "Let\'s just try something different."', 'maya', 'flat', 0.4),
  ('C', "[incredulous] So they want results from an ad they won't let finish learning?", 'claude', 'squint', 0.45),
  ('M', '[flatly] Exactly.', 'maya', 'flat', 0.35),
  ('M', '[hopeful] Can you explain that to my client?', 'maya', 'thinking', 0.5),
  ('C', '[confidently] I can.', 'claude', 'bounce', 0.4),
  ('M', '[relieved] Great. Send it.', 'wide', 'wink', 0.35),
  ('C', "[helpful] What's their email?", 'claude', 'bounce', 0.4),
  ('M', "[sleepy] You have it already! Send it in the morning. [yawns] Goodnight.", 'maya', 'sleepy', 0.45),
  ('C', '[softly] Okay, good night...', 'wide', 'tilt', 0.6),
  ('M', "[drowsy, eyes half closed] Actually... send it now. [pause] Before they ask for more edits.", 'maya', 'sleepy', 1.1),
  ('C', '[softly, hushed, gentle] Already sent. [whispers] Sleep tight.', 'claude', 'tilt', 1.0),
]
