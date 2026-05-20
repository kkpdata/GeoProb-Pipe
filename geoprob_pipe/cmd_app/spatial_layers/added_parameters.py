from __future__ import annotations

import sqlite3
from typing import TYPE_CHECKING

import InquirerPy.prompts.input as prompt

from.utils import valid_parameter_list
from geoprob_pipe.utils.validation_messages import BColors

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
    
    valid_list = valid_parameter_list(app_settings)

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
