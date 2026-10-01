import sys

from midi_parser import (
    create_bars,
    load_midi,
    extract_notes,
    get_tempo,
    get_time_signature,
    add_tick_info,
    assign_notes_to_bars,
    add_beat_positions,
    # group_notes_by_onset,
)

from key_detector import (
    detect_key,
    tonic_name_to_pitch_class,
)

from feature_extractor import (
    extract_bar_features,
)


def main(file_path):

    # 1. Load .mid
    midi = load_midi(file_path)
    print("\n=== MIDI INFORMATION ===")

    # 2. Tempo
    tempo, tempo_source = get_tempo(midi)
    print(f"Tempo: {tempo:.2f} BPM")
    print(f"Tempo source: {tempo_source}")

    # 3. Time signature
    numerator, denominator = get_time_signature(midi)
    print(f"Time signature: {numerator}/{denominator}")


    # 4. Notes with tick information
    notes = extract_notes(midi)
    print(f"Number of notes: {len(notes)}")

    notes = add_tick_info(midi, notes)

    # 5. Key
    key_result = detect_key(file_path)
    
    tonic_pc = tonic_name_to_pitch_class(
        key_result["tonic"]
    )

    mode = key_result["mode"]

    print("\n=== KEY ANALYSIS ===")
    print(f"Estimated key: {key_result['key']}")
    print(
        f"Correlation: "
        f"{key_result['correlation']:.3f}"
    )

    # 6. create bars
    bars = create_bars(midi)

    # 7. assign notes
    bars = assign_notes_to_bars(
        notes,
        bars,
    )

    # 8. add beat positions
    bars = add_beat_positions(midi, bars)

    # extract all features for each bar
    print("\n=== BAR ANALYSIS ===")

    for bar in bars:

        features = extract_bar_features(
            bar,
            tonic_pc,
            mode,
        )

        print(f"\nBar {bar['bar_number']}")

        for note in features["notes"]:
            print(
                f"  {note['pitch_class_name']}"
                f" | degree={note['scale_degree']}"
                f" | beat={note['metric_position']}"
                f" | duration={note['duration']:.2f}"
                f" | strong={note['strong_beat']}"
            )

        print(
            "Pitch histogram:",
            features["pitch_histogram"]
        )

        print(
            "Note count:",
            features["note_count"]
        )

        print(
            "Note density:",
            f"{features['note_density']:.2f}",
            "notes/beat"
        )

        print(
            "Pitch range:",
            features["pitch_range"],
            "semitones"
        )


if __name__ == "__main__":

    if len(sys.argv) != 2:

        print(
            "Usage: "
            "python main.py <midi_file>"
        )

        sys.exit(1)

    main(sys.argv[1])