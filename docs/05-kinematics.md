# Kinematics: Getting the Arm to the Right Square

Both robots face the same problem: a camera sees a chessboard in **pixels**, and
an arm moves in **centimetres**. Everything here is the bridge between those two
coordinate frames.

The two generations solved it very differently, and that contrast is the most
interesting engineering story in this repository.

---

## Hikaru (v2), Dobot Magician, 4 DOF

### The two coordinate frames

The camera's origin `(0,0,0)` is the **top-left pixel** of its field of view.
The Dobot's origin is at the **base of the arm**. Neither knows about the other,
so a fixed transform between them has to be established once, by measurement.

### Rotation

The camera frame is brought into the arm frame by rotating `X_C` through 180° and
`Z_C` through 90°:

```
        ⎡ cos90   −sin90   0 ⎤        ⎡ 1     0        0     ⎤
  R_z = ⎢ sin90    cos90   0 ⎥  R_x = ⎢ 0  cos180  −sin180   ⎥
        ⎣   0        0     1 ⎦        ⎣ 0  sin180   cos180   ⎦
```

Multiplying them gives:

```
  ⎡ 0  1   0 ⎤
  ⎢ 1  0   0 ⎥
  ⎣ 0  0  −1 ⎦
```

### Translation

The measured offset from the camera origin to the arm origin is
**Dx = 20.5 cm**, **Dy = 36 cm**, **Dz = 0**.

### The homogeneous transform

Rotation and displacement combine into a single 4×4 matrix:

```
              ⎡ 0  1   0  20.5 ⎤
  T_camera→arm = ⎢ 1  0   0   36  ⎥
              ⎢ 0  0  −1    0  ⎥
              ⎣ 0  0   0    1  ⎦
```

### Pixels to centimetres

The transform expects centimetres, but the camera reports pixels, so a scale
factor is applied first:

```
  pixel2cm = camera_width_cm / camera_width_pixels
```

Multiply the camera-space coordinate by that ratio, push it through
`T_camera→arm`, and the result is a Cartesian target the Dobot understands.

### Inverse kinematics

The Dobot's own DLL performs the inverse kinematics. Hand it `(x, y, z, r)` and
it returns joint angles. Deriving those angles independently first requires the
forward kinematics, and therefore the DH model:

| Joint | α(i−1) | a(i−1) | d(i) | θ(i)    |
|-------|--------|--------|------|---------|
| 1     | 180°   | 0      | L1   | θ1      |
| 2     | 0°     | L2     | 0    | θ2      |
| 3     | 90°    | 0      | L3   | θ3 + 90 |

```
  L1 = 13.8 cm      L2 = 13.5 cm      L3 = 14.7 cm
```

### Why a suction cup

The Dobot Magician carries a 500 g payload over a 320 mm reach with ±0.2 mm
repeatability. A vacuum suction cup end effector removes the entire problem of
gripper alignment: it only needs to arrive above a piece and descend. That in
turn constrained the physical design: the chess pieces were 3D-printed flat-
topped specifically so a 2 cm suction cup could seat on them, and the board was
raised 4.5–5 cm to stay inside the arm's working envelope.

---

## Magnus (v1), 3D-printed arm, 6 DOF

Magnus had no SDK and no inverse-kinematics library. It drove six hobby servos
directly through a **PCA9685** 16-channel PWM driver over I²C from a Raspberry Pi.

Position control is open-loop pulse arithmetic:

```python
pulse = int((650 - 150) / 180 * angle + 150 + zero_offset)
```

150–650 counts spans 0–180°, with a per-servo `zero_offset` correcting mechanical
mounting error. There is no feedback: nothing measures whether the joint actually
arrived. Accuracy comes from calibration and from moving slowly.

The servo mix was chosen by torque demand: **MG996r** for the load-bearing
joints, **SG90** for the light ones, plus a **CYS-S0200**. The whole arm was
printed in ten parts.

---

## The comparison

| | Magnus (v1) | Hikaru (v2) |
|---|---|---|
| DOF | 6 | 4 |
| Position control | Open-loop PWM, no feedback | Vendor IK over USB |
| Repeatability | Uncalibrated; drifts | ±0.2 mm |
| End effector | Printed gripper | Vacuum suction cup |
| Calibration | Per-servo zero offsets | One homogeneous transform |
| Failure mode | Silent drift; misplaced pieces | Piece not picked up |

v1 controls *joints*. v2 controls *positions* and lets the vendor firmware solve
the joints. That single change is why v2's calibration collapses from six
hand-tuned servo offsets into one measured transform, and it is the clearest
example of what the second generation bought.
