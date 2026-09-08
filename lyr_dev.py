from manim import * # type: ignore
from timestamp_parser import parse_lrc
from transliteration import GeminiAPI
from utilsx import apply_bg, wrap_text, is_non_english, get_font_name, list_files
import os
import json
from contextlib import ExitStack
config.disable_caching = True

CUTIE_CONFIG = cutie_config = json.loads(os.environ["CUTIE_CONFIG"])

class Lyrics(Scene):

    def construct(self):

        lrc_path = CUTIE_CONFIG["video"]["lrc_path"]
        sound_path = CUTIE_CONFIG["video"]["sound_path"]
        bg_path = CUTIE_CONFIG["video"]["bg_path"]
        custom_font_path = CUTIE_CONFIG["video"]["custom_font_path"]
        fade_time = CUTIE_CONFIG["video"]["fade_time"]
        font_size =  CUTIE_CONFIG["video"]["font_size"]
        slice_lyrics = CUTIE_CONFIG["video"]["slice_lyrics"]
        bg_opacity = CUTIE_CONFIG["video"]["bg_opacity"]
        t_opacity = CUTIE_CONFIG["video"]["t_opacity"]
        enable_no_fill = CUTIE_CONFIG["video"]["enable_no_fill"]
        enable_transliteration = CUTIE_CONFIG["video"]["enable_transliteration"]
        transliteration_language = CUTIE_CONFIG["video"]["transliteration_language"]
        reduction_factor = CUTIE_CONFIG["video"]["reduction_factor"]
        
        # --------------------------------------------------------------------------------------
        font_size = DEFAULT_FONT_SIZE * font_size
        correction_factor = reduction_factor * fade_time
        if slice_lyrics < 0: # TODO: fuck this will cause so many errors in future, fix this
            slice_lyrics = None

        stamped_lyrics = parse_lrc(lrc_path)
        stamped_lyrics = [
            {"time": k["time"] - correction_factor, "text": k["text"]}
            for k in stamped_lyrics
        ]

        if enable_transliteration:
            print("[Transliterating]")
            tr = GeminiAPI()
            past_lyrs = [stmp_lyr["text"] for stmp_lyr in stamped_lyrics]
            tr_lyrics = tr.transliterate(
                texts=[stmp_lyr["text"] for stmp_lyr in stamped_lyrics],
                language=transliteration_language,
            )
            stamped_lyrics = [
                {"time": stmp_lyr["time"], "text": tr_lyrics[i]}
                for i, stmp_lyr in enumerate(stamped_lyrics)
            ]
            present_lyrs = [stmp_lyr["text"] for stmp_lyr in stamped_lyrics]
            for past, present in zip(past_lyrs, present_lyrs):
                print(f"[{past}] --> [{present}]")

        self.add_sound(sound_path)
        if bg_path is not None:
            bg = apply_bg(self, bg_path, bg_opacity=bg_opacity, config=config)
        duration_sum = current_time = 0

        old_content = Text("")

        font_paths = list_files("custom_fonts", resolve=True)

        with ExitStack() as stack:
            registered_fonts = [
                stack.enter_context(register_font(path)) for path in font_paths
            ]
            for i, line in enumerate(stamped_lyrics[:slice_lyrics]):

                print(f"[{i}/{len(stamped_lyrics)}]")

                time_stamp = line["time"]
                l_text = line["text"]

                l_text = wrap_text(l_text, max_chars=24)

                wait_time = max(0, time_stamp - current_time)
                if wait_time > 0:
                    self.wait(wait_time)

                if i + 1 < len(stamped_lyrics):
                    next_time = stamped_lyrics[i + 1]["time"]
                    duration = next_time - time_stamp
                    duration_sum += duration
                else:
                    duration = round(duration_sum / (len(stamped_lyrics) - 1), 3)

                if is_non_english(l_text):
                    font = "Google Sans"
                else:
                    font = get_font_name(custom_font_path)

                # Animations Objects
                text_tb_written = MarkupText(
                    l_text, font_size=font_size, font=font
                ).set_opacity(t_opacity[0])

                if enable_no_fill:
                    text_low_opacity = (
                        MarkupText(l_text, font_size=font_size, font=font)
                        .set_opacity(t_opacity[1])
                        .set_fill(opacity=0)
                        .set_stroke(color=WHITE, width=2)
                    )

                else:  # Fills the text along with its stroke
                    text_low_opacity = MarkupText(
                        l_text, font_size=font_size, font=font
                    ).set_opacity(t_opacity[1])

                # Animations
                self.play(
                    TransformMatchingShapes(old_content, text_low_opacity),
                    run_time=reduction_factor * fade_time,
                )
                self.play(
                    Write(text_tb_written),
                    run_time=duration - reduction_factor * fade_time,
                )
                old_content = VGroup(text_low_opacity, text_tb_written)

                current_time += wait_time + duration

        self.wait(1)
