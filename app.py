import os
import subprocess
from fetch_lyrics import get_lrc
import subprocess
from utilsx import get_spotify_track_id, list_files, get_audio_duration
from description import save_description
import json
import description_helper

def driver(cutie_config):
    
    DEFAULT_PROJECT_DIRECTORY = cutie_config["default_project_directory"]
    SPOTIFY_URL = cutie_config["spotify_url"]

    spotify_track_id = get_spotify_track_id(SPOTIFY_URL)
    CURRENT_PROJECT_PATH = f"{DEFAULT_PROJECT_DIRECTORY}/{spotify_track_id}"
    os.makedirs(CURRENT_PROJECT_PATH, exist_ok=True)
    os.makedirs(f"{CURRENT_PROJECT_PATH}/output", exist_ok=True)

    # DOWNLOAD TRACK
    if (f"{spotify_track_id}-YT.wav" not in list_files(CURRENT_PROJECT_PATH)) and (cutie_config["video"]["sound_path"] is None):
        subprocess.run(
            [
                "spotdl",
                SPOTIFY_URL,
                "--output",
                f"{CURRENT_PROJECT_PATH}/{spotify_track_id}-YT.{{output-ext}}",
                "--format",
                "wav",
                "--lyrics",
                "synced",
                "--generate-lrc",
            ],
            check=True,
        )

    # DOWNLOADS LYRICS
    if (f"{spotify_track_id}-SP.lrc" not in list_files(CURRENT_PROJECT_PATH)) and (cutie_config["video"]["lrc_path"] is None):
        lyrics = get_lrc(
            spotify_track_id,
            f"{CURRENT_PROJECT_PATH}/{spotify_track_id}-SP.lrc",
            save=True,
        )

    audio_files = list_files(CURRENT_PROJECT_PATH, extension="wav", resolve=True)
    lrc_files = list_files(CURRENT_PROJECT_PATH, extension="lrc", resolve=True)

    if len(audio_files) != 0 and len(lrc_files) != 0:

        spotify_interface = description_helper.SpotifyInterface(spotify_track_id)

        render_quality = cutie_config["render_quality"]

        if cutie_config["video"]["sound_path"] is None:
            cutie_config["video"]["sound_path"] = f"{CURRENT_PROJECT_PATH}/{spotify_track_id}-YT.wav"
        if cutie_config["video"]["lrc_path"] is None:
            try:
                cutie_config["video"]["lrc_path"] = f"{CURRENT_PROJECT_PATH}/{spotify_track_id}-YT.lrc"
            except Exception as e:
                cutie_config["video"]["lrc_path"] = f"{CURRENT_PROJECT_PATH}/{spotify_track_id}-SP.lrc"
                if spotify_interface.get_duration_in_seconds() != get_audio_duration(f"{CURRENT_PROJECT_PATH}/{spotify_track_id}-YT.wav") :
                    print('Audio and LRC provider mismatch: May cause sync issues.')

        

        if cutie_config["thumbnail"]["title_name"] is None:
            cutie_config["thumbnail"]["title_name"] = spotify_interface.get_title()
        if cutie_config["thumbnail"]["artist_name"] is None:
            cutie_config["thumbnail"]["artist_name"] = spotify_interface.get_artists_in_fmt()

        env = os.environ.copy()                         # --> ye important hai 
        env["CUTIE_CONFIG"] = json.dumps(cutie_config)  # --> ye bhi bc


        if not cutie_config["no_video"]:
            subprocess.run(
                [
                    "manim",
                    f"-pq{render_quality}",
                    "--media_dir",
                    f"{CURRENT_PROJECT_PATH}/output",
                    "lyr_dev.py",
                    "Lyrics",
                ],
                env=env,
            )

        
        if not cutie_config["no_thumbnail"]:
            subprocess.run(
                [
                    "manim",
                    f"-pq{render_quality}",
                    "--media_dir",
                    f"{CURRENT_PROJECT_PATH}/output",
                    "thumbnail_dev.py",
                    "Thumbnail",
                ],
                env=env,
            )

        if not cutie_config["no_description"]:
            save_description(
                lrc_path=cutie_config["video"]["lrc_path"],
                title=spotify_interface.get_title(),
                artists=spotify_interface.get_artists_in_fmt(),
                save_path=f"{CURRENT_PROJECT_PATH}/output/description.txt",
            )

    else:
        raise Exception("Failed to fetch audio/lyrics")
