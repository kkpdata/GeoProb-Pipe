from __future__ import annotations

import configparser
import sqlite3
import sys
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
        "Maak het `batch_input.ini` bestand aan",
    ]
    while True:
        choice = ListPrompt(
            message=(
                "Wil je de gis-lagen handmatig invoeren of via een batch_input.ini bestand?"
            ),
            choices=choices_list,
            default=choices_list[0],
        ).execute()

        match choice:
            case "Nee, handmatig invoeren":
                update_batch_metadata(app_settings=app_settings, value=False)
                return
            case "Ja, invoeren via `batch_input.ini` bestand":
                app_settings.batch_input = True
                return
            case "Maak het `batch_input.ini` bestand aan":
                batch_config_writer(app_settings)
                app_settings.batch_input = True
                ready_inquiry()
                return


def ready_inquiry():
    """
    Keuzemenu als wacht periode voor het invullen van batch_input.ini.
    """
    choices_list = [
        "batch_input.ini is klaar voor uitlezen",
        "applicatie afsluiten",
    ]
    while True:
        choise = ListPrompt(
            message="Is het batch_input.ini bestand klaar voor gebruik?",
            choices=choices_list,
            default=choices_list[0],
        ).execute()
        match choise:
            case "batch_input.ini is klaar voor uitlezen":
                return
            case "applicatie afsluiten":
                sys.exit("Applicatie is afgesloten.")


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
        "vak_id_kolom": "",
    }

    config["uittredepunten"] = {
        "filepath": "",
        "database_layer": "",
        "mv_exit_kolom": "",
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

    if not parameters == [""]:
        for parameter in parameters:
            config[parameter] = {"filepath": "", "database_layer": ""}

    with open(f"{app_settings.workspace_dir}/batch_input.ini", "w") as f:
        f.write("""
# Dit is een bestand om een deel van de invoer van GeoProb-Pipe in
# een keer in te voeren. Hier moeten dezelfde paden, lagen en kolommen
# worden ingevoerd als met de handmatige invoer.

# Geef bij 'filepath' het volledige bestandspad op naar het bestand met de invoer.
# Als het bestand een shapefile is mag je de volgende waarde leeg houden.
# Deze wordt alleen uitgelezen bij een database(.gdb of .gpkg)
# Geef bij 'database_layer' de naam op van de laag waarin de invoer staat.
# Soms moet er ook nog een kolom worden opgegeven:
# Geef bij '*_kolom' de kolom naam op waarin de opgevraagde parameter in staat.

""")
        config.write(f)

def update_batch_metadata(app_settings: ApplicationSettings, value: bool):
    conn = sqlite3.connect(app_settings.geopackage_filepath)
    
    sql_update = "UPDATE geoprob_pipe_metadata SET metadata_value = ? WHERE metadata_type = ?"
    sql_insert = "INSERT INTO geoprob_pipe_metadata (metadata_type, metadata_value) VALUES (?, ?)"

    with conn:  # transaction
        cur = conn.execute(sql_update, (value, "batch_inquiry"))  # type:ignore
        if cur.rowcount == 0:
            conn.execute(sql_insert, ("batch_inquiry", value))  # type:ignore
        conn.execute(sql_update, (value, "batch_inquiry"))

    conn.commit()
    conn.close()

def read_metadata(app_settings: ApplicationSettings):
    conn = sqlite3.connect(app_settings.geopackage_filepath)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT metadata_value FROM geoprob_pipe_metadata WHERE metadata_type = ?",
        ("batch_inquiry",),
    )
    row = cursor.fetchone()
    conn.close()
    if row is None:
        return True
    
    return bool(int(row[0]))