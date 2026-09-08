import argparse
import json
from pathlib import Path
from copy import deepcopy
from app import driver


DEFAULT_CONFIG = {
    "spotify_url": None,
    "render_quality": "h",
    "default_project_directory": "projects",

    "no_video": False,
    "no_thumbnail": False,
    "no_description": False,

    "video": {
        "lrc_path": None,
        "sound_path": None,
        "bg_path": None,
        "custom_font_path": "custom_fonts/Stardom-Regular.ttf",
        "fade_time": 0.25,
        "font_size": 1.5,
        "slice_lyrics": -1,
        "bg_opacity": 0.70,
        "t_opacity": (0.80, 0.35),
        "enable_no_fill": False,
        "enable_transliteration": False,
        "transliteration_language": "English",
        "reduction_factor": 3,
    },

    "thumbnail": {
        "img_path": None,
        "title_name": None,
        "artist_name": None,
        "font_size": 1.5,
        "opacity": 1,
        "custom_font_path": "custom_fonts/Stardom-Regular.ttf",
    },
}


def generate_config(path="config.json"):
    path = Path(path)

    if path.exists():
        print(f"Config already exists: {path}")
        return

    with path.open("w", encoding="utf-8") as f:
        json.dump(DEFAULT_CONFIG, f, indent=4)

    print(f"Default config created: {path}")


