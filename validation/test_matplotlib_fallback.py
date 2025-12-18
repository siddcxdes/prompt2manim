from manim import *
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from renderer.actions import EquationAction
from renderer.executor import execute_actions

class TestMatplotlibFallback(Scene):
    def construct(self):
        print("\n--- Testing Matplotlib Fallback ---")
        action = EquationAction(r"\int_{-\infty}^{\infty} f(t) e^{-i\omega t} dt", duration=2)
        execute_actions(self, [action])
        print("--- Test Complete ---")

if __name__ == "__main__":
    try:
        config.preview = False
        config.dry_run = True 
        scene = TestMatplotlibFallback()
        scene.render()
        print("\nMatplotlib Fallback Test completed.")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"\nTest Failed: {e}")
