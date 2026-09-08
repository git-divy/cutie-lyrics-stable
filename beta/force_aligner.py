from utils import get_segments
from timestamp_parser import parse_lrc
import whisperx
import json
from pathlib import Path


def get_word_level_stamps(
    audio_file_path,
    lrc_file_path=None,
    save=True,
    save_path="",
    language_code=None,
):
    device = "cpu"
    batch_size = 16
    compute_type = "int8"

    audio = whisperx.load_audio(audio_file_path)

    # Load Whisper model
    model = whisperx.load_model(
        "small",
        device,
        compute_type=compute_type,
        language=language_code,  # None = auto detect
    )

    # Transcribe
    transcription = model.transcribe(audio, batch_size=batch_size)

    if language_code is None:
        language_code = transcription["language"]

    # Decide which segments to align
    if lrc_file_path is not None:
        print("Using LRC for alignment...")
        segments = get_segments(parse_lrc(lrc_file_path))
    else:
        print("Using Whisper transcription...")
        segments = transcription["segments"]

    # Load alignment model
    model_a, metadata = whisperx.load_align_model(
        language_code=language_code,
        device=device,
    )

    # Word-level alignment
    result_align = whisperx.align(
        segments,
        model_a,
        metadata,
        audio,
        device,
    )

    result = {
        "language": language_code,
        "transcription": transcription,
        "alignment": result_align,
    }

    if save:
        save_path = Path(save_path)
        save_path.mkdir(parents=True, exist_ok=True)

        output_file = save_path / f"{Path(audio_file_path).stem}.json"

        with output_file.open("w", encoding="utf-8") as f:
            json.dump(result, f, indent=4, ensure_ascii=False)

        print(f"Saved: {output_file.resolve()}")

    return result

print(get_word_level_stamps(r'assets\audio\videoplayback.weba', None, language_code='hi'))