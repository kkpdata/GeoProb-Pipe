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

if TYPE_CHECKING:
    from geoprob_pipe.cmd_app.cmd import ApplicationSettings
    
# Lijst van parameters die verwerkt kunnen worden:
# Polygon of raster alleen beschikbaar als iets per uittredepunt kan verschillen
# en afstand tot de keringlijn uitmaakt.
LIST_PARAMS: dict[str, dict] = {
    "mv_exit": {"shape": ["raster"]},
    "polderpeil": {"shape": ["line", "polygon", "raster"]},
    "buitenwaterstand_gemiddeld": {"shape": ["line"]},
    "phi_exit_gemiddeld": {"shape": ["line", "polygon", "raster"]},
    "r_exit": {"shape": ["line", "polygon", "raster"]},
    "k_wvp": {"shape": ["line"]},
    "kD_wvp": {"shape": ["line"]},
    "modelfactor_h": {"shape": ["line"]},
    "modelfactor_ff": {"shape": ["line"]},
    "modelfactor_3d": {"shape": ["line"]},
    "modelfactor_ml": {"shape": ["line"]},
    "i_c_h": {"shape": ["line"]},
    "modelfactor_u": {"shape": ["line"]},
    "modelfactor_p": {"shape": ["line"]},
    "d70": {"shape": ["line"]},
    "c_voorland": {"shape": ["line"]},
    "c_achterland": {"shape": ["line"]},
}

def valid_parameter_list(app_settings: ApplicationSettings):
    conn = sqlite3.connect(app_settings.geopackage_filepath)
    cur = conn.cursor()
    cur.execute(
        "SELECT metadata_value FROM geoprob_pipe_metadata WHERE metadata_type='geohydrologisch_model'"
    )
    model = cur.fetchone()[0]
    conn.close()

    input_list: list[str] = [param for param in LIST_PARAMS.keys()]
    valid_list = []
    match model:
        case "model4a":
            model_list = [param["name"] for param in MODEL4A_INPUT]
            valid_list = [param for param in input_list if param in model_list]

        case "wbi":
            model_list = [param["name"] for param in WBI_INPUT]
            valid_list = [param for param in input_list if param in model_list]
        case "moria":
            model_list = [param["name"] for param in MORIA_INPUT]
            valid_list = [param for param in input_list if param in model_list]
            
    return valid_list
