"""Shared styling and the narration-synced scene base class."""
import json
import os

from manim import (BOLD, NORMAL, WHITE, FadeOut, MathTex, Scene, Text)

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, "build")

BG = "#0f1218"
BLUE_ = "#58C4DD"
YELLOW_ = "#FFD166"
PINK = "#FF6B8B"
GREEN_ = "#5CE1A6"
GREY_ = "#8A93A6"
ORANGE_ = "#FF9F43"
PURPLE_ = "#B388FF"
CJK = "Noto Sans CJK SC"

# Keep all visuals above this y so the burned-in subtitles never cover them.
SAFE_BOTTOM = -2.95

def _load_durations():
    """Real clip durations from tts.py, or (for layout previews before the
    narration exists) an estimate of ~4.5 spoken characters per second."""
    path = os.path.join(BUILD, "durations.json")
    if os.environ.get("PREVIEW") or not os.path.exists(path):
        from script import SCENES
        return {key: [{"wav": None, "dur": len("".join(sp for _, sp in line)) / 4.5,
                       "chunks": [[c, len(sp)] for c, sp in line]} for line in lines]
                for key, lines in SCENES}
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


DURATIONS = _load_durations()


def zh(text, size=36, color=WHITE, bold=False, **kw):
    return Text(text, font=CJK, font_size=size, color=color,
                weight=BOLD if bold else NORMAL, **kw)


def tex(*parts, size=48, color=WHITE, **kw):
    return MathTex(*parts, font_size=size, color=color, **kw)


class VScene(Scene):
    """A scene whose animations are paced by pre-recorded narration.

    ``say(i)`` starts narration line ``i`` (after the previous one has
    finished) and returns its duration so animations can be sized to it.
    Start times are written to build/cues/<KEY>.json for the subtitles.
    """

    KEY = ""
    GAP = 0.3

    def setup(self):
        self.camera.background_color = BG
        self.lines = DURATIONS[self.KEY]
        self.cues = []
        self._end = 0.0

    def say(self, i):
        self.hold()
        info = self.lines[i]
        if info["wav"]:
            self.add_sound(os.path.join(HERE, info["wav"]))
        self.cues.append({"line": i, "start": round(self.time, 4)})
        self._end = self.time + info["dur"]
        return info["dur"]

    def remaining(self):
        return max(0.0, self._end - self.time)

    def hold(self, gap=None):
        gap = self.GAP if gap is None else gap
        rest = self._end + gap - self.time
        if rest >= 1 / 60:
            self.wait(rest)

    def finish(self, extra=0.2, fade=0.6):
        self.hold(extra)
        if self.mobjects:
            self.play(*[FadeOut(m) for m in self.mobjects], run_time=fade)

    def tear_down(self):
        os.makedirs(os.path.join(BUILD, "cues"), exist_ok=True)
        with open(os.path.join(BUILD, "cues", f"{self.KEY}.json"), "w") as fh:
            json.dump({"cues": self.cues, "end": round(self.time, 4)}, fh)
