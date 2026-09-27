"""Manim scenes for the Basel problem video (render with -qh for 1080p60).

Each scene is paced by its narration lines (see common.VScene).
"""
from math import gcd

import numpy as np
from manim import *

from common import (BLUE_, GREEN_, GREY_, ORANGE_, PINK, PURPLE_, YELLOW_,
                    VScene, tex, zh)

PI2 = np.pi ** 2 / 6


def sinc(x):
    return np.sinc(x / np.pi)  # sin(x)/x with the removable singularity filled


def partial_product(x, n):
    k = np.arange(1, n + 1)
    return np.prod(1 - x ** 2 / (k ** 2 * np.pi ** 2))


# ---------------------------------------------------------------------------
class S01Intro(VScene):
    KEY = "intro"

    def construct(self):
        self.wait(0.3)
        series = tex("1", "+", r"\frac{1}{4}", "+", r"\frac{1}{9}", "+",
                     r"\frac{1}{16}", "+", r"\frac{1}{25}", "+", r"\cdots",
                     "=", "?", size=80)
        series.to_edge(UP, buff=0.8)
        series[-1].set_color(YELLOW_)

        # squares of side 1/n: their areas are the terms of the series
        squares = VGroup()
        unit = 2.5
        for n in range(1, 21):
            s = unit / n
            sq = Square(side_length=s, stroke_width=2 if n < 8 else 1,
                        stroke_color=BLUE_, fill_color=BLUE_,
                        fill_opacity=0.15 + 0.55 / n)
            squares.add(sq)
        squares.arrange(RIGHT, buff=0.1, aligned_edge=DOWN)
        squares.move_to(ORIGIN).align_to(DOWN * 2.55, DOWN)
        labels = VGroup(*[
            tex(t, size=36, color=GREY_).next_to(squares[i], UP, buff=0.15)
            for i, t in enumerate(["1", r"\tfrac{1}{4}", r"\tfrac{1}{9}", r"\tfrac{1}{16}"])
        ])
        cap = zh("边长为 1/n 的正方形，面积恰好是 1/n²", 28, GREY_)
        cap.move_to([0, 0.95, 0]).align_to(squares, RIGHT)

        D = self.say(0)
        step = 0.52 * D / 4
        for k in range(4):
            parts = [series[2 * k]] if k == 0 else [series[2 * k - 1], series[2 * k]]
            self.play(*[FadeIn(p, shift=0.2 * DOWN) for p in parts],
                      GrowFromEdge(squares[k], DOWN), FadeIn(labels[k]),
                      run_time=step)
        self.play(FadeIn(series[7:11], shift=0.2 * DOWN),
                  LaggedStart(*[GrowFromEdge(s, DOWN) for s in squares[4:]], lag_ratio=0.15),
                  FadeIn(cap), run_time=0.3 * D)
        self.play(Write(series[11:]), run_time=0.5)
        self.hold()

        D = self.say(1)
        self.play(Indicate(series[-1], scale_factor=1.6, color=YELLOW_), run_time=1.2)
        self.play(squares.animate.set_fill(opacity=0.08).set_stroke(opacity=0.4),
                  labels.animate.set_opacity(0.35), cap.animate.set_opacity(0.35),
                  run_time=1.0)
        self.hold()

        D = self.say(2)
        pi = tex(r"\pi", size=150, color=YELLOW_).move_to(series[-1]).shift(0.1 * DOWN)
        self.play(FadeOut(VGroup(squares, labels, cap)),
                  ReplacementTransform(series[-1], pi), run_time=1.0)
        self.play(pi.animate.move_to(0.2 * DOWN), FadeOut(series[:-1], shift=UP),
                  run_time=1.0)
        ring = Circle(radius=1.2, color=YELLOW_, stroke_width=3).move_to(pi)
        self.play(Create(ring), run_time=1.0)
        title = zh("巴塞尔问题", 84, bold=True).to_edge(UP, buff=0.9)
        sub = Text("The Basel Problem", font_size=36, color=GREY_).next_to(title, DOWN, buff=0.25)
        self.play(FadeIn(title, shift=0.3 * DOWN), FadeIn(sub), run_time=0.9)
        self.hold(0.8)
        self.finish(extra=0)


