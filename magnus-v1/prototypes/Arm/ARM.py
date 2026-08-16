import time

# Adafruit_PCA9685 talks to a PCA9685 PWM driver over I2C, so it only imports on
# a Raspberry Pi with I2C enabled. Guarding it keeps this module readable and
# importable on any machine; only actual servo motion needs the hardware.
try:
    import Adafruit_PCA9685  # type: ignore

    PCA9685_AVAILABLE = True
    _IMPORT_ERROR = None
except Exception as exc:  # ImportError on a PC, OSError if /dev/i2c is missing
    Adafruit_PCA9685 = None  # type: ignore
    PCA9685_AVAILABLE = False
    _IMPORT_ERROR = exc



class servo_Class:
    # "Channel" is the channel for the servo motor on PCA9685
    # "ZeroOffset" is a parameter for adjusting the reference position of the servo motor
    def __init__(self, Channel, ZeroOffset):
        self.Channel = Channel
        self.ZeroOffset = ZeroOffset

        # Initialize Adafruit_PCA9685
        self.pwm = Adafruit_PCA9685.PCA9685(address=0x40)
        self.pwm.set_pwm_freq(int(60))

    # Angle setting
    def SetPos(self, pos):
        # PCA9685 controls angles with pulses, 150~650 of pulses correspond to 0~180° of angle
        pulse = int((650-150)/180*pos+150+self.ZeroOffset)
        self.pwm.set_pwm(self.Channel, 0, pulse)


class _UnavailableServo:
    """Stand-in used when there is no PCA9685, so importing ARM.py still works.

    Every motion call raises with an explanation instead of failing obscurely.
    """

    def __init__(self, Channel, ZeroOffset):
        self.Channel = Channel
        self.ZeroOffset = ZeroOffset

    def SetPos(self, pos):
        raise RuntimeError(
            f"Cannot drive servo on channel {self.Channel}: the Adafruit_PCA9685 "
            f"library is unavailable ({_IMPORT_ERROR!r}).\n"
            "Magnus's arm needs a Raspberry Pi with I2C enabled and a PCA9685 "
            "driver wired up. The vision, engine and web layers run anywhere; "
            "only physical arm motion requires the hardware."
        )



_servo = servo_Class if PCA9685_AVAILABLE else _UnavailableServo

total_delay=4
servo0 = _servo(Channel=0, ZeroOffset=0)
servo1 = _servo(Channel=1, ZeroOffset=0)
servo2 = _servo(Channel=2, ZeroOffset=0)
servo3 = _servo(Channel=3, ZeroOffset=0)
servo4 = _servo(Channel=4, ZeroOffset=0)
servo5 = _servo(Channel=5, ZeroOffset=0)


angles = [[62, 30, 60],  [62, 40, 70],  [62, 50, 85],  [62, 60, 105],  [54, 70, 115],  [54, 80, 130],  [54, 90, 145],  [54, 100, 170],
          [70, 30, 60],  [70, 40, 70],  [70, 50, 85],  [70, 60, 105],  [62, 70, 120],  [62, 80, 130],  [62, 90, 145],  [62, 100, 170],
          [78, 30, 60],  [78, 40, 70],  [78, 50, 85],  [78, 60, 105],  [74, 70, 120],  [74, 80, 130],  [74, 90, 145],  [74, 100, 170],
          [89, 30, 60],  [89, 40, 70],  [89, 50, 85],  [89, 60, 105],  [85, 70, 120],  [85, 80, 130],  [85, 90, 145],  [85, 100, 170],
          [100, 30, 60], [100, 40, 70], [100, 50, 85], [100, 60, 105], [100, 70, 120], [100, 80, 130], [100, 90, 145], [100, 100, 170],
          [107, 30, 60], [107, 40, 70], [107, 50, 85], [107, 60, 105], [107, 70, 120], [107, 80, 130], [107, 90, 145], [107, 100, 170],
          [115, 30, 60], [115, 40, 70], [115, 50, 85], [115, 60, 105], [120, 70, 120], [120, 80, 130], [120, 90, 145], [120, 100, 170],
          [122, 30, 60], [122, 40, 70], [122, 50, 85], [122, 60, 105], [129, 70, 115], [129, 80, 130], [129, 90, 145], [129, 100, 170]]


def goto(move):
    if(move[0]=='a'):
        index1=0
    elif(move[0]=='b'):
        index1=1
    elif(move[0]=='c'):
        index1=2
    elif(move[0]=='d'):
        index1=3
    elif(move[0]=='e'):
        index1=4
    elif(move[0]=='f'):
        index1=5
    elif(move[0]=='g'):
        index1=6
    elif(move[0]=='h'):
        index1=7

    index2=int(move[1])-1

    mygoal=angles[index1][index2]
    smooth(servo0, 90, mygoal[0], total_delay)
    smooth(servo2, 90, mygoal[2], total_delay)
    smooth(servo1, 150, mygoal[1], total_delay)


def grab():
    smooth(servo5, 145, 125, total_delay)


def drop():
    smooth(servo5, 125, 145, total_delay)


def initial(move):
    if(move[0]=='a'):
        index1=0
    elif(move[0]=='b'):
        index1=1
    elif(move[0]=='c'):
        index1=2
    elif(move[0]=='d'):
        index1=3
    elif(move[0]=='e'):
        index1=4
    elif(move[0]=='f'):
        index1=5
    elif(move[0]=='g'):
        index1=6
    elif(move[0]=='h'):
        index1=7

    index2=int(move[1])-1

    mygoal=angles[index1][index2]
    smooth(servo1, mygoal[1], 150, total_delay)
    smooth(servo2, mygoal[2], 90, total_delay)
    smooth(servo0, mygoal[0], 90, total_delay)


def gotobox():
    smooth(servo0, 90, 45 , total_delay)

def gofrombox():
    smooth(servo0, 45, 90 , total_delay)

def smooth(servo, start, end, total_delay):
    inc = 1
    if end < start:
        inc = -1
    unit_delay = total_delay / abs(start - end)
    for i in range(start, end, inc):
        servo.SetPos(i)
        time.sleep(unit_delay)


def moveArm(moves,kill):

    start = moves[0]+moves[1]
    end = moves[2]+moves[3]
   
    
    if (kill == False):
        goto(start)
        grab()
        initial(start)
        goto(end)
        drop()
        initial(end)
    else:
        goto(end)
        grab()
        initial(end)
        gotobox()
        drop()
        gofrombox()
        goto(start)
        grab()
        initial(start)
        goto(end)
        drop()
        initial(end)
