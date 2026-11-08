import os
import time
import serial
import spotipy
from serial.tools import list_ports
from spotipy.oauth2 import SpotifyOAuth
from get_lyrics import fetch_lyrics, parse_lrc

POLL_SECONDS = 4        # how often to ask Spotify
LEAD_SECONDS = 0.5      # how early to show each line


# Automatically find the board among all ports
def find_port():
    for p in list_ports.comports():
        if p.vid in (0x239A, 0x303A):           # Adafruit or Espressif
            return p.device
    raise SystemExit("Board not found")


board = serial.Serial(find_port(), 115200, timeout=3, exclusive=True)
board.write(b"\n")
board.readline()


def send(kind, text=""):
    board.write(f"{kind};{text}\n".encode())
    reply = board.readline().decode().strip()
    if reply != "ok":
        print(f"board rejected {kind!r}: {reply!r}")


def current_index(lyrics, position):
    last_reached = -1
    for i, (t, _) in enumerate(lyrics):
        if t <= position:
            last_reached = i
        else:
            break
    return last_reached     # searches from the start, so seeking backward works too
  

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.environ["SPOTIPY_CLIENT_ID"],
    client_secret=os.environ["SPOTIPY_CLIENT_SECRET"],
    redirect_uri="http://127.0.0.1:8888/callback",
    scope="user-read-currently-playing",
    cache_path=".spotify_token_cache",
))

song_id = None          # song on screen
lyrics = []             # [(seconds, text), ...]
shown_index = None      # lyric line on screen
spotify_pos = 0.0       # position Spotify last told us (s)
spotify_time = 0.0      # when it told us (our clock)
playing = False
last_ask = 0.0          # when we last asked Spotify

send("C")
send("T", "Connected")
send("L", "Play something on Spotify")

while True:
    now = time.monotonic()

    # 1) Every few seconds: ask Spotify where we are
    if now >= last_ask + POLL_SECONDS:
        last_ask = now
        try:
            current = sp.current_user_playing_track()
        except Exception as e:
            print("error:", e)
            current = None

        if current and current.get('item'): # a song is playing
            song = current['item']
            playing = current['is_playing']
            spotify_pos = current['progress_ms'] / 1000
            spotify_time = now

            temp_id = song.get('id') or song.get('uri')  # local files have no id
            if temp_id != song_id: # a new song
                song_id = temp_id
                artist = song['artists'][0]['name']
                print("now playing:", song['name'], "-", artist)
                send("C")
                send("T", f"{song['name']} - {artist}")

                lrc = fetch_lyrics(song['name'], artist)
                lyrics = parse_lrc(lrc) if lrc else []
                print("lines found:", len(lyrics))
                shown_index = None # force the first line to be sent
                if not lyrics:
                    send("L", "No synced lyrics")
        else: # nothing playing
            if song_id is not None: # music just stopped
                send("C")
                send("T", "Nothing playing")
            song_id = None
            lyrics = []
            playing = False

    if lyrics:
        temp_index = current_index(lyrics, spotify_pos + (now - spotify_time if playing else 0) + LEAD_SECONDS) # add elapsed time since spotify time
        if (shown_index != temp_index ):
            text = lyrics[temp_index][1] if temp_index >= 0 else ""
            shown_index = temp_index
            send("L", text or "...")
            if shown_index + 1 < len(lyrics): 
                send("N", lyrics[shown_index + 1][1])
            else:
                send("N", "")

    time.sleep(0.1)