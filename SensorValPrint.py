#!/usr/bin/python3.4

import ev3dev.ev3 as ev3
from time import sleep
import signal

#Prints the values of the sensors



#----------------------------------------------------------------------------------------------------------------------

#Attach sensors
colorSensorLeft = ev3.ColorSensor('in1')
colorSensorRight = ev3.ColorSensor('in2')
lightSensorFront = ev3.LightSensor('in3') 

#Check sensors if they are connected, will throw an error message if not
assert colorSensorLeft.connected, "ColorSensorLeft (CS) is not connected to in1"
assert colorSensorRight.connected, "ColorSensorLeft (CS) is not connected to in2"
assert lightSensorFront.connected, "LightSensoFront (LS) is not connected to in3"

# Put the color sensor into COL-REFLECT mode
# to measure reflected light intensity.
colorSensorLeft.mode='COL-REFLECT'
colorSensorRight.mode='COL-REFLECT'

#For shutdown, stop motors
def signal_handler(sig, frame):
    print('Shutting down gracefully')
    exit(0)
signal.signal(signal.SIGINT, signal_handler)
print('Press Ctrl+C to exit')


#This is the main loop that will keep going
while True :
    #Read the sensor value and store it
    sensorLeft = colorSensorLeft.value()
    sensorRight = colorSensorRight.value()
    sensorFront = lightSensorFront.value()	
    #Print the sensor values to the terminal (mainly for debugging reasons, like a lot of the comments here)
    print("sensorLeft: ", sensorLeft, " sensorRight: ", sensorRight, "sensorFront", sensorFront)
    sensorDif = sensorLeft-sensorRight
    sensorDif = abs(sensorDif)
    print("Sensor difference = ", sensorDif)
    sleep(1)