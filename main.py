#this is a more focused setup of the skelleton with a little more structure
from machine import Pin, ADC, I2C, UART, PWM
import utime, math, time, random, gc
from servo import Servo
from micropython_servo_pdm import ServoPDMRP2Irq
from smooth_servo import SmoothEaseInOut


from lcd_i2c import LCD
# Ended up using https://github.com/ShrimpingIt/micropython-dfplayer
# as it just works
from dfplayer import Player

# We will have a display to show what we're doing currently
# library uses https://micropython-i2c-lcd.readthedocs.io/en/latest/EXAMPLES.html
# PCF8574 on 0x50
I2C_ADDR = 0x27     # DEC 39, HEX 0x27
NUM_ROWS = 2
NUM_COLS = 16

recording_offset = 0
playback_offset = 0
currentAnimation = []
jukeboxKey = 0
jukeboxKeyTime = 0

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

mouth_open = 33
mouth_closed = 68

headr_top = 160
headr_bottom = 20

headl_top = 20
headl_bottom = 160

mouth_status = "mouth_closed"
head_status ="center"
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
    [ "1", "2", "3" ],
    [ "4", "5", "6" ],
    [ "7", "8", "9" ],
    [ "*", "0", "#" ]
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
player = Player(uart=pico_uart0, busy_pin=pico_busy)
player.awaitconfig()
player.awaitvolume()
player.volume(0.8)

# We will have a library of audio to play for the script


### Three Modes ###
# 1. Manual - done
# 2. Jukebox - planned
# 3. Interactive - planned
###

# and a variable to hold which mode we're in

mode = 1
autoplay = 0
lastplay = "song"
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
            if head_status != "bottom_right":
                head_status = "bottom_right"
                moveServos(head_status)
        elif(translatedYValue <= .33):
            if head_status != "bottom_left":
                head_status = "bottom_left"
                moveServos(head_status)
        else:
            if head_status != "center_bottom":
                head_status = "center_bottom"
                moveServos(head_status)
    elif(translatedXValue <= .33):
        if(translatedYValue >=.66):
            if head_status != "top_right":
                head_status = "top_right"
                moveServos(head_status)
        elif(translatedYValue <= .33):
            if head_status != "top_left":
                head_status = "top_left"
                moveServos(head_status)
        else:
            if head_status != "center_top":
                head_status = "center_top"
                moveServos(head_status)
    else:
        if head_status != "center":
            head_status = "center"
            moveServos(head_status)
       
def getMouthButton():
    global mouth_status
    buttonValue = mouth_button.value()
    if buttonValue == 0:
        if(mouth_status != "mouth_open"):
            mouth_status = "mouth_open"
            moveServos(mouth_status)
    else:
        if(mouth_status != "mouth_closed"):
            mouth_status ="mouth_closed"
            moveServos(mouth_status)
            
def moveServos(command = ""):
    if "mouth" in command:
        if(command == "mouth_open"):
            mouth_servo.write(mouth_open)
        else:
            mouth_servo.write(mouth_closed)
    else:
        if command == "bottom_right":
            headr_servo.move_to_angle(90, 500, SmoothEaseInOut)
            headl_servo.move_to_angle(180, 500, SmoothEaseInOut);
        elif command == "bottom_left":
            headr_servo.move_to_angle(0, 500, SmoothEaseInOut);
            headl_servo.move_to_angle(90, 500, SmoothEaseInOut);
        elif command == "center_bottom":
            headr_servo.move_to_angle(0, 1000, SmoothEaseInOut);
            headl_servo.move_to_angle(180, 1000, SmoothEaseInOut);
        elif command == "top_right":
            headr_servo.move_to_angle(180, 500, SmoothEaseInOut);
            headl_servo.move_to_angle(90, 500, SmoothEaseInOut);
        elif command == "top_left":
            headr_servo.move_to_angle(90, 500, SmoothEaseInOut);
            headl_servo.move_to_angle(0, 500, SmoothEaseInOut);
        elif command == "center_top":
            headr_servo.move_to_angle(180, 500, SmoothEaseInOut);
            headl_servo.move_to_angle(0, 500, SmoothEaseInOut);
        else:
            headr_servo.move_to_angle(90, 500, SmoothEaseInOut);
            headl_servo.move_to_angle(90, 500, SmoothEaseInOut);
#     print("[\""+command+"\", "+str(time.ticks_ms() - recording_offset)+"]")
    

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
        if autoplay == 1:
            lcd.set_cursor(0,1)
            lcd.print("Autoplay")        
        else:
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
    global mode, recording_offset, autoplay
    # if mode == 1:
    updateDisplay()
    if key is not None:
        if mode == 1:
            if key == "9":
                autoplay = 1
            else:
                autoplay = 0
        elif mode == 3:
            playRandomAnimation(key)
            
def jukeBoxPlay(key):
    global playback_offset, currentAnimation
    currentAnimation =[]
    gc.collect()
    
    print("playing song " + key)
    
    # let's try loading animation from the filesystem
    with open('songs/song'+key+'.py') as f: currentAnimation = eval(f.read())
    
    gc.collect()
    
    playback_offset = time.ticks_ms()+250
    
    player.play(10,int(key))
            
