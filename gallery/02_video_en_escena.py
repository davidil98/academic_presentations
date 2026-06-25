"""Demo: Video dentro de una escena.

Para ejecutar:
    manim-slides render gallery/02_video_en_escena.py DemoVideo -ql
    manim-slides DemoVideo
"""

import os

from manim import FadeIn, FadeOut, Text, Title, Write
from manim_slides import Slide

from toolkit import VideoMobject


# Busca el primer video disponible en figures/
FIGURES_DIR = os.path.join(os.path.dirname(__file__), "..", "figures")
video_path = None
if os.path.isdir(FIGURES_DIR):
    for fname in sorted(os.listdir(FIGURES_DIR)):
        if fname.lower().endswith((".mp4", ".mov", ".avi")):
            video_path = os.path.join(FIGURES_DIR, fname)
            break


class DemoVideo(Slide):
    def construct(self):
        titulo = Title("Video en escena").to_corner(UL)
        self.play(Write(titulo))
        self.next_slide()

        if video_path is not None:
            video = VideoMobject(video_path, speed=1.0, loop=True)
            video.height = 5
            self.play(FadeIn(video))
            self.next_slide(loop=True)
            self.wait(3)
            self.next_slide()
            self.play(FadeOut(video))
        else:
            placeholder = Text(
                "Coloca un .mp4 en figures/\\npara ver este demo"
            )
            self.play(Write(placeholder))
            self.next_slide()
            self.play(FadeOut(placeholder))

        self.wait()
