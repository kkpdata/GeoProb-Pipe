from __future__ import annotations
# from InquirerPy import inquirer
# import warnings
from typing import TYPE_CHECKING
# import os
# from pandas import DataFrame
# from datetime import datetime
# from pathlib import Path
# from geopandas import GeoDataFrame, read_file
import fiona
from geoprob_pipe.utils.validation_messages import BColors
if TYPE_CHECKING:
    from geoprob_pipe.pre_processing.cmd import ApplicationSettings


def added_input_parameter_data(app_settings: ApplicationSettings) -> bool:
    layers = fiona.listlayers(app_settings.geopackage_filepath)

    if "input_parameter_data" in layers:
        print(BColors.OKBLUE, f"✔  Invoer data al toegevoegd.", BColors.ENDC)
        return True

    # generate_dummy_parameter_input_data(app_settings=app_settings)
    # ask_to_export_or_import(app_settings=app_settings)
    return True

