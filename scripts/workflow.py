"""Script de comandos para el flujo de trabajo Manim Slides.

Subcomandos:
    render-all                  Detecta y renderiza todas las clases Slide/SlidesControl.
    present ESCENAS...          Abre el visor interactivo con las escenas indicadas.
    export FORMATO DESTINO      Convierte la presentación a html/pptx/pdf/zip.

Uso:
    python scripts/workflow.py render-all
    python scripts/workflow.py render-all --quality h
    python scripts/workflow.py present Introduccion Estructura
    python scripts/workflow.py export html salida.html --open
    python scripts/workflow.py list
"""

import argparse
import importlib.util
import inspect
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_FILE = ROOT / "presentacion.py"

MANIM_SLIDES_BIN = Path(sys.executable).parent / "manim-slides"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def load_module(path):
    """Carga un archivo .py como módulo sin ejecutarlo como __main__."""
    spec = importlib.util.spec_from_file_location("presentacion_mod", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def detect_scenes(module, base_classes):
    """Devuelve una lista de (nombre, clase) para todas las subclases de base_classes."""
    scenes = []
    for name, obj in inspect.getmembers(module, inspect.isclass):
        if obj.__module__ != module.__name__:
            continue
        if any(issubclass(obj, base) for base in base_classes):
            scenes.append((name, obj))
    return scenes


def cmd_render_all(args):
    from manim_slides import Slide
    from toolkit.canvas import SlidesControl

    if not args.file.exists():
        sys.exit(f"Error: no se encontró {args.file}")

    module = load_module(args.file)
    base_classes = (Slide, SlidesControl)
    scenes = detect_scenes(module, base_classes)

    if not scenes:
        sys.exit(f"No se encontraron clases Slide/SlidesControl en {args.file}")

    print(f"Renderizando {len(scenes)} escenas con calidad -{args.quality}")
    for name, _ in scenes:
        print(f"  - {name}")
        cmd = [
            str(MANIM_SLIDES_BIN),
            "render",
            str(args.file),
            name,
            f"-q{args.quality}",
        ]
        import subprocess

        result = subprocess.run(cmd, cwd=ROOT)
        if result.returncode != 0:
            sys.exit(f"Falló el renderizado de {name}")


def cmd_present(args):
    if not args.scenes:
        sys.exit("Error: debes indicar al menos una escena")
    import subprocess

    cmd = [str(MANIM_SLIDES_BIN), *args.scenes]
    result = subprocess.run(cmd, cwd=ROOT)
    sys.exit(result.returncode)


def cmd_export(args):
    if not args.scenes:
        sys.exit("Error: debes indicar al menos una escena")
    import subprocess

    cmd = [
        str(MANIM_SLIDES_BIN),
        "convert",
        *args.scenes,
        str(args.destino),
    ]
    if args.open:
        cmd.append("--open")
    if args.config:
        cmd.extend(["-c" + c for c in args.config])

    result = subprocess.run(cmd, cwd=ROOT)
    sys.exit(result.returncode)


def cmd_list(args):
    from manim_slides import Slide
    from toolkit.canvas import SlidesControl

    if not args.file.exists():
        sys.exit(f"Error: no se encontró {args.file}")

    module = load_module(args.file)
    scenes = detect_scenes(module, (Slide, SlidesControl))
    if not scenes:
        print(f"No se encontraron escenas en {args.file}")
        return
    print(f"Escenas encontradas en {args.file.name}:")
    for i, (name, _) in enumerate(scenes, 1):
        print(f"  {i}. {name}")


def main():
    parser = argparse.ArgumentParser(
        description="Flujo de trabajo Manim Slides",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--file",
        type=Path,
        default=DEFAULT_FILE,
        help=f"Archivo con las clases Slide (default: {DEFAULT_FILE.name})",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_render = sub.add_parser("render-all", help="Renderizar todas las escenas")
    p_render.add_argument(
        "-q",
        "--quality",
        choices=["l", "m", "h", "p", "k"],
        default="l",
        help="Calidad: l (low), m (medium), h (high), p (2k), k (4k) [default: l]",
    )
    p_render.set_defaults(func=cmd_render_all)

    p_present = sub.add_parser("present", help="Visualizar escenas en el visor")
    p_present.add_argument("scenes", nargs="+", help="Nombres de las clases Slide")
    p_present.set_defaults(func=cmd_present)

    p_export = sub.add_parser("export", help="Exportar presentación a un formato")
    p_export.add_argument(
        "formato",
        choices=["html", "pdf", "pptx", "zip"],
        help="Formato de salida (también detecta por la extensión de destino)",
    )
    p_export.add_argument(
        "scenes",
        nargs="+",
        help="Nombres de las clases Slide a incluir",
    )
    p_export.add_argument(
        "destino",
        type=Path,
        help="Archivo de salida (ej. salida.html)",
    )
    p_export.add_argument(
        "--open",
        action="store_true",
        help="Abrir el archivo generado al terminar",
    )
    p_export.add_argument(
        "-c",
        "--config",
        action="append",
        default=[],
        help="Opciones de configuración para el conversor (repetible)",
    )
    p_export.set_defaults(func=cmd_export)

    p_list = sub.add_parser("list", help="Listar escenas disponibles")
    p_list.set_defaults(func=cmd_list)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
