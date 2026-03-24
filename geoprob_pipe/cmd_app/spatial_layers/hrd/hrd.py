from __future__ import annotations
from InquirerPy import inquirer
from typing import TYPE_CHECKING
from geoprob_pipe.utils.validation_messages import BColors
from geoprob_pipe.cmd_app.spatial_layers.hrd.import_from_hrd import import_from_hrd
from geoprob_pipe.cmd_app.spatial_layers.hrd.import_from_other_geopackage import import_from_other_geopackage
import fiona
import sqlite3
if TYPE_CHECKING:
    from geoprob_pipe.cmd_app.cmd import ApplicationSettings


# def added_hrd(app_settings: ApplicationSettings) -> bool:
#     hrd_files_are_provided: bool = folder_contains_hrd_db(app_settings=app_settings)
#     if hrd_files_are_provided:
#         print(BColors.OKBLUE, f"✔  HRD-bestanden al toegevoegd.", BColors.ENDC)
#         check_hrd_locations_added_to_geopackage(app_settings=app_settings)
#         return True
#
#     # Verzoek toe te voegen
#     choices_list = ["Ik heb ze nu toegevoegd", "Applicatie afsluiten"]
#     choice = inquirer.select(
#         message=f"Voeg s.v.p. de bestanden van de hydraulische database toe aan de onderstaande map. Het gaat om alle "
#                 f"drie SQLite-bestanden, inclusief hlcd.sqlite.\n"
#                 f"{app_settings.hrd_dir}",
#         choices=choices_list,
#         default=choices_list[0],
#     ).execute()
#
#     if choice == choices_list[0]:
#
#         while folder_contains_hrd_db(app_settings=app_settings) is not True:
#
#             inquirer.select(
#                 message=f"De HRD-bestanden zijn nog niet gevonden in de map. Voeg ze s.v.p. toe.",
#                 choices=choices_list,
#                 default=choices_list[0],
#             ).execute()
#         print(BColors.OKBLUE, f"✅  HRD-bestanden toegevoegd.", BColors.ENDC)
#         check_hrd_locations_added_to_geopackage(app_settings=app_settings)
#         return True
#
#     elif choice == choices_list[1]:
#         return False
#     else:
#         raise ValueError


# def check_hrd_locations_added_to_geopackage(app_settings: ApplicationSettings):
#
#     # Check if already added
#     layers = fiona.listlayers(app_settings.geopackage_filepath)
#     if "hrd_locaties" in layers:
#         print(BColors.OKBLUE, f"✔  HRD-locatie punten al uitgelezen.", BColors.ENDC)
#         check_hrd_frag_lines_added_to_geopackage(app_settings=app_settings)
#         return
#
#     # Add HRD locations to GeoPackage
#     hrd_path = app_settings.hrd_file_path
#     hrd = pydra.HRDatabase(hrd_path)
#     location_names = hrd.locationnames
#     hrd_location_rows = []
#     for location_name in location_names:
#         with warnings.catch_warnings():
#             warnings.filterwarnings("ignore", category=FutureWarning)
#             try:
#                 hrd_location = hrd.get_location(location_name)
#             except NotImplementedError as e:
#                 print(f"{BColors.WARNING}Failed adding Hydra-NL location '{location_name}'. "
#                       f"Code continues without adding location. "
#                       f"Using fragility curve for this location is not possible. "
#                       f"Error is: {e}{BColors.ENDC}")
#                 continue
#         hrd_location_rows.append({
#             "location_name": location_name,
#             "geometry": Point(hrd_location.settings.x_coordinate, hrd_location.settings.y_coordinate)
#         })
#
#     # Anticipate no locations added
#     # if hrd_location_rows.__len__() == 0:
#     #     return
#
#     gdf = GeoDataFrame(hrd_location_rows, columns=['location_name', 'geometry'], crs='EPSG:28992')
#     gdf.to_file(Path(app_settings.geopackage_filepath), layer="hrd_locaties", driver="GPKG")
#     print(BColors.OKBLUE, f"✅  HRD-locatie punten toegevoegd aan GeoProb-Pipe GeoPackage.", BColors.ENDC)
#
#     check_hrd_frag_lines_added_to_geopackage(app_settings=app_settings)


