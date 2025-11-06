from __future__ import annotations
from InquirerPy import inquirer
import sqlite3

from geoprob_pipe.pre_processing.parameter_input.expand_input_tables import run_expand_input_tables
from geoprob_pipe.pre_processing.parameter_input.initiate_input_excel_tables import initiate_input_excel_tables
from geoprob_pipe.pre_processing.parameter_input.input_parameter_figures import InputParameterFigures
from geoprob_pipe.pre_processing.parameter_input.export_input_parameter_excel import export_input_parameter_tables
from geoprob_pipe.pre_processing.parameter_input.input_parameter_tables import InputParameterTables
from typing import TYPE_CHECKING, Optional
import os
import sys
from geoprob_pipe.utils.loggers import BColors
if TYPE_CHECKING:
    from geoprob_pipe.pre_processing.cmd import ApplicationSettings


# class ProcessInputParameterTables:
#
#     def __init__(self, app_settings: ApplicationSettings):
#         self.app_settings: ApplicationSettings = app_settings
#         self._check_if_input_tables_exist()


# def _check_if_input_tables_exist(app_settings: ApplicationSettings):
#
#     # Get table names
#     conn = sqlite3.connect(app_settings.geopackage_filepath)
#     cursor = conn.cursor()
#     cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
#     tables_names = [row[0] for row in cursor.fetchall()]
#     conn.close()
#
#     # If already exist
#     if ("parameter_invoer" in tables_names and
#             "scenario_invoer" in tables_names and "fragility_values_invoer" in tables_names):
#         print(f"{BColors.UNDERLINE}Tables exist in geopackage{BColors.ENDC}")
#     else:
#         # If it doesn't exist yet
#         print(f"{BColors.UNDERLINE}Tables do not exist in geopackage{BColors.ENDC}")
#         _initiate_input_excel_tables(app_settings=app_settings)
#         print(f"{BColors.UNDERLINE}Tables exist in geopackage{BColors.ENDC}")
#
#     # Load tables into class
#     tables = InputParameterTables(app_settings=app_settings)
#     _validate_input_excel_tables(
#         app_settings=app_settings,
#         tables=tables,
#         tables_exist_in_geopackage=True,  # They either exist, or are initiated, thus always True in this function.
#     )


# def _validate_input_excel_tables(
#         app_settings: ApplicationSettings, tables: InputParameterTables, tables_exist_in_geopackage: bool):
#     valid: bool = True  # TODO
#     if not valid:
#         print(f"Input Excel tables are not valid. Validation messages are exported to \n"
#               f"TODO")  # TODO: Specify path to exported validation messages.
#         _import_export_continue_or_store(
#             app_settings=app_settings, tables=tables, tables_exist_in_geopackage=tables_exist_in_geopackage)
#         # -> Directly to this, because other steps can't be performed on invalid data
#
#     print(f"{BColors.UNDERLINE}Validation of tables executed{BColors.ENDC}")
#     _inquire_to_export_input_parameter_figures(app_settings=app_settings, tables=tables)


# def _initiate_input_excel_tables(app_settings: ApplicationSettings):
#     initiate_input_excel_tables(app_settings=app_settings)
#     print(f"{BColors.UNDERLINE}Tables initiated in geopackage{BColors.ENDC}")


# def _inquire_to_export_input_parameter_figures(app_settings: ApplicationSettings, tables: InputParameterTables):
#     choices_list = [
#         "Ja",
#         "Nee",
#         "Applicatie afsluiten"
#     ]
#     choice = inquirer.select(
#         message="Wil je overzichtsfiguren exporteren van de invoer tabellen? \n"
#                 "Hierin kun je gemakkelijk zien voor welke parameter welke invoer is ingesteld, en op welk niveau "
#                 "(geografisch-, traject-, vak-, of uittredepunt-niveau).",
#         choices=choices_list,
#         default=choices_list[0],
#     ).execute()
#
#     if choice == choices_list[0]:
#         _export_parameter_input_figures(app_settings=app_settings, tables=tables)
#     elif choice == choices_list[1]:
#         pass  # Just continue
#     elif choice == choices_list[2]:
#         sys.exit(f"Applicatie is afgesloten.")
#     else:
#         raise ValueError
#
#     # Continue to next step: validation
#     _validate_expanded_parameter_input(app_settings=app_settings, tables=tables)


