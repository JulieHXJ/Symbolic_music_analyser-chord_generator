from music21 import converter

def tonic_name_to_pitch_class(name):
    mapping = {
        "C": 0,
        "C#": 1,
        "D-": 1,
        "D": 2,
        "D#": 3,
        "E-": 3,
        "E": 4,
        "F": 5,
        "F#": 6,
        "G-": 6,
        "G": 7,
        "G#": 8,
        "A-": 8,
        "A": 9,
        "A#": 10,
        "B-": 10,
        "B": 11,
    }

    return mapping[name]

def detect_key(file_path: str):
    """
    Estimate the key of a MIDI file.

    Returns:
        {
            "tonic": "C",
            "mode": "major",
            "key": "C major",
            "correlation": ...
        }
    """

    score = converter.parse(file_path)

    key = score.analyze("key") # key estimation

    return {
        "tonic": key.tonic.name,
        "mode": key.mode,
        "key": f"{key.tonic.name} {key.mode}",
        "correlation": key.correlationCoefficient,
    }