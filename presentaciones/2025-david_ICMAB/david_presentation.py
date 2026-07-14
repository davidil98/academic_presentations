"""David Ibarra — Presentation at ICMAB (Nanomol-Mat, 2025).

Image-heavy introduction with a persistent timeline canvas.
Each section is a SlidesControl class with title, slide number and a
horizontal progress timeline that highlight the current section.

Render:
    python scripts/workflow.py render-all
        --file presentaciones/2025-david_ICMAB/david_presentation.py -q l
"""

import sys
from pathlib import Path

# Add project root to sys.path so that 'toolkit' can be imported
# when this file is run from a different cwd (e.g., via manim-slides subprocess).
_project_root = Path(__file__).resolve().parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

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


def find_project_root(marker):
    """Sube desde este archivo hasta encontrar una carpeta con nombre `marker`."""
    start = Path(__file__).resolve().parent
    for parent in [start, *start.parents]:
        if (parent / marker).is_dir():
            return str(parent / marker)
    raise FileNotFoundError(
        f"No se encontró '{marker}' partiendo de {start}"
    )


ASSETS_DIR = find_project_root("assets")

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

    number = Text(str(slide_num), font_size=NORMAL_SIZE+10)
    number.to_corner(DL, buff=0.5)

    timeline = build_timeline(current_section, total).scale(0.7).to_edge(DOWN, buff=0.6)

    self.add_to_canvas(title=title, slide_number=number, timeline=timeline)
    self.play(Write(title), Write(number), FadeIn(timeline))
    self._slide_count = slide_num # semilla del contador


def update_slide_number(self, new_number=None):
    """Si new_number es None, incrementa el último número de la sección."""
    if new_number is None:
        if not hasattr(self, "_slide_count"):
            raise RuntimeError(
                "Llama primero a setup_canvas() para inicializar el contador."
            )
        self._slide_count += 1
        new_number = self._slide_count
    else:
        self._slide_count = new_number
    old = self.canvas["slide_number"]
    new = Text(str(new_number), font_size=NORMAL_SIZE).move_to(old)
    self.play(Transform(old, new))

# --- Image collage helper ---

_SCATTER_ROTATIONS = [-0.06, 0.04, -0.05, 0.07, -0.03, 0.05, -0.04, 0.06]

def image_collage(self, image_names: list, max_height=2.2, replace=False):
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
    x_spacing = 1.2
    y_spacing = max_height - 0.4
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


# Test slides