# def _export_parameter_input_figures(app_settings: ApplicationSettings, tables: InputParameterTables):
#     InputParameterFigures(app_settings=app_settings, tables=tables, export=True)
#     print(f"{BColors.UNDERLINE}Parameter figures exported{BColors.ENDC}")


# def _validate_expanded_parameter_input(
#         app_settings: ApplicationSettings, tables: InputParameterTables, tables_exist_in_geopackage: bool):
#     valid: bool = True  # TODO
#     if not valid:
#         print(f"Input Excel tables are not valid. Validation messages are exported to \n"
#               f"TODO")  # TODO: Specify path to exported validation messages.
#
#     print(f"{BColors.UNDERLINE}Expanded validation executed{BColors.ENDC}")
#     _import_export_continue_or_store(
#         app_settings=app_settings, tables=tables, tables_exist_in_geopackage=tables_exist_in_geopackage)


# def _import_export_continue_or_store(
#         app_settings: ApplicationSettings, tables: InputParameterTables, tables_exist_in_geopackage: bool):
#     if tables_exist_in_geopackage:
#         choices_list = [
#             "Invoer tabellen importeren (vanuit Excel)", "Invoer tabellen exporteren (naar Excel)",
#             "Applicatie afsluiten"]
#         choice = inquirer.select(
#             message="Wil je de tabellen exporteren (vanuit de GeoPackage)? Of een nieuwe versie importeren?\n"
#                     "Na exporteren kun je het naar smaak aanpassen en weer importeren.",
#             choices=choices_list,
#             default=choices_list[0],
#         ).execute()
#         if choice == choices_list[0]:
#             _import_excel()
#         elif choice == choices_list[1]:
#             export_input_parameter_tables(app_settings=app_settings, tables=tables)
#             _import_export_continue_or_store(
#                 app_settings=app_settings, tables=tables, tables_exist_in_geopackage=tables_exist_in_geopackage)
#             # -> In case of export, just re-ask to export/import
#         elif choice == choices_list[2]:
#             sys.exit(f"Applicatie is afgesloten.")
#         else:
#             raise ValueError
#
#     else:
#         # Ask if tables should be saved
#         choices_list = ["Ja", "Nee", "Applicatie afsluiten"]
#         choice = inquirer.select(
#             message="Je hebt deze tabellen nieuw geïmporteerd. Wil je ze opslaan in de GeoPackage? "
#                     "Dit overschrijft de bestaande versie.",
#             choices=choices_list,
#             default=choices_list[0],
#         ).execute()
#
#         if choice == choices_list[0]:
#             _store_new_tables(tables=tables)
#         elif choice == choices_list[1]:
#             sys.exit(f"Gekozen voor 'Nee'. Applicatie is afgesloten.")
#         elif choice == choices_list[2]:
#             sys.exit(f"Applicatie is afgesloten.")
#         else:
#             raise ValueError


# def _import_excel():
#     pass  # TODO


# def _store_new_tables(tables: InputParameterTables):
#     pass  # TODO


