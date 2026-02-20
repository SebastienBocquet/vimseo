# Copyright 2021 IRT Saint Exupéry, https://www.irt-saintexupery.com
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License version 3 as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Sequence

from meshio import read

import pyvista as pv
import os
import glob

if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path

    from numpy import ndarray


@dataclass
class Field:
    """A field."""

    path: str | Path = ""
    point_data: ndarray | None = None
    cell_data: ndarray | None = None
    mesh_points: ndarray | None = None
    mesh_cells: ndarray | None = None

    @property
    def cell_variable_names(self) -> Iterable[str]:
        return list(self.cell_data.keys())

    @property
    def point_variable_names(self) -> Iterable[str]:
        return list(self.point_data.keys())

    @classmethod
    def load(cls, path: Path | str):
        field = read(path)
        return cls(
            path=path,
            point_data=field.point_data,
            cell_data=field.cell_data,
            mesh_points=field.points,
            mesh_cells=field.cells,
        )



def extract_line_y(
    vtu_file: str,
    x_probe: float = 0.0,
    n_points: int = 200,
    fields: list[str] = None,
    y_min: float = None,
    y_max: float = None,
) -> dict:
    """
    Extrait les valeurs des champs le long d'une ligne verticale (x=x_probe)
    depuis un fichier VTU 2D.

    Paramètres
    ----------
    vtu_file  : chemin vers le fichier .vtu
    x_probe   : position x de la ligne d'extraction
    n_points  : nombre de points sur la ligne
    fields    : liste des champs à extraire (None = tous)
    y_min     : borne inférieure en y (None = auto depuis le maillage)
    y_max     : borne supérieure en y (None = auto depuis le maillage)

    Retourne
    --------
    dict avec clés : 'y' + un tableau par champ extrait
    """
    mesh = pv.read(vtu_file)

    # Bornes automatiques depuis le maillage si non spécifiées
    bounds = mesh.bounds  # (xmin, xmax, ymin, ymax, zmin, zmax)
    y0 = y_min if y_min is not None else bounds[2]
    y1 = y_max if y_max is not None else bounds[3]

    # Définir la ligne d'extraction
    point_a = (x_probe, y0, 0.0)
    point_b = (x_probe, y1, 0.0)

    # Échantillonnage le long de la ligne (interpolation)
    line = mesh.sample_over_line(point_a, point_b, resolution=n_points)

    # Coordonnées y
    y_coords = line.points[:, 1]

    # Champs disponibles
    available = list(line.point_data.keys())
    if fields is None:
        fields = available
    else:
        fields = [f for f in fields if f in available]
        missing = [f for f in fields if f not in available]
        if missing:
            print(f"  [WARN] Champs non trouvés dans {vtu_file} : {missing}")
            print(f"  [INFO] Champs disponibles : {available}")

    result = {"y": y_coords}
    for field in fields:
        data = line.point_data[field]
        result[field] = data

    return result


def vtu_to_png(files: Sequence[str], scalar_name: str, output_folder: str, clim: tuple[float, float] | None = None):
    """Convert a sequence of .vtu files to .png images using PyVista."""

    # --- Boucle de rendu ---
    plotter = pv.Plotter(off_screen=True) # Fenêtre invisible

    for i, filepath in enumerate(files):
        mesh = pv.read(filepath)

        # On vide le plotter à chaque itération pour ne pas superposer
        plotter.clear()

        # Ajout du maillage avec configuration de la colorbar
        plotter.add_mesh(
            mesh,
            scalars=scalar_name,
            cmap="viridis",
            clim=clim,
            show_scalar_bar=True
        )

        # Optionnel : Ajouter un titre ou le nom du fichier sur l'image
        plotter.add_text(f"Step: {i}", font_size=10, color="black")

        # Ajuster la caméra (automatique au premier fichier, puis fixe)
        if i == 0:
            plotter.view_isometric()

        # Sauvegarde
        filename = os.path.basename(filepath).replace(".vtu", f"_{scalar_name}.png")
        save_path = os.path.join(output_folder, filename)
        plotter.screenshot(save_path)

        print(f"Image sauvegardée : {filename}")

    plotter.close()
    print("Terminé !")
