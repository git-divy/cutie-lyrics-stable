from manim import *
from timestamp_parser import parse_lrc
import os
import random
from fetch_metadata import get_track_names
import fetch_lyrics
import time
from pydub import AudioSegment

config.disable_caching = True


def eta_tracker():
    start_time = time.time()
    last_time = start_time
    total_iters = 0

    def update(current_iter, total_iter, prefix=""):
        nonlocal last_time, total_iters

        now = time.time()
        total_iters += 1

        elapsed = now - start_time
        avg_time = elapsed / total_iters if total_iters else 0

        remaining_iters = total_iter - current_iter
        eta = avg_time * remaining_iters

        # format nicely
        def fmt(t):
            m, s = divmod(int(t), 60)
            return f"{m:02d}:{s:02d}"

        print(
            f"{prefix}[{current_iter}/{total_iter}] | ETA: {fmt(eta)} | Elapsed: {fmt(elapsed)}"
        )

        last_time = now

    return update


def get_content(song_list, highlight=0, font_size=30, opacity=1):
    song_names = []
    base = Text("")
    for i, song_name in enumerate(song_list):

        song_name_slice_length = 18
        highlighted_song_name = song_name
        if len(song_name) > song_name_slice_length:
            highlighted_song_name = song_name[:song_name_slice_length] + "."

        pre = ""
        if len(str(i + 1)) == 1:
            pre = "0"

        if i == 0:
            if highlight == 0:
                song_names.append(
                    Text(
                        f"[{pre}{i+1}]  {highlighted_song_name}",
                        font_size=font_size + 8,
                    )
                    .set_opacity(opacity)
                    .next_to(base, DOWN, aligned_edge=LEFT)
                )
            else:
                song_names.append(
                    Text(f"[{pre}{i+1}]  {song_name}", font_size=font_size - 8)
                    .set_opacity(opacity - 0.50)
                    .next_to(base, DOWN, aligned_edge=LEFT)
                )
        elif i == highlight:
            song_names.append(
                Text(f"[{pre}{i+1}]  {highlighted_song_name}", font_size=font_size + 8)
                .set_opacity(opacity)
                .next_to(song_names[i - 1], DOWN, aligned_edge=LEFT)
            )
        else:
            song_names.append(
                Text(f"[{pre}{i+1}]  {song_name}", font_size=font_size - 8)
                .set_opacity(opacity - 0.50)
                .next_to(song_names[i - 1], DOWN, aligned_edge=LEFT)
            )

    content = VGroup(*song_names)
    content.move_to(ORIGIN).to_edge(LEFT)

    return content


def is_hindi(text: str) -> bool:
    return any("\u0900" <= char <= "\u097f" for char in text)


def is_renderable(text: str) -> bool:
    for char in text:
        # English (Basic Latin + common punctuation)
        if "\u0020" <= char <= "\u007e":
            continue

        # Hindi (Devanagari)
        if "\u0900" <= char <= "\u097f":
            continue

        # Optional: whitespace / newline
        if char in ["\n", "\t"]:
            continue

        # If anything else → reject
        return False

    return True


def apply_bg(lyc_animation, image_path, bg_opacity):
    bg = ImageMobject(image_path)
    bg.scale_to_fit_width(config.frame_width)
    bg.set_opacity(bg_opacity)
    lyc_animation.add(bg)
    return bg


def wrap_text(text, max_chars=12):
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        # Check if adding the next word exceeds limit
        if len(current_line) + len(word) + 1 <= max_chars:
            if current_line:
                current_line += " " + word
            else:
                current_line = word
        else:
            lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return "\n".join(lines), lines


def circular_file_iterator(folder_path):
    files = [
        os.path.join(folder_path, f)
        for f in os.listdir(folder_path)
        if os.path.isfile(os.path.join(folder_path, f))
    ]

    if not files:
        raise ValueError("No files found in directory")

    index = 0
    n = len(files)

    while True:
        yield files[index]
        index = (index + 1) % n


def smart_random_circular(folder_path):
    files = [
        os.path.join(folder_path, f)
        for f in os.listdir(folder_path)
        if os.path.isfile(os.path.join(folder_path, f))
    ]

    if not files:
        raise ValueError("No files found")

    while True:
        random.shuffle(files)
        for file in files:
            yield file


