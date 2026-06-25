"""Helpers para crear gráficas de espectros en Manim.

`ManimGraph` desacopla la creación de ejes, el graficado de datos y la
construcción de leyendas para mayor flexibilidad.

Uso:
    from toolkit import ManimGraph

    helper = ManimGraph(scene)
    axes = helper.setup_axes("λ (nm)", "Abs", [300, 800, 50], [0, 1, 0.2])
    curve = helper.plot_spectrum("datos/espectro.txt", color=BLUE)
    scene.play(Create(axes), Create(curve))
"""

import numpy as np
from manim import *
from scipy.signal import savgol_filter


class ManimGraph:
    """Wrapper para configurar ejes, graficar espectros y crear leyendas.

    Requiere que el archivo de datos tenga dos columnas (x, y) sin encabezado.
    """

    def __init__(self, escena):
        self.escena = escena
        self.axes = None
        self.x_range = None
        self.y_range = None

    def setup_axes(
        self,
        x_label,
        y_label,
        x_range,
        y_range,
        x_length=8,
        y_length=5,
        **kwargs,
    ):
        """Crea ejes con etiquetas y los devuelve como VGroup."""
        self.x_range = x_range
        self.y_range = y_range

        decimal_config = {
            "group_with_commas": False,
            "num_decimal_places": 0,
        }

        self.axes = Axes(
            x_range=self.x_range,
            y_range=self.y_range,
            x_length=x_length,
            y_length=y_length,
            axis_config={"include_tip": False, "color": GREY},
            x_axis_config={"decimal_number_config": decimal_config},
            y_axis_config={"decimal_number_config": decimal_config},
            **kwargs,
        ).add_coordinates()

        x_ax_label = self.axes.get_x_axis_label(
            Tex(x_label), edge=DOWN, direction=DOWN, buff=0.35
        )
        y_ax_label = self.axes.get_y_axis_label(
            Tex(y_label).rotate(90 * DEGREES), edge=LEFT, direction=LEFT, buff=0.35
        )

        self.axes_with_labels = VGroup(self.axes, x_ax_label, y_ax_label)
        return self.axes_with_labels

    def plot_spectrum(self, filepath, color, smooth=False):
        """Carga datos de un archivo de 2 columnas y los grafica.

        Devuelve el objeto de la curva para que puedas animarlo por separado.
        """
        if self.axes is None:
            raise Exception("Debes llamar a setup_axes() antes de plot_spectrum()")

        try:
            data = np.loadtxt(filepath)
        except Exception:
            # Si el archivo tiene encabezado, intentar con pandas como fallback
            import pandas as pd

            data = pd.read_csv(filepath, sep=None, engine="python").to_numpy()

        x_min, x_max = self.x_range[:2]
        mask = (data[:, 0] >= x_min) & (data[:, 0] <= x_max)
        x_data = data[mask, 0]
        y_data = data[mask, 1]

        y_min, y_max = self.y_range[:2]
        y_data = np.clip(y_data, y_min, y_max)

        if smooth:
            window_length = min(15, len(y_data))
            if window_length % 2 == 0:
                window_length -= 1
            if window_length > 1:
                y_data = savgol_filter(y_data, window_length=window_length, polyorder=2)

        graph = self.axes.plot_line_graph(
            x_values=x_data,
            y_values=y_data,
            line_color=color,
            add_vertex_dots=False,
        )
        return graph

    def create_legend(self, legend_items, position=UR, buff=0.2):
        """Crea un bloque de leyenda posicionado en una esquina del gráfico.

        Args:
            legend_items: lista de dicts, ej. [{"text": "Mi curva", "color": BLUE}].
            position: esquina de anclaje (UR, UL, DR, DL).
            buff: margen desde la esquina.
        """
        if self.axes is None:
            raise Exception("Debes configurar los ejes con setup_axes() primero.")

        labels = VGroup()
        for item in legend_items:
            label = Tex(item["text"], color=item["color"], font_size=28)
            labels.add(label)

        labels.arrange(DOWN, aligned_edge=LEFT, buff=0.15)

        opposite_direction = -position
        labels.next_to(self.axes.get_corner(position), opposite_direction, buff=buff)

        return labels
