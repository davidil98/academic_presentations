"""Canvas persistente y control de diapositivas.

Este módulo proporciona `SlidesControl`, una clase base que combina
`Slide` (de manim-slides) y `ZoomedScene` (de manim), y añade un
método `clear_canvas` que encapsula el patrón de limpieza al final
de una sección.

Patrón de canvas
----------------
`self.canvas` es un dict `nombre -> Mobject` para objetos que deben
**persistir** entre diapositivas (título de sección, número, timeline,
etc.).

Reglas (de `manim_slides.slide.base`):
- `add_to_canvas(...)` solo guarda referencias; **no** agrega a la
  escena. Hay que animar/añadir aparte (típicamente con `Write`,
  `FadeIn` o `self.add`).
- `mobjects_without_canvas` = `self.mobjects` - canvas. Es lo que
  pasas a `wipe()` para limpiar el contenido "no persistente" y
  dejar el canvas intacto.
- `remove_from_canvas(...)` solo borra del dict; **no** borra de la
  escena. Hay que wipear aparte.
- `wipe(current, future)` hace `FadeOut` de `current` y `FadeIn` de
  `future`. Pasar `Group()` como `future` = solo fade-out.

Patrón recomendado de fin de sección
------------------------------------
    self.wipe(self.mobjects_without_canvas, Group())   # limpia no-canvas
    self.remove_from_canvas("title", "slide_number", "timeline")
    self.wipe(self.mobjects_without_canvas, Group())   # ahora limpia el canvas

O, equivalentemente, en una sola llamada:

    self.clear_canvas()

Uso básico
----------
    from toolkit import SlidesControl

    class MiSeccion(SlidesControl):
        def construct(self):
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
            old = self.canvas["slide_number"]
            new = Text("2").move_to(old)
            self.play(Transform(old, new))

            # Limpiar todo (canvas + no-canvas)
            self.clear_canvas()
            self.wait(0.3)

Nota: `add_to_canvas`, `remove_from_canvas`, `mobjects_without_canvas`,
`wipe` y `zoom` vienen de manim-slides.
"""

from manim import *
from manim_slides import Slide

TINY_SIZE = 17
TITLE_SIZE = 50
NORMAL_SIZE = 30

HOME = "figures"


class SlidesControl(Slide, ZoomedScene):
    """Clase base para escenas con canvas persistente.

    Hereda de `manim_slides.Slide` y `manim.ZoomedScene`, y añade
    `clear_canvas`. El resto del comportamiento de canvas
    (`add_to_canvas`, `remove_from_canvas`, `mobjects_without_canvas`,
    `wipe`) lo aporta `manim_slides`.

    Ver el docstring del módulo para las reglas y el patrón de uso.
    """

    def clear_canvas(self):
        """Limpia TODO el contenido de la escena y vacía el dict del canvas.

        Pasos (siguiendo el patrón de la docstring de
        `manim_slides.slide.base.BaseSlide.canvas`):

        1. `remove_from_canvas(*canvas.keys())` — saca las referencias
           del dict, para que los antiguos canvas-items pasen a
           contarse como `mobjects_without_canvas`.
        2. `wipe(self.mobjects_without_canvas, Group())` — fade-out
           de todo lo que quede en la escena (lo que antes era canvas
           + lo que nunca estuvo en canvas).

        Después de esta llamada, `self.mobjects` queda vacío y
        `self.canvas == {}`. Es lo que típicamente cierra una sección
        antes de pasar a la siguiente o terminar la presentación.

        Equivale a:

            self.wipe(self.mobjects_without_canvas, Group())
            self.remove_from_canvas("title", "slide_number", "timeline")
            self.wipe(self.mobjects_without_canvas, Group())

        Uso:
            setup_canvas(self, "Roots", 4, 1)
            # ... contenido de la sección ...
            self.next_slide()
            update_slide_number(self, 5)
            # ... más contenido ...
            self.clear_canvas()    # fin de la sección
            self.wait(0.3)
        """
        if self.canvas:
            self.remove_from_canvas(*list(self.canvas.keys()))
        self.wipe(self.mobjects_without_canvas, Group())
