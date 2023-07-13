import RPi.GPIO as GPIO
import time
from enum import Enum
import numpy as np
import signal                   
import sys

MOTOR_X_CW_PIN=13
MOTOR_X_CLK_PIN=6
MOTOR_Y_CW_PIN=26
MOTOR_Y_CLK_PIN=19
MOTOR_Z_CW_PIN=21
MOTOR_Z_CLK_PIN=20

END_SWITCH_X1=22
END_SWITCH_X2=23
END_SWITCH_Y1=24
END_SWITCH_Y2=25
END_SWITCH_Z1=27
END_SWITCH_Z2=17

X_LEN=27217
Y_LEN=19052
Z_LEN=26757

X_UNIT=9600
Z_UNIT=10200

X_OFFSET=4200
Y_OFFSET=6500
Z_OFFSET=3000

Y_IN_DIST=6400
Y_OUT_DIST=-7000
Z_UP_DIST=3500

OUT=GPIO.OUT
IN=GPIO.IN

ROTATION_T=0.0001
STOP_T=0.0001
ORIGIN=4000
GRID=(3,4)

class Motor(Enum):
    X = 0
    Y = 1
    Z = 2
class Dir(Enum):
    CW = True #GPIO.HIGH
    CCW = False #GPIO.LOW

class SmartFarmControl():
    def __init__(self):
        self.xpos=0
        self.ypos=0
        self.zpos=0
        self.xdir=True
        self.ydir=True
        self.zdir=True

        self.xlen=X_LEN
        self.ylen=Y_LEN
        self.zlen=Z_LEN
        self.counter=0
        self.xcounter=0
        self.ycounter=0
        self.zcounter=0

        self.emergencyStop=False
        
        self.modes=["initialization" for i in range(3)]
        self.setPinMode()

        
        # self.initializing_end_to_end()

        """
        An initialization function

        Parameters
        ----------
        origin: origin of passenger

        dest: destination of passenger

        state: one of WAIT, ONBOARD, ARRIVAL
            4200
        """
    def setPinMode(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(MOTOR_X_CW_PIN,OUT)
        # GPIO.setmode(GPIO.BCM)
        GPIO.setup(MOTOR_X_CLK_PIN,OUT)

        # GPIO.setmode(GPIO.BCM)
        GPIO.setup(MOTOR_Y_CW_PIN,OUT)
        # GPIO.setmode(GPIO.BCM)
        GPIO.setup(MOTOR_Y_CLK_PIN,OUT)

        # GPIO.setmode(GPIO.BCM)
        GPIO.setup(MOTOR_Z_CW_PIN,OUT)
        # GPIO.setmode(GPIO.BCM)
        GPIO.setup(MOTOR_Z_CLK_PIN,OUT)

        GPIO.setup(END_SWITCH_X1, IN, pull_up_down = GPIO.PUD_UP)
        GPIO.setup(END_SWITCH_X2, IN, pull_up_down = GPIO.PUD_UP)
        GPIO.add_event_detect(END_SWITCH_X1, GPIO.FALLING, callback=self.switchX1Pressed,bouncetime=300)
        GPIO.add_event_detect(END_SWITCH_X2, GPIO.FALLING, callback=self.switchX2Pressed,bouncetime=300)

        GPIO.setup(END_SWITCH_Y1, IN, pull_up_down = GPIO.PUD_UP)
        GPIO.setup(END_SWITCH_Y2, IN, pull_up_down = GPIO.PUD_UP)
        GPIO.add_event_detect(END_SWITCH_Y1, GPIO.FALLING, callback=self.switchY1Pressed,bouncetime=300)
        GPIO.add_event_detect(END_SWITCH_Y2, GPIO.FALLING, callback=self.switchY2Pressed,bouncetime=300)

        GPIO.setup(END_SWITCH_Z1, IN, pull_up_down = GPIO.PUD_UP)
        GPIO.setup(END_SWITCH_Z2, IN, pull_up_down = GPIO.PUD_UP)
        GPIO.add_event_detect(END_SWITCH_Z1, GPIO.FALLING, callback=self.switchZ1Pressed,bouncetime=300)
        GPIO.add_event_detect(END_SWITCH_Z2, GPIO.FALLING, callback=self.switchZ2Pressed,bouncetime=300)
    def getMotorNum(self,motor):
        if motor==Motor.X:return 0
        if motor==Motor.Y:return 1      
        if motor==Motor.Z:return 2
    def checkMode(self):
        for mode in self.modes:
            if mode=="initialization":
                return False
        return True
    def checkMotorMode(self,motor):
        num=self.getMotorNum(motor)
        if self.modes[num]=="initialization":
            return False
        else:
            return True

    def setMotorRotationDir(self,motor,dir):
        if motor==Motor.X:
            self.xdir=dir
            GPIO.output(MOTOR_X_CW_PIN,dir)
        elif motor==Motor.Y:
            self.ydir=dir
            GPIO.output(MOTOR_Y_CW_PIN,not dir)
        elif motor==Motor.Z:
            self.zdir=dir
            GPIO.output(MOTOR_Z_CW_PIN,not dir)
    def setMotorsDir(self,distances):
        if distances[0]>=0:
            self.setMotorRotationDir(Motor.X,True)
        else:
            self.setMotorRotationDir(Motor.X,False)
        if distances[1]>=0:
            self.setMotorRotationDir(Motor.Y,True)
        else:
            self.setMotorRotationDir(Motor.Y,False)
        if distances[2]>=0:
            self.setMotorRotationDir(Motor.Z,True)
        else:
            self.setMotorRotationDir(Motor.Z,False)

    def setMotorsRotationDir(self,motors,dir):
        for motor in motors:
            self.setMotorRotationDir(motor,dir)
    def setDirection(self,dir):
        if dir is True:
            return 1
        else:
            return -1

    def moveMotors(self,motors):
        if motors is None:
            return
        for motor in motors:
            if motor==Motor.X:
                self.xpos+=self.setDirection(self.xdir)
                GPIO.output(MOTOR_X_CLK_PIN,True)
            elif motor==Motor.Y:
                self.ypos+=self.setDirection(self.ydir)
                GPIO.output(MOTOR_Y_CLK_PIN,True)
            elif motor==Motor.Z:
                self.zpos+=self.setDirection(self.zdir)
                GPIO.output(MOTOR_Z_CLK_PIN,True)
        time.sleep(ROTATION_T)
        for motor in motors:
            if motor==Motor.X:
                GPIO.output(MOTOR_X_CLK_PIN,False)
            elif motor==Motor.Y:
                GPIO.output(MOTOR_Y_CLK_PIN,False)
            elif motor==Motor.Z:
                GPIO.output(MOTOR_Z_CLK_PIN,False)
        time.sleep(STOP_T)
    
    def movableMotors(self,distances):
        motors=[]
        if distances[0]!=0:
            motors.append(Motor.X)
        if distances[1]!=0:
            motors.append(Motor.Y)
        if distances[2]!=0:
            motors.append(Motor.Z)
        return motors

    def updateDistance(self,distances):
        updatedDistance=[]
        for distance in distances:
            if distance>0:
                updatedDistance.append(distance-1)
            elif distance<0:
                updatedDistance.append(distance+1)
            elif distance==0:
                updatedDistance.append(0)
        return updatedDistance
    def calculateCoordDistance(self,coord):
        x=GRID[1]-coord[1]-1
        z=GRID[0]-coord[0]-1
        print(x)
        print(z)
        distances=[(x*X_UNIT+X_OFFSET)-self.xpos,Y_OFFSET-self.ypos,(z*Z_UNIT+Z_OFFSET)-self.zpos]

        return distances
    def moveMotorsDistance(self,distances):
        distances=np.array(distances)
        distances=distances.astype(int)
        # print(distances)
        if distances[0]>=0:
            if distances[0]+self.xpos>=self.xlen:
                distances[0]=self.xlen-self.xpos-1
        else:
            if distances[0]+self.xpos<=0:
                distances[0]=-self.xpos+1
        if distances[1]>=0:
            if distances[1]+self.ypos>=self.ylen:
                distances[1]=self.ylen-self.ypos-1
        else:
            if distances[1]+self.ypos<=0:
                distances[1]=-self.ypos+1
        if distances[2]>=0:
            if distances[2]+self.zpos>=self.zlen:
                distances[2]=self.zlen-self.zpos-1
        else:
            if distances[2]+self.zpos<=0:
                distances[2]=-self.zpos+1
        maxdist=max(abs(distances))
        # print(distances)
        self.setMotorsDir(distances)
        for i in range(maxdist):
            # print(self.movableMotors(distances))
            self.moveMotors(self.movableMotors(distances))
            distances=self.updateDistance(distances)

    def moveMotorsToCoords(self,coords):
        distances=self.calculateCoordDistance(coords)
        self.moveMotorsDistance(distances)

    def moveMotorsToOrigin(self):
        # print(self.xpos)
        # print(self.ypos)
        # print(self.zpos)
        distances=[ORIGIN-self.xpos,ORIGIN-self.ypos,ORIGIN-self.zpos]
        # print(distances)
        self.moveMotorsDistance(distances)

    def moveMotorsOrigDest(self,orig,dest):
        self.moveMotorsToCoords(orig)
        time.sleep(0.1)
        self.moveMotorsDistance([0,Y_IN_DIST,0])#Y IN
        time.sleep(0.1)
        self.moveMotorsDistance([0,0,Z_UP_DIST])#Z UP
        time.sleep(0.1)
        self.moveMotorsDistance([0,Y_OUT_DIST,0])#Y IN   
        time.sleep(0.1)      #catch

        self.moveMotorsToCoords(dest)
        self.moveMotorsDistance([0,0,Z_UP_DIST])#Z UP
        time.sleep(0.1)
        self.moveMotorsDistance([0,Y_IN_DIST,0])#Y IN
        time.sleep(0.1)
        self.moveMotorsDistance([0,0,-Z_UP_DIST])#Z UP
        self.moveMotorsDistance([0,-Y_IN_DIST,0])#Y IN

        time.sleep(0.1)
        self.moveMotorsToOrigin()

    def test(self):
        self.setMotorsRotationDir([Motor.Y],True)
        counter=0
        self.counter=0
        while True:
            self.moveMotors([Motor.Y])
            self.counter+=1
            # print(self.counter)
            # if self.emergencyStop==True:
            #     counter+=1
            #     if counter==100:break
            if self.counter==1000:
                break


            ## y,z reverse


    def initializing_end_to_end(self):
        self.setMotorsRotationDir([Motor.X,Motor.Y,Motor.Z],True)
        self.counter=0
        while True:
            self.moveMotors([Motor.X,Motor.Y,Motor.Z])
            self.counter+=1
            print(self.counter)
            if self.checkMode():
                break
        self.counter=0
        while True:
            self.moveMotors([Motor.X])
            self.counter+=1
            # print(self.counter)
            if self.counter==1000:
                break
        
    def initializing_origin(self):
        motors=[Motor.X,Motor.Y,Motor.Z]
        self.setMotorsRotationDir(motors,False)
        self.counter=np.zeros(3)
        while True:
            self.moveMotors(motors)
            self.counter+=1
            if self.checkMode():
                break
            for motor in motors:
                if self.checkMotorMode(motor):
                    if self.counter[self.getMotorNum(motor)]==ORIGIN:
                        motors.remove(motor)
        self.moveMotorsToOrigin()

        
    def switchX1Pressed(self,channel):
        if self.modes[0]=="initialization":
            print("x1")
            self.counter[0]=0
            self.xpos=0
            self.xdir=True
            # self.xlen=self.counter-self.xlen
            self.modes[0]="normal"
            self.setMotorRotationDir(Motor.X,True)
        else:
            self.xpos=0
            self.xdir=True
            self.setMotorRotationDir(Motor.X,True)
    def switchX2Pressed(self,channel):
        if self.modes[0]=="initialization":
            print("x2")
            self.xdir=False
            # self.xlen=self.counter
            self.setMotorRotationDir(Motor.X,False)
        else:
            self.xpos=self.xlen
            self.xdir=False
            self.setMotorRotationDir(Motor.X,False)
    def switchY1Pressed(self,channel):
        if self.modes[1]=="initialization":
            print("y1")
            self.counter[1]=0
            self.ypos=0
            self.ydir=True
            # self.ylen=self.counter-self.ylen
            self.modes[1]="normal"
            self.setMotorRotationDir(Motor.Y,True)
        else:
            self.ypos=0
            self.ydir=True
            self.setMotorRotationDir(Motor.Y,True)
    def switchY2Pressed(self,channel):
        if self.modes[1]=="initialization":
            print("y2")
            self.ydir=False
            # self.ylen=self.counter
            self.setMotorRotationDir(Motor.Y,False)
            # self.emergencyStop=True
        else:
            self.ypos=self.ylen
            self.ydir=False
            self.setMotorRotationDir(Motor.Y,False)
    def switchZ1Pressed(self,channel):
        if self.modes[2]=="initialization":
            self.counter[2]=0
            print("z1")
            self.zpos=0
            self.zdir=True
            # self.zlen=self.counter-self.zlen
            self.modes[2]="normal"
            self.setMotorRotationDir(Motor.Z,True)
        else:
            self.zpos=0
            self.zdir=True
            self.setMotorRotationDir(Motor.Z,True)
    def switchZ2Pressed(self,channel):
        if self.modes[2]=="initialization":
            print("z2")
            self.zdir=False
            # self.zlen=self.counter
            self.setMotorRotationDir(Motor.Z,False)
        else:
            self.zpos=self.zlen
            self.zdir=False
            self.setMotorRotationDir(Motor.Z,False)

    


