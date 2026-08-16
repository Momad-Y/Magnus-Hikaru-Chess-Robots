# Running the Code

Both projects originally ran only on Windows, with hardcoded absolute paths.
They now run on **Linux, macOS and Windows** — with one honest caveat: the arm
layers cannot be verified, because the hardware is no longer available.

## What actually runs without hardware

| Layer | Without any hardware | Notes |
|---|---|---|
| Magnus web app | **Yes** | All three pages render |
| Hikaru desktop GUI | **Yes** | Menus, settings, difficulty, board view |
| Stockfish engine | **Yes** | Any recent build |
| DRLCE neural engine | **Yes** | CPU or GPU |
| Vision (C2M) | Partly | Needs a webcam for live capture; sample images included |
| Magnus servo arm | **No** | Raspberry Pi + PCA9685 over I²C |
| Hikaru Dobot arm | **No** | Dobot Magician over USB |

Missing hardware degrades gracefully: `ARM.py` imports fine and refuses motion
with an explanation, and `C2M.init_cam()` returns `None` when there is no camera.

---

## 1. Stockfish

Neither project vendors the engine any more — four copies of a Windows binary
and its NNUE file accounted for roughly 380 MB. Install it instead:

```bash
# Linux (Debian/Ubuntu)
sudo apt install stockfish
# Linux (Arch)
sudo pacman -S stockfish
# macOS
brew install stockfish
# Windows
winget install Stockfish.Stockfish
```

Or download from [stockfishchess.org](https://stockfishchess.org/download/) and
point at it:

```bash
export STOCKFISH_PATH=/full/path/to/stockfish
```

Resolution order is `$STOCKFISH_PATH` → a local `stockfish.txt` → `PATH` → a
bundled `engine/` directory. If all fail you get install instructions, not a
stack trace. Developed against Stockfish 15.1; any recent release speaks the
same UCI protocol.

## 2. Python

Both projects target **Python 3.11**.

> **Tkinter gotcha.** Hikaru's GUI needs Tk, which is a property of your
> *interpreter build*, not your OS. Several common Python builds omit it —
> pyenv compiles without `_tkinter` unless Tk headers were present, and `uv`'s
> standalone 3.11 has no `_tkinter` either. Check before filing a bug:
>
> ```bash
> python -c "import tkinter; print(tkinter.TkVersion)"
> ```
>
> If that fails: install Tk (`sudo pacman -S tk`, `sudo apt install python3-tk`,
> `brew install python-tk`) and rebuild, or use a build that includes it.

## 3. Hikaru (v2) — desktop app

```bash
cd hikaru-v2
python -m venv .venv && . .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python ../tools/fetch_weights.py                 # 93 MB DRLCE weights
python main.py
```

Then open **Settings** and set the camera ID if the default (0) is wrong.

Difficulty 1–4 are Stockfish at increasing depth and skill. **Difficulty 5 is
DRLCE**, the neural engine — not a harder Stockfish.

### Driving the Dobot outside Windows

Only the Windows `DobotDll.dll` is included here. Linux and macOS need
`libDobotDll.so` / `libDobotDll.dylib` from Dobot's own
[SDK downloads](https://download.dobot.cc/), placed next to the DLL in
`hikaru-v2/Dobot/`.

**This path is untested.** There is no arm to test it against. The loader's
Linux branch called `cdll.loadLibrary` — not a real ctypes API — so it had never
worked; that is now `cdll.LoadLibrary`, but a fixed call is not a verified one.

## 4. Magnus (v1) — web app

```bash
cd magnus-v1
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
python src/app.py
```

Then open <http://127.0.0.1:9999/>.

### Driving the servo arm

Needs a Raspberry Pi with I²C enabled and a PCA9685 wired to six servos:

```bash
sudo raspi-config          # Interface Options -> I2C -> enable
pip install Adafruit_PCA9685
```

Then uncomment `import ARM as arm` and the `arm.moveArm(...)` calls in
`src/app.py` — they are commented out so the web app runs anywhere.

**Also untested**, for the same reason. And the six per-servo `ZeroOffset`
constants are calibrated to one physical build; a new arm needs new ones.

---

## What was changed to make this work

| Fix | Where |
|---|---|
| Stockfish resolved at runtime | `engine_path.py` in both projects |
| Paths anchored to the module, not the CWD | `GUI.py`, `app.py` |
| Import-time `os.chdir(cwd + "\Dobot")` removed | `Dobot/DoBotArm.py` |
| `cdll.loadLibrary` → `cdll.LoadLibrary` | `Dobot/DobotDllType.py` |
| `.ico` → `.png` (OpenCV cannot decode `.ico`) | `Images/icon.png` |
| `iconbitmap()` → `iconphoto()` | `GUI.py` |
| `"Courier"` → `"Courier New"` at 42 sites | `GUI.py` |
| `Adafruit_PCA9685` import guarded | `ARM.py` (both copies) |
| Invalid `\P` / `\s` escapes removed | `prototypes/CEP/*.py` |
| Stale `Test/` paths repointed | `GUI.py` |

The `os.chdir` one deserves a note. It ran at *import* time and mutated the
process working directory as a side effect — and the old `cwd + "/.."` line in
`GUI.py` existed purely to undo it. Removing one required fixing the other.
