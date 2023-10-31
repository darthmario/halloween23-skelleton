#this is a more focused setup of the skelleton with a little more structure
from machine import Pin, ADC, I2C, UART, PWM
import utime, math, time
from servo import Servo
from micropython_servo_pdm import ServoPDMRP2Irq
from smooth_servo import SmoothEaseInOut
from collections import deque

from lcd_i2c import LCD
# Ended up using https://github.com/ShrimpingIt/micropython-dfplayer
# as it just works
from dfplayer import Player
from animHelloImp import *
from animHelloCute import *
from animHelloShock import *
from animQuestions import *
from animParents import *
from animJokes import *
from animSFX import *
from animGoodbye import *
from animIdle import *
from song1 import *
from song9 import *

# We will have a display to show what we're doing currently
# library uses https://micropython-i2c-lcd.readthedocs.io/en/latest/EXAMPLES.html
# PCF8574 on 0x50
I2C_ADDR = 0x27     # DEC 39, HEX 0x27
NUM_ROWS = 2
NUM_COLS = 16

recording_offset = 0
playback_offset = 0
currentAnimation = []

i2c = I2C(0, scl=Pin(21), sda=Pin(20), freq=800000)
lcd = LCD(addr=I2C_ADDR, cols=NUM_COLS, rows=NUM_ROWS, i2c=i2c)
lcd.begin()
lcd.set_cursor(0,0)
lcd.print("Booting")
lcd.set_cursor(0,1)
lcd.print("Setup servos")

    # We will define 3 servos for use across the project
mouth_servo = Servo(pin_id=1)
headr_pin = PWM(Pin(2))
headl_pin = PWM(Pin(3))
min_us=544.0
max_us=2400.0
min_angle=0.0
max_angle=180.0
freq=50
headr_servo = ServoPDMRP2Irq(pwm=headr_pin, min_us=min_us, max_us=max_us, freq=freq, max_angle=max_angle, min_angle=min_angle)
headl_servo = ServoPDMRP2Irq(pwm=headl_pin, min_us=min_us, max_us=max_us, freq=freq, max_angle=max_angle, min_angle=min_angle)

mo = 33
mc = 68

headr_top = 160
headr_bottom = 20

headl_top = 20
headl_bottom = 160

mouth_status = "mc"
head_status ="hc"
# We will have a joystick for moving the head
# Joystick Setup (only using x & y no button)
lcd.clear()
lcd.set_cursor(0,0)
lcd.print("Booting")
lcd.set_cursor(0,1)
lcd.print("Setup joystick")
xAxis = ADC(Pin(27))
yAxis = ADC(Pin(26))


# We will have a button for opening and closing the mouth manually
lcd.clear()
lcd.set_cursor(0,0)
lcd.print("Booting")
lcd.set_cursor(0,1)
lcd.print("Setup button")
mouth_button = Pin(0, Pin.IN, Pin.PULL_UP)

# We will have a keypad setup for choosing the phrases
lcd.clear()
lcd.set_cursor(0,0)
lcd.print("Booting")
lcd.set_cursor(0,1)
lcd.print("Setup keypad")

keyMatrix = [
    [ "1",  "2",   "3"],
    [ "4",    "5",   "6"],
    [ "7",    "8",   "9"],
    ["*",  "0", "#"]
]

colPins = [6,4,8]
rowPins = [5,10,9,7]

# keyscan setup
row = []
column = []
keypressed = 0;

for item in rowPins:
    row.append(machine.Pin(item, machine.Pin.OUT))
for item in colPins:
    column.append(machine.Pin(item,machine.Pin.IN, machine.Pin.PULL_DOWN))
key ='0'


lcd.clear()
lcd.set_cursor(0,0)
lcd.print("Booting")
lcd.set_cursor(0,1)
lcd.print("Setup mp3 player")

# We will have an mp3 player to play the items
# df=DFPlayer(uart_id=0,tx_pin_id=16,rx_pin_id=17)
pico_uart0 = UART(0, baudrate=9600, tx=Pin(16), rx=Pin(17), bits=8, parity=None, stop=1)
pico_busy = Pin(18)
player = Player(uart=pico_uart0, busy_pin=pico_busy , volume=1.0)
player.awaitconfig()
player.awaitvolume()

# We will have a library of audio to play for the script


### Three Modes ###
# 1. Manual - done
# 2. Jukebox - planned
# 3. Interactive - planned
###

# and a variable to hold which mode we're in

mode = 1
lcd.clear()
lcd.set_cursor(0,0)
lcd.print("Complete")
lcd.set_cursor(0,1)
lcd.print("Starting App")


lcd.clear()
lcd.set_cursor(0,0)
lcd.print("Mode: Manual")
lcd.set_cursor(0,1)
lcd.print("Freeform")
#### Manual Mode ####
# When the skelleton is in manual mode, the joystick controls the movement and the button opens and closes the mouth

