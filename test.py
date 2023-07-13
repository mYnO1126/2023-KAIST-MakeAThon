import RPi.GPIO as GPIO
import time
import SmartFarmControl
from enum import Enum


control=SmartFarmControl.SmartFarmControl()
#control.test()
# control.moveMotorsDistance([1000,1000,1000])
# control.initializing_origin()
control.moveMotorsToCoords((0,0))

# control.initializing_end_to_end(1)

# control.initializing_end_to_end(2)
GPIO.cleanup()

# OUT=GPIO.OUT
# IN=GPIO.IN
# END_SWITCH_X1=22
# END_SWITCH_X2=23
# END_SWITCH_X1=22
# END_SWITCH_X2=23
# END_SWITCH_Y1=24
# END_SWITCH_Y2=25
# END_SWITCH_Z1=17
# END_SWITCH_Z2=27

# # def switchXPressed(channel):
# #     left = GPIO.input(END_SWITCH_X1)
# #     right= GPIO.input(END_SWITCH_X2)
# #     print("aaa")
# #     print(left)
# #     print(right)


# class Test():
#     def setMode(self):        
#         self.a=1
#         GPIO.setmode(GPIO.BCM)
#         GPIO.setup(END_SWITCH_X1, IN, pull_up_down = GPIO.PUD_UP)
#         GPIO.setup(END_SWITCH_X2, IN, pull_up_down = GPIO.PUD_UP)
#         GPIO.add_event_detect(END_SWITCH_X1, GPIO.FALLING, callback=self.switchXPressed)
#         GPIO.add_event_detect(END_SWITCH_X2, GPIO.FALLING, callback=self.switchXPressed,bouncetime=300)
#         GPIO.setup(END_SWITCH_Y1, IN, pull_up_down = GPIO.PUD_UP)
#         GPIO.setup(END_SWITCH_Y2, IN, pull_up_down = GPIO.PUD_UP)
#         GPIO.add_event_detect(END_SWITCH_Y1, GPIO.FALLING, callback=self.switchYPressed)
#         GPIO.add_event_detect(END_SWITCH_Y2, GPIO.FALLING, callback=self.switchYPressed)

#         GPIO.setup(END_SWITCH_Z1, IN, pull_up_down = GPIO.PUD_UP)
#         GPIO.setup(END_SWITCH_Z2, IN, pull_up_down = GPIO.PUD_UP)
#         GPIO.add_event_detect(END_SWITCH_Z1, GPIO.FALLING, callback=self.switchZPressed)
#         GPIO.add_event_detect(END_SWITCH_Z2, GPIO.FALLING, callback=self.switchZPressed)
#     def switchXPressed(self,channel):
#         # left = GPIO.input(END_SWITCH_X1)
#         # right= GPIO.input(END_SWITCH_X2)
#         print("X")
#         # print(left)
#         # print(right)
#     def switchYPressed(self,channel):
#         # left = GPIO.input(END_SWITCH_X1)
#         # right= GPIO.input(END_SWITCH_X2)
#         print("Y")
#         # print(left)
#         # print(right)
#     def switchZPressed(self,channel):
#         # left = GPIO.input(END_SWITCH_X1)
#         # right= GPIO.input(END_SWITCH_X2)
#         print("Z")
#         # print(left)
#         # print(right)

# try:
#     # test=Test()
#     # test.setMode()
#     while 1:
#         # print(".")
#         # pin_read = GPIO.input(END_SWITCH_X2)
#         # print(pin_read)
#         time.sleep(0.1)
# finally:
#     GPIO.cleanup()