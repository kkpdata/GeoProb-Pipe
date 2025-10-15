from __future__ import annotations
import os
from InquirerPy import inquirer
from geopandas import GeoDataFrame, read_file
import shutil
from pandas import DataFrame, ExcelWriter
from geoprob_pipe.calculations.system_calculations.piping_system.dummy_input import DUMMY_INPUT
from datetime import datetime
import importlib.resources
from typing import TYPE_CHECKING
import sys
import fiona
from geoprob_pipe.utils.validation_messages import BColors
if TYPE_CHECKING:
    from geoprob_pipe.pre_processing.cmd import ApplicationSettings


def added_input_parameter_data(app_settings: ApplicationSettings) -> bool:
    layers = fiona.listlayers(app_settings.geopackage_filepath)

    if "input_parameter_data" in layers:
        print(BColors.OKBLUE, f"✔  Invoer data al toegevoegd.", BColors.ENDC)
        return True

    start_import_data_menu(app_settings=app_settings)
    return True


def start_import_data_menu(app_settings: ApplicationSettings):

    choices_list = ["Excel-bestand importeren", "Template exporteren", "Applicatie afsluiten"]
    choice = inquirer.select(
        message="Er is nog geen invoer data geïmporteerd. Nu importeren?",
        choices=choices_list,
        default=choices_list[0],
    ).execute()

    if choice == choices_list[0]:
        import_excel(app_settings=app_settings)
    elif choice == choices_list[1]:
        export_template(app_settings=app_settings)
    elif choice == choices_list[2]:
        sys.exit(f"Applicatie is afgesloten.")
    else:
        raise ValueError


def export_template(app_settings: ApplicationSettings):

    # Copy template to workspace
    dst_path = os.path.join(app_settings.workspace_dir, "input_parameters_template.xlsx")
    if os.path.exists(dst_path):
        datetime_stamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        dst_path = dst_path.replace(".xlsx", f"_{datetime_stamp}.xlsx")
    with importlib.resources.path(
            'geoprob_pipe.pre_processing.parameter_input', 'parameter_input_template.xlsx'
    ) as src_path:
        shutil.copy2(src=src_path, dst=dst_path)

    # Fill 'Model parameters'
    df_dummy_data = DataFrame(DUMMY_INPUT)
    df_dummy_data = df_dummy_data.sort_values(by=["name"])
    df_model_parameters = df_dummy_data[["name", "description", "remark", "unit"]].copy()
    with ExcelWriter(dst_path, engine="openpyxl", mode="a", if_sheet_exists="overlay") as writer:
        df_model_parameters.to_excel(
            writer, sheet_name="Model parameters", index=False, header=False, startrow=4, startcol=0)

    # Fill 'Scenario invoer'
    gdf_vakindeling: GeoDataFrame = read_file(app_settings.geopackage_filepath, layer="vakindeling")
    gdf_vakindeling = gdf_vakindeling.sort_values(by=["id"])
    df_scenarios = gdf_vakindeling[["id"]].copy()
    df_scenarios.loc[:, 'naam'] = "scenario1"
    df_scenarios.loc[:, 'kans'] = 1.00
    with ExcelWriter(dst_path, engine="openpyxl", mode="a", if_sheet_exists="overlay") as writer:
        df_scenarios.to_excel(writer, sheet_name="Scenario invoer", index=False, header=False, startrow=3, startcol=0)

    # Fill 'Parameter invoer'
    df_parameter_invoer = df_dummy_data[["name", "distribution_type", "mean", "variation", "deviation"]].copy()
    df_parameter_invoer.loc[:, "scope"] = "traject"
    df_parameter_invoer.loc[:, "scope_referentie"] = ""
    df_parameter_invoer.loc[:, "ondergrondscenario_naam"] = ""
    df_parameter_invoer = df_parameter_invoer[[
        "name", "scope", "scope_referentie", "ondergrondscenario_naam",
        "distribution_type", "mean", "variation", "deviation"]].copy()
    with ExcelWriter(dst_path, engine="openpyxl", mode="a", if_sheet_exists="overlay") as writer:
        df_parameter_invoer.to_excel(
            writer, sheet_name="Parameter invoer", index=False, header=False, startrow=4, startcol=0)

    print(f"Exporteren van template compleet:\n"
          f"{dst_path}")


def import_excel(app_settings: ApplicationSettings):

    # Benodigde identifiers ophalen voor invoer per scenario opzetten
    #   - df_uittredepunt met 'uittredepunt_id' en 'vak_id'
    #   - mergen met df_ondergrondscenarios:
    #       - explodeert df_uittredepunt naar rij per scenario
    #       - voeg kolom ondergrondscenario_id toe
    # Merge per parameter op uittredepunt-niveau met de 'Parameter invoer'-Excel sheet
    # Voor de lege cellen, merge per parameter op scenario en vakniveau-niveau met de 'Parameter invoer'-Excel sheet
    # Voor de lege cellen, merge per parameter op vakniveau-niveau met de 'Parameter invoer'-Excel sheet
    # Voor de lege cellen, merge per parameter op traject-niveau met de 'Parameter invoer'-Excel sheet
    # Voor overige lege cellen, geeft validatie error terug.

    pass
