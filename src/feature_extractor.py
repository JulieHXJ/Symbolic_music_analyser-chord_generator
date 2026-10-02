from collections import defaultdict

from theory_definitions import (
    pitch_to_pitch_class,
    pitch_class_name,
    MAJOR_SCALE,
    NATURAL_MINOR_SCALE,
)



def get_scale_degree(
    pitch_class,
    tonic_pitch_class,
    mode
):
    """
    Return diatonic scale degree 1-7. 返回调内音级

    MVP: Non-diatonic notes return None. 暂时不考虑调外音
    """

    if mode == "major":
        scale = MAJOR_SCALE
    elif mode == "minor":
        scale = NATURAL_MINOR_SCALE
    else:
        return None

    relative_pc = (
        pitch_class - tonic_pitch_class
    ) % 12

    if relative_pc not in scale:
        return None

    return scale.index(relative_pc) + 1



# metric position + strong beat 
def quantize_beat(beat, grid=0.5):
    """
    Quantize beat to nearest rhythmic grid. 量化-八分音符

    grid=0.5 -> eighth-note grid.
    """

    return (round((beat - 1) / grid) * grid + 1)

def is_strong_beat(beat):
    """
    4/4 MVP: 判断强弱拍

    Beat 1 = strongest
    Beat 3 = secondary strong beat.
    """

    quantized = quantize_beat(beat)

    return quantized in (1.0, 3.0)



# long note / short note weight
def build_pitch_histogram(notes):
    """
    Duration-weighted pitch-class histogram. 长强短弱

    Example:
        E lasting 2 beats contributes 2.0
        B lasting 0.5 beat contributes 0.5
    """

    histogram = defaultdict(float)

    for note in notes:
        pc = pitch_to_pitch_class(note["pitch"])
        histogram[pc] += note["duration_beats"]

    return dict(histogram)

def histogram_to_names(histogram):
    """
    Convert numeric pitch-class histogram to note-name histogram.

    Example:
        {"E": 3.0, "B": 1.0}
    """

    named_histogram = {}

    for pitch_class, value in histogram.items():

        name = pitch_class_name(pitch_class)

        named_histogram[name] = round(
            value,
            2
        )

    return named_histogram



def calculate_note_density(notes, beats_per_bar=4):
    """
    Calculate note activity inside a bar.

    Returns:
        note_count:
            total number of note-on events

        note_density:
            note-on events per beat
    """

    note_count = len(notes)

    if beats_per_bar == 0:
        return note_count, 0.0

    note_density = (
        note_count / beats_per_bar
    )

    return note_count, note_density

def calculate_pitch_range(notes):
    """
    Calculate the pitch range in semitones.
    音域跨度
    """

    if not notes:
        return 0

    pitches = [
        note["pitch"]
        for note in notes
    ]

    return max(pitches) - min(pitches)


def extract_bar_features(bar, tonic_pitch_class, mode):
    """
    Extract MIR features from one bar.
    """

    notes = bar["notes"]

    if not notes:
        return {
            "bar_number": bar["bar_number"],
            "notes": [],
            "pitch_histogram": {},
            "pitch_histogram_names": {},
            "strong_beat_notes": [],
            "note_count": 0,
            "note_density": 0.0,
            "pitch_range": 0,
        }

    note_features = []
    strong_beat_notes = []

    for note in notes:

        pc = pitch_to_pitch_class(note["pitch"])
        quantized_beat = quantize_beat(note["beat"])

        degree = get_scale_degree(pc, tonic_pitch_class, mode)

        strong = is_strong_beat(note["beat"])

        feature = {
            "pitch": note["pitch"],
            "pitch_class": pc,
            "pitch_class_name": pitch_class_name(pc),
            "duration": note["duration_beats"],
            "metric_position": quantized_beat,
            "scale_degree": degree,
            "strong_beat": strong,
        }

        note_features.append(feature)
        if strong:
            strong_beat_notes.append(feature)

    histogram = build_pitch_histogram(notes)
    named_histogram = histogram_to_names(histogram)

    note_count, note_density = (
        calculate_note_density(
            notes,
            beats_per_bar=4
        )
    )

    return {
        "bar_number": bar["bar_number"],
        "notes": note_features,
        # "pitch_histogram": histogram,
        "pitch_histogram": named_histogram,
        "strong_beat_notes": strong_beat_notes,
        "note_count": note_count,
        "note_density": note_density,
        "pitch_range": calculate_pitch_range(notes),
    }
