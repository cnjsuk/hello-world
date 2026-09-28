"""Generate the narration with ZipVoice (zero-shot flow-matching TTS, k2-fsa,
run through sherpa-onnx), then pick, for every line, the take that the
SenseVoice ASR transcribes most accurately and the UTMOS predictor rates as
most natural.

The voice prompt (voice/prompt.wav) is fully synthetic: it was produced by
Kokoro v1.1-zh (speaker 90) and then re-voiced once by ZipVoice itself, so no
real person's voice is cloned.

Usage: MODEL_DIR=/path/to/models python3 tts_zipvoice.py [line ...]
Writes build/audio/<scene>_<i>.wav and build/durations.json.
Models (from github.com/k2-fsa/sherpa-onnx/releases):
  tts-models/sherpa-onnx-zipvoice-zh-en-emilia.tar.bz2          (fp32 weights)
  tts-models/sherpa-onnx-zipvoice-distill-int8-zh-en-emilia.tar.bz2 (lexicon/tokens)
  vocoder-models/vocos_24khz.onnx
  asr-models/sherpa-onnx-sense-voice-zh-en-ja-ko-yue-int8-2024-07-17.tar.bz2
UTMOS (optional): github.com/tarepan/SpeechMOS + its v1.0.0 release weights.
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
UTMOS_DIR = os.environ.get("UTMOS_DIR", "/tmp/claude-0/mos")
OUT = os.path.join(HERE, "build", "audio")
TAKES = int(os.environ.get("TAKES", "2"))
MAX_TAKES = int(os.environ.get("MAX_TAKES", "4"))
SPEED = float(os.environ.get("SPEED", "0.9"))
STEPS = int(os.environ.get("STEPS", "16"))
PROMPT_WAV = os.path.join(HERE, "voice", "prompt.wav")
PROMPT_TEXT = open(os.path.join(HERE, "voice", "prompt.txt"), encoding="utf-8").read().strip()

full = os.path.join(MODEL_DIR, "sherpa-onnx-zipvoice-zh-en-emilia")
front = os.path.join(MODEL_DIR, "sherpa-onnx-zipvoice-distill-int8-zh-en-emilia")
os.makedirs(OUT, exist_ok=True)

# Readings the stock pinyin lexicon gets wrong for this script.
LEXICON_FIXES = {
    "倒数": "倒数 d0 ao4 sh0 u4",        # reciprocal: dào shù (not dào shǔ)
    "转动": "转动 zh0 uan4 d0 ong4",     # rotate: zhuàn dòng
}
LEXICON_ADDITIONS = [
    "巴塞尔 b0 a1 s0 ai4 er3",           # Bāsài'ěr (塞 defaults to sāi)
    "大胆地 d0 a4 d0 an3 d0 e5",
    "离得 l0 i2 d0 e5",
    "增长得 z0 eng1 zh0 ang3 d0 e5",
    "收敛得 sh0 ou1 l0 ian3 d0 e5",
]
lexicon = os.path.join(HERE, "build", "zipvoice-lexicon-patched.txt")
os.makedirs(os.path.dirname(lexicon), exist_ok=True)
with open(os.path.join(front, "lexicon.txt"), encoding="utf-8") as fin, \
        open(lexicon, "w", encoding="utf-8") as fout:
    for row in fin:
        word = row.split(" ", 1)[0]
        fout.write(LEXICON_FIXES[word] + "\n" if word in LEXICON_FIXES else row)
    fout.write("\n".join(LEXICON_ADDITIONS) + "\n")

cfg = sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(
    zipvoice=sherpa_onnx.OfflineTtsZipvoiceModelConfig(
        tokens=os.path.join(front, "tokens.txt"),
        encoder=os.path.join(full, "text_encoder.onnx"),
        decoder=os.path.join(full, "fm_decoder.onnx"),
        data_dir=os.path.join(front, "espeak-ng-data"),
        lexicon=lexicon,
        vocoder=os.path.join(MODEL_DIR, "vocos_24khz.onnx")),
    num_threads=4, provider="cpu"))
assert cfg.validate(), "bad ZipVoice config"
tts = sherpa_onnx.OfflineTts(cfg)

prompt, prompt_sr = sf.read(PROMPT_WAV, dtype="float32")
if prompt.ndim > 1:
    prompt = prompt[:, 0]

sd = os.path.join(MODEL_DIR, "sherpa-onnx-sense-voice-zh-en-ja-ko-yue-int8-2024-07-17")
asr = sherpa_onnx.OfflineRecognizer.from_sense_voice(
    model=f"{sd}/model.int8.onnx", tokens=f"{sd}/tokens.txt",
    language="zh", use_itn=False, num_threads=4)

try:  # naturalness predictor, used as a tie-breaker between takes
    import torch
    sys.path.insert(0, os.path.join(UTMOS_DIR, "SpeechMOS"))
    from speechmos.utmos22.strong.model import UTMOS22Strong
    utmos = UTMOS22Strong()
    utmos.load_state_dict(torch.load(os.path.join(UTMOS_DIR, "utmos22_strong_step7459_v1.pt"), map_location="cpu"))
    utmos.eval()

    def mos(x16):
        with torch.no_grad():
            return float(utmos(torch.from_numpy(x16)[None, :], 16000))
except Exception as exc:  # pragma: no cover - optional dependency
    print("UTMOS unavailable:", exc)

    def mos(x16):
        return 0.0


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


def trim(x, sr, thresh=0.01, pad=0.06):
    idx = np.where(np.abs(x) > thresh)[0]
    if len(idx) == 0:
        return x
    return x[max(0, idx[0] - int(pad * sr)):min(len(x), idx[-1] + int(pad * sr))]


def take(text):
    g = sherpa_onnx.GenerationConfig()
    g.reference_audio = prompt
    g.reference_sample_rate = prompt_sr
    g.reference_text = PROMPT_TEXT
    g.num_steps = STEPS
    g.speed = SPEED
    g.extra["min_char_in_sentence"] = "30"
    a = tts.generate(text, g)
    sr = a.sample_rate
    x = trim(np.asarray(a.samples, dtype=np.float32), sr)
    x16 = ss.resample_poly(x, 2, 3).astype(np.float32)  # 24 kHz -> 16 kHz
    st = asr.create_stream()
    st.accept_waveform(16000, x16)
    asr.decode_stream(st)
    return x, sr, cer(text, st.result.text), mos(x16), st.result.text


only = set(sys.argv[1:])
dpath = os.path.join(HERE, "build", "durations.json")
durations = json.load(open(dpath, encoding="utf-8")) if only and os.path.exists(dpath) else {}
report = []
for key, lines in SCENES:
    durations.setdefault(key, [None] * len(lines))
    for i, line in enumerate(lines):
        name = f"{key}_{i}"
        if only and name not in only:
            continue
        text = spoken_text(line)
        takes = []
        while len(takes) < MAX_TAKES:
            takes.append(take(text))
            best = min(takes, key=lambda t: (round(t[2], 2), -t[3]))
            if len(takes) >= TAKES and best[2] <= 0.05:
                break
        x, sr, e, m, hyp = best
        f = int(0.01 * sr)
        x[:f] *= np.linspace(0, 1, f)
        x[-f:] *= np.linspace(1, 0, f)
        path = os.path.join(OUT, f"{name}.wav")
        sf.write(path, x, sr, subtype="PCM_16")
        durations[key][i] = {"wav": os.path.relpath(path, HERE), "dur": round(len(x) / sr, 3),
                             "chunks": [[c, len(s)] for c, s in line]}
        report.append((name, len(x) / sr, e, m, text, hyp, len(takes)))
        print(f"{name}: {len(x) / sr:5.2f}s CER={e:.3f} UTMOS={m:.2f} takes={len(takes)}\n"
              f"  ref: {text}\n  asr: {hyp}", flush=True)
        with open(dpath, "w", encoding="utf-8") as fh:  # keep progress on disk
            json.dump(durations, fh, ensure_ascii=False, indent=1)

if report:
    print(f"\nTotal speech: {sum(r[1] for r in report):.1f}s  mean CER: {np.mean([r[2] for r in report]):.3f}"
          f"  mean UTMOS: {np.mean([r[3] for r in report]):.2f}")
    for r in sorted(report, key=lambda r: -r[2])[:8]:
        print(f"  {r[0]} CER={r[2]:.3f} UTMOS={r[3]:.2f} asr={r[5]}")
