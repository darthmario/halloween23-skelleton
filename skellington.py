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

#Display setup
tm = tm1637.TM1637(clk=Pin(8), dio=Pin(7))

#keyscan setup
row = []
column = []

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
    if key is not None:
        print("Key pressed is:{} ".format(key))
        if key == "#":
            tm.show('play')
        elif key == "*":
            tm.show('lock')
        else:
            tm.show("   " + key)
    utime.sleep(0.2)
    
while True:
    printKey()