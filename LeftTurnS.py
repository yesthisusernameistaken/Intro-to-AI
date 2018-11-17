#!/usr/bin/python3.4

import ev3dev.ev3 as ev3
from time import sleep
import signal

#Follows a line and stops when the front sensor detect an intersection. 

#Todo list
#Get it to count lines but not multiple times the same one
#Get the turns to be partialy sensor based
#find a way of setting a list of steps to take (ie turns)

#Long term to do
#Raise sensors 
#will be getting more analogue values so will need to speed up, slow down motors 

#Done
#Get it to really stop when it detecs a line

#Threshold for the sensors, the two color ones and the light
THRESHOLD_LEFT = 20
THRESHOLD_RIGHT = 20
THRESHOLD_FRONT = 350
THRESHOLD_DIF = 10

intersections = 0
holdBit = 0

##Speeds the motor will use
BASE_SPEED = 300
TURN_SPEED = 400

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
#90 degree turn to the left
#Experimental left turn, uses sensor for final position
def leftTurnS():
    mB.run_to_rel_pos(position_sp=400, speed_sp=600, stop_action="hold")
    mB.wait_while('running')
    sensorLeftT = colorSensorLeft.value()
    sensorRightT = colorSensorRight.value()

    if sensorRightT < THRESHOLD_RIGHT:
        #This is the case that the right sensor has seen the line
        print('Line seen right from the start')
        mA.stop(stop_action="hold")
        mB.stop(stop_action="hold")
        #This bit above is just a placeholder so it compiles
    else:
        #In this case the senor has't seen the light yet so it sould keep turning a bit
        print('Looking for line')
        while sensorRightT > THRESHOLD_RIGHT:
            print('Stepping to find line')
            mB.run_to_rel_pos(position_sp=10, speed_sp=200, stop_action="hold")
            sensorRightT = colorSensorRight.value()
            print("Right sensor value: ", sensorRightT)

    return

#90 degree turn to the left
def leftTurn():
    mB.run_to_rel_pos(position_sp=460, speed_sp=900, stop_action="hold")
    mB.wait_while('running')
    return

#90 degree turn to the right
def rightTurn():
    mA.run_to_rel_pos(position_sp=460, speed_sp=900, stop_action="hold")
    #mA.wait_while('running')
    return

#Full 180 turn
def uTurn():
    mA.run_to_rel_pos(position_sp=420, speed_sp=900, stop_action="hold")
    mB.polarity = "inversed"
    mB.run_to_rel_pos(position_sp=420, speed_sp=900, stop_action="hold")
    #Pauses program while the motor is running
    #mB.wait_while('running')
    mB.polarity = "normal"
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
    leftTurnS()
    sleep(100)
