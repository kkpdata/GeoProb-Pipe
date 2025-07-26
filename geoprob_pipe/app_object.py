from dataclasses import dataclass
from pathlib import Path
import pandas as pd
from pandas.api.types import CategoricalDtype
from datetime import datetime

from geoprob_pipe.calculations.system_calculations.piping_system.reliability_calculation import \
    PipingSystemReliabilityCalculation
from geoprob_pipe.graphs.overview.generate_flow_chart_v2 import generate_overview_flow_chart_with_betas
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
from geoprob_pipe.helper_functions.statistics_utils import convert_failure_probability_to_beta
from geoprob_pipe.calculations.system_calculations.piping_system.limit_state_functions import (
    calc_Z_h, calc_Z_p, calc_Z_u)
from geoprob_pipe.calculations.system_calculations.system_base_objects.parallel_system_reliability_calculation import (
    ParallelSystemReliabilityCalculation)
from geoprob_pipe.input_data import InputData
from geoprob_pipe.graphs import Graphs
import time
import os
from geoprob_pipe.calculations.system_calculations.piping_system.system_builder import PipingSystemBuilder
from typing import List

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

        # Initialize Workspace object (also checks if input/output folders contain all necessary files)
        self.workspace = Workspace(path_to_workspace)

        # Gather input data
        self.input_data = InputData(self.workspace)

        # Initialize collections. Note that UittredepuntCollection and OndergrondscenarioCollection link the
        # instances of Uittredepunt and OndergrondScenario to the corresponding Vak instance


        # Read calculation settings
        self._read_calculation_settings()

        # Build parallel system calculations
        self.system_calculations: List[ParallelSystemReliabilityCalculation] = _build_system_calculations(self)
        for calc in self.system_calculations:
            calc.run()
            # TODO Nu Should Middel: Uitvoeren van system calculations ombouwen naar Threads
        self.df_results_system_calculations = _create_results_df(self)


        # Build and run calculations per limit state
        self._build_and_run_calculations_per_limit_state()
        # TODO Nu Must Klein: Exporteer df met resultaten per limit state.

        return

        # Build and run combined limit state calculations
        self._build_and_run_combined_limit_state_calculations()
        # TODO Nu Must Klein: Exporteer df met resultaten per combinatie.

        # Use the chances of the underlying scenarios to calculate the combined failure probability for each
        # uittredepunt
        self._calculations_uittredepunt = self._calculations_combined_models.assign(
            combined_failure_probability=self._calculations_combined_models.apply(
                lambda row: row['failure_probability'] *
                            row['reliability_calculation'].ondergrond_scenario.variables.ondergrondscenario_kans[
                                "value"], axis=1)).groupby('uittredepunt_id', as_index=False)[
            'combined_failure_probability'].sum()
        self._calculations_uittredepunt["beta"] = self._calculations_uittredepunt["combined_failure_probability"].apply(
            lambda failure_prob: convert_failure_probability_to_beta(failure_prob))

        # TODO Later Must Middel: Exporteer df met resultaten per uittredepunt.
        # TODO Later Must Middel: Exporteer df met resultaten per vak.

        # Log finish
        self.time_end = datetime.now()
        time_diff = self.time_end - self.time_start
        logger.info(f"Calculations were performed successfully in {int(time_diff.total_seconds())} seconds.")
        provide_explanation_to_user()

        # Append logic classes
        self.graphs = Graphs(self)

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

    @property
    def results(self) -> _DataClassResults:
        """ Returns a dataclass with dot-access to the results of the unique model calculations (uplift/heave/piping)
        and of the combined calculations. """
        return _DataClassResults(
            df_limit_states=self._df_calculation_results_limit_states,
            df_combined=self._calculations_combined_models,
            df_uittredepunt=self._calculations_uittredepunt
        )

    def export_results(self):

        # Results of limit state calculations
        df = self.results.df_limit_states
        df = df[["uittredepunt_id", "ondergrondscenario_id", "model", "converged", "beta", "failure_probability"]]
        df.loc[:, 'beta'] = df['beta'].round(2)
        # TODO Later Should Middel: Alpha en/of influence_factors exporteren in een aparte Excel.
        #  Daarbij eveneens afronden.
        # TODO Later Should Klein: Bespreken wat we met resultaten doen die niet 'converged' zijn.
        df.to_excel(excel_writer=self.workspace.path_output_folder.folderpath / "df_limit_states.xlsx")
        # TODO Nu Must Middel: Visualiseer de limit state resultaten.
        #  Indien dat niet al bestaat, dan visualiseren in een eenvoudige maar overzichtelijke grafiek. Geen map nodig
        #  (voor nu).

        # Results of combined calculations
        df = self.results.df_combined
        df = df[["uittredepunt_id", "ondergrondscenario_id", "converged", "beta", "failure_probability"]]
        df.loc[:, 'beta'] = df['beta'].round(2)
        df.to_excel(excel_writer=self.workspace.path_output_folder.folderpath / "df_combined.xlsx")
        # TODO Nu Must Middel: Visualiseer de combined resultaten.
        #  Indien dat niet al bestaat, dan visualiseren in een eenvoudige maar overzichtelijke grafiek. Geen map nodig
        #  (voor nu).
        # TODO Nu Must Middel: Visualiseer een vergelijking tussen de combined en de limit state resultaten.
        #  Indien dat niet al bestaat, dan visualiseren in een eenvoudige maar overzichtelijke grafiek. Geen map nodig
        #  (voor nu).

        # Export graphs
        fig = self.graphs.combined.betrouwbaarheidsindex()
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        export_dir = r"C:\Users\CP\git_clones\GeoProb-Pipe\GeoProb-PipeV2\exports"
        os.makedirs(export_dir, exist_ok=True)
        export_path = os.path.join(export_dir, f"{timestamp}_B_STPH_sc.png")
        fig.savefig(export_path, dpi=300)

        # Export result overview flowchart
        df = self.results.df_combined
        lowest_beta_row: pd.DataFrame  = df.loc[df['beta'].idxmin()]
        # print(f"{lowest_beta_row=}")
        # print(f"{lowest_beta_row['ondergrondscenario_id']=}")
        generate_overview_flow_chart_with_betas(
            app_obj=self,
            export_dir=export_dir,
            ondergrondscenario_id=lowest_beta_row['ondergrondscenario_id'],
            uittredepunt_id=lowest_beta_row['uittredepunt_id']
        )

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


def _build_system_calculations(self: GeoProbPipe) -> List[PipingSystemReliabilityCalculation]:
    system_builder = PipingSystemBuilder()
    df = self.input_data.df_overview_parameters
    df_constants = df[df["parameter_type"] == "constant"]
    return system_builder.build_instances(
        vak_collection=self.input_data.vakken,
        df_settings=self.df_settings,
        df_constants=df_constants)


def _create_results_df(self: GeoProbPipe):

    def create_row(calc):
        return {
            "uittredepunt_id": calc.metadata["uittredepunt_id"],
            "ondergrondscenario_id": calc.metadata["ondergrondscenario_id"],
            "vak_id": calc.metadata["vak_id"],
            "system_calculation": calc,
            "converged": calc.system_design_point.is_converged,
            "beta": round(calc.system_design_point.reliability_index, 2),
            "failure_probability": calc.system_design_point.probability_failure,
            "model_betas": ", ".join([
                str(round(dp.reliability_index, 2)) for dp in calc.model_design_points
            ])
        }

    df = pd.DataFrame([
        create_row(calc)
        for calc in self.system_calculations]
    ).sort_values(
        by=["uittredepunt_id", "ondergrondscenario_id", "vak_id"]).reset_index(drop=True)
    return df
