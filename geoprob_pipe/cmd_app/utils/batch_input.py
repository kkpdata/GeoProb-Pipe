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

    config = configparser.ConfigParser()
    
    config["vakindeling"] = {
        "filepath": "",
        "database_layer": "",
        "vak_naam_kolom": "",
        "vak_id_kolom": ""
    }
    
    config["uittredepunten"] = {
        "filepath": "",
        "database_layer": "",
        "mv_exit_kolom": ""
    }
    
    config["binnenteenlijn"] = {
        "filepath": "",
        "database_layer": "",
    }
    
    config["buitenteenlijn"] = {
        "filepath": "",
        "database_layer": "",
    }
    
    config["intredelijn"] = {
        "filepath": "",
        "database_layer": "",
    }

    if not parameters == ['']:
        for parameter in parameters:
            config[parameter] = {
                "filepath": "",
                "database_layer": ""
            }
    
    with open(f"{app_settings.workspace_dir}/batch_input.ini", "w") as f:
        config.write(f)
