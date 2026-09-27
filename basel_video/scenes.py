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
        ints = tex(r"1,\ 2,\ 3,\ 4,\ \ldots", size=48, color=BLUE_).next_to(ring, LEFT, buff=1.6)
        link = tex(r"\overset{?}{\longleftrightarrow}", size=56, color=GREY_).move_to(
            (ints.get_right() + ring.get_left()) / 2)
        self.play(FadeIn(ints, shift=0.2 * RIGHT), FadeIn(link), run_time=max(0.8, min(1.4, self.remaining())))
        self.hold()

        D = self.say(3)
        title = zh("巴塞尔问题", 84, bold=True).to_edge(UP, buff=0.7)
        sub = Text("The Basel Problem", font_size=36, color=GREY_).next_to(title, DOWN, buff=0.25)
        self.play(FadeIn(title, shift=0.3 * DOWN), FadeIn(sub), FadeOut(VGroup(ints, link)),
                  VGroup(pi, ring).animate.scale(0.8).move_to(UP * 0.1), run_time=1.0)
        routes = VGroup(
            VGroup(zh("欧拉的路", 32, BLUE_, bold=True), zh("正弦函数的零点", 26, GREY_)).arrange(DOWN, buff=0.12),
            VGroup(zh("直观的路", 32, YELLOW_, bold=True), zh("灯塔与越变越大的圆", 26, GREY_)).arrange(DOWN, buff=0.12),
        ).arrange(RIGHT, buff=3.2).move_to(DOWN * 2.05)
        self.play(FadeIn(routes[0], shift=0.2 * UP), run_time=0.8)
        self.wait(max(0, 0.35 * D - 1.8))
        self.play(FadeIn(routes[1], shift=0.2 * UP), run_time=0.8)
        self.finish(extra=0.5)


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




# ===========================================================================
# Shared pieces for the "why pi" and lighthouse chapters
# ===========================================================================
def lighthouse(point, scale=1.0, color=YELLOW_):
    """A glowing light source drawn as concentric translucent discs."""
    g = VGroup()
    for r, op in ((0.42, 0.05), (0.31, 0.08), (0.22, 0.13), (0.14, 0.22)):
        g.add(Circle(radius=r * scale, stroke_width=0, fill_color=color, fill_opacity=op))
    g.add(Dot(radius=0.07 * scale, color=color))
    g.move_to(point)
    return g


def observer(point, label=True):
    dot = Dot(point, radius=0.09, color=WHITE)
    if not label:
        return VGroup(dot)
    return VGroup(dot, zh("你", 26).next_to(dot, DOWN, buff=0.12))


def lake_xy(L, s):
    """Point at arc length s (counter-clockwise) from the observer O=(0,0) on a
    circle of circumference L that sits on top of O."""
    r = L / TAU
    th = s / r
    return np.array([r * np.sin(th), r - r * np.cos(th), 0.0])


def lake_circle(L, O, z, **kw):
    r = L / TAU
    style = dict(color=BLUE_, stroke_width=2.5)
    style.update(kw)
    return Circle(radius=r * z, **style).move_to(O + z * np.array([0, r, 0]))


def odd_positions(L):
    """Lighthouse arc positions after the circle has grown to circumference L."""
    return [s for s in np.arange(1, L, 2)]


# ---------------------------------------------------------------------------
class S07Radian(VScene):
    KEY = "radian"

    def construct(self):
        self.wait(0.2)
        head = zh("π 是从哪一步混进来的？", 40, bold=True).to_edge(UP, buff=0.45)
        f = tex(r"\frac{\sin x}{x}", "=", r"\left(1-\frac{x^2}{\pi^2}\right)", r"\left(1-\frac{x^2}{4\pi^2}\right)",
                r"\left(1-\frac{x^2}{9\pi^2}\right)", r"\cdots", size=52).move_to(UP * 0.9)
        zline = tex(r"\sin x = 0", r"\iff", r"x = 0,\ \pm\pi,\ \pm 2\pi,\ \pm 3\pi,\ \ldots", size=50).move_to(DOWN * 0.9)
        zline[2].set_color(PINK)

        D = self.say(0)
        self.play(FadeIn(head, shift=0.2 * DOWN), FadeIn(f), run_time=1.0)
        self.play(*[Indicate(f[i], color=PINK, scale_factor=1.08) for i in (2, 3, 4)], run_time=1.2)
        self.play(FadeIn(zline, shift=0.2 * UP), run_time=max(0.8, min(1.4, self.remaining())))
        self.hold()

        # --- radians: angle = arc length on the unit circle
        D = self.say(1)
        R = 1.55
        C = np.array([-4.2, 0.2, 0])
        circ = Circle(radius=R, color=GREY_, stroke_width=2.5).move_to(C)
        hline = Line(C + LEFT * (R + 0.35), C + RIGHT * (R + 0.35), color=GREY_, stroke_width=1.5)
        rlab = tex("1", size=34, color=GREY_).next_to(Line(C, C + RIGHT * R), DOWN, buff=0.1)
        ang = ValueTracker(1.0)
        arc = always_redraw(lambda: Arc(radius=R, start_angle=0, angle=max(ang.get_value(), 1e-3), arc_center=C,
                                        color=ORANGE_, stroke_width=7))
        r0 = Line(C, C + RIGHT * R, color=WHITE, stroke_width=2)
        r1 = always_redraw(lambda: Line(C, C + R * np.array([np.cos(ang.get_value()), np.sin(ang.get_value()), 0]),
                                        color=WHITE, stroke_width=2))
        self.play(FadeOut(VGroup(head, f, zline)), run_time=0.6)
        self.play(Create(circ), Create(hline), Create(r0), FadeIn(rlab), run_time=1.0)
        self.add(arc, r1)
        rule = VGroup(zh("角的大小", 34), tex("=", size=44), zh("对应的弧长", 34, ORANGE_)).arrange(RIGHT, buff=0.2)
        rule.move_to([2.6, 2.3, 0])
        sub = zh("单位圆：半径 = 1", 26, GREY_).next_to(rule, DOWN, buff=0.25)
        self.play(FadeIn(rule), FadeIn(sub), run_time=0.9)
        t = max(1.2, 0.3 * D)
        self.play(ang.animate.set_value(TAU - 1e-3), run_time=t, rate_func=smooth)
        full = VGroup(zh("转动一整圈", 34), tex(r"=2\pi", size=46, color=ORANGE_)).arrange(RIGHT, buff=0.2)
        full.move_to([2.6, 0.7, 0])
        self.play(FadeIn(full, shift=0.15 * UP), run_time=0.8)
        self.play(ang.animate.set_value(PI), run_time=1.2)
        half = VGroup(zh("转动半圈", 34), tex(r"=\pi", size=46, color=YELLOW_)).arrange(RIGHT, buff=0.2)
        half.next_to(full, DOWN, buff=0.45).align_to(full, LEFT)
        self.play(FadeIn(half, shift=0.15 * UP), run_time=max(0.6, min(1.0, self.remaining())))
        self.hold()

        # --- a point on the circle, its height, and the traced sine
        D = self.say(2)
        axes = Axes(x_range=[0, 3 * np.pi + 0.3, np.pi], y_range=[-1.25, 1.25, 1],
                    x_length=(3 * np.pi + 0.3) * 0.82, y_length=2.5 * R,
                    axis_config={"color": GREY_, "stroke_width": 2}, tips=False)
        axes.shift(C - axes.c2p(0, 0) + RIGHT * (R + 0.9))
        th = ValueTracker(0.0)
        P = lambda: C + R * np.array([np.cos(th.get_value()), np.sin(th.get_value()), 0])
        dot = always_redraw(lambda: Dot(P(), color=YELLOW_, radius=0.1))
        rad = always_redraw(lambda: Line(C, P(), color=WHITE, stroke_width=2))
        height = always_redraw(lambda: Line([P()[0], C[1], 0], P(), color=YELLOW_, stroke_width=5))
        trace = always_redraw(lambda: axes.plot(np.sin, x_range=[0, max(th.get_value(), 1e-3), 0.01],
                                                color=YELLOW_, stroke_width=4))
        link = always_redraw(lambda: DashedLine(P(), axes.c2p(th.get_value(), np.sin(th.get_value())),
                                                color=GREY_, stroke_width=1.5, dash_length=0.08))
        lab = VGroup(zh("高度", 28, YELLOW_), tex(r"=\sin\theta", size=38, color=YELLOW_)).arrange(RIGHT, buff=0.1)
        lab.next_to(axes, UP, buff=0.15).align_to(axes, RIGHT)
        self.play(FadeOut(VGroup(rule, sub, full, half, rlab, r0)), FadeOut(arc), FadeOut(r1), run_time=0.6)
        self.play(Create(axes), FadeIn(lab), run_time=0.8)
        self.add(rad, height, trace, link, dot)
        self.play(th.animate.set_value(PI / 2), run_time=max(1.0, self.remaining()), rate_func=linear)
        self.hold()

        # --- height is zero only at the two ends of the horizontal diameter
        D = self.say(3)
        e0 = Dot(C + RIGHT * R, color=PINK, radius=0.11)
        e1 = Dot(C + LEFT * R, color=PINK, radius=0.11)
        diam = Line(C + LEFT * R, C + RIGHT * R, color=PINK, stroke_width=4)
        l0 = zh("出发点", 24, PINK).next_to(e0, DOWN, buff=0.14)
        l1 = zh("正对面", 24, PINK).next_to(e1, DOWN, buff=0.14)
        self.play(Create(diam), run_time=0.8)
        self.play(GrowFromCenter(e0), GrowFromCenter(e1), FadeIn(l0), FadeIn(l1), run_time=0.9)
        self.play(th.animate.set_value(PI), run_time=max(1.0, self.remaining() - 0.2), rate_func=linear)
        self.hold()

        # --- zeros every pi
        D = self.say(4)
        half_arc = Arc(radius=R, start_angle=0, angle=PI, arc_center=C, color=ORANGE_, stroke_width=7)
        hl = VGroup(zh("半圈", 26, ORANGE_), tex(r"=\pi", size=36, color=ORANGE_)).arrange(RIGHT, buff=0.1)
        hl.next_to(circ, UP, buff=0.18)
        self.play(Create(half_arc), FadeIn(hl), run_time=1.0)
        zeros = VGroup(*[Dot(axes.c2p(k * np.pi, 0), color=PINK, radius=0.1) for k in range(4)])
        zl = VGroup(*[tex(s, size=34, color=PINK).next_to(axes.c2p(k * np.pi, 0), DOWN, buff=0.22)
                      for k, s in enumerate(["0", r"\pi", r"2\pi", r"3\pi"])])
        zl[0].shift(RIGHT * 0.2)
        self.play(GrowFromCenter(zeros[0]), GrowFromCenter(zeros[1]), FadeIn(zl[:2]), run_time=0.7)
        t = max(2.0, self.remaining() - 0.6)
        self.play(th.animate.set_value(2 * PI), run_time=t / 2, rate_func=linear)
        self.add(zeros[2], zl[2])
        self.play(th.animate.set_value(3 * PI), run_time=t / 2, rate_func=linear)
        self.play(GrowFromCenter(zeros[3]), FadeIn(zl[3]), run_time=0.4)
        self.hold()

        # --- zeros are the integers times pi
        D = self.say(5)
        for m in (rad, height, trace, link, dot):
            m.clear_updaters()
        ints = VGroup(*[tex(str(k), size=40, color=BLUE_).move_to(zl[k].get_center() + DOWN * 1.15) for k in range(4)])
        arrows = VGroup(*[Arrow(ints[k].get_top(), zl[k].get_bottom(), buff=0.1, color=GREY_, stroke_width=3,
                                max_tip_length_to_length_ratio=0.25) for k in range(4)])
        times = tex(r"\times\pi", size=36, color=YELLOW_).next_to(arrows[3], RIGHT, buff=0.2)
        self.play(LaggedStart(*[FadeIn(i, shift=0.1 * UP) for i in ints], lag_ratio=0.2), run_time=1.2)
        self.play(LaggedStart(*[GrowArrow(a) for a in arrows], lag_ratio=0.15), FadeIn(times), run_time=1.2)
        note = zh("整数 × π  =  圆每转动半圈的位置", 30, YELLOW_).move_to(DOWN * 2.55)
        self.wait(max(0, 0.55 * D - 2.4))
        self.play(FadeIn(note, shift=0.15 * UP), run_time=max(0.6, min(1.0, self.remaining())))
        self.finish(extra=0.5)