def playRandomAnimation(key):
    global playback_offset, currentAnimation
    currentAnimation=[]
    selectedPlaylist = []
    selectedPlaylistName = ""
    playlistString =""
    song = []
    gc.collect()
    if key == "1":
        selectedPlaylistName = "helloImp"
        playlistString = "Hi Impress"
    elif key == "2":
        selectedPlaylistName = "helloCute"
        playlistString = "Hi Cute"
    elif key == "3":
        selectedPlaylistName = "helloShock"
        playlistString = "Hi Shock"
    elif key == "4":
        selectedPlaylistName = "question"
        playlistString = "Question"
    elif key == "5":
        selectedPlaylistName = "parents"
        playlistString = "Parents"
    elif key == "6":
        selectedPlaylistName = "jokes"
        playlistString = "Joke"
    elif key == "7":
        selectedPlaylistName = "sfx"
        playlistString = "SFX"
    elif key == "8":
        selectedPlaylistName = "goodbye"
        playlistString = "Goodbye"
    elif key == "9":
        selectedPlaylistName = "idle"
        playlistString = "Idle"
    print("seleted playlist" + playlistString)
    with open('animations/'+selectedPlaylistName+'.py') as f:
        selectedPlaylist = eval(f.read())
    
    gc.collect()
    selectedAnswer = random.randint(1, len(selectedPlaylist))

    currentAnimation = selectedPlaylist[selectedAnswer - 1][:]
    playback_offset = time.ticks_ms()
    player.play(int(key),int(selectedAnswer))
    lcd.clear()
    lcd.set_cursor(0,0)
    lcd.print("Mode: Interactive")
    lcd.set_cursor(0,1)
    lcd.print(playlistString + " " + str(selectedAnswer))

def printKey():
    key=scanKeypad()
    global keypressed, mode, jukeboxKeyTime, jukeboxKey, recording_offset
    if key is not None:
        currentTime = time.ticks_ms()
        if (keypressed + 500) < currentTime:
            keypressed = currentTime
            print("Key pressed is:{} ".format(key))
            print("mode is: {}".format(mode))
            if key is "*":
                mode = 1
                key = None
            elif key is "#":
                mode = 3
                key = None
            elif mode is 2:
                if jukeboxKeyTime == 0:
                    jukeboxKeyTime = time.ticks_ms()
                    jukeboxKey = str(key)
                    print(jukeboxKey)
                elif (time.ticks_ms() - jukeboxKeyTime) < 1000:
                    print("capture second key " + str(time.ticks_ms() - jukeboxKeyTime))
                    if int(jukeboxKey) <= 99:
                        jukeboxKey = jukeboxKey + "" + str(key)
                        print(jukeboxKey)
                    lcd.clear()
                    lcd.set_cursor(0,0)
                    lcd.print("Mode: Jukebox")
                    lcd.set_cursor(0,1)
                    lcd.print("Playing track " + jukeboxKey)
                    # This is for recording the animation
#                     recording_offset = time.ticks_ms()
#                     print("starting track "+ jukeboxKey + " at time " + str(recording_offset))
#                     player.play(10,int(jukeboxKey))
#                     mode = 1
                    jukeBoxPlay(jukeboxKey)
                    jukeboxKeyTime = 0
                    jukeboxKey = 0
                else:
                    # This is for recording the animation
#                     recording_offset = time.ticks_ms()
#                     print("starting track "+ jukeboxKey + " at time " + str(recording_offset))
#                     player.play(10,int(jukeboxKey))
#                     mode = 1
                    lcd.clear()
                    lcd.set_cursor(0,0)
                    lcd.print("Mode: Jukebox")
                    lcd.set_cursor(0,1)
                    lcd.print("Playing track " + jukeboxKey)
                    jukeBoxPlay(jukeboxKey)
                    jukeboxKeyTime = 0
                    jukeboxKey = 0
            elif key is "0":
                mode = 2
                key = None
                
            # now we'll setup the s
            startSkelleton(key)
            
# starting in manual mode
startSkelleton()

def controlAnimation():
    global lastplay
    if len(currentAnimation) is not 0:
        currentTime = time.ticks_ms() - playback_offset
        nextTimestamp = currentAnimation[0][1]
        if currentTime >= nextTimestamp:
            #print(currentAnimation[0])
            moveServos(currentAnimation[0][0])
            currentAnimation.pop(0)
    elif autoplay == 1:
        if lastplay == "song":
            lastplay = "patter"
            #choose a random patter to say
            selectedAnswer = random.randint(1, 6)
            if selectedAnswer == 6:
                selectedAnswer = 8
            if selectedAnswer == 5:
                selectedAnswer = 6
            playRandomAnimation(str(selectedAnswer))
        else:
            lastplay = "song"
            # choose a song from random list
            selectedAnswer = random.randint(1, 18)
            jukeBoxPlay(str(selectedAnswer))

#### Main Program Loop
while True:
    # watch for keypress & kick off other stuff
    printKey()
    controlAnimation()
    if mode == 1:
        getJoystick()
        getMouthButton()
    elif mode == 3:
        getJoystick()
        getMouthButton()
        
        




