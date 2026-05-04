from manim import *
import numpy as np
import matplotlib.pyplot as plt
import io
from PIL import Image
from renderer.actions import (
    TextAction,
    EquationAction,
    WaitAction,
    ShapeAction,
    AnimationAction,
    GraphAction,
)


def figure_out_function(func_text):
    """
    Takes a string like "sin(x)" or "x^2" and returns
    a function we can actually use to plot a graph.
    """

    func_text = func_text.strip().lower()

    # simple matches - just check what the string contains
    if "sin" in func_text:
        return np.sin

    if "cos" in func_text:
        return np.cos

    if "tan" in func_text:
        # clip tan so it doesn't go to infinity
        def tan_safe(x):
            result = np.tan(x)
            return np.clip(result, -10, 10)
        return tan_safe

    if "sqrt" in func_text:
        def sqrt_safe(x):
            # only take sqrt of positive numbers
            return np.sqrt(np.maximum(x, 0))
        return sqrt_safe

    if "exp" in func_text:
        def exp_safe(x):
            result = np.exp(x)
            return np.clip(result, -100, 100)
        return exp_safe

    if "log" in func_text:
        def log_safe(x):
            return np.log(np.maximum(x, 0.001))
        return log_safe

    if "x^3" in func_text or "x**3" in func_text:
        def cube(x):
            return x ** 3
        return cube

    if "x^2" in func_text or "x**2" in func_text:
        def square(x):
            return x ** 2
        return square

    if "abs" in func_text:
        return np.abs

    # if nothing matched, just plot y = x (a straight line)
    def linear(x):
        return x
    return linear


