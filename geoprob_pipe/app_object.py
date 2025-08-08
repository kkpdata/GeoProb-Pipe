from pathlib import Path
import pandas as pd
from datetime import datetime
try:
    import probabilistic_library
except ModuleNotFoundError:
    raise ModuleNotFoundError(
        "No module named 'probabilistic_library'. This package is not publicly available or part of the repository. \n"
        "Please request the wheel-file through the developer and install it manually. Due to copyright reasons, do \n"
        "not commit the wheel-file into the repository.")
import logging
from geoprob_pipe.utils.workspace import Workspace
from geoprob_pipe.calculations.system_calculations.system_base_objects.parallel_system_reliability_calculation import (
    ParallelSystemReliabilityCalculation)
from geoprob_pipe.results.main_object import Results
from geoprob_pipe.input_data import InputData
from geoprob_pipe.visualizations import Visualizations
import time
from typing import List
from geoprob_pipe.calculations.system_calculations.piping_system.build_and_run import (
    build_and_run_piping_system_calculations)


logger = logging.getLogger("geoprob_pipe_logger")


def provide_explanation_to_user():
    time.sleep(1)  # Timer to make sure the logger is finished first.
    print("""
    You can now use the interactive console to explore and/or export the results. Some examples:
        project.export_archive())
        project.results.export_results()
        print(project.results.df_beta_uittredepunten)
        print(project.input_data.vakken)
    """)


class GeoProbPipe:
    """ Project class """
    # TODO Later Could Groot: Gebruiker optie geven OpenTurns of Prob-library te kiezen? Dus engine keuze.

    def __init__(
            self,
            path_to_workspace: str|Path
    ) -> None:

        logger.info("Initiating project.")
        self.time_start = datetime.now()

        self.workspace = Workspace(path_to_workspace)
        self.input_data = InputData(self.workspace)

        # Read calculation settings
        self._read_calculation_settings()
        # TODO: Unsure if the single statement belongs here. Wouldn't it be part of input data?

        self.calculations: List[ParallelSystemReliabilityCalculation] = build_and_run_piping_system_calculations(self)
        self.results = Results(self)
        # self.df_beta_limit_states = _collect_df_beta_per_limit_state(self)
        # self.df_beta_scenarios = _collect_df_beta_per_scenario(self)
        # self.df_beta_uittredepunten = self._calculate_df_beta_per_uittredepunt()
        # self.df_beta_vakken = self._calculated_df_beta_per_limit_state()

        # Log finish
        self.time_end = datetime.now()
        time_diff = self.time_end - self.time_start
        logger.info(f"Calculations were performed successfully in {int(time_diff.total_seconds())} seconds.")
        provide_explanation_to_user()

        # Append logic classes
        self.visualizations = Visualizations(self)

    def _read_calculation_settings(self):
        """ Read calculation settings from Excel file. """
        self.df_settings = pd.read_excel(self.workspace.path_input_excel, sheet_name="Settings", index_col=0, header=0)
        logger.info(f"Settings successfully loaded from `{self.workspace.path_input_excel.name}`.")
        time.sleep(1)  # Some time to make sure the print below, is printed after the logger print.

        print(f"""
    For your information, display a full list of settings by printing:
        from probabilistic_library.reliability import Settings
        print(Settings().__dir__())
    This unfortunately lacks in further documentation, but the parameter names are relatively descriptive. 
        """)

    def export_archive(self):
        """ Exports everything related to this project. """
        self.results.export_results()
        self.visualizations.export_visualizations()