def load_config(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    except FileNotFoundError:
        raise SystemExit(f"Error: Config file not found: {path}")

    except json.JSONDecodeError as e:
        raise SystemExit(f"Error: Invalid JSON config: {e}")


def parse_args():
    parser = argparse.ArgumentParser(
        prog="cutie",
        description="Generate lyric videos."
    )

    # Spotify URL is positional
    parser.add_argument(
        "spotify_url",
        nargs="?",
        help="Spotify track URL to turn into lyric-video."
    )

    # General
    parser.add_argument(
        "--render-quality",
        choices=["l", "h", "k"],
        default=None,
        help="Manim render quality: l (low), h (high, default), or k (4K)."
    )

    parser.add_argument(
        "--default-project-directory",
        default=None,
        help="Directory in which per-track project folders are created (default: projects)."
    )

    parser.add_argument(
        "--config",
        help="Use only the specified JSON configuration file; ignores other CLI options."
    )

    parser.add_argument(
        "--generate-config",
        action="store_true",
        help="Create a default config.json in the current directory and exit."
    )

    # Output options
    output = parser.add_argument_group("output options")

    output.add_argument(
        "--no-video",
        action="store_true",
        default=None,
        help="Do not generate the lyric video"
    )

    output.add_argument(
        "--no-thumbnail",
        action="store_true",
        default=None,
        help="Do not generate the thumbnail"
    )

    output.add_argument(
        "--no-description",
        action="store_true",
        default=None,
        help="Do not generate the description"
    )

    # Video
    video = parser.add_argument_group("video options")

    video.add_argument(
        "--lrc-path",
        help="Path to a synchronized LRC lyrics file to use instead of downloaded lyrics."
    )
    video.add_argument(
        "--sound-path",
        help="Path to an audio file to use instead of downloading the Spotify track."
    )
    video.add_argument(
        "--bg-path",
        help="Path to the image used as the lyric video's background."
    )

    video.add_argument(
        "--custom-font-path",
        dest="custom_font_path",
        help="Path to the font file used for lyric text."
    )

    video.add_argument(
        "--fade-time",
        type=float,
        help="Base duration, in seconds, for lyric-line transitions (default: 0.25)."
    )
    video.add_argument(
        "--font-size",
        type=float,
        help="Multiplier for the lyric text size (default: 1.5)."
    )
    video.add_argument(
        "--slice-lyrics",
        type=int,
        help="Render only the first N lyric lines; use -1 to render all lines (default)."
    )
    video.add_argument(
        "--bg-opacity",
        type=float,
        help="Background image opacity from 0 (transparent) to 1 (opaque) (default: 0.7)."
    )

    video.add_argument(
        "--t-opacity",
        nargs=2,
        type=float,
        metavar=("ACTIVE", "INACTIVE"),
        help="Text opacity for the active and inactive lyric layers (default: 0.8 0.35)."
    )

    video.add_argument(
        "--enable-no-fill",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Use outlined, unfilled text for the inactive lyric layer."
    )

    video.add_argument(
        "--enable-transliteration",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Transliterate lyrics with Gemini; requires GEMINI_API_KEY."
    )

    video.add_argument(
        "--transliteration-language",
        help="Language or script for Gemini transliteration (default: English)."
    )
    video.add_argument(
        "--reduction-factor",
        type=int,
        help="Multiplier that controls lyric transition timing (default: 3)."
    )

    # Thumbnail
    thumbnail = parser.add_argument_group("thumbnail options")

    thumbnail.add_argument(
        "--img-path",
        help="Path to the image used as the thumbnail background."
    )
    thumbnail.add_argument(
        "--title-name",
        help="Override the title displayed on the thumbnail."
    )
    thumbnail.add_argument(
        "--artist-name",
        help="Override the artist name displayed on the thumbnail."
    )

    thumbnail.add_argument(
        "--thumbnail-font-size",
        type=int,
        help="Multiplier for thumbnail title text size (default: 1.5)."
    )

    thumbnail.add_argument(
        "--thumbnail-opacity",
        type=float,
        help="Thumbnail text opacity from 0 (transparent) to 1 (opaque) (default: 1)."
    )

    thumbnail.add_argument(
        "--thumbnail-custom-font-path",
        help="Path to the font file used for the thumbnail title."
    )

    return parser.parse_args()


def resolve_config():
    args = parse_args()

    # Generate default config
    if args.generate_config:
        generate_config()
        return None

    # Config mode
    # JSON is the ONLY configuration source.
    if args.config:
        return load_config(args.config)

    # Normal CLI mode
    if not args.spotify_url:
        raise SystemExit(
            "Error: Spotify URL is required.\n"
            "Usage: cutie <spotify_url>"
        )

    config = deepcopy(DEFAULT_CONFIG)

    # General
    config["spotify_url"] = args.spotify_url

    if args.render_quality is not None:
        config["render_quality"] = args.render_quality

    if args.default_project_directory is not None:
        config["default_project_directory"] = (
            args.default_project_directory
        )

    # Output
    output_mapping = {
        "no_video": args.no_video,
        "no_thumbnail": args.no_thumbnail,
        "no_description": args.no_description,
    }

    for key, value in output_mapping.items():
        if value is not None:
            config[key] = value

    # Video
    video_mapping = {
        "lrc_path": args.lrc_path,
        "sound_path": args.sound_path,
        "bg_path": args.bg_path,
        "custom_font_path": args.custom_font_path,
        "fade_time": args.fade_time,
        "font_size": args.font_size,
        "slice_lyrics": args.slice_lyrics,
        "bg_opacity": args.bg_opacity,
        "t_opacity": args.t_opacity,
        "enable_no_fill": args.enable_no_fill,
        "enable_transliteration": args.enable_transliteration,
        "transliteration_language": args.transliteration_language,
        "reduction_factor": args.reduction_factor,
    }

    for key, value in video_mapping.items():
        if value is not None:
            config["video"][key] = value

    # Thumbnail
    thumbnail_mapping = {
        "img_path": args.img_path,
        "title_name": args.title_name,
        "artist_name": args.artist_name,
        "font_size": args.thumbnail_font_size,
        "opacity": args.thumbnail_opacity,
        "custom_font_path": args.thumbnail_custom_font_path,
    }

    for key, value in thumbnail_mapping.items():
        if value is not None:
            config["thumbnail"][key] = value

    return config


def main():
    config = resolve_config()

    if config is None:
        return

    print(json.dumps(config, indent=4))

    driver(config)


if __name__ == "__main__":
    main()
