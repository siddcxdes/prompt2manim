import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from manim import *
from renderer.actions import ActionFactory
from renderer.executor import execute_actions
import json

class TestScene(Scene):
    def construct(self):
        # Mock plan with various action types
        plan = {
            "steps": [
                {"type": "text", "content": "Testing Fixes", "duration": 2},
                {"type": "shape", "content": "square", "duration": 2},
                {"type": "shape", "content": "triangle", "duration": 2}, # Was failing?
                {"type": "graph", "content": "sin(x)", "duration": 3},
                {"type": "wait", "content": "1", "duration": 1}
            ]
        }
        
        print("Creating actions...")
        actions = ActionFactory.create_all(plan)
        for a in actions:
            print(f"Created: {a}")
            
        print("\nExecuting actions...")
        executor = execute_actions(self, actions)
        print(f"\nTotal actions executed: {len(actions)}")
        print(f"Objects remaining on screen: {executor.get_displayed_count()}")

if __name__ == "__main__":
    # Render low quality for speed
    config.quality = "low_quality"
    config.preview = False
    scene = TestScene()
    scene.render()
