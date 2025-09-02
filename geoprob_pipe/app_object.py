import os
from pathlib import Path
from datetime import datetime
from pandas import DataFrame, read_excel, concat
try:
    import probabilistic_library
except ModuleNotFoundError:
    raise ModuleNotFoundError(
        "No module named 'probabilistic_library'. This package is not publicly available or part of the repository. \n"
        "Please request the wheel-file through the developer and install it manually. Due to copyright reasons, do \n"
        "not commit the wheel-file into the repository.")
# noinspection PyPep8Naming
from geoprob_pipe.utils.loggers import TmpAppConsoleHandler as logger
from geoprob_pipe.utils.workspace import Workspace
from geoprob_pipe.calculations.system_calculations.system_base_objects.parallel_system_reliability_calculation import (
    ParallelSystemReliabilityCalculation)
from geoprob_pipe.results import Results
from geoprob_pipe.spatial import Spatial
from geoprob_pipe.input_data import InputData
from geoprob_pipe.visualizations import Visualizations
import time
from typing import List, Optional
from geoprob_pipe.calculations.system_calculations.piping_system.build_and_run import (
    build_and_run_piping_system_calculations)


class GeoProbPipe:
    """ GeoProb-Pipe application object. """
    # TODO Later Could Groot: Gebruiker optie geven OpenTurns of Prob-library te kiezen? Dus engine keuze.

    def __init__(
            self,
            path_to_workspace: str|Path
    ) -> None:

        # Miscellaneous
        import warnings
        warnings.simplefilter(
            action='ignore',
            category=FutureWarning)  # Preferably address FutureWarnings: part of pydra-core

        logger.info("Initiating project.")
        self.time_start = datetime.now()

        self.workspace = Workspace(path_to_workspace)
        self.input_data = InputData(self.workspace)

        # Read calculation settings
        self._read_calculation_settings()
        # TODO: Unsure if the single statement belongs here. Wouldn't it be part of input data?

        self.calculations: List[ParallelSystemReliabilityCalculation] = build_and_run_piping_system_calculations(self)
        self.results = Results(self)

        # Log finish
        self.time_end = datetime.now()
        time_diff = self.time_end - self.time_start
        logger.info(f"Calculations were performed successfully in {int(time_diff.total_seconds())} seconds.")

        # Append logic classes
        self.visualizations = Visualizations(self)
        self.spatial = Spatial(self)

    def _read_calculation_settings(self):
        """ Read calculation settings from Excel file. """
        self.df_settings = read_excel(self.workspace.path_input_excel, sheet_name="Settings", index_col=0, header=0)
        logger.info(f"Settings successfully loaded from `{self.workspace.path_input_excel.name}`.")
        time.sleep(1)  # Some time to make sure the print below, is printed after the logger print.

    def _export_validation_messages(self):
        df: Optional[DataFrame] = None

        # Gather validation messages from all calculations
        for calc in self.calculations:

            # Get df to append
            df_to_append = calc.validation_messages.df
            if df_to_append is None:
                continue

            # Describe about
            selected_keys = ["uittredepunt_id", "ondergrondscenario_id", "vak_id"]
            original_dict = calc.metadata
            filtered_dict = {key: original_dict[key] for key in selected_keys if key in original_dict}
            df_to_append["about"] = f"Calculation {filtered_dict}"
            df_to_append = df_to_append[["type", "about", "msg"]]

            # Append to all other validation messages
            if df is None:
                df = df_to_append
            df = concat([df, df_to_append])

        # Export dataframe with validation messages
        if df is not None:
            export_path = os.path.join(self.workspace.path_output_folder.folderpath, "validation_messages.xlsx")
            df.to_excel(export_path)

    def export_archive(self):
        """ Exports everything related to this project. """
        logger.info("Now exporting archive...")
        self.results.export_results()
        self.visualizations.export_visualizations()
        self.spatial.export_geopackage()
        self._export_validation_messages()
