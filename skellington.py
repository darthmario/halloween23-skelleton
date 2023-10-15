from machine import Pin, ADC
import utime
import tm1637

# for display https://github.com/mcauser/micropython-tm1637
# for servo controller https://github.com/jposada202020/MicroPython_PCA9685

# keymatrix setup
keyMatrix = [
    [ "1",  "2",   "3"],
    [ "4",    "5",   "6"],
    [ "7",    "8",   "9"],
    ["*",  "0", "#"]
]

colPins = [2,0,4]
rowPins = [1,6,5,3]

# Display setup
tm = tm1637.TM1637(clk=Pin(8), dio=Pin(7))

# Joystick Setup
xAxis = ADC(Pin(27))
yAxis = ADC(Pin(26))
button = Pin(9, Pin.IN, Pin.PULL_UP)

# keyscan setup
row = []
column = []
keypressed = False;

for item in rowPins:
    row.append(machine.Pin(item, machine.Pin.OUT))
for item in colPins:
    column.append(machine.Pin(item,machine.Pin.IN, machine.Pin.PULL_DOWN))
key ='0'
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
def printKey():
    key=scanKeypad()
    global keypressed
    if key is not None:
        print("keypressd value is"+str(keypressed))
        print("Key pressed is:{} ".format(key))
        keypressed = True
        print("keypressd value is"+str(keypressed))
        # now we'll setup the debounce so we don't have to use sleep later on.
        if key == "#":
            tm.show('auto')
        elif key == "*":
            tm.show('free')
        elif key == "0":
            tm.show('manu')
        else:
            tm.show("   " + key)


def getJoystick():
    xValue = xAxis.read_u16()
    yValue = yAxis.read_u16()
    buttonValue = button.value()
    print(str(xValue)+", "+str(yValue)+" -- "+str(buttonValue))
    
while True:
    printKey()
    #getJoystick()
    utime.sleep(0.2)