# ---------------------------------------------------------------------------
class S02History(VScene):
    KEY = "history"

    def construct(self):
        self.wait(0.2)
        line = NumberLine(x_range=[1640, 1750, 10], length=12.4, include_numbers=False,
                          color=GREY_, stroke_width=2, tick_size=0.06)
        line.move_to(UP * 2.55)
        years = VGroup(*[
            Text(str(y), font_size=22, color=GREY_).next_to(line.n2p(y), UP, buff=0.15)
            for y in (1650, 1700, 1750)
        ])

        def event(year, color):
            dot = Dot(line.n2p(year), radius=0.1, color=color)
            lab = Text(str(year), font_size=30, color=color, weight=BOLD).next_to(dot, DOWN, buff=0.18)
            return dot, lab

        def card(title, latin, lines, color, x):
            t = zh(title, 34, color, bold=True)
            l = Text(latin, font_size=24, color=GREY_, slant=ITALIC)
            body = VGroup(*[zh(s, 24) for s in lines]).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
            g = VGroup(t, l, body).arrange(DOWN, aligned_edge=LEFT, buff=0.16)
            box = SurroundingRectangle(g, buff=0.22, corner_radius=0.12, color=color,
                                       stroke_width=1.5, fill_color=color, fill_opacity=0.06)
            c = VGroup(box, g)
            c.move_to([x, 0.55, 0]).align_to(UP * 1.75, UP)
            c.shift(RIGHT * np.clip(-6.85 - c.get_left()[0], 0, None))
            c.shift(LEFT * np.clip(c.get_right()[0] - 6.85, 0, None))
            return c

        # 1650 Mengoli
        D = self.say(0)
        self.play(Create(line), FadeIn(years), run_time=1.0)
        d1, y1 = event(1650, BLUE_)
        c1 = card("门戈利", "Pietro Mengoli", ["意大利 · 博洛尼亚", "《Novae quadraturae", "  arithmeticae》"],
                  BLUE_, line.n2p(1650)[0])
        self.play(GrowFromCenter(d1), FadeIn(y1), FadeIn(c1, shift=0.2 * DOWN), run_time=1.2)
        self.hold()

        # 1689 Jakob Bernoulli
        D = self.say(1)
        d2, y2 = event(1689, GREEN_)
        c2 = card("雅各布·伯努利", "Jakob Bernoulli", ["瑞士 · 巴塞尔", "知道：这个和是有限的", "但求不出确切值"],
                  GREEN_, line.n2p(1689)[0])
        self.play(GrowFromCenter(d2), FadeIn(y2), FadeIn(c2, shift=0.2 * DOWN), run_time=1.2)
        self.wait(0.45 * D - 1.2)
        quote = VGroup(
            zh("“若有人能求出这个一直难倒我们的结果，并告诉我们，", 28),
            zh("我们将不胜感激。”", 28),
            zh("—— 雅各布·伯努利，1689", 24, GREY_),
        ).arrange(DOWN, buff=0.18)
        quote[2].align_to(quote[0], RIGHT)
        quote.move_to(DOWN * 2.05)
        self.play(FadeIn(quote[:2], shift=0.2 * UP), run_time=1.2)
        self.play(FadeIn(quote[2]), run_time=0.6)
        self.hold()

        # named after Basel
        D = self.say(2)
        basel = VGroup(Text("Basel", font_size=64, weight=BOLD, color=YELLOW_),
                       zh("巴塞尔", 56, YELLOW_, bold=True)).arrange(RIGHT, buff=0.4)
        home = zh("伯努利家族的故乡 · 欧拉的故乡", 30, GREY_)
        bg = VGroup(basel, home).arrange(DOWN, buff=0.25).move_to(DOWN * 2.05)
        self.play(FadeOut(quote, shift=0.2 * DOWN), run_time=0.6)
        self.play(FadeIn(basel, scale=1.2), c2[0].animate.set_stroke(YELLOW_, width=3), run_time=1.0)
        self.play(FadeIn(home), run_time=0.8)
        self.hold()

        # 1734 Euler
        D = self.say(3)
        d3, y3 = event(1734, YELLOW_)
        c3 = card("莱昂哈德·欧拉", "Leonhard Euler", ["1734 年解出", "1735.12.5 在圣彼得堡", "科学院宣读 · 时年 28 岁"],
                  YELLOW_, line.n2p(1734)[0])
        self.play(FadeOut(bg), c2[0].animate.set_stroke(GREEN_, width=1.5), run_time=0.6)
        self.play(GrowFromCenter(d3), FadeIn(y3), FadeIn(c3, shift=0.2 * DOWN), run_time=1.2)
        span = BraceBetweenPoints(line.n2p(1650) + UP * 0.02, line.n2p(1734) + UP * 0.02, UP, color=GREY_)
        span.shift(UP * 0.3)
        years_txt = zh("84 年", 26, GREY_).next_to(span, UP, buff=0.08)
        self.play(FadeOut(years), GrowFromCenter(span), FadeIn(years_txt), run_time=1.0)
        self.finish(extra=0.5)


