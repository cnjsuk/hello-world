"""Synthesize a quiet ambient pad to sit under the narration.

Usage: python3 music.py <seconds> <out.wav>
"""
import sys

import numpy as np
import soundfile as sf
from scipy.signal import lfilter

SR = 48000


def note(name):
    names = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
    semis = names[name[0]] + 12 * (int(name[-1]) + 1) - 69
    return 440.0 * 2 ** (semis / 12)


# I - vi - IV - V flavoured progression, 8 s per chord
CHORDS = [
    ["C3", "G3", "B3", "E4", "G4"],
    ["A2", "E3", "G3", "C4", "E4"],
    ["F2", "C3", "E3", "A3", "C4"],
    ["G2", "D3", "G3", "B3", "D4"],
]
CHORD_LEN = 8.0


def pad(total):
    n = int(total * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    rng = np.random.default_rng(7)
    k = 0
    start = 0.0
    while start < total:
        chord = CHORDS[k % len(CHORDS)]
        seg_len = CHORD_LEN + 3.0  # overlap for a smooth crossfade
        s = int(start * SR)
        e = min(n, int((start + seg_len) * SR))
        tt = t[s:e] - start
        env = np.minimum(1, tt / 2.5) * np.minimum(1, np.clip((seg_len - tt) / 3.0, 0, 1))
        env = env ** 1.5
        for nm in chord:
            f = note(nm)
            ph = rng.uniform(0, 2 * np.pi, 3)
            v = (np.sin(2 * np.pi * f * tt + ph[0])
                 + 0.5 * np.sin(2 * np.pi * f * 1.003 * tt + ph[1])   # gentle chorus
                 + 0.18 * np.sin(2 * np.pi * 2 * f * tt + ph[2]))     # soft octave
            trem = 1 + 0.08 * np.sin(2 * np.pi * 0.2 * tt + ph[0])
            out[s:e] += v * env * trem / len(chord)
        start += CHORD_LEN
        k += 1
    # one-pole low-pass for warmth
    a = np.exp(-2 * np.pi * 1800 / SR)
    y = lfilter([1 - a], [1, -a], out)
    fade = int(3 * SR)
    y[:fade] *= np.linspace(0, 1, fade)
    y[-fade:] *= np.linspace(1, 0, fade)
    y /= np.max(np.abs(y)) + 1e-9
    return (y * 0.9).astype(np.float32)


if __name__ == "__main__":
    total = float(sys.argv[1])
    sig = pad(total)
    sf.write(sys.argv[2], np.stack([sig, sig], axis=1), SR, subtype="PCM_16")
