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
from geoprob_pipe.classes.ondergrond_scenario import OndergrondScenarioCollection
from geoprob_pipe.classes.overschrijdingsfrequentielijn import OverschrijdingsfrequentielijnCollection
from geoprob_pipe.classes.uittredepunt import UittredepuntCollection
from geoprob_pipe.classes.vak import VakCollection
from geoprob_pipe.classes.workspace import Workspace
from geoprob_pipe.calculations.combined import build_and_run_combined_calculation
from geoprob_pipe.calculations.limit_states import build_and_run_unique_model_calculations
from geoprob_pipe.helper_functions.data_validation import checks_input_parameters, checks_overview_parameters
from geoprob_pipe.helper_functions.statistics_utils import convert_failure_probability_to_beta
from geoprob_pipe.helper_functions.z_functions import calc_Z_h, calc_Z_p, calc_Z_u
import time


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
        project.results.combined.to_excel(project.workspace.output.folderpath / "fragility_curve_data_combined.xlsx")
    """)


class Project:
    """ Project class """
    def __init__(
            self,
            path_to_workspace: str|Path
    ) -> None:

        logger.info("Initiating project.")
        self.time_start = datetime.now()

        # Initialize Workspace object (also checks if input/output folders contain all necessary files)
        self.workspace = Workspace(path_to_workspace)

        # Read overview data of parameters from input Excel file (includes e.g. upper and lower bounds, type of
        # distribution, etc.) and carry out checks
        self.df_overview_parameters = pd.read_excel(self.workspace.excel_path, sheet_name="Overzicht_parameters",
                                                    index_col=0, header=0).rename(columns=lambda x: x.strip())
        checks_overview_parameters(self.df_overview_parameters)

        # Read input data of vakken, uittredepunten and ondergrondscenarios data from input Excel file and carry out
        # checks. Note that the df's are not set on self (Project) but are added below to VakCollection/
        # UittredepuntCollection/OndergrondScenarioCollection. Strip trailing whitespace in column names. Also, unused
        # ondergrond scenario's (ondergrondscenario_kans=Nan or ondergrondscenario_kans=0) are removed since these are
        # not relevant
        df_vakken = pd.read_excel(self.workspace.excel_path, sheet_name="Vakken").rename(columns=lambda x: x.strip())
        # TODO Later Must Groot: Volledige object georiënteerde/gebruiksvriendelijke validatie voor de invoer bestanden.
        df_uittredepunten = pd.read_excel(self.workspace.excel_path, sheet_name="Uittredepunten").rename(
            columns=lambda x: x.strip())
        df_ondergrond_scenarios = pd.read_excel(self.workspace.excel_path, sheet_name="Ondergrondscenarios").rename(
            columns=lambda x: x.strip()).dropna(subset=['ondergrondscenario_kans']).loc[
            lambda x: x['ondergrondscenario_kans'] != 0]
        checks_input_parameters(self.df_overview_parameters, df_vakken, df_uittredepunten, df_ondergrond_scenarios)
        logger.info(f"Parameter data successfully loaded from `{self.workspace.excel_path.name}`")

        # Initialize collections. Note that UittredepuntCollection and OndergrondscenarioCollection link the
        # instances of Uittredepunt and OndergrondScenario to the corresponding Vak instance
        self.vak_collection = VakCollection(df_vakken, self.df_overview_parameters)
        self.uittredepunt_collection = UittredepuntCollection(
            df_uittredepunten, self.vak_collection, self.df_overview_parameters)
        self.ondergrond_scenario_collection = OndergrondScenarioCollection(
            df_ondergrond_scenarios, self.vak_collection, self.df_overview_parameters)
        self.overschrijdingsfrequentielijn_collection = OverschrijdingsfrequentielijnCollection(
            self.workspace.hrd_path, self.uittredepunt_collection)
        logger.info(f"HRD .sqlite file successfully loaded from `{self.workspace.hrd_path.name}`")

        # Read calculation settings
        self._read_calculation_settings()

        # Build and run calculations per limit state
        self._build_and_run_calculations_per_limit_state()
        # TODO Nu Must Klein: Exporteer df met resultaten per limit state.

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

    def _read_calculation_settings(self):
        """ Read calculation settings from Excel file. """
        self.df_settings = pd.read_excel(self.workspace.excel_path, sheet_name="Settings", index_col=0, header=0)
        logger.info(f"Settings successfully loaded from `{self.workspace.excel_path.name}`.")
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
            vak_collection=self.vak_collection,
            df_overview_parameters=self.df_overview_parameters,
            df_settings=self.df_settings)

        logger.info(f"[Heave] Building and running calculations.")
        df_heave = build_and_run_unique_model_calculations(
            model=calc_Z_h,
            vak_collection=self.vak_collection,
            df_overview_parameters=self.df_overview_parameters,
            df_settings=self.df_settings)

        logger.info(f"[Piping] Building and running 'piping' calculations.")
        df_piping = build_and_run_unique_model_calculations(
            model=calc_Z_p,
            vak_collection=self.vak_collection,
            df_overview_parameters=self.df_overview_parameters,
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
                self.uittredepunt_collection[str(df_group.name[0])],
                self.ondergrond_scenario_collection[str(df_group.name[1])])).reset_index(drop=True)
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
        df.to_excel(excel_writer=self.workspace.output.folderpath / "df_limit_states.xlsx")
        # TODO Nu Must Middel: Visualiseer de limit state resultaten.
        #  Indien dat niet al bestaat, dan visualiseren in een eenvoudige maar overzichtelijke grafiek. Geen map nodig
        #  (voor nu).

        # Results of combined calculations
        df = self.results.df_combined
        df = df[["uittredepunt_id", "ondergrondscenario_id", "converged", "beta", "failure_probability"]]
        df.loc[:, 'beta'] = df['beta'].round(2)
        df.to_excel(excel_writer=self.workspace.output.folderpath / "df_combined.xlsx")
        # TODO Nu Must Middel: Visualiseer de combined resultaten.
        #  Indien dat niet al bestaat, dan visualiseren in een eenvoudige maar overzichtelijke grafiek. Geen map nodig
        #  (voor nu).
        # TODO Nu Must Middel: Visualiseer een vergelijking tussen de combined en de limit state resultaten.
        #  Indien dat niet al bestaat, dan visualiseren in een eenvoudige maar overzichtelijke grafiek. Geen map nodig
        #  (voor nu).

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
