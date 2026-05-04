"""
Actions - these are the building blocks of an animation.
Each action type represents something that can happen on screen:
- TextAction: show some text
- EquationAction: show a math equation
- GraphAction: plot a graph
- ShapeAction: draw a shape
- AnimationAction: animate something
- WaitAction: pause
"""


class Action:
    """Base class - all actions have content and duration."""

    def __init__(self, content, duration=1):
        self.content = content
        self.duration = duration

    def get_info(self):
        return {
            "type": self.__class__.__name__,
            "content": self.content,
            "duration": self.duration,
        }

    def __str__(self):
        return self.__class__.__name__ + ": " + str(self.content) + " (" + str(self.duration) + "s)"


class TextAction(Action):
    """Show text on screen."""

    def __init__(self, content, duration=1):
        super().__init__(content, duration)
        self.text = content
        self.font_size = 40

    def get_info(self):
        info = super().get_info()
        info["font_size"] = self.font_size
        return info

    def set_font_size(self, size):
        self.font_size = size
        return self


class EquationAction(Action):
    """Show a math equation."""

    def __init__(self, content, duration=1):
        super().__init__(content, duration)
        self.equation = content
        self.font_size = 36

    def get_info(self):
        info = super().get_info()
        info["font_size"] = self.font_size
        return info

    def set_font_size(self, size):
        self.font_size = size
        return self


class WaitAction(Action):
    """Pause the animation."""

    def __init__(self, content, duration=None):
        # try to convert content to a number
        try:
            wait_seconds = float(content)
        except:
            wait_seconds = 1

        # if no duration given, use the content value
        if duration is None:
            duration = wait_seconds

        super().__init__(content, duration)
        self.wait_time = wait_seconds

    def get_info(self):
        info = super().get_info()
        info["wait_time"] = self.wait_time
        return info


class ShapeAction(Action):
    """Draw a shape."""

    # all the shapes we know how to draw
    KNOWN_SHAPES = [
        "circle", "square", "triangle", "rectangle",
        "line", "star", "dot", "point",
    ]

    def __init__(self, content, duration=1):
        super().__init__(content, duration)
        shape_name = content.lower().strip()

        # check if it's a known shape
        found = False
        for known in self.KNOWN_SHAPES:
            if known in shape_name:
                self.shape_type = known
                found = True
                break

        # if not found, default to circle
        if not found:
            self.shape_type = "circle"

        self.stroke_width = 2
        self.color = "WHITE"

    def get_info(self):
        info = super().get_info()
        info["shape_type"] = self.shape_type
        info["stroke_width"] = self.stroke_width
        info["color"] = self.color
        return info

    def set_color(self, color):
        self.color = color
        return self

    def set_stroke_width(self, width):
        self.stroke_width = width
        return self


class AnimationAction(Action):
    """Animate the previous object."""

    def __init__(self, content, duration=1):
        super().__init__(content, duration)
        self.animation_type = content

    def get_info(self):
        info = super().get_info()
        info["animation_type"] = self.animation_type
        return info


class GraphAction(Action):
    """Plot a math function graph."""

    def __init__(self, content, duration=2):
        super().__init__(content, duration)
        self.function_str = content
        self.x_range = [-4, 4, 1]   # [min, max, step]
        self.y_range = [-3, 3]
        self.color = "BLUE"
        self.show_axes = True

    def get_info(self):
        info = super().get_info()
        info["function"] = self.function_str
        info["x_range"] = self.x_range
        info["y_range"] = self.y_range
        return info

    def set_range(self, x_range, y_range):
        self.x_range = x_range
        self.y_range = y_range
        return self

    def set_color(self, color):
        self.color = color
        return self


# --- Factory: creates the right action from a step dict ---

class ActionFactory:
    """
    Takes a step like {"type": "text", "content": "hello", "duration": 2}
    and creates the matching Action object.
    """

    # map of type name -> action class
    ACTION_MAP = {
        "text": TextAction,
        "equation": EquationAction,
        "wait": WaitAction,
        "shape": ShapeAction,
        "animation": AnimationAction,
        "graph": GraphAction,
    }

    @staticmethod
    def create(step):
        """Create one action from a step dict."""
        step_type = step.get("type", "text").lower()
        content = step.get("content", "")
        duration = step.get("duration", 1)

        # find the right class, default to TextAction
        action_class = ActionFactory.ACTION_MAP.get(step_type, TextAction)

        try:
            action = action_class(content, duration)
            return action
        except Exception as e:
            print("Error creating action: " + str(e))
            return TextAction(content, duration)

    @staticmethod
    def create_all(plan):
        """Create actions for every step in the plan."""
        actions = []
        steps = plan.get("steps", [])

        for step in steps:
            action = ActionFactory.create(step)
            actions.append(action)

        return actions


# --- Utility functions ---

def total_duration(actions):
    """Add up the duration of all actions."""
    total = 0
    for action in actions:
        total = total + action.duration
    return total


def actions_summary(actions):
    """Get a summary of the actions list."""
    summary = {
        "total_actions": len(actions),
        "total_duration": total_duration(actions),
        "action_types": {},
    }

    for action in actions:
        name = action.__class__.__name__
        if name not in summary["action_types"]:
            summary["action_types"][name] = 0
        summary["action_types"][name] = summary["action_types"][name] + 1

    return summary