# ---------------------------------------------------------------------------
class S03Numeric(VScene):
    KEY = "numeric"

    def construct(self):
        self.wait(0.2)
        axes = Axes(x_range=[0, 31, 5], y_range=[0, 2.25, 0.5], x_length=7.2, y_length=4.6,
                    axis_config={"color": GREY_, "stroke_width": 2, "include_ticks": True},
                    x_axis_config={"numbers_to_include": [5, 10, 15, 20, 25, 30], "font_size": 26},
                    y_axis_config={"numbers_to_include": [0.5, 1, 1.5, 2], "font_size": 26},
                    tips=False)
        axes.move_to([-3.1, 0.15, 0])
        xl = zh("项数 N", 24, GREY_).next_to(axes.x_axis, DOWN, buff=0.35).align_to(axes.x_axis, RIGHT)
        yl = zh("前 N 项之和", 24, GREY_).next_to(axes.y_axis, UP, buff=0.15).shift(RIGHT * 0.6)
        sums = np.cumsum([1 / n ** 2 for n in range(1, 31)])
        bars = VGroup()
        for n, s in enumerate(sums, start=1):
            p0, p1 = axes.c2p(n - 0.38, 0), axes.c2p(n + 0.38, s)
            bar = Rectangle(width=p1[0] - p0[0], height=p1[1] - p0[1], stroke_width=0,
                            fill_color=interpolate_color(ManimColor(BLUE_), ManimColor(GREEN_), n / 30),
                            fill_opacity=0.85)
            bar.move_to((p0 + p1) / 2)
            bars.add(bar)
        readouts = VGroup(
            tex(r"S_{1} = 1", size=44),
            tex(r"S_{2} = 1.25", size=44),
            tex(r"S_{10} \approx 1.5498", size=44),
            tex(r"S_{100} \approx 1.6350", size=44),
            tex(r"S_{1000} \approx 1.6439", size=44),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.32).move_to([4.2, 0.4, 0])
        sdef = tex(r"S_N = \sum_{n=1}^{N} \frac{1}{n^2}", size=40, color=GREY_).next_to(readouts, UP, buff=0.5)

        D = self.say(0)
        self.play(Create(axes), FadeIn(xl), FadeIn(yl), FadeIn(sdef), run_time=1.0)
        self.play(GrowFromEdge(bars[0], DOWN), FadeIn(readouts[0]), run_time=0.9)
        self.play(GrowFromEdge(bars[1], DOWN), FadeIn(readouts[1]), run_time=0.9)
        t = max(1.0, 0.45 * D - 1.8)
        self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars[2:10]], lag_ratio=0.3),
                  FadeIn(readouts[2]), run_time=t)
        self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars[10:]], lag_ratio=0.2),
                  FadeIn(readouts[3]), FadeIn(readouts[4]), run_time=max(1.0, self.remaining()))
        self.hold()

        D = self.say(1)
        two = DashedLine(axes.c2p(0, 2), axes.c2p(31, 2), color=PINK, dash_length=0.12)
        two_l = tex("2", size=34, color=PINK).next_to(two, RIGHT, buff=0.1)
        lim = DashedLine(axes.c2p(0, PI2), axes.c2p(31, PI2), color=YELLOW_, dash_length=0.08, stroke_width=2)
        lim_l = tex("?", size=40, color=YELLOW_).next_to(lim, RIGHT, buff=0.1)
        self.play(Create(two), FadeIn(two_l), run_time=1.2)
        self.play(Create(lim), FadeIn(lim_l), run_time=1.0)
        self.hold()

        D = self.say(2)
        chart = VGroup(axes, xl, yl, bars, two, two_l, lim, lim_l)
        self.play(FadeOut(readouts), FadeOut(sdef), chart.animate.scale(0.45).to_corner(UL, buff=0.3),
                  run_time=1.0)
        ineq = tex(r"\frac{1}{n^2}", "<", r"\frac{1}{(n-1)\,n}", "=", r"\frac{1}{n-1}-\frac{1}{n}",
                   r"\qquad (n\ge 2)", size=48)
        ineq.move_to([2.4, 2.45, 0])
        ineq[-1].set_color(GREY_)
        self.play(Write(ineq), run_time=1.6)
        tele = tex(r"\frac{1}{4}+\frac{1}{9}+\frac{1}{16}+\cdots", "<",
                   r"\left(1-\frac{1}{2}\right)", "+", r"\left(\frac{1}{2}-\frac{1}{3}\right)", "+",
                   r"\left(\frac{1}{3}-\frac{1}{4}\right)", "+", r"\cdots", "=", "1", size=44)
        tele.move_to([0.2, 0.05, 0])
        if tele.width > 13.2:
            tele.scale_to_fit_width(13.2)
        self.play(FadeIn(tele[:2]), run_time=0.8)
        self.play(FadeIn(tele[2:9], lag_ratio=0.2), run_time=1.6)
        # cross out the cancelling pairs: -1/2 with +1/2, -1/3 with +1/3
        def strike(mob, a, b):
            sub = mob[a:b] if b else mob
            return Line(sub.get_corner(DL), sub.get_corner(UR), color=PINK, stroke_width=4)
        p1, p2, p3 = tele[2], tele[4], tele[6]
        n1 = len(p1)
        s1 = Line(p1[n1 - 4:n1 - 1].get_corner(DL), p1[n1 - 4:n1 - 1].get_corner(UR), color=PINK, stroke_width=4)
        s2 = Line(p2[1:4].get_corner(DL), p2[1:4].get_corner(UR), color=PINK, stroke_width=4)
        n2 = len(p2)
        s3 = Line(p2[n2 - 4:n2 - 1].get_corner(DL), p2[n2 - 4:n2 - 1].get_corner(UR), color=PINK, stroke_width=4)
        s4 = Line(p3[1:4].get_corner(DL), p3[1:4].get_corner(UR), color=PINK, stroke_width=4)
        self.play(LaggedStart(Create(s1), Create(s2), Create(s3), Create(s4), lag_ratio=0.35), run_time=1.6)
        self.play(FadeIn(tele[9:], scale=1.3), run_time=0.7)
        total = tex(r"1+\frac{1}{4}+\frac{1}{9}+\frac{1}{16}+\cdots", "<", "1+1", "=", "2", size=52)
        total[-1].set_color(PINK)
        total.move_to([0.2, -1.85, 0])
        self.play(Write(total), run_time=max(0.8, min(1.5, self.remaining())))
        self.hold()

        D = self.say(3)
        self.play(*[FadeOut(m) for m in [chart, ineq, tele, s1, s2, s3, s4, total]], run_time=0.8)
        num = tex(r"1.644934\ldots", size=110).move_to(UP * 0.6)
        who = zh("欧拉的数值估算", 30, GREY_).next_to(num, UP, buff=0.5)
        self.play(FadeIn(who), Write(num), run_time=1.8)
        self.wait(max(0, 0.5 * D - 2.6))
        q = tex("=", r"\ ?", size=110).next_to(num, RIGHT, buff=0.3)
        q[1].set_color(YELLOW_)
        grp = VGroup(num, q)
        self.play(FadeIn(q), grp.animate.move_to(UP * 0.6), run_time=0.8)
        self.play(Indicate(q[1], scale_factor=1.4, color=YELLOW_), run_time=1.0)
        self.finish(extra=0.3)


# ---------------------------------------------------------------------------
class S04Poly(VScene):
    KEY = "poly"

    def construct(self):
        self.wait(0.2)
        a, b, c = -1.5, 1.0, 2.5
        P = lambda x: (1 - x / a) * (1 - x / b) * (1 - x / c)
        axes = Axes(x_range=[-2.2, 3.2, 1], y_range=[-1.6, 1.8, 1], x_length=6.2, y_length=4.6,
                    axis_config={"color": GREY_, "stroke_width": 2}, tips=False)
        axes.move_to([-3.6, 0.1, 0])
        graph = axes.plot(P, x_range=[-1.95, 3.05], color=BLUE_, stroke_width=4)
        head = zh("多项式由它的根决定", 40, bold=True).to_edge(UP, buff=0.45)

        D = self.say(0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(axes), run_time=1.2)
        self.play(Create(graph), run_time=1.6)
        roots = VGroup(*[Dot(axes.c2p(r, 0), radius=0.09, color=PINK) for r in (a, b, c)])
        # put each label on the side of the root the curve does not pass through
        rl = VGroup(*[tex(s, size=40, color=PINK).next_to(d, direction, buff=0.1)
                      for s, d, direction in zip("abc", roots, (UL, UR, DR))])
        self.play(LaggedStart(*[GrowFromCenter(d) for d in roots], lag_ratio=0.3),
                  LaggedStart(*[FadeIn(l) for l in rl], lag_ratio=0.3), run_time=1.2)
        self.hold()

        D = self.say(1)
        one = Dot(axes.c2p(0, 1), radius=0.09, color=YELLOW_)
        one_l = tex("P(0)=1", size=34, color=YELLOW_).next_to(one, UR, buff=0.08)
        self.play(GrowFromCenter(one), FadeIn(one_l), run_time=0.9)
        f1 = tex("P(x)", "=", r"\left(1-\frac{x}{a}\right)", r"\left(1-\frac{x}{b}\right)",
                 r"\left(1-\frac{x}{c}\right)", size=46)
        f1.move_to([3.45, 1.2, 0])
        if f1.width > 6.6:
            f1.scale_to_fit_width(6.6)
        for i, col in zip((2, 3, 4), (PINK, PINK, PINK)):
            f1[i].set_color(WHITE)
        self.play(Write(f1[:2]), run_time=0.6)
        for i, d in zip((2, 3, 4), roots):
            self.play(FadeIn(f1[i], shift=0.15 * DOWN), Indicate(d, scale_factor=1.8), run_time=0.75)
        self.hold()

        D = self.say(2)
        f2 = tex("P(x)", "=", "1", "-", r"\left(\frac{1}{a}+\frac{1}{b}+\frac{1}{c}\right)", "x", r"+\cdots",
                 size=46)
        f2.next_to(f1, DOWN, buff=0.9).align_to(f1, LEFT)
        if f2.width > 6.6:
            f2.scale_to_fit_width(6.6).align_to(f1, LEFT)
        self.play(TransformFromCopy(f1, f2), run_time=1.4)
        box = SurroundingRectangle(f2[3:5], color=YELLOW_, buff=0.1)
        note = zh("x 的系数 = −（根的倒数之和）", 28, YELLOW_).next_to(box, DOWN, buff=0.35)
        note.align_to(f2, LEFT)
        self.play(Create(box), f2[3:5].animate.set_color(YELLOW_), run_time=0.9)
        self.play(FadeIn(note, shift=0.15 * UP), run_time=0.8)
        link = VGroup(zh("根", 34, PINK, bold=True), tex(r"\longleftrightarrow", size=48),
                      zh("系数", 34, YELLOW_, bold=True)).arrange(RIGHT, buff=0.3)
        link.next_to(note, DOWN, buff=0.5).align_to(f2, LEFT).shift(RIGHT * 0.8)
        self.play(FadeIn(link, scale=1.2), run_time=max(0.6, min(1.0, self.remaining())))
        self.finish(extra=0.6)


