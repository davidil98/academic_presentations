"""Canvas persistente y control de diapositivas.

Este módulo proporciona `SlidesControl`, una clase base que combina
`Slide` (de manim-slides) y `ZoomedScene` (de manim).

Uso:
    from toolkit import SlidesControl

    class MiSeccion(SlidesControl):
        def construct(self):
            self.slide_count = 1
            titulo = Text("Mi sección").to_corner(UL)
            num = Text("1").to_corner(DL)
            self.add_to_canvas(title=titulo, slide_number=num)
            self.play(FadeIn(titulo), FadeIn(num))
            self.next_slide()

            # Contenido de la diapositiva...
            circulo = Circle()
            self.play(Create(circulo))
            self.next_slide()

            # Incrementar número de diapositiva
            self.slide_count += 1
            old = self.canvas["slide_number"]
            new = Text(str(self.slide_count)).move_to(old)
            self.play Transform(old, new)

            # Limpiar solo el contenido (canvas persiste)
            self.wipe(self.mobjects_without_canvas, Square())
            self.next_slide()

Nota: toda la lógica de canvas (add_to_canvas, remove_from_canvas,
mobjects_without_canvas, wipe, zoom) viene de manim-slides.
"""

from manim import *
from manim_slides import Slide

TINY_SIZE = 17
TITLE_SIZE = 50
NORMAL_SIZE = 30

HOME = "figures"


class SlidesControl(Slide, ZoomedScene):
    pass
