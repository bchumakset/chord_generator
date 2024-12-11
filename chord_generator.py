import argparse
import numpy as np
import random
import struct
import wave

SAMPLE_RATE = 44100

NOTE_FREQUENCIES = {
    "C": 261.63,
    "C#": 277.18,
    "D": 293.66,
    "D#": 311.13,
    "E": 329.63,
    "F": 349.23,
    "F#": 369.99,
    "G": 392.00,
    "G#": 415.30,
    "A": 440.00,
    "A#": 466.16,
    "B": 493.88,
}

ROOT_NOTE_SEQUENCE = {
    "I": "C",
    "II": "D",
    "III": "E",
    "IV": "F",
    "V": "G",
    "VI": "A",
    "VII": "B",
}

MOOD_PROGRESSIONS = {
    "epic": [
        ["I", "V", "vi", "IV"],
        ["i", "VII", "VI", "VII"],
        ["IV", "V", "iii", "vi"],
        ["i", "iv", "V", "i"],
    ],
    "sad": [
        ["vi", "IV", "I", "V"],
        ["i", "iv", "i", "V"],
        ["ii", "v", "I", "vi"],
        ["i", "VII", "iv", "i"],
    ],
    "cool": [
        ["ii", "V", "I", "vi"],
        ["IV", "I", "ii", "V"],
        ["iii", "vi", "ii", "V"],
        ["I", "VII", "IV", "I"],
    ],
    "happy": [
        ["I", "IV", "V", "IV"],
        ["I", "vi", "IV", "V"],
        ["IV", "I", "V", "I"],
        ["I", "V", "vi", "iii"],
    ],
}


def get_note_by_step(note, steps):
    notes_list = list(NOTE_FREQUENCIES.keys())
    index = notes_list.index(note)
    new_index = (index + steps) % len(notes_list)
    return notes_list[new_index]


def get_chords(progression):
    chords = []
    for chord in progression:
        root_note = ROOT_NOTE_SEQUENCE[chord.upper()]
        second_note_step = 4 if chord.isupper() else 3  # is upper means it's major
        second_note = get_note_by_step(root_note, second_note_step)
        third_note = get_note_by_step(root_note, 7)
        chords.append([root_note, second_note, third_note])
    return chords


def generate_wave(frequency, duration, amplitude, wave_type):
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    if wave_type == "sine":
        form = amplitude * np.sin(2 * np.pi * frequency * t)
    elif wave_type == "saw":
        form = amplitude * (2 * (t * frequency - np.floor(0.5 + t * frequency)))
    elif wave_type == "triangle":
        form = amplitude * (
            2 * np.abs(2 * (t * frequency - np.floor(0.5 + t * frequency))) - 1
        )
    elif wave_type == "square":
        form = amplitude * np.sign(np.sin(2 * np.pi * frequency * t))
    else:
        raise ValueError("Unknown wave type")
    return form


def apply_adsr(wave, attack, decay, sustain, release):
    total_samples = len(wave)
    attack_samples = int(attack * SAMPLE_RATE)
    decay_samples = int(decay * SAMPLE_RATE)
    release_samples = int(release * SAMPLE_RATE)
    sustain_samples = total_samples - (attack_samples + decay_samples + release_samples)

    adsr = np.zeros(total_samples)
    if attack_samples > 0:
        adsr[:attack_samples] = np.linspace(0, 1, attack_samples)
    if decay_samples > 0:
        adsr[attack_samples : attack_samples + decay_samples] = np.linspace(
            1, sustain, decay_samples
        )
    if sustain_samples > 0:
        adsr[
            attack_samples
            + decay_samples : attack_samples
            + decay_samples
            + sustain_samples
        ] = sustain
    if release_samples > 0:
        adsr[-release_samples:] = np.linspace(sustain, 0, release_samples)

    return wave * adsr


def generate_chord(notes, chord_duration, amplitude, wave_type, adsr_params):
    chord = np.zeros(int(SAMPLE_RATE * chord_duration))
    attack, decay, sustain, release = adsr_params
    for frequency in notes:
        raw_wave = generate_wave(frequency, chord_duration, amplitude, wave_type)
        adjusted_wave = apply_adsr(raw_wave, attack, decay, sustain, release)
        chord += adjusted_wave
    return chord / len(notes)