# ---------------------------------------------------------------------------
class S05Sine(VScene):
    KEY = "sine"

    def construct(self):
        self.wait(0.2)
        L = 4 * np.pi + 0.6
        axes = Axes(x_range=[-L, L, np.pi], y_range=[-0.45, 1.25, 0.5], x_length=13.4, y_length=3.3,
                    axis_config={"color": GREY_, "stroke_width": 2}, tips=False)
        axes.move_to(UP * 0.95)
        graph = axes.plot(sinc, x_range=[-L, L, 0.02], color=BLUE_, stroke_width=4)
        head = VGroup(zh("正弦函数：一个“无穷次多项式”？", 38, bold=True)).to_edge(UP, buff=0.35)
        name = tex(r"y=\frac{\sin x}{x}", size=44, color=BLUE_).move_to([4.6, 2.25, 0])

        D = self.say(0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(axes), run_time=1.2)
        self.play(Create(graph), FadeIn(name), run_time=2.2)
        self.hold()

        D = self.say(1)
        one = Dot(axes.c2p(0, 1), color=YELLOW_, radius=0.08)
        one_l = tex("1", size=36, color=YELLOW_).next_to(one, UR, buff=0.08)
        self.play(GrowFromCenter(one), FadeIn(one_l), run_time=0.8)
        zeros, zl = VGroup(), VGroup()
        for n in (1, 2, 3, 4):
            for sgn in (1, -1):
                zeros.add(Dot(axes.c2p(sgn * n * np.pi, 0), color=PINK, radius=0.08))
                s = ("" if n == 1 else str(n)) + r"\pi"
                zl.add(tex(("-" if sgn < 0 else "") + s, size=30, color=PINK)
                       .next_to(axes.c2p(sgn * n * np.pi, 0), DOWN, buff=0.22))
        self.play(LaggedStart(*[AnimationGroup(GrowFromCenter(z), FadeIn(l)) for z, l in zip(zeros, zl)],
                              lag_ratio=0.25), run_time=max(1.5, 0.75 * D - 0.8))
        self.hold()

        D = self.say(2)
        arcs = VGroup()
        for n, col in zip((1, 2, 3), (YELLOW_, ORANGE_, PURPLE_)):
            arc = ArcBetweenPoints(axes.c2p(-n * np.pi, 0) + DOWN * 0.55, axes.c2p(n * np.pi, 0) + DOWN * 0.55,
                                   angle=PI * 0.35, color=col, stroke_width=3)
            arcs.add(arc)
        pair = tex(r"\left(1-\frac{x}{n\pi}\right)", r"\left(1+\frac{x}{n\pi}\right)", "=",
                   r"1-\frac{x^2}{n^2\pi^2}", size=50)
        pair.move_to(DOWN * 2.1)
        pair[3].set_color(YELLOW_)
        self.play(LaggedStart(*[Create(a) for a in arcs], lag_ratio=0.4), run_time=1.8)
        self.play(Write(pair[:2]), run_time=1.4)
        self.play(Write(pair[2:]), run_time=1.2)
        self.hold()

        D = self.say(3)
        prod = tex(r"\frac{\sin x}{x}", "=", r"\left(1-\frac{x^2}{\pi^2}\right)",
                   r"\left(1-\frac{x^2}{4\pi^2}\right)", r"\left(1-\frac{x^2}{9\pi^2}\right)", r"\cdots", size=50)
        prod.move_to(DOWN * 2.1)
        prod[0].set_color(BLUE_)
        self.play(FadeOut(arcs), ReplacementTransform(pair, prod), run_time=1.3)
        frame = SurroundingRectangle(prod, color=YELLOW_, buff=0.18, corner_radius=0.1)
        self.play(Create(frame), run_time=0.7)

        # partial products creeping onto sin(x)/x
        def pp_graph(n):
            xs = np.linspace(0, L, 2000)
            ok = np.array([-0.42 <= partial_product(x, n) <= 1.22 for x in xs])
            bad = np.where(~ok)[0]
            xmax = xs[bad[0] - 1] if len(bad) else L
            return axes.plot(lambda x: partial_product(x, n), x_range=[-xmax, xmax, 0.02],
                             color=ORANGE_, stroke_width=3)
        label = lambda n: tex(rf"N={n}", size=34, color=ORANGE_).move_to([-5.2, 2.25, 0])
        g, lab = pp_graph(1), label(1)
        self.play(Create(g), FadeIn(lab), run_time=0.7)
        steps = [2, 4, 8, 25]
        t = max(0.4, (self.remaining() - 0.2) / len(steps))
        for n in steps:
            self.play(Transform(g, pp_graph(n)), Transform(lab, label(n)), run_time=t)
        self.finish(extra=0.5)


