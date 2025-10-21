from __future__ import annotations
from InquirerPy import inquirer
import sqlite3
from geoprob_pipe.pre_processing.parameter_input.initiate_input_excel_tables import initiate_input_excel_tables
from geoprob_pipe.pre_processing.parameter_input.input_parameter_figure import InputParameterFigures
from geoprob_pipe.pre_processing.parameter_input.export_input_parameter_excel import export_input_parameter_tables
from geoprob_pipe.pre_processing.parameter_input.input_parameter_tables import InputParameterTables
from typing import TYPE_CHECKING
import sys
from geoprob_pipe.utils.loggers import BColors
if TYPE_CHECKING:
    from geoprob_pipe.pre_processing.cmd import ApplicationSettings


class ProcessInputParameterTables:

    def __init__(self, app_settings: ApplicationSettings):
        self.app_settings: ApplicationSettings = app_settings
        self._check_if_input_tables_exist()

    def _check_if_input_tables_exist(self):

        # Get table names
        conn = sqlite3.connect(self.app_settings.geopackage_filepath)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables_names = [row[0] for row in cursor.fetchall()]
        conn.close()

        # If already exist
        if ("parameter_invoer" in tables_names and
                "scenario_invoer" in tables_names and "fragility_values_invoer" in tables_names):
            print(f"{BColors.UNDERLINE}Tables exist in geopackage{BColors.ENDC}")
        else:
            # If it doesn't exist yet
            print(f"{BColors.UNDERLINE}Tables do not exist in geopackage{BColors.ENDC}")
            self._initiate_input_excel_tables()
            print(f"{BColors.UNDERLINE}Tables exist in geopackage{BColors.ENDC}")

        # Load tables into class
        tables = InputParameterTables(app_settings=self.app_settings)
        self._validate_input_excel_tables(tables=tables)

    def _validate_input_excel_tables(self, tables: InputParameterTables):
        valid: bool = True  # TODO
        if not valid:
            print(f"Input Excel tables are not valid. Validation messages are exported to \n"
                  f"TODO")  # TODO: Specify path to exported validation messages.
            self._import_export_continue_or_store(tables=tables)  # Directly to this, because other steps can't be performed on invalid data

        print(f"{BColors.UNDERLINE}Validation of tables executed{BColors.ENDC}")
        self._inquire_to_export_input_parameter_figures(tables=tables)

    def _initiate_input_excel_tables(self):
        initiate_input_excel_tables(app_settings=self.app_settings)
        print(f"{BColors.UNDERLINE}Tables initiated in geopackage{BColors.ENDC}")
        self.tables_exist_in_geopackage = True

    def _inquire_to_export_input_parameter_figures(self, tables: InputParameterTables):
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
            self._export_parameter_input_figures(tables=tables)
        elif choice == choices_list[1]:
            pass  # Just continue
        elif choice == choices_list[2]:
            sys.exit(f"Applicatie is afgesloten.")
        else:
            raise ValueError

        # Continue to next step: validation
        self._validate_expanded_parameter_input(tables=tables)

    def _export_parameter_input_figures(self, tables: InputParameterTables):
        InputParameterFigures(app_settings=self.app_settings, tables=tables, export=True)
        print(f"{BColors.UNDERLINE}Parameter figures exported{BColors.ENDC}")

    def _validate_expanded_parameter_input(self, tables: InputParameterTables):
        valid: bool = True  # TODO
        if not valid:
            print(f"Input Excel tables are not valid. Validation messages are exported to \n"
                  f"TODO")  # TODO: Specify path to exported validation messages.

        print(f"{BColors.UNDERLINE}Expanded validation executed{BColors.ENDC}")
        self._import_export_continue_or_store(tables=tables)

    def _import_export_continue_or_store(self, tables: InputParameterTables):
        if self.tables_exist_in_geopackage:
            choices_list = [
                "Invoer tabellen importeren (vanuit Excel)", "Invoer tabellen exporteren (naar Excel)",
                "Applicatie afsluiten"]
            choice = inquirer.select(
                message="Wil je de tabellen exporteren (vanuit de GeoPackage)? Of een nieuwe versie importeren?\n"
                        "Na exporteren kun je het naar smaak aanpassen en weer importeren.",
                choices=choices_list,
                default=choices_list[0],
            ).execute()
            if choice == choices_list[0]:
                self._import_excel()
            elif choice == choices_list[1]:
                export_input_parameter_tables(app_settings=self.app_settings, tables=tables)
                self._import_export_continue_or_store(tables=tables)  # In case of export, just re-ask to export/import
            elif choice == choices_list[2]:
                sys.exit(f"Applicatie is afgesloten.")
            else:
                raise ValueError

        else:
            # Ask if tables should be saved
            choices_list = ["Ja", "Nee", "Applicatie afsluiten"]
            choice = inquirer.select(
                message="Je hebt deze tabellen nieuw geïmporteerd. Wil je ze opslaan in de GeoPackage? "
                        "Dit overschrijft de bestaande versie.",
                choices=choices_list,
                default=choices_list[0],
            ).execute()

            if choice == choices_list[0]:
                self._store_new_tables(tables=tables)
            elif choice == choices_list[1]:
                sys.exit(f"Gekozen voor 'Nee'. Applicatie is afgesloten.")
            elif choice == choices_list[2]:
                sys.exit(f"Applicatie is afgesloten.")
            else:
                raise ValueError

    def _import_excel(self):
        pass  # TODO

    def _store_new_tables(self, tables: InputParameterTables):
        pass  # TODO


def added_input_parameter_data(app_settings: ApplicationSettings) -> bool:
    _ = ProcessInputParameterTables(app_settings=app_settings)
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