class PortadaIntroduccion(SlidesControl):
    """Slide 1: Who am I? — self introduction, hobbies, motivation."""

    def construct(self):
        # TODO: photo + name + brief intro
        # Speaker: short self introduction, where from

        title = Text("Welcome Presentation", font_size=TITLE_SIZE, weight=BOLD)
        title.center()

        subtitle = Text("David Ibarra Luna", font_size=NORMAL_SIZE, weight=BOLD)
        subtitle.next_to(title, DOWN, buff=0.5)

        me = ImageMobject(f"{ASSETS_DIR}/me.jpg").scale_to_fit_height(3)
        me.to_corner(UR, buff=0.5).scale(0.65)

        icmab_logo = ImageMobject(f"{ASSETS_DIR}/icmab_logo.jpg").scale_to_fit_height(1)
        icmab_logo.to_corner(UL, buff=0.5)

        date = Text("Tuesday July 14, 2026", font_size=TINY_SIZE, weight=BOLD)
        date.to_edge(DOWN, buff=0.5)
        
        self.play(Write(title))
        self.play(Write(subtitle), Write(date))
        self.play(FadeIn(me, shift=UP*0.2), FadeIn(icmab_logo, shift=UP*0.2))

        self.next_slide()
        self.clear_canvas()

        # TODO: collage, hobbies
        # Speaker: talk about hobbies briefly

        setup_canvas(self, "Who am I?", 2, 0)

        breif_intro = Text("A chemist from Monterrey, Nuevo León, México.", font_size=NORMAL_SIZE)
        breif_intro.next_to(self.canvas["title"], DOWN, buff=0.5, aligned_edge=LEFT)

        mty_map = SVGMobject(f"{ASSETS_DIR}/nl_map.svg").scale(2)
        mty_map.center()

        collage_city_things = ["carne.jpg", "carne2.jpg"]

        mty_landscape = ImageMobject(f"{ASSETS_DIR}/mty_landscape.jpg").scale_to_fit_height(3.5)
        mty_landscape.center()
        
        self.play(FadeIn(breif_intro), DrawBorderThenFill(mty_map))
        self.next_slide()
        self.play(FadeOut(mty_map))
        image_collage(self, image_names=collage_city_things, replace=False, max_height=3.5)
        self.next_slide()
        self.play(FadeIn(mty_landscape))
        self.next_slide()
        self.play(*[FadeOut(mob) for mob in self.mobjects if isinstance(mob, ImageMobject)])
        self.play(FadeOut(mty_landscape))

        # wipe breif_description --> hobbies_txt
        hobbies_txt = Text("Some of my hobbies", font_size=NORMAL_SIZE)
        hobbies_txt.next_to(self.canvas["title"], DOWN, buff=0.5, aligned_edge=LEFT)

        collage_hobbies_imgs = ["wlifting.jpg", "cali.JPG", "cocinar.jpg", 
                                "pasta.jpg", "brochetas.jpg", "poesía.jpg",
                                "poesía2.jpg", "arte.jpg", "guitars.jpg"]

        self.wipe(breif_intro, hobbies_txt)
        image_collage(self, image_names=collage_hobbies_imgs, replace=False, max_height=1.7)

        self.next_slide()
        self.play(*[FadeOut(mob) for mob in self.mobjects if isinstance(mob, ImageMobject)]) # remove collage
        
        # TODO: my core drive (key phrase or icon)
        # Speaker: science for social impact, honor mentorship
        # wipe hobbies_txt --> reason_here_txt
        reason_txt = Text("What drives me", font_size=NORMAL_SIZE)
        reason_txt.next_to(self.canvas["title"], DOWN, buff=0.5, aligned_edge=LEFT)

        self.wipe(hobbies_txt, reason_txt)

        # Creación de la lista sin usar LaTeX
        drive_list = BulletedList(
            "Leveraging science for social impact",
            "The knowledge to be acquired",
            font_size=NORMAL_SIZE+10)
        drive_list.center()
        
        self.play(FadeIn(drive_list))

        # finish section
        self.next_slide()
        self.clear_canvas()
        self.wait(1)



class Raices(SlidesControl):
    """Sección 2: The Roots — infancia, familia, preparatoria técnica."""

    def construct(self):
        # --- Slide 4: curiosidad en la infancia ---
        setup_canvas(self, "Roots", 4, 1)

        text_father = Text(
            "Curiosity sparked in childhood, in my father's lab.",
            font_size=NORMAL_SIZE,
        )
        text_father.next_to(self.canvas["title"], DOWN, buff=0.5, aligned_edge=LEFT)

        family_photo = ImageMobject(f"{ASSETS_DIR}/papa_mama_yo.jpg").scale_to_fit_height(3.5)
        family_photo.center()

        self.play(FadeIn(text_father), FadeIn(family_photo, shift=UP * 0.2))
        self.next_slide()

        # --- Slide 5: mi madre (solo texto) ---
        update_slide_number(self)

        text_mother = Text(
            "Nurtured by my mother, who taught middle school chemistry.",
            font_size=NORMAL_SIZE,
        )
        text_mother.next_to(self.canvas["title"], DOWN, buff=0.5, aligned_edge=LEFT)

        self.wipe(text_father, text_mother)
        self.next_slide()
        self.play(FadeOut(family_photo))

        # --- Slide 6: preparatoria ---
        update_slide_number(self)

        text_prepa = Text(
            "A technical high school degree confirmed my path early on.",
            font_size=NORMAL_SIZE,
        )
        text_prepa.next_to(self.canvas["title"], DOWN, buff=0.5, aligned_edge=LEFT)

        prepa_photo = ImageMobject(f"{ASSETS_DIR}/david_prepa.jpg").scale_to_fit_height(3.2)
        prepa_photo.center()

        self.wipe(text_mother, text_prepa)
        self.play(FadeIn(prepa_photo, shift=UP * 0.2))

        # --- Fin de la sección ---
        self.next_slide()
        self.clear_canvas()
        self.wait(1)



