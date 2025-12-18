from manim import *
import numpy as np

# Manim Community Edition (CE)
# This scene visually explains the Fourier Transform using graphs and animations.
# Concept shown:
# 1) A time-domain signal (sum of sinusoids)
# 2) Rotating complex vectors (phasors) contributing to the signal
# 3) Frequency-domain magnitude spectrum

class FourierTransformExplanation(Scene):
    def construct(self):
        #-----------------------------
        # 1. TIME-DOMAIN AXES & SIGNAL
        #-----------------------------
        time_axes = Axes(
            x_range=[0, 10, 1],
            y_range=[-3, 3, 1],
            x_length=8,
            y_length=3,
            axis_config={"include_numbers": True},
        ).to_edge(UP)

        time_label = Text("Time Domain Signal", font_size=28).next_to(time_axes, UP)

        # Define the signal: sum of two sinusoids
        def time_signal(t):
            return np.sin(2 * np.pi * 1 * t) + 0.5 * np.sin(2 * np.pi * 3 * t)

        signal_graph = time_axes.plot(
            time_signal,
            x_range=[0, 10],
            color=BLUE,
        )

        self.play(Create(time_axes), Write(time_label))
        self.play(Create(signal_graph))
        self.wait(1)

        # -----------------------------
        # 2. ROTATING VECTORS (PHASORS)
        # -----------------------------
        phasor_origin = ORIGIN + DOWN * 0.5
        circle1 = Circle(radius=1, color=GRAY).move_to(phasor_origin)
        circle2 = Circle(radius=0.5, color=GRAY).move_to(phasor_origin)

        angle = ValueTracker(0)

        vector1 = always_redraw(
            lambda: Arrow(
                phasor_origin,
                phasor_origin + np.array([
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
                phasor_origin,
                phasor_origin + np.array([
                    0.5 * np.cos(3 * angle.get_value()),
                    0.5 * np.sin(3 * angle.get_value()),
                    0
                ]),
                buff=0,
                color=RED
            )
        )

        phasor_text = Text("Rotating Vectors (Frequencies)", font_size=26)
        phasor_text.next_to(phasor_origin, DOWN)

        self.play(Create(circle1), Create(circle2), Write(phasor_text))
        self.play(Create(vector1), Create(vector2))
        self.play(angle.animate.set_value(4 * PI), run_time=4, rate_func=linear)
        self.wait(1)

        # -----------------------------
        # 3. FREQUENCY-DOMAIN AXES
        # -----------------------------
        freq_axes = Axes(
            x_range=[0, 5, 1],
            y_range=[0, 3, 1],
            x_length=8,
            y_length=3,
            axis_config={"include_numbers": True},
        ).to_edge(DOWN)

        freq_label = Text("Frequency Domain (Magnitude)", font_size=28)
        freq_label.next_to(freq_axes, UP)

        # Frequency bars representing amplitudes
        bar1 = Rectangle(
            width=0.5,
            height=1.5,
            fill_color=BLUE,
            fill_opacity=0.8,
        ).move_to(freq_axes.c2p(1, 0.75))

        bar2 = Rectangle(
            width=0.5,
            height=0.75,
            fill_color=RED,
            fill_opacity=0.8,
        ).move_to(freq_axes.c2p(3, 0.375))

        self.play(Create(freq_axes), Write(freq_label))
        self.play(GrowFromEdge(bar1, DOWN), GrowFromEdge(bar2, DOWN))
        self.wait(2)

        # -----------------------------
        # 4. FINAL EXPLANATION TEXT
        # -----------------------------
        final_text = Text(
            "Fourier Transform decomposes a signal\n"
            "into its frequency components",
            font_size=30,
        ).to_edge(RIGHT)

        self.play(Write(final_text))
        self.wait(3)

# Run using:
# manim -pql filename.py FourierTransformExplanation
# (Use -pqh or -pqm for higher quality)
