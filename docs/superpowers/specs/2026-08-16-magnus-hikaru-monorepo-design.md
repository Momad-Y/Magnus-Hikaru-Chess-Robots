# Magnus + Hikaru Monorepo — Design

**Date:** 2026-08-16
**Status:** Approved design, pending implementation plan
**Target repo:** `Momad-Y/Magnus-Hikaru-Chess-Robots` (renamed from `Hikaru-Nakarmsen-Chess-Robot`)

---

## 1. Context

Two university robotics projects at AAST, built by overlapping teams, solving the
same problem with different hardware:

| | **Magnus Armsen (v1)** | **Hikaru Nakarmsen (v2)** |
|---|---|---|
| Course | GN312 — Embedded Systems & IoT | RB310 — Fundamentals of Robotics |
| Team | Hazem Abdelghafar, Mohamed Abdelnasser, Belal Sameh, Mohamed Elfeel | Hazem Abdelghafar, Mohamed Abdelnasser, Mohamed Elfeel |
| Supervisors | Dr. Omar Shalash, Eng. Hossam Eldeen | — |
| Arm | 3D-printed, 6 DOF, MG996r + SG90 + CYS-S0200 servos via PCA9685 | Dobot Magician, 4 DOF, vacuum suction cup |
| Controller | Raspberry Pi 4B 8GB | Desktop PC over USB |
| Camera | Raspberry Pi HQ Camera | Logitech C270 (720p, 30fps, 55° DFoV) |
| Interface | Flask web app | Tkinter desktop app |
| Engine | Stockfish | Stockfish + DRLCE (AlphaZero/MCTS, PyTorch) |
| Budget | 9,000 EGP | 1,000 EGP |

Both independently evolved a module named **C2M** ("Chess Board to Moves") for
board detection and move inference. They are siblings, not forks: Magnus's is
6.8 KB, Hikaru's is 24 KB, and they differ by 896 diff lines.

### Goal

A single repository presenting both generations as a portfolio showcase.
Success criterion, set by the owner: **a reader grasps both projects in about
five minutes from the README and media, without running anything.**

### Constraints

- Hardware is unavailable. Vision, engines, and both UIs can be run on a laptop;
  neither arm can be driven. Any change to arm code is unverifiable.
- All current working-tree material is 756 MB, of which ~380 MB is duplication.
- Published history is already a 124.81 MiB pack; deletions in new commits do not
  shrink it. This forced the history-rewrite decision recorded in §4.1.
- Code is currently Windows-only in several places, with hardcoded absolute paths.

### Non-goals

- Extracting a shared core library across v1 and v2. Rejected: the projects are
  historical artifacts with independently evolved logic, and unifying them would
  destroy the v1→v2 comparison that gives the repo its value.
- Making either arm actually drivable on a new platform. We cannot verify it.
- Resuming feature development on either project.

---

## 2. Decisions

Each decision below states what it costs, not only what it wins.

### 2.1 Repo name → `Magnus-Hikaru-Chess-Robots`

**For:** encodes equal billing in the URL, matching the structural decision;
contains "chess-robots" for search; preserves the Carlsen/Nakamura pun that
gives the work identity; reads as a series, which is the actual story; matches
the owner's existing `Title-Case-Hyphenated` convention.
**Against:** 26 characters; "Magnus"/"Hikaru" are opaque to non-chess readers
until the README explains them; drops the word "arm", a search term.
**Alternative — `Chess-Robot-Arms`:** maximally searchable and instantly legible,
but generic among many similarly-named repos, and hides that there are two
generations.
**Deciding factor:** the repo's job is to make a reader arriving from a CV link
immediately grasp *two generations of one idea*. The chosen name encodes that;
the alternative does not.
**Note:** GitHub permanently redirects the old URL. Both documentation PDFs cite
`github.com/Momad-Y/Hikaru-Nakarmsen-Chess-Robot`, and those citations keep
resolving after the rename.

### 2.2 Build in the existing repo, not a fresh one

