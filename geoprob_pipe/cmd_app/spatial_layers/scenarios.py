from __future__ import annotations

import sqlite3
from typing import TYPE_CHECKING

import InquirerPy.prompts.input as prompt

if TYPE_CHECKING:
    from geoprob_pipe.cmd_app.cmd import ApplicationSettings


def added_scenarios(app_settings: ApplicationSettings):
    """
    Check of de scenarios voor ruimtelijke invoer al zijn toegevoegd aan de metadata.

    :param app_settings: _description_
    :return: _description_
    """    
    conn = sqlite3.connect(app_settings.geopackage_filepath)
    cur = conn.cursor()
    cur.execute(
        "SELECT EXISTS (SELECT 1 FROM geoprob_pipe_metadata WHERE metadata_type = ?)",
        ("ruimtelijke_scenarios",)
        )
    check = cur.fetchone()[0] == 1
    if not check:
        request_scenarios(app_settings)
    return True


def request_scenarios(app_settings: ApplicationSettings):
    """
    Vraag de mogelijke lijst van scenarios voor de ruimtelijke invoer op en voeg
    deze toe aan de metadata.

    :param app_settings: _description_
    """    
    scenario_input_is_valid = False
    while scenario_input_is_valid is False:
        scenario_input: str = prompt.InputPrompt(
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
            scenarios = scenario_input.split(",")

        
        sql_upsert = """
        INSERT INTO geoprob_pipe_metadata (metadata_type, values)
        VALUES (?, ?)
        ON CONFLICT(metadata_type) DO UPDATE SET
            values = excluded.values
        """
        conn = sqlite3.connect(app_settings.geopackage_filepath)
        conn.cursor().execute(sql_upsert, ("ruimtelijke_scenarios", scenarios))
        conn.commit()
        conn.close()