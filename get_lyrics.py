import requests
import re

TIMESTAMP = re.compile(r"\[(\d+):(\d+(?:\.\d+)?)\]")
    # regex:
    # \[ \] string literals need backward slashes
    # (\d+) one or more digits
    # : colon
    # (\d+(?:\.\d+)?) digits, optionally followed by . and more digits ? -> stuff before it is optional

    # ?: non-capturing group, does not return as result itself


def fetch_lyrics(track, artist):
    # ask LRCLIB for a song's synced lyrics. Returns LRC text, or None
    response = requests.get(
        "https://lrclib.net/api/get",
        params={"track_name": track, "artist_name": artist}, # sends HTTP get request for track name and artist name
        headers={"User-Agent": "lyrics-learn/1.0"},
        timeout=10,
    )
    if response.status_code != 200:
        return None
    return response.json().get("syncedLyrics")

def parse_lrc(lrc_text):
    lines = []
    for raw in lrc_text.splitlines():
        stamps = TIMESTAMP.findall(raw) #only the timestamps on this line
        words = TIMESTAMP.sub("", raw).strip() #line with time stamps removed

        for minutes, seconds, in stamps:
            lines.append((int(minutes)* 60 + float(seconds), words))
    lines.sort()
    return lines

# lrc = fetch_lyrics("Viva La Vida", "Coldplay")
# if lrc:
#     for t, text in parse_lrc(lrc)[:8]:
#         print(f"{t:7.2f} {text}")