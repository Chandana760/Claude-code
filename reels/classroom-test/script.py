"""Classroom set TEST (reuses the dark post audio): shows the board being written,
struck, drawn on and wiped, and Claude's pointer following it. Not a real episode."""
BOARD = [
  (0, -2.0, "title", "What's a dark post?"),
  (3, 0.4, "write", "w1", "ad", (0.08, 0.30), "blue"),
  (3, 1.4, "write", "w2", "not on profile", (0.30, 0.30), "blue"),
  (4, 1.0, "strike", "w1"),
  (5, 0.3, "draw", "you", "stick", (0.14, 0.66), 120, "black"),
  (5, 1.2, "arrow", "a1", (0.24, 0.66), (0.46, 0.66), "green"),
  (5, 2.0, "write", "w3", "audience", (0.50, 0.66), "green"),
  (8, 0.8, "draw", "ok", "check", (0.90, 0.66), 55, "green"),
  (12, 0.2, "wipe",),
  (12, 1.0, "title", "Everyone uses it"),
]