# ---------------------------------------------------------------------------
class S06Compare(VScene):
    KEY = "compare"

    def construct(self):
        self.wait(0.2)
        A = tex(r"\sin x", "=", "x", r"-\frac{x^3}{3!}", r"+\frac{x^5}{5!}", r"-\cdots", size=50)
        B = tex(r"\frac{\sin x}{x}", "=", "1", r"-\frac{1}{6}", "x^2", r"+\frac{1}{120}x^4-\cdots", size=50)
        C = tex(r"\frac{\sin x}{x}", "=", r"\left(1-\frac{x^2}{\pi^2}\right)", r"\left(1-\frac{x^2}{4\pi^2}\right)",
                r"\left(1-\frac{x^2}{9\pi^2}\right)", r"\cdots", size=50)
        Dd = tex("=", "1", "-", r"\left(\frac{1}{\pi^2}+\frac{1}{4\pi^2}+\frac{1}{9\pi^2}+\cdots\right)", "x^2",
                 r"+\cdots", size=50)
        A.move_to([0, 2.75, 0])
        B.move_to([0, 1.45, 0])
        C.move_to([0, -0.05, 0])
        Dd.move_to([0, -1.6, 0])
        Dd.align_to(C[1], LEFT)
        for m in (A, B, C, Dd):
            m[0].set_color(BLUE_) if m is not Dd else None
        tag1 = zh("泰勒展开", 26, GREY_).next_to(A, LEFT, buff=0.5)
        tag2 = zh("欧拉的乘积", 26, GREY_).next_to(C, LEFT, buff=0.5)
        # centre each labelled row as a unit so the labels stay on screen
        VGroup(tag1, A).move_to([0, A.get_y(), 0])
        VGroup(tag2, C).move_to([0, C.get_y(), 0])
        Dd.align_to(C[1], LEFT)

        D = self.say(0)
        self.play(Write(A), FadeIn(tag1), run_time=1.8)
        self.play(TransformFromCopy(A, B), run_time=1.5)
        b1 = SurroundingRectangle(B[3], color=YELLOW_, buff=0.08)
        self.play(Create(b1), B[3].animate.set_color(YELLOW_), run_time=0.8)
        self.hold()

        D = self.say(1)
        self.play(Write(C), FadeIn(tag2), run_time=1.6)
        self.wait(max(0, 0.22 * D - 1.6))
        for i in (2, 3, 4):
            self.play(Indicate(C[i], color=BLUE_, scale_factor=1.12), run_time=0.7)
        self.play(FadeIn(Dd, shift=0.2 * DOWN), run_time=1.2)
        b2 = SurroundingRectangle(Dd[2:4], color=BLUE_, buff=0.08)
        self.play(Create(b2), Dd[2:4].animate.set_color(BLUE_), run_time=max(0.8, min(1.4, self.remaining())))
        self.hold()

        D = self.say(2)
        eq1 = tex(r"-\frac{1}{6}", "=", r"-\left(\frac{1}{\pi^2}+\frac{1}{4\pi^2}+\frac{1}{9\pi^2}+\cdots\right)",
                  size=54)
        eq1[0].set_color(YELLOW_)
        eq1[2].set_color(BLUE_)
        eq1.move_to(UP * 0.4)
        self.play(FadeOut(VGroup(b1, b2)), run_time=0.3)
        self.play(FadeTransform(B[3], eq1[0]),
                  FadeTransform(Dd[2:4], eq1[2]),
                  FadeIn(eq1[1]),
                  FadeOut(VGroup(A, B[:3], B[4:], C, Dd[:2], Dd[4:], tag1, tag2)), run_time=1.3)
        self.wait(max(0, 0.45 * D - 1.6))
        eq2 = tex(r"\frac{1}{6}", "=", r"\frac{1}{\pi^2}", r"\left(1+\frac{1}{4}+\frac{1}{9}+\cdots\right)", size=54)
        eq2[0].set_color(YELLOW_)
        eq2[2].set_color(PINK)
        eq2[3].set_color(BLUE_)
        eq2.move_to(DOWN * 1.2)
        self.play(FadeIn(eq2, shift=0.3 * DOWN), run_time=1.2)
        self.hold()

        D = self.say(3)
        final = tex(r"1+\frac{1}{4}+\frac{1}{9}+\frac{1}{16}+\cdots", "=", r"\frac{\pi^2}{6}", size=84)
        final[2].set_color(YELLOW_)
        final.move_to(UP * 0.3)
        self.play(FadeOut(VGroup(eq1, eq2), shift=0.3 * UP), run_time=0.5)
        self.play(Write(final), run_time=2.2)
        glow = SurroundingRectangle(final, color=YELLOW_, buff=0.3, corner_radius=0.15, stroke_width=3)
        check = tex(r"\frac{\pi^2}{6} = 1.6449340668\ldots", size=44, color=GREY_).next_to(glow, DOWN, buff=0.45)
        self.play(Create(glow), run_time=1.0)
        self.play(FadeIn(check, shift=0.15 * UP), run_time=0.8)
        self.finish(extra=0.9)


