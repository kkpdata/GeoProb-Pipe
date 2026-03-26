from __future__ import annotations
from InquirerPy import inquirer
from typing import TYPE_CHECKING
from rich.console import Console
from rich.panel import Panel
from geoprob_pipe.utils import clear_terminal
import os
from pandas import DataFrame
from datetime import datetime
from pathlib import Path
import sys
from importlib.metadata import distributions
from geopandas import GeoDataFrame
from geoprob_pipe.cmd_app.utils.misc import get_geoprob_pipe_version_number
from geoprob_pipe.cmd_app.comparisons.start_comparison import start_comparison
from geoprob_pipe.calculations.systems.single_calc import (
    EXAMPLE_SCRIPT_REPRODUCING_SINGLE_CALCULATION, EXPLANATION_REPRODUCING_SINGLE_CALCULATION)
import logging
from packaging.version import Version
from geoprob_pipe.utils.validation_messages import BColors
import sqlite3
from typing import Optional
import ast
from geoprob_pipe.utils.loggers import enable_geopackage_logging
if TYPE_CHECKING:
    from geoprob_pipe.cmd_app.cmd import ApplicationSettings



logger = logging.getLogger("geoprob-pipe")


def created_project(app_settings: ApplicationSettings) -> bool:

    choices_list = [
        "Bestaand project openen",
        "Nieuw project starten",
        "Twee projectbestanden vergelijken",
        "Inspecteer een enkele berekening",
        "Applicatie afsluiten"]
    choice = inquirer.select(
        message="Wil je verder gaan met een bestaand project, "
                "een nieuw project starten, "
                "of twee project bestanden vergelijken?",
        choices=choices_list,
        default=choices_list[0],
    ).execute()

    if choice == choices_list[0]:
        specify_path_to_existing_project(app_settings)
        enable_geopackage_logging(app_settings=app_settings)
        return True

    elif choice == choices_list[1]:
        specify_dir_for_new_project(app_settings)
        enable_geopackage_logging(app_settings=app_settings)
        return True

    elif choice == choices_list[2]:
        start_comparison()
        sys.exit("Applicatie afgesloten")

    elif choice == choices_list[3]:
        clear_terminal()
        console = Console()
        console.print(Panel(
            EXPLANATION_REPRODUCING_SINGLE_CALCULATION,
            title=f"Inspecteer een enkele berekening".upper(),
            title_align="left",
            border_style="bright_blue",
            padding=(0, 2)))
        print(EXAMPLE_SCRIPT_REPRODUCING_SINGLE_CALCULATION)
        sys.exit("Applicatie afgesloten")

    return False


def _get_file_geoprob_pipe_version(file_path: str) -> Optional[str]:
    conn = sqlite3.connect(file_path)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM geoprob_pipe_metadata WHERE metadata_type = 'pip_freeze' LIMIT 1;")
    row = cursor.fetchone()
    dict_item = ast.literal_eval(row[2])

    # Check if created with development environment
    if "geoprob_pipe" not in dict_item:
        return None

    return dict_item["geoprob_pipe"]


def _compare_versions_and_possibly_warn(installed_version: str, file_version: str):

    v_installed = Version(installed_version)
    v_file = Version(file_version)

    version_diff_msg = (
        f"Er is een GeoProb-Pipe versie verschil tussen de installatie ({v_installed}) en het bestand ({v_file}).")
    reinstall_msg = (
        f"\n"
        f"Wil je de versies liever gelijk trekken? Dit doe je door eerst de applicatie af te sluiten en vervolgens het \n"
        f"commando `pip install geoprob-pipe==versie_nummer` uit te voeren. Waarbij je `versie_nummer` vervangt met het \n"
        f"nummer van de gewenste versie")

    if v_installed.major != v_file.major:
        print(f"\n{BColors.FAIL}SEVERE WARNING:\n"
              f"{version_diff_msg}\n"
              f"Dit is een versie verschil met major changes. Dit is een risico. Het kan goed zijn dat de applicatie niet "
              f"compatibel is met je bestand. \n"
              f"{reinstall_msg}"
              f"{BColors.ENDC}\n")
    elif v_installed.minor != v_file.minor:
        print(f"\n{BColors.WARNING}WARNING:\n"
              f"{version_diff_msg}\n"
              f"Dit is een versie verschil met minor changes. Dit kan mogelijk een probleem zijn tijdens het gebruik van "
              f"de applicatie. \n"
              f"{reinstall_msg}"
              f"{BColors.ENDC}\n")
    elif v_installed.micro != v_file.micro:
        print(f"\n{BColors.OKBLUE}"
              f"{version_diff_msg}\n"
              f"Dit verschil is slechts op patch-niveau. Dit is waarschijnlijk geen probleem tijdens het gebruik van "
              f"de applicatie. \n"
              f"{reinstall_msg}"
              f"{BColors.ENDC}\n")


def _possibly_warn_if_version_difference(file_path: str):

    installed_app_version = get_geoprob_pipe_version_number()
    if installed_app_version == "DEV":
        return  # We do not warn if application is run in development environment.

    file_app_version = _get_file_geoprob_pipe_version(file_path=file_path)
    if file_app_version is None:
        return  # Version was not found what probably means it was made in a development environment.

    _compare_versions_and_possibly_warn(installed_version=installed_app_version, file_version=file_app_version)


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

    _possibly_warn_if_version_difference(file_path=app_settings.geopackage_filepath)


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
