from manim import *
import numpy as np

class FourierTransformExplanation(Scene):
    def construct(self):

        # -------------------------------------------------
        # 1️⃣ TIME DOMAIN SIGNAL
        # -------------------------------------------------
        time_axes = Axes(
            x_range=[0, 10],
            y_range=[-3, 3],
            x_length=8,
            y_length=3,
            tips=False,
        ).to_edge(UP)

        time_title = Text("Time Domain Signal", font_size=28)
        time_title.next_to(time_axes, UP)

        def signal(t):
            return np.sin(2 * np.pi * t) + 0.5 * np.sin(2 * np.pi * 3 * t)

        signal_graph = time_axes.plot(
            signal,
            x_range=[0, 10],
            color=BLUE
        )

        self.play(Create(time_axes))
        self.play(Write(time_title))
        self.play(Create(signal_graph))
        self.wait(1)

        # -------------------------------------------------
        # 2️⃣ ROTATING VECTORS (PHASORS)
        # -------------------------------------------------
        origin = ORIGIN + DOWN * 0.5
        circle1 = Circle(radius=1, color=GRAY).move_to(origin)
        circle2 = Circle(radius=0.5, color=GRAY).move_to(origin)

        angle = ValueTracker(0)

        vector1 = always_redraw(
            lambda: Arrow(
                origin,
                origin + np.array([
                    np.cos(angle.get_value()),
                    np.sin(angle.get_value()),
                    0
                ]),
                buff=0,
                color=YELLOW
            )
        )

        vector2 = always_redraw(
            lambda: Arrow(
                origin,
                origin + np.array([
                    0.5 * np.cos(3 * angle.get_value()),
                    0.5 * np.sin(3 * angle.get_value()),
                    0
                ]),
                buff=0,
                color=RED
            )
        )

        phasor_title = Text("Rotating Vectors (Frequencies)", font_size=26)
        phasor_title.next_to(origin, DOWN)

        self.play(Create(circle1), Create(circle2))
        self.play(Write(phasor_title))
        self.play(Create(vector1), Create(vector2))
        self.play(angle.animate.set_value(4 * PI), run_time=4, rate_func=linear)
        self.wait(1)

        # -------------------------------------------------
        # 3️⃣ FREQUENCY DOMAIN (MAGNITUDE)
        # -------------------------------------------------
        freq_axes = Axes(
            x_range=[0, 5],
            y_range=[0, 3],
            x_length=8,
            y_length=3,
            tips=False,
        ).to_edge(DOWN)

        freq_title = Text("Frequency Domain (Magnitude)", font_size=28)
        freq_title.next_to(freq_axes, UP)

        bar1 = Rectangle(
            width=0.5,
            height=1.5,
            fill_color=BLUE,
            fill_opacity=0.8
        ).move_to(freq_axes.c2p(1, 0.75))

        bar2 = Rectangle(
            width=0.5,
            height=0.75,
            fill_color=RED,
            fill_opacity=0.8
        ).move_to(freq_axes.c2p(3, 0.375))

        self.play(Create(freq_axes))
        self.play(Write(freq_title))
        self.play(GrowFromEdge(bar1, DOWN))
        self.play(GrowFromEdge(bar2, DOWN))
        self.wait(1)

        # -------------------------------------------------
        # 4️⃣ FINAL MESSAGE
        # -------------------------------------------------
        conclusion = Text(
            "Fourier Transform = Signal → Frequencies",
            font_size=30
        ).to_edge(RIGHT)

        self.play(Write(conclusion))
        self.wait(2)