class ActionExecutor:
    """
    This class takes actions (like TextAction, GraphAction, etc.)
    and actually shows them on screen using Manim.
    """

    def __init__(self, scene):
        # the manim scene we're drawing on
        self.scene = scene
        # list of things currently on screen
        self.objects_on_screen = []

    def run_all(self, actions):
        """Run every action in the list, one by one."""
        done = 0
        total = len(actions)

        for i in range(total):
            action = actions[i]
            print("Running action " + str(i + 1) + "/" + str(total) + ": " + str(action))

            worked = self.run_one(action)
            if worked:
                done = done + 1
            else:
                print("Action " + str(i + 1) + " failed, skipping it.")

        # hold the last frame for a second
        self.scene.wait(1)
        print("Done! " + str(done) + "/" + str(total) + " actions worked.")
        return done

    def run_one(self, action):
        """Run a single action. Returns True if it worked, False if not."""
        try:
            # check what type of action it is and run the right method
            if isinstance(action, TextAction):
                self.show_text(action)
            elif isinstance(action, EquationAction):
                self.show_equation(action)
            elif isinstance(action, WaitAction):
                self.do_wait(action)
            elif isinstance(action, ShapeAction):
                self.show_shape(action)
            elif isinstance(action, AnimationAction):
                self.do_animation(action)
            elif isinstance(action, GraphAction):
                self.show_graph(action)
            else:
                print("Unknown action type: " + type(action).__name__)
                return False
            return True

        except Exception as error:
            print("Error running action: " + str(error))
            return False

    # --- TEXT ---
    def show_text(self, action):
        """Show text on screen."""
        text = Text(
            action.content,
            font_size=action.font_size,
            color=WHITE,
        )

        # if there's stuff already on screen, push it up
        if len(self.objects_on_screen) > 0:
            animations = []
            for obj in self.objects_on_screen:
                animations.append(obj.animate.shift(UP * 1.5))
            self.scene.play(*animations, run_time=0.5)

        text.move_to(ORIGIN)
        self.scene.play(Write(text), run_time=1.5)

        # wait for remaining duration
        if action.duration > 1.5:
            self.scene.wait(action.duration - 1.5)

        self.objects_on_screen.append(text)

    # --- EQUATION ---
    def show_equation(self, action):
        """Show a math equation on screen."""
        equation = None

        # try using MathTex first (needs LaTeX installed)
        try:
            equation = MathTex(
                action.content,
                font_size=action.font_size,
                color=YELLOW,
            )
        except Exception as e:
            print("MathTex failed, trying fallback: " + str(e))
            # try matplotlib as backup
            equation = self.make_equation_image(action.content, action.font_size)
            if equation is None:
                # last resort: just show it as plain text
                equation = Text(action.content, font_size=action.font_size, color=YELLOW)

        # push existing stuff up
        if len(self.objects_on_screen) > 0:
            animations = []
            for obj in self.objects_on_screen:
                animations.append(obj.animate.shift(UP * 2))
            self.scene.play(*animations, run_time=0.5)

        equation.move_to(ORIGIN)

        # use Write for text/math objects, FadeIn for images
        if isinstance(equation, VMobject):
            self.scene.play(Write(equation), run_time=1.5)
        else:
            self.scene.play(FadeIn(equation), run_time=1.5)

        if action.duration > 1.5:
            self.scene.wait(action.duration - 1.5)

        self.objects_on_screen.append(equation)

    def make_equation_image(self, latex_text, font_size):
        """
        If MathTex doesn't work (no LaTeX installed),
        use matplotlib to render the equation as an image.
        """
        try:
            fig = plt.figure(figsize=(6, 1.5), dpi=200)
            fig.patch.set_alpha(0.0)
            ax = fig.add_axes([0, 0, 1, 1])
            ax.axis("off")

            ax.text(
                0.5, 0.5,
                "$" + latex_text + "$",
                fontsize=24,
                ha="center", va="center",
                color="yellow",
                transform=ax.transAxes,
            )

            buf = io.BytesIO()
            plt.savefig(buf, format="png", transparent=True, bbox_inches="tight", pad_inches=0.1)
            plt.close(fig)
            buf.seek(0)

            image = Image.open(buf)
            img_array = np.array(image)
            mob = ImageMobject(img_array)
            mob.height = 1.2
            return mob

        except Exception as e:
            print("Matplotlib fallback also failed: " + str(e))
            return None

    # --- WAIT ---
    def do_wait(self, action):
        """Just pause for a bit."""
        self.scene.wait(action.wait_time)

    # --- SHAPE ---
    def show_shape(self, action):
        """Draw a shape on screen."""
        shape = self.make_shape(action.shape_type)

        shape.set_color(action.color)
        shape.set_stroke(width=action.stroke_width)

        # clear the screen first so the shape has room
        if len(self.objects_on_screen) > 0:
            fade_outs = []
            for obj in self.objects_on_screen:
                fade_outs.append(FadeOut(obj))
            self.scene.play(*fade_outs, run_time=0.5)
            self.objects_on_screen = []

        shape.move_to(ORIGIN)
        self.scene.play(Create(shape), run_time=1.5)

        # do a little pulse animation if there's time
        if action.duration > 1.5:
            leftover = action.duration - 1.5
            self.scene.play(shape.animate.scale(1.1), run_time=leftover / 2)
            self.scene.play(shape.animate.scale(1.0), run_time=leftover / 2)

        self.objects_on_screen.append(shape)

    def make_shape(self, shape_name):
        """Create a manim shape object from a name."""
        name = shape_name.lower().strip()

        if "circle" in name:
            return Circle()
        if "square" in name:
            return Square()
        if "triangle" in name:
            return Triangle()
        if "rect" in name:
            return Rectangle()
        if "star" in name:
            return Star()
        if "line" in name:
            return Line(LEFT, RIGHT)

        # default to circle
        return Circle()

    # --- ANIMATION ---
    def do_animation(self, action):
        """Animate the last object on screen."""
        # need something on screen to animate
        if len(self.objects_on_screen) == 0:
            return

        target = self.objects_on_screen[-1]
        anim_type = action.animation_type.lower().strip()
        duration = action.duration

        if "rotate" in anim_type:
            self.scene.play(Rotate(target, angle=PI * 2), run_time=duration)
        elif "scale" in anim_type or "grow" in anim_type:
            self.scene.play(target.animate.scale(1.5), run_time=duration / 2)
            self.scene.play(target.animate.scale(1.0), run_time=duration / 2)
        elif "move" in anim_type:
            self.scene.play(target.animate.shift(RIGHT * 2), run_time=duration)
        else:
            self.scene.play(Indicate(target), run_time=duration)

    # --- GRAPH ---
    def show_graph(self, action):
        """Plot a mathematical function."""
        # clear screen for the graph
        if len(self.objects_on_screen) > 0:
            fade_outs = []
            for obj in self.objects_on_screen:
                fade_outs.append(FadeOut(obj))
            self.scene.play(*fade_outs, run_time=0.5)
            self.objects_on_screen = []

        # create the axes (the x and y lines)
        axes = Axes(
            x_range=action.x_range,
            y_range=action.y_range + [1],
            x_length=8,
            y_length=5,
            axis_config={"include_numbers": False, "include_tip": True},
        )

        # figure out which function to plot
        func = figure_out_function(action.function_str)

        # plot the function
        try:
            graph = axes.plot(func, color=BLUE)
        except:
            # if it fails, just plot a straight line
            graph = axes.plot(lambda x: x, color=WHITE)

        # animate it
        self.scene.play(Create(axes), run_time=1)
        self.scene.play(Create(graph), run_time=2)

        if action.duration > 3:
            self.scene.wait(action.duration - 3)

        self.objects_on_screen.append(axes)
        self.objects_on_screen.append(graph)


# --- helper functions that other files use ---

def execute_actions(scene, actions):
    """Create an executor and run all actions."""
    executor = ActionExecutor(scene)
    executor.run_all(actions)
    return executor


def execute_plan(scene, actions):
    """Same as execute_actions (kept for compatibility)."""
    return execute_actions(scene, actions)