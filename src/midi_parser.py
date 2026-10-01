import pretty_midi
from bisect import bisect_right


def load_midi(file_path: str) -> pretty_midi.PrettyMIDI:
    """Load input MIDI file."""
    return pretty_midi.PrettyMIDI(file_path)


def extract_notes(midi: pretty_midi.PrettyMIDI):
    """
    Extract notes as dic from all non-drum instruments.

    Returns:
        list of dictionaries:
        {
            "pitch": 60,
            "name": "C4",
            "start": 0.0,
            "end": 0.5,
            "duration": 0.5,
            "velocity": 90
        }
    """
    notes = []

    for instrument in midi.instruments:

        if instrument.is_drum:
            continue

        for note in instrument.notes:
            notes.append({
                "pitch": note.pitch,
                "name": pretty_midi.note_number_to_name(note.pitch),
                "start": note.start,
                "end": note.end,
                "duration": note.end - note.start,
                "velocity": note.velocity,
            })

    # Sort by start time.
    # If two notes start together, sort lower pitch first.
    notes.sort(
        key=lambda n: (
            n["start"],
            n["pitch"]
        )
    )

    return notes


def get_tempo(midi):
    """Read from MIDI or estimate BPM."""
    _, tempi = midi.get_tempo_changes()

    if len(tempi) > 0:
        return tempi[0], "metadata"

    estimated_tempo = midi.estimate_tempo()

    return estimated_tempo, "estimated"


# 2/4, 3/4, 4/4, 6.8
def get_time_signature(midi: pretty_midi.PrettyMIDI):
    """
    Return the first time signature.

    For ordering notes.
    """
    changes = midi.time_signature_changes

    if not changes:
        return 4, 4

    ts = changes[0] # for now just take the first meter.

    return ts.numerator, ts.denominator


def add_tick_info(
    midi: pretty_midi.PrettyMIDI,
    notes
):
    """
    Add MIDI tick information to every note.

    Keeps the original note data unchanged
    and returns copied note dictionaries.
    """

    notes_with_ticks = []

    for note in notes:

        note_copy = note.copy()

        start_tick = int(
            midi.time_to_tick(
                note["start"]
            )
        )

        end_tick = int(
            midi.time_to_tick(
                note["end"]
            )
        )

        note_copy["start_tick"] = start_tick
        note_copy["end_tick"] = end_tick
        note_copy["duration_ticks"] = (
            end_tick - start_tick
        )

        notes_with_ticks.append(
            note_copy
        )

    return notes_with_ticks



def create_bars(
    midi: pretty_midi.PrettyMIDI
):
    """
    Create bar containers from MIDI downbeats.
    """

    downbeats = midi.get_downbeats()

    if len(downbeats) == 0:
        downbeats = [0.0]

    downbeat_ticks = [
        int(
            midi.time_to_tick(time)
        )
        for time in downbeats
    ]

    midi_end_tick = int(
        midi.time_to_tick(
            midi.get_end_time()
        )
    )

    bars = []

    for i, start_tick in enumerate(
        downbeat_ticks
    ):

        if i + 1 < len(downbeat_ticks):
            end_tick = downbeat_ticks[i + 1]
        else:
            end_tick = midi_end_tick

        bars.append({
            "bar_number": i + 1,
            "start_tick": start_tick,
            "end_tick": end_tick,
            "notes": [],
        })

    return bars

# for now only notes in bar 4/4
def assign_notes_to_bars(notes, bars):
    """
    Assign each note to the bar in which the note onset occurs.

    Notes sustaining from a previous bar are not duplicated into the next bar.
    跨小节的音不会被重复记录。
    """
    bar_start_ticks = [
        bar["start_tick"]
        for bar in bars
    ]

    for note in notes:

        # get the index of the bar that contains the note's start tick
        bar_index = (
            bisect_right(
                bar_start_ticks,
                note["start_tick"]
            )
            - 1
        )

        if 0 <= bar_index < len(bars):

            bars[bar_index]["notes"].append(
                note
            )

    # Sort notes inside each bar:
    # first by onset, then low pitch -> high pitch.
    for bar in bars:

        bar["notes"].sort(
            key=lambda n: (
                n["start_tick"],
                n["pitch"]
            )
        )

    return bars

def add_beat_positions(midi: pretty_midi.PrettyMIDI, bars: list):
    """
    Add musical timing information.

    Current MVP:
    quarter note = one beat.
    """

    ticks_per_beat = midi.resolution

    for bar in bars:

        bar_start_tick = bar["start_tick"]

        for note in bar["notes"]:

            relative_ticks = (
                note["start_tick"]
                - bar_start_tick
            )

            note["beat"] = (
                relative_ticks
                / ticks_per_beat
            ) + 1

            note["duration_beats"] = (
                note["duration_ticks"]
                / ticks_per_beat
            )

    return bars


# def group_notes_by_onset(notes, tolerance=0.01):
#     """
#     Group notes that start at approximately the same time.

#     tolerance:
#         Maximum difference in seconds for notes
#         to be considered simultaneous.
#     """

#     if not notes:
#         return []

#     notes = sorted(
#         notes,
#         key=lambda n: n["start"]
#     )

#     groups = []
#     current_group = [notes[0]]
#     current_time = notes[0]["start"]

#     for note in notes[1:]:

#         if abs(note["start"] - current_time) <= tolerance:
#             current_group.append(note)

#         else:
#             groups.append(current_group)

#             current_group = [note]
#             current_time = note["start"]

#     groups.append(current_group)

#     return groups