import RPi.GPIO as GPIO
import time
import SmartFarmControl

# control=SmartFarmControl.SmartFarmControl()
# #control.test()
# control.initializing_end_to_end()
OUT=GPIO.OUT
IN=GPIO.IN
END_SWITCH_X1=22
END_SWITCH_X2=23

def switchXPressed(self,channel):
    left = GPIO.input(END_SWITCH_X1)
    right= GPIO.input(END_SWITCH_X2)
    print("aaa")
    print(left)
    print(right)

GPIO.setup(END_SWITCH_X1, IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(END_SWITCH_X2, IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.add_event_detect(END_SWITCH_X1, GPIO.RISING, callback=switchXPressed)
GPIO.add_event_detect(END_SWITCH_X2, GPIO.RISING, callback=switchXPressed)

try:
    while 1:
        print(".")
        time.sleep(0.1)
finally:
    GPIO.cleanup()