def possibly_initiatie_input_tables_in_db(app_settings: ApplicationSettings):

    # Get table names
    conn = sqlite3.connect(app_settings.geopackage_filepath)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables_names = [row[0] for row in cursor.fetchall()]
    conn.close()

    # If already exist
    if ("parameter_invoer" in tables_names and
            "scenario_invoer" in tables_names and "fragility_values_invoer" in tables_names):
        # print(f"{BColors.UNDERLINE}Tables already exist in geopackage{BColors.ENDC}")
        return

    # If it doesn't exist yet
    # print(f"{BColors.UNDERLINE}Tables do not yet exist in geopackage{BColors.ENDC}")
    initiate_input_excel_tables(app_settings=app_settings)
    print(f"{BColors.UNDERLINE}Basis invoer tabellen zijn nu geïnitieerd in het GeoProb-Pipe-bestand. Deze kun je naar "
          f"wens aanpassen in het vervolgproces.{BColors.ENDC}")


def load_tables_from_db(app_settings: ApplicationSettings) -> InputParameterTables:
    tables = InputParameterTables(geopackage_filepath=app_settings.geopackage_filepath)
    return tables


def validate_raw_input_tables(
        # app_settings: ApplicationSettings, tables: InputParameterTables
) -> bool:
    valid: bool = True  # TODO
    if not valid:
        print(f"Input Excel tables are not valid. Validation messages are exported to \n"
              f"TODO")  # TODO: Specify path to exported validation messages.
    return valid


def inquire_if_input_figures_should_be_exported(app_settings: ApplicationSettings, tables: InputParameterTables):
    choices_list = [
        "Ja",
        "Nee",
        "Applicatie afsluiten"
    ]
    choice = inquirer.select(
        message="Wil je overzichtsfiguren exporteren van de invoer tabellen? \n"
                "Hierin kun je gemakkelijk zien voor welke parameter welke invoer is ingesteld, en op welk niveau "
                "(geografisch-, traject-, vak-, of uittredepunt-niveau).",
        choices=choices_list,
        default=choices_list[0],
    ).execute()

    if choice == choices_list[0]:
        InputParameterFigures(app_settings=app_settings, tables=tables, export=True)
    elif choice == choices_list[1]:
        pass  # Just continue
    elif choice == choices_list[2]:
        sys.exit(f"Applicatie is afgesloten.")
    else:
        raise ValueError


# def expand_input_tables() -> float:
#     return 1.0  # TODO


def validate_expanded_input_tables(geopackage_filepath: str) -> bool:
    df_expanded = run_expand_input_tables(geopackage_filepath=geopackage_filepath)
    df_nans = df_expanded[df_expanded['parameter_input'].isna()]

    # No issues?
    if df_nans.__len__() == 0:
        return True

    # Report issues back
    export_dir = os.path.join(os.path.dirname(geopackage_filepath), "parameter_input_process")
    os.makedirs(export_dir, exist_ok=True)
    export_path = os.path.join(export_dir, "validation_missing_parameter_input.xlsx")
    print(f"{export_path=}")
    if os.path.exists(export_path):
        os.remove(export_path)
    df_nans.to_excel(export_path)
    print(f"{BColors.WARNING}Er mist parameter invoer voor {df_nans.__len__()} berekeningen.\n"
          f"Dit is voor {df_nans['parameter_name'].unique().__len__()} unieke parameters, "
          f"{df_nans['uittredepunt_id'].unique().__len__()} unieke uittredepunten en "
          f"{df_nans['ondergrondscenario_naam'].unique().__len__()} unieke ondergrondscenarios.\n"
          f"De gedetailleerde lijst is geëxporteerd naar\n"
          f"{export_path}{BColors.ENDC}")
    return False


