from __future__ import annotations

import configparser
import sqlite3
from typing import TYPE_CHECKING

from InquirerPy.prompts.list import ListPrompt

if TYPE_CHECKING:
    from geoprob_pipe.cmd_app.cmd import ApplicationSettings
    
def batch_inquiry(app_settings: ApplicationSettings):
    """
    Keuzemenu voor het gebruik van ee batch input bestand of handmatige invoer.

    :param app_settings: _description_
    """    
    choices_list = [
        "Nee, handmatig invoeren",
        "Ja, invoeren via `batch_input.ini` bestand",
        "Maak het `batch_input.ini` bestand aan"
    ]
    while True:
        choice = ListPrompt(
            message=("Wil je de gis-lagen handmatig invoeren of via een batch_input.ini bestand?"),
            choices=choices_list,
            default=choices_list[0]
        ).execute()
        
        match choice:
            case "Nee, handmatig invoeren":
                return
            case "Ja, invoeren via `batch_input.ini` bestand":
                app_settings.batch_input = True
                return
            case "Maak het `batch_input.ini` bestand aan":
                batch_config_writer(app_settings)
                app_settings.batch_input = True
                return


def batch_config_writer(app_settings: ApplicationSettings):
    """
    Functie om het bestand op te zetten voor alle benodigde handelingen.

    :param app_settings: _description_
    """    
    conn = sqlite3.connect(app_settings.geopackage_filepath)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT metadata_value FROM geoprob_pipe_metadata WHERE metadata_type = ?",
        ("ruimtelijke_parameters",),
    )
    parameters: list[str] = cursor.fetchone()[0].split(", ")
    conn.close()
    
    datasets = [
        {"name": "vakindeling", "path": "", "layer": "", "column": ""},
        {"name": "uittredepunten", "path": "", "layer": "", "column": ""},
        {"name": "binnenteenlijn", "path": "", "layer": "", "column": ""},
        {"name": "buitenteenlijn", "path": "", "layer": "", "column": ""},
        {"name": "intredelijn", "path": "", "layer": "", "column": ""},
    ]
    if not parameters == ['']:
        for parameter in parameters:
            datasets.append({
                "name": f"{parameter}", "path": "", "layer": ""
            })

    config = configparser.ConfigParser()

    for ds in datasets:
        config[ds["name"]] = {
            "path": ds["path"],
            "layer": ds["layer"],
            "column": ds["column"]
        }

    with open(f"{app_settings.workspace_dir}/batch_input.ini", "w") as f:
        config.write(f)