# ---------------------------------------------------------------------------
class S08Squared(VScene):
    KEY = "squared"

    def construct(self):
        self.wait(0.2)
        prod = tex(r"\frac{\sin x}{x}", "=", r"\prod_{n=1}^{\infty}\left(1-\frac{x^2}{(n\pi)^2}\right)", size=54)
        prod[0].set_color(BLUE_)
        prod.move_to(UP * 2.35)
        lab = zh("x² 的系数：", 32, GREY_)
        c1 = tex(r"-\sum_{n=1}^{\infty}\frac{1}{(n\pi)^2}", size=56)
        row = VGroup(lab, c1).arrange(RIGHT, buff=0.3).move_to(UP * 0.35)

        D = self.say(0)
        self.play(Write(prod), run_time=1.6)
        self.wait(max(0, 0.45 * D - 1.6))
        self.play(FadeIn(row, shift=0.2 * DOWN), run_time=1.2)
        self.hold()

        D = self.say(1)
        c2 = tex("-", r"\frac{1}{\pi^2}", r"\sum_{n=1}^{\infty}\frac{1}{n^2}", size=56)
        c2[1].set_color(YELLOW_)
        c2[2].set_color(BLUE_)
        c2.move_to(c1, LEFT)
        self.play(Indicate(c1, color=YELLOW_, scale_factor=1.08), run_time=1.0)
        self.play(TransformMatchingShapes(c1, c2), run_time=1.4)
        brace = Brace(c2[2], DOWN, color=BLUE_)
        bl = zh("巴塞尔和", 28, BLUE_).next_to(brace, DOWN, buff=0.12)
        self.play(GrowFromCenter(brace), FadeIn(bl), run_time=max(0.7, min(1.2, self.remaining())))
        self.hold()

        # --- why squared: zeros come in +/- pairs
        D = self.say(2)
        self.play(FadeOut(VGroup(prod, row, c2, brace, bl)), run_time=0.6)
        nl = NumberLine(x_range=[-3.5, 3.5, 1], length=9, color=GREY_, include_ticks=False).move_to(UP * 2.0)
        zs = VGroup()
        for k in (1, 2, 3):
            for sg in (1, -1):
                zs.add(Dot(nl.n2p(sg * k), color=PINK, radius=0.09))
        zlab = VGroup(*[tex(("-" if sg < 0 else "") + ("" if k == 1 else str(k)) + r"\pi", size=32, color=PINK)
                        .next_to(nl.n2p(sg * k), DOWN, buff=0.2) for k in (1, 2, 3) for sg in (1, -1)])
        arcs = VGroup(*[ArcBetweenPoints(nl.n2p(-k), nl.n2p(k), angle=-PI * 0.5, color=c, stroke_width=3)
                        .shift(UP * 0.08) for k, c in zip((1, 2, 3), (YELLOW_, ORANGE_, PURPLE_))])
        self.play(Create(nl), LaggedStart(*[GrowFromCenter(z) for z in zs], lag_ratio=0.1), FadeIn(zlab), run_time=1.2)
        self.play(LaggedStart(*[Create(a) for a in arcs], lag_ratio=0.3), run_time=1.2)
        e1 = tex(r"\left(1-\frac{x}{n\pi}\right)\left(1+\frac{x}{n\pi}\right)", "=", "1", r"-\frac{x}{n\pi}",
                 r"+\frac{x}{n\pi}", r"-\frac{x^2}{(n\pi)^2}", size=50).move_to(DOWN * 0.3)
        self.play(Write(e1), run_time=1.8)
        s1 = Line(e1[3].get_corner(DL), e1[3].get_corner(UR), color=PINK, stroke_width=4)
        s2 = Line(e1[4].get_corner(DL), e1[4].get_corner(UR), color=PINK, stroke_width=4)
        self.play(Create(s1), Create(s2), run_time=0.8)
        e2 = tex(r"=1-\frac{x^2}{(n\pi)^2}", size=54).next_to(e1, DOWN, buff=0.45).align_to(e1[1], LEFT)
        e2[0][3:].set_color(YELLOW_)
        self.play(FadeIn(e2, shift=0.15 * DOWN), run_time=max(0.7, min(1.2, self.remaining())))
        self.hold()

        # --- where the 6 comes from: how sine bends near 0
        D = self.say(3)
        self.play(FadeOut(VGroup(nl, zs, zlab, arcs, e1, s1, s2, e2)), run_time=0.6)
        ax = Axes(x_range=[-3.2, 3.2, 1], y_range=[-1.5, 1.5, 1], x_length=7.0, y_length=4.4,
                  axis_config={"color": GREY_, "stroke_width": 2}, tips=False).move_to([-3.0, 0.1, 0])
        g_sin = ax.plot(np.sin, x_range=[-3.2, 3.2], color=BLUE_, stroke_width=4)
        g_lin = ax.plot(lambda x: x, x_range=[-1.5, 1.5], color=GREY_, stroke_width=2)
        g_cub = ax.plot(lambda x: x - x ** 3 / 6, x_range=[-2.75, 2.75], color=ORANGE_, stroke_width=3)
        lsin = tex(r"\sin x", size=36, color=BLUE_).move_to(ax.c2p(2.4, 1.05))
        llin = tex("y=x", size=32, color=GREY_).move_to(ax.c2p(1.05, 1.45))
        self.play(Create(ax), Create(g_sin), FadeIn(lsin), run_time=1.2)
        self.play(Create(g_lin), FadeIn(llin), run_time=0.8)
        approx = tex(r"\sin x", r"\approx", "x", r"-\frac{x^3}{", "6", "}", size=58).move_to([3.6, 1.3, 0])
        approx[0].set_color(BLUE_)
        approx[3:].set_color(ORANGE_)
        self.play(Create(g_cub), Write(approx), run_time=1.6)
        fact = tex("6", "=", "3!", "=", r"1\times2\times3", size=48).next_to(approx, DOWN, buff=0.6)
        fact[0].set_color(ORANGE_)
        fact[2].set_color(ORANGE_)
        self.wait(max(0, 0.6 * D - 4.2))
        self.play(FadeIn(fact, shift=0.15 * UP), run_time=max(0.7, min(1.2, self.remaining())))
        self.hold()

        # --- reading the answer
        D = self.say(4)
        self.play(FadeOut(VGroup(ax, g_sin, g_lin, g_cub, lsin, llin, approx, fact)), run_time=0.6)
        big = tex(r"\sum_{n=1}^{\infty}\frac{1}{n^2}", "=", r"\frac{\pi^2}{6}", size=90).move_to([-1.8, 0.4, 0])
        self.play(FadeIn(big), run_time=0.9)
        frac = big[2]                      # glyphs: pi, 2, fraction bar, 6
        num, den = frac[:2], frac[3:]
        a1 = Arrow(num.get_right() + RIGHT * 1.9 + UP * 0.25, num.get_right() + RIGHT * 0.1, color=YELLOW_, buff=0.05)
        t1 = zh("零点的间距 π", 30, YELLOW_).next_to(a1.get_start(), RIGHT, buff=0.15)
        a2 = Arrow(den.get_right() + RIGHT * 1.9 + DOWN * 0.25, den.get_right() + RIGHT * 0.1, color=ORANGE_, buff=0.05)
        t2 = zh("曲线的弯曲 3!", 30, ORANGE_).next_to(a2.get_start(), RIGHT, buff=0.15)
        self.play(num.animate.set_color(YELLOW_), GrowArrow(a1), FadeIn(t1), run_time=1.0)
        self.play(den.animate.set_color(ORANGE_), GrowArrow(a2), FadeIn(t2), run_time=1.0)
        same = zh("两种描述，同一个函数 ⟹ 必须相等", 30, GREY_).move_to(DOWN * 2.1)
        self.wait(max(0, 0.55 * D - 2.9))
        self.play(FadeIn(same, shift=0.15 * UP), run_time=max(0.6, min(1.0, self.remaining())))
        self.hold()

        D = self.say(5)
        grp = VGroup(big, a1, t1, a2, t2, same)
        self.play(grp.animate.scale(0.55).set_opacity(0.35).to_edge(UP, buff=0.4), run_time=1.0)
        q = zh("能不能直接“看见”那个圆？", 44, YELLOW_, bold=True).move_to(DOWN * 0.6)
        ring = Circle(radius=1.6, color=YELLOW_, stroke_width=3, stroke_opacity=0.6).move_to(DOWN * 0.6)
        self.play(FadeIn(q, shift=0.2 * UP), Create(ring), run_time=max(1.2, min(2.0, self.remaining())))
        self.finish(extra=0.5)


