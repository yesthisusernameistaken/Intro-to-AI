#!/usr/bin/python3.4

import ev3dev.ev3 as ev3
from time import sleep
import signal

#This code follows a line and will count the intersections it passes 

#Todo list
#If it needs to use the ensors when reversing will 

#Long term to do
#Ues the dif between  current and previous reading
#Will be getting more analogue values so will need to speed up, slow down motors at smaller increments
#If it detecs the line twice on one side, stop motor?

#Done
#Get it to really stop when it detecs a line
#Get the turns to be partialy sensor based
#Raise sensors (will need to sheild them but the values seem more consisten)
#Get the Uturn working
#Get it to count lines but not multiple times the same one, code written, need to test
#Might get the bot to stop right after the fully crossed a line OR get turns to reset that bit
#When it makes a U-turn, might need to get it to backup but only when doing a 180? Yeah looks like it
#Sheild the sensors from external light 
#Find a way of setting a list of steps to take (ie turns) - dictionary

#Threshold for the sensors, the two color ones and the light
THRESHOLD_LEFT = 25
THRESHOLD_RIGHT = 25
THRESHOLD_FRONT = 450
THRESHOLD_DIF = 15

intersections = 0
holdBit = 0
ReversedBit = 0

#Speeds the motors will use
BASE_SPEED = 100
TURN_SPEED = 400
TURN_SPEED_SENS = 700
TURN_SPEED_SENS_FINAL = 300
TURN_SPEED_SENS_U = 300
BASE_SPEED_FORW = 500

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
    mA.polarity = "normal"
    mB.polarity = "normal"
    global ReversedBit
    ReversedBit = 0
    #Initial turn to make it most of the way there
    mB.run_to_rel_pos(position_sp=350, speed_sp=TURN_SPEED_SENS, stop_action="hold")
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
    mA.polarity = "normal"
    mB.polarity = "normal"
    global ReversedBit
    ReversedBit = 0
    #Initial turn to make it most of the way there
    mA.run_to_rel_pos(position_sp=350, speed_sp=TURN_SPEED_SENS, stop_action="hold")
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

#180 to the right with sensors for final bit
def UturnSR():
    #First need to reverse a bit
    mA.polarity = "inversed"
    mB.polarity = "inversed"
    mA.run_to_rel_pos(position_sp=REVERSE_DIST, speed_sp=TURN_SPEED_SENS_U, stop_action="hold")
    mB.run_to_rel_pos(position_sp=REVERSE_DIST, speed_sp=TURN_SPEED_SENS_U, stop_action="hold")
    mA.wait_while('running')
    mB.wait_while('running')
    #Set direction back to normal
    mA.polarity = "normal"
    mB.polarity = "normal"

    #Now do the turn
    mA.run_to_rel_pos(position_sp=400, speed_sp=TURN_SPEED_SENS, stop_action="hold")
    mB.polarity = "inversed"
    mB.run_to_rel_pos(position_sp=400, speed_sp=TURN_SPEED_SENS, stop_action="hold")
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

    mA.polarity = "normal"
    mB.polarity = "normal"

    return

def ReverseM():
    print("Reversing following the line")
    global ReversedBit
    ReversedBit = 1
    #Reverse motors
    mA.polarity = "inversed"
    mB.polarity = "inversed"
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

def TurnForLineReverse(sensorRight, sensorLeft):
 if sensorRight < sensorLeft:
     print("Turn right")
     mB.run_forever(speed_sp=TURN_SPEED)
     mA.run_forever(speed_sp=BASE_SPEED)
 else:
     print("Turn left")
     mB.run_forever(speed_sp=BASE_SPEED)
     mA.run_forever(speed_sp=TURN_SPEED)
 return

#This bit attempts to count the black intersections
def countLine(sensorFront):
    global holdBit
    global intersections
    if holdBit == 1:
        intersections = intersections+1
    return

#----------------------------------------------------------------------------------------------------------------------
#This bit will decide what direction to take

