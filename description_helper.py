from yt_dlp import YoutubeDL
import json
import requests
from bs4 import BeautifulSoup
from spotapi import Public

class YTInterface:
    def fetch_spotify_title(self, spotify_url):
        soup = BeautifulSoup(requests.get(spotify_url).text, "html.parser")
        h1 = soup.find("h1")
        if h1 is not None:
            h1_text = h1.get_text(strip=True)
            return h1_text
        else:
            raise Exception()

    def yt_info(self, query):

        ydl = YoutubeDL()

        search_query = f"ytsearch3:{query}"

        return ydl.extract_info(search_query, download=False)

    def fetch(self, spotify_url):
        info_dict = self.yt_info(query=self.fetch_spotify_title(spotify_url))

        item_contents = []

        for item in info_dict['entries']: # type: ignore
            item_contents.append({"title" : item["title"], "description" : item["description"]}) # type: ignore
            
        return item_contents

class SpotifyInterface:
    def __init__(self, spotify_id) -> None:
        self.song = Public.song_info(spotify_id)

    def get_artists_in_fmt(self):
        
        artists = []
        
        with open("extract.json", "w") as file:
            json.dump(self.song, file, indent=4)

        for first_artist in self.song['data']["trackUnion"]["firstArtist"]["items"]:
            artists.append(first_artist["profile"]["name"])
        for other_artist in self.song['data']["trackUnion"]["otherArtists"]["items"]:
            artists.append(other_artist["profile"]["name"])

        return ", ".join(artists)

    def get_duration_in_seconds(self):
        return int(float(self.song['data']["trackUnion"]["duration"]["totalMilliseconds"])/1000.0)

    def get_title(self):
        return self.song['data']["trackUnion"]["name"]