# ---------------------------------------------------------------------------
class S07WhyPi(VScene):
    KEY = "whypi"

    def construct(self):
        self.wait(0.2)
        res = tex(r"\sum_{n=1}^{\infty}\frac{1}{n^2}", "=", r"\frac{\pi^2}{6}", size=60).move_to(UP * 0.6)
        res[2].set_color(YELLOW_)
        q = zh("π 从哪里来？", 44, YELLOW_, bold=True).next_to(res, DOWN, buff=0.7)

        D = self.say(0)
        self.play(FadeIn(res), run_time=0.9)
        self.play(Indicate(res[2], color=YELLOW_, scale_factor=1.4), FadeIn(q, shift=0.2 * UP), run_time=1.2)
        key = zh("关键：sin x 的零点", 36, PINK, bold=True).move_to(q)
        self.play(ReplacementTransform(q, key), run_time=max(0.6, min(1.0, self.remaining())))
        self.hold()

        # unit circle + traced sine
        D = self.say(1)
        R = 1.45
        center = np.array([-4.6, 0.35, 0])
        circ = Circle(radius=R, color=GREY_, stroke_width=2).move_to(center)
        cx = Line(center + LEFT * (R + 0.3), center + RIGHT * (R + 0.3), color=GREY_, stroke_width=1.5)
        axes = Axes(x_range=[0, 2 * np.pi + 0.3, np.pi], y_range=[-1.2, 1.2, 1], x_length=(2 * np.pi + 0.3) * R * 0.78,
                    y_length=2.4 * R, axis_config={"color": GREY_, "stroke_width": 2}, tips=False)
        axes.shift(center - axes.c2p(0, 0) + RIGHT * 2.6)
        theta = ValueTracker(0.0)
        pt = lambda: center + R * np.array([np.cos(theta.get_value()), np.sin(theta.get_value()), 0])
        dot = always_redraw(lambda: Dot(pt(), color=YELLOW_, radius=0.09))
        radius = always_redraw(lambda: Line(center, pt(), color=WHITE, stroke_width=2))
        height = always_redraw(lambda: Line([pt()[0], center[1], 0], pt(), color=YELLOW_, stroke_width=4))
        arc = always_redraw(lambda: Arc(radius=R, start_angle=0, angle=max(theta.get_value(), 1e-4),
                                        color=ORANGE_, stroke_width=6, arc_center=center))
        trace = always_redraw(lambda: axes.plot(
            lambda t: np.sin(t), x_range=[0, max(theta.get_value(), 1e-3), 0.01], color=YELLOW_, stroke_width=4))
        link = always_redraw(lambda: DashedLine(pt(), axes.c2p(theta.get_value(), np.sin(theta.get_value())),
                                                color=GREY_, stroke_width=1.5, dash_length=0.08))
        sin_lab = tex(r"y=\sin\theta", size=38, color=YELLOW_).next_to(axes, UP, buff=0.1).align_to(axes, RIGHT)
        self.play(FadeOut(res), FadeOut(key), run_time=0.6)
        self.play(Create(circ), Create(cx), Create(axes), FadeIn(sin_lab), run_time=1.2)
        self.add(arc, radius, height, trace, link, dot)
        self.play(theta.animate.set_value(PI / 2), run_time=max(1.0, self.remaining()), rate_func=linear)
        self.hold()

        D = self.say(2)
        self.play(theta.animate.set_value(PI), run_time=0.45 * D, rate_func=linear)
        arc_lab = VGroup(zh("弧长", 30, ORANGE_), tex(r"=\pi", size=38, color=ORANGE_)).arrange(RIGHT, buff=0.12)
        arc_lab.next_to(circ, UP, buff=0.2)
        z0 = Dot(axes.c2p(0, 0), color=PINK, radius=0.09)
        z1 = Dot(axes.c2p(np.pi, 0), color=PINK, radius=0.09)
        self.play(FadeIn(arc_lab), GrowFromCenter(z0), GrowFromCenter(z1), run_time=0.7)
        self.play(theta.animate.set_value(2 * PI), run_time=max(0.8, self.remaining() - 0.1), rate_func=linear)
        z2 = Dot(axes.c2p(2 * np.pi, 0), color=PINK, radius=0.09)
        zl = VGroup(tex("0", size=30, color=PINK).next_to(z0, DL, buff=0.08),
                    tex(r"\pi", size=30, color=PINK).next_to(z1, DOWN, buff=0.15),
                    tex(r"2\pi", size=30, color=PINK).next_to(z2, DOWN, buff=0.15))
        self.play(GrowFromCenter(z2), FadeIn(zl), run_time=0.5)
        self.hold()

        D = self.say(3)
        still = VGroup(circ, cx, axes, sin_lab, arc_lab, z0, z1, z2, zl, arc, radius, height, trace, link, dot)
        for m in (arc, radius, height, trace, link, dot):
            m.clear_updaters()
        self.play(still.animate.scale(0.5).to_edge(UP, buff=0.25), run_time=1.0)
        r1 = tex(r"\sin x = 0", r"\iff", r"x = n\pi", size=50).move_to([0, 1.25, 0])
        r1[2].set_color(PINK)
        self.play(Write(r1), run_time=1.2)
        self.wait(max(0, 0.25 * D - 2.2))
        r2 = tex(r"n\pi\ \Rightarrow\ ", r"\frac{1}{(n\pi)^2}", "=", r"\frac{1}{\pi^2}",
                 r"\cdot", r"\frac{1}{n^2}", size=50)
        r2_lab = zh("每个零点", 32, GREY_)
        VGroup(r2_lab, r2).arrange(RIGHT, buff=0.3).move_to([0, -0.2, 0])
        r2[1].set_color(PINK)
        r2[3].set_color(YELLOW_)
        r2[5].set_color(BLUE_)
        self.play(FadeIn(r2_lab), FadeIn(r2[:2], shift=0.2 * DOWN), run_time=1.0)
        self.play(FadeIn(r2[2:], shift=0.2 * LEFT), run_time=1.0)
        self.play(Indicate(r2[3], color=YELLOW_, scale_factor=1.5), run_time=1.0)
        self.wait(max(0, 0.7 * D - (self.time - (self._end - D)) - 0.3))
        r3 = tex(r"\sin x = x - \frac{x^3}{", "3!", r"}+\cdots", r"\qquad", "3!", "=", "6", size=50)
        r3.move_to([0, -1.75, 0])
        r3[1].set_color(ORANGE_)
        r3[4].set_color(ORANGE_)
        r3[6].set_color(ORANGE_)
        self.play(Write(r3), run_time=max(0.8, min(1.6, self.remaining() - 0.3)))
        self.hold()

        D = self.say(4)
        self.play(FadeOut(VGroup(still, r1, r2_lab, r2, r3)), run_time=0.7)
        res2 = tex(r"\sum_{n=1}^{\infty}\frac{1}{n^2}", "=", r"\frac{\pi^2}{6}", size=72).move_to(UP * 0.35)
        res2[2].set_color(YELLOW_)
        ring = Circle(radius=2.35, color=YELLOW_, stroke_width=3).move_to(res2)
        self.play(FadeIn(res2, scale=0.9), run_time=0.8)
        self.play(Create(ring), run_time=max(1.0, self.remaining() - 0.2))
        self.hold()

        D = self.say(5)
        self.play(VGroup(res2, ring).animate.scale(0.5).to_edge(UP, buff=0.3), run_time=0.8)

        # card 1: Fourier series (square wave built from sines)
        fa = Axes(x_range=[0, 2 * np.pi, np.pi], y_range=[-1.3, 1.3, 1], x_length=3.6, y_length=1.8,
                  axis_config={"color": GREY_, "stroke_width": 1.5}, tips=False)
        sq = lambda t: sum(4 / (np.pi * k) * np.sin(k * t) for k in range(1, 16, 2))
        fg = fa.plot(sq, x_range=[0, 2 * np.pi, 0.01], color=BLUE_, stroke_width=3)
        card1 = VGroup(VGroup(fa, fg), zh("傅里叶级数", 30, bold=True), Text("Fourier series", font_size=22, color=GREY_))
        card1.arrange(DOWN, buff=0.25)
        # card 2: lighthouses around a circular lake
        lake = Circle(radius=1.0, color=BLUE_, stroke_width=2, fill_color=BLUE_, fill_opacity=0.08)
        lights = VGroup(*[Dot(lake.point_at_angle(a), radius=0.07, color=YELLOW_) for a in np.linspace(0, TAU, 9)[:-1]])
        glows = VGroup(*[Dot(l.get_center(), radius=0.16, color=YELLOW_, fill_opacity=0.25) for l in lights])
        obs = Dot(lake.get_center() + DOWN * 0.35, radius=0.06, color=WHITE)
        card2 = VGroup(VGroup(lake, glows, lights, obs), zh("灯塔与光", 30, bold=True),
                       Text("lighthouses & light", font_size=22, color=GREY_))
        card2.arrange(DOWN, buff=0.25)
        cards = VGroup(card1, card2).arrange(RIGHT, buff=2.2).move_to(DOWN * 0.35)
        self.play(FadeIn(card1, shift=0.2 * UP), run_time=1.0)
        self.play(FadeIn(card2, shift=0.2 * UP), run_time=1.0)
        n1 = VGroup(zh("周期", 26, YELLOW_), tex(r"2\pi", size=34, color=YELLOW_)).arrange(RIGHT, buff=0.12)
        n1.next_to(card1, DOWN, buff=0.25)
        n2 = zh("灯塔排在圆周上", 26, YELLOW_).next_to(card2, DOWN, buff=0.25)
        self.wait(max(0, 0.55 * D - 2.8))
        self.play(FadeIn(n1, shift=0.1 * UP), FadeIn(n2, shift=0.1 * UP), Indicate(lights, color=WHITE),
                  run_time=max(0.8, min(1.4, self.remaining())))
        self.finish(extra=0.6)


