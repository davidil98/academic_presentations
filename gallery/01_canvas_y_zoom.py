"""Demo: Canvas persistente y ZoomedScene.

Para ejecutar:
    manim-slides render gallery/01_canvas_y_zoom.py DemoCanvasZoom -ql
    manim-slides DemoCanvasZoom
"""

from manim import (
    Circle,
    Create,
    Group,
    GREEN,
    BLUE,
    Rectangle,
    Square,
    Text,
    Title,
    Transform,
    Write,
    YELLOW,
    RIGHT,
    DL,
    UL,
)
from manim_slides import Slide

from toolkit import SlidesControl, TITLE_SIZE


class DemoCanvasZoom(SlidesControl):
    def construct(self):
        # 1) Canvas persistente: título arriba-izquierda, número abajo-izquierda
        titulo = Title("Canvas y Zoom", font_size=TITLE_SIZE).to_corner(UL)
        num = Text("1").to_corner(DL)
        self.add_to_canvas(title=titulo, slide_number=num)
        self.play(Write(titulo), Write(num))
        self.next_slide()

        # 2) Contenido principal con dos mobjects
        circulo = Circle(radius=1.5, color=BLUE).shift(RIGHT * -3)
        cuadrado = Square(side_length=2, color=GREEN).shift(RIGHT * 3)
        self.play(Create(circulo), Create(cuadrado))
        self.next_slide()

        # 3) Limpiar el contenido usando wipe nativo de manim-slides
        #    (el título y el número del canvas permanecen)
        self.wipe(Group(circulo, cuadrado), Group())
        self.next_slide()

        # 4) Incrementar el contador del canvas (Transform nativo)
        old = self.canvas["slide_number"]
        new = Text("2").move_to(old)
        self.play(Transform(old, new))
        self.next_slide()

        # 5) ZoomedScene heredado: preparar un rectángulo para hacer zoom
        objetivo = Rectangle(width=2, height=2, color=YELLOW).shift(RIGHT * 3)
        self.play(Create(objetivo))
        self.next_slide()

        # 6) Activar zoom sobre el rectángulo amarillo
        zoomed_display = self.zoomed_display
        zoomed_display.move_to(objetivo.get_center())
        self.activate_zooming(animate=False)
        self.next_slide()

        # 7) Salir del zoom
        self.activate_zooming(animate=True)
        self.next_slide()

        # 8) Limpiar todo al final (quitar canvas también)
        self.remove_from_canvas("title", "slide_number")
        self.wipe(self.mobjects_without_canvas, Group())
        self.wait()
