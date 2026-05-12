from __future__ import annotations
from InquirerPy import inquirer
from typing import TYPE_CHECKING
import sys
from geoprob_pipe.utils.validation_messages import BColors
from geoprob_pipe.cmd_app.spatial_layers.hrd.import_from_hrd import import_from_hrd
from geoprob_pipe.cmd_app.spatial_layers.hrd.import_from_other_geopackage import import_from_other_geopackage
import fiona
import sqlite3
if TYPE_CHECKING:
    from geoprob_pipe.cmd_app.cmd import ApplicationSettings


def _hrd_data_requested(app_settings: ApplicationSettings) -> bool:

    # Check if asked to store HRD data
    file_path = app_settings.geopackage_filepath
    conn = sqlite3.connect(file_path)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM geoprob_pipe_metadata WHERE metadata_type = 'extract_hrd_data' LIMIT 1;")
    row = cursor.fetchone()
    asked: bool = row is not None

    if asked:
        cursor.close()
        return bool(int(row[2]))

    # Optionally ask and then store choice
    choices_list = ["Ja", "Nee"]
    choice = inquirer.select(
        message=f"Wil je HRD-data importeren? Dit is optioneel. "
                f"Je kunt ook handmatig overschrijdingsfrequentielijnen toevoegen.",
        choices=choices_list, default=choices_list[0]).execute()
    keuze = True
    if choice == "Nee":
        keuze = False
    cursor.execute(
        f"INSERT INTO geoprob_pipe_metadata (metadata_type, 'values') VALUES ('extract_hrd_data', {keuze});")
    conn.commit()
    cursor.close()
    return keuze


def _hrd_data_imported(app_settings: ApplicationSettings) -> bool:

    # Check if locations shape already added
    layers = fiona.listlayers(app_settings.geopackage_filepath)
    if "hrd_locaties" not in layers:
        return False

    # Check overschrijdingsfrequentielijnen already added
    conn = sqlite3.connect(app_settings.geopackage_filepath)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables_names = [row[0] for row in cursor.fetchall()]
    conn.close()
    if "fragility_values_invoer_hrd" not in tables_names:
        return False

    return True


def _ask_for_import_method() -> str:
    choices_list = [
        "Hydra-NL database",
        "Ander GeoProb-Pipe bestand",
        "Applicatie afsluiten",
    ]
    choice = inquirer.select(
        message=f"Welke bron wil je gebruiken voor de Hydra-NL data?",
        choices=choices_list, default=choices_list[0]).execute()
    if choice == choices_list[0]:
        return "from_hrd"
    elif choice == choices_list[1]:
        return "from_other_geopackage"
    elif choice == choices_list[2]:
        sys.exit(f"Applicatie is afgesloten.")
    raise NotImplementedError(f"Unknown choice '{choice}'. Contact the developer.")


def added_hrd_fragility_curves(app_settings: ApplicationSettings):

    # User wants HRD data in Geopackage?
    requested: bool = _hrd_data_requested(app_settings=app_settings)
    if not requested:
        print(BColors.OKBLUE, f"✔  HRD-data als niet nodig aangemerkt.", BColors.ENDC)
        return True

    # Check HRD locations and fragility curves are added to database
    already_imported: bool = _hrd_data_imported(app_settings=app_settings)
    if already_imported:
        print(BColors.OKBLUE, f"✔  HRD-data al geïmporteerd.", BColors.ENDC)
        return True

    # If not imported, start with import method
    import_method: str = _ask_for_import_method()
    if import_method == "from_other_geopackage":
        import_from_other_geopackage(app_settings=app_settings)
    elif import_method == "from_hrd":
        import_from_hrd(app_settings=app_settings)
    else:
        raise NotImplementedError(f"Import method '{import_method}' is unknown. Contact a developer.")

    return True