class Formacion(SlidesControl):
    """Sección 3: Academic Journey & Early Research — BSc, servicio social, CQDs."""

    YEARS = ["2016", "2019", "2021"]

    def construct(self):
        # --- Slide 7: BSc en UANL FCQ ---
        setup_canvas(self, "Formation", 7, 2)

        # Timeline horizontal centrado
        timeline_y = 0.0
        spacing = 2.0
        start_x = -((len(self.YEARS) - 1) * spacing) / 2

        nodes = VGroup()
        labels = VGroup()
        for i, year in enumerate(self.YEARS):
            node = Circle(radius=0.14, color=TIMELINE_COLOR, fill_opacity=1)
            node.move_to([start_x + i * spacing, timeline_y, 0])
            nodes.add(node)

            label = Text(year, font_size=TINY_SIZE, weight=BOLD)
            label.next_to(node, UP, buff=0.25)
            labels.add(label)

        bars = VGroup()
        for i in range(len(self.YEARS) - 1):
            bar = Line(
                nodes[i].get_right(),
                nodes[i + 1].get_left(),
                color=TIMELINE_COLOR,
                stroke_width=3,
            )
            bars.add(bar)

        highlight = Circle(radius=0.22, color=PRIMARY, fill_opacity=1)
        highlight.move_to(nodes[0].get_center())

        timeline_group = VGroup(bars, nodes, labels, highlight)
        timeline_group.to_edge(LEFT, buff=1.5)

        text_bsc = Text(
            "BSc in Industrial Chemistry at UANL FCQ (2016-2021).",
            font_size=NORMAL_SIZE,
        )
        text_bsc.next_to(self.canvas["title"], DOWN, buff=0.5, aligned_edge=LEFT)

        uanl_photo = ImageMobject(f"{ASSETS_DIR}/uanl_photo.jpg").scale_to_fit_height(2.5)
        uanl_photo.move_to([4.5, 0, 0])
        uanl_logo = ImageMobject(f"{ASSETS_DIR}/uanl_logo.png").scale_to_fit_height(0.7)
        uanl_logo.next_to(uanl_photo, DOWN, buff=0.3)

        self.play(
            FadeIn(timeline_group),
            FadeIn(text_bsc),
            FadeIn(uanl_photo, shift=UP * 0.2),
            FadeIn(uanl_logo, shift=UP * 0.2),
        )
        self.next_slide()

        # --- Slide 8: servicio social ---
        update_slide_number(self)

        text_service = Text(
            "Social service in a food & toxicology lab (2019).",
            font_size=NORMAL_SIZE,
        )
        text_service.next_to(self.canvas["title"], DOWN, buff=0.5, aligned_edge=LEFT)

        fqc_photo = ImageMobject(f"{ASSETS_DIR}/fqc_photo.jpg").scale_to_fit_height(2.5)
        fqc_photo.move_to(uanl_photo.get_center())
        fqc_logo = ImageMobject(f"{ASSETS_DIR}/fqc_logo.png").scale_to_fit_height(0.7)
        fqc_logo.next_to(fqc_photo, DOWN, buff=0.3)

        self.wipe(text_bsc, text_service)
        self.play(
            highlight.animate.move_to(nodes[1].get_center()),
            FadeOut(uanl_photo),
            FadeIn(fqc_photo, shift=UP * 0.2),
            FadeOut(uanl_logo),
            FadeIn(fqc_logo, shift=UP * 0.2),
        )
        self.next_slide()

        # --- Slide 9: CQDs con Dra. Idalia ---
        update_slide_number(self)

        text_cqd = Text(
            "Optoelectronics with Dra. Idalia: GQDs + AuNPs.",
            font_size=NORMAL_SIZE,
        )
        text_cqd.next_to(self.canvas["title"], DOWN, buff=0.5, aligned_edge=LEFT)

        idalia = ImageMobject(f"{ASSETS_DIR}/dra_idalia.jpg").scale_to_fit_height(1.5)
        idalia.next_to(text_cqd, DOWN, buff=0.3).to_edge(RIGHT, buff=0.5)

        paper1 = ImageMobject(f"{ASSETS_DIR}/ngqd_cpaper.png").scale_to_fit_height(1.5)
        paper1.next_to(idalia, DOWN, buff=0.2)

        paper2 = ImageMobject(f"{ASSETS_DIR}/ngqd_aunp_cpaper_lspr.png").scale_to_fit_height(1.5)
        paper2.next_to(paper1, DOWN, buff=0.2)

        self.wipe(text_service, text_cqd)
        self.play(
            highlight.animate.move_to(nodes[2].get_center()),
            FadeOut(fqc_photo),
            FadeOut(fqc_logo),
            FadeIn(idalia, shift=UP * 0.2),
            FadeIn(paper1, shift=UP * 0.2),
            FadeIn(paper2, shift=UP * 0.2),
        )
        self.next_slide()

        # --- Fin de la sección ---
        self.clear_canvas()
        self.wait(1)



