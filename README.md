# Personal Music Analysis Tool

> Rule-based MIDI analysis, harmony inference, and accompaniment generation baseline.

## Project Status

| Phase | Status | Goal |
|---|---|---|
| Phase 1 — MIDI Parsing + Key Detection | ✅ | Convert raw MIDI into structured notes, bars, beats, and key information |
| Phase 2 — Musical Feature Extraction | ✅ | Extract bar-level musical features used by the harmony engine |
| Phase 3 — Rule-Based Harmony Engine | 🔧| Generate chord candidates and score them against melody/context |
| Phase 4 — Context / Progression | Planned | Model chord-to-chord context and decode a coherent progression |
| Phase 5 — Accompaniment Generator | Planned | Render selected harmony as MIDI accompaniment |
| Evaluation | Planned | Evaluate the baseline on example melodies and document failure cases |

---

# 1. Project Goal

The project is a **Personal Music Analysis Tool** that begins with a rule-based MIR baseline and can later evolve toward data-driven and machine-learning approaches.

Target pipeline:

```text
MIDI melody
     ↓
MIDI Parsing
     ↓
Beat / Bar Representation
     ↓
Key Analysis
     ↓
Feature Extraction
     ↓
Chord Candidate Generation
     ↓
Rule-Based Chord Scoring
     ↓
Sequence Decoding
     ↓
Harmony Recommendation
     ↓
Accompaniment MIDI
```


---

# 2. Execute

Save your MIDI file in data/input/

```bash
.venv/bin/python src/main.py data/input/*.mid
```

Current MVP assumptions:

- MIDI input
- primarily 4/4 meter
- constant time signature
- quarter-note-based beat representation
- polyphonic MIDI can be parsed
- automatic voice separation is not yet implemented

---

# Phase 1 — MIDI Parsing + Key Detection

## 1.1 Tools

### `pretty_midi`

```text
pretty_midi
│
├── MIDI I/O
├── pitch
├── note start / end
├── velocity
├── tempo metadata
├── MIDI ticks
├── beat / downbeat information
└── MIDI output
```

### `music21`

```text
music21
│
├── key analysis
├── scale
├── chord
├── Roman numeral analysis
└── music theory utilities
```

---

## 1.2 Parsing Logic

Current preprocessing pipeline:

```text
raw MIDI
      ↓
extract_notes()
      ↓
add_tick_info()
      ↓
create_bars()
      ↓
assign_notes_to_bars()
      ↓
add_beat_positions()
```

---

## 1.3 Note Representation

Structure:
```python
{
    "pitch": 60,
    "name": "C4",
    "start": 0.0,
    "end": 0.5,
    "duration": 0.5,
    "velocity": 90,
    "start_tick": ...,
    "end_tick": ...,
    "duration_ticks": ...,
    "beat": ...,
    "duration_beats": ...
}
```

---

## 1.4 Time Signature

The current implementation reads the first time-signature event.

If no time signature is stored, the MVP currently assumes:

```text
4/4
```

Changing meter not yet supported

---

## 1.5 Initial Bar Segmentation

Early output:

```text
=== BAR ANALYSIS ===

Bar 1
Time: 0.00s - 2.40s
Notes: D#5 E2 E3 B3 E5 E3 B3 F#5 E3

Bar 2
Time: 2.40s - 4.80s
Notes: D#5 E2 E3 B3 E5 E3 B3 F#5 E3

Bar 3
Time: 4.80s - 7.20s
Notes: D#5 G#2 G#3 B3 E5 G#3 B3 F#5 G#3
```

### Limitation

The first implementation grouped notes using floating-point seconds.

This could produce boundary errors such that a note on the next downbeat therefore is assigned to the previous bar.

---

## 1.6 Upgrade — Tick-Based Bar Assignment

Current logic:

```text
MIDI downbeats
      ↓
convert seconds → MIDI ticks
      ↓
integer bar boundaries
      ↓
assign note using start_tick
```

Example:

```text
=== BAR ANALYSIS ===

Bar 8
  Beat 1.0: B2(47) D#5(75) F#5(78)
  Beat 1.5: F#3(54)
  Beat 2.0: B3(59)
  Beat 2.5: E5(76) G#5(80)
  Beat 3.0: F#3(54)
  Beat 3.5: B3(59)
  Beat 4.0: F#5(78) A5(81)
  Beat 4.5: B3(59)
```

Beat positions are more musically meaningful than seconds and are therefore used by later harmony analysis.

---

