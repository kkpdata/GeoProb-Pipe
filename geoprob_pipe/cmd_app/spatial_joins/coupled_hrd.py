"""
TODO Nu Must Klein: Voeg laag toe aan GeoPackage met visuele koppeling tussen HRD en uittredepunten.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import fiona
from hrd_couple import HRDCouple

if TYPE_CHECKING:
    from geoprob_pipe.cmd_app.cmd import ApplicationSettings


def coupled_hrd_to_uittredepunten(app_settings: ApplicationSettings) -> bool:

    layers = fiona.listlayers(app_settings.geopackage_filepath)

    if "hrd_locaties" not in layers:
        return True  # Geen Hydra-locatie geïmporteerd, dan ook niks koppelen.

    HRDCouple(app_settings).couple_exit_points()

    return True
