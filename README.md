# Cutie Lyrics

Create lyric-video assets from a Spotify track URL.

Cutie Lyrics downloads or reuses audio and synchronized lyrics, then renders an animated lyric video, a thumbnail, and a text description with [Manim](https://www.manim.community/). Each run is isolated in a project directory named after the Spotify track ID.

> This is a source-based CLI. Run it from the project root so that the Manim scene files and bundled fonts are available.

## What it creates

For a Spotify track URL, Cutie Lyrics can create:

- A WAV audio download via `spotdl`
- Synced LRC lyrics from `spotdl` and a Spotify lyrics service
- An animated lyric video
- A PNG thumbnail with the track title and artists
- A `description.txt` file containing the title, artists, and lyrics

It also supports custom backgrounds, custom fonts, lyric styling, partial renders, and optional Gemini-powered transliteration.

## Requirements

- Python 3.10 or newer
- [FFmpeg](https://ffmpeg.org/) available on your `PATH`
- A Spotify **track** URL
- Internet access for Spotify metadata, lyrics, and downloads

FFmpeg is required by Manim and Pydub. If Manim does not install correctly, follow the [official Manim installation instructions](https://docs.manim.community/en/stable/installation.html) for your operating system.

## Installation

Clone the repository and enter its root directory:

```bash
git clone <repository-url>
cd cutie-lyrics-stable
```

Create a virtual environment:

```powershell
# Windows PowerShell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

```bash
# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

Install the CLI and its core dependencies in editable mode:

```bash
python -m pip install --upgrade pip
python -m pip install -e .
```

Confirm the tools are available:

```bash
cutie --help
spotdl --version
manim --version
```

You can also run the source file directly:

```bash
python cutie.py --help
```

## Quick start

Run the command from the project root with a Spotify track URL:

```bash
cutie "https://open.spotify.com/track/TRACK_ID"
```

The equivalent source command is:

```bash
python cutie.py "https://open.spotify.com/track/TRACK_ID"
```

By default, Cutie Lyrics renders at Manim high quality and writes everything to `projects/<track-id>/`.

## Examples

The [`examples/`](examples/) directory contains completed 4K renders made with Cutie Lyrics.

### Thumbnail examples

#### Standard

<img src="examples/thumbnail/thumbnail_standard%20%281%29.webp" alt="Standard thumbnail 1" width="50%"><img src="examples/thumbnail/thumbnail_standard%20%282%29.webp" alt="Standard thumbnail 2" width="50%"><img src="examples/thumbnail/thumbnail_standard%20%283%29.webp" alt="Standard thumbnail 3" width="50%"><img src="examples/thumbnail/thumbnail_standard%20%284%29.webp" alt="Standard thumbnail 4" width="50%">

#### Playlist
<img src="examples/thumbnail/thumbnail_playlist%20%281%29.webp" alt="Playlist thumbnail 1" width="50%"><img src="examples/thumbnail/thumbnail_playlist%20%282%29.webp" alt="Playlist thumbnail 2" width="50%">

### Video examples

#### Standard

<video src="examples/videos/video_standard%20%281%29.mp4" controls width="50%" style="max-width: 700px;">
  Your browser does not support the video tag.
</video><video src="examples/videos/video_standard%20%282%29.mp4" controls width="50%" style="max-width: 700px;">
  Your browser does not support the video tag.
</video><video src="examples/videos/video_standard%20%283%29.mp4" controls width="50%" style="max-width: 700px;">
  Your browser does not support the video tag.
</video><video src="examples/videos/video_standard%20%284%29.mp4" controls width="50%" style="max-width: 700px;">
  Your browser does not support the video tag.
</video>

#### Playlist

<video src="examples/videos/video_playlist%20%281%29.mp4" controls width="50%" style="max-width: 700px;">
  Your browser does not support the video tag.
</video><video src="examples/videos/video_playlist%20%282%29.mp4" controls width="50%" style="max-width: 700px;">
  Your browser does not support the video tag.
</video>

## Output layout

```text
projects/
└── <spotify-track-id>/
    ├── <spotify-track-id>-YT.wav
    ├── <spotify-track-id>-YT.lrc
    ├── <spotify-track-id>-SP.lrc
    └── output/
        ├── description.txt
        ├── images/
        │   └── thumbnail_dev/
        │       └── Thumbnail_ManimCE_*.png
        └── videos/
            └── lyr_dev/
                └── <resolution>/
                    └── Lyrics.mp4
```

Manim also writes intermediate media, text, and partial-render files below `output/`.

## Common commands

```bash
# Render every asset at the default high quality
cutie "https://open.spotify.com/track/TRACK_ID"

# Render a lyric video only, with a custom background image
cutie "https://open.spotify.com/track/TRACK_ID" \
  --bg-path "assets/background.jpg" \
  --no-thumbnail \
  --no-description

# Use low-quality rendering while refining a design
cutie "https://open.spotify.com/track/TRACK_ID" --render-quality l

# Save a track project under a different directory
cutie "https://open.spotify.com/track/TRACK_ID" \
  --default-project-directory "my-projects"

# Generate a thumbnail and description without rendering a lyric video
cutie "https://open.spotify.com/track/TRACK_ID" --no-video
```

## Command reference

Run `cutie --help` for the same reference in your terminal.

### General options

| Option | Description |
| --- | --- |
| `spotify_url` | Spotify track URL. Required unless using `--config` or `--generate-config`. |
| `--render-quality {l,h,k}` | Manim quality: `l` for low, `h` for high (default), or `k` for 4K. |
| `--default-project-directory PATH` | Directory that receives track-specific project folders. Default: `projects`. |
| `--config PATH` | Use only the specified JSON configuration file; other CLI options are ignored. |
| `--generate-config` | Create a default `config.json` in the current directory and exit. |

### Output options

| Option | Description |
| --- | --- |
| `--no-video` | Skip lyric-video rendering. |
| `--no-thumbnail` | Skip thumbnail generation. |
| `--no-description` | Skip creation of `description.txt`. |

### Lyric-video options

| Option | Description |
| --- | --- |
| `--lrc-path PATH` | LRC file to render instead of the downloaded lyrics. |
| `--sound-path PATH` | Audio file to render instead of downloading the track. |
| `--bg-path PATH` | Image used as the lyric-video background. |
| `--custom-font-path PATH` | Font file used for lyric text. |
| `--fade-time SECONDS` | Base duration of a lyric-line transition. Default: `0.25`. |
| `--font-size NUMBER` | Lyric text-size multiplier. Default: `1.5`. |
| `--slice-lyrics NUMBER` | Render the first *N* lyric lines. Use `-1` to render every line (default). |
| `--bg-opacity NUMBER` | Background-image opacity from `0` to `1`. Default: `0.7`. |
| `--t-opacity ACTIVE INACTIVE` | Opacity for active and inactive lyric text. Default: `0.8 0.35`. |
| `--enable-no-fill` / `--no-enable-no-fill` | Enable or disable outlined inactive lyric text. |
| `--enable-transliteration` / `--no-enable-transliteration` | Enable or disable Gemini-powered transliteration. |
| `--transliteration-language LANGUAGE` | Target language or script for transliteration. Default: `English`. |
| `--reduction-factor NUMBER` | Multiplier used to time lyric transitions. Default: `3`. |

### Thumbnail options

| Option | Description |
| --- | --- |
| `--img-path PATH` | Image used as the thumbnail background. |
| `--title-name TEXT` | Override the track title shown on the thumbnail. |
| `--artist-name TEXT` | Override the artist names shown on the thumbnail. |
| `--thumbnail-font-size NUMBER` | Thumbnail title text-size multiplier. Default: `1.5`. |
| `--thumbnail-opacity NUMBER` | Thumbnail text opacity from `0` to `1`. Default: `1`. |
| `--thumbnail-custom-font-path PATH` | Font file used for the thumbnail title. |

## JSON configuration

Generate the default configuration file:

```bash
cutie --generate-config
```

Edit `config.json`, then run it:

```bash
cutie --config config.json
```

Example:

```json
{
  "spotify_url": "https://open.spotify.com/track/TRACK_ID",
  "render_quality": "h",
  "default_project_directory": "projects",
  "no_video": false,
  "no_thumbnail": false,
  "no_description": false,
  "video": {
    "lrc_path": null,
    "sound_path": null,
    "bg_path": null,
    "custom_font_path": "custom_fonts/Stardom-Regular.ttf",
    "fade_time": 0.25,
    "font_size": 1.5,
    "slice_lyrics": -1,
    "bg_opacity": 0.7,
    "t_opacity": [0.8, 0.35],
    "enable_no_fill": false,
    "enable_transliteration": false,
    "transliteration_language": "English",
    "reduction_factor": 3
  },
  "thumbnail": {
    "img_path": null,
    "title_name": null,
    "artist_name": null,
    "font_size": 1.5,
    "opacity": 1,
    "custom_font_path": "custom_fonts/Stardom-Regular.ttf"
  }
}
```

## Fonts and backgrounds

Bundled font files are in `custom_fonts/`. The default font is `Stardom-Regular.ttf`. Pass a `.ttf` or `.otf` file with `--custom-font-path` or `--thumbnail-custom-font-path` to override it.

`--bg-path` controls the lyric-video background and `--img-path` controls the thumbnail background. If no image is supplied, the respective render uses Manim's default background.

## Custom audio and lyrics

`--sound-path` and `--lrc-path` disable the corresponding download step. The current driver still verifies that audio and LRC files are present in the track project directory before rendering. If you use custom source files, stage compatible files in that project directory or verify the generated project contents before rendering.

## Optional API credentials

Create a `.env` file in the project root only for features that require credentials:

```env
# Required only when --enable-transliteration is used
GEMINI_API_KEY=your_gemini_api_key

# Used by the legacy Spotify metadata helpers and beta tools
CLIENT_ID=your_spotify_client_id
CLIENT_SECRET=your_spotify_client_secret
```

The main single-track workflow uses public Spotify metadata and does not require Spotify client credentials. Never commit `.env`; it is ignored by Git.

## Experimental tools

The scripts in `beta/` are experimental and are not part of the supported CLI workflow. They include prototypes for album/playlist renders, audio visualisation, and WhisperX alignment.

Install their additional dependencies only when you need them:

```bash
python -m pip install -e ".[beta]"
```

Some beta scripts reference local assets or helpers that are not included as part of the stable CLI, so expect to adapt them before use.

## Troubleshooting

| Problem | Check |
| --- | --- |
| `spotdl` or `manim` is not recognized | Activate the virtual environment, reinstall with `python -m pip install -e .`, and confirm FFmpeg is on `PATH`. |
| Manim fails to render | Follow Manim's platform-specific installation guide and run `manim --version`. |
| Lyrics are missing or do not align | The external lyrics source may not have the track; use a synchronized LRC file where possible. |
| Transliterating lyrics fails | Install the core dependencies and set `GEMINI_API_KEY` in `.env`. |
| A custom audio or LRC file is not found | Use an absolute path while troubleshooting, then ensure compatible source files are present in the generated track project. |

## License

This project is licensed under the [MIT License](LICENSE).

## Rights and attribution

You are responsible for ensuring that you have the necessary rights to download, use, and publish music, artwork, lyrics, and any generated media.
