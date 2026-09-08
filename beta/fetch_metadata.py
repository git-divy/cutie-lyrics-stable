import requests
import base64
import os
from pydub import AudioSegment
from dotenv import load_dotenv

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
token = None


def get_track_names(album_id):
    auth_str = f"{client_id}:{client_secret}"
    b64_auth = base64.b64encode(auth_str.encode()).decode()

    token_url = "https://accounts.spotify.com/api/token"

    headers = {"Authorization": f"Basic {b64_auth}"}

    data = {"grant_type": "client_credentials"}

    res = requests.post(token_url, headers=headers, data=data).json()
    # print(res)
    access_token = res["access_token"]
    global token
    token = access_token
    # print(access_token)

    headers = {"Authorization": f"Bearer {access_token}"}

    res = requests.get(f"https://api.spotify.com/v1/albums/{album_id}", headers=headers)
    #print(res.text)
    res = res.json()
  

    return [
        (item["name"], f"https://open.spotify.com/track/{item['id']}")
        for item in res["tracks"]["items"]
    ]
    # print(track["name"], "-", track["artists"][0]["name"])


def fetch_album_tracks(album_id, token):
    url = f"https://api.spotify.com/v1/albums/{album_id}"

    headers = {"Authorization": f"Bearer {token}"}

    res = requests.get(url, headers=headers).json()
    return res["tracks"]["items"]


def prettify_tracks(tracks):
    lines = []

    for i, track in enumerate(tracks, start=1):
        name = track["name"]

        # Multiple artists
        artists = track["artists"]
        artist_names = ", ".join(a["name"] for a in artists)

        # Artist profile links
        # artist_links = ", ".join(
        #     f"https://open.spotify.com/artist/{a['id']}" for a in artists
        # )

        # track_link = f"https://open.spotify.com/track/{track['id']}"

        line = f"{i:02d}. {name} – {artist_names}"

        lines.append(line)

    return "\n".join(lines)

def prettify_tracks_with_timestamps(tracks, time_stamps:list):
    lines = []

    for i, track in enumerate(tracks, start=1):
        ts = time_stamps[i-1]
        name = track["name"]

        # Multiple artists
        artists = track["artists"]
        artist_names = ", ".join(a["name"] for a in artists)

        # Artist profile links
        # artist_links = ", ".join(
        #     f"https://open.spotify.com/artist/{a['id']}" for a in artists
        # )

        # track_link = f"https://open.spotify.com/track/{track['id']}"

        line = f"{ts} {name}"

        lines.append(line)

    return "\n".join(lines)


def seconds_to_timestamp(seconds_list, include_zero=True):
    def format_time(sec):
        sec = int(round(sec))  # round to nearest second
        minutes = sec // 60
        seconds = sec % 60
        return f"{minutes:02d}:{seconds:02d}"

    timestamps = []

    if include_zero:
        timestamps.append("00:00")

    for sec in seconds_list:
        timestamps.append(format_time(sec))

    return timestamps



if __name__ == "__main__":

    album_id = "58eNU0JJvtAWAg9KUZ9Ghf"
    internal_playlist_id = "pl_02"
    
    tracks = get_track_names(album_id)
    tracks_ = fetch_album_tracks(album_id, token=token)

    

    total = 2
    track_lengths = []
    
    for tr in tracks:
        audio = AudioSegment.from_file(f"assets\\audio\\playlist\\{internal_playlist_id}\\{tr[0]}_spotdown.org.mp3")
        audio_duration = len(audio) / 1000  # ms → seconds
        total += audio_duration + 2
        track_lengths.append(round(total, 3))

    time_stamps = seconds_to_timestamp(track_lengths, include_zero=True)

    with open("description.txt", "w", encoding="utf-8") as des:
        pretty_tracks = prettify_tracks_with_timestamps(tracks_, time_stamps) + '\n\nArtists-\n'+prettify_tracks(tracks_)
        print(pretty_tracks)
        des.write(pretty_tracks)
