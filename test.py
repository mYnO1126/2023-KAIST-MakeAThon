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
END_SWITCH_X1=22
END_SWITCH_X2=23
END_SWITCH_Y1=24
END_SWITCH_Y2=25
END_SWITCH_Z1=17
END_SWITCH_Z2=27

def switchXPressed(channel):
    left = GPIO.input(END_SWITCH_X1)
    right= GPIO.input(END_SWITCH_X2)
    print("aaa")
    print(left)
    print(right)

GPIO.setmode(GPIO.BCM)
GPIO.setup(END_SWITCH_X1, IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(END_SWITCH_X2, IN, pull_up_down = GPIO.PUD_UP)
GPIO.add_event_detect(END_SWITCH_X1, GPIO.FALLING, callback=switchXPressed)
GPIO.add_event_detect(END_SWITCH_X2, GPIO.FALLING, callback=switchXPressed,bouncetime=300)
GPIO.setup(END_SWITCH_Y1, IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(END_SWITCH_Y2, IN, pull_up_down = GPIO.PUD_UP)
# GPIO.add_event_detect(END_SWITCH_Y1, GPIO.RISING, callback=self.switchYPressed)
# GPIO.add_event_detect(END_SWITCH_Y2, GPIO.RISING, callback=self.switchYPressed)

GPIO.setup(END_SWITCH_Z1, IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(END_SWITCH_Z2, IN, pull_up_down = GPIO.PUD_UP)
# GPIO.add_event_detect(END_SWITCH_Z1, GPIO.RISING, callback=self.switchZPressed)
# GPIO.add_event_detect(END_SWITCH_Z2, GPIO.RISING, callback=self.switchZPressed)

try:
    while 1:
        # print(".")
        pin_read = GPIO.input(END_SWITCH_X2)
        print(pin_read)
        time.sleep(0.1)
finally:
    GPIO.cleanup()