class ImpactoSocial(SlidesControl):
    """Sección 4: Master's Degree - Science driven by Social Impact."""

    def construct(self):
        # --- Slide 10: MSc + Dra. Idalia ---
        setup_canvas(self, "Impact", 10, 3)

        text_msc = Text(
            "MSc in Materials Chemistry (2022-2024), again with Dra. Idalia.",
            font_size=NORMAL_SIZE,
        )
        text_msc.next_to(self.canvas["title"], DOWN, buff=0.5, aligned_edge=LEFT)

        idalia = ImageMobject(f"{ASSETS_DIR}/dra_idalia.jpg").scale_to_fit_height(3)
        idalia.center()

        self.play(FadeIn(text_msc), FadeIn(idalia, shift=UP * 0.2))
        self.next_slide()

        # --- Slide 11: Crisis hídrica ---
        update_slide_number(self)

        text_crisis = Text(
            "2022 drought: critical levels at Cerro Prieto and La Boca dams.",
            font_size=NORMAL_SIZE,
        )
        text_crisis.next_to(self.canvas["title"], DOWN, buff=0.5, aligned_edge=LEFT)

        cerro = ImageMobject(f"{ASSETS_DIR}/cerro_prieto_dry.jpg").scale_to_fit_height(3.0)
        cerro.move_to([-2.5, -0.5, 0])

        boca = ImageMobject(f"{ASSETS_DIR}/presa_laBoca_seco.jpg").scale_to_fit_height(3.0)
        boca.move_to([2.5, -0.5, 0])

        self.wipe(text_msc, text_crisis)
        self.play(FadeOut(idalia), FadeIn(cerro, shift=UP * 0.2), FadeIn(boca, shift=UP * 0.2))
        self.next_slide()

        # --- Slide 12: Pozos someros ---
        update_slide_number(self)

        text_wells = Text(
            "Government response: restore and incorporate shallow water wells.",
            font_size=NORMAL_SIZE,
        )
        text_wells.next_to(self.canvas["title"], DOWN, buff=0.5, aligned_edge=LEFT)

        gob_pozos = ImageMobject(f"{ASSETS_DIR}/gob_pozos_someros.jpg").scale_to_fit_height(3.8)
        gob_pozos.center()

        self.wipe(text_crisis, text_wells)
        self.play(FadeOut(cerro), FadeOut(boca), FadeIn(gob_pozos, shift=UP * 0.2))
        self.next_slide()

        # --- Slide 13: Quenching - Estado 0 (NH2, PL alta) ---
        update_slide_number(self)

        text_quench = Text(
            "Detection mechanism: N-GQD fluorescence quenching by nitrites.",
            font_size=NORMAL_SIZE,
        )
        text_quench.next_to(self.canvas["title"], DOWN, buff=0.5, aligned_edge=LEFT)

        n_gqd = SVGMobject(f"{ASSETS_DIR}/n_gqd.svg").scale(1.7).to_edge(LEFT, buff=0.5)
        n_gqd_label = Text("N-GQD", font_size=NORMAL_SIZE - 2).next_to(n_gqd, DOWN, buff=0.3)

        nh2_0 = Text("NH₂", font_size=NORMAL_SIZE - 4, color=BLUE).next_to(n_gqd, UP, buff=0.1)
        nh2_1 = Text("NH₂", font_size=NORMAL_SIZE - 4, color=BLUE).next_to(n_gqd, LEFT, buff=0.05)
        nh2_2 = Text("NH₂", font_size=NORMAL_SIZE - 4, color=BLUE).next_to(n_gqd, DOWN, buff=0.1).shift(LEFT)
        nh2_group = VGroup(nh2_0, nh2_1, nh2_2)

        x_min_wl, x_max_wl = 400, 700
        y_min_intensity, y_max_intensity = 0.0, 1.8
        axes = Axes(
            x_range=[x_min_wl, x_max_wl, 100],
            y_range=[y_min_intensity, y_max_intensity, 0.3],
            x_length=5.0,
            y_length=2.8,
            axis_config={"include_numbers": True, "font_size": 16, "color": BLACK},
            x_axis_config={"color": BLACK},
            y_axis_config={"color": BLACK},
        ).to_edge(RIGHT, buff=0.5).shift(DOWN * 0.3)
        x_label = axes.get_x_axis_label(Text("Wavelength (nm)", font_size=18), edge=DOWN, direction=DOWN, buff=0.3)
        y_label = axes.get_y_axis_label(Text("PL Intensity (a.u.)", font_size=18).rotate(90 * DEGREES), edge=LEFT, direction=LEFT, buff=0.3)
        pl_plot_group = VGroup(axes, x_label, y_label)

        def get_pl_curve(amplitude, color):
            safe_amplitude = min(amplitude, y_max_intensity * 0.95)
            return axes.plot(
                lambda x: safe_amplitude * np.exp(-((x - 525) ** 2) / (2 * 30 ** 2)),
                x_range=[x_min_wl, x_max_wl],
                color=color,
                stroke_width=4,
            )

        initial_curve = get_pl_curve(1.5, GREEN_B)

        self.wipe(text_wells, text_quench)
        self.play(FadeOut(gob_pozos))
        self.play(
            FadeIn(n_gqd), Write(n_gqd_label),
            Write(nh2_group),
            Create(pl_plot_group), Create(initial_curve),
        )
        self.next_slide()

        # --- Slide 14: Quenching - Estados 1+2 ---
        update_slide_number(self)

        no2_batch1 = VGroup(*[
            Tex(r"$NO_2^-$", font_size=NORMAL_SIZE - 4, color=ORANGE).move_to(pos)
            for pos in [
                n_gqd.get_top() + UP * 0.2 + RIGHT * 0.3,
                n_gqd.get_left() + LEFT * 0.2 + UP * 0.3,
                n_gqd.get_bottom() + DOWN * 0.1 + LEFT * 0.4,
            ]
        ])
        no2_batch2 = VGroup(*[
            Tex(r"$NO_2^-$", font_size=NORMAL_SIZE - 4, color=ORANGE).move_to(pos)
            for pos in [
                n_gqd.get_top() + UP * 0.4 + LEFT * 0.2,
                n_gqd.get_right() + RIGHT * 0.3 + UP * 0.2,
                n_gqd.get_bottom() + DOWN * 0.1 + RIGHT * 0.5,
            ]
        ])

        nn_target_0 = Text("N=N⁻", font_size=NORMAL_SIZE - 4, color=RED).move_to(nh2_0)
        nn_target_1 = Text("N=N⁻", font_size=NORMAL_SIZE - 4, color=RED).move_to(nh2_1)
        nn_target_2 = Text("N=N⁻", font_size=NORMAL_SIZE - 4, color=RED).move_to(nh2_2)

        medium_curve = get_pl_curve(0.8, YELLOW_D)
        self.play(
            FadeIn(no2_batch1),
            Indicate(nh2_0),
            FadeOut(nh2_0),
            FadeIn(nn_target_0),
            FadeOut(initial_curve),
            FadeIn(medium_curve),
        )

        low_curve = get_pl_curve(0.3, RED_D)
        self.play(
            FadeIn(no2_batch2),
            Indicate(nh2_1),
            FadeOut(nh2_1),
            FadeIn(nn_target_1),
            Indicate(nh2_2),
            FadeOut(nh2_2),
            FadeIn(nn_target_2),
            FadeOut(medium_curve),
            FadeIn(low_curve),
        )
        self.next_slide()
        # --- Slide 15: Sensor conceptual (haz grueso) ---
        update_slide_number(self)

        text_sensor = Text(
            "Sensor concept: LED UV + N-GQD sample + photodetector.",
            font_size=NORMAL_SIZE,
        )
        text_sensor.next_to(self.canvas["title"], DOWN, buff=0.5, aligned_edge=LEFT)

        led_body = Circle(radius=0.3, color=DARKER_GRAY, fill_opacity=0.6).move_to(LEFT * 4.0 + DOWN * 0.3)
        led_emitter = Dot(color=PURPLE_B, radius=0.14).move_to(led_body.get_critical_point(RIGHT))
        led_group = VGroup(led_body, led_emitter)
        led_label = Text("LED UV", font_size=NORMAL_SIZE - 5).next_to(led_group, DOWN, buff=0.3)

        sample_cuvette = Rectangle(width=1.4, height=2.4, color=BLUE_C, fill_opacity=0.25).move_to(ORIGIN + DOWN * 0.3)
        sample_label = Text("Muestra (N-GQD)", font_size=NORMAL_SIZE - 5).next_to(sample_cuvette, DOWN, buff=0.3)
        n_gqd_in_sample = SVGMobject(f"{ASSETS_DIR}/n_gqd.svg").scale(0.5).move_to(sample_cuvette.get_center())

        photodetector_sensitive_area = Rectangle(width=0.8, height=1.6, color=TEAL_E, fill_opacity=0.7).move_to(RIGHT * 4.0 + DOWN * 0.3)
        photodetector_base = Rectangle(width=1.0, height=0.2, color=GRAY).next_to(photodetector_sensitive_area, DOWN, buff=0)
        photodetector_group = VGroup(photodetector_sensitive_area, photodetector_base)
        photodetector_label = Text("Fotodetector", font_size=NORMAL_SIZE - 5).next_to(photodetector_group, DOWN, buff=0.3)

        # Haz de luz grueso y representativo (3 líneas paralelas con opacidades)
        beam1_core = Line(led_emitter.get_center(), sample_cuvette.get_critical_point(LEFT), color=PURPLE_A, stroke_width=14, stroke_opacity=1.0)
        beam1_glow = Line(led_emitter.get_center(), sample_cuvette.get_critical_point(LEFT), color=PURPLE_C, stroke_width=20, stroke_opacity=0.4)
        beam2_core = Line(sample_cuvette.get_critical_point(RIGHT), photodetector_sensitive_area.get_critical_point(LEFT), color=GREEN_A, stroke_width=14, stroke_opacity=1.0)
        beam2_glow = Line(sample_cuvette.get_critical_point(RIGHT), photodetector_sensitive_area.get_critical_point(LEFT), color=GREEN_C, stroke_width=20, stroke_opacity=0.4)

        self.wipe(self.mobjects_without_canvas, Group())
        self.play(
            FadeIn(text_sensor),
            FadeIn(led_group), Write(led_label),
            FadeIn(sample_cuvette), Write(sample_label),
            FadeIn(n_gqd_in_sample),
            FadeIn(photodetector_group), Write(photodetector_label),
        )
        self.play(FadeIn(beam1_glow), FadeIn(beam2_glow), run_time=0.6)
        self.play(FadeIn(beam1_core), FadeIn(beam2_core), run_time=0.6)
        self.next_slide()

        # --- Slide 16: Paper + calibration curve (compactos) ---
        update_slide_number(self)

        text_paper = Text(
            "Second publication: ACS Omega (June 2026).",
            font_size=NORMAL_SIZE,
        )
        text_paper.next_to(self.canvas["title"], DOWN, buff=0.5, aligned_edge=LEFT)

        paper = ImageMobject(f"{ASSETS_DIR}/second_paper_ss.jpeg").scale_to_fit_height(3.5)
        paper.to_edge(buff=0.3)
        curve = ImageMobject(f"{ASSETS_DIR}/calibration_curves_acsomegapaper.jpeg").scale_to_fit_height(2.8)
        curve.move_to([2.8, 0, 0])

        self.wipe(self.mobjects_without_canvas, Group())
        self.play(FadeIn(text_paper), FadeIn(paper, shift=UP * 0.2), FadeIn(curve, shift=UP * 0.2))
        self.next_slide()

        # --- Fin de la sección ---
        self.clear_canvas()
        self.wait(1)



