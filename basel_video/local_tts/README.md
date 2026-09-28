# 在本地电脑用微软语音配音

视频的动画在云端渲染，配音这一步放到你自己的电脑上做：你的网络能直接连到微软的语音服务，
生成好的音频推回 GitHub 后，云端会按新音频的时长重新对齐动画和字幕，再渲染成片。

## 需要准备

- Python 3.9 或更新版本（Windows 从 python.org 安装时勾选 “Add python.exe to PATH”）
- Git（没有也行，见文末“不用 Git 的办法”）

## 第 1 步：取代码

```bash
git clone --depth 1 -b claude/basel-problem-video-9du4ff https://github.com/cnjsuk/hello-world.git
cd hello-world/basel_video/local_tts
```

## 第 2 步：安装依赖

```bash
pip install -r requirements.txt
```

Windows 如果提示找不到 `pip`，用 `py -m pip install -r requirements.txt`；后面的 `python` 同样可以换成 `py`。

## 第 3 步：试听、选语音（可选）

```bash
python make_narration.py --preview
```

会用 5 种中文语音各读两句，放在 `basel_video/voice_preview/`，双击即可试听：

| 语音 | 特点 |
| --- | --- |
| `zh-CN-YunxiNeural`（默认） | 男声，活泼阳光，常用于视频解说 |
| `zh-CN-YunyangNeural` | 男声，专业沉稳，新闻播音风格 |
| `zh-CN-YunjianNeural` | 男声，激情，体育解说风格 |
| `zh-CN-XiaoxiaoNeural` | 女声，温暖 |
| `zh-CN-XiaoyiNeural` | 女声，活泼 |

`python make_narration.py --list-voices` 可以列出全部中文语音。

## 第 4 步：生成全部旁白

```bash
python make_narration.py --voice zh-CN-YunxiNeural
```

共 80 句，一般几分钟就能完成。语速可以用 `--rate -5%`（慢一点）或 `--rate +5%` 调整。
中途断网就直接再运行一次，已经生成的句子会自动跳过。
想换语音重做全部句子，加 `--force`；只重做个别句子，用 `--only intro_0 lake_1 --force`。

输出在 `basel_video/voice_ms/`：每句一个 mp3，外加记录了语音设置和逐词时间戳的 `manifest.json`。

## 第 5 步：推回 GitHub

```bash
cd ..
git add voice_ms
git commit -m "Add Microsoft neural voice narration"
git push
```

推完告诉我一声，我会拉取音频、重新渲染 1080p60 成片并更新在线播放页。

## 可选：Azure 的 HD 语音（需要 Azure 语音服务密钥）

微软更新一代的 HD 语音（例如男声 `zh-CN-Yunfan:DragonHDLatestNeural`、女声
`zh-CN-Xiaochen:DragonHDLatestNeural`）不在 Edge 免费语音里，需要 Azure 语音服务的密钥和区域。
先设置环境变量：

- macOS / Linux：`export AZURE_SPEECH_KEY=你的密钥` 和 `export AZURE_SPEECH_REGION=你的区域`
- Windows PowerShell：`$env:AZURE_SPEECH_KEY="你的密钥"` 和 `$env:AZURE_SPEECH_REGION="你的区域"`

然后：

```bash
python make_narration.py --preview                                   # 试听两种 HD 语音
python make_narration.py --voice zh-CN-Yunfan:DragonHDLatestNeural --force
```

HD 语音只在部分区域提供；如果返回 400/404，请在微软文档里确认你的区域支持该语音。
Azure 接口不返回逐词时间戳，这时字幕按字数比例对齐。
Edge 语音服务适合个人使用；如果视频要商用，建议用 Azure（按微软的服务条款计费使用）。

## 不用 Git 的办法

在第 1 步改为下载压缩包：打开
<https://github.com/cnjsuk/hello-world/tree/claude/basel-problem-video-9du4ff>，
点 “Code → Download ZIP”，解压后进入 `basel_video/local_tts` 继续第 2–4 步。
第 5 步改为在网页上打开同一分支的 `basel_video` 文件夹，点 “Add file → Upload files”，
把整个 `voice_ms` 文件夹拖进去提交。
