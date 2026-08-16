# DRLCE Attribution

The chess engine in this directory is **adapted from someone else's work**, and
this file records whose.

> **pytorch-alpha-zero** by **jackdawkins11**
> https://github.com/jackdawkins11/pytorch-alpha-zero
> *"A chess engine based on the AlphaZero algorithm"*, a PyTorch implementation
> of DeepMind's AlphaZero, trained by supervised learning on the CCRL dataset.

`AlphaZeroNetwork.py`, `MCTS.py`, `encoder.py` and the pretrained weights
`AlphaZeroNet_20x256.pt` all come from there. Only `DRLCE.py`, the
`get_best_move(weights_file, board)` wrapper that adapts the engine to this
project's interface, was written by this team.

## How this was established

The upstream source was not recorded when the code was added (commit
`296581c Add AlphaZeroNet_20x256.pt weights file` carries no note), so it was
reconstructed afterwards and verified by comparison, normalising for whitespace
and comments:

| File | Identical to upstream |
|---|---|
| `AlphaZeroNetwork.py` | **100.0%** |
| `encoder.py` | **97.8%** |
| `MCTS.py` | **94.3%** |

The same three filenames and the same `weights/AlphaZeroNet_20x256.pt` appear
upstream, as do all the distinctive function names: `calcUCT`,
`parallelRollouts`, `maxNSelect`, `encodePositionForInference`,
`decodePolicyOutput`, `callNeuralNetworkBatched`, `mirrorMove`,
`encodeTrainingPoint`.

Two tells pointed there before the source was found: these modules are written
entirely in `camelCase` while every module this team authored uses
`snake_case`, and `encoder.py` defines `encodeTrainingPoint()`, a training-time
helper, although this project only ever runs inference.

## What was changed here

- Reformatted (upstream writes `def parseResult( result )`; here `def parseResult(result)`)
- Module docstrings added
- `import encoder` → `import DRLCE.encoder as encoder`, to namespace it under `DRLCE/`
- The `atomic.AtomicLong` dependency dropped from `MCTS.py`
- `encoder.py`: `cuda = False` → `cuda = torch.cuda.is_available()`, so the engine
  uses a GPU when present and falls back to CPU otherwise

## Licence

The upstream repository publishes no LICENSE file, so no explicit terms accompany
the code. It is credited here in full, and the weights are fetched at setup time
rather than redistributed from this repository.

If you are jackdawkins11 and would like this changed, whether different wording
or removal, please open an issue and it will be actioned.
