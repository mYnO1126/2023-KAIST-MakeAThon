import RPi.GPIO as GPIO
import time
import signal                   
import sys

def signal_handler(sig, frame):
    GPIO.cleanup()
    sys.exit(0)

def main(args):
    
    return


if __name__ == "__main__":

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(23,GPIO.OUT)
    signal.signal(signal.SIGINT, signal_handler)
    while(True):
        GPIO.output(23,True)
        time.sleep(1)
        GPIO.output(23,False)
        time.sleep(1)
    main(args)