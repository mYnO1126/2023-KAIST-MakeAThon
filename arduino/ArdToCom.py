import serial
import os

arduino = serial.Serial('/dev/ttyACM0', 115200)

while 1:
    arduino.flushInput()
    line = arduino.readline()
    line = line.decode('euc-kr') # cp949 euc-kr utf-8
    line = line.split()

    temp = line[0] # 0 ~ 50 C
    humi = line[1] # 20 ~ 80 %
    light = line[2] # 0 ~ 1023
    soil1 = line[3] # 0 ~ 1023
    soil2 = line[4] # 0 ~ 1023
    print(temp, humi, light, soil1, soil2)
