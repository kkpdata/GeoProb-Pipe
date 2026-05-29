"""
TODO Nu Must Klein: Voeg laag toe aan GeoPackage met visuele koppeling tussen HRD en uittredepunten.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import fiona
from .couple_objects.hrd import HRDCouple

if TYPE_CHECKING:
    from geoprob_pipe.cmd_app.cmd import ApplicationSettings


def coupled_hrd_to_uittredepunten(app_settings: ApplicationSettings) -> bool:
    """
    Voeg de HRD locaties toe aan de invoer tabel als deze zijn opgegeven.
    Als deze er al staan worden ze overschreven.

    :param ApplicationSettings app_settings: Object met de instellingen van de applicatie
    :return: _description_
    :rtype: bool
    """    

    layers = fiona.listlayers(app_settings.geopackage_filepath)

    if "hrd_locaties" not in layers:
        return True  # Geen Hydra-locatie geïmporteerd, dan ook niks koppelen.

    HRDCouple(app_settings).couple_exit_points()

    return True