def transpose_progression(key, chords):
    transpose = list(NOTE_FREQUENCIES.keys()).index(key) - list(
        NOTE_FREQUENCIES.keys()
    ).index("C")
    return [
        [
            list(NOTE_FREQUENCIES.keys())[
                (list(NOTE_FREQUENCIES.keys()).index(note) + transpose) % 12
            ]
            for note in chord
        ]
        for chord in chords
    ]


def adjust_chord(frequencies, tone_multiplier):
    root_note = (NOTE_FREQUENCIES[frequencies[0]]) * tone_multiplier
    second_note_frequency = NOTE_FREQUENCIES[frequencies[2]] * tone_multiplier
    second_note = (
        second_note_frequency * 2
        if second_note_frequency < root_note
        else second_note_frequency
    )
    third_note_frequency = NOTE_FREQUENCIES[frequencies[1]] * tone_multiplier * 2
    third_note = (
        third_note_frequency * 2
        if third_note_frequency < second_note
        else third_note_frequency
    )
    return [root_note, second_note, third_note]


def generate_progression(
    bpm,
    mood,
    key,
    tone,
    wave_type,
    adsr_params,
):
    amplitude = 0.3
    duration = 4
    chord_duration = 60 / bpm * duration
    random_progression = random.choice(MOOD_PROGRESSIONS[mood])
    chords = get_chords(random_progression)

    if key != "C":
        chords = transpose_progression(key, chords)

    tone_multiplier = 1.0
    if tone == "high":
        tone_multiplier = 2.0
    elif tone == "low":
        tone_multiplier = 0.5

    audio = []
    for chord in chords:
        adjusted_chord = adjust_chord(chord, tone_multiplier)
        audio.extend(
            generate_chord(
                adjusted_chord, chord_duration, amplitude, wave_type, adsr_params
            )
        )

    audio = np.array(audio)
    return audio


def save_wav(filename, data):
    with wave.open(filename, "w") as wav_file:
        wav_file.setnchannels(1)  # mono
        wav_file.setsampwidth(2)  # 16 bit
        wav_file.setframerate(SAMPLE_RATE)
        wav_file.writeframes(
            struct.pack("<" + ("h" * len(data)), *(np.int16(data * 32767)))
        )


def take_value(arg, values):
    return random.choice(values) if arg is None else arg


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Chord progression generation and recording to a WAV file."
    )
    parser.add_argument("--bpm", type=int, default=120, help="Beats per minute(BPM).")
    parser.add_argument(
        "--mood",
        type=str,
        choices=MOOD_PROGRESSIONS.keys(),
        help="Mood of the progression.",
    )
    parser.add_argument(
        "--key",
        type=str,
        choices=NOTE_FREQUENCIES.keys(),
        help="Scale the of progression.",
    )
    parser.add_argument(
        "--tone",
        type=str,
        choices=["high", "normal", "low"],
        default="normal",
        help="Tone of the progression.",
    )
    parser.add_argument(
        "--wave",
        type=str,
        choices=["sine", "saw", "triangle", "square"],
        help="Wave type.",
    )
    parser.add_argument(
        "--adsr",
        type=float,
        nargs=4,
        default=(0.1, 0.3, 0.75, 0.15),
        help="ADSR Envelope: Attack(A), decay(D), sustain(S), release(R).",
    )
    parser.add_argument("--output", type=str, help="File name.", default="clip.wav")

    args = parser.parse_args()

    audio_data = generate_progression(
        bpm=args.bpm,
        mood=take_value(args.mood, list(MOOD_PROGRESSIONS.keys())),
        key=take_value(args.key, list(NOTE_FREQUENCIES.keys())),
        tone=take_value(args.tone, ["high", "normal", "low"]),
        wave_type=take_value(args.wave, ["sine", "saw", "triangle", "square"]),
        adsr_params=tuple(args.adsr),
    )

    save_wav(args.output, audio_data)
    print(f"{args.output} saved.")