def inquire_to_import_export_tables_and_figures_or_continue(
        app_settings: ApplicationSettings, tables: InputParameterTables,
        validity_raw_tables: bool, validity_extended_tables: bool
):

    # Determine options
    choices_list = []
    if validity_raw_tables and validity_extended_tables:
        choices_list.append("Invoer tabellen zijn naar wens, ga door naar volgende stap")
    else:
        choices_list.append("Invoer tabellen zijn naar wens, ga door naar volgende stap (n.v.t. -> invoer niet valide)")
    if validity_raw_tables:
        choices_list.append("Overzichtsfiguren van invoertabellen: Exporteren")
    choices_list.extend([
        "Invoer tabellen: Importeren vanuit Excel",
        "Invoer tabellen: Exporteren naar Excel",
        "Toelichting per keuze optie",
        "Applicatie afsluiten"])

    # Provide user options
    choice = inquirer.select(
        message="Maak een keuze voor het gereedmaken van de invoertabellen.",
        choices=choices_list,
        default=choices_list[0],
    ).execute()

    if choice == "Invoer tabellen zijn naar wens, ga door naar volgende stap":
        raise NotImplementedError(f"Volgende stap nog te implementeren")

    elif choice == "Invoer tabellen zijn naar wens, ga door naar volgende stap (n.v.t. -> invoer niet valide)":
        inquire_to_import_export_tables_and_figures_or_continue(
            app_settings=app_settings, tables=tables, validity_raw_tables=validity_raw_tables,
            validity_extended_tables=validity_extended_tables)

    elif choice == "Overzichtsfiguren van invoertabellen: Exporteren":
        InputParameterFigures(app_settings=app_settings, tables=tables, export=True)
        inquire_to_import_export_tables_and_figures_or_continue(
            app_settings=app_settings, tables=tables, validity_raw_tables=validity_raw_tables,
            validity_extended_tables=validity_extended_tables)

    elif choice == "Invoer tabellen: Importeren vanuit Excel":
        process_import_input(app_settings=app_settings)

    elif choice == "Invoer tabellen: Exporteren naar Excel":
        process_export_input_of_db(
            app_settings=app_settings, tables=tables, validity_raw_tables=validity_raw_tables,
            validity_extended_tables=validity_extended_tables)

    elif choice == "Toelichting per keuze optie":
        print("""
Invoer tabellen zijn naar wens, ga door naar volgende stap  ->  Indien je deze keuzemogelijkheid krijgt zijn de invoertabellen valide en kun je door naar de volgende stap.
                                                                Je zegt daarmee eveneens dat de invoertabellen naar wens zijn. 
Overzichtsfiguren van invoertabellen: Exporteren            ->  Deze interactive HTML-figuren geven je per parameter een snel visueel overzicht van de invoer in het GeoProb-Pipe-bestand. 
Invoer tabellen: Importeren vanuit Excel                    ->  Importeer vanuit Excel de invoertabellen om ze te laten valideren, visualiseren en/of op te slaan in het GeoProb-Pipe-bestand. 
Invoer tabellen: Exporteren naar Excel                      ->  Exporteer vanuit het GeoProb-Pipe-bestand de invoertabellen om ze in Excel te bekijken en/of verder aan te vullen. 
        """)
        inquire_to_import_export_tables_and_figures_or_continue(
            app_settings=app_settings, tables=tables, validity_raw_tables=validity_raw_tables,
            validity_extended_tables=validity_extended_tables)

    elif choice == "Applicatie afsluiten":
        sys.exit(f"Applicatie is afgesloten.")

    else:
        raise ValueError


def export_input_tables_of_db(app_settings: ApplicationSettings, tables: InputParameterTables):
    export_input_parameter_tables(app_settings=app_settings, tables=tables)


def import_input_tables(geopackage_filepath: str) -> InputParameterTables:

    filepath: Optional[str] = None
    filepath_is_valid = False
    while filepath_is_valid is False:
        filepath: str = inquirer.text(
            message="Specificeer het volledige bestandspad naar het input parameters Excel.",
        ).execute()

        filepath = filepath.replace('"', '')

        if not filepath.endswith(".xlsx"):
            print(BColors.WARNING, f"Het bestand moet een .xlsx-bestand zijn. Jouw invoer "
                                   f"{os.path.basename(filepath)} eindigt niet op deze extensie.", BColors.ENDC)
            continue
        if not os.path.exists(filepath):
            print(BColors.WARNING, f"Het opgegeven bestandspad bestaat niet.", BColors.ENDC)
            continue

        filepath_is_valid = True

    tables = InputParameterTables(path_to_excel=filepath, geopackage_filepath=geopackage_filepath)
    print(f"{BColors.UNDERLINE}Tabellen zijn nu geïmporteerd.{BColors.ENDC}")
    return tables


