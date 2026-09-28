#!/usr/bin/env python3
"""在你自己的电脑上，用微软神经语音为《巴塞尔问题》视频生成全部旁白。

两种方式：
  1. Edge 神经语音（默认，免费，不需要密钥）：通过 edge-tts 调用 Edge “大声朗读”用的在线语音。
  2. Azure 语音服务（可选，需要密钥）：可以用 HD 语音，例如 zh-CN-Yunfan:DragonHDLatestNeural。

常用命令（在本文件所在目录运行）：
  python make_narration.py --list-voices            # 列出可用的中文（普通话）语音
  python make_narration.py --preview                # 用几种候选语音各读两句，放进 voice_preview/ 试听
  python make_narration.py                          # 用默认语音（云希）生成全部 80 句
  python make_narration.py --voice zh-CN-YunyangNeural --rate -5%
  python make_narration.py --only intro_0 lake_1 --force   # 只重做指定几句
  AZURE_SPEECH_KEY=... AZURE_SPEECH_REGION=eastasia python make_narration.py --voice zh-CN-Yunfan:DragonHDLatestNeural

输出在 ../voice_ms/：每句一个音频文件 + manifest.json（语音、语速、逐词时间戳）。
已经生成过的句子会跳过，所以网络中断后直接重新运行即可接着做。
"""
import argparse
import asyncio
import json
import os
import sys
import time
import urllib.error
import urllib.request
from xml.sax.saxutils import escape

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
sys.path.insert(0, PROJ)
from script import SCENES, spoken_text  # noqa: E402

OUT = os.path.join(PROJ, "voice_ms")
PREVIEW_DIR = os.path.join(PROJ, "voice_preview")
DEFAULT_VOICE = "zh-CN-YunxiNeural"
PREVIEW_VOICES = [
    "zh-CN-YunxiNeural",      # 男，活泼阳光
    "zh-CN-YunyangNeural",    # 男，专业沉稳（新闻）
    "zh-CN-YunjianNeural",    # 男，激情（体育解说）
    "zh-CN-XiaoxiaoNeural",   # 女，温暖
    "zh-CN-XiaoyiNeural",     # 女，活泼
]
AZURE_PREVIEW_VOICES = [
    "zh-CN-Yunfan:DragonHDLatestNeural",
    "zh-CN-Xiaochen:DragonHDLatestNeural",
]
PREVIEW_LINES = ["intro_2", "meaning_3"]

# script.py 里有几处为旧的离线 TTS 做的同音字替换，微软语音不需要
MS_TEXT_FIXES = {"圣彼德堡": "圣彼得堡"}


def all_lines():
    for key, lines in SCENES:
        for i, line in enumerate(lines):
            text = spoken_text(line)
            for a, b in MS_TEXT_FIXES.items():
                text = text.replace(a, b)
            yield f"{key}_{i}", text


# ----------------------------------------------------------------- Edge TTS
async def edge_say(text, voice, rate, pitch, path):
    import edge_tts
    com = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch, boundary="WordBoundary")
    words = []
    tmp = path + ".part"
    with open(tmp, "wb") as fh:
        async for chunk in com.stream():
            if chunk["type"] == "audio":
                fh.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                words.append({"text": chunk["text"],
                              "start": round(chunk["offset"] / 1e7, 3),
                              "dur": round(chunk["duration"] / 1e7, 3)})
    if os.path.getsize(tmp) == 0:
        os.remove(tmp)
        raise RuntimeError("服务没有返回音频")
    os.replace(tmp, path)
    return words


async def edge_voices():
    import edge_tts
    vs = await edge_tts.list_voices()
    return [v for v in vs if v["Locale"].startswith("zh-CN")]


