"""David Ibarra — Presentation at ICMAB (Nanomol-Mat, 2025).

Image-heavy introduction with a persistent timeline canvas.
Each section is a SlidesControl class with title, slide number and a
horizontal progress timeline that highlight the current section.

Expected images (place in the assets/ folder):

  Section 1 (Who am I):     me.jpg, calisthenics.jpg, cooking.jpg, poetry.jpg
  Section 2 (Roots):        father_lab.jpg, mother_class.jpg, high_school.jpg
  Section 3 (Formation):    uanl.jpg, lab_food.jpg, cqd_paper_cover.jpg
  Section 4 (Impact):       drought.jpg, nitrite_sensor.jpg, paper2_cover.jpg
  Section 5 (Stay):         cnm.jpg, icmab.jpg, lab_equipment.jpg
  Section 6 (Maker):        raspberry_pi.jpg, streamlit_dashboard.jpg, workshop.jpg
  Section 7 (Future):       egofet_diagram.png

Render:
    python scripts/workflow.py render-all \
        --file presentaciones/2025-david_ICMAB/david_presentation.py -q l
"""

from manim import *
from manim_slides import Slide
from toolkit import SlidesControl, TITLE_SIZE, NORMAL_SIZE, TINY_SIZE

config.verbosity = "WARNING"
config.background_color = WHITE
Text.set_default(color=BLACK)
MathTex.set_default(color=BLACK)

PRIMARY = BLUE
ACCENT = TEAL_D
TIMELINE_COLOR = GREY_B
ASSETS_DIR = "assets"

TOTAL_SECTIONS = 7
SECTION_LABELS = [
    "Who am I", "Roots", "Formation",
    "Impact", "Stay", "Maker", "Future",
]


# --- Canvas helpers ---

