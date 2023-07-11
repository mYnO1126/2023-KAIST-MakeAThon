import serial
import os

arduino = serial.Serial('COM11', 115200)

while 1:
    arduino.flushInput()
    line = arduino.readline()
    line = line.decode('euc-kr') # cp949 euc-kr utf-8
    line = line.split()

    temp = line[0]
    humi = line[1]
    light = line[2]
    soil = line[3]
    print(temp, humi, light, soil)
