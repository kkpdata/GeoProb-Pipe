from __future__ import annotations

import sqlite3
from typing import TYPE_CHECKING

from geoprob_pipe.calculations.systems.model4a.initial_input import (
    INITIAL_INPUT as MODEL4A_INPUT,
)
from geoprob_pipe.calculations.systems.moria.initial_input import (
    INITIAL_INPUT as MORIA_INPUT,
)
from geoprob_pipe.calculations.systems.wbi.initial_input import (
    INITIAL_INPUT as WBI_INPUT,
)
from geoprob_pipe.cmd_app.spatial_layers import LIST_PARAMS

if TYPE_CHECKING:
    from geoprob_pipe.cmd_app.cmd import ApplicationSettings

def valid_parameter_list(app_settings: ApplicationSettings):
    conn = sqlite3.connect(app_settings.geopackage_filepath)
    cur = conn.cursor()
    cur.execute(
        "SELECT metadata_value FROM geoprob_pipe_metadata WHERE metadata_type='geohydrologisch_model'"
    )
    model = cur.fetchone()[0]
    # conn wordt later gesloten.

    input_list: list[str] = [param for param in LIST_PARAMS.keys()]
    valid_list = []
    match model:
        case "model4a":
            model_list = [param["name"] for param in MODEL4A_INPUT]
            valid_list = [x for x in input_list if x in model_list]

        case "wbi":
            model_list = [param["name"] for param in WBI_INPUT]
            valid_list = [x for x in input_list if x in model_list]
        case "moria":
            model_list = [param["name"] for param in MORIA_INPUT]
            valid_list = [x for x in input_list if x in model_list]
            
    return valid_list