class Estancia(SlidesControl):
    """Sección 5: Research Stay at CNM & ICMAB."""

    def construct(self):
        # --- Slide 17: CNM + ICMAB ---
        setup_canvas(self, "Stay", 17, 4)

        text_stay = Text(
            "A pivotal 3-month research stay at CNM & ICMAB.",
            font_size=NORMAL_SIZE,
        )
        text_stay.next_to(self.canvas["title"], DOWN, buff=0.5, aligned_edge=LEFT)

        cnm = ImageMobject(f"{ASSETS_DIR}/imb-cnm-institut-fachada.jpg").scale_to_fit_height(3.0)
        cnm.to_edge(LEFT, buff=0.5)

        icmab = ImageMobject(f"{ASSETS_DIR}/icmab_building.jpeg").scale_to_fit_height(3.0)
        icmab.to_edge(RIGHT, buff=0.5)

        self.play(
            FadeIn(text_stay),
            FadeIn(cnm, shift=UP * 0.2),
            FadeIn(icmab, shift=UP * 0.2),
        )
        self.next_slide()

        # --- Slide 18: Investigadores + experimentos ---
        update_slide_number(self)

        text_team = Text(
            "With César Fernández-Sánchez and Martí Gich.",
            font_size=NORMAL_SIZE,
        )
        text_team.next_to(self.canvas["title"], DOWN, buff=0.5, aligned_edge=LEFT)

        team_photo = ImageMobject(f"{ASSETS_DIR}/marti_cesar_yo.jpg").scale_to_fit_height(3.5)
        team_photo.to_edge(LEFT, buff=1)

        experiments = ImageMobject(f"{ASSETS_DIR}/cnm_experiments1.jpg").scale_to_fit_height(3.5)
        experiments.to_edge(RIGHT, buff=1)

        self.wipe(text_stay, text_team)
        self.play(
            FadeOut(cnm), FadeOut(icmab),
            FadeIn(team_photo, shift=UP * 0.2),
            FadeIn(experiments, shift=UP * 0.2),
        )
        self.next_slide()

        # --- Fin de la sección ---
        self.clear_canvas()
        self.wait(1)