**For:** preserves 198 published commits of genuine history (199 locally; local is one ahead of origin/main); the GitHub rename gives a
permanent redirect from the cited URL; no re-publishing or re-starring.
**Against:** the repo's history is entirely Hikaru's, so Magnus enters with no
history and looks "added late"; root-level restructuring produces one large,
noisy commit.
**Alternative — fresh repo:** clean linear history telling the combined story,
but discards 198 commits and breaks every existing citation.
**Deciding factor:** 198 commits of real development history is irreplaceable
evidence of the work; a tidy commit graph is cosmetic. Mitigate the "added late"
appearance in the README narrative, not the git graph.

### 2.3 Directory naming → `magnus-v1/` and `hikaru-v2/`

**For:** the `-v1`/`-v2` suffix encodes the generational relationship, which is
the repo's central story, and sorts naturally.
**Against:** slightly verbose; implies v2 supersedes v1, when in fact v1 has the
richer hardware story and v2 is not strictly "better".
**Alternative — bare `magnus/`, `hikaru/`:** cleaner, but a reader must already
know which came first.
**Deciding factor:** chronology is the spine of the narrative; putting it in the
path means it never has to be explained twice.

### 2.4 Stockfish → fetch, never vendor

**For:** removes 4 identical copies of a 48 MB Windows `.exe` and 4 of a 47 MB
NNUE file (~380 MB, over half the repo); the vendored binary is Windows-only and
is the single largest portability blocker; system packages exist on every target
OS (`apt`/`brew`/`winget`).
**Against:** the repo no longer runs immediately after clone — a setup step is
required; a future Stockfish release could change UCI behaviour, where the pinned
binary was reproducible.
**Alternative — vendor one cross-platform build per OS:** still ~150 MB and still
needs per-OS selection logic.
**Deciding factor:** ~380 MB recovered and the primary portability blocker
removed, against one documented install step. Mitigate reproducibility by
pinning a known-good version range in docs and failing with a clear message.

### 2.5 Videos → committed short clips + Release assets for full files

**For:** GIF/WebP hero clips (~2–5 MB) autoplay inline in the README, which is
what makes a showcase land; full videos as Release assets keep clone size flat;
avoids Git LFS entirely.
**Against:** two places to update when media changes; Release assets are a manual
upload step; GIF quality is markedly worse than source.
**Alternative — Git LFS:** keeps everything in one place, but the free tier has
bandwidth quotas that, once exhausted, break `git clone` for everyone — an
unacceptable failure mode for a portfolio piece.
**Alternative — YouTube embed:** zero repo weight and best playback, but GitHub
READMEs cannot embed players (only linked thumbnails), and it introduces an
external dependency that can rot.
**Deciding factor:** LFS's quota failure mode directly attacks the repo's only
job — being browsable by a stranger.

### 2.6 AlphaZero weights (97 MB) → Release asset + fetch script

**For:** keeps clone under 60 MB; the file is a build artifact, not source;
92.7 MiB is uncomfortably near GitHub's 100 MiB hard block.
**Against:** DRLCE will not run until fetched; a stale or moved asset breaks the
fetch script.
**Deciding factor:** it is a model artifact. Source repos should not carry them.

### 2.7 Dobot vendor manuals → link, do not vendor

Decided by the owner. Seven PDFs, ~50 MB, third-party copyrighted, freely
available from Dobot. Referenced in `docs/06-hardware.md` as links to
`dobot-robots.com` and `download.dobot.cc`.
**Against:** offline readers lose them, and Dobot could reorganise its site.
**Deciding factor:** owner's explicit instruction; also avoids redistributing
third-party copyrighted material and a third of the repo's weight.

### 2.8 Media source → frames from the owner's own videos, not Dobot renders

