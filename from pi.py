#this is a more focused setup of the skelleton with a little more structure
from machine import Pin, ADC, I2C, UART
import utime, math, time
from servo import Servo
from lcd_i2c import LCD
from dfplayer import Player

# We will have a display to show what we're doing currently
# library uses https://micropython-i2c-lcd.readthedocs.io/en/latest/EXAMPLES.html
# PCF8574 on 0x50
I2C_ADDR = 0x27     # DEC 39, HEX 0x27
NUM_ROWS = 2
NUM_COLS = 16

i2c = I2C(0, scl=Pin(21), sda=Pin(20), freq=800000)
lcd = LCD(addr=I2C_ADDR, cols=NUM_COLS, rows=NUM_ROWS, i2c=i2c)
lcd.begin()
lcd.set_cursor(0,0)
lcd.print("Booting")
lcd.set_cursor(0,1)
lcd.print("Setup servos")

# We will define 3 servos for use across the project
mouth_servo = Servo(pin_id=1)
mouth_open = 33
mouth_closed = 68
headr_servo = Servo(pin_id=2)
headr_top = 160
headr_bottom = 20
headl_servo = Servo(pin_id=3)
headl_top = 20
headl_bottom = 160
# We will have a joystick for moving the head
# Joystick Setup (only using x & y no button)
xAxis = ADC(Pin(27))
yAxis = ADC(Pin(26))

# We will have a button for opening and closing the mouth manually
mouth_button = Pin(0, Pin.IN, Pin.PULL_UP)

# We will have a keypad setup for choosing the phrases

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
player.play(1,1)
#wait some time till the DFPlayer is ready
# utime.sleep(5)
# df.send_cmd(15,1,0)
# utime.sleep(1)
# print(df.send_cmd(72,0,0))
# utime.sleep(1)
# df.reset()
# utime.sleep(1)
# print(df.get_files_in_folder(1))
# utime.sleep(1)
# print(df.get_files_in_folder(4))
# df.volume(30)
# utime.sleep(1)
# print(df.get_volume())

# We will have a library of audio to play for the script


### Three Modes ###
# 1. Manual - done
# 2. Automatic - planned
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
            headr_servo.write(90);
            headl_servo.write(180);
        elif(translatedYValue <= .33):
            headr_servo.write(0);
            headl_servo.write(90);
        else:
            headr_servo.write(0);
            headl_servo.write(180);
    elif(translatedXValue <= .33):
        if(translatedYValue >=.66):
            headr_servo.write(180);
            headl_servo.write(90);
        elif(translatedYValue <= .33):
            headr_servo.write(90);
            headl_servo.write(0);
        else:
            headr_servo.write(180);
            headl_servo.write(0);
    else:
        headr_servo.write(90);
        headl_servo.write(90);
    
#     print("X " + str(translatedXValue) + " Y " + str(translatedYValue))
    
def getMouthButton():
    buttonValue = mouth_button.value()
    #print("button" + str(buttonValue))
    if buttonValue == 0:
        mouth_servo.write(mouth_open)
    else:
        mouth_servo.write(mouth_closed)


#### Main Program Loop
while True:
    player.volume(0.2)
    mode
    if mode == 1:
        getJoystick()
        getMouthButton()
        #temporary sleep to limit what is displayed
#         utime.sleep(0.1)

