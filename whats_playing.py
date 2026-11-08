import os 
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.environ["SPOTIPY_CLIENT_ID"],
    client_secret=os.environ["SPOTIPY_CLIENT_SECRET"],
    redirect_uri="http://127.0.0.1:8888/callback", # spotipy temporarily listens on 8888 port, spotify sends browser
    scope="user-read-currently-playing", # only can see what is currently playing
    cache_path=".spotify_token_cache",
)) # create a spotify client object
# os.environ is a dictionary of all terminal environ variables, feed it the variable name
# spotify token cache
# saves result in file so no need to relog in everytime in a JSON file as long as access toke is still valid
# remove cache file when you add new scope

#.gitignore
# tells git which files to leave out -> secrets, build output, editor settings, system junk, caches

current = sp.current_user_playing_track()
#print(json.dumps(current, indent=2))

if current is None:
    print("Nothing is playing")
else:
    song = current['item']
    print(f"Song: {song['name']}")
    print(f"Artist: {song['artists'][0]['name']}")
    print(f"Position: {current['progress_ms'] / 100} s")
    print(f"Length: {song['duration_ms'] / 100} s")
    print(f"Playing: {current['is_playing']}")