# ---------------------------------------------------------------------------
class S08Rigor(VScene):
    KEY = "rigor"

    def construct(self):
        self.wait(0.2)
        prod = tex(r"\frac{\sin x}{x}", r"\overset{?}{=}", r"\prod_{n=1}^{\infty}\left(1-\frac{x^2}{n^2\pi^2}\right)", size=60)
        prod[0].set_color(BLUE_)
        prod[1].set_color(PINK)
        prod.move_to(UP * 2.25)
        warn = zh("无穷乘积也能像多项式一样按根分解吗？", 32, PINK).next_to(prod, DOWN, buff=0.35)

        D = self.say(0)
        self.play(Write(prod), run_time=1.6)
        self.play(FadeIn(warn, shift=0.15 * UP), run_time=0.9)
        self.hold()

        D = self.say(1)
        chk = VGroup(
            tex(r"\sum_{n=1}^{\infty}\frac{1}{n^2} = 1.644934\ldots", size=44),
            tex(r"\frac{\pi^2}{6} = 1.644934\ldots", size=44),
        ).arrange(RIGHT, buff=1.2).move_to(DOWN * 0.45)
        tick1 = tex(r"\checkmark", size=52, color=GREEN_).next_to(chk, RIGHT, buff=0.35)
        self.play(FadeIn(chk, shift=0.15 * UP), run_time=1.0)
        self.play(FadeIn(tick1, scale=1.5), run_time=0.6)
        self.wait(max(0, 0.4 * D - 1.6))
        y1741 = VGroup(Text("1741", font_size=34, color=YELLOW_, weight=BOLD),
                       zh("欧拉给出不依赖无穷乘积的新证明", 30)).arrange(RIGHT, buff=0.35)
        y1741.move_to(DOWN * 1.65)
        self.play(FadeIn(y1741, shift=0.15 * UP), run_time=1.0)
        self.hold()

        D = self.say(2)
        w = VGroup(Text("1876", font_size=34, color=GREEN_, weight=BOLD),
                   zh("魏尔斯特拉斯因式分解定理", 30, GREEN_, bold=True)).arrange(RIGHT, buff=0.35)
        w.move_to(DOWN * 2.45)
        self.play(FadeIn(w, shift=0.15 * UP), run_time=1.0)
        eq = tex("=", size=60, color=GREEN_).move_to(prod[1])
        self.play(ReplacementTransform(prod[1], eq), warn.animate.set_opacity(0.3), run_time=1.0)
        box = SurroundingRectangle(VGroup(prod[0], eq, prod[2]), color=GREEN_, buff=0.2, corner_radius=0.1)
        self.play(Create(box), run_time=0.8)
        self.finish(extra=0.5)