def indirect(i):
        switcher={
            0 : Nothing ,
            1 : rightTurnS ,
            2 : Nothing ,
            3 : Nothing ,
            4 : Nothing ,
            5 : rightTurnS ,
            6 : Nothing ,
            7 : Nothing ,
            8 : Nothing ,
            9 : rightTurnS ,
            10 : Nothing ,
            11 : Nothing ,
            12 : UturnSR ,
            13 : leftTurnS ,
            14 : leftTurnS ,
            15 : Nothing ,
            16 : Nothing ,
            17 : Nothing ,
            18 : UturnSR ,
            19 : leftTurnS ,
            20 : leftTurnS ,
            21 : Nothing ,
            22 : Nothing ,
            23 : Nothing ,
            24 : UturnSR ,
            25 : leftTurnS ,
            26 : leftTurnS ,
            27 : Nothing ,
            28 : UturnSR ,
            29 : Nothing ,
            30 : Nothing ,
            31 : rightTurnS ,
            32 : Nothing ,
            33 : Nothing ,
            34 : rightTurnS ,
            35 : Nothing ,
            36 : Nothing ,
            37 : leftTurnS ,
            38 : Nothing ,
            39 : leftTurnS ,
            40 : leftTurnS ,
            41 : Nothing ,
            42 : UturnSR ,
            43 : rightTurnS ,
            44 : rightTurnS ,
            45 : Nothing ,
            46 : Nothing ,
            47 : UturnSR ,
            48 : leftTurnS ,
            49 : leftTurnS ,
            50 : Nothing ,
            51 : Nothing ,
            52 : Nothing ,
            53 : UturnSR ,
            54 : leftTurnS ,
            55 : leftTurnS ,
            56 : Nothing ,
            57 : UturnSR ,
            58 : rightTurnS ,
            59 : rightTurnS ,
            60 : Nothing ,
            61 : UturnSR ,
            62 : leftTurnS ,
            63 : leftTurnS ,
            64 : Nothing ,
            65 : Nothing ,
            66 : UturnSR ,
            67 : Nothing ,
            68 : rightTurnS ,
            69 : Nothing ,
            70 : Nothing ,
            71 : Nothing ,
            72 : Nothing ,
            73 : rightTurnS ,
            74 : Nothing ,
            75 : Nothing ,
            76 : leftTurnS ,
            77 : Nothing ,
            78 : Nothing ,
            79 : leftTurnS ,
            80 : Nothing ,
            81 : Nothing ,
            82 : Nothing ,
            83 : leftTurnS ,
            84 : leftTurnS ,
            85 : Nothing ,
            86 : UturnSR ,
            87 : rightTurnS ,
            88 : Nothing ,
            89 : rightTurnS ,
            90 : Nothing ,
            91 : Nothing ,
            92 : Nothing ,
            93 : UturnSR ,
            94 : rightTurnS ,
            95 : rightTurnS ,
            96 : Nothing ,
            97 : Nothing ,
            98 : UturnSR ,
            99 : leftTurnS ,
            100 : leftTurnS ,
            101 : Nothing ,
            102 : Nothing ,
            103 : Nothing ,
            104 : UturnSR ,
            105 : rightTurnS ,
            106 : rightTurnS ,
            107 : Nothing ,
            108 : UturnSR ,
            109 : rightTurnS ,
            110 : rightTurnS ,
            111 : Nothing ,
            112 : UturnSR ,
            113 : leftTurnS ,
            114 : Nothing ,
            115 : Nothing ,
            116 : Nothing ,
            117 : rightTurnS ,
            118 : Nothing ,
            119 : leftTurnS ,
            120 : Nothing ,
            121 : Nothing ,
            122 : leftTurnS ,
            123 : Nothing ,
            124 : leftTurnS ,
            125 : leftTurnS ,
            126 : Nothing ,
            127 : UturnSR ,
            128 : rightTurnS ,
            129 : rightTurnS ,
            130 : Nothing ,
            131 : Nothing ,
            132 : Nothing ,
            133 : UturnSR ,
            134 : rightTurnS ,
            135 : rightTurnS ,
            136 : Nothing ,
            137 : rightTurnS ,
            138 : leftTurnS ,
            139 : leftTurnS ,
            140 : Nothing ,
            141 : Nothing ,
            142 : leftTurnS ,
            143 : rightTurnS ,
            144 : Nothing ,
            145 : rightTurnS ,
            146 : Nothing ,
            147 : rightTurnS ,
            148 : rightTurnS ,
            149 : rightTurnS ,
            150 : leftTurnS ,
            151 : leftTurnS, }
        func=switcher.get(i, "Invalid")
        return func()


#----------------------------------------------------------------------------------------------------------------------
#This would be the main bit

def followLinev3():
    global holdBit
    global intersections
    global ReversedBit
    print ("Reversed bit:", ReversedBit)
    print("-------------------------------------------------------------------------------------------")
    sensorFront = lightSensorFront.value()
    
    #sensorLeft = colorSensorLeft.value()
    #sensorRight = colorSensorRight.value()
    #print("Left: ", sensorLeft, "Right: ", sensorRight, "Front: ", sensorFront)	

    if ReversedBit == 0:
        #Normal operation forward
        sensorLeft = colorSensorLeft.value()
        sensorRight = colorSensorRight.value()
        print("Left: ", sensorLeft, "Right: ", sensorRight, "Front: ", sensorFront)	
    else:
        #Reversed sensor
        sensorLeft = colorSensorRight.value()
        sensorRight = colorSensorLeft.value()
        print("Left: ", sensorLeft, "Right: ", sensorRight, "Front: ", sensorFront)

    print("Number of intersections counted = ", intersections)

    #Check the front sensor and stop/count it, if a line is detected
    if sensorFront < THRESHOLD_FRONT:
        #Black line detected by front sensor
        holdBit = holdBit+1
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
            mA.run_forever(speed_sp=BASE_SPEED_FORW)
            mB.run_forever(speed_sp=BASE_SPEED_FORW)
        else:
            print("There is a diff in the sensors readings above the threshold")
            if ReversedBit == 0:
                #Normal operation
                TurnForLine(sensorRight, sensorLeft)
            else:
                print("Reversed sensor input to motor")
                #TurnForLine(sensorLeft, sensorRight)
                TurnForLineReverse(sensorRight, sensorLeft)


    return

#This is the main loop that will keep going forever
while True :
    followLinev3()