# Phase 2 — Musical Feature Extraction

For each bar, the analyzer currently extracts eight musical features.

| Feature | Representation | Purpose |
|---|---|---|
| Pitch class | `0–11` | Note identity without octave |
| Scale degree | `1–7` | Position relative to the detected key |
| Metric position | `1.0, 1.5, 2.0...` | Position inside the bar |
| Strong-beat notes | Boolean / beat position | Identify metrically important notes |
| Duration | beats | Longer notes contribute more evidence |
| Pitch histogram | weighted pitch-class values | Measure dominant pitch classes |
| Note density | note onsets per beat | Describe rhythmic / textural activity |
| Pitch range | `max MIDI - min MIDI` | Describe pitch span |

---

## 2.1 Metric Weighting

Planned baseline metric weights:

```text
Beat 1       → 1.50
Beat 3       → 1.25
Beat 2 / 4   → 1.00
Offbeat      → 0.70
```

These are intended as **soft weights**, not strict harmony rules.

---

## 2.2 Duration Weighting

Current duration is stored in beats.

Example:

```text
duration=3.64
```

means that the note lasts approximately:

```text
3.64 beats
```

Future option:

```text
raw_duration + quantized_duration
```

---

## 2.3 Bar Analysis Output

Example:

```text
=== BAR ANALYSIS ===

Bar 1
  E | degree=1 | beat=1.0 | duration=3.64 | strong=True
  D# | degree=7 | beat=1.0 | duration=1.53 | strong=True
  E | degree=1 | beat=1.5 | duration=1.02 | strong=False
  B | degree=5 | beat=2.0 | duration=0.57 | strong=False
  E | degree=1 | beat=2.5 | duration=1.55 | strong=False
  E | degree=1 | beat=3.0 | duration=0.99 | strong=True
  B | degree=5 | beat=3.5 | duration=0.49 | strong=False
  F# | degree=2 | beat=4.0 | duration=1.00 | strong=False
  E | degree=1 | beat=4.5 | duration=0.60 | strong=False

Pitch histogram:
{'E': 7.79, 'D#': 1.53, 'B': 1.06, 'F#': 1.0}

Note count:
9

Note density:
2.25 notes/beat

Pitch range:
38 semitones
```

---

## 2.5 Interpretation

### Per-note information

For every note:

```text
pitch class
+
scale degree
+
metric position
+
duration
+
strong / weak beat
```

---

### Pitch Histogram

The current histogram is duration-weighted.

Example:

```text
E lasts 3.64 beats
E lasts 1.02 beats
E lasts 1.55 beats
...
```

The contributions are accumulated:

```text
Bar 1 pitch importance

E   ████████████████████  7.79
D#  ████                  1.53
B   ███                   1.06
F#  ███                   1.00
```

This suggests that E is the dominant pitch class in the bar.

---

### Note Count / Note Density

```text
Note count: 9 in the bar
Note density: 2.25 notes per beat
```

This describes musical or textural activity.

It is currently a descriptive feature rather than a primary harmony-selection feature.

---

### Pitch Range

highest MIDI pitch - lowest MIDI pitch = 38 semitones

---

# Phase 3 — Rule-Based Harmony Engine

The harmony engine is split into two tasks:

```text
Candidate Generation
=
Which chords should be considered?

Candidate Scoring
=
Which candidate best explains the current musical evidence?
```

---

## 3.1 Candidate Generation

The system is not limited to strict classical four-part harmony.

Instead, the planned harmonic vocabulary combines:

```text
Functional harmony
+
Pop harmony
+
Jazz / extended harmony
+
Modal mixture
+
Borrowed chords
+
Secondary dominants
+
Chromatic mediants
+
Voice-leading / common-tone logic
+
Bass evidence
```

The goal is to represent harmony as a set of **soft preferences**, not rigid legal/illegal rules.

---

## 3.2 Diatonic Harmony

For C major:

```text
I     C E G
ii    D F A
iii   E G B
IV    F A C
V     G B D
vi    A C E
vii°  B D F
```

Diatonic triads and seventh chords automatically enter the candidate pool.


---

## 3.3 Modern Chord Vocabulary

