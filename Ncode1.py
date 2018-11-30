#!/usr/bin/python3.4

import ev3dev.ev3 as ev3
from time import sleep
import signal

#This code follows a line and will count the intersections it passes 

#Todo list
#Find a way of setting a list of steps to take (ie turns)
#If it needs to use the ensors when reversing will 

#Long term to do
#Ues the dif between  current and previous reading
#Will be getting more analogue values so will need to speed up, slow down motors at smaller increments

#Done
#Get it to really stop when it detecs a line
#Get the turns to be partialy sensor based
#Raise sensors (will need to sheild them but the values seem more consisten)
#Get the Uturn working
#Get it to count lines but not multiple times the same one, code written, need to test
#Might get the bot to stop right after the fully crossed a line OR get turns to reset that bit
#When it makes a U-turn, might need to get it to backup but only when doing a 180? Yeah looks like it
#Sheild the sensors from external light 


#Threshold for the sensors, the two color ones and the light
THRESHOLD_LEFT = 30
THRESHOLD_RIGHT = 30
THRESHOLD_FRONT = 350
THRESHOLD_DIF = 20

intersections = 0
holdBit = 0

#Speeds the motors will use
BASE_SPEED = 300
TURN_SPEED = 400
TURN_SPEED_SENS = 600
TURN_SPEED_SENS_FINAL = 200

REVERSE_DIST = 100

#----------------------------------------------------------------------------------------------------------------------
#Initial setup of sensors and motors

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
#Put the color sensor into COL-REFLECT mode to measure reflected light intensity.
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
#Code concerning movement actions

#90 degree turn to the left, uses sensor for final position
def leftTurnS():
    print("Left Turn")
    Stops()
    #Initial turn to make it most of the way there
    mB.run_to_rel_pos(position_sp=400, speed_sp=TURN_SPEED_SENS, stop_action="hold")
    mB.wait_while('running')
    sensorRightT = colorSensorRight.value()

    if sensorRightT < THRESHOLD_RIGHT:
        #This is the case that the right sensor has seen the line
        print('Line seen right from the start')
        mA.stop(stop_action="hold")
        mB.stop(stop_action="hold")
    else:
        #In this case the senor hasn't seen the light yet so it sould keep turning a bit
        print('Looking for line')
        while sensorRightT > THRESHOLD_RIGHT:
            print('Stepping to find line')
            mB.run_to_rel_pos(position_sp=10, speed_sp=TURN_SPEED_SENS_FINAL, stop_action="hold")
            sensorRightT = colorSensorRight.value()
            print("Right sensor value: ", sensorRightT)

    return

#90 degree turn to the right, uses sensor for final position
def rightTurnS():
    print("Right Turn")
    Stops()
    #Initial turn to make it most of the way there
    mA.run_to_rel_pos(position_sp=400, speed_sp=TURN_SPEED_SENS, stop_action="hold")
    mA.wait_while('running')
    sensorLeftT = colorSensorLeft.value()

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

def Reverse():
    print("Reverse")
    Stops()
    #First need to reverse a bit
    mA.polarity = "inversed"
    mB.polarity = "inversed"
    mA.run_to_rel_pos(position_sp=REVERSE_DIST, speed_sp=TURN_SPEED_SENS, stop_action="hold")
    mB.run_to_rel_pos(position_sp=REVERSE_DIST, speed_sp=TURN_SPEED_SENS, stop_action="hold")
    #Set direction back to normal
    mA.polarity = "normal"
    mB.polarity = "normal"
    return

#180 to the right with sensors for final bit
def UturnS():
    #First reverse to clear the can
    Reverse()
    mA.run_to_rel_pos(position_sp=380, speed_sp=TURN_SPEED_SENS, stop_action="hold")
    mB.polarity = "inversed"
    mB.run_to_rel_pos(position_sp=380, speed_sp=TURN_SPEED_SENS, stop_action="hold")
    mA.wait_while('running')
    mB.wait_while('running')
    #Set the motor back to normal, not sure if needed but to be on the safe side
    mB.polarity = "normal"

    sensorLeftT = colorSensorLeft.value()
    
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
    return

def Nothing():
    print('No intersection counted yet')
    return
#----------------------------------------------------------------------------------------------------------------------	

#Turn left and right to keep the line in the center
def TurnForLine(sensorRight, sensorLeft):
 if sensorRight < sensorLeft:
     print("Turn right")
     mA.run_forever(speed_sp=TURN_SPEED)
     mB.run_forever(speed_sp=BASE_SPEED)
 else:
     print("Turn left")
     mA.run_forever(speed_sp=BASE_SPEED)
     mB.run_forever(speed_sp=TURN_SPEED)
 return

#This bit attempts to count the black intersections
def countLine(sensorFront):
    global holdBit
    global intersections
    if holdBit == 0:
        intersections = intersections+1
        holdBit = holdBit+1
    return

#----------------------------------------------------------------------------------------------------------------------
#This bit will decide what direction to take

def indirect(i):
        switcher={
                0: Nothing,
                1: leftTurnS,
                2: Stops,
                3: Stops }
        func=switcher.get(i, "Invalid")
        return func()


#----------------------------------------------------------------------------------------------------------------------
#This would be the main bit

def followLinev2():
    global holdBit
    global intersections
    #Read the sensor value and store it
    sensorLeft = colorSensorLeft.value()
    sensorRight = colorSensorRight.value()
    sensorFront = lightSensorFront.value()	
    print("-------------------------------------------------------------------------------------------")
    #Print the sensor values to the terminal (for debugging reasons, like a lot of the prints here)
    print("Left: ", sensorLeft, "Right: ", sensorRight, "Front: ", sensorFront)
    print("Number of intersections counted = ", intersections)

    #Check the front sensor and stop/count it, if a line is detected
    if sensorFront < THRESHOLD_FRONT:
        #Black line detected by front sensor
        #Stops()
        countLine(sensorFront)
        indirect(intersections)
    else:
        #Front sensor doesn't see a black line
        holdBit = 0
        #Get the difference between the two sensors
        sensorDif = sensorLeft-sensorRight
        sensorDif = abs(sensorDif)
        print("Sensor difference: ", sensorDif)

        if sensorDif < THRESHOLD_DIF:
            print("Go ahead, difference is sensors is below threshold")
            mA.run_forever(speed_sp=BASE_SPEED)
            mB.run_forever(speed_sp=BASE_SPEED)
        else:
            print("There is a diff in the sensors readings above the threshold")
            TurnForLine(sensorRight, sensorLeft)
            #one might be looking at black	
    

    return


#This is the main loop that will keep going forever
while True :
    followLinev2()