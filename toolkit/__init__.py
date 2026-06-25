"""Toolkit reutilizable para presentaciones con Manim Slides.

Re-exporta los componentes principales para que se puedan importar
directamente desde `toolkit`:

    from toolkit import SlidesControl, VideoMobject, ManimGraph
"""

from .canvas import (
    SlidesControl,
    TINY_SIZE,
    TITLE_SIZE,
    NORMAL_SIZE,
    HOME,
)
from .video import VideoMobject
from .graphs import ManimGraph
from .chemistry import (
    mol_to_image,
    dm_mol_to_image,
    mols_to_grid_image,
)

__all__ = [
    "SlidesControl",
    "TINY_SIZE",
    "TITLE_SIZE",
    "NORMAL_SIZE",
    "HOME",
    "VideoMobject",
    "ManimGraph",
    "mol_to_image",
    "dm_mol_to_image",
    "mols_to_grid_image",
]
