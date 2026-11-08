import time
import serial
from serial.tools import list_ports

def find_port():
    for p in list_ports.comports():
        if p.vid in (0x239A, 0x303A):
            return p.device
    raise SystemExit("Board not found")

board = serial.Serial(find_port(), 115200, timeout = 3)
board.write(b"\n")
board.readline()

while True:
    now = time.strftime("%H : %M : %S")
    board.write((now + '\n').encode())
    board.readline()

    t = time.time()
    time.sleep(1 - (t % 1))