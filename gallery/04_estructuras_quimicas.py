"""Demo: Estructuras químicas con RDKit/Datamol.

Para ejecutar:
    manim-slides render gallery/04_estructuras_quimicas.py DemoQuimica -ql
    manim-slides DemoQuimica
"""

from manim import DOWN, FadeIn, FadeOut, ImageMobject, Text, Title, Write
from manim_slides import Slide

from toolkit import mol_to_image, mols_to_grid_image


EJEMPLOS = {
    "benceno": "c1ccccc1",
    "cafeína": "CN1C=NC2=C1C(=O)N(C(=O)N2C)C",
    "aspirina": "CC(=O)OC1=CC=CC=C1C(=O)O",
    "glucosa": "OCC1OC(O)C(O)C(O)C1O",
}


class DemoQuimica(Slide):
    def construct(self):
        titulo = Title("Estructuras químicas con RDKit").to_corner(UL)
        self.play(Write(titulo))
        self.next_slide()

        # 1) Benceno
        mol_benceno = mol_to_image(EJEMPLOS["benceno"], size=(400, 400))
        img_benceno = ImageMobject(mol_benceno).scale_to_fit_height(4)
        caption_benceno = Text("Benceno (C6H6)", font_size=28).next_to(
            img_benceno, DOWN, buff=0.3
        )
        self.play(FadeIn(img_benceno), Write(caption_benceno))
        self.next_slide()

        # 2) Cafeína
        self.play(
            FadeOut(img_benceno),
            FadeOut(caption_benceno),
        )
        self.next_slide()

        mol_cafeina = mol_to_image(EJEMPLOS["cafeína"], size=(500, 500))
        img_cafeina = ImageMobject(mol_cafeina).scale_to_fit_height(4)
        caption_cafeina = Text("Cafeína (C8H10N4O2)", font_size=28).next_to(
            img_cafeina, DOWN, buff=0.3
        )
        self.play(FadeIn(img_cafeina), Write(caption_cafeina))
        self.next_slide()

        # 3) Grid de varias moléculas
        self.play(
            FadeOut(img_cafeina),
            FadeOut(caption_cafeina),
        )
        self.next_slide()

        grid = mols_to_grid_image(
            list(EJEMPLOS.values()),
            size=(200, 150),
            legends=list(EJEMPLOS.keys()),
        )
        img_grid = ImageMobject(grid).scale_to_fit_width(11)
        self.play(FadeIn(img_grid))
        self.next_slide()

        self.wait()
