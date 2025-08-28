from __future__ import annotations
import pydra_core as pydra
import warnings
from InquirerPy import inquirer
from pathlib import Path
from typing import TYPE_CHECKING
from geopandas import GeoDataFrame
from shapely import Point
import os
from geoprob_pipe.utils.other import BColors
import fiona

if TYPE_CHECKING:
    from geoprob_pipe.cmd import ApplicationSettings


def folder_contains_hrd_db(app_settings: ApplicationSettings) -> bool:
    cnt_sql_files = 0
    cnt_config_files = 0
    cnt_hlcd_files = 0


    for file in os.listdir(app_settings.hrd_dir):
        filename = os.fsdecode(file)
        if filename.endswith(".sqlite"):
            cnt_sql_files += 1
        if filename.endswith(".config.sqlite"):
            cnt_config_files += 1
        if filename.endswith("hlcd.sqlite"):
            cnt_hlcd_files += 1

    if cnt_sql_files == 3 and cnt_config_files == 1 and cnt_hlcd_files == 1:
        return True
    return False


def hrd_file_path(app_settings: ApplicationSettings) -> str:
    for file in os.listdir(app_settings.hrd_dir):
        filename = os.fsdecode(file)
        if filename.endswith(".config.sqlite"):
            continue
        if filename.endswith("hlcd.sqlite"):
            continue
        return os.path.join(app_settings.hrd_dir, filename)
    raise ValueError


def added_hrd(app_settings: ApplicationSettings) -> bool:
    hrd_files_are_provided: bool = folder_contains_hrd_db(app_settings=app_settings)
    if hrd_files_are_provided:
        print(BColors.OKBLUE, f"✔  HRD-bestanden al toegevoegd.", BColors.ENDC)
        check_hrd_locations_added_to_geopackage(app_settings=app_settings)
        return True

    # Verzoek toe te voegen
    choices_list = ["Ik heb ze nu toegevoegd", "Applicatie afsluiten"]
    choice = inquirer.select(
        message=f"Voeg s.v.p. de bestanden van de hydraulische database toe aan de onderstaande map. Het gaat om alle "
                f"drie SQLite-bestanden, inclusief hlcd.sqlite.\n"
                f"{app_settings.hrd_dir}",
        choices=choices_list,
        default=choices_list[0],
    ).execute()

    if choice == choices_list[0]:

        while folder_contains_hrd_db(app_settings=app_settings) is not True:

            inquirer.select(
                message=f"De HRD-bestanden zijn nog niet gevonden in de map. Voeg ze s.v.p. toe.",
                choices=choices_list,
                default=choices_list[0],
            ).execute()
        print(BColors.OKBLUE, f"✅  HRD-bestanden toegevoegd.", BColors.ENDC)
        check_hrd_locations_added_to_geopackage(app_settings=app_settings)
        return True

    elif choice == choices_list[1]:
        return False
    else:
        raise ValueError


def check_hrd_locations_added_to_geopackage(app_settings: ApplicationSettings):

    # Check if already added
    layers = fiona.listlayers(app_settings.geopackage_filepath)
    if "hrd_locaties" in layers:
        print(BColors.OKBLUE, f"✔  HRD-locatie punten al uitgelezen.", BColors.ENDC)
        return

    # Add HRD locations to GeoPackage
    hrd_path = hrd_file_path(app_settings=app_settings)
    hrd = pydra.HRDatabase(hrd_path)
    location_names = hrd.locationnames
    hrd_location_rows = []
    for location_name in location_names:
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=FutureWarning)
            hrd_location = hrd.get_location(location_name)
        hrd_location_rows.append({
            "location_name": location_name,
            "geometry": Point(hrd_location.settings.x_coordinate, hrd_location.settings.y_coordinate)
        })
    gdf = GeoDataFrame(hrd_location_rows, crs='EPSG:28992')
    gdf.to_file(Path(app_settings.geopackage_filepath), layer="hrd_locaties", driver="GPKG")
    print(BColors.OKBLUE, f"✅  HRD-locatie punten toegevoegd aan GeoProb-Pipe GeoPackage.", BColors.ENDC)
