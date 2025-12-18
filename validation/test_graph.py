from manim import *
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from renderer.actions import GraphAction
from renderer.executor import execute_actions

class TestGraph(Scene):
    def construct(self):
        print("\n--- Testing Graph Rendering ---")
        action = GraphAction("sin(x)", duration=3)
        execute_actions(self, [action])
        print("--- Test Complete ---")

if __name__ == "__main__":
    try:
        config.preview = False
        config.dry_run = True
        scene = TestGraph()
        scene.render()
        print("\nGraph Test completed.")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"\nTest Failed: {e}")
