"""Script de comandos para el flujo de trabajo Manim Slides (monorepo).

Subcomandos:
    presentations                  Lista las presentaciones registradas en presentaciones.yaml.
    list --file FILE               Lista las escenas (clases Slide/SlidesControl) de un archivo.
    render-all [--file FILE]       Renderiza una o todas las presentaciones.
    present --file FILE ESCENAS... Abre el visor interactivo.
    export --file FILE FORMATO DEST ESCENAS...   Exporta a html/pptx/pdf/zip.

Soporta dos modos:
    - Con --file: opera sobre una presentación específica apuntada por FILE
      (camino relativo a la raíz, p.ej. presentaciones/2025-david_ICMAB/david_presentation.py).
      El `cwd` del manim-slides se fija a la carpeta de la presentación, de modo que
      `slides/` y `media/` se generan *dentro* de la subcarpeta.
    - Sin --file: itera sobre todas las entradas de presentaciones.yaml (o descubre
      presentaciones por convención si el YAML no existe).

Uso:
    python scripts/workflow.py presentations
    python scripts/workflow.py list --file presentaciones/2025-david_ICMAB/david_presentation.py
    python scripts/workflow.py render-all --file presentaciones/2025-david_ICMAB/david_presentation.py -q l
    python scripts/workflow.py present --file presentaciones/2025-david_ICMAB/david_presentation.py Introduccion
    python scripts/workflow.py export --file presentaciones/2025-david_ICMAB/david_presentation.py html salida.html Introduccion
"""

import argparse
import importlib.util
import inspect
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
YAML_PATH = ROOT / "presentaciones.yaml"

MANIM_SLIDES_BIN = Path(sys.executable).parent / "manim-slides"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def load_module(path: Path):
    """Carga un archivo .py como módulo sin ejecutarlo como __main__."""
    spec = importlib.util.spec_from_file_location("presentacion_mod", path)
    if spec is None or spec.loader is None:
        sys.exit(f"Error: no se pudo cargar {path} como módulo Python.")
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


def load_yaml_entries():
    """Lee presentaciones.yaml. Devuelve lista de dicts {name, file} o [] si no existe.

    Intenta usar PyYAML; si no está disponible, hace un parser mínimo propio para
    evitar añadir una dependencia dura solo para leer este registro.
    """
    if not YAML_PATH.exists():
        return []

    text = YAML_PATH.read_text(encoding="utf-8")

    try:
        import yaml

        data = yaml.safe_load(text) or {}
        return list(data.get("presentaciones", []))
    except ImportError:
        return _parse_yaml_minimal(text)


def _parse_yaml_minimal(text: str):
    """Parser YAML muy limitado: solo soporta el formato de este repo.

    Estructura esperada:
        presentaciones:
          - name: <str>
            file: <str>
    """
    entries = []
    in_presentaciones = False
    current = None
    for raw in text.splitlines():
        line = raw.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        if not line.startswith(" "):
            if line.startswith("presentaciones:"):
                in_presentaciones = True
            else:
                in_presentaciones = False
            continue
        if not in_presentaciones:
            continue
        stripped = line.strip()
        if stripped.startswith("- "):
            if current is not None:
                entries.append(current)
            current = {}
            stripped = stripped[2:].strip()
        if ":" in stripped and current is not None:
            key, _, value = stripped.partition(":")
            current[key.strip()] = value.strip()
    if current is not None:
        entries.append(current)
    return entries


def discover_presentations():
    """Descubre presentaciones por convención si no hay YAML.

    Busca cualquier `*.py` directamente bajo `presentaciones/*/` cuya carpeta
    no empiece por `_`. Devuelve [{name, file}, ...].
    """
    pres_dir = ROOT / "presentaciones"
    if not pres_dir.is_dir():
        return []
    out = []
    for sub in sorted(pres_dir.iterdir()):
        if not sub.is_dir() or sub.name.startswith(("_", ".")):
            continue
        for py in sorted(sub.glob("*.py")):
            if py.name.startswith("_"):
                continue
            out.append(
                {
                    "name": sub.name,
                    "file": str(py.relative_to(ROOT)),
                }
            )
    return out


def resolve_presentations(args) -> list[dict]:
    """Devuelve la lista de presentaciones sobre las que operar.

    Prioridad:
        1. --file explícito (una sola presentación, con name = nombre de carpeta).
        2. presentaciones.yaml si existe.
        3. Descubrimiento por convención.
    """
    if getattr(args, "file", None):
        f = Path(args.file)
        if not f.is_absolute():
            f = ROOT / f
        if not f.exists():
            sys.exit(f"Error: no se encontró {f}")
        return [{"name": f.parent.name, "file": str(f.relative_to(ROOT))}]
    entries = load_yaml_entries()
    if entries:
        return entries
    return discover_presentations()


