from __future__ import annotations
from InquirerPy import inquirer
from typing import Optional, TYPE_CHECKING
import os
from pandas import DataFrame
from datetime import datetime
from pathlib import Path
import sys
from importlib.metadata import distributions
from geopandas import GeoDataFrame
from geoprob_pipe.questionnaire.utils.misc import get_geoprob_pipe_version_number
from geoprob_pipe.questionnaire.comparisons.start_comparison import start_comparison
from geoprob_pipe.utils.validation_messages import BColors
if TYPE_CHECKING:
    from geoprob_pipe.questionnaire.cmd import ApplicationSettings


def created_project(app_settings: ApplicationSettings) -> bool:

    choices_list = [
        "Bestaand project openen",
        "Nieuw project starten",
        "Twee projectbestanden vergelijken",
        "Inspecteer een enkele berekening",
        "Applicatie afsluiten"
    ]
    choice = inquirer.select(
        message="Wil je verder gaan met een bestaand project, "
                "een nieuw project starten, "
                "of twee project bestanden vergelijken?",
        choices=choices_list,
        default=choices_list[0],
    ).execute()

    if choice == choices_list[0]:
        specify_path_to_existing_project(app_settings)
        return True
    elif choice == choices_list[1]:
        specify_dir_for_new_project(app_settings)
        return True
    elif choice == choices_list[2]:
        start_comparison()
        sys.exit("Applicatie afgesloten")
    elif choice == choices_list[3]:
        example_script = r"""
from geoprob_pipe import reproduce_single_calc, ParallelSystemReliabilityCalculation

calc: ParallelSystemReliabilityCalculation = reproduce_single_calc(
    geopackage_filepath=r"/pad/naar/het/bestand/geoprob_pipe.gpkg",
    uittredepunt_id=1234,            # Replace with id of interest
    ondergrondscenario_naam="PL",    # Replace with scenario name of interest
)
"""
        print(f"""
=== Uitleg =============================================================================================================
Met de onderstaande code kun je in de Python console een enkele berekening reproduceren en inspecteren. Dit is 
bijvoorbeeld handig wanneer je de Python objecten wilt vergelijken met de gegenereerde in- en uitvoer. Of wanneer je een 
vergelijk aan het maken bent met de PTK-tool.  

Om dit te doen kopieer je de onderstaande code naar de Python console. Zorg er voor dat je de Python console gebruikt 
waar je GeoProb-Pipe ook hebt geïnstalleerd. Vervang vervolgens nog het uittredepunt id met het id wat je wilt bekijken. 
Hetzelfde doe je voor de ondergrondscenario_naam. 

Het reproduceren en herberekenen duurt slechts enkele seconden. Daarna kun je de objecten inspecteren.   

Let op: Dit vergt wel enige ervaring met Python. 
========================================================================================================================
{example_script}
========================================================================================================================
""")
        sys.exit("Applicatie afgesloten")
    return False


def specify_path_to_existing_project(app_settings: ApplicationSettings):
    filepath: Optional[str] = None
    filepath_is_valid = False
    while filepath_is_valid is False:
        filepath: str = inquirer.text(
            message="Specificeer het volledige bestandspad naar het .geoprob_pipe.gpkg-bestand.",
        ).execute()

        filepath = filepath.replace('"', '')

        if not filepath.endswith(".geoprob_pipe.gpkg"):
            print(BColors.WARNING, f"Het bestand moet een .geoprob_pipe.gpkg-bestand zijn. Jouw invoer "
                                   f"{os.path.basename(filepath)} eindigt niet op deze extensie.", BColors.ENDC)
            continue
        if not os.path.exists(filepath):
            print(BColors.WARNING, f"Het opgegeven bestandspad bestaat niet.", BColors.ENDC)
            continue

        filepath_is_valid = True

    app_settings.workspace_dir = os.path.dirname(filepath)
    app_settings.geopackage_filename = os.path.basename(filepath)


def specify_dir_for_new_project(app_settings: ApplicationSettings):
    workspace_dir: Optional[str] = None
    workspace_dir_is_valid = False
    while workspace_dir_is_valid is False:
        workspace_dir: str = inquirer.text(
            message="Specificeer het volledige pad naar de map waar je het GeoProb-Pipe-bestand wilt opslaan.",
        ).execute()
        workspace_dir = workspace_dir.replace('"', '')

        if not os.path.exists(workspace_dir):
            print(BColors.WARNING, f"De opgegeven map bestaat niet.", BColors.ENDC)
            continue
        if not os.path.isdir(workspace_dir):
            print(BColors.WARNING, f"De opgegeven locatie is geen map.", BColors.ENDC)
            continue

        workspace_dir_is_valid = True

    app_settings.workspace_dir = workspace_dir

    # Continue questionnaire
    specify_project_filename(app_settings)


def specify_project_filename(app_settings: ApplicationSettings):
    filename: Optional[str] = None
    filename_is_valid = False
    while filename_is_valid is False:
        project_name: str = inquirer.text(
            message="Specificeer een bestandsnaam voor het project. "
                    "Het bestand wordt opgeslagen met een .geoprob_pipe.gpkg-extensie.",
        ).execute()

        filename = f"{project_name}.geoprob_pipe.gpkg"
        filepath = os.path.join(app_settings.workspace_dir, filename)

        if os.path.exists(filepath):
            print(BColors.WARNING, f"De opgegeven bestandsnaam bestaat al. "
                                   f"Kies een andere naam. "
                                   f"Je gaf het volgden op:\n"
                                   f" {filepath}", BColors.ENDC)
            continue

        filename_is_valid = True

    app_settings.geopackage_filename = filename

    create_geopackage_file(app_settings)


def create_geopackage_file(app_settings: ApplicationSettings):

    df = DataFrame({
        "metadata_type": ["created_by", "created_datetime", "application_version", "python_version", "pip_freeze"],
        "values": [
            os.getenv("USERNAME"),
            datetime.now(),
            get_geoprob_pipe_version_number(),
            f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            {dist.metadata["Name"]: dist.version for dist in distributions()},
        ]
    })

    gdf = GeoDataFrame(df, geometry=None)

    gdf.to_file(Path(app_settings.geopackage_filepath), layer="geoprob_pipe_metadata", driver="GPKG")
    print(BColors.OKBLUE, f"✅  Project-bestand aangemaakt op locatie:\n {app_settings.geopackage_filepath}", BColors.ENDC)
