import time
import serial
from serial.tools import list_ports

# Automatically find the port among all ports
def find_port():
    for p in list_ports.comports():
        if p.vid in (0x239A, 0x303A): # adafruit or esp
            return p.device
    raise SystemExit("Board not found")
    
board = serial.Serial(find_port(), 115200, timeout = 3)
board.write(b"\n")
board.readline()

def send(kind, text = ""):
    board.write(f"{kind};{text}\n".encode())
    reply = board.readline().decode().strip()
    if reply != "ok":
        print(f"board rejected {kind!r}: {reply!r}")

send("C")
send("T", "Twinkle Twinkle Little Star - Traditional")

lyrics = [
    "Twinkle, twinkle, little star",
    "How I wonder what you are",
    "Up above the world so high",
    "Like a diamond in the sky",
]

for i in range(len(lyrics)):
    send("L", lyrics[i])
    if i + 1 < len(lyrics):
        send("N", lyrics[i + 1])
    else:
        send("N", "")
    time.sleep(2)

send("L", "(end)")