# ---------------------------------------------------------------------------
class S09Light(VScene):
    KEY = "light"

    def construct(self):
        self.wait(0.2)
        t = zh("直观的证明：灯塔", 64, bold=True).move_to(UP * 1.2)
        who = VGroup(Text("Johan Wästlund, 2010", font_size=32, color=GREY_),
                     zh("瑞典数学家韦斯特伦德的几何证明", 28, GREY_)).arrange(DOWN, buff=0.18).next_to(t, DOWN, buff=0.5)
        yt = VGroup(Text("3Blue1Brown", font_size=30, color=BLUE_),
                    Text("“Why is pi here? And why is it squared?”", font_size=26, color=GREY_, slant=ITALIC)
                    ).arrange(DOWN, buff=0.14).next_to(who, DOWN, buff=0.5)

        D = self.say(0)
        self.play(FadeIn(t, shift=0.2 * DOWN), run_time=1.0)
        self.play(FadeIn(who), run_time=0.9)
        self.wait(max(0, 0.45 * D - 1.9))
        self.play(FadeIn(yt), run_time=0.9)
        self.hold()

        # --- inverse square law
        D = self.say(1)
        self.play(FadeOut(VGroup(t, who, yt)), run_time=0.6)
        u = 2.2
        O = np.array([-5.6, 0.6, 0])
        you = observer(O)
        pos = ValueTracker(1.0)
        lh = always_redraw(lambda: lighthouse(O + RIGHT * u * pos.get_value(), 1.3))
        dist = always_redraw(lambda: DoubleArrow(O + DOWN * 0.85, O + RIGHT * u * pos.get_value() + DOWN * 0.85,
                                                 buff=0, color=GREY_, stroke_width=2, tip_length=0.15))
        dlab = always_redraw(lambda: tex(rf"d={pos.get_value():.0f}", size=34, color=GREY_)
                             .next_to(dist, DOWN, buff=0.12))
        # brightness meter
        base = np.array([4.2, -1.6, 0])
        frame = Rectangle(width=0.9, height=3.4, color=GREY_, stroke_width=2).move_to(base + UP * 1.7)
        bar = always_redraw(lambda: Rectangle(width=0.9, height=max(3.4 / pos.get_value() ** 2, 0.01), stroke_width=0,
                                              fill_color=YELLOW_, fill_opacity=0.85)
                            .move_to(base + UP * 3.4 / pos.get_value() ** 2 / 2))
        mlab = zh("看到的亮度", 26, GREY_).next_to(frame, DOWN, buff=0.2)
        self.play(FadeIn(you), FadeIn(lh), Create(dist), FadeIn(dlab), Create(frame), FadeIn(bar), FadeIn(mlab),
                  run_time=1.0)
        self.wait(max(0, 0.35 * D - 1.0))
        self.play(pos.animate.set_value(2.0), run_time=1.8)
        q = VGroup(tex(r"d\times 2", size=40), tex(r"\Rightarrow", size=40),
                   zh("亮度", 30, YELLOW_), tex(r"\times\frac{1}{4}", size=40, color=YELLOW_)).arrange(RIGHT, buff=0.2)
        q.move_to([-1.2, 2.4, 0])
        self.play(FadeIn(q, shift=0.15 * DOWN), run_time=max(0.6, min(1.0, self.remaining())))
        self.hold()

        D = self.say(2)
        rule = VGroup(zh("亮度", 40, YELLOW_), tex(r"=\frac{1}{d^2}", size=64, color=YELLOW_)).arrange(RIGHT, buff=0.2)
        rule.move_to([-1.2, -1.9, 0])
        self.play(Write(rule), run_time=1.4)
        self.hold()

        # --- a row of lighthouses at 1, 2, 3, ...
        D = self.say(3)
        for m in (lh, dist, dlab, bar):
            m.clear_updaters()
        self.play(FadeOut(VGroup(lh, dist, dlab, bar, frame, mlab, q, rule, you)), run_time=0.6)
        u = 1.25
        O2 = np.array([-6.0, 0.4, 0])
        line = Line(O2 + LEFT * 0.3, O2 + RIGHT * 13.2, color=GREY_, stroke_width=2)
        you2 = observer(O2)
        ticks = VGroup(*[tex(str(k), size=30, color=GREY_).move_to(O2 + RIGHT * u * k + DOWN * 0.5) for k in range(1, 11)])
        lights = VGroup(*[lighthouse(O2 + RIGHT * u * k, max(0.45, 1.25 / k ** 0.6)) for k in range(1, 11)])
        dots = tex(r"\cdots", size=40, color=GREY_).move_to(O2 + RIGHT * u * 10.6 + UP * 0.1)
        self.play(Create(line), FadeIn(you2), run_time=0.8)
        self.play(LaggedStart(*[FadeIn(l, scale=0.6) for l in lights], lag_ratio=0.12), FadeIn(ticks), FadeIn(dots),
                  run_time=max(1.5, self.remaining() - 0.3))
        self.hold()

        D = self.say(4)
        vals = VGroup(*[tex(s, size=34, color=YELLOW_).move_to(O2 + RIGHT * u * k + UP * 1.0)
                        for k, s in zip(range(1, 6), ["1", r"\frac{1}{4}", r"\frac{1}{9}", r"\frac{1}{16}", r"\frac{1}{25}"])])
        self.play(LaggedStart(*[FadeIn(v, shift=0.1 * DOWN) for v in vals], lag_ratio=0.2), run_time=1.6)
        tot = VGroup(zh("总亮度", 34, YELLOW_),
                     tex(r"=1+\frac{1}{4}+\frac{1}{9}+\frac{1}{16}+\cdots", size=52)).arrange(RIGHT, buff=0.2)
        tot.move_to(DOWN * 1.35)
        self.play(FadeIn(tot, shift=0.15 * UP), run_time=1.0)
        ask = zh("这一排灯塔，到底有多亮？", 36, bold=True).next_to(tot, DOWN, buff=0.4)
        self.wait(max(0, 0.55 * D - 2.6))
        self.play(FadeIn(ask), run_time=max(0.6, min(1.0, self.remaining())))
        self.finish(extra=0.5)


