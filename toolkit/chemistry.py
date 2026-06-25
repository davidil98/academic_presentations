"""Utilidades para estructuras químicas con RDKit y Datamol.

Este módulo proporciona funciones para generar imágenes de moléculas
desde SMILES u otros formatos, compatibles con Manim.

Uso:
    from toolkit.chemistry import mol_to_image, dm_mol_to_image

    # Con RDKit directamente
    img = mol_to_image("CCO", size=(300, 300))

    # Con Datamol (API más simple)
    img = dm_mol_to_image("CCO", size=(300, 300))

    # Usar en Manim
    from manim import ImageMobject
    mol_img = ImageMobject(img).scale_to_fit_width(4)
    scene.play(FadeIn(mol_img))
"""

from __future__ import annotations

from typing import Optional, Tuple, Union

try:
    from PIL import Image
except ImportError:
    Image = None
    _PIL_MISSING_MSG = "pillow es requerido. Instálalo con: pip install pillow"

try:
    from rdkit import Chem
    from rdkit.Chem import Draw
except ImportError:
    Chem = None
    Draw = None
    _RDKIT_MISSING_MSG = "RDKit es requerido. Instálalo con: conda install -c conda-forge rdkit"

try:
    import datamol as dm
except ImportError:
    dm = None
    _DATAMOL_MISSING_MSG = "Datamol es opcional. Instálalo con: pip install datamol"


def mol_to_image(
    smiles: str,
    size: Tuple[int, int] = (300, 300),
    sanitize: bool = True,
    add_atom_indices: bool = False,
) -> "Image.Image":
    """Convierte un SMILES a imagen PIL usando RDKit.

    Parameters
    ----------
    smiles : str
        Cadena SMILES de la molécula.
    size : tuple of int
        Dimensiones de la imagen (ancho, alto).
    sanitize : bool
        Si True, sanitiza y estandariza la molécula.
    add_atom_indices : bool
        Si True, muestra los índices de los átomos.

    Returns
    -------
    PIL.Image
        Imagen de la molécula.

    Raises
    ------
    ImportError
        Si RDKit o Pillow no están instalados.
    ValueError
        Si el SMILES es inválido.
    """
    if Image is None:
        raise ImportError(_PIL_MISSING_MSG)
    if Chem is None or Draw is None:
        raise ImportError(_RDKIT_MISSING_MSG)

    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"SMILES inválido: {smiles}")

    if sanitize:
        mol = Chem.MolFromSmiles(smiles)
        mol = Chem.rdmolops.AddHs(mol)
        Chem.rdDistGeom.EmbedMolecule(mol, randomSeed=42)
        Chem.rdMolAlign.AlignMol(mol)
        mol = Chem.rdmolops.RemoveHs(mol)

    if add_atom_indices:
        img = Draw.MolToImage(mol, size=size, options={"addAtomIndices": True})
    else:
        img = Draw.MolToImage(mol, size=size)

    return img


def dm_mol_to_image(
    smiles: str,
    size: Tuple[int, int] = (300, 300),
    sanitize: bool = True,
) -> "Image.Image":
    """Convierte un SMILES a imagen PIL usando Datamol (wrapper de RDKit).

    Parameters
    ----------
    smiles : str
        Cadena SMILES de la molécula.
    size : tuple of int
        Dimensiones de la imagen (ancho, alto).
    sanitize : bool
        Si True, sanitiza y estandariza la molécula.

    Returns
    -------
    PIL.Image
        Imagen de la molécula.

    Raises
    ------
    ImportError
        Si Datamol o Pillow no están instalados.
    ValueError
        Si el SMILES es inválido.
    """
    if Image is None:
        raise ImportError(_PIL_MISSING_MSG)
    if dm is None:
        raise ImportError(_DATAMOL_MISSING_MSG)

    mol = dm.to_mol(smiles, sanitize=sanitize)
    if mol is None:
        raise ValueError(f"SMILES inválido: {smiles}")

    return dm.to_image(mol, mol_size=size)


def mols_to_grid_image(
    smiles_list: list[str],
    size: Tuple[int, int] = (200, 150),
    legends: Optional[list[str]] = None,
    max_grid: int = 4,
    use_datamol: bool = True,
) -> "Image.Image":
    """Genera una imagen con varias moléculas en formato grid.

    Parameters
    ----------
    smiles_list : list of str
        Lista de SMILES para convertir.
    size : tuple of int
        Tamaño de cada celda del grid.
    legends : list of str, optional
        Leyendas para cada molécula.
    max_grid : int
        Número máximo de columnas del grid.
    use_datamol : bool
        Si True usa Datamol, si no RDKit.

    Returns
    -------
    PIL.Image
        Imagen con el grid de moléculas.
    """
    if Image is None:
        raise ImportError(_PIL_MISSING_MSG)

    if legends is None:
        legends = [s[:20] + "..." if len(s) > 20 else s for s in smiles_list]

    if use_datamol and dm is not None:
        mols = [dm.to_mol(s) for s in smiles_list]
        return dm.to_image(mols, mol_size=size, legends=legends)
    elif Chem is not None and Draw is not None:
        rdkit_mols = [Chem.MolFromSmiles(s) for s in smiles_list]
        return Draw.MolsToGridImage(rdkit_mols, molsPerRow=min(max_grid, len(smiles_list)), subImgSize=size, legends=legends)
    else:
        raise ImportError(
            "Se requiere RDKit o Datamol. "
            "Instálalos con: pip install datamol"
        )
