# v1 → v2: What Changed and Why

Magnus Armsen and Hikaru Nakarmsen solve the same problem, a robot arm that
plays chess against a human, nine months apart, with an overlapping team, for
two different courses. This is what the second attempt changed, and why.

---

## The two projects at a glance

| | **Magnus Armsen (v1)** | **Hikaru Nakarmsen (v2)** |
|---|---|---|
| Course | GN312, Embedded Systems & IoT | RB310, Fundamentals of Robotics |
| Proposal | 18 March 2023 | November 2023 |
| Team | Hazem Abdelghafar, Mohamed Abdelnasser, Belal Sameh, Mohamed Elfeel | Hazem Abdelghafar, Mohamed Abdelnasser, Mohamed Elfeel |
| Arm | 3D-printed, 6 DOF, hobby servos | Dobot Magician, 4 DOF |
| Controller | Raspberry Pi 4B 8 GB | Desktop PC over USB |
| Interface | Flask web app | Tkinter desktop app |
| Engine | Stockfish | Stockfish + DRLCE |
| Budget | 9,000 EGP | 1,000 EGP |

The budget line is the headline: **v2 cost about a ninth of v1**, because the
arm stopped being something they built.

The team also shrank from four to three: **Belal Sameh was part of Magnus (v1)
and not Hikaru (v2)**. v1 was a four-person Embedded Systems & IoT project; v2
was taken on by three of the same people for a different course, Robotics.

---

## Change 1. Buy the arm instead of building it

v1's central engineering effort went into the arm itself: ten 3D-printed parts,
six servos across three types, a PCA9685 driver, and a wiring loom, all
controlled open-loop with no position feedback. The proposal's own risk list
opens with "controlling the robotic arm and its degrees of freedom efficiently,
a problem that has never been addressed before by any of the group members."

v2 bought a Dobot Magician: 4 DOF, 500 g payload, 320 mm reach, **±0.2 mm
repeatability**, with inverse kinematics in vendor firmware.

**What that bought:** repeatability that can be quoted as a number, and the
disappearance of an entire class of failure. A servo that silently doesn't reach
its commanded angle puts a piece on the wrong square with no error anywhere.

**What it cost:** two degrees of freedom, and a hard dependency on a proprietary
Windows-first SDK. v1's arm can be rebuilt by anyone with a printer and 9,000
EGP. v2's cannot be rebuilt at all: you buy it or you don't have it.

## Change 2. Suction instead of grasping

v1 printed a multi-link gripper with a separate gripper base and four grip links.
Grasping needs the fingers aligned with the piece in two axes.

v2 switched to a vacuum suction cup, and then **redesigned the game around it**:
chess pieces were 3D-printed with flat tops sized for a 2 cm cup (2.25–2.5 cm),
and the board was raised 4.5–5 cm to sit inside the arm's envelope. The
`TODOs.docx` shows this being worked out as measurements: cup diameter, maximum
descent, optimal board dimensions of 29×29, 28×28 or 27×27 cm.

This is the most quietly significant decision in the project. Rather than making
the manipulator cleverer, they **changed the world so a dumb manipulator would
work**. Suction only requires arriving above a piece and descending.

## Change 3. Desktop app instead of web app

v1's Flask app is genuinely nice: a split black-and-white card design,
chessboard.js, a chat easter egg, a team page. But it meant maintaining a
browser↔Python protocol, documented in `Overthinking.txt` as a hand-written table
of interchange variables and error codes (`Camera not found (12)`, `Couldn't
calibrate (55)`, `Move Incorrect (100)`).

`TODOs.docx` records v2 reopening the question from scratch:

> **Main Code:** Write the Outline. CLI? GUI App? Web App?

They chose a Tkinter desktop app. The protocol layer disappears, because the UI and the
robot logic are the same process, sharing objects directly instead of serialising
state across HTTP.

**What it cost:** the app is no longer reachable from another machine, and
Tkinter looks considerably plainer than the v1 web design.

## Change 4. A second engine, adopted not written

v1 used Stockfish at fixed maximum strength. v2 kept Stockfish with a 1–4
difficulty scale and added **DRLCE**, an AlphaZero-style 20×256 residual network
with MCTS, as difficulty 5.

**DRLCE was adopted, not written.** Its network, search and encoder come from
[jackdawkins11/pytorch-alpha-zero](https://github.com/jackdawkins11/pytorch-alpha-zero),
along with the pretrained weights; this team wrote the wrapper that loads it and
exposes it through the same interface as the Stockfish path. See
[`hikaru-v2/DRLCE/ATTRIBUTION.md`](../hikaru-v2/DRLCE/ATTRIBUTION.md).

Competitively it adds nothing. At 10 rollouts per move it is far weaker than the
Stockfish beside it. It exists because the v2 proposal's stated goal was to
"learn more about chess engines and the AI behind it", and integrating a working
implementation serves that goal. Read it as a learning artifact, not a rival.

## Change 5. The vision module grew up

Both wrote their own `C2M`. v2's is 3.5× larger and differs by 896 lines. The
substantive changes: tile size derived from camera resolution rather than
hardcoded at 50 px, a per-pixel difference metric instead of a total, and most
importantly `cam_2_arm_transformation()`, which makes the vision module
responsible for answering *"where is this square in the arm's frame?"*

That last one exists because of Change 1. v1 didn't need it: a human-tuned servo
table encoded the board geometry implicitly. v2 controls Cartesian positions, so
something has to convert pixels into centimetres, and that something lives in
`C2M`. See [03-vision-c2m.md](03-vision-c2m.md) and [05-kinematics.md](05-kinematics.md).

---

## What neither generation finished

Both proposals list the same future work: a match database, and putting a
wrongly-moved piece back rather than only alerting. Neither shipped.

v1's proposal also promised voice control, framed around accessibility: players
who know the game but cannot easily move the pieces would speak their move
instead. It survives in v2's `TODOs.docx` as "Add voice control feature to enable
people with disabilities to play against the arm", still unbuilt.

And v2's **Instructions screen is empty**. `instructions_label` carries the text
`"Instructions:"` and nothing else; the screen renders a heading and two buttons.
The main menu labels that button "Instructions (Important!)".

These are left visible rather than tidied away. They are the honest shape of two
university projects delivered against a deadline.
