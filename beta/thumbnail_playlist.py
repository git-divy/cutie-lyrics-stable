from manim import *
from lyr_dev import apply_bg
import fetch_metadata

config.disable_caching = True


def smoothstep(t):
    return t * t * (3 - 2 * t)


def smootherstep(t):
    return t * t * t * (t * (6 * t - 15) + 10)


def ease_in(t):
    return t**3


def ease_out(t):
    return 1 - (1 - t) ** 3


def left_gradient_overlay(
    width=None,
    height=None,
    steps=60,
    max_opacity=0.8,
    direction="right_to_left",
    s_func=smootherstep,
):
    if width is None:
        width = config.frame_width / 2
    if height is None:
        height = config.frame_height

    strips = VGroup()
    step_width = width / steps

    for i in range(steps):
        t = i / (steps - 1)

        if direction == "left_to_right":
            opacity = s_func(t) * max_opacity
        else:
            opacity = s_func(1 - t) * max_opacity

        rect = Rectangle(
            width=step_width,
            height=height,
            stroke_width=0,
            fill_color=BLACK,
            fill_opacity=opacity,
        )

        # KEY CHANGE: anchor from LEFT edge
        rect.move_to(LEFT * (config.frame_width / 2 - step_width * i - step_width / 2))

        strips.add(rect)

    return strips


def get_content(song_list, highlight=0, font_size=30 + 5, opacity=1):
    song_names = []
    base = Text("")
    for i, song_name in enumerate(song_list):

        song_name_slice_length = 18
        highlighted_song_name = song_name
        if len(song_name) > song_name_slice_length:
            highlighted_song_name = song_name[:song_name_slice_length] + "."

        pre = ""
        if len(str(i)) == 1:
            pre = "0"

        if i == 0:
            if highlight == 0:
                song_names.append(
                    Text(f"{i+1}. {highlighted_song_name}", font_size=font_size + 30)
                    .set_opacity(opacity)
                    .next_to(base, DOWN, aligned_edge=LEFT)
                )
            else:
                song_names.append(
                    Text(f"{i+1}. {song_name}", font_size=font_size - 8)
                    .set_opacity(opacity)
                    .next_to(base, DOWN, aligned_edge=LEFT)
                )
        elif i == highlight:
            song_names.append(
                Text(f"{i+1}. {highlighted_song_name}", font_size=font_size + 8)
                .set_opacity(opacity)
                .next_to(song_names[i - 1], DOWN, aligned_edge=LEFT)
            )
        else:
            song_names.append(
                Text(f"{i+1}. {song_name}", font_size=font_size - 8)
                .set_opacity(opacity)
                .next_to(song_names[i - 1], DOWN, aligned_edge=LEFT)
            )

    content = VGroup(*song_names)
    content.move_to(ORIGIN + 3.5 / 3).to_edge(LEFT)

    return content


class ThumbnailGen(Scene):

    def construct(self):

        song_meta_data = song_meta.get_track_names("58eNU0JJvtAWAg9KUZ9Ghf")

        aashiqui_2_songs = [x[0] for x in song_meta_data]
        aashiqui_2_songs = [x[0] for x in song_meta_data]

        img_path = BG_PATH

        img_path = "assets\\images\\Gemini_Generated_Image_v6tqgv6tqgv6tqgv.png"

        font_size = 3 * 10
        opacity = 1

        apply_bg(self, img_path, bg_opacity=1)

        # Add gradient overlay
        gradient = left_gradient_overlay(
            width=config.frame_width / 2,
            steps=100,  # higher = smoother
            max_opacity=0.75,
            s_func=smootherstep,
        )

        self.add(gradient)

        # self.add(Line(UP*3.5, DOWN*3.5).set_opacity(0.50))

        contents = []

        self.add(get_content(aashiqui_2_songs, highlight=-1))
