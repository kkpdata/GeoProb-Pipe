from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import TYPE_CHECKING

from geopandas import GeoDataFrame, read_file
from InquirerPy.prompts.input import InputPrompt
from pandas import DataFrame, read_sql_query

from geoprob_pipe.utils.validation_messages import BColors

if TYPE_CHECKING:
    from geoprob_pipe.cmd_app.cmd import ApplicationSettings


def _ask_for_other_geopackage_file_path() -> str:

    while True:
        filepath: str = InputPrompt(
            message="Specificeer het volledige bestandspad naar het .geoprob_pipe.gpkg-bestand.",
        ).execute()

        filepath = filepath.replace('"', '')

        if not filepath.endswith(".geoprob_pipe.gpkg"):
            print(BColors.WARNING, f"Het bestand moet een .geoprob_pipe.gpkg-bestand zijn. Jouw invoer "
                                   f"{os.path.basename(filepath)} eindigt niet op deze extensie.", BColors.ENDC)
            continue
        
        if not os.path.exists(filepath):
            print(BColors.WARNING, "Het opgegeven bestandspad bestaat niet.", BColors.ENDC)
            continue

        break

    return filepath


def _add_hrd_locations_to_database(other_gpkg_path: str, app_settings: ApplicationSettings):
    gdf_locations: GeoDataFrame = read_file(other_gpkg_path, layer="geom__hrd_locaties")
    gdf_locations.to_file(Path(app_settings.geopackage_filepath), layer="geom__hrd_locaties", driver="GPKG")
    print(BColors.OKBLUE, "✅  HRD-locatie punten toegevoegd aan GeoProb-Pipe GeoPackage.", BColors.ENDC)


def _add_hrd_overschrijdingsfrequentielijnen(other_gpkg_path: str, app_settings: ApplicationSettings):
    conn = sqlite3.connect(other_gpkg_path)
    df: DataFrame = read_sql_query("SELECT * FROM data__fragility_values_invoer_hrd;", conn)
    conn.close()

    conn = sqlite3.connect(app_settings.geopackage_filepath)
    df.to_sql("data__fragility_values_invoer_hrd", conn, if_exists="replace", index=False)
    conn.close()

    print(BColors.OKBLUE, "✅  HRD-overschrijdingsfrequentielijnen toegevoegd aan GeoProb-Pipe "
                          "GeoPackage.", BColors.ENDC)


def _add_traject_parameters(other_gpkg_path: str, app_settings: ApplicationSettings):
    conn = sqlite3.connect(other_gpkg_path)
    df: DataFrame = read_sql_query("SELECT * FROM geoprob_pipe_metadata;", conn)
    conn.close()

    traject_id = df[df["metadata_type"] == "traject_id"]["metadata_value"].values[0]
    signaleringswaarde = int(df[df["metadata_type"] == "signaleringswaarde"]["metadata_value"].values[0])
    ondergrens = int(df[df["metadata_type"] == "ondergrens"]["metadata_value"].values[0])
    w = float(df[df["metadata_type"] == "w"]["metadata_value"].values[0])
    is_bovenrivierengebied = bool(int(df[df["metadata_type"] == "is_bovenrivierengebied"]["metadata_value"].values[0]))

    conn = sqlite3.connect(app_settings.geopackage_filepath)
    cursor = conn.cursor()
    cursor.execute(
        f"INSERT INTO geoprob_pipe_metadata (metadata_type, metadata_value) VALUES ('traject_id', '{traject_id}');")
    cursor.execute(
        f"INSERT INTO geoprob_pipe_metadata (metadata_type, metadata_value) "
        f"VALUES ('signaleringswaarde', {signaleringswaarde});")
    cursor.execute(
        f"INSERT INTO geoprob_pipe_metadata (metadata_type, metadata_value) VALUES ('ondergrens', {ondergrens});")
    cursor.execute(f"INSERT INTO geoprob_pipe_metadata (metadata_type, metadata_value) VALUES ('w', {w});")
    cursor.execute(f"INSERT INTO geoprob_pipe_metadata (metadata_type, metadata_value) "
                   f"VALUES ('is_bovenrivierengebied', {is_bovenrivierengebied});")
    conn.commit()
    cursor.close()

    print(BColors.OKBLUE, "✅  Traject-parameters toegevoegd aan GeoPackage.", BColors.ENDC)


def import_from_other_geopackage(app_settings: ApplicationSettings):
    other_geopackage_file_path: str = _ask_for_other_geopackage_file_path()
    _add_hrd_locations_to_database(other_gpkg_path=other_geopackage_file_path, app_settings=app_settings)
    _add_hrd_overschrijdingsfrequentielijnen(other_gpkg_path=other_geopackage_file_path, app_settings=app_settings)
    _add_traject_parameters(other_gpkg_path=other_geopackage_file_path, app_settings=app_settings)