# def check_hrd_frag_lines_added_to_geopackage(app_settings: ApplicationSettings):
#
#     conn = sqlite3.connect(app_settings.geopackage_filepath)
#     cursor = conn.cursor()
#     cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
#     tables_names = [row[0] for row in cursor.fetchall()]
#     conn.close()
#
#     # If already exist
#     if "fragility_values_invoer_hrd" in tables_names:
#         print(BColors.OKBLUE, f"✔  HRD-fragility lines al uitgelezen.", BColors.ENDC)
#         return
#
#     # Add frag lines to geopackage
#     print(f"{BColors.UNDERLINE}HRD-fragility lines worden nu toegevoegd aan de GeoProb-Pipe GeoPackage.{BColors.ENDC}")
#     hrd = pydra.HRDatabase(app_settings.hrd_file_path)
#     gdf_locations: GeoDataFrame = read_file(app_settings.geopackage_filepath, layer="hrd_locaties")
#     location_names = gdf_locations['location_name'].unique().tolist()
#     # location_names = hrd.get_location_names()
#     fl = pydra.ExceedanceFrequencyLine("h")
#     dfs: List[DataFrame] = []
#     start_time = time.time()
#     last_report = start_time
#
#     for index, location_name in enumerate(location_names):
#
#         # Status report
#         if time.time() - last_report >= 10.0:
#             print(f"Bezig met locatie {index+1} ({location_name}) van in totaal {location_names.__len__()} locaties.")
#             last_report = time.time()
#
#         # TODO:
#         #  - Dit proces kan vrij lang duren. Daarom is het beter om per locatie de fragility values in de GeoPackage
#         #    te zetten. Dan kan de gebruiker tussentijds afsluiten en later vanaf hetzelfde moment weer oppakken,
#         #    indien gewenst.
#         #  - Nice to have: In status bericht tijdsindicatie geven wanneer klaar.
#
#         # Continue collecting fragility values
#         import warnings
#         with warnings.catch_warnings():
#             warnings.simplefilter(action='ignore', category=FutureWarning)
#             location = hrd.get_location(location_name)
#         frequency_line = fl.calculate(location)
#         df_to_append = DataFrame({
#             "fragility_values_ref": [location_name] * frequency_line.level.__len__(),
#             "waarde": frequency_line.level,
#             "kans": frequency_line.exceedance_frequency,
#             "beta": -sct.norm.ppf(frequency_line.exceedance_frequency)
#         })
#         df_to_append = df_to_append[df_to_append["kans"] < 1.0]
#         df_to_append = df_to_append[df_to_append["beta"] < 8.0]
#         df_to_append = df_to_append.drop(columns=["beta"])
#         dfs.append(df_to_append)
#
#     # Combine data and push
#     df = DataFrame(data=[], columns=["fragility_values_ref", "waarde", "kans"])
#     if dfs.__len__() > 0:
#         df = concat(dfs, ignore_index=True)
#     conn = sqlite3.connect(app_settings.geopackage_filepath)
#     df.to_sql("fragility_values_invoer_hrd", conn, if_exists="replace", index=False)
#     conn.close()
#
#     print(BColors.OKBLUE, f"✅  HRD-fragility lines toegevoegd aan GeoProb-Pipe GeoPackage.", BColors.ENDC)


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
        message=f"Wil je HRD-data importeren? Dit is optioneel. Je kunt ook handmatig "
                f"overschrijdingsfrequentielijnen toevoegen, of werken met deterministische buitenwaterstanden.",
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
    choices_list = ["Hydra-NL database", "Ander GeoProb-Pipe bestand"]
    choice = inquirer.select(
        message=f"Welke bron wil je gebruiken voor de Hydra-NL data?",
        choices=choices_list, default=choices_list[0]).execute()
    if choice == choices_list[0]:
        return "from_hrd"
    return "from_other_geopackage"


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