# ---------------------------------------------------------------------------
class S10InvPyth(VScene):
    KEY = "invpyth"

    def construct(self):
        self.wait(0.2)
        A = np.array([-6.2, 1.9, 0])
        B = np.array([-0.6, 1.9, 0])
        M = (A + B) / 2
        rad = np.linalg.norm(B - A) / 2
        O = M + rad * np.array([np.cos(-2 * PI / 3), np.sin(-2 * PI / 3), 0])
        H = np.array([O[0], A[1], 0])
        tri = Polygon(O, A, B, color=WHITE, stroke_width=3)
        alt = DashedLine(O, H, color=GREEN_, stroke_width=3)
        ra = RightAngle(Line(O, A), Line(O, B), length=0.28, color=WHITE, quadrant=(1, 1))
        rh = RightAngle(Line(H, O), Line(H, B), length=0.22, color=GREEN_, quadrant=(1, 1))
        la = tex("a", size=40, color=BLUE_).move_to((O + A) / 2 + np.array([-0.3, -0.1, 0]))
        lb = tex("b", size=40, color=ORANGE_).move_to((O + B) / 2 + np.array([0.3, -0.2, 0]))
        lh = tex("h", size=40, color=GREEN_).move_to((O + H) / 2 + RIGHT * 0.25)
        lc = tex("c", size=40, color=GREY_).move_to(M + UP * 0.35)
        head = zh("逆勾股定理", 44, bold=True).move_to([3.3, 2.7, 0])

        D = self.say(0)
        self.play(FadeIn(head, shift=0.2 * DOWN), Create(tri), run_time=1.2)
        self.play(Create(ra), run_time=max(0.5, min(1.0, self.remaining())))
        self.hold()

        D = self.say(1)
        self.play(Create(alt), Create(rh), run_time=1.2)
        self.play(FadeIn(la), FadeIn(lb), FadeIn(lh), FadeIn(lc), run_time=0.9)
        thm = tex(r"\frac{1}{a^2}", "+", r"\frac{1}{b^2}", "=", r"\frac{1}{h^2}", size=66).move_to([3.3, 1.2, 0])
        thm[0].set_color(BLUE_)
        thm[2].set_color(ORANGE_)
        thm[4].set_color(GREEN_)
        self.wait(max(0, 0.55 * D - 2.1))
        self.play(Write(thm), run_time=max(1.0, min(1.8, self.remaining())))
        self.hold()

        D = self.say(2)
        shade = Polygon(O, A, B, stroke_width=0, fill_color=BLUE_, fill_opacity=0.18)
        area = VGroup(zh("面积算两次：", 28, GREY_), tex(r"ab = ch", size=46)).arrange(RIGHT, buff=0.2)
        area.move_to([3.3, -0.25, 0])
        self.play(FadeIn(shade), FadeIn(area), run_time=1.0)
        step = tex(r"\frac{1}{h^2}", "=", r"\frac{c^2}{a^2b^2}", "=", r"\frac{a^2+b^2}{a^2b^2}", "=",
                   r"\frac{1}{a^2}+\frac{1}{b^2}", size=44).move_to([3.3, -1.55, 0])
        if step.width > 7.2:
            step.scale_to_fit_width(7.2)
        self.wait(max(0, 0.3 * D - 1.0))
        self.play(FadeIn(step[:3], shift=0.1 * LEFT), run_time=1.0)
        self.wait(max(0, 0.7 * D - (self.time - (self._end - D)) - 1.0))
        self.play(FadeIn(step[3:], shift=0.1 * LEFT), run_time=max(0.8, min(1.4, self.remaining())))
        self.hold()

        # --- lighthouse reading
        D = self.say(3)
        self.play(FadeOut(VGroup(shade, area, step, lc)), run_time=0.6)
        you = observer(O)
        lH = lighthouse(H, 1.2)
        lA = lighthouse(A, 1.2)
        lB = lighthouse(B, 1.2)
        self.play(FadeIn(you), FadeIn(lH, scale=0.5), run_time=0.9)
        bars = VGroup()
        base_y = -2.55
        hgt = 2.2
        b1 = Rectangle(width=0.7, height=hgt, stroke_width=0, fill_color=GREEN_, fill_opacity=0.85)
        b1.move_to([1.6, base_y + hgt / 2, 0])
        fa = 1 / np.linalg.norm(A - O) ** 2
        fb = 1 / np.linalg.norm(B - O) ** 2
        fh = 1 / np.linalg.norm(H - O) ** 2
        b2a = Rectangle(width=0.7, height=hgt * fa / fh, stroke_width=0, fill_color=BLUE_, fill_opacity=0.85)
        b2b = Rectangle(width=0.7, height=hgt * fb / fh, stroke_width=0, fill_color=ORANGE_, fill_opacity=0.85)
        b2a.move_to([4.2, base_y + b2a.height / 2, 0])
        b2b.next_to(b2a, UP, buff=0)
        bl1 = VGroup(zh("垂足一座", 24, GREEN_), tex(r"\frac{1}{h^2}", size=34, color=GREEN_)).arrange(RIGHT, buff=0.1)
        bl1.next_to(b1, LEFT, buff=0.2)
        bl2 = VGroup(zh("两端两座", 24, GREY_), tex(r"\frac{1}{a^2}+\frac{1}{b^2}", size=34)).arrange(DOWN, buff=0.08)
        bl2.next_to(VGroup(b2a, b2b), RIGHT, buff=0.2)
        self.play(FadeOut(thm), GrowFromEdge(b1, DOWN), FadeIn(bl1), run_time=1.0)
        self.play(FadeIn(lA, scale=0.5), FadeIn(lB, scale=0.5), lH.animate.fade(0.65), run_time=0.9)
        self.play(GrowFromEdge(b2a, DOWN), run_time=0.6)
        self.play(GrowFromEdge(b2b, DOWN), FadeIn(bl2), run_time=0.6)
        eqbar = DashedLine([1.1, base_y + hgt, 0], [4.7, base_y + hgt, 0], color=YELLOW_, stroke_width=2)
        self.play(Create(eqbar), run_time=max(0.5, min(0.9, self.remaining())))
        self.hold()

        D = self.say(4)
        c1, c2 = lighthouse(H, 1.2), lighthouse(H, 1.2)
        self.remove(lA, lB)
        self.play(c1.animate.move_to(A), c2.animate.move_to(B), FadeOut(lH), run_time=1.6)
        motto = VGroup(zh("一座 → 两座", 36, YELLOW_, bold=True), zh("总亮度不变", 36, YELLOW_, bold=True)
                       ).arrange(DOWN, buff=0.15).move_to([3.3, 1.6, 0])
        self.play(FadeIn(motto, scale=1.1), run_time=max(0.6, min(1.0, self.remaining())))
        self.finish(extra=0.6)


# ---------------------------------------------------------------------------
class S11Lake(VScene):
    KEY = "lake"

    def construct(self):
        self.wait(0.2)
        O = np.array([-2.4, -2.45, 0])
        z = 3.55
        L1 = 2.0
        c1 = lake_circle(L1, O, z, fill_color=BLUE_, fill_opacity=0.12)
        T = O + z * lake_xy(L1, 1.0)
        you = observer(O)
        lT = lighthouse(T, 1.25)
        per1 = VGroup(zh("周长", 28, BLUE_), tex("=2", size=36, color=BLUE_)).arrange(RIGHT, buff=0.1)
        per1.next_to(c1, LEFT, buff=0.3)

        D = self.say(0)
        self.play(DrawBorderThenFill(c1), FadeIn(you), FadeIn(per1), run_time=1.4)
        self.play(FadeIn(lT, scale=0.5), run_time=max(0.6, min(1.2, self.remaining())))
        self.hold()

        D = self.say(1)
        diam = DashedLine(O, T, color=WHITE, stroke_width=2.5)
        dl = tex(r"d=\frac{2}{\pi}", size=40).next_to(diam, RIGHT, buff=0.12).shift(DOWN * 0.3)
        self.play(Create(diam), run_time=0.8)
        self.play(FadeIn(dl), run_time=0.7)
        bright = VGroup(zh("亮度", 34, YELLOW_), tex(r"=\frac{1}{d^2}=", size=54),
                        tex(r"\frac{\pi^2}{4}", size=60, color=YELLOW_)).arrange(RIGHT, buff=0.15)
        bright.move_to([3.7, 1.3, 0])
        self.wait(max(0, 0.35 * D - 1.5))
        self.play(Write(bright), run_time=1.3)
        here = zh("π 在这里出现：直径 = 周长 ÷ π", 28, YELLOW_).next_to(bright, DOWN, buff=0.35)
        self.play(FadeIn(here, shift=0.1 * UP), Indicate(dl, color=YELLOW_), run_time=max(0.6, min(1.2, self.remaining())))
        self.hold()

        # --- the doubled circle centred at the lighthouse
        D = self.say(2)
        L2 = 4.0
        c2 = lake_circle(L2, O, z, color=BLUE_, stroke_width=2.5)
        per2 = VGroup(zh("周长", 28, BLUE_), tex("=4", size=36, color=BLUE_)).arrange(RIGHT, buff=0.1)
        per2.next_to(c2, LEFT, buff=0.25).shift(UP * 1.0)
        cdot = Dot(T, radius=0.05, color=GREY_)
        self.play(Create(c2), FadeOut(per1), run_time=1.8)
        self.play(FadeIn(per2), FadeIn(cdot), run_time=max(0.5, min(0.9, self.remaining())))
        self.hold()

        D = self.say(3)
        Ap = O + z * lake_xy(L2, 1.0)
        Bp = O + z * lake_xy(L2, 3.0)
        chord = Line(Bp, Ap, color=GREEN_, stroke_width=3)
        oa = Line(O, Ap, color=WHITE, stroke_width=2.5)
        ob = Line(O, Bp, color=WHITE, stroke_width=2.5)
        ra = RightAngle(Line(O, Ap), Line(O, Bp), length=0.25, color=WHITE, quadrant=(1, 1))
        rt = RightAngle(Line(T, Ap), Line(T, O), length=0.2, color=GREEN_, quadrant=(1, 1))
        self.play(Create(chord), run_time=1.0)
        self.play(Create(oa), Create(ob), run_time=1.0)
        self.play(Create(ra), Create(rt), run_time=max(0.6, min(1.0, self.remaining() - 1.0)))
        self.hold()

        D = self.say(4)
        a1, a2 = lT.copy(), lT.copy()
        self.play(a1.animate.move_to(Ap), a2.animate.move_to(Bp), lT.animate.fade(0.8), run_time=1.6)
        still = VGroup(zh("总亮度", 30, YELLOW_), tex(r"=\frac{\pi^2}{4}", size=52, color=YELLOW_)).arrange(RIGHT, buff=0.15)
        still.move_to([3.7, -0.9, 0])
        self.play(FadeIn(still, shift=0.1 * UP), FadeOut(here), run_time=max(0.6, min(1.0, self.remaining())))
        self.hold()

        D = self.say(5)
        self.play(FadeOut(VGroup(oa, ob, ra, rt, chord, diam, dl)), run_time=0.6)
        r2 = L2 / TAU * z
        C2 = O + UP * r2
        arcR = Arc(radius=r2, start_angle=-PI / 2, angle=PI / 2, arc_center=C2, color=ORANGE_, stroke_width=7)
        arcL = Arc(radius=r2, start_angle=-PI / 2, angle=-PI / 2, arc_center=C2, color=ORANGE_, stroke_width=7)
        l1 = tex("1", size=38, color=ORANGE_).move_to(C2 + (r2 + 0.35) * np.array([np.cos(-PI / 4), np.sin(-PI / 4), 0]))
        l2 = tex("1", size=38, color=ORANGE_).move_to(C2 + (r2 + 0.35) * np.array([np.cos(-3 * PI / 4), np.sin(-3 * PI / 4), 0]))
        self.play(Create(arcR), Create(arcL), FadeIn(l1), FadeIn(l2), run_time=1.4)
        top = Arc(radius=r2, start_angle=0, angle=PI, arc_center=C2, color=PURPLE_, stroke_width=5)
        l3 = VGroup(zh("相隔", 26, PURPLE_), tex("2", size=36, color=PURPLE_)).arrange(RIGHT, buff=0.1)
        l3.next_to(top, UP, buff=0.12)
        self.play(Create(top), FadeIn(l3), run_time=max(0.6, min(1.2, self.remaining())))
        self.finish(extra=0.6)


