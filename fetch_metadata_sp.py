import requests
import base64
import os
from dotenv import load_dotenv

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")


class SpotifyAPI:
    def __init__(self) -> None:
        auth_str = f"{client_id}:{client_secret}"
        b64_auth = base64.b64encode(auth_str.encode()).decode()

        token_url = "https://accounts.spotify.com/api/token"
        headers = {"Authorization": f"Basic {b64_auth}"}
        data = {"grant_type": "client_credentials"}

        res = requests.post(token_url, headers=headers, data=data)
        res.raise_for_status()

        access_token = res.json()["access_token"]

        self.headers = {
            "Authorization": f"Bearer {access_token}"
        }

    def get_track_artists(self, track_id: str) -> list[str]:
        url = f"https://api.spotify.com/v1/tracks/{track_id}"

        response = requests.get(url, headers=self.headers)
        response.raise_for_status()

        track = response.json()

        return [artist["name"] for artist in track["artists"]]

    
