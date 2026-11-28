# Classroom set: shots and staging (from the reference reel)

Build with `--set classroom`. Maya and Claude keep their standard look (seated body,
mustard office chair, smooth low-poly jacket back are classroom-only additions).

## Cameras (all positions live in blender/classroom_room.py)

| Shot (script name) | Camera | Framing | Use it for (reference shots) |
|---|---|---|---|
| `wide`   | Cam_Wide   | Front-right, desk level: board high in frame, Claude on his podium left, Maya full seated body + chair right foreground | her opening question, big board beats, the punchline (ref 0, 2, 4, 8) |
| `board`  | Cam_Board  | Board large, Claude bottom-left pointing up, Maya head/shoulder bottom-right | while Claude explains and the board is being written / struck (ref 1, 3, 10, 13, 17) |
| `claude` | Cam_Mascot | Low, front-right close on Claude + pointer, neon/ivy bokeh behind | Claude's talking lines (ref 5, 7, 9, 12, 15, 19, 21) |
| `maya`   | Cam_Human  | Three-quarter front-left close on Maya, board writing soft top-left | her lines and her reactions to Claude (ref 6, 11, 14, 16, 18, 20) |

## Staging that happens automatically

* **Claude talking** - faces the camera / Maya (neutral), pointer resting toward the board, small teaching taps.
* **Board being written** - Claude turns ~35 deg toward the board and his pointer tracks the item being written,
  then he turns back to camera.
* **Maya while Claude explains** - lifts her chin and looks up at the board; settles back for her own lines.
* **Board title** is on the board from the first frame; the lesson builds underneath line by line.

## Board plan (BOARD list in the episode's script.py)

`(line_index, seconds_into_line, op, ...)` with ops:
`title`, `write` (blue / red / green / black marker), `strike` (red line through an item),
`draw` (stick | box | circle | check), `arrow`, `wipe`.
Pattern from the reference: title -> jargon words written then struck out -> simple drawing with a label ->
arrow to the answer -> red label + arrow naming the concept -> closing question at the bottom.

## Render quality

Faceted characters need at least 540x960 / 16 samples (finals 1080x1920, 32-48 samples).
