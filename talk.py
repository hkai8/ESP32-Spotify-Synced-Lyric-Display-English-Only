import time
from serial.tools import list_ports
import serial

# Automatically find the port among all ports
def find_port():
    for p in list_ports.comports():
        if p.vid in (0x239A, 0x303A): # adafruit or esp
            return p.device
    raise SystemExit("Board not found")
    
board = serial.Serial(find_port(), 115200, timeout = 3) # open connection 

while True:
    text = input("> ")
    if text == 'quit':
        break
    start = time.time()
    board.write((text + "\n").encode())
    reply = board.readline().decode().strip() # waits to read from board, decode from bytes to string, strip of white space
    took = (time.time() - start) * 1000
    print(f"board said: {reply!r} ({took:.0f} ms)")

board.close()
