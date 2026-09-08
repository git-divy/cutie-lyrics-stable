from fontTools.ttLib import TTFont
from manim import * # type: ignore
import os
from functools import wraps
from pathlib import Path
from pydub import AudioSegment

def get_spotify_track_id(url: str) -> str:
    return url.split("/track/")[1].split("?")[0]

def list_files(folder_path, extension=None, resolve=False):
    folder = Path(folder_path)
    if extension is None:
        files = [file for file in folder.iterdir() if file.is_file()]
    else:
        files = [file for file in folder.glob(f"*.{extension}")]

    if resolve:
        return [str(f.resolve()) for f in files]
    else:
        return [f.name for f in files]

def wrap_text(text, max_chars=12):
    words = text.split()
    lines = []
    current_line = ""

    for word in words:

        while len(word) > max_chars:

            if current_line:
                lines.append(current_line)
                current_line = ""

            lines.append(word[: max_chars - 1] + "-")
            word = word[max_chars - 1 :]

        if not current_line:
            current_line = word
        elif len(current_line) + 1 + len(word) <= max_chars:
            current_line += " " + word
        else:
            lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return "\n".join(lines)

def apply_bg(lyc_animation, image_path, bg_opacity, config, fit=True):
    bg = ImageMobject(image_path)
    if fit:
        bg.scale_to_fit_width(config.frame_width)
    bg.set_opacity(bg_opacity)
    lyc_animation.add(bg)
    return bg

def get_font_name(font_path: str) -> str:
    try:
        font = TTFont(font_path)
        name = ""

        for record in font["name"].names:
            if record.nameID == 1:  # Font Family name
                try:
                    name = record.toStr()
                except:
                    name = record.string.decode("utf-8", errors="ignore")
                break

        font.close()
        return name

    except Exception as e:
        print(f"Error reading font: {e}")
        raise Exception()

def is_non_english(text: str) -> bool:
    return any(ord(c) > 127 for c in text)

def ffplay_preview(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)

        video = self.renderer.file_writer.movie_file_path

        # start = non-blocking on windows
        os.system(f'start ffplay -autoexit "{video}"')

        return result

    return wrapper

def gradient_overlay(
    width=None,
    height=None,
    steps=100,
    color=BLACK,
    max_opacity=1.0,
    direction="left_to_right",
    easing=smootherstep,
):
    """
    Gradient directions:

    left_to_right:
        BLACK ---> transparent

    right_to_left:
        transparent ---> BLACK

    top_to_bottom:
        BLACK
          ↓
        transparent

    bottom_to_top:
        transparent
          ↑
        BLACK
    """

    width = width or config.frame_width
    height = height or config.frame_height

    strips = VGroup()

    horizontal = direction in (
        "left_to_right",
        "right_to_left",
    )

    if horizontal:

        strip_width = width / steps

        for i in range(steps):

            t = i / (steps - 1)

            # reverse opacity direction
            if direction == "left_to_right":
                opacity_t = 1 - t
            else:
                opacity_t = t

            opacity = easing(opacity_t) * max_opacity

            rect = Rectangle(
                width=strip_width + 0.001,
                height=height,
                stroke_width=0,
                fill_color=color,
                fill_opacity=opacity,
            )

            x = -width / 2 + strip_width * (i + 0.5)

            rect.move_to([x, 0, 0]) # type: ignore

            strips.add(rect)

    else:

        strip_height = height / steps

        for i in range(steps):

            t = i / (steps - 1)

            if direction == "top_to_bottom":
                opacity_t = 1 - t
            else:
                opacity_t = t

            opacity = easing(opacity_t) * max_opacity

            rect = Rectangle(
                width=width,
                height=strip_height + 0.001,
                stroke_width=0,
                fill_color=color,
                fill_opacity=opacity,
            )

            y = height / 2 - strip_height * (i + 0.5)

            rect.move_to([0, y, 0]) # type: ignore

            strips.add(rect)

    return strips

def get_audio_duration(file_path):
    audio = AudioSegment.from_file(file_path)
    return audio.duration_seconds  # Returns duration in seconds