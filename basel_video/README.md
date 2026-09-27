# 巴塞尔问题：π 为什么会出现在平方倒数和里？

约 13 分钟、1920×1080 / 60 fps 的中文讲解视频，成品在
[`output/basel_problem_1080p60.mp4`](output/basel_problem_1080p60.mp4)，
字幕文件在 [`output/basel_problem.zh.srt`](output/basel_problem.zh.srt)。

## 内容

| 段落 | 讲什么 |
| --- | --- |
| 问题 | 1 + 1/4 + 1/9 + … = ?（用边长 1/n 的正方形表示每一项） |
| 历史 | 门戈利 1650 年提出；雅各布·伯努利 1689 年求助；欧拉 1734 年解出、1735 年 12 月在圣彼得堡科学院宣读 |
| 数值 | 部分和；裂项相消说明总和 < 2；欧拉的数值 1.644934 |
| 欧拉的证明 | 多项式由根决定 → sin x / x 的无穷乘积 → 与泰勒展开比较 x² 系数，得 π²/6 |
| π 从哪来（一） | 弧度：角 = 单位圆上的弧长；正弦 = 高度；零点每隔一个 π 出现一次 |
| π 从哪来（二） | 为什么是平方（零点正负成对）；6 = 3! 来自正弦在 0 附近的弯曲 |
| 直观证明：灯塔 | 亮度 ∝ 1/d²；逆勾股定理 1/a² + 1/b² = 1/h²；周长为 2 的湖 → 不断加倍 → 直线；奇数平方和 π²/8 → π²/6（Wästlund 2010） |
| π 的意义 | 直线是无限大的圆；直径 = 周长 ÷ π；平方反比带来 π²；两条证明说的是同一件事 |
| 用整数算 π | π = √(6 Σ 1/n²) 的收敛 |
| 严格性 | 沃利斯乘积（1656）；欧拉 1741 年的新证明；1876 年魏尔斯特拉斯因式分解定理 |
| 余波 | ζ(2k) = 有理数 × π²ᵏ；ζ(3) 与阿佩里 1978；黎曼 1859；两数互质概率 6/π² |

## 重新生成

依赖：Python 3.11、[manim](https://www.manim.community/) 0.21、LaTeX（texlive）、ffmpeg（含 libass）、
Noto Sans CJK 字体、`sherpa-onnx`、`soundfile`、`scipy`。

旁白用离线 TTS 生成（sherpa-onnx + Kokoro v1.1-zh，男声 sid 90），每句合成多遍，再用 SenseVoice
语音识别回听挑选发音最准的一版。模型从 sherpa-onnx 的 GitHub Releases 下载到 `MODEL_DIR`：

- `tts-models/kokoro-multi-lang-v1_1.tar.bz2`
- `asr-models/sherpa-onnx-sense-voice-zh-en-ja-ko-yue-int8-2024-07-17.tar.bz2`

```bash
cd basel_video
MODEL_DIR=/path/to/models python3 tts.py   # 生成 build/audio/*.wav 与 build/durations.json
python3 build.py                           # 渲染 17 个场景（1080p60）并合成成品
PREVIEW=1 manim -ql scenes.py S12Doubling  # 不需要旁白的低清排版预览
```

- `script.py`：旁白稿（字幕文字 + 朗读文字）
- `scenes.py`：manim 动画，每个场景按旁白时长自动对齐
- `music.py`：合成很轻的背景铺底音
- `build.py`：拼接场景、烧录字幕、混音、响度标准化（−16 LUFS）
