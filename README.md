# ESP32 Spotify Synced Lyric Display

Shows the current line of whatever song is playing on Spotify, synced to playback, on a
240×135 TFT screen driven by an ESP32-S2.

A Python service on the computer gets the current track and playback position from the
Spotify Web API, downloads time-stamped lyrics from [LRCLIB](https://lrclib.net), and sends
each line to the ESP32 over USB serial at the right moment. The ESP32 parses the messages
and draws the title, current line and next line in separate regions of the screen.

```
Spotify Web API ──► Python (sync.py) ──USB serial──► ESP32-S2 ──► TFT
LRCLIB          ──►
```

## Hardware

- Adafruit Feather ESP32-S2 TFT (240×135 ST7789 display)
- USB-C data cable

## How it works

### Python service (`sync.py`)
- **Polling:** asks Spotify for the current track and position every 4 seconds
  (`POLL_SECONDS`), to stay well within API rate limits.
- **Dead reckoning:** between polls, estimates the position as
  `last_position + time_since_last_poll` while playing. Every poll corrects any drift.
- **Lyrics:** when the song changes, downloads its LRC lyrics from LRCLIB (matched by title
  and artist) and parses them into a sorted list of `(seconds, text)`.
- **Current line:** finds the last line whose timestamp has been reached. It searches from
  the start each time, so seeking backward works too.
- **Only sends on change:** the loop runs every 0.1 s, but a message goes to the board only
  when the current line actually changes.
- **Pauses, skips and seeking:** pausing freezes the estimate; a new track ID clears the
  screen and loads new lyrics; seeking is picked up at the next poll (within 4 s).
- **`LEAD_SECONDS`** (0.5 s) shows each line slightly early to make up for transfer and
  drawing time.

### ESP32 firmware (`src/main.cpp`)
Reads serial input byte by byte into a buffer until `\n`, then handles one message:

| Message | Meaning | Drawn as |
|---|---|---|
| `T;<text>` | song title | top, small, green |
| `L;<text>` | current lyric line | middle, large, white |
| `N;<text>` | next lyric line | bottom, small, grey |
| `C;` | clear the screen | |

- Each message gets exactly one reply: `ok`, or `err` for malformed or unknown messages.
- Each screen region is erased and redrawn on its own, so updates don't flicker the whole screen.
- Text is word-wrapped to fit each region, and words longer than a row are split.

## Setup

### 1. Flash the ESP32 (PlatformIO)
Open this folder in VS Code with the PlatformIO extension and click **Upload**.
`platformio.ini` sets the board and libraries:
- Adafruit ST7735 and ST7789 Library
- Adafruit GFX Library

### 2. Spotify app
Create an app at the [Spotify developer dashboard](https://developer.spotify.com/dashboard)
and add `http://127.0.0.1:8888/callback` as a Redirect URI.

### 3. Python
```sh
pip3 install spotipy requests pyserial
export SPOTIPY_CLIENT_ID="your-client-id"
export SPOTIPY_CLIENT_SECRET="your-client-secret"
python3 sync.py
```
The first run opens a browser to log in to Spotify. The board is found automatically by its
USB vendor ID. Only one program can use the serial port at a time, so close any serial
monitor first.

## Files

| File | Purpose |
|---|---|
| `src/main.cpp` | ESP32 firmware: serial protocol and display |
| `sync.py` | Main program: Spotify polling, lyric sync, sending to the board |
| `get_lyrics.py` | Downloading (LRCLIB) and parsing LRC lyrics |
| `now_playing.py`, `whats_playing.py` | Earlier steps: showing the current track |
| `talk.py`, `lyrics_demo.py`, `clock.py` | Serial protocol testing tools |
| `ports.py` | Finding the board's serial port |

## Possible improvements
- Run standalone over Wi-Fi on the ESP32, without the computer
- Match lyrics by song duration too, to avoid live or remix versions
- A progress bar showing elapsed and total time
- Support for Chinese, Japanese and Korean text