# ---------------------------------------------------------------------------
class S12Doubling(VScene):
    KEY = "doubling"
    O = np.array([-2.2, -2.55, 0])
    SIZE = 4.9  # on-screen diameter of the newest circle

    def zoom(self, k):
        return self.SIZE * PI / 2 ** k

    def circles(self, kmax, z, kmin=1):
        return VGroup(*[lake_circle(2 ** k, self.O, z, stroke_opacity=1.0 if k == kmax else 0.35,
                                    stroke_width=2.5 if k == kmax else 1.5)
                        for k in range(kmin, kmax + 1)])

    def lights(self, k, z, scale):
        return VGroup(*[lighthouse(self.O + z * lake_xy(2 ** k, s), scale) for s in odd_positions(2 ** k)])

    def construct(self):
        self.wait(0.2)
        O = self.O
        you = observer(O)
        # stage 2 (from the previous chapter), drawn so that circle 3 fits
        z = self.zoom(3)
        circs = self.circles(2, z)
        lts = self.lights(2, z, 1.0)
        T2 = O + z * lake_xy(4, 2.0)

        D = self.say(0)
        self.play(FadeIn(circs), FadeIn(you), FadeIn(lts), run_time=1.0)
        topdot = Dot(T2, radius=0.07, color=WHITE)
        toplab = zh("最高点", 24, GREY_).next_to(topdot, UP, buff=0.1)
        self.play(FadeIn(topdot), FadeIn(toplab), run_time=0.7)
        c3 = lake_circle(8, O, z)
        self.play(Create(c3), run_time=1.4)
        new_pts = [O + z * lake_xy(8, s) for s in (1, 5, 3, 7)]  # pairs: (1,5) from s=1, (3,7) from s=3
        lines = VGroup(Line(new_pts[0], new_pts[1], color=GREEN_, stroke_width=2.5),
                       Line(new_pts[2], new_pts[3], color=GREEN_, stroke_width=2.5))
        self.play(Create(lines), run_time=max(1.0, min(2.0, self.remaining() - 0.2)))
        self.hold()

        D = self.say(1)
        P = O + z * lake_xy(4, 1.0)
        oa = Line(O, new_pts[0], color=WHITE, stroke_width=2)
        ob = Line(O, new_pts[1], color=WHITE, stroke_width=2)
        op = DashedLine(O, P, color=YELLOW_, stroke_width=2)
        ra = RightAngle(Line(O, new_pts[0]), Line(O, new_pts[1]), length=0.22, color=WHITE, quadrant=(1, 1))
        rp = RightAngle(Line(P, new_pts[0]), Line(P, O), length=0.18, color=YELLOW_, quadrant=(1, 1))
        self.play(Create(oa), Create(ob), Create(op), run_time=0.9)
        self.play(Create(ra), Create(rp), run_time=0.8)
        new_l = VGroup(*[lighthouse(p, 1.0) for p in new_pts])
        src = VGroup(lts[0].copy(), lts[0].copy(), lts[1].copy(), lts[1].copy())
        self.play(*[Transform(src[i], new_l[i]) for i in range(4)], FadeOut(lts), run_time=1.4)
        self.remove(*src)
        self.add(new_l)
        self.play(FadeOut(VGroup(oa, ob, op, ra, rp, lines, topdot, toplab)), run_time=max(0.5, min(0.8, self.remaining())))
        circs = VGroup(*circs, c3)
        lts = self.lights(3, z, 1.0)
        self.remove(new_l)
        self.add(lts)
        self.hold()

        # --- keep doubling
        D = self.say(2)
        info = VGroup(
            VGroup(zh("周长", 28, BLUE_), tex("8", size=38, color=BLUE_)).arrange(RIGHT, buff=0.15),
            VGroup(zh("灯塔", 28, YELLOW_), tex("4", size=38, color=YELLOW_)).arrange(RIGHT, buff=0.15),
            VGroup(zh("总亮度", 28, YELLOW_), tex(r"\frac{\pi^2}{4}", size=44, color=YELLOW_)).arrange(RIGHT, buff=0.15),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.35).move_to([4.6, 0.6, 0])
        self.play(FadeIn(info), run_time=0.7)
        steps = [4, 5, 6, 7]
        t = max(1.2, (self.remaining() - 0.4) / len(steps))
        for k in steps:
            zn = self.zoom(k)
            scale = max(0.28, 0.9 * 0.72 ** (k - 3))
            new_c = VGroup(*self.circles(k, zn)[:-1])
            nxt = lake_circle(2 ** k, O, zn)
            target = self.lights(k, zn, scale)
            # every old light splits into two: position s and s + L_(k-1)
            n_old = 2 ** (k - 2)
            src = VGroup(*[lts[i % n_old].copy() for i in range(2 * n_old)])
            order = [target[i] for i in range(2 * n_old)]
            # target is sorted by arc position; old light i (position 2i+1) maps to
            # positions 2i+1 (index i) and 2i+1+L_old (index i + n_old)
            new_info = VGroup(
                VGroup(zh("周长", 28, BLUE_), tex(str(2 ** k), size=38, color=BLUE_)).arrange(RIGHT, buff=0.15),
                VGroup(zh("灯塔", 28, YELLOW_), tex(str(2 ** (k - 1)), size=38, color=YELLOW_)).arrange(RIGHT, buff=0.15),
                info[2].copy(),
            ).arrange(DOWN, aligned_edge=LEFT, buff=0.35).move_to(info)
            self.remove(lts)
            self.play(Transform(circs, new_c), Create(nxt),
                      *[Transform(src[i], order[i]) for i in range(2 * n_old)],
                      Transform(info[0], new_info[0]), Transform(info[1], new_info[1]),
                      run_time=t)
            self.remove(*src)
            circs = VGroup(*circs, nxt)
            lts = target
            self.add(lts)
        self.hold()

        # --- positions along the shore are preserved
        D = self.say(3)
        rule = VGroup(zh("圆周角 = 圆心角的一半", 28, GREY_),
                      zh("⟹ 沿湖岸的位置不变：±1, ±3, ±5, …", 28, YELLOW_)).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        rule.move_to([3.4, -2.2, 0])
        self.play(FadeIn(rule, shift=0.1 * UP), run_time=1.0)
        self.play(Indicate(lts, color=WHITE, scale_factor=1.05), run_time=max(1.0, min(1.8, self.remaining())))
        self.hold()

        # --- local view: the shore near you flattens into a line
        D = self.say(4)
        self.play(FadeOut(VGroup(circs, lts, info, rule, you)), run_time=0.7)
        O2 = np.array([0, -1.4, 0])
        zl = 0.42
        u = ValueTracker(5.0)

        def shore():
            L = 2 ** u.get_value()
            smax = min(L / 2, 17.5)
            return ParametricFunction(lambda s: O2 + zl * lake_xy(L, s), t_range=[-smax, smax, 0.05],
                                      color=BLUE_, stroke_width=3)

        def near_lights():
            L = 2 ** u.get_value()
            ss = [s for s in range(-15, 16, 2) if abs(s) <= L / 2]
            return VGroup(*[lighthouse(O2 + zl * lake_xy(L, s), 0.7) for s in ss])

        sh = always_redraw(shore)
        nl = always_redraw(near_lights)
        you2 = observer(O2)
        self.play(FadeIn(sh), FadeIn(nl), FadeIn(you2), run_time=0.8)
        self.play(u.animate.set_value(12.0), run_time=max(2.0, self.remaining() - 1.6), rate_func=smooth)
        sh.clear_updaters()
        nl.clear_updaters()
        flat = Line(O2 + LEFT * 7.2, O2 + RIGHT * 7.2, color=BLUE_, stroke_width=3)
        marks = VGroup(*[tex(("-" if s < 0 else "") + str(abs(s)), size=28, color=YELLOW_).move_to(O2 + zl * s * RIGHT + DOWN * 0.55)
                         for s in range(-13, 14, 2)])
        self.play(ReplacementTransform(sh, flat), FadeIn(marks), run_time=max(0.8, min(1.4, self.remaining())))
        self.hold()

        # --- conclusion: the odd sum
        D = self.say(5)
        e1 = tex(r"2\left(1+\frac{1}{9}+\frac{1}{25}+\frac{1}{49}+\cdots\right)", "=", r"\frac{\pi^2}{4}", size=54)
        e1[2].set_color(YELLOW_)
        e1.move_to(UP * 2.3)
        self.play(Write(e1), run_time=1.8)
        e2 = tex(r"1+\frac{1}{9}+\frac{1}{25}+\frac{1}{49}+\cdots", "=", r"\frac{\pi^2}{8}", size=54)
        e2[2].set_color(YELLOW_)
        e2.move_to(UP * 0.75)
        self.wait(max(0, 0.6 * D - 2.2))
        self.play(TransformFromCopy(e1, e2), run_time=max(1.0, min(1.6, self.remaining())))
        self.hold()

        # --- from odd squares to all squares
        D = self.say(6)
        self.play(FadeOut(VGroup(flat, nl, marks, you2, e1)), e2.animate.move_to(UP * 2.4).scale(0.85), run_time=0.8)
        ev = tex(r"\frac{1}{4}+\frac{1}{16}+\frac{1}{36}+\cdots", "=", r"\frac{1}{4}", r"\left(1+\frac{1}{4}+\frac{1}{9}+\cdots\right)",
                 size=48).move_to(UP * 0.85)
        ev[2].set_color(PINK)
        elab = zh("偶数项", 26, PINK).next_to(ev, LEFT, buff=0.3)
        olab = zh("奇数项", 26, YELLOW_).next_to(e2, LEFT, buff=0.3)
        self.play(FadeIn(ev), FadeIn(elab), FadeIn(olab), run_time=1.2)
        s1 = tex(r"S", "-", r"\frac{1}{4}S", "=", r"\frac{3}{4}S", "=", r"\frac{\pi^2}{8}", size=56).move_to(DOWN * 0.55)
        s1[6].set_color(YELLOW_)
        self.wait(max(0, 0.35 * D - 1.2))
        self.play(Write(s1), run_time=1.4)
        s2 = tex(r"S", "=", r"\frac{\pi^2}{8}\cdot\frac{4}{3}", "=", r"\frac{\pi^2}{6}", size=64).move_to(DOWN * 1.85)
        s2[4].set_color(YELLOW_)
        self.wait(max(0, 0.7 * D - (self.time - (self._end - D)) - 1.0))
        self.play(Write(s2), run_time=max(0.9, min(1.4, self.remaining())))
        box = SurroundingRectangle(s2[3:], color=YELLOW_, buff=0.15)
        self.play(Create(box), run_time=0.6)
        self.hold()

        D = self.say(7)
        note = zh("注：取极限需要严格论证，韦斯特伦德的原论文给出了完整证明", 26, GREY_).move_to(DOWN * 2.85)
        self.play(FadeIn(note), run_time=0.8)
        self.finish(extra=0.4)


