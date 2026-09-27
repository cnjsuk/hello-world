# 巴塞尔问题：π 为什么会出现在平方倒数和里？

一段约 5 分钟、1920×1080 / 60 fps 的中文讲解视频，成品在
[`output/basel_problem_1080p60.mp4`](output/basel_problem_1080p60.mp4)，
字幕文件在 [`output/basel_problem.zh.srt`](output/basel_problem.zh.srt)。

## 内容

| 段落 | 讲什么 |
| --- | --- |
| 开场 | 1 + 1/4 + 1/9 + … = ?（用边长 1/n 的正方形表示每一项） |
| 历史 | 门戈利 1650 年提出；雅各布·伯努利 1689 年求助；欧拉 1734 年解出、1735 年 12 月 5 日在圣彼得堡科学院宣读 |
| 数值 | 部分和 S₁、S₂、S₁₀、S₁₀₀；用裂项相消说明总和 < 2；欧拉的数值 1.644934 |
| 多项式与根 | P(x) = (1 − x/a)(1 − x/b)(1 − x/c)，x 的系数 = −(1/a + 1/b + 1/c) |
| 正弦函数 | sin x / x 的零点 ±nπ，欧拉的无穷乘积，并演示部分乘积逐渐贴合曲线 |
| 比较系数 | 泰勒展开的 −1/6 对上乘积展开的 −Σ1/(n²π²)，得出 π²/6 |
| π 从哪来 | 单位圆 → 正弦 → 零点是 π 的整数倍；分母的 6 = 3! |
| 严格性 | 1741 年欧拉的新证明；1876 年魏尔斯特拉斯因式分解定理 |
| 余波 | ζ(4) = π⁴/90 … ζ(12)；ζ(3) 仍无闭式；黎曼 1859；两数互质概率 6/π² |

## 重新生成

依赖：Python 3.11、[manim](https://www.manim.community/) 0.21、LaTeX（texlive）、ffmpeg（含 libass）、
Noto Sans CJK 字体、`sherpa-onnx`、`soundfile`、`scipy`。

旁白用离线 TTS 生成（sherpa-onnx + Kokoro v1.1-zh，男声 sid 90），并用 SenseVoice 语音识别回听挑选
发音最准的一版。模型从 sherpa-onnx 的 GitHub Releases 下载到 `MODEL_DIR`：

- `tts-models/kokoro-multi-lang-v1_1.tar.bz2`
- `asr-models/sherpa-onnx-sense-voice-zh-en-ja-ko-yue-int8-2024-07-17.tar.bz2`

```bash
cd basel_video
MODEL_DIR=/path/to/models python3 tts.py   # 生成 build/audio/*.wav 与 build/durations.json
python3 build.py                           # 渲染 10 个场景（1080p60）并合成成品
```

- `script.py`：旁白稿（字幕文字 + 朗读文字）
- `scenes.py`：manim 动画，每个场景按旁白时长自动对齐
- `music.py`：合成很轻的背景铺底音
- `build.py`：拼接场景、烧录字幕、混音、响度标准化（−16 LUFS）
