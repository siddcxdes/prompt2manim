from manim import *
from renderer.actions import ActionFactory
from renderer.executor import execute_actions


class GeneratedScene(Scene):

    def __init__(self, plan=None, **kwargs):
 
        super().__init__(**kwargs)
        self.plan = plan
        self.actions = []
    
    def construct(self):

        if self.plan is None:
            print("error: no plan provided to scene")
            self._show_error_message()
            return

        print("creating actions from plan...")
        try:
            self.actions = ActionFactory.create_all(self.plan)
            print(f"created {len(self.actions)} actions")
        except Exception as error:
            print(f"error creating actions: {error}")
            self._show_error_message()
            return
        
        print("executing actions...")
        try:
            execute_actions(self, self.actions)
            print("all actions executed successfully!")
        except Exception as error:
            print(f"error executing actions: {error}")
            self._show_error_message()
    
    def _show_error_message(self):
        error_text = Text("Error in animation", font_size=40, color=RED)
        self.play(Write(error_text))
        self.wait(2)
        self.play(FadeOut(error_text))


class SimpleScene(Scene):
    def construct(self):
        text = Text("Hello Manim!", font_size=50, color=BLUE)

        self.play(Write(text))
        self.wait(2)
        self.play(FadeOut(text))


class TestScene(Scene):
    def construct(self):
        from renderer.actions import TextAction, EquationAction, WaitAction
        
        actions = [
            TextAction("Pythagorean Theorem", duration=2),
            EquationAction("a^2 + b^2 = c^2", duration=2),
            WaitAction("1"),
            TextAction("The End", duration=1)
        ]
        execute_actions(self, actions)

def create_scene_from_plan(plan, **kwargs):
    
    scene = GeneratedScene(plan=plan, **kwargs)
    return scene


def create_fullscreen_scene(plan):
    config.pixel_height = 1080
    config.pixel_width = 1920
    config.frame_rate = 60
    
    return create_scene_from_plan(plan)


def create_hd_scene(plan):
    
    config.pixel_height = 720
    config.pixel_width = 1280
    config.frame_rate = 30
    
    return create_scene_from_plan(plan)


def create_preview_scene(plan):

    config.pixel_height = 480
    config.pixel_width = 854
    config.frame_rate = 15
    config.preview = True
    
    return create_scene_from_plan(plan)

def get_scene_config(quality="hd"):
    configs = {
        "preview": {
            "pixel_height": 480,
            "pixel_width": 854,
            "frame_rate": 15,
        },
        "hd": {
            "pixel_height": 720,
            "pixel_width": 1280,
            "frame_rate": 30,
        },
        "fullscreen": {
            "pixel_height": 1080,
            "pixel_width": 1920,
            "frame_rate": 60,
        },
        "4k": {
            "pixel_height": 2160,
            "pixel_width": 3840,
            "frame_rate": 30,
        }
    }
    
    return configs.get(quality, configs["hd"])


def apply_scene_config(quality="hd"):
    config_dict = get_scene_config(quality)
    
    config.pixel_height = config_dict["pixel_height"]
    config.pixel_width = config_dict["pixel_width"]
    config.frame_rate = config_dict["frame_rate"]
    
    print(f"applied {quality} configuration")
    print(f"   resolution: {config.pixel_width}x{config.pixel_height}")
    print(f"   fps: {config.frame_rate}")