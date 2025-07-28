from dataclasses import dataclass
from pathlib import Path
import pandas as pd
from pandas.api.types import CategoricalDtype
from datetime import datetime
try:
    import probabilistic_library
except ModuleNotFoundError:
    raise ModuleNotFoundError(
        "No module named 'probabilistic_library'. This package is not publicly available or part of the repository. \n"
        "Please request the wheel-file through the developer and install it manually. Due to copyright reasons, do \n"
        "not commit the wheel-file into the repository.")
import logging
from geoprob_pipe.classes.workspace import Workspace
from geoprob_pipe.calculations.combined import build_and_run_combined_calculation
from geoprob_pipe.calculations.limit_states import build_and_run_unique_model_calculations
from geoprob_pipe.calculations.system_calculations.piping_system.limit_state_functions import (
    calc_Z_h, calc_Z_p, calc_Z_u)
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


@dataclass
class _DataClassResults:
    """Used for dot-accessing the calculation results
    """
    df_limit_states: pd.DataFrame
    df_combined: pd.DataFrame
    df_uittredepunt: pd.DataFrame


def provide_explanation_to_user():
    time.sleep(1)  # Timer to make sure the logger is finished first.
    print("""
    You can now use the interactive console to explore and/or export the results. Some examples:
        print(project.results.unique_models)
        print(project.results.combined)
        project.results.combined.to_excel(project.workspace.path_output_folder.folderpath / "fragility_curve_data_combined.xlsx")
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

    def _build_and_run_calculations_per_limit_state(self):
        """ Build and run ReliabilityCalculations objects per limit state.

        These objects are combinations of uittredepunten and ondergrondscenarios for each model (uplift/heave/piping).

        Note: due to limitations in the probabilistic_library, it is not possible to set up all calculations first and
        then run them. After setting up a calculations for each model (uplift/heave/piping), we need to run them
        immediately before setting up the next model.
        """

        logger.info(f"[Uplift] Building and running calculations.")
        df_uplift = build_and_run_unique_model_calculations(
            model=calc_Z_u,
            vak_collection=self.input_data.vakken,
            df_overview_parameters=self.input_data.df_overview_parameters,
            df_settings=self.df_settings)

        logger.info(f"[Heave] Building and running calculations.")
        df_heave = build_and_run_unique_model_calculations(
            model=calc_Z_h,
            vak_collection=self.input_data.vakken,
            df_overview_parameters=self.input_data.df_overview_parameters,
            df_settings=self.df_settings)

        logger.info(f"[Piping] Building and running 'piping' calculations.")
        df_piping = build_and_run_unique_model_calculations(
            model=calc_Z_p,
            vak_collection=self.input_data.vakken,
            df_overview_parameters=self.input_data.df_overview_parameters,
            df_settings=self.df_settings)

        self._calculations_unique = {
            "uplift": df_uplift,
            "heave": df_heave,
            "piping": df_piping,
        }

    def _build_and_run_combined_limit_state_calculations(self):
        """ Use the probabilistic_library to combine the calculations of the separate models (uplift/heave/piping) into
        one beta/failure probability for each uittredepunt and ondergrondscenario combination.

        :return:
        """

        logger.info(f"[Combined] Building and running calculations.")
        df_grouped = self._df_calculation_results_limit_states.groupby(["uittredepunt_id", "ondergrondscenario_id"])
        total = df_grouped.__len__()
        time_start = time.time()

        # Build and run calculations
        self._calculations_combined_models = df_grouped.apply(
            lambda df_group: build_and_run_combined_calculation(
                df_group,
                self.input_data.uittredepunten[str(df_group.name[0])],
                self.input_data.ondergrondscenarios[str(df_group.name[1])])).reset_index(drop=True)
        # TODO Nu Should Middel: Implement Thread Executor for this.

        # Reporting finished
        duration = int(time.time() - time_start)
        logger.info(f"[Combined] Finished all {total} calculations in under {duration} seconds. "
                    f"That is on average under {round(duration / total, 3)} seconds per calculation.")

    # @property
    # def results(self) -> _DataClassResults:
    #     """ Returns a dataclass with dot-access to the results of the unique model calculations (uplift/heave/piping)
    #     and of the combined calculations. """
    #     return _DataClassResults(
    #         df_limit_states=self._df_calculation_results_limit_states,
    #         df_combined=self._calculations_combined_models,
    #         df_uittredepunt=self._calculations_uittredepunt
    #     )

    @property
    def _df_calculation_results_limit_states(self) -> pd.DataFrame:
        """ Merge the DataFrames of the unique limit state calculations (uplift/heave/piping) into a single DataFrame
        for convenient access. The dataframe is sorted by uittredepunt, ondergrondscenario and limit state type. """
        
        # Store the model type in a new column
        df_unique_model_results = pd.concat(
            [df.assign(model=key) for key, df in self._calculations_unique.items()],
            ignore_index=True
        )  

        # Sort DataFrame of all ReliabilityCalculations by model using custom order uplift, heave and piping
        df_unique_model_results["model"] = df_unique_model_results["model"].astype(CategoricalDtype(
            categories=["uplift", "heave", "piping"], ordered=True))
        df_unique_model_results = df_unique_model_results.sort_values(
            by=["uittredepunt_id", "ondergrondscenario_id", "model"]
        ).reset_index(drop=True)
        
        # Make sure that the columns are in a specific order for easier access
        known = ["uittredepunt_id", "uittredepunt", "ondergrondscenario_id", "ondergrondscenario", "model",
                 "reliability_calculation"]
        df_unique_model_results = df_unique_model_results[known + [
            col for col in df_unique_model_results.columns if col not in known]]
        
        return df_unique_model_results
