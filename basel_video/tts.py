"""Generate the Chinese narration with an offline TTS model (sherpa-onnx +
Kokoro v1.1-zh), then transcribe every clip back with SenseVoice ASR as a
pronunciation check.

Usage: MODEL_DIR=/path/to/models python3 tts.py
Writes build/audio/<scene>_<i>.wav and build/durations.json.
"""
import json
import os
import re
import sys

import numpy as np
import scipy.signal as ss
import sherpa_onnx
import soundfile as sf

from script import SCENES, spoken_text

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.environ.get("MODEL_DIR", "/tmp/claude-0/tts")
OUT = os.path.join(HERE, "build", "audio")
SPEAKER = int(os.environ.get("SPEAKER", "90"))  # Chinese male voice
SPEED = float(os.environ.get("SPEED", "1.1"))
TAKES = int(os.environ.get("TAKES", "4"))

os.makedirs(OUT, exist_ok=True)

kd = os.path.join(MODEL_DIR, "kokoro-multi-lang-v1_1")

# The stock lexicon reads 倒数 as dào shǔ ("count down"); the math term
# "reciprocal" is dào shù. Write a patched copy with the fixed readings.
LEXICON_FIXES = {
    "倒数": "倒数 ㄉ ㄠ 4 ㄕ ㄨ 4",
    "小数点": "小数点 ㄒ 要 3 ㄕ ㄨ 4 ㄉ 言 3",
}
# Words missing from the stock lexicon whose per-character reading is wrong
# (塞 defaults to sāi; the city is Bāsài'ěr).
LEXICON_ADDITIONS = [
    "巴塞尔 ㄅ ㄚ 1 ㄙ ㄞ 4 ㄦ 3",
]
patched_lex = os.path.join(HERE, "build", "lexicon-zh-patched.txt")
os.makedirs(os.path.dirname(patched_lex), exist_ok=True)
with open(f"{kd}/lexicon-zh.txt", encoding="utf-8") as fin, \
        open(patched_lex, "w", encoding="utf-8") as fout:
    for row in fin:
        word = row.split(" ", 1)[0]
        fout.write(LEXICON_FIXES[word] + "\n" if word in LEXICON_FIXES else row)
    fout.write("\n".join(LEXICON_ADDITIONS) + "\n")

tts = sherpa_onnx.OfflineTts(sherpa_onnx.OfflineTtsConfig(
    model=sherpa_onnx.OfflineTtsModelConfig(
        kokoro=sherpa_onnx.OfflineTtsKokoroModelConfig(
            model=f"{kd}/model.onnx", voices=f"{kd}/voices.bin",
            tokens=f"{kd}/tokens.txt", data_dir=f"{kd}/espeak-ng-data",
            dict_dir=f"{kd}/dict",
            lexicon=f"{kd}/lexicon-us-en.txt,{patched_lex}"),
        num_threads=4),
    rule_fsts=f"{kd}/date-zh.fst,{kd}/phone-zh.fst,{kd}/number-zh.fst",
    max_num_sentences=1))

sd = os.path.join(MODEL_DIR, "sherpa-onnx-sense-voice-zh-en-ja-ko-yue-int8-2024-07-17")
asr = sherpa_onnx.OfflineRecognizer.from_sense_voice(
    model=f"{sd}/model.int8.onnx", tokens=f"{sd}/tokens.txt",
    language="zh", use_itn=False, num_threads=4)


def norm(s):
    return re.sub(r"[^一-鿿0-9a-zA-Z]", "", s).lower()


def cer(ref, hyp):
    a, b = norm(ref), norm(hyp)
    d = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        p = d[:]
        d[0] = i
        for j, cb in enumerate(b, 1):
            d[j] = min(p[j] + 1, d[j - 1] + 1, p[j - 1] + (ca != cb))
    return d[-1] / max(1, len(a))


def trim(x, sr, thresh=0.01, pad=0.05):
    idx = np.where(np.abs(x) > thresh)[0]
    if len(idx) == 0:
        return x
    s = max(0, idx[0] - int(pad * sr))
    e = min(len(x), idx[-1] + int(pad * sr))
    return x[s:e]


durations = {}
report = []
for key, lines in SCENES:
    durations[key] = []
    for i, line in enumerate(lines):
        text = spoken_text(line)
        # Synthesis is not deterministic, so make a few takes and keep the
        # one the ASR model transcribes most accurately.
        best = None
        for take in range(TAKES):
            audio = tts.generate(text, sid=SPEAKER, speed=SPEED)
            sr = audio.sample_rate
            cand = trim(np.asarray(audio.samples, dtype=np.float32), sr)
            st = asr.create_stream()
            st.accept_waveform(16000, ss.resample_poly(cand, 2, 3))
            asr.decode_stream(st)
            score = cer(text, st.result.text)
            if best is None or score < best[0]:
                best = (score, cand, st.result.text)
            if score == 0:
                break
        e, x, hyp = best
        # short fades so clips never click
        f = int(0.01 * sr)
        x[:f] *= np.linspace(0, 1, f)
        x[-f:] *= np.linspace(1, 0, f)
        path = os.path.join(OUT, f"{key}_{i}.wav")
        sf.write(path, x, sr, subtype="PCM_16")
        dur = len(x) / sr
        durations[key].append({"wav": os.path.relpath(path, HERE), "dur": round(dur, 3),
                               "chunks": [[c, len(s)] for c, s in line]})
        report.append((key, i, dur, e, text, hyp))
        print(f"{key}_{i}: {dur:5.2f}s CER={e:.3f}\n  ref: {text}\n  asr: {hyp}", flush=True)

with open(os.path.join(HERE, "build", "durations.json"), "w") as fh:
    json.dump(durations, fh, ensure_ascii=False, indent=1)

total = sum(r[2] for r in report)
print(f"\nTotal speech: {total:.1f}s  mean CER: {np.mean([r[3] for r in report]):.3f}")
worst = sorted(report, key=lambda r: -r[3])[:8]
print("Worst lines:")
for r in worst:
    print(f"  {r[0]}_{r[1]} CER={r[3]:.3f} asr={r[5]}")