**For:** unambiguously the owner's own material with no licensing question;
shows the *actual* builds, which is far more persuasive in a portfolio than a
stock product render; the Magnus video is 1972×1080 @ 60fps, a strong still
source.
**Against:** the Hikaru video is only 1138×640, so its stills will be visibly
softer; real footage is messier than marketing renders.
**Alternative — official Dobot product renders:** higher polish, but they are
Dobot's marketing IP, and they depict a stock arm rather than this project.
**Deciding factor:** a portfolio's credibility rests on showing your own work.
Dobot's renders are linked as hardware reference only.

### 2.9 Docs → Markdown chapters, PDFs retained alongside

**For:** Markdown is diffable, searchable, and renders on GitHub, so the
kinematics derivation and protocol spec become readable in-browser; the original
PDFs stay as submitted artifacts proving academic provenance.
**Against:** content is duplicated between Markdown and PDF and can drift; the
transformation matrix and DH table need LaTeX-ish rendering that GitHub Markdown
handles only via images or unicode tables.
**Deciding factor:** the stated success criterion is comprehension in five
minutes. Nobody opens a PDF in five minutes. PDFs are provenance, Markdown is
the interface.

### 2.10 Dependency management → keep `requirements.txt` per version

**For:** matches what both projects already used; zero migration risk;
immediately familiar.
**Against:** no lockfile, so installs are not reproducible; two files to maintain.
**Alternative — `pyproject.toml` + uv workspace:** modern and reproducible, but
imposes present-day tooling on frozen historical projects and misrepresents how
they were actually built.
**Deciding factor:** these are archived artifacts. Their dependency files are
part of the historical record.

---

## 3. Target structure

```
Magnus-Hikaru-Chess-Robots/
├── README.md                    # see §3.1
├── LICENSE                      # Apache-2.0
├── .gitignore
├── .gitattributes               # `* text=auto eol=lf` — prevents CRLF recurrence
├── docs/
│   ├── 01-overview.md           # what both projects are, at a glance
│   ├── 02-evolution.md          # v1 → v2: what changed and why
│   ├── 03-vision-c2m.md         # board detection, move inference (both)
│   ├── 04-chess-engines.md      # Stockfish integration; DRLCE/AlphaZero
│   ├── 05-kinematics.md         # DH model, camera→arm transform
│   ├── 06-hardware.md           # both BOMs, servo vs Dobot, vendor links
│   ├── assets/
│   └── superpowers/specs/       # this document
├── media/
│   ├── magnus/  hikaru/         # stills extracted from demo footage
│   └── clips/                   # short GIF/WebP for README
├── magnus-v1/
│   ├── README.md
│   ├── src/       # app.py, c2m.py, arm.py, engine.py
│   ├── web/       # templates/, static/ (incl. vendored jquery, chessboard.js)
│   ├── hardware/  # stl/, schematics/ (.fzz + .jpg), bom.xlsx
│   ├── docs/      # proposal, documentation, description PDFs; protocol notes
│   └── requirements.txt
├── hikaru-v2/
│   ├── README.md
│   ├── src/       # main.py, gui.py, c2m.py, ce.py, drdra.py, dobot/, drlce/
│   ├── hardware/  # chess-piece STL, RoboDK station
│   ├── docs/      # proposal, documentation, description, TODOs
│   ├── testing/
│   └── requirements.txt
└── tools/
    ├── fetch_stockfish.py
    └── fetch_weights.py
```

`.gitattributes` carries `* text=auto eol=lf` with binary exclusions. This is the
durable fix for the CRLF problem found across both projects — 19 tracked files in
Hikaru and 31 in Magnus were CRLF, producing phantom diffs. Repo-level attributes
fix it for every future contributor, where the local `core.autocrlf` setting only
fixes it for one machine.

### 3.1 Root README composition

The README is the deliverable that carries the five-minute success criterion, so
its structure is specified rather than left to taste:

1. **Title + one-line pitch** — "Two generations of a chess-playing robotic arm."
2. **Hero clip** — autoplaying GIF/WebP of an arm completing a move.
3. **Side-by-side comparison table** — the v1/v2 table from §1, so the two
   generations are legible within seconds of landing.
