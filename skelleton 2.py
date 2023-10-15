#this is a more focused setup of the skelleton with a little more structure
from machine import Pin, ADC, I2C
import utime, math
from servo import Servo
from lcd_i2c import LCD

# We will define 3 servos for use across the project
mouth_servo = Servo(pin_id=1)
headr_servo = Servo(pin_id=2)
headl_servo = Servo(pin_id=3)

# We will have a joystick for moving the head
# Joystick Setup (only using x & y no button)
xAxis = ADC(Pin(27))
yAxis = ADC(Pin(26))

# We will have a button for opening and closing the mouth manually
mouth_button = Pin(0, Pin.IN, Pin.PULL_UP)

# We will have a keypad setup for choosing the phrases

# We will have a display to show what we're doing currently
# library uses https://micropython-i2c-lcd.readthedocs.io/en/latest/EXAMPLES.html
# PCF8574 on 0x50
# I2C_ADDR = 0x27     # DEC 39, HEX 0x27
# NUM_ROWS = 2
# NUM_COLS = 16
# 
# i2c = I2C(0, scl=Pin(17), sda=Pin(16), freq=800000)
# lcd = LCD(addr=I2C_ADDR, cols=NUM_COLS, rows=NUM_ROWS, i2c=i2c)
# lcd.begin()


# We will have an mp3 player to play the items

# We will have a library of audio to play for the script


### Three Modes ###
# 1. Manual - in progress
# 2. Automatic - planned
# 3. Interactive - planned
###

# and a variable to hold which mode we're in

mode = 1

#### Manual Mode ####
# When the skelleton is in manual mode, the joystick controls the movement and the button opens and closes the mouth

# Get and Print the Joystick inputs
def getJoystick():
    servoL = .5
    servoR = .5
    xValue = xAxis.read_u16()
    yValue = yAxis.read_u16()
    translatedXValue = math.floor(xValue / 65) / 1000
    translatedYValue = math.floor(yValue / 65) / 1000
    # For this skull mechanic up and down are pure for both servos
    # left and right adjust the influence of up and down for left or right servo
    servoL = translatedXValue
    servoR = translatedXValue
    if(translatedYValue >= 0.5):
        translatedYValue -= 0.5
    else:
        translatedYValue = 0.5 - translatedYValue
    
#     headr_servo.write(translatedXValue);
#     headr_servo.write(translatedYValue);
    print("Joystick " + str(translatedXValue)+", "+str(translatedYValue))
    print("servoL " + str(servoL) + " servoR " + str(servoR))
    
def getMouthButton():
    buttonValue = mouth_button.value()
    #print("button" + str(buttonValue))
    if buttonValue == 0:
        mouth_servo.write(90)
    else:
        mouth_servo.write(0)


#### Main Program Loop
while True:
    mode
    if mode == 1:
#         lcd.print("Hello World")
        getJoystick()
        getMouthButton()
        #temporary sleep to limit what is displayed
        utime.sleep(0.1)