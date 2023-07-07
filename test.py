import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(21,GPIO.OUT)
GPIO.setup(20,GPIO.OUT)
GPIO.output(20,False)
while(True):
    
    GPIO.output(21,True)
    time.sleep(0.001)
    GPIO.output(21,False)
    time.sleep(0.001)