"""Template de presentación con Manim Slides.

Define cada sección como una clase `Slide` (versión simple) o
`SlidesControl` (versión con canvas persistente y número de diapositiva).
Renderiza selectivamente y ensambla al final con `manim-slides`.

Render individual:
    manim-slides render presentacion.py Introduccion

Ensamblado final:
    manim-slides convert Introduccion Estructura Funcionamiento Conclusion salida.html
"""

from manim import *
from manim_slides import Slide

from toolkit import NORMAL_SIZE, SlidesControl, TITLE_SIZE

config.verbosity = "WARNING"
config.background_color = WHITE
Text.set_default(color=BLACK)
MathTex.set_default(color=BLACK)

class Introduccion(Slide):
    def construct(self):
        titulo = Text('Introduccion', font_size=TITLE_SIZE)
        
        titulo.to_edge(UP, buff=0.5)

        self.play(Write(titulo))
        self.next_slide()
        self.play(FadeOut(titulo))
        self.wait(1)