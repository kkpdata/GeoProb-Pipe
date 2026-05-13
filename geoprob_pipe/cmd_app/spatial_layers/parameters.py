from __future__ import annotations

import sqlite3
from typing import TYPE_CHECKING

import InquirerPy.prompts.input as prompt

from geoprob_pipe.calculations.systems.model4a.initial_input import (
    INITIAL_INPUT as MODEL4A_INPUT,
)
from geoprob_pipe.calculations.systems.moria.initial_input import (
    INITIAL_INPUT as MORIA_INPUT,
)
from geoprob_pipe.calculations.systems.wbi.initial_input import (
    INITIAL_INPUT as WBI_INPUT,
)
from geoprob_pipe.utils.validation_messages import BColors

if TYPE_CHECKING:
    from geoprob_pipe.cmd_app.cmd import ApplicationSettings

# Lijst van parameters die verwerkt kunnen worden:
# Polygon of raster alleen beschikbaar als iets per uittredepunt kan verschillen
# en afstand tot de keringlijn uitmaakt.
LIST_PARAMS: list[dict] = [
    {"name": "mv_exit", "shape": ["raster"]},
    {"name": "polderpeil", "shape": ["line", "polygon", "raster"]},
    {"name": "buitenwaterstand_gemiddeld", "shape": ["line"]},
    {"name": "phi_exit_gemiddeld", "shape": ["line", "polygon", "raster"]},
    {"name": "r_exit", "shape": ["line", "polygon", "raster"]},
    {"name": "k_wvp", "shape": ["line"]},
    {"name": "kD_wvp", "shape": ["line"]},
    {"name": "modelfactor_h", "shape": ["line"]},
    {"name": "modelfactor_ff", "shape": ["line"]},
    {"name": "modelfactor_3d", "shape": ["line"]},
    {"name": "modelfactor_ml", "shape": ["line"]},
    {"name": "i_c_h", "shape": ["line"]},
    {"name": "modelfactor_u", "shape": ["line"]},
    {"name": "modelfactor_p", "shape": ["line"]},
    {"name": "d70", "shape": ["line"]},
    {"name": "c_voorland", "shape": ["line"]},
    {"name": "c_achterland", "shape": ["line"]},
]


def added_parameters(app_settings: ApplicationSettings):
    """
    Check of de parameters voor ruimtelijke invoer al zijn toegevoegd aan de metadata.

    :param app_settings: `ApplicationSettings` object.
    :return: bool
    """
    conn = sqlite3.connect(app_settings.geopackage_filepath)
    cur = conn.cursor()
    cur.execute(
        "SELECT EXISTS (SELECT 1 FROM geoprob_pipe_metadata WHERE metadata_type = ?)",
        ("ruimtelijke_parameters",),
    )
    check = cur.fetchone()[0] == 1
    if not check:
        request_parameters(app_settings)
    return True


def request_parameters(app_settings: ApplicationSettings):
    """
    Method voor het opvragen van de lijst met parameters waarvoor ruimtelijke
    invoer gewenst is. Er wordt gecheckd of deze paramerters ondersteund worden
    en of deze in het gekozen model zitten.

    :param app_settings: `ApplicationSettings` object.
    """
    conn = sqlite3.connect(app_settings.geopackage_filepath)
    cur = conn.cursor()
    cur.execute(
        "SELECT metadata_value FROM geoprob_pipe_metadata WHERE metadata_type='geohydrologisch_model'"
    )
    model = cur.fetchone()[0]
    # conn wordt later gesloten.

    input_list: list[str] = [param["name"] for param in LIST_PARAMS]
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

    scenario_input_is_valid = False
    while scenario_input_is_valid is False:
        parameter_input: str = prompt.InputPrompt(
            message=(
                """
Specificeer welke parameters je wilt toevoegen als ruimtelijke input.
Doe dit door de namen gescheiden met comma's op te geven.
Type 'list' om de lijst te zien met alle parameters die invoerbaar zijn voor dit model.
Als je geen ruimtelijke input wilt ingeven druk dan op enter zonder iets in te vullen. 
                """
            )
        ).execute()
        if parameter_input == "":
            parameters = ""
        elif parameter_input == "list":
            params_str = ", ".join(valid_list)  # type:ignore
            print(
                BColors.OKBLUE,
                f"De volgende parameters zijn beschikbaar voor ruimtelijke input: {params_str}",
                BColors.ENDC,
            )
            continue

        else:
            parameters = parameter_input.split(",")

            if parameters not in valid_list:  # type:ignore
                print(
                    BColors.WARNING,
                    "Een of meerdere van de opgegeven parameters zijn niet geschikt voor ruimtelijke invoer.",
                    BColors.ENDC,
                )
                continue
        scenario_input_is_valid = True

    sql_update = "UPDATE geoprob_pipe_metadata SET metadata_value = ? WHERE metadata_type = ?"
    sql_insert = "INSERT INTO geoprob_pipe_metadata (metadata_type, metadata_value) VALUES (?, ?)"

    with conn:  # transaction
        cur = conn.execute(sql_update, (parameters, "ruimtelijke_parameters"))  # type:ignore
        if cur.rowcount == 0:
            conn.execute(sql_insert, ("ruimtelijke_parameters", parameters))  # type:ignore

    conn.commit()
    conn.close()
