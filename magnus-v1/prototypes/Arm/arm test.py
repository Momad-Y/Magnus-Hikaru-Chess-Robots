import Adafruit_PCA9685
import time


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

    # End processing
    def Cleanup(self):
        # The servo motor is set at 90°.
        self.SetPos(int(90))
        print('90')

def smooth(servo, start, end, total_delay):
    inc = 1
    if end < start:
        inc = -1
    unit_delay = total_delay / abs(start - end)
    for i in range(start, end, inc):
        servo.SetPos(i)
        time.sleep(unit_delay)
        
if __name__ == '__main__':
    servo0 = servo_Class(Channel=0, ZeroOffset=0)
    servo1 = servo_Class(Channel=1, ZeroOffset=0)
    servo2 = servo_Class(Channel=2, ZeroOffset=0)
    servo3 = servo_Class(Channel=3, ZeroOffset=0)
    servo4 = servo_Class(Channel=4, ZeroOffset=0)
    servo5 = servo_Class(Channel=5, ZeroOffset=0)
    #smooth(servo5, 30,90,4)
    smooth(servo5, 125,145,4)
    #smooth(servo4,90,40,4)
    #smooth(servo4,40,90,4)
    
    smooth(servo0,90,129,4)
    smooth(servo2,90,115,4)
    smooth(servo1,90,70,4)
    smooth(servo5,145,125,4)
    smooth(servo1,70,90,4)
    smooth(servo2,115,90,4)
    smooth(servo0,129,90,4)
   
    #smooth(servo0,90,115,4)
    #smooth(servo2,90,70,4)
    #smooth(servo1,90,50,4)
    #smooth(servo5,125,145,4)
    #smooth(servo1,50,90,4)
    #smooth(servo2,70,90,4)
    #smooth(servo0,115,90 ,4)