# ---------------------------------------------------------------------------
class S13Meaning(VScene):
    KEY = "meaning"

    def construct(self):
        self.wait(0.2)
        q = zh("π 为什么会出现？", 60, YELLOW_, bold=True)

        D = self.say(0)
        self.play(FadeIn(q, scale=1.1), run_time=1.0)
        self.hold()

        # --- a line is an infinitely large circle
        D = self.say(1)
        self.play(q.animate.scale(0.55).to_edge(UP, buff=0.35), run_time=0.7)
        O = np.array([0, -2.1, 0])
        zl = 0.5
        u = ValueTracker(1.0)

        def nest():
            k_top = u.get_value()
            g = VGroup()
            for k in range(1, 13):
                if k > k_top + 1e-6:
                    break
                g.add(lake_circle(2 ** k, O, zl, stroke_width=2, stroke_opacity=0.25 + 0.75 * (k > k_top - 1)))
            return g

        ns = always_redraw(nest)
        you = observer(O)
        self.add(ns, you)
        self.play(u.animate.set_value(11.0), run_time=max(2.0, 0.65 * D), rate_func=linear)
        ns.clear_updaters()
        ln = Line(O + LEFT * 7.2, O + RIGHT * 7.2, color=BLUE_, stroke_width=3)
        cap = VGroup(zh("直线", 34, BLUE_, bold=True), tex("=", size=40),
                     zh("无限大的圆", 34, BLUE_, bold=True)).arrange(RIGHT, buff=0.2).move_to(UP * 1.9)
        self.play(FadeIn(ln), FadeIn(cap), run_time=max(0.6, min(1.2, self.remaining())))
        self.hold()

        # --- where pi enters
        D = self.say(2)
        self.play(FadeOut(VGroup(ns, ln, cap, you)), run_time=0.6)
        O2 = np.array([-3.8, -2.2, 0])
        z = 3.2
        lake = lake_circle(2.0, O2, z, fill_color=BLUE_, fill_opacity=0.12)
        T = O2 + z * lake_xy(2.0, 1.0)
        pieces = VGroup(lake, observer(O2), lighthouse(T, 1.1), DashedLine(O2, T, color=WHITE, stroke_width=2))
        self.play(FadeIn(pieces), run_time=0.9)
        d1 = VGroup(zh("直径", 32), tex("=", size=44), zh("周长", 32), tex(r"\div\,\pi", size=44, color=YELLOW_)
                    ).arrange(RIGHT, buff=0.15).move_to([2.6, 1.3, 0])
        d2 = tex(r"d=\frac{2}{\pi}", size=56).next_to(d1, DOWN, buff=0.45)
        self.play(FadeIn(d1, shift=0.1 * UP), run_time=1.0)
        self.play(FadeIn(d2, shift=0.1 * UP), run_time=0.8)
        pdef = VGroup(tex(r"\pi", size=48, color=YELLOW_), tex("=", size=44), zh("周长 ÷ 直径", 32, YELLOW_)
                      ).arrange(RIGHT, buff=0.15).next_to(d2, DOWN, buff=0.5)
        self.wait(max(0, 0.6 * D - 2.4))
        self.play(FadeIn(pdef, shift=0.1 * UP), run_time=max(0.6, min(1.0, self.remaining())))
        self.hold()

        # --- why squared
        D = self.say(3)
        self.play(FadeOut(VGroup(d1, pdef)), d2.animate.move_to([2.6, 1.9, 0]), run_time=0.7)
        br = VGroup(zh("亮度", 32, YELLOW_), tex(r"=\frac{1}{d^2}=", size=54), tex(r"\frac{\pi^2}{4}", size=60, color=YELLOW_)
                    ).arrange(RIGHT, buff=0.15).move_to([2.6, 0.3, 0])
        self.play(Write(br), run_time=1.3)
        why = zh("平方反比  ⟹  π 的平方", 32, ORANGE_).next_to(br, DOWN, buff=0.45)
        self.play(FadeIn(why, shift=0.1 * UP), run_time=max(0.6, min(1.0, self.remaining())))
        self.hold()

        # --- conserved through every split
        D = self.say(4)
        self.play(FadeOut(VGroup(pieces, d2, br, why)), run_time=0.6)

        def mini(n, r=0.62):
            c = Circle(radius=r, color=BLUE_, stroke_width=2)
            o = c.get_bottom()
            L = 1.0
            ls = VGroup(*[lighthouse(c.get_center() + r * np.array([np.sin(TAU * (2 * i + 1) / (2 * n)),
                                                                    -np.cos(TAU * (2 * i + 1) / (2 * n)), 0]), 0.45)
                          for i in range(n)])
            return VGroup(c, ls, Dot(o, radius=0.05, color=WHITE))

        chain = VGroup(mini(1), tex("=", size=48), mini(2), tex("=", size=48), mini(4), tex("=", size=48), mini(8),
                       tex(r"=\cdots=", size=48),
                       VGroup(Line(LEFT * 0.9, RIGHT * 0.9, color=BLUE_, stroke_width=2),
                              VGroup(*[lighthouse(RIGHT * x * 0.3, 0.4) for x in (-3, -1, 1, 3)]),
                              Dot(ORIGIN, radius=0.05, color=WHITE))).arrange(RIGHT, buff=0.3)
        chain.move_to(UP * 0.6)
        vals = VGroup(*[tex(r"\frac{\pi^2}{4}", size=36, color=YELLOW_).next_to(chain[i], DOWN, buff=0.3)
                        for i in (0, 2, 4, 6, 8)])
        self.play(LaggedStart(*[FadeIn(m, shift=0.1 * RIGHT) for m in chain], lag_ratio=0.2), run_time=2.4)
        self.play(LaggedStart(*[FadeIn(v) for v in vals], lag_ratio=0.2), run_time=1.2)
        cons = zh("像守恒量一样，π² 一路传到直线上的整数", 30, YELLOW_).move_to(DOWN * 1.8)
        self.play(FadeIn(cons, shift=0.1 * UP), run_time=max(0.6, min(1.0, self.remaining())))
        self.hold()

        # --- two roads, one circle
        D = self.say(5)
        self.play(FadeOut(VGroup(chain, vals, cons)), run_time=0.6)

        def card(title, color, body, meaning):
            t = zh(title, 34, color, bold=True)
            m = zh(meaning, 28, color)
            g = VGroup(t, body, m).arrange(DOWN, buff=0.35)
            box = SurroundingRectangle(g, buff=0.35, corner_radius=0.12, color=color, stroke_width=1.5,
                                       fill_color=color, fill_opacity=0.06)
            return VGroup(box, g)

        ce = card("欧拉", BLUE_, tex(r"\sin x = 0 \iff x = n\pi", size=40), "π = 正弦零点的间隔")
        cl = card("灯塔", YELLOW_, VGroup(zh("直径", 28), tex(r"=", size=36), zh("周长", 28), tex(r"\div\,\pi", size=36)).arrange(RIGHT, buff=0.12),
                  "π = 周长 ÷ 直径")
        cards = VGroup(ce, cl).arrange(RIGHT, buff=1.0).move_to(UP * 0.5)
        self.play(FadeIn(ce, shift=0.2 * UP), run_time=0.9)
        self.wait(max(0, 0.3 * D - 0.9))
        self.play(FadeIn(cl, shift=0.2 * UP), run_time=0.9)
        punch = zh("整数的背后，藏着一个圆", 44, YELLOW_, bold=True).move_to(DOWN * 2.1)
        self.wait(max(0, 0.72 * D - (self.time - (self._end - D)) - 1.0))
        self.play(FadeIn(punch, scale=1.1), run_time=max(0.8, min(1.2, self.remaining())))
        self.finish(extra=0.8)


