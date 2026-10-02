from theory_definitions import (
    CHORD_TYPES,
    MAJOR_SCALE,
    TRIAD_EXTENSIONS,
    SEVENTH_EXTENSIONS,
    BORROWED_CHORDS_MAJOR,
    SECONDARY_TARGET_NAMES,
    pitch_class_name,
    get_scale_info,
)

# helper
def build_pitch_classes(
    root_pc,
    quality
):
    """
    Convert root + chord intervals
    into pitch classes.

    Example:

        Cmaj7
        root = 0
        intervals = [0, 4, 7, 11]

        -> [0, 4, 7, 11]
        -> C E G B
    """

    intervals = (
        CHORD_TYPES[quality]["intervals"]
    )

    pitch_classes = [
        (root_pc + interval) % 12
        for interval in intervals
    ]

    # Remove duplicate pitch classes.
    return list(
        dict.fromkeys(pitch_classes)
    )

def remove_duplicate_candidates(
    candidates
):
    """
    Remove candidates with the same
    root and quality.
    """

    unique = {}

    for chord in candidates:

        key = (
            chord["root_pc"],
            chord["quality"],
        )

        if key not in unique:
            unique[key] = chord

    return list(
        unique.values()
    )



def create_candidate(
    root_pc,
    quality,
    function=None,
    source=None,
    degree=None,
):
    """
    Create one chord candidate dictionary.
    """

    root_name = pitch_class_name(
        root_pc
    )

    suffix = (
        CHORD_TYPES[quality]["suffix"]
    )

    return {
        "root_pc": root_pc,
        "root": root_name,

        "quality": quality,

        "symbol": (
            root_name + suffix
        ),

        "pitch_classes":
            build_pitch_classes(
                root_pc,
                quality,
            ),

        "function": function,
        "source": source,
        "degree": degree,
    }


def add_candidate(
    candidates,
    root_pc,
    quality,
    function=None,
    source=None,
    degree=None,
):
    """
    Helper to append one candidate.
    """

    candidates.append(
        create_candidate(
            root_pc=root_pc,
            quality=quality,
            function=function,
            source=source,
            degree=degree,
        )
    )

def generate_diatonic_candidates(
    tonic_pc,
    mode
):
    """
    Generate diatonic triads and seventh chords. 生成调内三和弦和七和弦
    """

    candidates = []
    info = get_scale_info(
        mode
    )
    scale = info["scale"]

    for i, interval in enumerate(
        scale
    ):

        root_pc = (
            tonic_pc + interval
        ) % 12

        degree = i + 1

        # Triad
        add_candidate(
            candidates,
            root_pc=root_pc,
            quality=info["triads"][i],
            function=(
                info["triad_roman"][i]
            ),
            source="diatonic",
            degree=degree,
        )

        # Seventh
        add_candidate(
            candidates,
            root_pc=root_pc,
            quality=info["sevenths"][i],
            function=(
                info["seventh_roman"][i]
            ),
            source="diatonic",
            degree=degree,
        )
    return candidates



def generate_extension_candidates(
    tonic_pc,
    mode
):
    """
    Generate selected modern chord extensions.

    These are not automatically considered
    better than simple triads.

    They only enlarge the candidate pool.
    """
    candidates = []
    info = get_scale_info(
        mode
    )

    for i, interval in enumerate(
        info["scale"]
    ):

        root_pc = (
            tonic_pc + interval
        ) % 12

        degree = i + 1

        triad_quality = (
            info["triads"][i]
        )

        seventh_quality = (
            info["sevenths"][i]
        )


        # Extensions derived from triads / sevenths
        triad_extensions = (
            TRIAD_EXTENSIONS.get(
                triad_quality,
                []
            )
        )

        for quality in triad_extensions:
            add_candidate(
                candidates,
                root_pc=root_pc,
                quality=quality,
                source="extension",
                degree=degree,
            )


        seventh_extensions = (
            SEVENTH_EXTENSIONS.get(
                seventh_quality,
                []
            )
        )

        for quality in seventh_extensions:

            add_candidate(
                candidates,
                root_pc=root_pc,
                quality=quality,
                source="extension",
                degree=degree,
            )

    return candidates


def generate_borrowed_candidates(
    tonic_pc,
    mode
):
    """
    Generate selected modal-mixture chords.

    First MVP:
    only borrowed chords in major keys.
    """

    candidates = []
    if mode != "major":
        return candidates

    for rule in BORROWED_CHORDS_MAJOR:
        root_pc = (
            tonic_pc
            + rule["interval"]
        ) % 12

        add_candidate(
            candidates,
            root_pc=root_pc,
            quality=rule["quality"],
            function=rule["function"],
            source="borrowed",
        )

    return candidates


def generate_secondary_dominants(
    tonic_pc,
    mode
):
    candidates = []

    if mode != "major":
        return candidates

    for degree, target_name in (
        SECONDARY_TARGET_NAMES.items()
    ):

        target_interval = (
            MAJOR_SCALE[
                degree - 1
            ]
        )

        target_root = (
            tonic_pc
            + target_interval
        ) % 12

        # Perfect fifth above target
        dominant_root = (
            target_root + 7
        ) % 12

        add_candidate(
            candidates,
            root_pc=dominant_root,
            quality="dom7",
            function=f"V/{target_name}",
            source="secondary_dominant",
        )

    return candidates

def generate_chromatic_candidates(
    tonic_pc,
    mode
):
    """
    Selected chromatic-color chords.
    """

    candidates = []

    # Iaug / iaug
    add_candidate(
        candidates,
        root_pc=tonic_pc,
        quality="augmented",
        function=(
            "Iaug"
            if mode == "major"
            else "iaug"
        ),
        source="chromatic",
    )

    if mode == "major":

        leading_tone = (
            tonic_pc + 11
        ) % 12

        add_candidate(
            candidates,
            root_pc=leading_tone,
            quality="dim7",
            function="vii°7",
            source="chromatic",
        )
    return candidates

def generate_candidates(
    tonic_pc,
    mode
):
    """
    Generate the complete candidate pool
    for the current key.
    """
    candidates = []
    candidates.extend(
        generate_diatonic_candidates(
            tonic_pc,
            mode,
        )
    )
    candidates.extend(
        generate_extension_candidates(
            tonic_pc,
            mode,
        )
    )
    candidates.extend(
        generate_borrowed_candidates(
            tonic_pc,
            mode,
        )
    )
    candidates.extend(
        generate_secondary_dominants(
            tonic_pc,
            mode,
        )
    )
    candidates.extend(
        generate_chromatic_candidates(
            tonic_pc,
            mode,
        )
    )
    return remove_duplicate_candidates(candidates)