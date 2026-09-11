# This is used for extracting audio features which can be further used to improve the animationa

import librosa
import numpy as np
import matplotlib.pyplot as plt
import numpy as np

def extract_audio_features(path: str, fps: int = 60, n_mels: int = 64, smooth: int = 5):
    """
    Extracts normalized, frame-aligned audio features for visualization.

    Returns:
        dict with:
            frames: total frames
            duration: seconds
            rms: (frames,)
            onset: (frames,)
            beats: (frames,) binary array
            mel: (n_mels, frames)
            centroid: (frames,)
            waveform: (frames,)
    """

    y, sr = librosa.load(path, sr=None)
    duration = librosa.get_duration(y=y, sr=sr)

    rms = librosa.feature.rms(y=y)[0]
    onset = librosa.onset.onset_strength(y=y, sr=sr)
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)

    mel = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=n_mels)
    mel = np.log1p(mel)  # perceptual scaling

    centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]

    def normalize(x):
        x = x - np.min(x)
        max_val = np.max(x)
        return x / max_val if max_val > 0 else x

    rms = normalize(rms)
    onset = normalize(onset)
    centroid = normalize(centroid)

    mel = mel / np.max(mel) if np.max(mel) > 0 else mel

    def smooth_signal(x, k):
        if k <= 1:
            return x
        return np.convolve(x, np.ones(k) / k, mode="same")

    rms = smooth_signal(rms, smooth)
    onset = smooth_signal(onset, smooth)
    centroid = smooth_signal(centroid, smooth)

    total_frames = int(duration * fps)

    def to_frames(x):
        return np.interp(np.linspace(0, len(x) - 1, total_frames), np.arange(len(x)), x)

    rms_f = to_frames(rms)
    onset_f = to_frames(onset)
    centroid_f = to_frames(centroid)

    mel_f = np.array([to_frames(row) for row in mel])

    waveform = to_frames(y)

    beat_times = librosa.frames_to_time(beat_frames, sr=sr)
    beat_frame_idx = (beat_times * fps).astype(int)

    beats = np.zeros(total_frames)
    beats[np.clip(beat_frame_idx, 0, total_frames - 1)] = 1

    return {
        "frames": total_frames,
        "duration": duration,
        "fps": fps,
        "rms": rms_f,
        "onset": onset_f,
        "beats": beats,
        "mel": mel_f,
        "centroid": centroid_f,
        "waveform": waveform,
    }


def plot_audio_features(features):
    frames = features["frames"]
    duration = features["duration"]
    fps = features["fps"]

    # Time axis
    t = np.linspace(0, duration, frames)

    rms = features["rms"]
    onset = features["onset"]
    beats = features["beats"]
    centroid = features["centroid"]
    waveform = features["waveform"]
    mel = features["mel"]

    fig, axes = plt.subplots(6, 1, figsize=(14, 12), sharex=True)

    # 1. Waveform
    axes[0].plot(t, waveform)
    axes[0].set_title("Waveform (Raw Audio Shape)")
    axes[0].set_ylabel("Amplitude")

    # 2. RMS (Loudness)
    axes[1].plot(t, rms)
    axes[1].set_title("RMS (Loudness / Energy)")
    axes[1].set_ylabel("Intensity")

    # 3. Onset Strength (transients)
    axes[2].plot(t, onset)
    axes[2].set_title("Onset Strength (Energy Changes)")
    axes[2].set_ylabel("Onset")

    # 4. Beats (binary spikes)
    axes[3].plot(t, beats)
    axes[3].set_title("Beats (Detected Rhythm)")
    axes[3].set_ylabel("Beat")

    # 5. Spectral Centroid (brightness)
    axes[4].plot(t, centroid)
    axes[4].set_title("Spectral Centroid (Brightness / Pitch Feel)")
    axes[4].set_ylabel("Centroid")

    # 6. Mel Spectrogram
    axes[5].imshow(
        mel, aspect="auto", origin="lower", extent=[0, duration, 0, mel.shape[0]]
    )
    axes[5].set_title("Mel Spectrogram (Frequency Energy)")
    axes[5].set_ylabel("Mel Bands")
    axes[5].set_xlabel("Time (seconds)")

    plt.tight_layout()
    plt.show()


from manim import *
import numpy as np

SONG_PATH = r"assets\audio\videoplayback.weba"


class AudioVisualizer(Scene):
    def construct(self):
        features = extract_audio_features(SONG_PATH)

        fps = features["fps"]
        total_frames = features["frames"]
        duration = features["duration"]

        self.add_sound(SONG_PATH)

        frame_tracker = ValueTracker(0)

        axes = Axes(
            x_range=[0, 2, 0.5],
            y_range=[0, 1, 0.2],
            x_length=13,
            y_length=7,
            axis_config={
                "include_numbers": False,
                "stroke_width": 2,
            },
        )

        axes.set_opacity(0)
        axes.scale(0.5)

        axes.center()

        title = Text("RMS").scale(0.8)
        title.to_edge(UP)

        self.add(axes, title)

        window = int(fps * 2)

        buffer_rms = [0] * window

        graphs = VMobject()

        def update_graph(mob):
            frame = int(frame_tracker.get_value())

            if frame >= total_frames:
                return mob

            buffer_rms.pop(0)
            buffer_rms.append(features["rms"][frame])

            x = np.linspace(0, 2, len(buffer_rms))

            graph = axes.plot_line_graph(
                x_values=x,
                y_values=buffer_rms,
                add_vertex_dots=False,
                line_color=BLUE,
            )

            graph.set_stroke(width=5)

            mob.become(graph)
            return mob

        graphs.add_updater(update_graph)

        self.add(graphs)

        self.play(
            frame_tracker.animate.set_value(total_frames),
            run_time=duration,
            rate_func=linear,
        )

        graphs.clear_updaters()
