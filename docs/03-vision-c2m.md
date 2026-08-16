# C2M: Chess Board to Moves

Neither robot has sensors in the board. The **only** way either one knows what
you played is by looking: photograph the board before your move, photograph it
after, and work out what changed.

`C2M` is the module that does this, and both generations wrote their own. They
are siblings, not forks. Magnus's is 6.8 KB across 6 functions, Hikaru's is
24 KB across 14, and they differ by 896 lines.

---

## The pipeline

```
  camera frame
      │
      ▼
  find the board          ← corner detection
      │
      ▼
  homography matrix       ← maps the skewed photo to a flat square
      │
      ▼
  warp to a top-down square
      │
      ▼
  split into 8×8 squares
      │
      ▼
  compare before / after per square
      │
      ▼
  rank the most-changed squares
      │
      ▼
  infer the move          ← disambiguation
```

## Step 1. Homography

The camera never looks at the board straight down; it sits at an angle. A
**homography** is the 3×3 projective transform that maps the four board corners
in the photo onto the four corners of a perfect square. Applying it produces a
top-down, axis-aligned image where square `e4` is always in the same place.

Magnus found the corners against a printed pattern (visible as the blue corner
markers in the demo footage). Hikaru added
`find_chessboard_corners()` and `modify_homography_matrix()`, letting the board
be re-detected and the transform adjusted without re-running calibration.

## Step 2. Difference per square

Both split the warped board into 64 tiles and score how much each one changed.
This is where the implementations diverge, and it matters:

**Magnus** uses an L2 norm, with the tile size hardcoded:

```python
size = 50                              # assumes a 400×400 warped image
dist = cv2.norm(img2Sq, img1Sq)
```

**Hikaru** uses a mean absolute difference, with the tile size derived:

```python
square_size = int(img_resolution[0] / num_of_squares)
diff = cv2.absdiff(prev_img_square, cur_img_square)
confidence_rate = np.sum(diff) / (square_size * square_size)
```

Two real improvements hide in that diff. Hikaru's tile size follows the camera
resolution instead of assuming 400×400, so changing camera no longer silently
breaks the grid. And dividing by tile area makes the score a **per-pixel
average** rather than a total, so the threshold means the same thing at any
resolution.

Both keep the **top four** most-changed squares with their confidence scores.
Four, because castling moves four pieces.

## Step 3. Inferring the move

Changed squares alone do not give you a move: `["c3", "b1"]` could be `b1→c3` or
`c3→b1`. The board state resolves it. From the original design notes:

> **2 squares changed.** `['c3', 'b1']` where `c3 = '.'` and `b1 = 'N'`.
> The square holding the piece is the *origin*: `b1c3`.
>
> **3 squares changed.** `['e5', 'f5', 'f6']` where `e5 = 'P'`, `f5 = 'p'`,
> `f6 = '.'`. This is *en passant*: the square with the moving side's piece is
> the origin, the empty square is the destination: `e5f6`.
>
> **4 squares changed.** `['e1', 'd1', 'c1', 'a1']`. This is *castling*: the
> origin is always `e1`, and the destination is whichever of `a1` or `h1` is
> present.

That is the whole trick. Vision only reports *which squares changed*; the chess
rules turn that into a legal move.

## Step 4. Validation

The inferred move is pushed to a `python-chess` `Board`. If it is not legal, the
system rejects it and asks the player to fix the position. That is why the
Magnus error table has both `Move Incorrect (100)` and `Move Incorrect on site
(101)`.

---

## What v2 added

| | Magnus (v1) | Hikaru (v2) |
|---|---|---|
| Functions | 6 | 14 |
| Naming | `camelCase` | `snake_case` |
| Docstrings | Brief | Full Args/Returns on every function |
| Tile size | Hardcoded 50 px | Derived from camera resolution |
| Difference metric | L2 norm (total) | Mean absolute difference (per pixel) |
| Corner detection | Implicit in homography | `find_chessboard_corners()` |
| Square → coordinates | none | `find_squares_coordinates()` |
| Camera → arm transform | none | `cam_2_arm_transformation()` |
| UI integration | Served as JPEG to the browser | `cv2_to_tk()` for live Tk display |

The last three rows are the real story. Magnus only had to answer *"what moved?"*
because a human-tuned servo table handled *"where is it?"*. Hikaru's `C2M` also
answers *"where is that square in the arm's coordinate frame?"*, which is why
`cam_2_arm_transformation()` lives in the vision module and not the arm module.

See [05-kinematics.md](05-kinematics.md) for the transform itself.
