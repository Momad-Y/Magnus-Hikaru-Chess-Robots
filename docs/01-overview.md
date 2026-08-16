# Overview

Two robots, one problem: **watch a human play a chess move on a physical board,
work out what they played, and play a reply with a robot arm.**

Neither robot has sensors in the board. Neither knows the position from anything
but photographs. Everything else follows from that.

---

## The shared architecture

Both generations are the same four subsystems wired in a loop.

```
        ┌──────────────────────────────────────────────────┐
        │                                                  │
        ▼                                                  │
   ┌─────────┐     ┌──────────┐     ┌────────┐     ┌───────────┐
   │ CAMERA  │────▶│   C2M    │────▶│ ENGINE │────▶│    ARM    │
   │         │     │  vision  │     │        │     │           │
   └─────────┘     └──────────┘     └────────┘     └───────────┘
    photograph      which squares    best reply     move the piece
    the board       changed?         to that
                    → what move?     position
```

| Subsystem | Magnus (v1) | Hikaru (v2) |
|---|---|---|
| Camera | Raspberry Pi HQ Camera | Logitech C270 |
| Vision | `C2M.py` — 6 functions | `C2M.py` — 14 functions |
| Engine | `CEP/` → Stockfish | `CE.py` → Stockfish + DRLCE |
| Arm | `ARM.py` — 6 servos via PCA9685 | `DrDRA.py` → Dobot SDK |
| Interface | Flask web app | Tkinter desktop app |

Both wrote their own `C2M`, independently. They are siblings, not forks — same
name, same job, 896 lines of difference.

## The turn loop

1. **Reference photo.** Capture the board before the human moves.
2. **Human moves.** They press a button to say they are done.
3. **Second photo.** Capture again.
4. **Diff.** Warp both images flat, split into 64 tiles, score how much each
   changed, keep the top four.
5. **Infer.** Changed squares plus board state give the move. Two squares is a
   normal move; three is en passant; four is castling.
6. **Validate.** Push it to a `python-chess` board. Illegal means the human is
   asked to fix the position.
7. **Reply.** Ask the engine for the best move.
8. **Execute.** Convert the destination square to arm coordinates and move.
9. **Repeat.**

## Where the difficulty actually is

Not the chess. Stockfish solves that, and has since 2008.

The hard parts are **perception** and **placement**:

- A camera at an angle sees a trapezoid, not a grid. → homography
- Lighting changes between two photos taken seconds apart. → per-pixel
  normalised difference and a top-N ranking rather than a fixed threshold
- Changed squares do not uniquely determine a move. → disambiguation against
  board state
- The arm's coordinate frame is not the camera's. → a measured homogeneous
  transform (v2) or hand-tuned per-servo offsets (v1)
- A piece placed 5 mm off is a piece knocked over next turn. → ±0.2 mm
  repeatability, or careful calibration and slow motion

## Reading order

If you want the engineering, go in this order:

1. [02 — Evolution](02-evolution.md) — what changed between the two and why
2. [03 — Vision](03-vision-c2m.md) — how a photograph becomes a move
3. [05 — Kinematics](05-kinematics.md) — how a square becomes a position
4. [04 — Chess engines](04-chess-engines.md) — Stockfish, and the vendored AlphaZero
5. [06 — Hardware](06-hardware.md) — what the two robots are made of

If you want to run it: [07 — Running the code](07-running.md).

## Honest status

Both projects are **finished university work, archived**. Neither is maintained,
and the hardware for both is gone.

What still runs on an ordinary laptop: both interfaces, both chess engines, and
the vision code against the sample board images included in the repository. What
cannot be run or verified: either arm.

Unfinished features are documented where they occur rather than tidied away —
v2's Instructions screen is genuinely empty, v1's `CEP` prototype genuinely does
not compile, and the voice-control feature promised in v1's proposal was never
built.