class Maker(SlidesControl):
    """Sección 6: The Maker Side."""

    def construct(self):
        # --- Slide 19: De la química al trabajo práctico ---
        setup_canvas(self, "Maker", 19, 5)

        text_intro = Text(
            "From chemistry to practical, hands-on work.",
            font_size=NORMAL_SIZE,
        )
        text_intro.next_to(self.canvas["title"], DOWN, buff=0.5, aligned_edge=LEFT)

        paneles = ImageMobject(f"{ASSETS_DIR}/paneles_solares.jpg").scale_to_fit_height(4)
        paneles.center()

        self.play(FadeIn(text_intro), FadeIn(paneles, shift=UP * 0.2))
        self.next_slide()

        # --- Slide 20: Negocio familiar ---
        update_slide_number(self)

        text_family = Text(
            "Family business: appliance reconditioning + solar panels.",
            font_size=NORMAL_SIZE,
        )
        text_family.next_to(self.canvas["title"], DOWN, buff=0.5, aligned_edge=LEFT)

        lavadora = ImageMobject(f"{ASSETS_DIR}/lavadora_reparacion.jpg").scale_to_fit_height(3.5)
        lavadora.move_to([-2.8, 0, 0])

        lavanderia = ImageMobject(f"{ASSETS_DIR}/lavanderia.jpg").scale_to_fit_height(3.5)
        lavanderia.move_to([2.8, 0, 0])

        self.wipe(text_intro, text_family)
        self.play(
            FadeOut(paneles),
            FadeIn(lavadora, shift=UP * 0.2),
            FadeIn(lavanderia, shift=UP * 0.2),
        )
        self.next_slide()

        # --- Slide 21: Raspberry Pi ---
        update_slide_number(self)

        text_pi = Text(
            "Raspberry Pi controllers for washing machines.",
            font_size=NORMAL_SIZE,
        )
        text_pi.next_to(self.canvas["title"], DOWN, buff=0.5, aligned_edge=LEFT)

        raspberry = ImageMobject(f"{ASSETS_DIR}/raspberry_tragamonedas_circuito.jpg").scale_to_fit_height(3.5)
        raspberry.to_edge(LEFT, buff=0.5)
        raspberry_coding = ImageMobject(f"{ASSETS_DIR}/raspberry_sas.jpg").scale_to_fit_height(3.5)
        raspberry_coding.to_edge(RIGHT, buff=0.5)

        self.wipe(text_family, text_pi)
        self.play(FadeOut(lavadora), FadeOut(lavanderia), FadeIn(raspberry, shift=UP * 0.2), FadeIn(raspberry_coding, shift=UP * 0.2))
        self.next_slide()

        # --- Slide 22: Web apps ---
        update_slide_number(self)

        text_web = Text(
            "Service web apps and dashboards with Streamlit.",
            font_size=NORMAL_SIZE,
        )
        text_web.next_to(self.canvas["title"], DOWN, buff=0.5, aligned_edge=LEFT)

        ecoluna = ImageMobject(f"{ASSETS_DIR}/ecoluna_webpage.jpeg").scale_to_fit_height(3.0)
        ecoluna.to_edge(LEFT, buff=1.0)

        gamagar = ImageMobject(f"{ASSETS_DIR}/gamagarsolar_webpage.jpeg").scale_to_fit_height(3.0)
        gamagar.to_edge(RIGHT, buff=1.0)

        self.wipe(text_pi, text_web)
        self.play(
            FadeOut(raspberry),
            FadeOut(raspberry_coding),
            FadeIn(ecoluna, shift=UP * 0.2),
            FadeIn(gamagar, shift=UP * 0.2),
        )
        self.next_slide()

        # --- Fin de la sección ---
        self.clear_canvas()
        self.wait(1)