| Chord type | C major example | Notes | Description |
|---|---|---|---|
| Major | C | C E G | I |
| Minor | Dm | D F A | ii |
| Diminished | Bdim | B D F | vii° |
| Augmented | Caug | C E G# | chromatic color |
| Major 7 | Cmaj7 | C E G B | Imaj7 |
| Minor 7 | Dm7 | D F A C | ii7 |
| Dominant 7 | G7 | G B D F | V7 |
| Half-diminished 7 | Bm7♭5 | B D F A | viiø7 |
| Diminished 7 | Bdim7 | B D F Ab | chromatic leading-tone chord |
| Sus2 | Csus2 | C D G | third replaced by second |
| Sus4 | Csus4 | C F G | third replaced by fourth |
| Add9 | Cadd9 | C E G D | triad + 9, no seventh |
| 6 | C6 | C E G A | major triad + 6 |
| m6 | Dm6 | D F A B | minor triad + major 6 |
| 6/9 | C6/9 | C E G A D | 6 + 9 |
| Maj9 | Cmaj9 | C E G B D | maj7 + 9 |
| Min9 | Dm9 | D F A C E | min7 + 9 |
| Dom9 | G9 | G B D F A | dominant7 + 9 |

---

## 3.4 Candidate Scoring

Question:

```text
Which candidate best explains the current melody/window?
```

Example melody window:

```text
C E G A
```

Each candidate receives a score.

Initial conceptual scoring function:

```text
Score(chord)
=
w1 × MelodyFit
+
w2 × StrongBeatFit
+
w3 × KeyFit
+
w4 × Transition
```

Possible local rules:

```text
MelodyFit
chord tone → positive score

StrongBeatFit
strong-beat chord tone → stronger positive score

NonChordTone
unsupported non-chord tone → penalty

Diatonic
diatonic chord → small prior bonus
```

The final score should depend on more than simple pitch matching.

---

## 3.5 Non-Chord Tones and Extensions

A melody note may function as:

```text
Chord tone
Extension
Suspension
Passing tone
Neighbor tone
Anticipation
Non-chord tone
```

---

## 3.6 Complexity / Evidence

A larger chord should not automatically win just because it contains more melody notes.

Future scoring should therefore consider:

```text
observed support
+
missing essential tones
+
complexity penalty
+
extension evidence
```

---

# Phase 4 — Context / Progression

If each bar independently chooses its highest local score, the output may become repetitive or unstable.

A second scoring layer should consider:

```text
previous chord
      ↓
current chord
```
---

## 4.1 Sequence Scoring

Conceptual model:

```text
Score(C_t)
=
LocalScore(C_t, M_t)
+
λ × TransitionScore(C_{t-1}, C_t)
```

where:

```text
C_t
=
current chord candidate

M_t
=
musical evidence in the current window
```

---

## 4.2 Sequence Decoding

Instead of choosing best chord for each bar independently, I use dynamic programming / Viterbi-style decoding.

Example:

```text
Bar1      Bar2      Bar3      Bar4

C         C         F         C
Am        G         Am        G
F         Am        C         Am
│          │         │         │
└──────── transition scores ───┘
```

Goal:

```text
maximum total score path
```

Example result:

```text
C → Am → F → G
```
---

# Phase 5 — Accompaniment Generator

Supported patterns:

## Block Chord

```text
C3 E3 G3
████████
```

## Arpeggio

```text
C3 → E3 → G3 → E3
```

## Bass + Chord

```text
Bass:   C2
Chord:  C3 E3 G3
```

Output will be written using `pretty_midi`.

The result can be imported directly into Logic Pro for listening and evaluation.

---

# Evaluation

The baseline should be evaluated on approximately 20–30 short examples.

Possible result table:

| Melody | Key | Expected Chords | Predicted Chords | Match | Musical Rating |
|---|---|---|---|---:|---:|
| 01 | C | C-G-Am-F | C-G-Am-F | 100% | 5 |
| 02 | G | G-D-Em-C | G-D-C-C | 50% | 3 |

Documentation:

```text
successful cases
+
ambiguous cases
+
failure cases
+
limitations of rule weights
```

Possible failure categories:

```text
non-chord tones confuse local inference
longer harmonic context is ignored
fixed transition rules over-prefer common progressions
multiple harmonizations are musically valid
manual weights do not generalize
voice separation is not implemented
```



# Current Limitations

Current baseline limitations:

```text
4/4-focused beat model
constant time signature
no automatic voice separation
no explicit melody / accompaniment / bass separation
no full sustain-across-bar harmonic model
no quantized duration representation yet
simplified strong / weak beat model
key estimation delegated to music21
candidate scoring not yet implemented
progression context not yet implemented
no accompaniment output yet
```

These limitations are intentional.

The MVP is designed to establish an interpretable baseline first, then measure where rule-based analysis fails.

---

