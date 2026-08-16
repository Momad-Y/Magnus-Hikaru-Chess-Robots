# Chess Engines

Both robots need an opponent. Magnus used Stockfish. Hikaru used Stockfish **and**
integrated a second, neural engine alongside it.

> **Attribution.** DRLCE's three core modules and its pretrained weights are
> adapted from
> [jackdawkins11/pytorch-alpha-zero](https://github.com/jackdawkins11/pytorch-alpha-zero).
> Only the thin `DRLCE.py` wrapper was written here. Details and evidence:
> [`hikaru-v2/DRLCE/ATTRIBUTION.md`](../hikaru-v2/DRLCE/ATTRIBUTION.md).

---

## Stockfish, both generations

Stockfish is a conventional alpha-beta search engine with an NNUE evaluation. It
is spoken to over **UCI** on stdin/stdout, wrapped here by the `stockfish` Python
package.

### Magnus (v1)

The v1 engine layer is a single script. Difficulty is fixed at maximum:

```python
stockfish.set_depth(20)        # how deep the search goes
stockfish.set_skill_level(20)  # strongest setting
```

There is no way to make it easier. The proposal set out to let players "compete
with the robot, not just lose" — the web app later added a difficulty selector,
but `CEP/chs.py` itself always plays at full strength.

### Hikaru (v2)

v2 turns difficulty into a parameter, mapping a 1–5 selector onto both knobs:

```python
stockfish.set_depth(difficulty_int * 5)
stockfish.set_skill_level(difficulty_int * 5)
```

So difficulty 1 is depth 5 / skill 5, and difficulty 4 is depth 20 / skill 20 —
matching Magnus's fixed setting at the top of the scale.

---

## DRLCE — the fifth difficulty is a different engine

Selecting **difficulty 5** does not make Stockfish stronger. It switches
opponents entirely, to **DRLCE** (Deep Reinforcement Learning Chess Engine), an
AlphaZero-style network adopted from
[jackdawkins11/pytorch-alpha-zero](https://github.com/jackdawkins11/pytorch-alpha-zero)
and wired into this project behind a small wrapper.

The give-away is in `CE.set_engine_difficulty()`:

```python
if difficulty_int == 5:
    difficulty_int = 1
```

Stockfish is still constructed, so it is pinned to its weakest setting and left
idle while `GUI.py:1170` routes the move request to DRLCE instead.

### Architecture

`AlphaZeroNet(20, 256)` — a 20-block residual tower, 256 filters per block, with
the standard AlphaZero two-head output:

- a **value head**, scoring how good the position is
- a **policy head**, giving a probability distribution over legal moves

Weights ship as `AlphaZeroNet_20x256.pt` (93 MB).

### Search

The network alone does not choose a move. **MCTS** (`DRLCE/MCTS.py`) builds a
search tree, using the policy head to decide which branches deserve exploration
and the value head to score leaves instead of playing games to completion. This
is the core AlphaZero idea: replace rollouts with a learned evaluator.

Defaults are deliberately small:

```python
rollouts = 10   # simulations per move
threads  = 1    # threads per rollout
```

### Encoding

`DRLCE/encoder.py` converts a `python-chess` board into the network's input
tensor — a `16 × 8 × 8` stack of planes — and decodes the policy output back into
legal moves, masked so illegal moves get zero probability.

### Device handling

The engine runs on GPU when one is available and falls back to CPU otherwise.

Measured on an RTX 3050 Laptop: a move from the opening position takes **1.42 s
on GPU** versus **0.79 s on CPU**, with a 205.6 MB peak GPU allocation. The GPU
is *slower* here, and that is expected rather than broken — at `rollouts = 10`,
`threads = 1`, every forward pass is a batch of one, so CUDA setup and per-call
host↔device transfer dominate and there is no parallelism to amortise them
against. `encoder.callNeuralNetworkBatched()` exists for batched inference and
would change the picture, but the default configuration never exercises it.

---

## Comparison

| | Magnus (v1) | Hikaru (v2) |
|---|---|---|
| Engine | Stockfish only | Stockfish + DRLCE |
| Engine functions | 1 script, ~20 lines | 14 functions in `CE.py` |
| Difficulty | Fixed at 20/20 | 1–4 scaled, 5 = DRLCE |
| Move validation | In the Flask route | `check_move()` / `check_game_state()` |
| Board rendering | chessboard.js in the browser | `cairosvg` → PIL → Tk |
| Game import | — | `set_board_from_pgn()`, `get_random_fen()` |

## A note on why DRLCE exists at all

Stockfish already plays far above human level, so a second engine adds nothing
competitively. DRLCE was integrated because the team's stated goal in the v2
proposal was to "learn more about chess engines and the AI behind it" — the work
was in understanding and wiring up an AlphaZero implementation, not in writing
one. At 10 rollouts per move it plays far below the Stockfish beside it.

What this team actually contributed here is `DRLCE.py`: loading the weights onto
the right device, freezing the parameters, running MCTS for a fixed rollout
budget, and returning the highest-visit move through the same interface the
Stockfish path uses. The network, the search and the encoder are upstream's.
