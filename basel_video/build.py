"""Render every scene at 1080p60, then assemble the final video:
concatenate scenes, burn in Chinese subtitles, mix in the ambient pad and
normalise loudness.

Usage:
  python3 build.py                 # render all scenes + assemble
  python3 build.py --only S03Numeric,S07WhyPi
  python3 build.py --skip-render   # just re-assemble
Prerequisite: python3 tts.py (writes build/audio and build/durations.json).
"""
import argparse
import concurrent.futures as cf
import json
import os
import subprocess
import sys

import numpy as np
import soundfile as sf

from script import SCENES

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, "build")
MEDIA = os.path.join(BUILD, "media")
OUT_DIR = os.path.join(HERE, "output")
SCENE_CLASSES = ["S01Intro", "S02History", "S03Numeric", "S04Poly", "S05Sine",
                 "S06Compare", "S07Radian", "S08Squared", "S09Light", "S10InvPyth",
                 "S11Lake", "S12Doubling", "S13Meaning", "S14ComputePi", "S15Rigor",
                 "S16Legacy", "S17Outro"]
KEYS = [k for k, _ in SCENES]
FONT = "Noto Sans CJK SC"


def scene_file(cls):
    return os.path.join(MEDIA, cls, "videos", "scenes", "1080p60", f"{cls}.mp4")


def render(cls):
    log = os.path.join(BUILD, f"render_{cls}.log")
    # separate media dirs: parallel renders sharing one Tex cache corrupt each other
    with open(log, "w") as fh:
        r = subprocess.run(["manim", "-qh", "--disable_caching", "--media_dir", os.path.join(MEDIA, cls),
                            "scenes.py", cls], cwd=HERE, stdout=fh, stderr=subprocess.STDOUT)
    return cls, r.returncode, log


def probe_duration(path):
    out = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                   "-of", "csv=p=0", path])
    return float(out)


def ass_time(t):
    t = max(0.0, t)
    h = int(t // 3600)
    m = int(t % 3600 // 60)
    s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def srt_time(t):
    t = max(0.0, t)
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def build_subtitles(offsets):
    durations = json.load(open(os.path.join(BUILD, "durations.json"), encoding="utf-8"))
    events = []
    for key, off in zip(KEYS, offsets):
        cues = json.load(open(os.path.join(BUILD, "cues", f"{key}.json")))["cues"]
        for cue in cues:
            line = durations[key][cue["line"]]
            start = off + cue["start"]
            if "chunk_times" in line:  # word timestamps from the TTS service
                bounds = start + np.array(line["chunk_times"] + [line["dur"]])
            else:  # otherwise spread the line by character count
                weights = np.array([n for _, n in line["chunks"]], dtype=float)
                bounds = start + line["dur"] * np.concatenate([[0], np.cumsum(weights) / weights.sum()])
            for (caption, _), a, b in zip(line["chunks"], bounds[:-1], bounds[1:]):
                events.append([a, b, caption])
    events.sort()
    # keep each caption a little past its speech, but never overlapping the next
    for i, ev in enumerate(events):
        nxt = events[i + 1][0] if i + 1 < len(events) else ev[1] + 1.0
        ev[1] = min(max(ev[1] + 0.2, ev[0] + 0.8), nxt - 0.02)

    ass = [
        "[Script Info]", "ScriptType: v4.00+", "PlayResX: 1920", "PlayResY: 1080",
        "WrapStyle: 2", "ScaledBorderAndShadow: yes", "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, "
        "Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, "
        "Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        f"Style: Default,{FONT},50,&H00FFFFFF,&H00FFFFFF,&H00101010,&H90000000,0,0,0,0,100,100,1,0,1,"
        "3,1.2,2,60,60,42,1", "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    srt = []
    for i, (a, b, text) in enumerate(events, 1):
        ass.append(f"Dialogue: 0,{ass_time(a)},{ass_time(b)},Default,,0,0,0,,{text}")
        srt += [str(i), f"{srt_time(a)} --> {srt_time(b)}", text, ""]
    with open(os.path.join(BUILD, "subs.ass"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(ass) + "\n")
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "basel_problem.zh.srt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(srt))
    return len(events)


def music_gain(total):
    """Gain that puts the pad about 24 dB under the average narration level."""
    speech = []
    for f in sorted(os.listdir(os.path.join(BUILD, "audio"))):
        x, _ = sf.read(os.path.join(BUILD, "audio", f), dtype="float32")
        speech.append(x[np.abs(x) > 0.02])
    v_rms = np.sqrt(np.mean(np.concatenate(speech) ** 2))
    m, _ = sf.read(os.path.join(BUILD, "music.wav"), dtype="float32")
    m_rms = np.sqrt(np.mean(m[:, 0] ** 2))
    return v_rms / m_rms * 10 ** (-24 / 20)


def assemble():
    files = [scene_file(c) for c in SCENE_CLASSES]
    durs = [probe_duration(f) for f in files]
    offsets = list(np.cumsum([0] + durs[:-1]))
    total = sum(durs)
    n = build_subtitles(offsets)
    print(f"scenes: {[round(d, 2) for d in durs]}  total {total:.2f}s  subtitles {n}")

    subprocess.check_call([sys.executable, "music.py", f"{total + 1:.2f}",
                           os.path.join(BUILD, "music.wav")], cwd=HERE)
    gain = music_gain(total)

    inputs = []
    for f in files:
        inputs += ["-i", f]
    inputs += ["-i", os.path.join(BUILD, "music.wav")]
    k = len(files)
    parts = [f"[{i}:a]aresample=48000,aformat=channel_layouts=stereo[a{i}];" for i in range(k)]
    cat = "".join(f"[{i}:v][a{i}]" for i in range(k)) + f"concat=n={k}:v=1:a=1[vc][ac];"
    subs = os.path.join(BUILD, "subs.ass").replace(":", r"\:")
    graph = ("".join(parts) + cat +
             f"[vc]ass='{subs}'[v];"
             f"[{k}:a]volume={gain:.4f}[m];"
             f"[ac][m]amix=inputs=2:normalize=0:duration=first,"
             f"loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000[a]")
    out = os.path.join(OUT_DIR, "basel_problem_1080p60.mp4")
    cmd = (["ffmpeg", "-y", "-loglevel", "error", "-stats"] + inputs +
           ["-filter_complex", graph, "-map", "[v]", "-map", "[a]",
            "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-pix_fmt", "yuv420p",
            "-r", "60", "-g", "120", "-profile:v", "high",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
            "-movflags", "+faststart", out])
    subprocess.check_call(cmd, cwd=HERE)
    print("wrote", out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--skip-render", action="store_true")
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--no-assemble", action="store_true")
    args = ap.parse_args()
    todo = [] if args.skip_render else (args.only.split(",") if args.only else SCENE_CLASSES)
    if todo:
        with cf.ThreadPoolExecutor(args.jobs) as ex:
            for cls, code, log in ex.map(render, todo):
                print(f"{cls}: {'ok' if code == 0 else 'FAILED, see ' + log}", flush=True)
                if code:
                    sys.exit(1)
    if not args.no_assemble:
        assemble()


if __name__ == "__main__":
    main()