4. **Two showcase blocks**, one per version, each with a still, a two-paragraph
   summary, a link to the full demo video, and a link into that version's
   directory.
5. **The evolution story** — three or four paragraphs on why v2 exists and what
   changed, linking to `docs/02-evolution.md`.
6. **Repo map** — annotated tree so a reader knows where to go next.
7. **Quickstart** — per-OS setup, with an explicit statement of what runs without
   hardware and what does not.
8. **Credits** — both teams, both courses, supervisors.

Media is embedded with relative repo paths (not external hosts) so it renders
offline and survives site changes elsewhere.

---

## 4. Deduplication and harvest

### 4.1 Removed

| Item | Recovered |
|---|---|
| 4 × `stockfish-windows-...avx2.exe` (48 MB each) | 193 MB |
| 4 × `nn-6877cd24400e.nnue` (47 MB each) | 188 MB |
| `Extra/Hikaru/Old Source Codes` — byte-identical to `Extra/Magnus/Source Codes` | (subsumed above) |
| Stockfish `.o` objects, `sf_15.zip`, `__pycache__`, `.vscode`, `.code-workspace` | ~5 MB |
| `Dobot Cam Empty.bmp` 15 MB → PNG | ~14 MB |
| Vendored Stockfish C++ source tree | ~4 MB |

Projected **working tree** size (NOT clone size — see the correction below):

```
current two project dirs (excl. .venv/.git)      350.5 MB
  − weights, 2×stockfish.exe, 2×nnue, 15 MB BMP  −302.9 MB
  − Stockfish C++ source trees (non-nnue part)     −9.2 MB
  + unique material harvested from Extra/           +0.8 MB
  + media budget (stills + GIF clips)              +12.0 MB
                                                  ─────────
                                                   ~51 MB
```

Down from 756 MB of working-tree material.

