import re

EMPTY_FILLER = "---"
RETENTION_LIMIT = 2
RETENTION_STARTING_POINT = 0.5

def parse_lrc(file_path):
    lyrics = []

    time_pattern = re.compile(r"\[(\d+):(\d+(?:\.\d+)?)\]")
    flag = True

    with open(file_path, encoding="utf-8") as f:
        for line in f:
            matches = time_pattern.findall(line)

            if not matches:
                continue

            text = time_pattern.sub("", line).strip()
            if text == "":
                text = EMPTY_FILLER

            for minute, second in matches:
                timestamp = round(int(minute) * 60 + float(second), 3)

                if flag:
                    if timestamp > RETENTION_LIMIT:
                         lyrics.append({"time": 0.5, "text": EMPTY_FILLER})
                    flag = False
               
                lyrics.append({"time": timestamp, "text": text})

    lyrics.sort(key=lambda x: x["time"])

    return lyrics
