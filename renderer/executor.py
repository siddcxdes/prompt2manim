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
    GraphAction
)


class ActionExecutor:
    
    def __init__(self, scene):
        self.scene = scene
        self.displayed_objects = []  # Keep track of objects on screen
    
    def execute_action(self, action):
        try:
            if isinstance(action, TextAction):
                self._execute_text_action(action)
            elif isinstance(action, EquationAction):
                self._execute_equation_action(action)
            elif isinstance(action, WaitAction):
                self._execute_wait_action(action)
            elif isinstance(action, ShapeAction):
                self._execute_shape_action(action)
            elif isinstance(action, AnimationAction):
                self._execute_animation_action(action)
            elif isinstance(action, GraphAction):
                self._execute_graph_action(action)
            else:
                print(f"Unknown action type: {type(action).__name__}")
                return False
            return True
        except Exception as error:
            print(f"Error executing action: {error}")
            import traceback
            traceback.print_exc()
            return False
    
    def execute_all_actions(self, actions):
        success_count = 0
        for index, action in enumerate(actions):
            print(f"Executing action {index + 1}/{len(actions)}: {action}")
            if self.execute_action(action):
                success_count += 1
            else:
                print(f"Action {index} failed")
        
        # Hold final frame
        self.scene.wait(1)
        print(f"Execution complete: {success_count}/{len(actions)} actions executed")
        return success_count
    
    def _execute_text_action(self, action):
        text = Text(
            action.content,
            font_size=action.font_size,
            color=WHITE
        )
        
        # Move previous objects up if any
        if self.displayed_objects:
            self.scene.play(
                *[obj.animate.shift(UP * 1.5) for obj in self.displayed_objects],
                run_time=0.5
            )
            
        text.move_to(ORIGIN)
        self.scene.play(Write(text), run_time=1.5)
        
        # Don't wait here - wait is a separate action
        if action.duration > 1.5:
             self.scene.wait(action.duration - 1.5)
             
        self.displayed_objects.append(text)
    
    def _execute_equation_action(self, action):
        equation = None
        try:
            equation = MathTex(
                action.content,
                font_size=action.font_size,
                color=YELLOW
            )
        except Exception as e:
            print(f"Warning: MathTex failed (likely missing LaTeX): {e}")
            # Fallback using Matplotlib
            equation = self._render_math_with_matplotlib(action.content, "yellow", action.font_size)
            if equation is None:
                # Ultimate fallback to Text
                equation = Text(action.content, font_size=action.font_size, color=YELLOW)
        
        if self.displayed_objects:
            self.scene.play(
                *[obj.animate.shift(UP * 2) for obj in self.displayed_objects],
                run_time=0.5
            )
            
        equation.move_to(ORIGIN)
        # Use Write for VMobjects (Text, MathTex), FadeIn for ImageMobject
        if isinstance(equation, VMobject):
            self.scene.play(Write(equation), run_time=1.5)
        else:
            self.scene.play(FadeIn(equation), run_time=1.5)
        
        if action.duration > 1.5:
             self.scene.wait(action.duration - 1.5)
             
        self.displayed_objects.append(equation)
    
    def _render_math_with_matplotlib(self, latex_str, color="white", font_size=12):
        """Render LaTeX math using Matplotlib as fallback when system LaTeX is missing."""
        try:
            # Setup matplotlib figure
            fig = plt.figure(figsize=(6, 1.5), dpi=200)
            fig.patch.set_alpha(0.0)  # Transparent background
            ax = fig.add_axes([0, 0, 1, 1])
            ax.axis('off')
            
            # Wrap in $...$ for matplotlib mathtext
            render_str = f"${latex_str}$"
            
            # Determine color
            text_color = "yellow" if "yellow" in color.lower() else "white"
            
            ax.text(0.5, 0.5, render_str, 
                   fontsize=24, 
                   ha='center', va='center', 
                   color=text_color,
                   transform=ax.transAxes)
            
            # Save to buffer
            buf = io.BytesIO()
            plt.savefig(buf, format='png', transparent=True, bbox_inches='tight', pad_inches=0.1)
            plt.close(fig)
            buf.seek(0)
            
            # Create Manim ImageMobject
            image = Image.open(buf)
            img_array = np.array(image)
            
            mob = ImageMobject(img_array)
            mob.height = 1.2  # Scale to match typical equation size
            return mob
            
        except Exception as e:
            print(f"Matplotlib render failed: {e}")
            return None
    
    def _execute_wait_action(self, action):
        self.scene.wait(action.wait_time)
    
    def _execute_shape_action(self, action):
        shape = self._create_shape(action.shape_type)
        if shape is None:
            return

        shape.set_color(action.color)
        shape.set_stroke(width=action.stroke_width)
        
        # If objects exist, clear them for the shape focus
        if self.displayed_objects:
             self.scene.play(
                *[FadeOut(obj) for obj in self.displayed_objects],
                run_time=0.5
             )
             self.displayed_objects = []

        shape.move_to(ORIGIN)
        self.scene.play(Create(shape), run_time=1.5)
        
        # Perform simple animation based on shape
        if action.duration > 1.5:
            remaining = action.duration - 1.5
            self.scene.play(
                shape.animate.scale(1.1),
                run_time=remaining/2
            )
            self.scene.play(
                shape.animate.scale(1.0),
                run_time=remaining/2
            )
            
        self.displayed_objects.append(shape)
    
    def _execute_animation_action(self, action):
        if not self.displayed_objects:
            return

        target = self.displayed_objects[-1]
        anim_type = action.animation_type.lower().strip()
        duration = action.duration

        if "rotate" in anim_type:
            self.scene.play(Rotate(target, angle=PI*2), run_time=duration)
        elif "scale" in anim_type or "grow" in anim_type:
            self.scene.play(
                target.animate.scale(1.5), 
                run_time=duration/2
            )
            self.scene.play(
                target.animate.scale(1.0), 
                run_time=duration/2
            )
        elif "move" in anim_type:
            direction = RIGHT if "right" in anim_type else LEFT
            self.scene.play(target.animate.shift(direction * 2), run_time=duration)
        elif "transform" in anim_type:
             self.scene.play(Transform(target, Square()), run_time=duration)
        else:
            self.scene.play(Indicate(target), run_time=duration)

    def _create_shape(self, shape_type):
        t = shape_type.lower().strip()
        if "circle" in t: return Circle()
        if "square" in t: return Square()
        if "triangle" in t: return Triangle()
        if "rect" in t: return Rectangle()
        if "star" in t: return Star()
        if "line" in t: return Line(LEFT, RIGHT)
        # Fallback
        return Circle()
    
    def clear_scene(self):
        self.scene.clear()
        self.displayed_objects = []
    
    def get_displayed_count(self):
        return len(self.displayed_objects)
    
    def _execute_graph_action(self, action):
        # Clear previous for clean graph view
        if self.displayed_objects:
             self.scene.play(
                *[FadeOut(obj) for obj in self.displayed_objects],
                run_time=0.5
             )
             self.displayed_objects = []

        # Axes with include_numbers=False to avoid LaTeX dependency
        axes = Axes(
            x_range=action.x_range,
            y_range=action.y_range + [1],
            x_length=8,
            y_length=5,
            axis_config={"include_numbers": False, "include_tip": True},
        )
        
        # Try plotting the function
        try:
            func_str = action.function_str.lower()
            if "sin" in func_str:
                graph = axes.plot(np.sin, color=BLUE)
            elif "cos" in func_str:
                graph = axes.plot(np.cos, color=RED)
            elif "x^2" in func_str or "x**2" in func_str:
                graph = axes.plot(lambda x: x**2, color=GREEN)
            else:
                # Default linear if unknown
                graph = axes.plot(lambda x: x, color=WHITE)
        except:
             graph = axes.plot(lambda x: x, color=WHITE)

        self.scene.play(Create(axes), run_time=1)
        self.scene.play(Create(graph), run_time=2)
        
        if action.duration > 3:
            self.scene.wait(action.duration - 3)
            
        self.displayed_objects.extend([axes, graph])


def execute_actions(scene, actions):
    
    executor = ActionExecutor(scene)
    executor.execute_all_actions(actions)
    return executor


def execute_plan(scene, actions):
    
    return execute_actions(scene, actions)