> **CORRECTION (red-team, verified).** This is a *working-tree* number and was
> wrongly presented as a clone number. `origin/main` publishes a **149.0 MiB
> tree in a 124.81 MiB pack**, and `git rm` in a new commit does not shrink a
> pack. Three already-published blobs dominate: the AlphaZero weights
> (92.73 MiB), the Stockfish Windows binary (46.04 MiB) and
> `Test/Dobot Cam Empty.bmp` (14.42 MiB). A plain clone was therefore going to
> stay ~125 MiB no matter what this restructure deleted, which falsified the
> deciding factor of §2.6 and the headline of §4.1.
>
> **Resolution: rewrite history with `git filter-repo`** (owner's decision).
> That drops the clone to roughly 10 MiB and simultaneously withdraws the
> GPL-3 Stockfish material and the Dobot vendor PDF from publication — see
> NOTICE. Cost: all 198 published commit SHAs change and a force-push is
> required.

### 4.2 Deliberately kept despite appearing duplicated

Each version's own `C2M`, arm module, engine wrapper, `Resources.docx`, and
`Project Description.pdf`. These are independently evolved siblings; collapsing
them would erase the v1→v2 comparison. Magnus's vendored `font-awesome`,
`jquery`, and `chessboard.js` also stay — they are part of v1's shipped web app.

### 4.3 Harvested from `Extra/` (unique content only)

`Magnus Armsen Showcasing Video.mp4`, `Magnus Armsen Testing the Final
Project.mp4`, `Hikaru Nakamura Showcasing Video.mp4`, `Hikaru Nakarmsen Chess
Piece.stl`, `RoboDK Project-Station Dobot Magician.rdk`, Hikaru's project
proposal / project description / `Resources.docx` / `TODOs.docx`, and Magnus's
`Resources.docx`.

Everything else in `Extra/` was verified to be a CRLF-variant duplicate of
material already in the two project directories (191 files compared; one
trailing-newline difference in `playStyle.css`).

**Not harvested, by owner's decision:** the seven Dobot vendor manuals (~50 MB).
These will be lost when `Extra/` is deleted unless archived separately.

### 4.4 Loose files at the working-directory root

`Steps.txt` (Hikaru's run instructions) is folded into `hikaru-v2/README.md`
as the quickstart and then deleted. `.python-version` (`3.11.3`, written by `uv`)
moves into `hikaru-v2/`. The stray `.cursor/` directory is ignored, not committed.

---

## 5. Cross-platform plan

Tiered by what can actually be verified, since no arm hardware is available.

### Tier 1 — portable, and empirically verified on Linux

Every item below was proven by running both applications on Arch Linux and
capturing screenshots (see §6). Five changes were sufficient to make the Hikaru
GUI import and render.

1. **`Dobot/DoBotArm.py:6` — module-level `os.chdir`.** At *import* time it
   executes `os.chdir(os.getcwd() + "\Dobot")`. The backslash is a literal
   filename character on POSIX, so this raises immediately. This is also the
   **root cause of the `cwd + "/.."` hack** in `GUI.py:13`: that line exists only
   to undo a working-directory mutation performed by an unrelated module on
   import. Remove the `chdir`; fix the paths properly. (`\D` is additionally an
   invalid escape sequence.)
2. **Path anchoring.** `GUI.py:12-13` uses `os.getcwd()`; replace with
   `Path(__file__).resolve().parent`. Same for `app.py:12` (`"engine/..."`).
3. **Stockfish resolver.** One helper: `$STOCKFISH_PATH` → config →
   `shutil.which("stockfish")` → actionable per-OS error. Replaces four hardcoded
   call sites. Verified against Stockfish 16 over UCI.
4. **Icon decode.** `gui_logo_path` points at `Images/icon.ico`, which is passed
   to `c2m.cv2_to_tk()`. **OpenCV cannot decode `.ico` at all.** Ship a PNG
   alongside.
5. **`iconbitmap()` → `iconphoto()`.** On X11 `iconbitmap` expects XBM, so an
   `.ico` raises `TclError`.

6. **Font fallback — `("Courier", …)` at 42 sites in `GUI.py`.** Tk resolves bare
   `"Courier"` to **Nimbus Mono PS** on Linux, which renders heavy and uneven and
   makes the whole UI look wrong. `"Courier New"` resolves to **Liberation Mono**,
   the metric-compatible substitute (identical 289 px measure for
   "Select Difficulty"). On Windows, Tk's `"Courier"` already maps to Courier New,
   so the change should be neutral there — *reasoned, not tested, no Windows box*.
7. **Stale `Test/` paths.** `GUI.py:906/992/1103` read `cwd + "/Test/Live *.jpg"`,
   but that directory no longer exists — the files now live in `testing/results/`.
   The game screen cannot initialise until these are repointed.

Also, but not blockers:

- **Invalid escape sequences.** `CEP/chs.py:6` and `CEP/main.py:13` contain
  `"C:\Program Files (x86)\stockfish_15.1_win_x64_avx2\..."`. `\P` and `\s` are
  invalid escapes — already a `SyntaxWarning` on Python 3.12 and scheduled to
  become a `SyntaxError`. A genuine latent bug, not merely a portability issue.
- **Camera index** moves to config rather than a manual in-app step.
  `c2m.init_cam()` already returns `None` when no camera is present, and the GUI
  starts fine without one.

**Interpreter caveat, worth documenting for users.** Tkinter is not the
portability problem — the *interpreter build* is. The project's pyenv 3.11.3 was
compiled without `_tkinter`, as is `uv`'s standalone 3.11. pyenv 3.13.11 has
Tk 8.6 and works unmodified. The README should tell readers to verify
`python -c "import tkinter"` before filing a bug.

**Not a fix — a capture artifact.** `GUI.py:120` calls
`attributes("-fullscreen", True)`, which requires a cooperating window manager.
Under a bare Xvfb there is none, so the window collapses to its natural size. For
headless capture only, substitute explicit `geometry()`. **This substitution must
not enter the shipped code** — fullscreen behaves correctly on a real desktop.

### Tier 2 — platform-aware, unverifiable without hardware

- **`DobotDllType.py:549` calls `cdll.loadLibrary`.** The correct ctypes API is
  `cdll.LoadLibrary`. As written, attribute lookup falls through to
  `LibraryLoader.__getattr__`, which attempts to load a library literally named
  `loadLibrary` and raises `OSError`. **The Linux branch is broken as shipped.**
- **`CDLL("./DobotDll.dll")` is cwd-relative** — resolve against the module
  directory instead.
- Only the Windows `.dll` can be shipped. Linux/macOS require Dobot's own
  `libDobotDll.so` / `.dylib` from the official SDK. This will be documented, not
  faked. Dobot publishes SDKs for C++/Python/ROS.

### Tier 3 — inherently hardware-bound

Magnus's `ARM.py` imports `Adafruit_PCA9685` at module scope, so it fails at
import on any non-Pi machine. Guard the import so vision, engine, and the Flask
app run anywhere; only actual servo motion requires a Pi with I2C. This is the
honest ceiling — I²C to a PCA9685 is not an OS-portability problem.

---

## 6. Verification

| Layer | Status | Evidence |
|---|---|---|
| Magnus Flask app | **Verified** | Launched on Linux; `/`, `/links`, `/play` all HTTP 200; 3 screenshots at 1920×1080 |
| Hikaru Tkinter GUI | **Verified** | Rendered under Xvfb; 5 screenshots at 1920×1080 — main menu, difficulty, settings, pre-game, and the live play screen (virtual board + both camera frames + clocks) |
| Stockfish resolver | **Verified** | Stockfish 16 Linux binary answers UCI; drives both apps |
| DRLCE | **Verified** | GPU and CPU paths both return `d2d4`; 205.6 MB peak VRAM |
| Import chain on Linux | **Verified** | `import GUI` succeeds after the five Tier-1 changes |
| Vision (C2M) | To do | Run against the committed sample board images |
| Path handling | To do | Launch each entry point from several working directories |
| Dobot layer | **Cannot verify** | No hardware. Static review + documented caveat only |
| Magnus servo layer | **Cannot verify** | No hardware. Import-guard testable; motion is not |

Screenshots live in the session scratchpad and will move to `media/` during
implementation. Caveats:

- They were produced from patched scratch copies, not the repo tree.
- The Hikaru captures ran on torch 2.13.0+cpu, not the pinned 2.1.2, because
  2.1.2 publishes no cp313 wheels. They demonstrate that the UI renders on
  Linux; they are not a test of the pinned dependency set.
- The play screen was captured with a fake `cv2.VideoCapture` replaying the
  project's own `testing/results/Live Empty.jpg`. No application logic was
  modified — the app simply received frames from disk instead of a webcam, which
  is what its own `# Test` fallback lines already do.

**The instructions screen is empty in the source, not broken in capture.**
`instructions_label` carries `text="Instructions:"` and nothing more, and
`display_instructions()` places only that label plus Back and Exit. The screen
was never written. No screenshot of it will be shipped, and
`docs/02-evolution.md` should mention it as one of the acknowledged unfinished
items from `TODOs.docx` rather than hiding it.

Claims in the README will be scoped to what was actually tested. Untested paths
will say so.

---

## 7. Risks

1. **Restructuring produces one enormous commit.** Mitigate by staging: move
   files first, then fix paths, then add docs — separate commits.
2. **Cross-platform edits to unverifiable code could break working Windows
   behaviour.** Mitigate by keeping Tier 2/3 changes minimal and mechanical, and
   never "improving" arm logic while touching it.
3. **Release assets are a manual step** the owner must perform after the first
   push; the fetch scripts fail with a clear message until then.
4. **Deleting `Extra/` is irreversible.** The vendor manuals should be archived
   elsewhere first if wanted.
5. **`git mv` at this scale can confuse rename detection**, making history harder
   to follow. Accept — the alternative is worse.