class LyricsAnimation(Scene):

    def construct(self):
        eta = eta_tracker()

        with register_font("custom_fonts\\NotoSansDevanagari-Regular.ttf"):
            # Params
            fade_time = 0.25
            font_size = DEFAULT_FONT_SIZE
            bg_opacity = 0.50
            internal_playlist_id = "pl_02"

            apply_bg(
                self,
                image_path="assets\\images\\Gemini_Generated_Image_v6tqgv6tqgv6tqgv.png",
                bg_opacity=bg_opacity,
            )
            track_meta = get_track_names("58eNU0JJvtAWAg9KUZ9Ghf")

            # self.add(Line(UP*3.5, DOWN*3.5).set_opacity(0.25))
            contents = []
            playlist_songs = [x[0] for x in track_meta]
            playlist_urls = [y[1] for y in track_meta]

            for i in range(-1, len(playlist_songs)):
                contents.append(get_content(playlist_songs, highlight=i))

            lrc_paths = []
            for k, _ in enumerate(contents):
                if k == len(contents) - 1:
                    break
                lrc_paths.append(
                    fetch_lyrics.get_lrc(
                        track_url=playlist_urls[k],
                        save_path=f"assets\\audio\\playlist\\{internal_playlist_id}",
                        save=True,
                    )[1]
                )
                time.sleep(2)

            old_content = contents[0]
            for j, _ in enumerate(contents[:]):

                if j == len(contents) - 1:
                    break

                new_content = contents[j + 1]

                self.play(ReplacementTransform(old_content, new_content), run_time=2)

                self.add_sound(
                    f"assets\\audio\\playlist\\{internal_playlist_id}\\{playlist_songs[j]}_spotdown.org.mp3"
                )
                audio = AudioSegment.from_file(
                    f"assets\\audio\\playlist\\{internal_playlist_id}\\{playlist_songs[j]}_spotdown.org.mp3"
                )
                audio_duration = len(audio) / 1000  # ms → seconds

                lrc_path = lrc_paths[j]

                stamped_lyrics = parse_lrc(lrc_path)

                old_content = new_content

                duration_sum = 0
                current_time = 0

                for i, line in enumerate(stamped_lyrics[:]):

                    # print(f"[{j+1}/{len(contents)-1}] --> [{i+1}/{len(stamped_lyrics)}]")
                    eta(
                        i + 1,
                        len(stamped_lyrics),
                        prefix=f"[{j+1}/{len(contents)-1}] --> ",
                    )

                    time_stamp = line["time"]
                    l_text: str = line["text"]

                    if l_text == "" or l_text == " ":
                        l_text = "..."

                    l_text, lines = wrap_text(l_text, max_chars=12)

                    wait_time = max(0, time_stamp - current_time)
                    if wait_time > 0:
                        self.wait(wait_time)

                    if i + 1 < len(stamped_lyrics):
                        next_time = stamped_lyrics[i + 1]["time"]
                        duration = next_time - time_stamp
                        duration_sum += duration
                    else:
                        duration = round(duration_sum / (len(stamped_lyrics) - 1), 6)

                    # Manim Objects
                    if not is_renderable(l_text):
                        continue

                    if is_hindi(l_text):
                        font = "Noto Sans Devanagari"
                        text_tb_written = (
                            MarkupText(l_text, font_size=font_size, font=font)
                            .set_opacity(0.75)
                            .move_to(3.5 * RIGHT)
                        )
                        text_low_opacity = (
                            MarkupText(l_text, font_size=font_size, font=font)
                            .set_opacity(0.50)
                            .move_to(3.5 * RIGHT)
                        )
                    else:
                        text_tb_written = (
                            Text(l_text, font_size=font_size)
                            .set_opacity(0.75)
                            .move_to(3.5 * RIGHT)
                        )
                        text_low_opacity = (
                            Text(l_text, font_size=font_size)
                            .set_opacity(0.50)
                            .move_to(3.5 * RIGHT)
                        )

                    # Animations
                    self.play(FadeIn(text_low_opacity), run_time=fade_time)
                    self.play(Write(text_tb_written), run_time=duration - 2 * fade_time)
                    self.play(
                        FadeOut(text_low_opacity),
                        FadeOut(text_tb_written),
                        run_time=fade_time,
                    )

                    current_time += wait_time + duration

                remaining_time = max(0, audio_duration - current_time)
                if remaining_time > 0:
                    self.wait(remaining_time)


# TODO : write custom rate function for Write() --> 15 April
# TODO : write vocal + intrumental based seperation engine either by web API or locally --> 15 April
