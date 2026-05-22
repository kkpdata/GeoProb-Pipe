from __future__ import annotations

import sqlite3
from typing import TYPE_CHECKING

import InquirerPy.prompts.input as prompt

from geoprob_pipe.utils.validation_messages import BColors

from .valid_parameters import valid_parameter_list

if TYPE_CHECKING:
    from geoprob_pipe.cmd_app.cmd import ApplicationSettings


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
    
    parameters: list[str] = []

    while True:
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
            parameters = []
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

            if not all(x in valid_list for x in parameters):  # type:ignore
                print(
                    BColors.WARNING,
                    "Een of meerdere van de opgegeven parameters zijn niet geschikt voor ruimtelijke invoer.",
                    BColors.ENDC,
                )
                continue
        break

    sql_update = "UPDATE geoprob_pipe_metadata SET metadata_value = ? WHERE metadata_type = ?"
    sql_insert = "INSERT INTO geoprob_pipe_metadata (metadata_type, metadata_value) VALUES (?, ?)"

    with conn:  # transaction
        cur = conn.execute(
            sql_update, (", ".join(parameters), "ruimtelijke_parameters")
        )
        if cur.rowcount == 0:
            conn.execute(
                sql_insert, ("ruimtelijke_parameters", ", ".join(parameters))
            )

    conn.commit()
    conn.close()
