# Force aligner code for word level sync video and uses different lyrics animation than ususal

from manim import *
from fontTools.ttLib import TTFont
config.disable_caching = True
import json

def wrap_text(text, max_chars=12):
    words = text.split()
    lines = []
    current_line = ""

    for word in words:

        while len(word) > max_chars:

            if current_line:
                lines.append(current_line)
                current_line = ""

            lines.append(word[:max_chars-1] + "-")
            word = word[max_chars-1:]

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

def get_ts(json_file):
    with open(json_file, 'r') as json_file_contents:
        ts = json.load(json_file_contents)

    return ts['segments']

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
    
def apply_bg(lyc_animation, image_path, bg_opacity):
    bg = ImageMobject(image_path)
    bg.scale_to_fit_width(config.frame_width)
    bg.set_opacity(bg_opacity)
    lyc_animation.add(bg)
    return bg


class SmoothedWrite(Write):
    def get_sub_alpha(self, alpha, index, num_submobjects):
        # Bypass per-character staggering — treat all chars at same alpha
        return self.rate_func(alpha)
    

highlights = [
    "kachi",
    "qadamon",
    "jalataa",
    "roti",
    "shabnam",
    "deevaaron",
    "bhool",
    "kahaan",
    "soona",
    "sajda",
    "honton",
    "pahunch",
    "bargad",
    "cheharaa",
    "jaadoo",
    "sandeshaa",
    "divaanaapan",
    "lakiron",
    "ibaadatein",
    "aashiq",
    "raani",
    "paagal",
    "khushboo",
    "chadar",
    "paayal",
    "jharokha",
    "doob",
    "pyaaree",
    "bhashaa",
    "halchal",
    "bargad",
    "soona",
    "sajda",
    "honton",
    "pahunch",
    "bargad",
    "cheharaa",
    "jaadoo",
    "sandeshaa",
    "divaanaapan",
    "lakiron",
    "ibaadatein",
    "aashiq"
]

class Animation1(Scene):
    def construct(self):
        custom_font_path = "custom_fonts\\Stardom-Regular.ttf"


        with register_font(custom_font_path):
            font = get_font_name(custom_font_path)

            sound_path = r"assets\audio\bargad_spotdown.org.mp3"
            bg_path = r'assets\images\ComfyUI_temp_etxcg_00001_.png'
            bg_opacity = 0.5
            sf = 0.04

            self.add_sound(sound_path)

            #self.add_sound(sound_path)
            bg = apply_bg(self, bg_path, bg_opacity=bg_opacity)

            fade_time = 0.25/2

            ts = get_ts(r"audio [vocals].json")


            current_fade_deff = 0
            for j, ts_item in enumerate(ts[:]):
                print(f"[{j}/{len(ts)}]")

                raw_text = ts_item["text"]
                max_word_length = len(max(raw_text.split(' ')))

                raw_text = wrap_text(raw_text, max_chars=24)

                text_0 = MarkupText(raw_text, font_size=DEFAULT_FONT_SIZE+6, font=font).move_to(2*UP)
                text_tb_written = text_0.copy()
                text_tb_written.set_style(fill_opacity=0.10, stroke_width=2, stroke_opacity=0.25)
                
                chars = text_0.submobjects

                for c in chars:
                    c.set_opacity(0.2)

                chars_2 = text_tb_written.submobjects

                # self.add(text_0)

                animations = []

                start_idx = 0
                for i, item in enumerate(ts_item["words"]):
                    word = item['word']
                    end_idx = start_idx + len(word)
                    target_chars = chars[start_idx:end_idx]
                    target_chars_2 = chars_2[start_idx:end_idx]

                    run_time = (item['end'] - item['start'])

                    opacity_strength = 1
                    highlight_color = "#176bd8"
                    if word in highlights:
                        for c1, c2 in zip(target_chars, target_chars_2):
                            c1.set_color(highlight_color)
                            c2.set_color(highlight_color)
                            opacity_strength = 1

                    
                    animations.append(LaggedStart(
                              *[    
                                    c.animate
                                    .set_opacity(opacity_strength)
                                    .shift(UP * sf) for c in target_chars
                            ],

                            lag_ratio=0.2,
                            run_time=max(run_time-(fade_time/(len(ts_item['words']))), 0.001),
                            #rate_func=linear
                        ))
                    
                    if i != len(ts_item["words"])-1:
                        next_start = ts_item["words"][i+1]['start']
                        animations.append(Wait(max(0.001, next_start-item['end'])))

                    
                    start_idx += len(word)

                self.play( SmoothedWrite(text_tb_written.shift(UP * sf), run_time=max(ts_item["end"]-ts_item["start"]-fade_time, 0.001)), Succession(*animations), )
                

                if j != len(ts)-1:
                    self.wait(max(ts[j+1]['start']-ts[j]['end'], 0.001))

                self.play(
                    FadeOut(text_0), FadeOut(text_tb_written), run_time=fade_time
                )



            self.wait(1)
                
