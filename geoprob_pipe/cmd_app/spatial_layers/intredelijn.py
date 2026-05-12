"""
TODO Later Should Klein: Controleer of de intredelijn ook echt aan de binnenzijde is.

"""

from __future__ import annotations

from typing import TYPE_CHECKING

import fiona

from geoprob_pipe.cmd_app.spatial_layers import BaseInquiry
from geoprob_pipe.utils.validation_messages import BColors

if TYPE_CHECKING:
    from geoprob_pipe.cmd_app.cmd import ApplicationSettings


def added_intredelijn(app_settings: ApplicationSettings) -> bool:
    layers = fiona.listlayers(app_settings.geopackage_filepath)

    if "intredelijn" in layers:
        print(BColors.OKBLUE, f"✔  Intredelijn al toegevoegd.", BColors.ENDC)
        return True

    request_intredelijn_filepath(app_settings=app_settings)
    return True


def request_intredelijn_filepath(app_settings: ApplicationSettings):
    intredelijn_inquiry = BaseInquiry(
        app_settings=app_settings,
        param="intredelijn",
        specific_shape="lines"
    )
    intredelijn_inquiry.request_filepath()
