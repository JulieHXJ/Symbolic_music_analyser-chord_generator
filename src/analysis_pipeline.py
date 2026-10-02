from pathlib import Path
import csv
import json

from midi_parser import (
    get_tempo,
    get_time_signature,
)

from key_detector import (
    detect_key,
    tonic_name_to_pitch_class,
)

from feature_extractor import (
    build_window_pitch_histogram,
    calculate_window_note_count,
    calculate_window_note_density,
    calculate_window_pitch_range,
)


def analyze_metadata(
    midi,
    file_path,
):
    """
    Analyze song-level information.
    """

    tempo, tempo_source = get_tempo(midi)
    numerator, denominator = (get_time_signature(midi))

    key_result = detect_key(file_path)

    tonic_pc = (
        tonic_name_to_pitch_class(
            key_result["tonic"]
        )
    )

    return {
        "file": Path(file_path).name,
        "tempo": tempo,
        "tempo_source": tempo_source,
        "time_signature": f"{numerator}/{denominator}",
        "numerator": numerator,
        "denominator": denominator,
        "key": key_result["key"],
        "tonic": key_result["tonic"],
        "tonic_pc": tonic_pc,
        "mode": key_result["mode"],
        "key_correlation": key_result["correlation"],
    }


# def analyze_bars(
#     bars,
#     metadata,
# ):
#     """
#     Extract musical features
#     for every bar.
#     """

#     results = []

#     for bar in bars:

#         features = extract_bar_features(
#             bar,
#             metadata["tonic_pc"],
#             metadata["mode"],
#         )

#         results.append(
#             features
#         )

#     return results

def create_harmonic_windows(
    bar_features,
    beats_per_bar=4,
    window_size=2.0,
):
    """
    Split each bar into fixed harmonic windows.

    Current MVP:
        4/4
        2 beats per harmonic window

    A note is included if it overlaps with the window.
    """

    windows = []

    for bar in bar_features:

        window_start = 1.0
        window_number = 1
        bar_end = (beats_per_bar + 1.0)

        while window_start < bar_end:

            window_end = min(window_start + window_size, bar_end)
            window_notes = []

            for note in bar["notes"]:

                note_start = (note["metric_position"])
                note_end = (note_start + note["duration"])

                overlap_start = max(
                    note_start,
                    window_start,
                )

                overlap_end = min(
                    note_end,
                    window_end,
                )

                overlap_duration = (overlap_end - overlap_start)

                if overlap_duration > 0:
                    note_copy = (note.copy())
                    note_copy["window_duration"] = overlap_duration
                    # note_copy["window_start_beat"] = overlap_start
                    window_notes.append(note_copy)

            # Window-level features
            pitch_histogram = (build_window_pitch_histogram(window_notes))
            note_count = (calculate_window_note_count(window_notes, window_start, window_end))
            note_density = (calculate_window_note_density(note_count, window_start, window_end))
            pitch_range = (calculate_window_pitch_range(window_notes))


            windows.append({
                "bar_number": bar["bar_number"],
                "window_number": window_number,
                "start_beat": window_start,
                "end_beat": window_end,
                "notes": window_notes,
                "pitch_histogram": pitch_histogram,
                "note_count": note_count,
                "note_density":
                    round(
                        note_density,
                        2,
                    ),

                "pitch_range": pitch_range,
            })

            window_start = (window_end)
            window_number += 1

    return windows

def ensure_output_dir(file_path):
    """
    Create processed output directory based on input filename.
    """

    stem = Path(file_path).stem

    output_dir = (Path("data") / "processed"/ stem)

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    return output_dir

def save_metadata(
    metadata,
    output_dir,
):
    """
    Save song-level metadata as JSON.
    """

    output_path = (output_dir / "metadata.json")

    with open(
        output_path,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            metadata,
            f,
            indent=4,
            ensure_ascii=False,
        )

    return output_path

def save_bar_features(
    bar_features,
    output_dir,
):
    """
    Save full bar-level feature analysis.
    """

    output_path = (output_dir / "bars.json"
    )

    with open(
        output_path,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            bar_features,
            f,
            indent=4,
            ensure_ascii=False,
        )

    return output_path


def save_window_features(
    windows,
    output_dir,
):
    """
    Save harmonic-window analysis as JSON.

    Each window contains:
    - bar/window position
    - analyzed notes
    - window-level aggregate features
    """

    output_path = (output_dir / "window_features.json")

    with open(
        output_path,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            windows,
            f,
            indent=4,
            ensure_ascii=False,
        )

    return output_path

def save_candidates(
    candidates,
    output_dir,
):
    """
    Save chord candidate pool as JSON.
    """

    output_path = (output_dir / "candidates.json")

    with open(
        output_path,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            candidates,
            f,
            indent=4,
            ensure_ascii=False,
        )

    return output_path