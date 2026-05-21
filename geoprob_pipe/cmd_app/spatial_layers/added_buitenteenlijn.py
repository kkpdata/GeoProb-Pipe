"""
TODO Later Should Klein: Controleer of de buitenteenlijn ook echt aan de buitenzijde is.

"""

from __future__ import annotations

from typing import TYPE_CHECKING

import fiona

from .base_inquiry import BaseInquiry
from geoprob_pipe.utils.validation_messages import BColors

if TYPE_CHECKING:
    from geoprob_pipe.cmd_app.cmd import ApplicationSettings


def added_buitenteenlijn(app_settings: ApplicationSettings) -> bool:
    layers = fiona.listlayers(app_settings.geopackage_filepath)

    if "buitenteenlijn" in layers:
        print(
            BColors.OKBLUE, "✔  Buitenteenlijn al toegevoegd.", BColors.ENDC
        )
        return True

    request_buitenteenlijn_filepath(app_settings=app_settings)
    return True


def request_buitenteenlijn_filepath(app_settings: ApplicationSettings):
    buitenteenlijn_inquiry = BaseInquiry(
        app_settings=app_settings,
        param="buitenteenlijn",
        specific_shape="lines",
        single_geometry=True
    )
    buitenteenlijn_inquiry.request_filepath()
