#!/usr/bin/python3.4

import ev3dev.ev3 as ev3
from time import sleep
import signal

#Reverse then do a Does a U turn

#Threshold for the sensors, the two color ones and the light
THRESHOLD_LEFT = 30
THRESHOLD_RIGHT = 30
THRESHOLD_FRONT = 350
THRESHOLD_DIF = 20


##Speeds the motor will use
BASE_SPEED = 300
TURN_SPEED = 400
TURN_SPEED_SENS = 300
TURN_SPEED_SENS_FINAL = 200

REVERSE_DIST = 100

#----------------------------------------------------------------------------------------------------------------------
#Attach motors mA is left, mb right
mA = ev3.LargeMotor('outA')
mB = ev3.LargeMotor('outB')
mB.run_direct()
mA.run_direct()
#Set motor direction
mA.polarity = "normal"
mB.polarity = "normal"

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
    Stops()
    exit(0)
signal.signal(signal.SIGINT, signal_handler)
print('Press Ctrl+C to exit')

#----------------------------------------------------------------------------------------------------------------------
#180 to the right with sensors for final bit
def UturnSR():
    
    #First need to reverse a bit
    mA.polarity = "inversed"
    mB.polarity = "inversed"
    mA.run_to_rel_pos(position_sp=REVERSE_DIST, speed_sp=TURN_SPEED_SENS, stop_action="hold")
    mB.run_to_rel_pos(position_sp=REVERSE_DIST, speed_sp=TURN_SPEED_SENS, stop_action="hold")
    #Set direction back to normal
    mA.polarity = "normal"
    mB.polarity = "normal"

    #Now do the turn
    mA.run_to_rel_pos(position_sp=380, speed_sp=TURN_SPEED_SENS, stop_action="hold")
    mB.polarity = "inversed"
    mB.run_to_rel_pos(position_sp=380, speed_sp=TURN_SPEED_SENS, stop_action="hold")
    mA.wait_while('running')
    mB.wait_while('running')
    sensorLeftT = colorSensorLeft.value()
    sensorRightT = colorSensorRight.value()
    
    if sensorLeftT < THRESHOLD_LEFT:
        print('Line seen right from the start')
        mA.stop(stop_action="hold")
        mB.stop(stop_action="hold")
    else:
        print('Looking for line')
        while sensorLeftT > THRESHOLD_LEFT:
            print('Stepping to find line')
            mA.run_to_rel_pos(position_sp=10, speed_sp=TURN_SPEED_SENS_FINAL, stop_action="hold")
            sensorLeftT = colorSensorLeft.value()
            print("Left sensor value: ", sensorLeftT)

    return


def Stops():
    print('Stop motors')
    mA.stop(stop_action="hold")
    mB.stop(stop_action="hold")
    #sleep(10)
    #followLinev2()
    return
#----------------------------------------------------------------------------------------------------------------------	


#This is the main loop that will keep going
while True :
    UturnSR()
    sleep(100)