def inquire_to_store_input_tables_to_db(
        app_settings: ApplicationSettings, tables: InputParameterTables):

    choices_list = ["Ja", "Nee"]
    choice = inquirer.select(
        message="Wil je de nieuwe tabellen opslaan in het GeoProb-Pipe-bestand?",
        choices=choices_list,
        default=choices_list[0],
    ).execute()

    if choice == "Ja":
        conn = sqlite3.connect(app_settings.geopackage_filepath)
        tables.df_scenario_invoer.to_sql("scenario_invoer", conn, if_exists="replace", index=False)
        tables.df_parameter_invoer.to_sql("parameter_invoer", conn, if_exists="replace", index=False)
        tables.df_fragility_values_invoer.to_sql("fragility_values_invoer", conn, if_exists="replace", index=False)
        conn.close()
        print(f"{BColors.UNDERLINE}Tabellen zijn nu opgeslagen in het GeoProb-Pipe-file.{BColors.ENDC}")

    elif choice == "Nee":
        pass  # Just continue

    else:
        raise ValueError


def process_input_exist_in_db(app_settings: ApplicationSettings):
    possibly_initiatie_input_tables_in_db(app_settings=app_settings)
    tables: InputParameterTables = load_tables_from_db(app_settings=app_settings)

    # Validate raw tables
    validity_raw_tables = validate_raw_input_tables()

    # Validate expanded tables
    validity_extended_tables: Optional[bool] = None
    if validity_raw_tables: validity_extended_tables = validate_expanded_input_tables(
        geopackage_filepath=app_settings.geopackage_filepath)

    # Provide user with follow-up options
    inquire_to_import_export_tables_and_figures_or_continue(
        app_settings=app_settings, tables=tables,
        validity_raw_tables=validity_raw_tables, validity_extended_tables=validity_extended_tables)
    # -> Redirects also to new process loop


def process_export_input_of_db(
        app_settings: ApplicationSettings, tables: InputParameterTables,
        validity_raw_tables: bool, validity_extended_tables: bool):
    export_input_tables_of_db(app_settings=app_settings, tables=tables)
    inquire_to_import_export_tables_and_figures_or_continue(
        app_settings=app_settings, tables=tables, validity_raw_tables=validity_raw_tables,
        validity_extended_tables=validity_extended_tables)
    # -> Redirects also to new process loop


def process_import_input(app_settings: ApplicationSettings):
    tables = import_input_tables(app_settings.geopackage_filepath)  # Asks user for path to input-file

    # Validate raw tables
    validity_raw_tables = validate_raw_input_tables()

    # Ask to export overview pictures
    if validity_raw_tables: inquire_if_input_figures_should_be_exported(app_settings=app_settings, tables=tables)

    # Validate expanded tables
    validity_extended_tables: Optional[bool] = None
    if validity_extended_tables: validity_extended_tables = validate_expanded_input_tables(
        geopackage_filepath=app_settings.geopackage_filepath)

    # Provide user with follow-up options
    inquire_to_store_input_tables_to_db(app_settings=app_settings, tables=tables)
    inquire_to_import_export_tables_and_figures_or_continue(
        app_settings=app_settings, tables=tables, validity_raw_tables=validity_raw_tables,
        validity_extended_tables=validity_extended_tables)
    # -> Redirects also to new process loop


def added_input_parameter_data(app_settings: ApplicationSettings) -> bool:
    process_input_exist_in_db(app_settings=app_settings)
    return True