# ---------------------------------------------------------------- Azure TTS
def azure_say(text, voice, rate, pitch, style, path, key, region):
    lang = "-".join(voice.split("-")[:2])
    body = escape(text)
    prosody = f'<prosody rate="{rate}" pitch="{pitch}">{body}</prosody>'
    if style:
        prosody = f'<mstts:express-as style="{style}">{prosody}</mstts:express-as>'
    ssml = (f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" '
            f'xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="{lang}">'
            f'<voice name="{voice}">{prosody}</voice></speak>')
    req = urllib.request.Request(
        f"https://{region}.tts.speech.microsoft.com/cognitiveservices/v1",
        data=ssml.encode("utf-8"), method="POST",
        headers={"Ocp-Apim-Subscription-Key": key,
                 "Content-Type": "application/ssml+xml",
                 "X-Microsoft-OutputFormat": "riff-24khz-16bit-mono-pcm",
                 "User-Agent": "basel-video-narration"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        audio = resp.read()
    if len(audio) < 1000:
        raise RuntimeError("服务没有返回音频")
    with open(path + ".part", "wb") as fh:
        fh.write(audio)
    os.replace(path + ".part", path)
    return []  # REST 接口不返回逐词时间戳，字幕按字数比例对齐


# ------------------------------------------------------------------- common
def synth(args, text, voice, path):
    last = None
    for attempt in range(5):
        try:
            if args.azure_key:
                return azure_say(text, voice, args.rate, args.pitch, args.style, path,
                                 args.azure_key, args.azure_region)
            return asyncio.run(edge_say(text, voice, args.rate, args.pitch, path))
        except (urllib.error.HTTPError,) as exc:
            if exc.code in (400, 401, 403, 404):
                raise SystemExit(f"Azure 返回 {exc.code}：请检查密钥、区域和语音名称。{exc.read()[:300]!r}")
            last = exc
        except Exception as exc:  # 网络抖动：退避后重试
            last = exc
        wait = 2 ** (attempt + 1)
        print(f"    出错（{last}），{wait} 秒后重试……", flush=True)
        time.sleep(wait)
    raise SystemExit(f"连续失败 5 次，最后的错误：{last}")


def main():
    ap = argparse.ArgumentParser(description="用微软神经语音生成视频旁白")
    ap.add_argument("--voice", default=DEFAULT_VOICE, help=f"语音名称，默认 {DEFAULT_VOICE}")
    ap.add_argument("--rate", default="+0%", help="语速，例如 -5%% 或 +5%%")
    ap.add_argument("--pitch", default="+0Hz", help="音高，例如 -2Hz")
    ap.add_argument("--style", default="", help="仅 Azure：说话风格，例如 narration-professional")
    ap.add_argument("--only", nargs="*", help="只生成这些句子，例如 intro_0 lake_1")
    ap.add_argument("--force", action="store_true", help="覆盖已经生成的文件")
    ap.add_argument("--preview", action="store_true", help="生成几种候选语音的试听样本")
    ap.add_argument("--list-voices", action="store_true", help="列出 Edge 的中文语音")
    ap.add_argument("--azure-key", default=os.environ.get("AZURE_SPEECH_KEY", ""))
    ap.add_argument("--azure-region", default=os.environ.get("AZURE_SPEECH_REGION", "eastasia"))
    args = ap.parse_args()

    if args.list_voices:
        for v in asyncio.run(edge_voices()):
            tags = "、".join(v.get("VoiceTag", {}).get("VoicePersonalities", []))
            print(f'{v["ShortName"]:32s} {v["Gender"]:6s} {tags}')
        return

    texts = dict(all_lines())
    ext = ".wav" if args.azure_key else ".mp3"

    if args.preview:
        os.makedirs(PREVIEW_DIR, exist_ok=True)
        voices = AZURE_PREVIEW_VOICES if args.azure_key else PREVIEW_VOICES
        for voice in voices:
            for name in PREVIEW_LINES:
                path = os.path.join(PREVIEW_DIR, f"{voice.replace(':', '_')}__{name}{ext}")
                print(f"{voice}  {name}", flush=True)
                synth(args, texts[name], voice, path)
        print(f"\n试听文件在：{PREVIEW_DIR}\n选好之后运行：python make_narration.py --voice <语音名称>")
        return

    os.makedirs(OUT, exist_ok=True)
    manifest_path = os.path.join(OUT, "manifest.json")
    manifest = {"lines": {}}
    if os.path.exists(manifest_path):
        manifest = json.load(open(manifest_path, encoding="utf-8"))
    settings = {"engine": "azure" if args.azure_key else "edge", "voice": args.voice,
                "rate": args.rate, "pitch": args.pitch, "style": args.style}
    if manifest.get("settings") and manifest["settings"] != settings and not args.force and not args.only:
        raise SystemExit("voice_ms/ 里已有用其它设置生成的旁白。要整体换语音，请加 --force 重新生成全部句子。")
    manifest["settings"] = settings

    todo = [(n, t) for n, t in texts.items() if not args.only or n in args.only]
    t0 = time.time()
    for k, (name, text) in enumerate(todo, 1):
        path = os.path.join(OUT, name + ext)
        if os.path.exists(path) and name in manifest["lines"] and not args.force:
            continue
        print(f"[{k}/{len(todo)}] {name}  {text[:28]}……", flush=True)
        words = synth(args, text, args.voice, path)
        manifest["lines"][name] = {"file": name + ext, "text": text, "words": words}
        with open(manifest_path, "w", encoding="utf-8") as fh:  # 每句写一次，方便断点续跑
            json.dump(manifest, fh, ensure_ascii=False, indent=1)
    missing = [n for n in texts if n not in manifest["lines"]]
    print(f"\n完成，用时 {time.time() - t0:.0f} 秒。输出目录：{OUT}")
    if missing:
        print(f"还有 {len(missing)} 句没有生成：{' '.join(missing[:10])} ……")
    else:
        print("全部 80 句都已生成。下一步：把 basel_video/voice_ms/ 推送到 GitHub（见 README）。")


if __name__ == "__main__":
    main()