class Futuro(SlidesControl):
    """Sección 7: Looking Forward."""

    def construct(self):
        # --- Slide 23: EGOFET + BCN (combinados) ---
        setup_canvas(self, "Future", 23, 6)

        text_future = Text(
            "I'm deeply grateful for the opportunity to join this research group!",
            font_size=NORMAL_SIZE,
        )
        text_future.next_to(self.canvas["title"], DOWN, buff=0.5, aligned_edge=LEFT)

        egofet = ImageMobject(f"{ASSETS_DIR}/egofet_device.jpg").scale_to_fit_height(2.5)
        egofet.move_to([-2.8, 0, 0])

        bcn = ImageMobject(f"{ASSETS_DIR}/david_bcn.JPG").scale_to_fit_height(3.0)
        bcn.to_edge(RIGHT, buff=1)

        self.play(
            FadeIn(text_future),
            FadeIn(egofet, shift=UP * 0.2),
            FadeIn(bcn, shift=UP * 0.2),
        )
        self.next_slide()

        # --- Slide 24: ¡Gracias! (meme despedida) ---
        update_slide_number(self)

        # Cambiar título del canvas a "Gracias"
        old_title = self.canvas["title"]
        new_title = Text("Gracias", font_size=NORMAL_SIZE, weight=BOLD)
        new_title.to_edge(UP, buff=0.4).to_edge(LEFT, buff=0.6)

        meme = ImageMobject(f"{ASSETS_DIR}/meme_bye.jpg").scale_to_fit_height(3.5)
        meme.move_to([0, 0.2, 0])

        gracias = Text("¡Gracias!", font_size=TITLE_SIZE, weight=BOLD)
        gracias.next_to(meme, DOWN, buff=0.4)
        gracias.set_x(0)  # centrar horizontalmente

        self.wipe(text_future, gracias)
        self.play(
            FadeOut(egofet),
            FadeOut(bcn),
            FadeIn(meme, shift=UP * 0.2),
        )
        self.play(
            FadeOut(old_title),
            FadeIn(new_title),
        )
        self.canvas["title"] = new_title
        self.next_slide()

        # --- Fin de la presentación ---
        self.clear_canvas()
        self.wait(1)

