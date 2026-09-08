import timestamp_parser


def save_description(lrc_path, title, artists, save_path):
    stamped_lyrics = timestamp_parser.parse_lrc(lrc_path)

    text = f"{title}\n\nArtists : {artists}\n\nLyrics : \n"
    
    for line in stamped_lyrics:
        text += line["text"] + "\n"

    with open(save_path, "w", encoding="utf-8") as des:
        des.write(text)
