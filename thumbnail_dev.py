from manim import *  # type: ignore
from lyr_dev import get_font_name
from utilsx import gradient_overlay, apply_bg, list_files, wrap_text
import os
import json
from contextlib import ExitStack

CUTIE_CONFIG = cutie_config = json.loads(os.environ["CUTIE_CONFIG"])


class Thumbnail(Scene):

    def construct(self):

        img_path = CUTIE_CONFIG["thumbnail"]["img_path"]
        title_name = CUTIE_CONFIG["thumbnail"]["title_name"]
        artist_name = CUTIE_CONFIG["thumbnail"]["artist_name"]
        font_size = CUTIE_CONFIG["thumbnail"]["font_size"]
        opacity = CUTIE_CONFIG["thumbnail"]["opacity"]
        custom_font_path = CUTIE_CONFIG["thumbnail"]["custom_font_path"]
        
        # ------------------------------------------------------------------------

        title_name = f"<b>{wrap_text(title_name, max_chars=24)}</b>"
        font_size = DEFAULT_FONT_SIZE * font_size
        if img_path is not None:
            apply_bg(self, img_path, bg_opacity=0.90, config=config)
        font_paths = list_files("custom_fonts", resolve=True)
        font = get_font_name(custom_font_path)

        with ExitStack() as stack:
            registered_fonts = [
                stack.enter_context(register_font(path)) for path in font_paths
            ]

            lyrics = MarkupText(
                "[Lyrics]",
                font_size=font_size // 2.5,
                font="Google Sans",
                weight=NORMAL,
            ).set_opacity(opacity)
            title = MarkupText(
                title_name, font_size=font_size, font=font, weight=NORMAL
            ).set_opacity(opacity)
            artist = (
                MarkupText(artist_name, font_size=font_size // 3.0, font="Google Sans")
                .set_opacity(opacity - 0.20)
                .next_to(title, DOWN, buff=0.4)
            )

            group = VGroup(title, artist)
            # group.move_to(2.25*(DOWN + 1.77*RIGHT))
            # group.move_to(14.22 / 4 * LEFT)

            lyrics.move_to(0.42 * (8 * UP + 14.22 * RIGHT))

            nf_1 = 2.5
            gradient_top = gradient_overlay(
                width=None,
                height=config.frame_height / nf_1,
                steps=100,
                max_opacity=0.50,
                easing=rate_functions.ease_out_cubic,
                direction="top_to_bottom",
            )

            nf_2 = 2.5
            gradient_bottom = gradient_overlay(
                width=None,
                height=config.frame_height / nf_2,
                steps=100,
                max_opacity=0.50,
                easing=rate_functions.ease_out_cubic,
                direction="bottom_to_top",
            )

        self.add(gradient_top)
        gradient_top.move_to(nf_1 * UP)

        self.add(gradient_bottom)
        gradient_bottom.move_to(nf_2 * DOWN)

        self.add(group)
        self.add(lyrics)
