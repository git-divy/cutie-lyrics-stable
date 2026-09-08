import requests

URL = "https://spotify-lyrics-api-qb6p.onrender.com"
# Uses this docker image
# https://hub.docker.com/layers/akashrchandran/spotify-lyrics-api/latest

def get_lrc(track_id, output, save=False):
    
    response = requests.get(f"{URL}/?trackid={track_id}&format=lrc")

    lrc_content = ""
    if response.status_code != 404:
        print(response.json())
        for line in response.json()["lines"]:
            lrc_content += f"[{line['timeTag']}]{line['words']}\n"
    else:
        raise Exception('LRC not found')

   
    if save:
        with open(output, "w", encoding="utf-8") as lrc_file:
            lrc_file.write(lrc_content)

    return lrc_content


