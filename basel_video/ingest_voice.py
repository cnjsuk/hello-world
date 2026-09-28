"""Bring narration recorded on another machine (local_tts/make_narration.py,
Microsoft neural voices) into the build: convert each clip to 24 kHz mono
WAV in build/audio, trim silence, and write build/durations.json. When the
clips come with word timestamps, subtitle cues are placed on them instead of
being spread by character count.

Usage: python3 ingest_voice.py [voice_dir]   (default: voice_ms)
Then: python3 build.py
"""
import json
import os
import re
import subprocess
import sys

import numpy as np
import soundfile as sf

from script import SCENES

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, sys.argv[1] if len(sys.argv) > 1 else "voice_ms")
OUT = os.path.join(HERE, "build", "audio")
SR = 24000
MS_TEXT_FIXES = {"圣彼德堡": "圣彼得堡"}  # keep in sync with local_tts/make_narration.py


def decode(path):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR),
                                   "-f", "f32le", "-"])
    return np.frombuffer(raw, dtype=np.float32).copy()


def trim_bounds(x, thresh=0.008, pad=0.06):
    idx = np.where(np.abs(x) > thresh)[0]
    if len(idx) == 0:
        return 0, len(x)
    return max(0, idx[0] - int(pad * SR)), min(len(x), idx[-1] + int(pad * SR))


def chunk_times(chunks, text, words, lead):
    """Start time of each subtitle chunk, from the word timestamps."""
    if not words:
        return None
    marks, pos = [], 0
    for w in words:
        t = w["text"].strip()
        if not t:
            continue
        i = text.find(t, pos)
        if i < 0:
            continue
        marks.append((i, w["start"] - lead))
        pos = i + len(t)
    if not marks:
        return None
    times, start = [], 0
    for _, spoken in chunks:
        hit = next((tm for i, tm in marks if i >= start), None)
        times.append(max(0.0, hit if hit is not None else times[-1] if times else 0.0))
        start += len(spoken)
    times[0] = 0.0
    return [round(t, 3) for t in times]


def main():
    manifest = json.load(open(os.path.join(SRC, "manifest.json"), encoding="utf-8"))
    lines = manifest["lines"]
    os.makedirs(OUT, exist_ok=True)
    durations, missing, aligned = {}, [], 0
    for key, scene_lines in SCENES:
        durations[key] = []
        for i, line in enumerate(scene_lines):
            name = f"{key}_{i}"
            if name not in lines:
                missing.append(name)
                continue
            entry = lines[name]
            x = decode(os.path.join(SRC, entry["file"]))
            a, b = trim_bounds(x)
            y = x[a:b].copy()
            f = int(0.01 * SR)
            y[:f] *= np.linspace(0, 1, f)
            y[-f:] *= np.linspace(1, 0, f)
            path = os.path.join(OUT, name + ".wav")
            sf.write(path, y, SR, subtype="PCM_16")
            spoken = [(c, s) for c, s in line]
            text = "".join(s for _, s in spoken)
            for p, q in MS_TEXT_FIXES.items():
                text = text.replace(p, q)
            ct = chunk_times(spoken, text, entry.get("words", []), a / SR)
            item = {"wav": os.path.relpath(path, HERE), "dur": round(len(y) / SR, 3),
                    "chunks": [[c, len(s)] for c, s in spoken]}
            if ct and all(t2 >= t1 for t1, t2 in zip(ct, ct[1:])) and ct[-1] < item["dur"]:
                item["chunk_times"] = ct
                aligned += 1
            durations[key].append(item)
    if missing:
        raise SystemExit(f"{len(missing)} lines are missing from {SRC}: {' '.join(missing[:12])}")
    with open(os.path.join(HERE, "build", "durations.json"), "w", encoding="utf-8") as fh:
        json.dump(durations, fh, ensure_ascii=False, indent=1)
    total = sum(it["dur"] for v in durations.values() for it in v)
    n = sum(len(v) for v in durations.values())
    print(f"voice: {manifest.get('settings')}")
    print(f"{n} clips, {total:.1f}s of speech, {aligned} with word-level subtitle timing")


if __name__ == "__main__":
    main()