# ---------------------------------------------------------------------------
class S14ComputePi(VScene):
    KEY = "computepi"

    def construct(self):
        self.wait(0.2)
        f = tex(r"\pi", "=", r"\sqrt{6\sum_{n=1}^{\infty}\frac{1}{n^2}}", size=72).move_to(UP * 2.1)
        f[0].set_color(YELLOW_)

        D = self.say(0)
        self.play(Write(f), run_time=1.8)
        self.hold()

        D = self.say(1)
        self.play(f.animate.scale(0.7).to_edge(UP, buff=0.3), run_time=0.7)
        # (N, sqrt(6*S_N), how many leading glyphs already agree with pi)
        data = [("10", "3.049", 1), ("100", "3.132", 3), ("1000", "3.1406", 4), ("10^6", "3.1415917", 7)]
        rows = VGroup()
        for N, val, good in data:
            n = tex(rf"N={N}", size=46, color=GREY_)
            v = tex(val, size=52)
            v[0][:good].set_color(YELLOW_)
            rows.add(VGroup(n, v))
        for r in rows:
            r[0].move_to([-3.2, 0, 0], aligned_edge=RIGHT)
            r[1].move_to([-2.4, 0, 0], aligned_edge=LEFT)
        for i, r in enumerate(rows):
            r.shift(UP * (1.1 - 0.9 * i))
        ref = tex(r"\pi = 3.14159265\ldots", size=44, color=YELLOW_).move_to([-2.2, -2.5, 0])
        t = max(0.8, (D - 1.5) / 4)
        for r in rows:
            self.play(FadeIn(r, shift=0.1 * LEFT), run_time=min(t, 2.5))
        self.play(FadeIn(ref), run_time=max(0.4, min(0.8, self.remaining())))
        self.hold()

        D = self.say(2)
        ax = Axes(x_range=[0, 6.3, 1], y_range=[2.4, 3.25, 0.2], x_length=5.4, y_length=3.6,
                  axis_config={"color": GREY_, "stroke_width": 2}, tips=False).move_to([3.6, -0.3, 0])
        xl = VGroup(*[tex(rf"10^{{{k}}}", size=24, color=GREY_).next_to(ax.c2p(k, 2.4), DOWN, buff=0.12) for k in range(0, 7, 2)])
        z2 = np.pi ** 2 / 6

        def approx(lx):
            N = 10 ** lx
            s = z2 - 1 / N + 1 / (2 * N ** 2) - 1 / (6 * N ** 3)  # Euler-Maclaurin tail
            return np.sqrt(6 * s)

        xs = np.linspace(0, 6, 121)
        pts = [ax.c2p(x, approx(x)) for x in xs]
        curve = VMobject(color=BLUE_, stroke_width=3).set_points_smoothly(pts)
        pil = DashedLine(ax.c2p(0, np.pi), ax.c2p(6.3, np.pi), color=YELLOW_, stroke_width=2)
        pl = tex(r"\pi", size=36, color=YELLOW_).next_to(pil, RIGHT, buff=0.1)
        nlab = zh("取的项数 N", 22, GREY_).next_to(ax, DOWN, buff=0.55)
        self.play(Create(ax), FadeIn(xl), FadeIn(nlab), Create(pil), FadeIn(pl), run_time=1.0)
        self.play(Create(curve), run_time=max(1.5, min(3.0, self.remaining() - 0.5)))
        self.finish(extra=0.6)


# ---------------------------------------------------------------------------
class S15Rigor(VScene):
    KEY = "rigor"

    def construct(self):
        self.wait(0.2)
        prod = tex(r"\frac{\sin x}{x}", r"\overset{?}{=}", r"\prod_{n=1}^{\infty}\left(1-\frac{x^2}{n^2\pi^2}\right)", size=60)
        prod[0].set_color(BLUE_)
        prod[1].set_color(PINK)
        prod.move_to(UP * 2.3)
        warn = zh("无穷乘积也能像多项式一样按根分解吗？", 32, PINK).next_to(prod, DOWN, buff=0.3)

        D = self.say(0)
        self.play(Write(prod), run_time=1.6)
        self.play(FadeIn(warn, shift=0.15 * UP), run_time=max(0.6, min(0.9, self.remaining())))
        self.hold()

        D = self.say(1)
        chk = tex(r"\sum_{n=1}^{\infty}\frac{1}{n^2} = 1.644934\ldots = \frac{\pi^2}{6}", size=42).move_to(DOWN * 0.1)
        tick = tex(r"\checkmark", size=50, color=GREEN_).next_to(chk, RIGHT, buff=0.3)
        self.play(FadeIn(chk), FadeIn(tick), run_time=1.0)
        w1 = tex(r"x=\frac{\pi}{2}:\quad", r"\frac{2}{\pi}", "=", r"\prod_{n=1}^{\infty}\left(1-\frac{1}{4n^2}\right)", size=44)
        w1.move_to(DOWN * 1.3)
        w2 = tex(r"\frac{\pi}{2}", "=", r"\frac{2}{1}\cdot\frac{2}{3}\cdot\frac{4}{3}\cdot\frac{4}{5}\cdot\frac{6}{5}\cdot\frac{6}{7}\cdots",
                 size=46).move_to(DOWN * 2.4)
        w2[0].set_color(YELLOW_)
        wl = VGroup(zh("沃利斯", 28, YELLOW_), Text("1656", font_size=28, color=YELLOW_)).arrange(RIGHT, buff=0.12)
        wl.next_to(w2, RIGHT, buff=0.35)
        self.wait(max(0, 0.3 * D - 1.0))
        self.play(FadeIn(w1, shift=0.1 * UP), run_time=1.2)
        self.play(FadeIn(w2, shift=0.1 * UP), FadeIn(wl), run_time=max(0.8, min(1.4, self.remaining())))
        self.hold()

        D = self.say(2)
        self.play(FadeOut(VGroup(chk, tick, w1, w2, wl)), run_time=0.6)
        y1741 = VGroup(Text("1741", font_size=34, color=YELLOW_, weight=BOLD),
                       zh("欧拉：不依赖无穷乘积的新证明", 30)).arrange(RIGHT, buff=0.35).move_to(DOWN * 0.2)
        self.play(FadeIn(y1741, shift=0.15 * UP), run_time=0.9)
        w = VGroup(Text("1876", font_size=34, color=GREEN_, weight=BOLD),
                   zh("魏尔斯特拉斯因式分解定理", 30, GREEN_, bold=True)).arrange(RIGHT, buff=0.35).move_to(DOWN * 1.4)
        self.wait(max(0, 0.4 * D - 1.5))
        self.play(FadeIn(w, shift=0.15 * UP), run_time=0.9)
        eq = tex("=", size=60, color=GREEN_).move_to(prod[1])
        self.play(ReplacementTransform(prod[1], eq), warn.animate.set_opacity(0.3), run_time=0.9)
        box = SurroundingRectangle(VGroup(prod[0], eq, prod[2]), color=GREEN_, buff=0.2, corner_radius=0.1)
        self.play(Create(box), run_time=max(0.5, min(0.8, self.remaining())))
        self.finish(extra=0.5)


