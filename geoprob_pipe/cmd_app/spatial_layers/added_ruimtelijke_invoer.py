from __future__ import annotations

import sqlite3
from typing import TYPE_CHECKING

import fiona

from geoprob_pipe.cmd_app.spatial_layers import LIST_PARAMS, BaseInquiry
from geoprob_pipe.utils.validation_messages import BColors

if TYPE_CHECKING:
    from geoprob_pipe.cmd_app.cmd import ApplicationSettings


def added_ruimtelijke_input(app_settings: ApplicationSettings) -> bool:
    conn = sqlite3.connect(app_settings.geopackage_filepath)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT metadata_value FROM geoprob_pipe_metadata WHERE metadata_type = ?",
        ("ruimtelijke_parameters",),
    )
    parameters: list[str] = cursor.fetchone()[0].split(", ")
    conn.close()
    list_layers: list[str] = fiona.listlayers(app_settings.geopackage_filepath)
    if parameters == ['']: # De split maakt één lege string als de uit de metadata gelezen string leeg is.
        print(
            BColors.OKBLUE,
            "✔  Geen ruimtelijke parameter invoer.",
            BColors.ENDC,
        )
        return True

    for parameter in parameters:
        if any(parameter in layer.split("_")[0] for layer in list_layers):
                    print(
                        BColors.OKBLUE,
                        f"✔  {parameter} al toegevoegd.",
                        BColors.ENDC,
                    )
                    return True

        inquiry = BaseInquiry(
            app_settings=app_settings,
            param=f"{parameter}",
            specific_shape=LIST_PARAMS[parameter]["shape"],
            include_value=True
        )
        inquiry.request_filepath()
        
    return True
