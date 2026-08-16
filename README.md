# Magnus & Hikaru — Two Generations of a Chess-Playing Robot Arm

Two university robotics projects that solve the same problem — *a robot arm that
sees your move and plays its own* — nine months apart, with an overlapping team,
using completely different hardware.

<p align="center">
  <img src="media/clips/magnus-demo.webp" width="48%" alt="Magnus Armsen, a 3D-printed arm, moving a piece">
  <img src="media/clips/hikaru-demo.webp" width="48%" alt="Hikaru Nakarmsen, a Dobot Magician, moving a piece">
</p>

<p align="center"><em>Left: Magnus Armsen (v1), 3D-printed, 6 DOF. Right: Hikaru Nakarmsen (v2), Dobot Magician, 4 DOF.</em></p>

Both are named after chess world number ones — Magnus **Carlsen** and Hikaru
**Nakamura** — with an arm pun welded on.

---

## The two generations

| | **Magnus Armsen (v1)** | **Hikaru Nakarmsen (v2)** |
|---|---|---|
| Course | GN312 — Embedded Systems & IoT | RB310 — Fundamentals of Robotics |
| Date | March 2023 | November 2023 |
| Arm | 3D-printed, 6 DOF, hobby servos | Dobot Magician, 4 DOF |
| End effector | Printed gripper | Vacuum suction cup |
| Controller | Raspberry Pi 4B 8 GB | Desktop PC over USB |
| Camera | Raspberry Pi HQ Camera | Logitech C270 |
| Interface | Flask web app | Tkinter desktop app |
| Engine | Stockfish | Stockfish + a vendored AlphaZero (DRLCE) |
| Repeatability | Uncalibrated | ±0.2 mm |
| Budget | 9,000 EGP | 1,000 EGP |

Both robots work the same way: photograph the board, photograph it again after
your move, diff the 64 squares, infer what you played, ask a chess engine for a
reply, and move a piece.

---

## Magnus Armsen — v1

<p align="center">
  <img src="media/magnus/magnus-arm-hero.png" width="80%" alt="The Magnus arm above its calibration board">
</p>

The arm itself was the project. Ten 3D-printed parts, six servos across three
types, a PCA9685 PWM driver, and a Raspberry Pi — all open-loop, with nothing
measuring whether a joint actually arrived where it was told.

The interface is a Flask web app: a split black-and-white card design,
chessboard.js for the board, live status, difficulty selection, and a chat
easter egg. The browser and the Python backend talk through a hand-designed
protocol of interchange variables and numeric error codes, written up in
[`magnus-v1/docs/protocol-notes.txt`](magnus-v1/docs/protocol-notes.txt).

<p align="center">
  <img src="media/ui/magnus-home.png" width="32%" alt="Magnus web app home page">
  <img src="media/ui/magnus-play.png" width="32%" alt="Magnus play page with the board and calibration modal">
  <img src="media/ui/magnus-links.png" width="32%" alt="Magnus team page">
</p>

**→ [`magnus-v1/`](magnus-v1/)** · [full demo video](../../releases) · 9,000 EGP · reproducible if you have a printer

---

## Hikaru Nakarmsen — v2

<p align="center">
  <img src="media/hikaru/hikaru-rig-hero.png" width="80%" alt="The Hikaru rig: Dobot Magician, board, camera and laptop">
</p>

The second generation bought the arm and spent the effort elsewhere. A Dobot
Magician brings ±0.2 mm repeatability and inverse kinematics in firmware, so the
work moved up the stack: a camera-to-arm coordinate transform, a much stronger
vision module, and a second chess engine integrated alongside Stockfish.

The interface became a Tkinter desktop app — no browser, no protocol layer, the
UI and robot logic in one process.

<p align="center">
  <img src="media/ui/hikaru-gui-main.png" width="32%" alt="Hikaru main menu">
  <img src="media/ui/hikaru-play.png" width="32%" alt="Hikaru play screen: virtual board plus two camera frames">
  <img src="media/ui/hikaru-settings.png" width="32%" alt="Hikaru settings screen">
</p>

The play screen shows all three views at once — the virtual board, and the
previous and current camera frames it diffs to work out your move.

**→ [`hikaru-v2/`](hikaru-v2/)** · [full demo video](../../releases) · 1,000 EGP · needs a Dobot Magician

