from __future__ import annotations
from InquirerPy import inquirer
from pathlib import Path
from typing import TYPE_CHECKING
import scipy.stats as sct
from geopandas import GeoDataFrame, read_file
from shapely import Point
import os
from geoprob_pipe.utils.validation_messages import BColors
import warnings
from geoprob_pipe.cmd_app.spatial_layers.hrd.utils import hrd_file_path
import importlib.resources
import time
import pydra_core as pydra
from pandas import DataFrame, concat
from typing import Optional, List, Tuple
import sqlite3
if TYPE_CHECKING:
    from geoprob_pipe.cmd_app.cmd import ApplicationSettings


def _folder_contains_hrd_db(hrd_dir: str) -> bool:
    cnt_sql_files = 0
    cnt_config_files = 0
    cnt_hlcd_files = 0


    for file in os.listdir(hrd_dir):
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


def _ask_path_to_hrd_dir() -> str:
    filepath: Optional[str] = None
    filepath_is_valid = False
    while filepath_is_valid is False:
        filepath: str = inquirer.text(
            message="Specificeer het volledige pad naar de bestandsmap met de Hydra-NL database. "
                    "Dat zijn de hlcd, config en het database .sqlite-bestand zelf.",
        ).execute()

        filepath = filepath.replace('"', '')

        if not os.path.isdir(filepath):
            print(BColors.WARNING, f"Het bestandspad moet een directory zijn. Probeer het opnieuw.", BColors.ENDC)
            continue

        if not _folder_contains_hrd_db(hrd_dir=filepath):
            print(BColors.WARNING, f"De opgegeven bestandsmap bevat geen of niet alle bestanden van de Hydra-NL "
                                   f"database. Zorg er voor dat het hlcd-, config.sqlite- en het .sqlite "
                                   f"database-bestand allen in de map staan. ", BColors.ENDC)
            continue

        filepath_is_valid = True

    return filepath


def _add_hrd_locations_to_database(app_settings: ApplicationSettings, hrd_dir: str):

    # Add HRD locations to GeoPackage
    print(f"{hrd_dir=}")
    hrd_path = hrd_file_path(hrd_dir=hrd_dir)
    print(f"{hrd_path=}")
    hrd = pydra.HRDatabase(hrd_path)
    location_names = hrd.locationnames
    hrd_location_rows = []
    for location_name in location_names:
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=FutureWarning)
            try:
                hrd_location = hrd.get_location(location_name)
            except NotImplementedError as e:
                print(f"{BColors.WARNING}Failed adding Hydra-NL location '{location_name}'. "
                      f"Code continues without adding location. "
                      f"Using fragility curve for this location is not possible. "
                      f"Error is: {e}{BColors.ENDC}")
                continue
        hrd_location_rows.append({
            "location_name": location_name,
            "geometry": Point(hrd_location.settings.x_coordinate, hrd_location.settings.y_coordinate)
        })

    gdf = GeoDataFrame(hrd_location_rows, columns=['location_name', 'geometry'], crs='EPSG:28992')
    gdf.to_file(Path(app_settings.geopackage_filepath), layer="hrd_locaties", driver="GPKG")
    print(BColors.OKBLUE, f"✅  HRD-locatie punten toegevoegd aan GeoProb-Pipe GeoPackage.", BColors.ENDC)


def _add_hrd_overschrijdingsfrequentielijnen(hrd_dir: str, app_settings: ApplicationSettings):
    print(f"{BColors.UNDERLINE}HRD-overschrijdingsfrequentielijnen worden nu toegevoegd aan de GeoProb-Pipe "
          f"GeoPackage.{BColors.ENDC}")

    hrd = pydra.HRDatabase(hrd_file_path(hrd_dir=hrd_dir))
    gdf_locations: GeoDataFrame = read_file(app_settings.geopackage_filepath, layer="hrd_locaties")
    location_names = gdf_locations['location_name'].unique().tolist()
    fl = pydra.ExceedanceFrequencyLine("h")
    dfs: List[DataFrame] = []
    start_time = time.time()
    last_report = start_time

    for index, location_name in enumerate(location_names):

        # Status report
        if time.time() - last_report >= 10.0:
            print(f"Bezig met locatie {index+1} ({location_name}) van in totaal {location_names.__len__()} locaties.")
            last_report = time.time()

        # Continue collecting fragility values
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter(action='ignore', category=FutureWarning)
            location = hrd.get_location(location_name)
        frequency_line = fl.calculate(location)
        df_to_append = DataFrame({
            "fragility_values_ref": [location_name] * frequency_line.level.__len__(),
            "waarde": frequency_line.level,
            "kans": frequency_line.exceedance_frequency,
            "beta": -sct.norm.ppf(frequency_line.exceedance_frequency)
        })
        df_to_append = df_to_append[df_to_append["kans"] < 1.0]
        df_to_append = df_to_append[df_to_append["beta"] < 8.0]
        df_to_append = df_to_append.drop(columns=["beta"])
        dfs.append(df_to_append)

    # Combine data and push
    df = DataFrame(data=[], columns=["fragility_values_ref", "waarde", "kans"])
    if dfs.__len__() > 0:
        df = concat(dfs, ignore_index=True)
    conn = sqlite3.connect(app_settings.geopackage_filepath)
    df.to_sql("fragility_values_invoer_hrd", conn, if_exists="replace", index=False)
    conn.close()

    print(BColors.OKBLUE, f"✅  HRD-overschrijdingsfrequentielijnen toegevoegd aan GeoProb-Pipe "
                          f"GeoPackage.", BColors.ENDC)


