import RPi.GPIO as GPIO
import time
from enum import Enum
import signal                   
import sys

MOTOR_X_CW_PIN=1
MOTOR_X_CLK_PIN=2
MOTOR_Y_CW_PIN=1
MOTOR_Y_CLK_PIN=2
MOTOR_Z_CW_PIN=1
MOTOR_Z_CLK_PIN=2

END_SWITCH_X1=1
END_SWITCH_X2=1
END_SWITCH_Y1=1
END_SWITCH_Y2=1
END_SWITCH_Z1=1
END_SWITCH_Z2=1

X_LEN=1.0
Y_LEN=2.0
Z_LEN=3.0

OUT=GPIO.OUT
IN=GPIO.IN


class Motor(Enum):
    X = 0
    Y = 1
    Z = 2
class Dir(Enum):
    CW = True #GPIO.HIGH
    CCW = False #GPIO.LOW
class Limit(Enum):
    LEFT=0
    RIGHT=1

class SmartFarmControl():
    def __init__(self):
        self.xpos=0
        self.ypos=0
        self.zpos=0
        self.xmax=0
        self.ymax=0
        self.zmax=0
        self.counter=0
        self.xcounter=0
        self.ycounter=0
        self.zcounter=0

        self.xlimit=None
        self.ylimit=None
        self.zlimit=None

        self.setPinMode()

        
        self.initializing_end_to_end()

        """
        An initialization function

        Parameters
        ----------
        origin: origin of passenger

        dest: destination of passenger

        state: one of WAIT, ONBOARD, ARRIVAL
            
        """
    def setPinMode(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(MOTOR_X_CW_PIN,OUT)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(MOTOR_X_CLK_PIN,OUT)

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(MOTOR_Y_CW_PIN,OUT)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(MOTOR_Y_CLK_PIN,OUT)

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(MOTOR_Z_CW_PIN,OUT)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(MOTOR_Z_CLK_PIN,OUT)

        GPIO.setup(END_SWITCH_X1, IN, pull_up_down = GPIO.PUD_DOWN)
        GPIO.setup(END_SWITCH_X2, IN, pull_up_down = GPIO.PUD_DOWN)
        GPIO.add_event_detect(END_SWITCH_X1, GPIO.RISING, callback=self.switchXPressed)
        GPIO.add_event_detect(END_SWITCH_X2, GPIO.RISING, callback=self.switchXPressed)

        GPIO.setup(END_SWITCH_Y1, IN, pull_up_down = GPIO.PUD_DOWN)
        GPIO.setup(END_SWITCH_Y2, IN, pull_up_down = GPIO.PUD_DOWN)
        GPIO.add_event_detect(END_SWITCH_X1, GPIO.RISING, callback=self.switchYPressed)
        GPIO.add_event_detect(END_SWITCH_X2, GPIO.RISING, callback=self.switchYPressed)

        GPIO.setup(END_SWITCH_Z1, IN, pull_up_down = GPIO.PUD_DOWN)
        GPIO.setup(END_SWITCH_Z2, IN, pull_up_down = GPIO.PUD_DOWN)
        GPIO.add_event_detect(END_SWITCH_X1, GPIO.RISING, callback=self.switchZPressed)
        GPIO.add_event_detect(END_SWITCH_X2, GPIO.RISING, callback=self.switchZPressed)
        
    def setMotorRotationDir(motor,dir):
        if motor==Motor.X:
            GPIO.output(MOTOR_X_CW_PIN,dir)
        elif motor==Motor.Y:
            GPIO.output(MOTOR_Y_CW_PIN,dir)
        elif motor==Motor.Z:
            GPIO.output(MOTOR_Z_CW_PIN,dir)

    def initializing_end_to_end(self):
        self.setMotorRotationDir(Motor.X,Dir.CW)
        self.setMotorRotationDir(Motor.Y,Dir.CW)
        self.setMotorRotationDir(Motor.Z,Dir.CW)

        self.counter=0
        while True:
            GPIO.output(MOTOR_X_CLK_PIN,True)
            GPIO.output(MOTOR_Y_CLK_PIN,True)
            GPIO.output(MOTOR_Z_CLK_PIN,True)
            time.sleep(0.003)
            GPIO.output(MOTOR_X_CLK_PIN,False)
            GPIO.output(MOTOR_Y_CLK_PIN,False)
            GPIO.output(MOTOR_Z_CLK_PIN,False)
            time.sleep(0.001)
            self.counter+=1
        
    def switchXPressed(self):
        left = GPIO.input(END_SWITCH_X1)
        right= GPIO.input(END_SWITCH_X2)

        if left==True:
            self.xlimit=Limit.LEFT

        elif right==True:
            self.xlimit=Limit.RIGHT

    def switchYPressed(self):
        left = GPIO.input(END_SWITCH_X1)
        right= GPIO.input(END_SWITCH_X2)

        if left==True:
            self.ylimit=Limit.LEFT
        elif right==True:
            self.ylimit=Limit.RIGHT
        
    def switchZPressed(self):
        left = GPIO.input(END_SWITCH_X1)
        right= GPIO.input(END_SWITCH_X2)

        if left==True:
            self.zlimit=Limit.LEFT

        elif right==True:
            self.zlimit=Limit.RIGHT

    


