'''this is used to create actions, example textAction, graphAction basically this will specify what actions should the executor takes'''
class Action:
    def __init__(self, content, duration=1):

        self.content = content
        self.duration = duration
    
    def get_info(self):
        
        return {
            "type": self.__class__.__name__,
            "content": self.content,
            "duration": self.duration
        }
    
    def __str__(self):
    
        return f"{self.__class__.__name__}: {self.content} ({self.duration}s)"



class TextAction(Action):
    """action for displaying text.
    example:
        action = TextAction("Hello World", duration=2)
        # shows "Hello World" on screen for 2 seconds
    """
    
    def __init__(self, content, duration=1):
        
        super().__init__(content, duration)
        self.text = content
        self.font_size = 40  # Default font size
    
    def get_info(self):
        info = super().get_info()
        info["font_size"] = self.font_size
        return info
    
    def set_font_size(self, size):
        self.font_size = size
        return self


class EquationAction(Action):

    def __init__(self, content, duration=1):
        super().__init__(content, duration)
        self.equation = content
        self.font_size = 36  # Default font size for equations
    
    def get_info(self):
        info = super().get_info()
        info["font_size"] = self.font_size
        return info
    
    def set_font_size(self, size):
        self.font_size = size
        return self


class WaitAction(Action):
    def __init__(self, content, duration=None):
        try:
            wait_seconds = float(content)
        except ValueError:
            wait_seconds = 1  

        if duration is None:
            duration = wait_seconds
        
        super().__init__(content, duration)
        self.wait_time = wait_seconds
    
    def get_info(self):
        info = super().get_info()
        info["wait_time"] = self.wait_time
        return info


class ShapeAction(Action):
    VALID_SHAPES = {
        "circle", "square", "triangle", "rectangle", "line", "star",
        "circ", "sq", "tri", "rect", "dot", "point"
    }

    def __init__(self, content, duration=1):
        super().__init__(content, duration)
        raw_type = content.lower().strip()
        self.shape_type = raw_type
        
        # Validation
        if raw_type not in self.VALID_SHAPES:
            # Partial match check
            for valid in self.VALID_SHAPES:
                if valid in raw_type:
                    self.shape_type = valid
                    break
            else:
                 # Default fallback
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
    def __init__(self, content, duration=1):
        super().__init__(content, duration)
        self.animation_type = content
    
    def get_info(self):
        info = super().get_info()
        info["animation_type"] = self.animation_type
        return info


class GraphAction(Action):
    """Action for displaying mathematical graphs/plots.
    
    Examples:
        action = GraphAction("sin(x)", duration=3)  # plots y = sin(x)
        action = GraphAction("x**2", duration=2)    # plots y = x²
    """
    
    def __init__(self, content, duration=2):
        super().__init__(content, duration)
        self.function_str = content
        self.x_range = [-4, 4, 1]  # [min, max, step]
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


'''this class helps in checking the input and using the respective output'''
class ActionFactory:
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
        
        step_type = step.get("type", "text").lower()
        content = step.get("content", "")
        duration = step.get("duration", 1)
        
        action_class = ActionFactory.ACTION_MAP.get(step_type, TextAction)
        
        try:
            action = action_class(content, duration)
            return action
        except Exception as e:
            print(f"error creating action: {e}")
            return TextAction(content, duration)
    
    @staticmethod
    def create_all(plan):
        actions = []
        
        for step in plan.get("steps", []):
            action = ActionFactory.create(step)
            actions.append(action)
        
        return actions

def print_action_info(action):
    info = action.get_info()
    print(f"action type: {info['type']}")
    print(f"content: {info['content']}")
    print(f"duration: {info['duration']} seconds")
    print()


def total_duration(actions):
    total = 0
    for action in actions:
        total += action.duration
    return total


def actions_summary(actions):
    summary = {
        "total_actions": len(actions),
        "total_duration": total_duration(actions),
        "action_types": {}
    }
    
    for action in actions:
        action_type = action.__class__.__name__
        if action_type not in summary["action_types"]:
            summary["action_types"][action_type] = 0
        summary["action_types"][action_type] += 1
    
    return summary