def build_timeline(current_section, total=TOTAL_SECTIONS, primary=PRIMARY, grey=TIMELINE_COLOR):
    """Horizontal timeline: `total` connected nodes; the one at `current_section` is highlighted."""
    spacing = 1.1
    start_x = -((total - 1) * spacing) / 2

    nodes = VGroup()
    for i in range(total):
        is_current = (i == current_section)
        node = Circle(
            radius=0.16 if is_current else 0.10,
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


def setup_canvas(self, section_title, slide_num, current_section, total=TOTAL_SECTIONS):
    """Persistent canvas: section title (top-left), slide number (bottom-left), timeline (bottom)."""
    title = Text(section_title, font_size=NORMAL_SIZE, weight=BOLD)
    title.to_edge(UP, buff=0.4).to_edge(LEFT, buff=0.6)

    number = Text(str(slide_num), font_size=NORMAL_SIZE)
    number.to_corner(DL, buff=0.5)

    timeline = build_timeline(current_section, total).scale(0.7).to_edge(DOWN, buff=0.6)

    self.add_to_canvas(title=title, slide_number=number, timeline=timeline)
    self.play(Write(title), Write(number), FadeIn(timeline))


def update_slide_number(self, new_number):
    """Animate the slide number on the canvas to a new value."""
    old = self.canvas["slide_number"]
    new = Text(str(new_number), font_size=NORMAL_SIZE).move_to(old)
    self.play(Transform(old, new))


# --- Image collage helper ---

_SCATTER_ROTATIONS = [-0.06, 0.04, -0.05, 0.07, -0.03, 0.05, -0.04, 0.06]


def image_collage(self, image_names, max_height=2.2, replace=False):
    """Display images as a scattered collage in the central content area.

    Each image appears in sequence, separated by next_slide().
    The last image is left on screen so the caller can either fade it
    out or let the section's wipe() clear it.

    Args:
        image_names: list of str, filenames relative to ASSETS_DIR.
        max_height: target height for each image.
        replace: if True, each new image replaces the previous; if False,
                 all images remain visible (true collage).
    """
    n = len(image_names)
    if n == 0:
        return

    images = [
        ImageMobject(f"{ASSETS_DIR}/{name}").scale_to_fit_height(max_height)
        for name in image_names
    ]

    cols = 2 if n <= 4 else 3
    rows = (n + cols - 1) // cols
    x_spacing = 3.2
    y_spacing = max_height + 0.4
    x_start = -((cols - 1) * x_spacing) / 2
    y_start = ((rows - 1) * y_spacing) / 2

    placed = []
    for i, img in enumerate(images):
        col = i % cols
        row = i // cols
        x = x_start + col * x_spacing
        y = y_start - row * y_spacing
        img.move_to([x, y, 0])
        img.rotate(_SCATTER_ROTATIONS[i % len(_SCATTER_ROTATIONS)])

        if replace and placed:
            self.play(FadeOut(placed[-1]), FadeIn(img))
        else:
            self.play(FadeIn(img, shift=UP * 0.2))
        placed.append(img)
        if i < n - 1:
            self.next_slide()
    self.next_slide()


# --- Section 1: Who am I? ---

class PortadaIntroduccion(SlidesControl):
    """Slide 1: Who am I? — self introduction, hobbies, motivation."""

    def construct(self):
        setup_canvas(self, "Who am I", 1, 0)
        self.next_slide()

        # TODO: photo + name + brief intro
        # Example:
        #   me = ImageMobject(f"{ASSETS_DIR}/me.jpg").scale_to_fit_height(3)
        #   me.to_edge(RIGHT)
        #   self.play(FadeIn(me))
        # Speaker: short self introduction, where from

        self.next_slide()
        update_slide_number(self, 2)

        # TODO: hobbies collage
        # image_collage(self, ["calisthenics.jpg", "cooking.jpg", "poetry.jpg"])
        # Speaker: talk about hobbies briefly

        self.next_slide()
        update_slide_number(self, 3)

        # TODO: my core drive (key phrase or icon)
        # Speaker: science for social impact, honor mentorship

        self.wipe(self.mobjects_without_canvas, Group())
        self.remove_from_canvas("title", "slide_number", "timeline")
        self.wait(1)


# --- Section 2: The Roots ---

class Raices(SlidesControl):
    """Slide 2: The Roots — childhood, parents, technical high school."""

    def construct(self):
        setup_canvas(self, "Roots", 4, 1)
        self.next_slide()

        # TODO: collage of childhood + family influences
        # image_collage(self, ["father_lab.jpg", "mother_class.jpg", "high_school.jpg"])
        # Speaker: how curiosity started, parents as mentors

        self.next_slide()
        update_slide_number(self, 5)

        # TODO: emphasize "curiosity + mentorship" (key words, sketch)
        # Speaker: confirmation of path through prepa técnica

        self.wipe(self.mobjects_without_canvas, Group())
        self.remove_from_canvas("title", "slide_number", "timeline")
        self.wait(1)


# --- Section 3: Academic Journey & Early Research ---

class Formacion(SlidesControl):
    """Slide 3: Formation — BSc, social service, carbon quantum dots, first paper."""

    def construct(self):
        setup_canvas(self, "Formation", 6, 2)
        self.next_slide()

        # TODO: timeline of BSc + social service
        # Speaker: UANL FCQ, food/toxicology lab

        self.next_slide()
        update_slide_number(self, 7)

        # TODO: highlight CQDs with Dra. Idalia
        # image_collage(self, ["uanl.jpg", "cqd.jpg"])
        # Speaker: low-cost carbon dots, first publication

        self.next_slide()
        update_slide_number(self, 8)

        # TODO: emphasize first publication (cover, key result)
        # Speaker: significance of the first paper

        self.wipe(self.mobjects_without_canvas, Group())
        self.remove_from_canvas("title", "slide_number", "timeline")
        self.wait(1)


# --- Section 4: Social impact — Master's ---

class ImpactoSocial(SlidesControl):
    """Slide 4: Impact — 2022 drought, nitrite sensors, second paper."""

    def construct(self):
        setup_canvas(self, "Impact", 9, 3)
        self.next_slide()

        # TODO: drought/water crisis visual
        # Speaker: MSc in Materials Chemistry, 2022 crisis reoriented research

        self.next_slide()
        update_slide_number(self, 10)

        # TODO: nitrite sensor diagram + photo
        # image_collage(self, ["drought.jpg", "nitrite_sensor.jpg"])
        # Speaker: optoelectronic sensors for shallow water wells

        self.next_slide()
        update_slide_number(self, 11)

        # TODO: 2nd publication (cover, key result)
        # Speaker: independent research, second publication

        self.wipe(self.mobjects_without_canvas, Group())
        self.remove_from_canvas("title", "slide_number", "timeline")
        self.wait(1)


# --- Section 5: Research Stay at CNM & ICMAB ---

class Estancia(SlidesControl):
    """Slide 5: Research stay — CNM, ICMAB, collaborators, equipment."""

    def construct(self):
        setup_canvas(self, "Stay", 12, 4)
        self.next_slide()

        # TODO: photos of CNM/ICMAB + collaborator names
        # image_collage(self, ["cnm.jpg", "icmab.jpg"])
        # Speaker: 3-month stay, César Fernández-Sánchez, Martí Gich

        self.next_slide()
        update_slide_number(self, 13)

        # TODO: equipment / materials / acceleration
        # Speaker: access to advanced tools, scientific perspective broadened

        self.wipe(self.mobjects_without_canvas, Group())
        self.remove_from_canvas("title", "slide_number", "timeline")
        self.wait(1)


# --- Section 6: The Maker Side ---

class Maker(SlidesControl):
    """Slide 6: Maker — bridging chemistry and engineering, RPi, Streamlit."""

    def construct(self):
        setup_canvas(self, "Maker", 14, 5)
        self.next_slide()

        # TODO: Venn diagram or collage of chemistry + electronics + code
        # image_collage(self, ["raspberry_pi.jpg", "streamlit_dashboard.jpg"])
        # Speaker: bridging chemistry and engineering

        self.next_slide()
        update_slide_number(self, 15)

        # TODO: family business support — reconditioning + solar
        # Speaker: appliance reconditioning, solar panel installation

        self.next_slide()
        update_slide_number(self, 16)

        # TODO: web apps / dashboards / RPi controllers
        # Speaker: Python + Streamlit for operations

        self.wipe(self.mobjects_without_canvas, Group())
        self.remove_from_canvas("title", "slide_number", "timeline")
        self.wait(1)


# --- Section 7: Looking Forward ---

class Futuro(SlidesControl):
    """Slide 7: Future — joining Nanomol-Mat, EGOFET, commitment."""

    def construct(self):
        setup_canvas(self, "Future", 17, 6)
        self.next_slide()

        # TODO: EGOFET diagram with 3 pillars (materials, electronics, code)
        # Speaker: excitement to join, ready to learn and contribute

        self.wipe(self.mobjects_without_canvas, Group())
        self.remove_from_canvas("title", "slide_number", "timeline")
        self.wait(1)