# ---------------------------------------------------------------------------
class S16Legacy(VScene):
    KEY = "legacy"

    def construct(self):
        self.wait(0.2)
        rows = VGroup(
            tex(r"\sum \frac{1}{n^2}", "=", r"\frac{\pi^2}{6}", size=46),
            tex(r"\sum \frac{1}{n^4}", "=", r"\frac{\pi^4}{90}", size=46),
            tex(r"\sum \frac{1}{n^6}", "=", r"\frac{\pi^6}{945}", size=46),
            tex(r"\vdots", size=46),
            tex(r"\sum \frac{1}{n^{12}}", "=", r"\frac{691\,\pi^{12}}{638512875}", size=46),
        ).arrange(DOWN, buff=0.3, aligned_edge=LEFT).move_to([-3.6, 0.45, 0])
        rows[3].shift(RIGHT * 0.5)
        for r in rows:
            if len(r) == 3:
                r[2].set_color(YELLOW_)

        D = self.say(0)
        self.play(FadeIn(rows[0]), run_time=0.8)
        self.wait(max(0, 0.3 * D - 0.8))
        self.play(FadeIn(rows[1], shift=0.15 * DOWN), run_time=0.9)
        self.play(FadeIn(rows[2], shift=0.15 * DOWN), run_time=0.8)
        self.play(FadeIn(rows[3:], shift=0.15 * DOWN), run_time=max(0.8, min(1.4, self.remaining())))
        self.hold()

        D = self.say(1)
        gen = tex(r"\sum_{n=1}^{\infty}\frac{1}{n^{2k}}", "=", r"q_k", r"\,\pi^{2k}", size=56).move_to([3.3, 1.2, 0])
        gen[2].set_color(GREEN_)
        gen[3].set_color(YELLOW_)
        gl = zh("其中系数 q 是有理数（来自正弦的零点）", 26, GREEN_).next_to(gen, DOWN, buff=0.35)
        self.play(Write(gen), run_time=1.4)
        self.play(FadeIn(gl), run_time=max(0.6, min(1.0, self.remaining())))
        self.hold()

        D = self.say(2)
        self.play(FadeOut(VGroup(gen, gl)), rows.animate.set_opacity(0.45), run_time=0.6)
        odd = tex(r"\sum \frac{1}{n^3}", "=", r"1.2020569\ldots", "=", r"\ ?", size=52).move_to([3.3, 1.4, 0])
        odd[4].set_color(PINK)
        tag = zh("奇数次方：没有已知的简洁公式", 26, PINK).next_to(odd, DOWN, buff=0.35)
        self.play(FadeIn(odd), FadeIn(tag), run_time=1.2)
        ap = VGroup(Text("1978", font_size=30, color=GREY_, weight=BOLD), zh("阿佩里：它是无理数", 28)).arrange(RIGHT, buff=0.3)
        ap2 = zh("与 π 的关系：仍是个谜", 28, GREY_)
        VGroup(ap, ap2).arrange(DOWN, buff=0.25, aligned_edge=LEFT).next_to(tag, DOWN, buff=0.55)
        self.wait(max(0, 0.45 * D - 1.2))
        self.play(FadeIn(ap, shift=0.1 * UP), run_time=0.9)
        self.play(FadeIn(ap2, shift=0.1 * UP), run_time=max(0.6, min(1.0, self.remaining())))
        self.hold()

        D = self.say(3)
        self.play(FadeOut(VGroup(rows, odd, tag, ap, ap2)), run_time=0.6)
        zeta = tex(r"\zeta(s)", "=", r"\sum_{n=1}^{\infty}\frac{1}{n^{s}}", size=64).move_to(UP * 1.5)
        zeta[0].set_color(GREEN_)
        rie = VGroup(zh("黎曼", 30, bold=True), Text("Riemann, 1859", font_size=26, color=GREY_)).arrange(RIGHT, buff=0.3)
        rie.next_to(zeta, DOWN, buff=0.35)
        primes = tex(r"2,\ 3,\ 5,\ 7,\ 11,\ 13,\ 17,\ 19,\ 23,\ 29,\ \ldots", size=46, color=BLUE_).move_to(DOWN * 1.2)
        plab = zh("素数的分布", 28, BLUE_).next_to(primes, DOWN, buff=0.3)
        self.play(Write(zeta), FadeIn(rie), run_time=1.5)
        self.play(FadeIn(primes, lag_ratio=0.1), FadeIn(plab), run_time=max(1.0, min(2.0, self.remaining())))
        self.hold()

        # --- coprime probability
        D = self.say(4)
        self.play(FadeOut(VGroup(zeta, rie, primes, plab)), run_time=0.6)
        cols, rws, sp = 24, 14, 0.26
        grid = {}
        dots = VGroup()
        for j in range(1, rws + 1):
            for i in range(1, cols + 1):
                d = Dot([(i - 1) * sp, (j - 1) * sp, 0], radius=0.065, color=GREY_, fill_opacity=0.55)
                grid[(i, j)] = d
                dots.add(d)
        dots.move_to([-3.6, 0.1, 0])
        axlab = VGroup(tex("a", size=34, color=GREY_).next_to(dots, DOWN, buff=0.15),
                       tex("b", size=34, color=GREY_).next_to(dots, LEFT, buff=0.15))
        self.play(FadeIn(dots, lag_ratio=0.002), FadeIn(axlab), run_time=1.2)
        p2 = tex(r"P(2\mid a,\ 2\mid b)=\frac{1}{4}", size=44).move_to([3.4, 1.9, 0])
        p3 = tex(r"P(3\mid a,\ 3\mid b)=\frac{1}{9}", size=44).move_to([3.4, 0.6, 0])
        both2 = VGroup(*[d for (i, j), d in grid.items() if i % 2 == 0 and j % 2 == 0])
        both3 = VGroup(*[d for (i, j), d in grid.items() if i % 3 == 0 and j % 3 == 0])
        self.play(both2.animate.set_color(PINK).set_opacity(1), FadeIn(p2), run_time=1.2)
        self.wait(max(0, 0.45 * D - 3.0))
        self.play(both2.animate.set_color(GREY_).set_opacity(0.55), both3.animate.set_color(ORANGE_).set_opacity(1),
                  FadeIn(p3), run_time=max(0.8, min(1.4, self.remaining())))
        self.hold()

        D = self.say(5)
        cop = VGroup(*[d for (i, j), d in grid.items() if gcd(i, j) == 1])
        frac = len(cop) / (cols * rws)
        self.play(FadeOut(VGroup(p2, p3)), dots.animate.set_color(GREY_).set_opacity(0.3),
                  cop.animate.set_color(GREEN_).set_opacity(1), run_time=1.0)
        e1 = VGroup(zh("互质的概率", 28, GREEN_),
                    tex(r"=\prod_{p}\left(1-\frac{1}{p^2}\right)", size=46)).arrange(RIGHT, buff=0.15)
        e1.move_to([0.6, 1.7, 0], aligned_edge=LEFT)
        e2 = tex(r"=\frac{1}{\sum 1/n^2}", "=", r"\frac{6}{\pi^2}", r"\approx 60.8\%", size=50).next_to(e1, DOWN, buff=0.4)
        e2.align_to(e1[1], LEFT)
        e2[2].set_color(YELLOW_)
        if e2.get_right()[0] > 6.9:
            e2.shift(LEFT * (e2.get_right()[0] - 6.9))
        self.play(FadeIn(e1, shift=0.1 * UP), run_time=1.2)
        self.wait(max(0, 0.45 * D - 2.2))
        self.play(FadeIn(e2, shift=0.1 * UP), run_time=1.2)
        here = zh(f"图中 {cols}×{rws} 个点：互质占 {frac * 100:.1f}%", 24, GREEN_).next_to(e2, DOWN, buff=0.45)
        here.align_to(e1, LEFT)
        self.play(FadeIn(here), run_time=max(0.5, min(0.9, self.remaining())))
        self.finish(extra=0.6)


# ---------------------------------------------------------------------------
class S17Outro(VScene):
    KEY = "outro"

    def construct(self):
        self.wait(0.2)
        ints = tex(r"1,\ 2,\ 3,\ 4,\ 5,\ \ldots", size=56, color=BLUE_).move_to([-4.2, 1.2, 0])
        circle = Circle(radius=1.1, color=YELLOW_, stroke_width=4).move_to([4.2, 1.2, 0])
        pi_in = tex(r"\pi", size=64, color=YELLOW_).move_to(circle)
        arrow = Arrow(ints.get_right() + RIGHT * 0.3, circle.get_left() + LEFT * 0.3, color=GREY_, buff=0)

        D = self.say(0)
        self.play(FadeIn(ints, shift=0.2 * RIGHT), run_time=1.0)
        self.play(GrowArrow(arrow), Create(circle), FadeIn(pi_in), run_time=max(1.2, min(2.0, self.remaining())))
        self.hold()

        D = self.say(1)
        ax = Axes(x_range=[-3.3 * np.pi, 3.3 * np.pi, np.pi], y_range=[-0.4, 1.1, 1], x_length=5.0, y_length=1.6,
                  axis_config={"color": GREY_, "stroke_width": 1.5}, tips=False)
        g = ax.plot(sinc, x_range=[-3.3 * np.pi, 3.3 * np.pi, 0.03], color=BLUE_, stroke_width=3)
        zs = VGroup(*[Dot(ax.c2p(k * np.pi, 0), radius=0.06, color=PINK) for k in (-3, -2, -1, 1, 2, 3)])
        left = VGroup(VGroup(ax, g, zs), zh("欧拉：正弦的零点", 28, BLUE_)).arrange(DOWN, buff=0.3)
        O = ORIGIN
        lk = VGroup(*[Circle(radius=0.25 * 2 ** k, color=BLUE_, stroke_width=2, stroke_opacity=0.3 + 0.2 * k)
                      .move_to(UP * 0.25 * 2 ** k) for k in range(0, 3)])
        lts = VGroup(*[lighthouse(lk[2].get_center() + lk[2].radius * np.array([np.sin(a), -np.cos(a), 0]), 0.4)
                       for a in TAU * (2 * np.arange(4) + 1) / 8])
        right = VGroup(VGroup(lk, lts, Dot(O, radius=0.05, color=WHITE)), zh("灯塔：越变越大的湖", 28, YELLOW_)).arrange(DOWN, buff=0.3)
        pair = VGroup(left, right).arrange(RIGHT, buff=1.4).move_to(DOWN * 1.35)
        self.play(FadeIn(left, shift=0.2 * UP), run_time=1.0)
        self.wait(max(0, 0.45 * D - 1.0))
        self.play(FadeIn(right, shift=0.2 * UP), run_time=max(0.8, min(1.2, self.remaining())))
        self.hold()

        D = self.say(2)
        final = tex(r"1+\frac{1}{4}+\frac{1}{9}+\frac{1}{16}+\cdots", "=", r"\frac{\pi^2}{6}", size=76)
        final[2].set_color(YELLOW_)
        title = zh("巴塞尔问题", 48, bold=True).to_edge(UP, buff=0.8)
        final.move_to(DOWN * 0.3)
        self.play(FadeOut(VGroup(ints, circle, pi_in, arrow, pair)), run_time=0.7)
        self.play(FadeIn(title), Write(final), run_time=1.8)
        self.hold(1.6)
        self.play(FadeOut(title), run_time=0.8)
        self.wait(1.0)
        self.play(FadeOut(final), run_time=1.0)
        self.wait(0.4)
