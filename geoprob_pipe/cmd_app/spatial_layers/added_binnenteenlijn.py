"""
TODO Later Should Klein: Controleer of de binnenteenlijn ook echt aan de binnenzijde is.
TODO Later Should Klein: Niet voor elk geohydrologisch model is de binnen/buiten/intredelijn benodigd.
 Maak het toevoegen van deze lijnen afhankelijk van de model keuze.
"""

from __future__ import annotations
from typing import TYPE_CHECKING

import fiona
from geoprob_pipe.utils.validation_messages import BColors
from .base_inquiry import BaseInquiry

if TYPE_CHECKING:
    from geoprob_pipe.cmd_app.cmd import ApplicationSettings


def added_binnenteenlijn(app_settings: ApplicationSettings) -> bool:
    layers = fiona.listlayers(app_settings.geopackage_filepath)

    if "binnenteenlijn" in layers:
        print(
            BColors.OKBLUE, "✔  Binnenteenlijn al toegevoegd.", BColors.ENDC
        )
        return True

    request_binnenteenlijn_filepath(app_settings=app_settings)
    return True


def request_binnenteenlijn_filepath(app_settings: ApplicationSettings):
    binnenteenlijn_inquiry = BaseInquiry(
        app_settings=app_settings,
        param="binnenteenlijn",
        specific_shape="lines",
        single_geometry=True,
    )
    binnenteenlijn_inquiry.request_filepath()
