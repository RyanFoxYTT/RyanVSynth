import soundfile as sf
import pyworld as pw
import numpy as np
from notes import midi_to_hz

phone_dict = {
    "a": "vowel",
    "V": "vowel",
    "Q": "vowel",
    "e": "vowel",
    "3": "vowel",
    "i": "vowel",
    "o": "vowel",
    "u": "vowel",
    "b": "stop",
    "c": "stop",
    "C": "stop",
    "d": "stop",
    "D": "tune",
    "f": "stop",
    "g": "stop",
    "h": "stop",
    "j": "stop",
    "k": "stop",
    "l": "tune",
    "m": "tune",
    "n": "tune",
    "N": "tune",
    "p": "stop",
    "q": "tune",
    "R": "tune",
    "s": "stop",
    "S": "stop",
    "t": "stop",
    "T": "tune",
    "v": "stop",
    "w": "tune",
    "y": "tune",
    "z": "stop",
    "Z": "stop",
}

def shift_sample(input_path, midi_note, phoneme_type, note_duration, vibrato_depth=0.0):
    if phoneme_type in ["vowel", "tune"]:  # if type = vowel or tuned consonant - tune
        data, fs = sf.read(input_path)
        if data.ndim > 1:
            data = data[:, 0]
        
        f0, t = pw.harvest(data, fs)
        sp = pw.cheaptrick(data, f0, t, fs)
        ap = pw.d4c(data, f0, t, fs)
        
        f0_nonzero = f0[f0 > 0]
        base_freq = np.median(f0_nonzero)
        target_freq = midi_to_hz(midi_note)
        shift = target_freq / base_freq

        f0_flat = np.where(f0 > 0, base_freq, 0.0)
        if vibrato_depth > 0:
            time = np.arange(len(f0_flat)) / fs
            vibrato = 1.0 + vibrato_depth * np.sin(2 * np.pi * 5.0 * time)
            f0_flat = f0_flat * vibrato
        f0_shifted = f0_flat * shift
        
        y = pw.synthesize(f0_shifted, sp, ap, fs)

        desired_length = int(note_duration * fs)
        if len(y) > desired_length:
            y = y[:desired_length]

        return y, fs
    else:  # if stop then just.. idk,
        data, fs = sf.read(input_path)
        if data.ndim > 1:
            data = data[:, 0]
        return data, fs