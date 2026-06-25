"""Demo: Gráficos de espectros con ManimGraph.

Para ejecutar:
    manim-slides render gallery/03_graficos_espectros.py DemoEspectro -ql
    manim-slides DemoEspectro
"""

import os

import numpy as np

from manim import (
    BLUE,
    Create,
    Dot,
    FadeIn,
    GREEN,
    MathTex,
    RED,
    Title,
    UP,
    UR,
    WHITE,
    Write,
)
from manim_slides import Slide

from toolkit import ManimGraph


# Generar datos sintéticos para probar sin un archivo real
rng = np.random.default_rng(42)
x = np.linspace(300, 800, 200)
y = np.exp(-((x - 500) ** 2) / (2 * 30 ** 2)) + 0.1 * rng.random(200)
data_path = "/tmp/espectro_demo.txt"
np.savetxt(data_path, np.column_stack([x, y]))


class DemoEspectro(Slide):
    def construct(self):
        titulo = Title("Espectro de absorción").to_corner(UL)
        self.play(Write(titulo))
        self.next_slide()

        helper = ManimGraph(self)
        axes = helper.setup_axes(
            x_label=r"\lambda \,(\mathrm{nm})",
            y_label="Absorbancia",
            x_range=[300, 800, 50],
            y_range=[0, 1.2, 0.2],
        )
        self.play(Create(axes))
        self.next_slide()

        # 1) Graficar curva cruda
        curva_cruda = helper.plot_spectrum(data_path, color=BLUE, smooth=False)
        self.play(Create(curva_cruda), run_time=2)
        self.next_slide()

        # 2) Graficar curva suavizada encima
        curva_suave = helper.plot_spectrum(data_path, color=GREEN, smooth=True)
        self.play(Create(curva_suave), run_time=2)
        self.next_slide()

        # 3) Añadir leyenda
        leyenda = helper.create_legend(
            [
                {"text": "Crudo", "color": BLUE},
                {"text": "Suavizado (Savitzky-Golay)", "color": GREEN},
            ],
            position=UR,
        )
        self.play(Write(leyenda))
        self.next_slide()

        # 4) Marcar el máximo
        idx_max = int(np.argmax(y))
        x_max, y_max = float(x[idx_max]), float(y[idx_max])
        punto_max = Dot(helper.axes.coords_to_point(x_max, y_max), color=RED)
        etiqueta_max = MathTex(
            f"\\lambda_{{max}} = {x_max:.0f}\\;\\mathrm{{nm}}",
            color=WHITE,
            font_size=28,
        ).next_to(punto_max, UP, buff=0.2)
        self.play(FadeIn(punto_max), Write(etiqueta_max))
        self.next_slide()

        self.wait()