def run_manim_slides(cmd, cwd: Path):
    """Ejecuta un subcomando de manim-slides con cwd apuntando a la carpeta de la presentación."""
    result = subprocess.run(cmd, cwd=cwd)
    if result.returncode != 0:
        sys.exit(f"Falló el comando: {' '.join(cmd)} (en {cwd})")
    return result


def cmd_presentations(_args):
    entries = resolve_presentations(_args)
    if not entries:
        sys.exit(
            "No se encontraron presentaciones. Crea presentaciones/<nombre>/<archivo>.py "
            "o añade entradas en presentaciones.yaml."
        )
    print(f"Presentaciones registradas ({len(entries)}):")
    for i, e in enumerate(entries, 1):
        print(f"  {i}. {e['name']}  ->  {e['file']}")


def cmd_list(args):
    entries = resolve_presentations(args)
    if not entries:
        sys.exit("No se encontraron presentaciones.")
    for entry in entries:
        file_path = ROOT / entry["file"]
        if not file_path.exists():
            print(f"[AVISO] {entry['name']}: no se encontró {file_path}")
            continue
        try:
            from manim_slides import Slide
            from toolkit.canvas import SlidesControl
        except ImportError as e:
            sys.exit(
                f"Error: faltan dependencias del entorno Manim Slides ({e}).\n"
                "Activa el entorno conda con `conda activate manim`."
            )
        module = load_module(file_path)
        scenes = detect_scenes(module, (Slide, SlidesControl))
        if not scenes:
            print(f"{entry['name']} ({entry['file']}): sin escenas")
            continue
        print(f"{entry['name']} ({entry['file']}):")
        for i, (name, _) in enumerate(scenes, 1):
            print(f"  {i}. {name}")


def cmd_render_all(args):
    entries = resolve_presentations(args)
    if not entries:
        sys.exit("No se encontraron presentaciones para renderizar.")

    for entry in entries:
        file_path = ROOT / entry["file"]
        if not file_path.exists():
            print(f"[AVISO] {entry['name']}: no se encontró {file_path}, se omite.")
            continue
        try:
            from manim_slides import Slide
            from toolkit.canvas import SlidesControl
        except ImportError as e:
            sys.exit(
                f"Error: faltan dependencias del entorno Manim Slides ({e}).\n"
                "Activa el entorno conda con `conda activate manim`."
            )
        module = load_module(file_path)
        scenes = detect_scenes(module, (Slide, SlidesControl))
        if not scenes:
            print(f"[AVISO] {entry['name']}: sin escenas, se omite.")
            continue

        pres_dir = file_path.parent
        print(
            f"Renderizando {entry['name']} ({len(scenes)} escenas) con calidad -{args.quality}"
        )
        for name, _ in scenes:
            print(f"  - {name}")
            cmd = [
                str(MANIM_SLIDES_BIN),
                "render",
                str(file_path),
                name,
                f"-q{args.quality}",
            ]
            run_manim_slides(cmd, cwd=pres_dir)


def cmd_present(args):
    if not args.scenes:
        sys.exit("Error: debes indicar al menos una escena")
    entries = resolve_presentations(args)
    if len(entries) != 1:
        sys.exit("Error: `present` requiere --file apuntando a una sola presentación.")
    file_path = ROOT / entries[0]["file"]
    pres_dir = file_path.parent
    cmd = [str(MANIM_SLIDES_BIN), *args.scenes]
    result = subprocess.run(cmd, cwd=pres_dir)
    sys.exit(result.returncode)


def cmd_export(args):
    if not args.scenes:
        sys.exit("Error: debes indicar al menos una escena")
    entries = resolve_presentations(args)
    if len(entries) != 1:
        sys.exit("Error: `export` requiere --file apuntando a una sola presentación.")
    file_path = ROOT / entries[0]["file"]
    pres_dir = file_path.parent

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

    result = subprocess.run(cmd, cwd=pres_dir)
    sys.exit(result.returncode)


def main():
    parser = argparse.ArgumentParser(
        description="Flujo de trabajo Manim Slides (monorepo)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--file",
        type=str,
        default=None,
        help="Ruta al .py de una presentación (ej. presentaciones/<nombre>/<archivo>.py). "
        "Si se omite, opera sobre todas las del YAML o descubiertas por convención.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_pres = sub.add_parser("presentations", help="Listar presentaciones registradas")
    p_pres.set_defaults(func=cmd_presentations)

    p_list = sub.add_parser(
        "list", help="Listar escenas de una o todas las presentaciones"
    )
    p_list.set_defaults(func=cmd_list)

    p_render = sub.add_parser("render-all", help="Renderizar escenas")
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

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
