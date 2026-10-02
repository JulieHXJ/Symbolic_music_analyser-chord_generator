
PITCH_CLASS_NAMES = [
    "C", "C#", "D", "D#", "E", "F",
    "F#", "G", "G#", "A", "A#", "B"
]

# Semitone distances from tonic
MAJOR_SCALE = [0, 2, 4, 5, 7, 9, 11]
NATURAL_MINOR_SCALE = [0, 2, 3, 5, 7, 8, 10]

# 定义和弦音级关系
CHORD_TYPES = {
    # Triads 三和弦
    "major": {
        "intervals": [0, 4, 7],
        "suffix": "",
    },

    "minor": {
        "intervals": [0, 3, 7],
        "suffix": "m",
    },

    "diminished": {
        "intervals": [0, 3, 6],
        "suffix": "dim",
    },

    "augmented": {
        "intervals": [0, 4, 8],
        "suffix": "aug",
    },


    # Seventh chords 七和弦
    "maj7": {
        "intervals": [0, 4, 7, 11],
        "suffix": "maj7",
    },

    "min7": {
        "intervals": [0, 3, 7, 10],
        "suffix": "m7",
    },

    "dom7": {
        "intervals": [0, 4, 7, 10],
        "suffix": "7",
    },

    "half_dim7": {
        "intervals": [0, 3, 6, 10],
        "suffix": "m7b5",
    },

    "dim7": {
        "intervals": [0, 3, 6, 9],
        "suffix": "dim7",
    },


    # Suspended 挂留和弦
    "sus2": {
        "intervals": [0, 2, 7],
        "suffix": "sus2",
    },

    "sus4": {
        "intervals": [0, 5, 7],
        "suffix": "sus4",
    },


    # Added-tone chords
    "add9": {
        "intervals": [0, 4, 7, 14],
        "suffix": "add9",
    },

    "6": {
        "intervals": [0, 4, 7, 9],
        "suffix": "6",
    },

    "m6": {
        "intervals": [0, 3, 7, 9],
        "suffix": "m6",
    },

    "6_9": {
        "intervals": [0, 4, 7, 9, 14],
        "suffix": "6/9",
    },


    # Ninth chords
    "maj9": {
        "intervals": [0, 4, 7, 11, 14],
        "suffix": "maj9",
    },

    "min9": {
        "intervals": [0, 3, 7, 10, 14],
        "suffix": "m9",
    },

    "dom9": {
        "intervals": [0, 4, 7, 10, 14],
        "suffix": "9",
    },
}

# 定义调内和弦
SCALE_HARMONY = {

    "major": {
        "scale": MAJOR_SCALE,

        "triads": [
            "major",
            "minor",
            "minor",
            "major",
            "major",
            "minor",
            "diminished",
        ],

        "sevenths": [
            "maj7",
            "min7",
            "min7",
            "maj7",
            "dom7",
            "min7",
            "half_dim7",
        ],

        "triad_roman": [
            "I",
            "ii",
            "iii",
            "IV",
            "V",
            "vi",
            "vii°",
        ],

        "seventh_roman": [
            "Imaj7",
            "ii7",
            "iii7",
            "IVmaj7",
            "V7",
            "vi7",
            "viiø7",
        ],
    },


    "minor": {
        "scale": NATURAL_MINOR_SCALE,

        "triads": [
            "minor",
            "diminished",
            "major",
            "minor",
            "minor",
            "major",
            "major",
        ],

        "sevenths": [
            "min7",
            "half_dim7",
            "maj7",
            "min7",
            "min7",
            "maj7",
            "dom7",
        ],

        "triad_roman": [
            "i",
            "ii°",
            "III",
            "iv",
            "v",
            "VI",
            "VII",
        ],

        "seventh_roman": [
            "i7",
            "iiø7",
            "IIImaj7",
            "iv7",
            "v7",
            "VImaj7",
            "VII7",
        ],
    },
}

# 扩展调性和弦
TRIAD_EXTENSIONS = {
    "major": [
        "sus2",
        "sus4",
        "add9",
        "6",
        "6_9",
    ],

    "minor": [
        "sus2",
        "sus4",
        "m6",
    ],

    "diminished": [],
}

SEVENTH_EXTENSIONS = {
    "maj7": [
        "maj9",
    ],

    "min7": [
        "min9",
    ],

    "dom7": [
        "dom9",
    ],
}


BORROWED_CHORDS_MAJOR = [
    {
        "interval": 3,
        "quality": "major",
        "function": "bIII",
    },

    {
        "interval": 5,
        "quality": "minor",
        "function": "iv",
    },

    {
        "interval": 8,
        "quality": "major",
        "function": "bVI",
    },

    {
        "interval": 10,
        "quality": "major",
        "function": "bVII",
    },
]

SECONDARY_TARGET_NAMES = {
    2: "ii",
    3: "iii",
    4: "IV",
    5: "V",
    6: "vi",
}

def pitch_class_name(pc):
    return PITCH_CLASS_NAMES[pc % 12]


def pitch_to_pitch_class(pitch):
    return pitch % 12

def get_scale_info(mode):

    if mode not in SCALE_HARMONY:
        raise ValueError(
            f"Unsupported mode: {mode}"
        )

    return SCALE_HARMONY[mode]