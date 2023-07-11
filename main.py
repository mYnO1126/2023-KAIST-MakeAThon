import RPi.GPIO as GPIO
import time
import signal                   
import sys
import pygame
import SmartFarmControl

def signal_handler(sig, frame):
    GPIO.cleanup()
    sys.exit(0)

def main(args):
    pygame.init()
    fps=30
    fpsClock = pygame.time.Clock()
    width, height = 640, 480
    screen = pygame.display.set_mode((width, height),pygame.FULLSCREEN)
    screen.fill((0,0,0))

    smartfarm=SmartFarmControl.SmartFarmControl()
    smartfarm.initializing_end_to_end()

    while True:
        pygame.display.flip()
        fpsClock.tick(fps)



if __name__ == "__main__":

    
    signal.signal(signal.SIGINT, signal_handler)
    
    main()