---

## What changed between them

The most interesting thing here is not either robot; it is the **delta**.

- **The arm stopped being the project.** v1's central risk was "controlling the
  robotic arm — a problem never addressed before by any group member". v2 bought
  that problem off the shelf for a ninth of the budget.
- **Suction beat grasping — by changing the world.** Rather than making the
  gripper cleverer, v2 3D-printed flat-topped chess pieces sized for a 2 cm
  suction cup and raised the board 4.5 cm. A dumb manipulator became sufficient.
- **The protocol layer vanished.** Moving from web app to desktop app deleted an
  entire hand-written browser↔Python contract.
- **Vision grew a coordinate system.** v1's `C2M` only answered *"what moved?"*.
  v2's also answers *"where is that square in the arm's frame?"* — because v2
  commands Cartesian positions instead of joint angles.

Full write-up: **[docs/02-evolution.md](docs/02-evolution.md)**

---

## Documentation

| | |
|---|---|
| [01 — Overview](docs/01-overview.md) | What both projects are, at a glance |
| [02 — Evolution](docs/02-evolution.md) | v1 → v2: what changed and why |
| [03 — Vision (C2M)](docs/03-vision-c2m.md) | Board detection and move inference |
| [04 — Chess engines](docs/04-chess-engines.md) | Stockfish, and the vendored AlphaZero |
| [05 — Kinematics](docs/05-kinematics.md) | DH model and the camera→arm transform |
| [06 — Hardware](docs/06-hardware.md) | Both bills of materials, servos vs Dobot |
| [07 — Running the code](docs/07-running.md) | Setup on Linux, macOS and Windows |

---

## Repository map

```
├── docs/            the write-ups above
├── media/           stills and clips from the demo footage
├── magnus-v1/       Raspberry Pi + servos + Flask
│   ├── src/           the integrated app
│   ├── web/           templates and static assets
│   ├── prototypes/    per-subsystem code, before integration
│   ├── hardware/      STLs, schematics, bill of materials
│   └── docs/          proposal, documentation, protocol notes
├── hikaru-v2/       Dobot Magician + Tkinter + DRLCE
│   ├── Dobot/         vendor SDK wrapper
│   ├── DRLCE/         AlphaZero network and MCTS
│   ├── hardware/      chess piece STL, RoboDK station
│   ├── testing/       test scripts and captured board images
│   └── docs/          proposal, documentation, TODO list
└── tools/           fetch scripts for large release assets
```

## Quick start

Both projects run on Linux, macOS and Windows. Neither arm can be driven without
its hardware, but **the vision, engines and both interfaces run on a laptop**.

```bash
git clone https://github.com/Momad-Y/Magnus-Hikaru-Chess-Robots.git
cd Magnus-Hikaru-Chess-Robots

# Hikaru — desktop app
cd hikaru-v2 && pip install -r requirements.txt
python ../tools/fetch_weights.py && python main.py

# Magnus — web app at http://127.0.0.1:9999
cd magnus-v1 && pip install -r requirements.txt && python src/app.py
```

Stockfish is not vendored — install it, or set `STOCKFISH_PATH`. Full details
and the Tkinter gotcha: **[docs/07-running.md](docs/07-running.md)**.

---

## Team

**Magnus Armsen (v1)** — Hazem Abdelghafar · Mohamed Abdelnasser ·
**Belal Sameh** · Mohamed Elfeel
Supervised by Dr. Omar Shalash and Eng. Hossam Eldeen.

**Hikaru Nakarmsen (v2)** — Hazem Abdelghafar · Mohamed Abdelnasser ·
Mohamed Elfeel

*Belal Sameh was part of the v1 team only; v2 was built by the remaining three
for a different course.*

Arab Academy for Science, Technology & Maritime Transport (AAST).

## Licence and attribution

Project code is Apache-2.0 — see [LICENSE](LICENSE). Third-party components keep
their own licences; see [NOTICE](NOTICE).

**DRLCE**, the neural chess engine at difficulty 5, is adapted from
[jackdawkins11/pytorch-alpha-zero](https://github.com/jackdawkins11/pytorch-alpha-zero)
— credit to its author. Only the wrapper around it was written here. See
[`hikaru-v2/DRLCE/ATTRIBUTION.md`](hikaru-v2/DRLCE/ATTRIBUTION.md).
