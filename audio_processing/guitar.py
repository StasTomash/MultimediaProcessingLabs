import numpy as np

NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
OCTAVES = ["sub-contra", "contra", "great", "small", "1-line", "2-line", "3-line", "4-line", "5-line"]

STRUM_UP = 0
STRUM_DOWN = 1

CHORD_ARTICULATIONS = {
    "C": [0, 1, 0, 2, 3, 0],
    "Cm": [3, 4, 5, 5, 3, None],
    "C#": [4, 6, 6, 6, 4, None],
    "C#m": [4, 5, 6, 6, 4, None],
    "D": [2, 3, 2, 0, None, None],
    "Dm": [1, 3, 2, 0, None, None],
    "D#": [5, 7, 7, 7, 5, None],
    "D#m": [5, 6, 7, 7, 5, None],
    "E": [0, 0, 1, 2, 2, 0],
    "Em": [0, 0, 0, 2, 2, 0],
    "F": [1, 1, 2, 3, 3, 1],
    "Fm": [1, 1, 1, 3, 3, 1],
    "F#": [2, 2, 3, 4, 4, 2],
    "F#m": [2, 2, 2, 4, 4, 2],
    "G": [3, 0, 0, 0, 2, 3],
    "Gm": [3, 3, 3, 5, 5, 3],
    "G#": [4, 4, 5, 6, 6, 4],
    "G#m": [4, 4, 4, 6, 6, 4],
    "A": [0, 2, 2, 2, 0, None],
    "Am": [0, 1, 2, 2, 0, None],
    "A#": [1, 3, 3, 3, 1, None],
    "A#m": [1, 2, 3, 3, 1, None],
    "B": [2, 4, 4, 4, 2, None],
    "Bm": [2, 3, 4, 4, 2, None]
}

def get_note_number(note):
    note_name, octave = note

    if not isinstance(octave, int):
        octave_num = OCTAVES.index(octave)
    else:
        octave_num = octave
    note_num = NOTES.index(note_name)
    return octave_num * 12 + note_num - 8

def _get_next_note(note):
    note_name, octave = note
    if not isinstance(octave, int):
        octave_num = OCTAVES.index(octave)
    else:
        octave_num = octave
    note_num = NOTES.index(note_name)
    next_note_num = note_num + 1
    if next_note_num < len(NOTES):
        return (NOTES[next_note_num], octave)
    else:
        return (NOTES[0], OCTAVES[octave_num + 1])

def get_next_note(note, num):
    for i in range(num):
        note = _get_next_note(note)
    return note

def get_pitch(note):
    return 2 ** ((get_note_number(note) - 49) / 12) * 440

class GuitarString:
    def __init__(self, tuning_note, sample_rate, stretch_factor):
        self.base_note = tuning_note
        self.pitch = get_pitch(tuning_note)
        self.sample_rate = sample_rate
        self.base_stretch_factor = stretch_factor
        self.stretch_factor = stretch_factor
        self.init_wavetable()
        self.current_sample = 0
        self.previous_value = 0

        self.string_length = 63
        self.fret_increment = 0.947
        self.first_fret_length = 3.5
        
    def init_wavetable(self):
        wavetable_size = self.sample_rate // int(self.pitch)
        self.wavetable = (2 * np.random.randint(0, 2, wavetable_size) - 1).astype(np.float)  # type: ignore
        
    def __call__(self, fret):
        note = get_next_note(self.base_note, fret)
        self.pitch = get_pitch(note)
        fret_len = sum(self.first_fret_length * (self.fret_increment ** i) for i in range(fret))
        self.stretch_factor = self.base_stretch_factor * (self.string_length) / (self.string_length - fret_len)
        return self
    
    def __iter__(self):
        self.init_wavetable()
        self.current_sample = 0
        self.previous_value = 0
        return self
    
    def __next__(self):
        current_sample_mod = self.current_sample % self.wavetable.size
        r = np.random.binomial(1, 1 - 1 / self.stretch_factor)
        if r == 0:
            self.wavetable[current_sample_mod] =  0.5 * (self.wavetable[current_sample_mod] + self.previous_value)
        sample = self.wavetable[current_sample_mod]
        self.previous_value = sample
        self.current_sample += 1
        return sample

class Guitar:
    def __init__(self, sample_rate = 44100):
        string_tunings = [("E", "1-line"), ("B", "1-line"), ("G", "small"), ("D", "small"), ("A", "great"), ("E", "great")]
        stretch_factors = [4, 3.75, 3.5, 2.5, 2.25, 2]

        self.sample_rate = sample_rate
        self.strings = [GuitarString(string_tunings[i], sample_rate, stretch_factors[i]) for i in range(6)]

    def pinch_string(self, string_num, fret, duration, power = 1.0):
        string_iterator = iter(self.strings[string_num](fret))
        duration_samples = round(duration * self.sample_rate)
        res = []
        for i in range(duration_samples):
            res.append(next(string_iterator))
        res /= np.max(np.abs(res), axis=0)
        res *= power
        return np.array(res)

    def pinch_chord(self, articulation, duration, power=1.0):
        duration_samples = round(duration * self.sample_rate)
        res = np.zeros(duration_samples)
        for i in range(6):
            if articulation[i] is not None:
                res += self.pinch_string(i, articulation[i], duration, power)
        return res
    
    def strum_chord(self, articulation, duration, power=1.0, strumming_interval=0.005, power_decay=0.95, strum_direction=STRUM_UP):
        if isinstance(articulation, str):
            articulation = CHORD_ARTICULATIONS[articulation]
        duration_samples = round(duration * self.sample_rate)
        res = np.zeros(duration_samples)
        if strum_direction == STRUM_UP:
            strum_order = [0, 1, 2, 3, 4, 5]
        else:
            strum_order = [5, 4, 3, 2, 1, 0]
        delay = 0
        cur_power = power
        for i in strum_order:
            if articulation[i] is not None:
                delay_samples = round(delay * self.sample_rate)
                res += np.append(np.zeros(delay_samples), self.pinch_string(i, articulation[i], duration, cur_power))[:duration_samples]
                delay += strumming_interval
                cur_power *= power_decay
        return res

    def pinch_rythmic_pattern(self, articulation, durations):
        res = np.array([])
        for duration in durations:
            res = np.append(res, self.pinch_chord(articulation, duration))
        return res

    def strum_rythmic_pattern(self, articulations, durations=None, tempo=1.0, directions=None, powers=None):
        res = np.array([])
        if durations is None:
            durations = [1.0] * len(articulations)
        if directions is None:
            directions = [STRUM_DOWN] * len(articulations)
        if powers is None:
            powers = [1.0] * len(articulations)
        for articulation, duration, direction, power in zip(articulations, durations, directions, powers):
            res = np.append(res, self.strum_chord(articulation, duration * tempo, strum_direction=direction, power=power))
        return res