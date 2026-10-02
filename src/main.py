import sys

from midi_parser import (
    create_bars,
    load_midi,
    extract_notes,
    add_tick_info,
    assign_notes_to_bars,
    add_beat_positions,
)

from feature_extractor import (
    extract_bar_features,
)

from chord_candidates import (
    generate_candidates,
)
from analysis_pipeline import (
    analyze_metadata,
    # analyze_bars,
    create_harmonic_windows,
    ensure_output_dir,
    save_metadata,
    save_window_features,
    save_candidates,
    save_bar_features,
)


def main(file_path):

    midi = load_midi(file_path)

    # generate song-level metadata
    metadata = analyze_metadata(
        midi,
        file_path,
    )

    # Notes with tick information
    notes = extract_notes(midi)
    notes = add_tick_info(midi, notes)
    metadata["note_count"] = len(notes)

    # bars with notes and beat positions
    bars = create_bars(midi)
    bars = assign_notes_to_bars(notes, bars)
    bars = add_beat_positions(midi, bars)
    metadata["bar_count"] = len(bars)


    # bar-level analysis data
    bar_features = [
        extract_bar_features(
            bar,
            metadata["tonic_pc"],
            metadata["mode"],
        )
        for bar in bars
    ]
    windows = create_harmonic_windows(bar_features, beats_per_bar=metadata["numerator"], window_size=2.0)
    metadata["window_count"] = len(windows)

    # chord-level data
    candidates = generate_candidates(
        metadata["tonic_pc"],
        metadata["mode"],
    )

    scores = []

    analysis = {
        "metadata": metadata,
        "bars": bar_features,
        "windows": windows,
        "candidates": candidates,
        "scores": scores,
    }

    # output json and csv files
    output_dir = ensure_output_dir(file_path)
    save_metadata(metadata, output_dir)
    save_window_features(windows, output_dir)
    save_candidates(candidates, output_dir)
    save_bar_features(bar_features, output_dir)


    print("\n=== ANALYSIS SUMMARY ===")

    print(
        f"File: "
        f"{metadata['file']}"
    )

    print(
        f"Tempo: "
        f"{metadata['tempo']:.2f} BPM"
    )

    print(
        f"Time signature: "
        f"{metadata['time_signature']}"
    )

    print(
        f"Key: "
        f"{metadata['key']}"
    )

    print(
        f"Notes: "
        f"{metadata['note_count']}"
    )

    print(
        f"Bars: "
        f"{metadata['bar_count']}"
    )

    print(
        f"Harmonic windows: "
        f"{metadata['window_count']}"
    )


if __name__ == "__main__":

    if len(sys.argv) != 2:

        print(
            "Usage: "
            "python main.py <midi_file>"
        )

        sys.exit(1)

    main(sys.argv[1])