def _get_traject_id(hrd_dir: str) -> Tuple[int, str]:
    """ Queries first the HRD for the integer ID of the traject.
    Then queries the HLCD to find the textual traject ID.
    """
    print(f"_get_traject_id")
    conn = sqlite3.connect(hrd_file_path(hrd_dir=hrd_dir))
    cursor = conn.cursor()
    query = "SELECT TrackID FROM General;"
    cursor.execute(query)
    track_id = cursor.fetchone()[0]
    print(f"{track_id=}")
    conn.close()

    conn = sqlite3.connect(_hlcd_file_path(hrd_dir=hrd_dir))
    cursor = conn.cursor()
    query = f"SELECT Name FROM Tracks WHERE TrackID={track_id};"
    cursor.execute(query)
    traject_id = cursor.fetchone()[0]
    print(f"{traject_id=}")
    conn.close()

    return track_id, traject_id


def _hlcd_file_path(hrd_dir: str):
    return os.path.join(os.path.dirname(hrd_file_path(hrd_dir=hrd_dir)), "hlcd.sqlite")


def _query_dijktrajecten(traject_id: str) -> Tuple[int, int]:
    """ Queries the dijktrajecten.shp that was retrieved from the API of
    the Waterveiligheidsportaal [1].

    [1] https://www.nationaalgeoregister.nl/geonetwork/srv/dut/catalog.search#/metadata/fa4cc54e-26b3-4f25-b643-59458622901c
    """
    with importlib.resources.path(
            package='geoprob_pipe.input_data.dijktrajecten', resource='dijktrajecten.shp') as shp_path:
        gdf: GeoDataFrame = read_file(shp_path)
    gdf = gdf[gdf['TRAJECT_ID'] == traject_id]
    assert gdf.__len__() == 1, "Only one traject id should have been found. Address this issue."
    return gdf.iloc[0]['NORM_SW'], gdf.iloc[0]['NORM_OG']


def _ask_is_bovenrivierengebied() -> bool:
    choices_list = ["Ja", "Nee"]
    choice = inquirer.select(
        message=f"Is dit traject in het bovenrivierengebied?", choices=choices_list, default=choices_list[0]).execute()
    if choice == "Ja":
        return True
    return False


def _add_traject_parameters(app_settings: ApplicationSettings, hrd_dir: str):

    # Gather data
    traject_id = _get_traject_id(hrd_dir=hrd_dir)[1].strip()
    print(f"{traject_id=}")
    signaleringswaarde, ondergrens = _query_dijktrajecten(traject_id=traject_id)
    w: float = 0.24  # Assumed to be always 24% in case of HRD database
    is_bovenrivierengebied: bool = _ask_is_bovenrivierengebied()

    # Store data
    file_path = app_settings.geopackage_filepath
    conn = sqlite3.connect(file_path)
    cursor = conn.cursor()
    cursor.execute(
        f"INSERT INTO geoprob_pipe_metadata (metadata_type, 'values') VALUES ('traject_id', '{traject_id}');")
    cursor.execute(
        f"INSERT INTO geoprob_pipe_metadata (metadata_type, 'values') "
        f"VALUES ('signaleringswaarde', {signaleringswaarde});")
    cursor.execute(
        f"INSERT INTO geoprob_pipe_metadata (metadata_type, 'values') VALUES ('ondergrens', {ondergrens});")
    cursor.execute(f"INSERT INTO geoprob_pipe_metadata (metadata_type, 'values') VALUES ('w', {w});")
    cursor.execute(f"INSERT INTO geoprob_pipe_metadata (metadata_type, 'values') "
                   f"VALUES ('is_bovenrivierengebied', {is_bovenrivierengebied});")
    conn.commit()
    cursor.close()

    print(BColors.OKBLUE, f"✅  Traject-parameters toegevoegd aan GeoPackage.", BColors.ENDC)


def import_from_hrd(app_settings: ApplicationSettings):
    hrd_dir = _ask_path_to_hrd_dir()
    _add_hrd_locations_to_database(app_settings=app_settings, hrd_dir=hrd_dir)
    _add_hrd_overschrijdingsfrequentielijnen(hrd_dir=hrd_dir, app_settings=app_settings)
    _add_traject_parameters(app_settings=app_settings, hrd_dir=hrd_dir)

