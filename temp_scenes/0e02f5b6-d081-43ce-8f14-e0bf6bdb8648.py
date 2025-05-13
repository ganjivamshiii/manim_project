from manim import *
import numpy as np
from math import pi as PI

class FallbackScene(Scene):
    def construct(self):
        title = Text("Animation Example", color=BLUE)
        self.play(Write(title))
        self.wait(0.5)
        
        circle = Circle(color=RED, fill_opacity=0.5)
        self.play(Create(circle))
        
        text = Text("Fallback Animation").scale(0.5).next_to(circle, DOWN)
        self.play(FadeIn(text))