# def check_input_excel_tables_exist(app_settings: ApplicationSettings):
#     layers = fiona.listlayers(app_settings.geopackage_filepath)
#
#     if "parameter_invoer" in layers and "scenario_invoer" in layers and "fragility_values" in layers:
#
#         print(BColors.OKBLUE, f"✔  Invoer data al toegevoegd", BColors.ENDC)
#         pass
#
#     start_import_data_menu(app_settings=app_settings)


# def start_import_data_menu(app_settings: ApplicationSettings):
#
#     choices_list = ["Excel-bestand importeren", "Template exporteren", "Applicatie afsluiten"]
#     choice = inquirer.select(
#         message="Er is nog geen invoer data geïmporteerd. Nu importeren?",
#         choices=choices_list,
#         default=choices_list[0],
#     ).execute()
#
#     if choice == choices_list[0]:
#         import_excel(app_settings=app_settings)
#     elif choice == choices_list[1]:
#         export_template(app_settings=app_settings)
#     elif choice == choices_list[2]:
#         sys.exit(f"Applicatie is afgesloten.")
#     else:
#         raise ValueError


# def export_template(app_settings: ApplicationSettings):
#
#     # Copy template to workspace
#     dst_path = os.path.join(app_settings.workspace_dir, "input_parameters_template.xlsx")
#     if os.path.exists(dst_path):
#         datetime_stamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
#         dst_path = dst_path.replace(".xlsx", f"_{datetime_stamp}.xlsx")
#     with importlib.resources.path(
#             'geoprob_pipe.pre_processing.parameter_input', 'parameter_input_template.xlsx'
#     ) as src_path:
#         shutil.copy2(src=src_path, dst=dst_path)
#
#     # Fill 'Model parameters'
#     df_dummy_data = DataFrame(DUMMY_INPUT)
#     df_dummy_data = df_dummy_data.sort_values(by=["name"])
#     df_model_parameters = df_dummy_data[["name", "description", "remark", "unit"]].copy()
#     with ExcelWriter(dst_path, engine="openpyxl", mode="a", if_sheet_exists="overlay") as writer:
#         df_model_parameters.to_excel(
#             writer, sheet_name="Model parameters", index=False, header=False, startrow=4, startcol=0)
#
#     # Fill 'Scenario invoer'
#     gdf_vakindeling: GeoDataFrame = read_file(app_settings.geopackage_filepath, layer="vakindeling")
#     gdf_vakindeling = gdf_vakindeling.sort_values(by=["id"])
#     df_scenarios = gdf_vakindeling[["id"]].copy()
#     df_scenarios.loc[:, 'naam'] = "scenario1"
#     df_scenarios.loc[:, 'kans'] = 1.00
#     with ExcelWriter(dst_path, engine="openpyxl", mode="a", if_sheet_exists="overlay") as writer:
#         df_scenarios.to_excel(writer, sheet_name="Scenario invoer", index=False, header=False, startrow=3, startcol=0)
#
#     # Fill 'Parameter invoer'
#     df_parameter_invoer = df_dummy_data[["name", "distribution_type", "mean", "variation", "deviation"]].copy()
#     df_parameter_invoer.loc[:, "scope"] = "traject"
#     df_parameter_invoer.loc[:, "scope_referentie"] = ""
#     df_parameter_invoer.loc[:, "ondergrondscenario_naam"] = ""
#     df_parameter_invoer = df_parameter_invoer[[
#         "name", "scope", "scope_referentie", "ondergrondscenario_naam",
#         "distribution_type", "mean", "variation", "deviation"]].copy()
#     with ExcelWriter(dst_path, engine="openpyxl", mode="a", if_sheet_exists="overlay") as writer:
#         df_parameter_invoer.to_excel(
#             writer, sheet_name="Parameter invoer", index=False, header=False, startrow=4, startcol=0)
#
#     print(f"Exporteren van template compleet:\n"
#           f"{dst_path}")
