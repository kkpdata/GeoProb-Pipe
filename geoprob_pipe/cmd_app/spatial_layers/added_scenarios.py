from __future__ import annotations

import sqlite3
from typing import TYPE_CHECKING

from InquirerPy.prompts.input import InputPrompt

from geoprob_pipe.utils.validation_messages import BColors

if TYPE_CHECKING:
    from geoprob_pipe.cmd_app.cmd import ApplicationSettings


def added_scenarios(app_settings: ApplicationSettings):
    """
    Check of de scenarios voor ruimtelijke invoer al zijn toegevoegd aan de metadata.

    :param app_settings: `ApplicationSettings` object.
    :return: bool
    """
    conn = sqlite3.connect(app_settings.geopackage_filepath)
    cur = conn.cursor()
    cur.execute(
        "SELECT EXISTS (SELECT 1 FROM geoprob_pipe_metadata WHERE metadata_type = ?)",
        ("ruimtelijke_scenarios",),
    )
    check = cur.fetchone()[0] == 1
    if not check:
        request_scenarios(app_settings)
    return True


def request_scenarios(app_settings: ApplicationSettings):
    """
    Vraag de mogelijke lijst van scenarios voor de ruimtelijke invoer op en voeg
    deze toe aan de metadata.

    :param app_settings: `ApplicationSettings` object.
    """

    while True:
        scenario_input: str = InputPrompt(
            message="""
Specificeer welke scenarios je wilt toevoegen als ruimtelijke input.
Doe dit door de namen gescheiden met comma's op te geven. Bijvoorbeeld: Scenario1, Scenario2. 
De scenario namen moeten als kolom in de attributes van de laag staan.
Als je geen ruimtelijke input wilt ingeven druk dan op enter zonder iets in te vullen. 
            """
        ).execute()
        if scenario_input == "":
            scenarios = ""
        else:
            try:
                scenarios = scenario_input.split(",")
                scenarios = ", ".join(scenarios)
            except Exception:
                print(
                    BColors.OKBLUE,
                    f"Geen scenarios toegevoegd. '{scenario_input}' is geen geldige invoer.",
                    BColors.ENDC,
                )
                continue
        break

    conn = sqlite3.connect(app_settings.geopackage_filepath)

    sql_update = "UPDATE geoprob_pipe_metadata SET metadata_value = ? WHERE metadata_type = ?"
    sql_insert = "INSERT INTO geoprob_pipe_metadata (metadata_type, metadata_value) VALUES (?, ?)"

    with conn:  # transaction
        cur = conn.execute(sql_update, (scenarios, "ruimtelijke_scenarios"))  # type:ignore
        if cur.rowcount == 0:
            conn.execute(sql_insert, ("ruimtelijke_scenarios", scenarios))  # type:ignore

    conn.commit()
    conn.close()
