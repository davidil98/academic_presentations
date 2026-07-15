"""Demo: Basic usage de SlidesControl paso a paso.

Cubre, en una sola clase:
    1. Mínimo: Slide + next_slide() (espejo del Basic Example oficial).
    2. Configurar canvas: título y número persistentes.
    3. Transformar el canvas: cambiar título y número.
    4. Línea de progresión (timeline) simplificada.
    5. Limpieza: wipe() nativo vs *[] con FadeOut vs clear_canvas().

Para ejecutar:
    manim-slides render gallery/00_basic_usage.py BasicUsage -ql
    manim-slides BasicUsage
"""

from manim import *
from manim_slides import Slide

from toolkit import SlidesControl, NORMAL_SIZE, TITLE_SIZE


def build_timeline(current, total, primary=BLUE, grey=GREY_B, spacing=1.1, radius=0.12):
    """Versión simplificada de la línea de progresión.

    Args:
        current: índice de la sección activa (0-based).
        total: número total de secciones.
        primary: color del nodo activo.
        grey: color de los nodos inactivos y de las barras.
        spacing: separación horizontal entre nodos.
        radius: radio de los nodos inactivos (el activo es ~1.6x).

    La versión de producción está en
    presentaciones/2026-david_ICMAB/david_presentation.py:56 (build_timeline).
    """
    start_x = -((total - 1) * spacing) / 2

    nodes = VGroup()
    for i in range(total):
        is_current = (i == current)
        node = Circle(
            radius=radius * (1.6 if is_current else 1.0),
            color=primary if is_current else grey,
            fill_opacity=1,
        )
        node.move_to([start_x + i * spacing, 0, 0])
        nodes.add(node)

    bars = VGroup()
    for i in range(total - 1):
        bar = Line(
            nodes[i].get_right(),
            nodes[i + 1].get_left(),
            color=grey,
            stroke_width=3,
        )
        bars.add(bar)

    return VGroup(bars, nodes)


class BasicUsage(SlidesControl):
    def construct(self):
        # --- 1. Mínimo: Slide + next_slide() (espejo del Basic Example oficial) ---
        circulo = Circle(radius=2, color=BLUE)
        self.play(Create(circulo))
        self.next_slide()
        self.play(FadeOut(circulo))
        self.next_slide()

        # --- 2. Configurar canvas: título y número persistentes ---
        titulo = Text("Mi sección", font_size=TITLE_SIZE, weight=BOLD).to_corner(UL)
        numero = Text("1", font_size=NORMAL_SIZE).to_corner(DL)
        self.add_to_canvas(title=titulo, slide_number=numero)
        self.play(Write(titulo), Write(numero))
        self.next_slide()

        # --- 3a. Transformar canvas: cambiar el número ---
        old_num = self.canvas["slide_number"]
        new_num = Text("2", font_size=NORMAL_SIZE).move_to(old_num)
        self.play(Transform(old_num, new_num))
        self.next_slide()

        # --- 3b. Transformar canvas: cambiar el título ---
        old_title = self.canvas["title"]
        new_title = Text("Otra sección", font_size=TITLE_SIZE, weight=BOLD).to_corner(UL)
        self.play(FadeOut(old_title), FadeIn(new_title))
        self.canvas["title"] = new_title
        self.next_slide()

        # --- 4. Línea de progresión (timeline) ---
        timeline = build_timeline(current=1, total=4).scale(0.7).to_edge(DOWN, buff=0.6)
        self.add_to_canvas(timeline=timeline)
        self.play(FadeIn(timeline))
        self.next_slide()

        # Avanzar el nodo activo de 1 -> 2
        new_timeline = build_timeline(current=2, total=4).scale(0.7).to_edge(DOWN, buff=0.6)
        self.play(Transform(self.canvas["timeline"], new_timeline))
        self.canvas["timeline"] = new_timeline
        self.next_slide()

        # --- 5a. wipe() nativo: limpia el contenido no-canvas ---
        demo_a = VGroup(Circle(radius=1).shift(LEFT * 3), Square(side_length=2).shift(RIGHT * 3))
        self.play(FadeIn(demo_a))
        self.next_slide()
        self.wipe(demo_a, Group())
        self.next_slide()

        # --- 5b. Patrón *[]: desempaquetar una lista como argumentos ---
        demo_b = VGroup(Circle().shift(LEFT * 2), Square().shift(RIGHT * 2))
        self.play(FadeIn(demo_b))
        self.next_slide()
        # *[] aplica FadeOut a cada mobject no-canvas en una sola llamada.
        # Mismo patrón sirve con self.remove(*[...]) para borrado instantáneo.
        self.play(*[FadeOut(m) for m in self.mobjects_without_canvas])
        self.next_slide()

        # --- 5c. clear_canvas(): limpia canvas + no-canvas (fin de sección) ---
        self.clear_canvas()
        self.wait(0.3)
