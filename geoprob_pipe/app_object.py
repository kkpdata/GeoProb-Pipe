from __future__ import annotations
import os
from datetime import datetime
from typing import TYPE_CHECKING, Optional, List
import pandas as pd

from geoprob_pipe.cmd_app.parameter_input.expand_input_tables import run_expand_input_tables
from geoprob_pipe.cmd_app.parameter_input.input_parameter_figures import InputParameterFigures
from geoprob_pipe.cmd_app.parameter_input.input_parameter_tables import InputParameterTables

try:
    import probabilistic_library
except ModuleNotFoundError:
    raise ModuleNotFoundError(
        "No module named 'probabilistic_library'. This package is not publicly available or part of the repository. \n"
        "Please request the wheel-file through the developer and install it manually. Due to copyright reasons, do \n"
        "not commit the wheel-file into the repository.")

from geoprob_pipe.input_data import InputData
from geoprob_pipe.results import Results
from geoprob_pipe.spatial import Spatial
from geoprob_pipe.visualizations import Visualizations
from geoprob_pipe.calculations.systems.build_and_run import build_and_run_system_calculations
from geoprob_pipe.utils.update_metadata import update_metadata
import logging
if TYPE_CHECKING:
    from geoprob_pipe.calculations.systems.build_and_run import CalcResult
    from geoprob_pipe.cmd_app.cmd import ApplicationSettings


logger = logging.getLogger("geoprob-pipe")


def dummy_function(a: float, b: float, c: float) -> float:
    return a + b - c


class GeoProbPipe:
    """ GeoProb-Pipe application object. """
    # TODO Later Could Groot: Gebruiker optie geven OpenTurns of Prob-library te kiezen? Dus engine keuze.

    def __init__(self, app_settings: ApplicationSettings) -> None:

        # Miscellaneous
        import warnings
        warnings.simplefilter(
            action='ignore',
            category=FutureWarning)  # Preferably address FutureWarnings: part of pydra-core

        logger.info("Initiating project.")
        self.time_start = datetime.now()

        self.input_data = InputData(app_settings=app_settings)  # TODO: Alter with new option

        # Read calculation settings
        # self._read_calculation_settings()  # TODO: Not part of new version
        # TODO: Unsure if the single statement belongs here. Wouldn't it be part of input data?

        self.calc_results: List[CalcResult] = build_and_run_system_calculations(self)
        self.results = Results(self)

        # Log finish
        self.time_end = datetime.now()
        self.time_diff = self.time_end - self.time_start
        logger.info(f"Calculations were performed successfully in {int(self.time_diff.total_seconds())} seconds.")

        # Append logic classes
        self.visualizations = Visualizations(self)
        self.spatial = Spatial(self)

    # def _read_calculation_settings(self):  # TODO: Not (yet) part of new version
    #     """ Read calculation settings from Excel file. """
    #     self.df_settings = read_excel(self.workspace.path_input_excel, sheet_name="Settings", index_col=0, header=0)
    #     logger.info(f"Settings successfully loaded from `{self.workspace.path_input_excel.name}`.")
    #     time.sleep(1)  # Some time to make sure the print below, is printed after the logger print.

    def _export_validation_messages(self):
        # Gather validation messages from calculations
        df_val: Optional[pd.DataFrame] = None
        [result.validation_message.concat_with_df(df_to_append_to=df_val) for result in self.calc_results
         if result.validation_message is not None]

        # Export dataframe with validation messages
        if df_val is not None:
            export_path = os.path.join(self.input_data.app_settings.workspace_dir, "validation_messages.xlsx")
            df_val.to_excel(export_path, index=False)

    def export_archive(self):
        """ Exports everything related to this project. """
        logger.info("Now exporting archive...")

        export_dir: str = os.path.join(
            str(self.input_data.app_settings.workspace_dir), "exports",
            str(self.input_data.app_settings.datetime_stamp))

        self.results.export_results()
        self.visualizations.export_visualizations()
        self.spatial.export_geopackage()

        # Parameter invoer als expanded
        df_expanded = run_expand_input_tables(geopackage_filepath=self.input_data.app_settings.geopackage_filepath)
        input_dir = os.path.join(export_dir, "input")
        os.makedirs(input_dir, exist_ok=True)
        df_expanded.to_excel(excel_writer=os.path.join(input_dir, "df_parameter_invoer_expanded.xlsx"), index=False)

        # Input parameter figures
        obj = InputParameterFigures.populate(
            app_settings=self.input_data.app_settings, export=True, export_sub_dir="input")
        obj.run()

        # Add run metadata to geopackage
        update_metadata(self)
        self._export_validation_messages()

        print(f"Exported archive to {export_dir}")