# Get and Print the Joystick inputs
def getJoystick():
    global head_status
    xValue = xAxis.read_u16()
    yValue = yAxis.read_u16()
    translatedXValue = math.floor(xValue / 65) / 1000
    translatedYValue = math.floor(yValue / 65) / 1000
    # For this skull mechanic up and down are pure for both servos
    # left and right adjust the influence of up and down for left or right servo
    rServo = 20+(140*translatedXValue)
    lServo = 180-(140*translatedXValue)
    
    if(translatedXValue >= .66):
        if(translatedYValue >=.66):
            if head_status != "hbr":
                head_status = "hbr"
                moveServos(head_status)
        elif(translatedYValue <= .33):
            if head_status != "hbl":
                head_status = "hbl"
                moveServos(head_status)
        else:
            if head_status != "hcb":
                head_status = "hcb"
                moveServos(head_status)
    elif(translatedXValue <= .33):
        if(translatedYValue >=.66):
            if head_status != "htr":
                head_status = "htr"
                moveServos(head_status)
        elif(translatedYValue <= .33):
            if head_status != "htl":
                head_status = "htl"
                moveServos(head_status)
        else:
            if head_status != "hct":
                head_status = "hct"
                moveServos(head_status)
    else:
        if head_status != "hc":
            head_status = "hc"
            moveServos(head_status)
       
def getMouthButton():
    global mouth_status
    buttonValue = mouth_button.value()
    if buttonValue == 0:
        if(mouth_status != "mo"):
            mouth_status = "mo"
            moveServos(mouth_status)
    else:
        if(mouth_status != "mc"):
            mouth_status ="mc"
            moveServos(mouth_status)
            
def moveServos(command = ""):
    if command == "mc" or command == "mo":
        if(command == "mouth_open"):
            mouth_servo.write(mo)
        else:
            mouth_servo.write(mc)
    else:
        if command == "hbr":
            headr_servo.move_to_angle(90, 500, SmoothEaseInOut)
            headl_servo.move_to_angle(180, 500, SmoothEaseInOut);
        elif command == "hbl":
            headr_servo.move_to_angle(0, 500, SmoothEaseInOut);
            headl_servo.move_to_angle(90, 500, SmoothEaseInOut);
        elif command == "hcb":
            headr_servo.move_to_angle(0, 1000, SmoothEaseInOut);
            headl_servo.move_to_angle(180, 1000, SmoothEaseInOut);
        elif command == "htr":
            headr_servo.move_to_angle(180, 500, SmoothEaseInOut);
            headl_servo.move_to_angle(90, 500, SmoothEaseInOut);
        elif command == "htl":
            headr_servo.move_to_angle(90, 500, SmoothEaseInOut);
            headl_servo.move_to_angle(0, 500, SmoothEaseInOut);
        elif command == "hct":
            headr_servo.move_to_angle(180, 500, SmoothEaseInOut);
            headl_servo.move_to_angle(0, 500, SmoothEaseInOut);
        else:
            headr_servo.move_to_angle(90, 500, SmoothEaseInOut);
            headl_servo.move_to_angle(90, 500, SmoothEaseInOut);
    print("[\""+command+"\", "+str(time.ticks_ms() - recording_offset)+"]")
    

def scanKeypad():
    global key
    for rowKey in range(4):
        row[rowKey].value(1)
        for colKey in range(3):
            if column[colKey].value() == 1:
                key = keyMatrix[rowKey][colKey]
                row[rowKey].value(0)
                return(key)
        row[rowKey].value(0)

def updateDisplay():
    # when updating displays we'll also reset the skelleton
    if mode == 1:
        lcd.clear()
        lcd.set_cursor(0,0)
        lcd.print("Mode: Manual")
        lcd.set_cursor(0,1)
        lcd.print("Freeform")
    elif mode == 2:
        lcd.clear()
        lcd.set_cursor(0,0)
        lcd.print("Mode: Jukebox")
        lcd.set_cursor(0,1)
        lcd.print("Waiting for song")
    else:
        lcd.clear()
        lcd.set_cursor(0,0)
        lcd.print("Mode: Interactive")
        lcd.set_cursor(0,1)
        lcd.print("Waiting to select")
        
        
def startSkelleton(key = None):
    global mode, recording_offset
    # if mode == 1:
    updateDisplay()
    if key is not None:
        recording_offset = time.ticks_ms();
        print("starting track "+ key + " at time " + str(recording_offset))
        player.play(10,int(key))

def printKey():
    key=scanKeypad()
    global keypressed, mode
    if key is not None:
        currentTime = time.ticks_ms()
        if (keypressed + 500) < currentTime:
            keypressed = currentTime
            print("Key pressed is:{} ".format(key))
            if key is "*":
                mode = 1
                key = None
            elif key is "#":
                mode = 3
                key = None
            elif key is "0":
                mode = 2
                key = None
                
            # now we'll setup the s
            startSkelleton(key)
            
# starting in manual mode
startSkelleton()

def controlAnimation():
    if len(currentAnimation) is not 0:
        currentTime = time.ticks_ms() - playback_offset
        nextTimestamp = currentAnimation[0][1]
        if currentTime >= nextTimestamp:
            print(currentAnimation[0])
            moveServos(currentAnimation[0][0])
            currentAnimation.pop(0)
            


playback_offset = time.ticks_ms()
currentAnimation = song1
player.play(10,1)

#### Main Program Loop
while True:
    # watch for keypress & kick off other stuff
    printKey()
    controlAnimation()
    if mode == 1:
        getJoystick()
        getMouthButton()
        


