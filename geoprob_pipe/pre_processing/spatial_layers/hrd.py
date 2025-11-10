from __future__ import annotations
from InquirerPy import inquirer
from pathlib import Path
from typing import TYPE_CHECKING
from geopandas import GeoDataFrame
from shapely import Point
import os
import sqlite3
from geoprob_pipe.utils.validation_messages import BColors
import fiona
import warnings
import time
import pydra_core as pydra
from pandas import DataFrame, concat
from typing import List
if TYPE_CHECKING:
    from geoprob_pipe.pre_processing.cmd import ApplicationSettings


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
        check_hrd_frag_lines_added_to_geopackage(app_settings=app_settings)
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

    check_hrd_frag_lines_added_to_geopackage(app_settings=app_settings)


def check_hrd_frag_lines_added_to_geopackage(app_settings: ApplicationSettings):

    conn = sqlite3.connect(app_settings.geopackage_filepath)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables_names = [row[0] for row in cursor.fetchall()]
    conn.close()

    # If already exist
    if "fragility_values_invoer_hrd" in tables_names:
        print(BColors.OKBLUE, f"✔  HRD-fragility lines al uitgelezen.", BColors.ENDC)
        return

    # Check if already added
    # layers = fiona.listlayers(app_settings.geopackage_filepath)
    # if "fragility_values_invoer_hrd" in layers:
    #     print(BColors.OKBLUE, f"✔  HRD-fragility lines al uitgelezen.", BColors.ENDC)
    #     return

    # Add frag lines to geopackage
    print(f"{BColors.UNDERLINE}HRD-fragility lines worden nu toegevoegd aan de GeoProb-Pipe GeoPackage.{BColors.ENDC}")
    hrd = pydra.HRDatabase(hrd_file_path(app_settings=app_settings))
    location_names = hrd.get_location_names()
    fl = pydra.ExceedanceFrequencyLine("h")
    dfs: List[DataFrame] = []
    start_time = time.time()
    last_report = start_time

    for index, location_name in enumerate(location_names):

        # Status report
        if time.time() - last_report >= 10:
            print(f"Bezig met locatie {index+1} ({location_name}) van in totaal {location_names.__len__()} locaties.")
            last_report = time.time()

        # TODO:
        #  - Dit proces kan vrij lang duren. Daarom is het beter om per locatie de fragility values in de GeoPackage
        #    te zetten. Dan kan de gebruiker tussentijds afsluiten en later vanaf hetzelfde moment weer oppakken,
        #    indien gewenst.
        #  - Nice to have: In status bericht tijdsindicatie geven wanneer klaar.

        # Continue collecting fragility values
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter(action='ignore', category=FutureWarning)
            location = hrd.get_location(location_name)
        frequency_line = fl.calculate(location)
        dfs.append(DataFrame({
            "fragility_values_ref": [location_name] * frequency_line.level.__len__(),
            "waarde": frequency_line.level,
            "kans": frequency_line.exceedance_frequency}))
    df = concat(dfs, ignore_index=True)
    conn = sqlite3.connect(app_settings.geopackage_filepath)
    df.to_sql("fragility_values_invoer_hrd", conn, if_exists="replace", index=False)
    conn.close()

    print(BColors.OKBLUE, f"✅  HRD-fragility lines toegevoegd aan GeoProb-Pipe GeoPackage.", BColors.ENDC)
