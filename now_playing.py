import os
import time
import serial
import spotipy
from serial.tools import list_ports
from spotipy.oauth2 import SpotifyOAuth
from get_lyrics import fetch_lyrics, parse_lrc

# Automatically find the port among all ports
def find_port():
    for p in list_ports.comports():
        if p.vid in (0x239A, 0x303A): # adafruit or esp
            return p.device
    raise SystemExit("Board not found")

board = serial.Serial(find_port(), 115200, timeout = 3, exclusive=True)
board.write(b"\n")
board.readline()

def send(kind, text = ""):
    board.write(f"{kind};{text}\n".encode())
    reply = board.readline().decode().strip()
    if reply != "ok":
        print(f"board rejected {kind!r}: {reply!r}")

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.environ["SPOTIPY_CLIENT_ID"],
    client_secret=os.environ["SPOTIPY_CLIENT_SECRET"],
    redirect_uri="http://127.0.0.1:8888/callback", # spotipy temporarily listens on 8888 port, spotify sends browser
    scope="user-read-currently-playing", # only can see what is currently playing
    cache_path=".spotify_token_cache",
))

last_id = None # last showed song 

while True:
    current = sp.current_user_playing_track()
    if current and current.get("item"): # if there is a current song
        song = current["item"]
        if song['id'] != last_id: # new song is playing
            last_id = song['id']
            send("C") # clear board, change song
            send("T", f"{song['name']} - {song["artists"][0]["name"]}")
            
            lrc = fetch_lyrics(song['name'], song['artists'][0]['name'])
            lyrics = parse_lrc(lrc) if lrc else []
            print(f"found {len(lyrics)} lyric lines")
        secs = current["progress_ms"] // 1000
        total = song['duration_ms'] // 1000 # convert to seconds 

        send("L", f"{secs // 60} : {secs % 60:02} / {total // 60} : {total % 60:02}")
    time.sleep(4)

