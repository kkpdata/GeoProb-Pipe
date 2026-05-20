from __future__ import annotations

import sqlite3
from typing import TYPE_CHECKING

from shape_couple import ShapeCouple
from geoprob_pipe.utils.validation_messages import BColors

if TYPE_CHECKING:
    from geoprob_pipe.cmd_app.cmd import ApplicationSettings


def coupled_parameters_to_uittredepunten(
    app_settings: ApplicationSettings,
) -> bool:
    conn = sqlite3.connect(app_settings.geopackage_filepath)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT metadata_value FROM geoprob_pipe_metadata WHERE metadata_type = ?",
        ("ruimtelijke_parameters",),
    )
    parameters: list[str] = cursor.fetchone()[0].split(", ")
    conn.close()
    if parameters == []:
        print(
            BColors.OKBLUE,
            "✔  Geen ruimtelijke koppelingen.",
            BColors.ENDC,
        )
        return True

    for parameter in parameters:
        ShapeCouple(app_settings, parameter).couple_exit_points()

    return True