# ---------------------------------------------------------------------------
class S09Legacy(VScene):
    KEY = "legacy"

    def construct(self):
        self.wait(0.2)
        rows = VGroup(
            tex(r"\sum \frac{1}{n^2}", "=", r"\frac{\pi^2}{6}", size=46),
            tex(r"\sum \frac{1}{n^4}", "=", r"\frac{\pi^4}{90}", size=46),
            tex(r"\sum \frac{1}{n^6}", "=", r"\frac{\pi^6}{945}", size=46),
            tex(r"\vdots", size=46),
            tex(r"\sum \frac{1}{n^{12}}", "=", r"\frac{691\,\pi^{12}}{638512875}", size=46),
        ).arrange(DOWN, buff=0.3, aligned_edge=LEFT).move_to([-3.4, 0.45, 0])
        rows[3].shift(RIGHT * 0.5)
        for r in rows:
            if len(r) == 3:
                r[2].set_color(YELLOW_)

        D = self.say(0)
        self.play(FadeIn(rows[0]), run_time=0.8)
        self.wait(max(0, 0.25 * D - 0.8))
        self.play(FadeIn(rows[1], shift=0.15 * DOWN), run_time=0.9)
        self.play(FadeIn(rows[2], shift=0.15 * DOWN), run_time=0.8)
        self.play(FadeIn(rows[3:], shift=0.15 * DOWN), run_time=max(0.8, min(1.4, self.remaining())))
        self.hold()

        D = self.say(1)
        odd = tex(r"\sum \frac{1}{n^3}", "=", r"1.2020569\ldots", "=", r"\ ?", size=50).move_to([3.4, 0.9, 0])
        odd[4].set_color(PINK)
        tag = zh("奇数次方：至今没有已知的简洁公式", 26, PINK).next_to(odd, DOWN, buff=0.35)
        self.play(FadeIn(odd[:3]), run_time=1.0)
        self.play(FadeIn(odd[3:], scale=1.4), FadeIn(tag), run_time=0.9)
        self.hold()

        D = self.say(2)
        zeta = tex(r"\zeta(s)", "=", r"\sum_{n=1}^{\infty}\frac{1}{n^{s}}", size=64)
        zeta[0].set_color(GREEN_)
        zeta.move_to(UP * 1.6)
        rie = VGroup(zh("黎曼", 30, bold=True), Text("Riemann, 1859", font_size=26, color=GREY_)).arrange(RIGHT, buff=0.3)
        rie.next_to(zeta, DOWN, buff=0.35)
        primes = tex(r"2,\ 3,\ 5,\ 7,\ 11,\ 13,\ 17,\ 19,\ 23,\ 29,\ \ldots", size=46, color=BLUE_).move_to(DOWN * 1.2)
        plab = zh("素数的分布", 28, BLUE_).next_to(primes, DOWN, buff=0.3)
        self.play(FadeOut(VGroup(rows, odd, tag)), run_time=0.7)
        self.play(Write(zeta), FadeIn(rie), run_time=1.6)
        self.play(FadeIn(primes, lag_ratio=0.1), FadeIn(plab), run_time=max(1.0, min(2.0, self.remaining())))
        self.hold()

        D = self.say(3)
        self.play(FadeOut(VGroup(zeta, rie, primes, plab)), run_time=0.6)
        cols, rws, sp = 24, 14, 0.26
        dots = VGroup()
        cop = 0
        for j in range(1, rws + 1):
            for i in range(1, cols + 1):
                ok = gcd(i, j) == 1
                cop += ok
                dots.add(Dot([(i - 1) * sp, (j - 1) * sp, 0], radius=0.065,
                              color=GREEN_ if ok else GREY_, fill_opacity=1 if ok else 0.25))
        dots.move_to([-3.6, 0.1, 0])
        axlab = VGroup(tex("a", size=34, color=GREY_).next_to(dots, DOWN, buff=0.15),
                       tex("b", size=34, color=GREY_).next_to(dots, LEFT, buff=0.15))
        frac = cop / (cols * rws)
        prob = VGroup(zh("两个正整数 a、b 互质的概率", 30),
                      tex("=", r"\frac{6}{\pi^2}", r"\approx 60.8\%", size=54))
        prob[1][1].set_color(YELLOW_)
        prob.arrange(DOWN, aligned_edge=LEFT, buff=0.35).move_to([3.5, 0.9, 0])
        here = zh(f"图中 {cols}×{rws} 个点：互质占 {frac * 100:.1f}%", 26, GREEN_).next_to(prob, DOWN, buff=0.45)
        here.align_to(prob, LEFT)
        self.play(LaggedStart(*[FadeIn(d) for d in dots], lag_ratio=0.004), FadeIn(axlab), run_time=2.2)
        self.play(Write(prob), run_time=1.6)
        self.play(FadeIn(here, shift=0.15 * UP), run_time=max(0.6, min(1.0, self.remaining())))
        self.finish(extra=0.6)


# ---------------------------------------------------------------------------
class S10Outro(VScene):
    KEY = "outro"

    def construct(self):
        self.wait(0.2)
        ints = tex(r"1,\ 2,\ 3,\ 4,\ 5,\ \ldots", size=56, color=BLUE_).move_to([-4.2, 1.1, 0])
        circle = Circle(radius=1.1, color=YELLOW_, stroke_width=4).move_to([4.2, 1.1, 0])
        pi_in = tex(r"\pi", size=64, color=YELLOW_).move_to(circle)
        arrow = Arrow(ints.get_right() + RIGHT * 0.3, circle.get_left() + LEFT * 0.3, color=GREY_, buff=0)

        D = self.say(0)
        self.play(FadeIn(ints, shift=0.2 * RIGHT), run_time=1.0)
        self.play(GrowArrow(arrow), Create(circle), FadeIn(pi_in), run_time=max(1.2, min(2.0, self.remaining())))
        self.hold()

        D = self.say(1)
        final = tex(r"1+\frac{1}{4}+\frac{1}{9}+\frac{1}{16}+\cdots", "=", r"\frac{\pi^2}{6}", size=76)
        final[2].set_color(YELLOW_)
        final.move_to(DOWN * 1.35)
        self.play(Write(final), run_time=1.6)
        title = zh("巴塞尔问题", 48, bold=True).to_edge(UP, buff=0.55)
        self.play(FadeIn(title), run_time=0.8)
        self.hold(1.4)
        self.play(FadeOut(VGroup(ints, circle, pi_in, arrow, title)), final.animate.move_to(ORIGIN), run_time=1.0)
        self.wait(1.2)
        self.play(FadeOut(final), run_time=1.0)
        self.wait(0.4)
