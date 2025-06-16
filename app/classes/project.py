
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from pandas.api.types import CategoricalDtype
from probabilistic_library.reliability import Settings

from app.classes.ondergrond_scenario import OndergrondScenarioCollection
from app.classes.overschrijdingsfrequentielijn import (
    OverschrijdingsfrequentielijnCollection,
)
from app.classes.uittredepunt import UittredepuntCollection
from app.classes.vak import VakCollection
from app.classes.workspace import Workspace
from app.helper_functions.calculation_helpers import (
    build_and_run_combined_calculations,
    build_and_run_unique_model_calculations,
)
from app.helper_functions.data_validation import (
    checks_input_parameters,
    checks_overview_parameters,
)
from app.helper_functions.z_functions import calc_Z_h, calc_Z_p, calc_Z_u


@dataclass
class _DataClassResults:
    """Used for dot-accessing the calculation results
    """
    unique_models: pd.DataFrame
    combined: pd.DataFrame


class Project():
    """ Project class """
    def __init__(self, PATH_WORKSPACE: str|Path) -> None:
        
        # Initialize Workspace object (also checks if input/output folders contain all necessary files)
        self.workspace = Workspace(PATH_WORKSPACE)
        print("\nINFO: workspace (I/O folders) successfully processed")

        # Read overview data of parameters from input Excel file (includes e.g. upper and lower bounds, type of distribution, etc.) and carry out checks
        self.df_overview_parameters = pd.read_excel(self.workspace.excel_path, sheet_name="Overzicht_parameters", index_col=0, header=0).rename(columns=lambda x: x.strip())
        checks_overview_parameters(self.df_overview_parameters)

        # Read input data of vakken, uittredepunten and ondergrondscenarios data from input Excel file and carry out checks.
        # Note that the df's are not set on self (Project) but are added below to VakCollection/UittredepuntCollection/OndergrondScenarioCollection
        # Strip trailing whitespace in column names. Also, unused ondergrondscenario's (ondergrondscenario_kans=Nan or ondergrondscenario_kans=0) are removed since these are not relevant
        df_vakken = pd.read_excel(self.workspace.excel_path, sheet_name="Vakken").rename(columns=lambda x: x.strip())
        df_uittredepunten = pd.read_excel(self.workspace.excel_path, sheet_name="Uittredepunten").rename(columns=lambda x: x.strip())
        df_ondergrond_scenarios = pd.read_excel(self.workspace.excel_path, sheet_name="Ondergrondscenarios").rename(columns=lambda x: x.strip()).dropna(subset=['ondergrondscenario_kans']).loc[lambda x: x['ondergrondscenario_kans'] != 0]
        checks_input_parameters(self.df_overview_parameters, df_vakken, df_uittredepunten, df_ondergrond_scenarios)
        print(f"INFO: parameter data successfully loaded from `{self.workspace.excel_path.name}`")

        # Initialize collections. Note that UittredepuntCollection and OndergrondscenarioCollection link the
        # instances of Uittredepunt and OndergrondScenario to the corresponding Vak instance
        self.vak_collection = VakCollection(df_vakken, self.df_overview_parameters)
        self.uittredepunt_collection = UittredepuntCollection(df_uittredepunten, self.vak_collection, self.df_overview_parameters)
        self.ondergrond_scenario_collection = OndergrondScenarioCollection(df_ondergrond_scenarios, self.vak_collection, self.df_overview_parameters)        
        self.overschrijdingsfrequentielijn_collection = OverschrijdingsfrequentielijnCollection(self.workspace.hrd_path, self.uittredepunt_collection)
        print(f"INFO: HRD .sqlite file successfully loaded from `{self.workspace.hrd_path.name}`")

        # Read calculation settings from Excel file
        self.df_settings = pd.read_excel(self.workspace.excel_path, sheet_name="Settings", index_col=0, header=0)
        print(f"INFO: settings successfully loaded from `{self.workspace.excel_path.name}`")
        print(f"INFO: full list of available settings (set these in `{self.workspace.excel_path.name}`):\n{Settings().__dir__()}")

        # Build and run ReliabilityCalculations objects (= combinations of uittredepunten, ondergrondscenarios) for each model (uplift/heave/piping).
        # Note: due to limitations in the probabilistic_library, we cannot first set up all calculations and then run them. After setting up calculations for each model (uplift/heave/piping), we need to run them immediately before setting up the next model.
        self._calculations_unique_models = {
                                            "uplift": build_and_run_unique_model_calculations(calc_Z_u, self.vak_collection, self.df_overview_parameters, self.df_settings),
                                            "heave": build_and_run_unique_model_calculations(calc_Z_h, self.vak_collection, self.df_overview_parameters, self.df_settings),
                                            "piping": build_and_run_unique_model_calculations(calc_Z_p, self.vak_collection, self.df_overview_parameters, self.df_settings),
                                        }

        self._calculations_combined = self._combined_df_calculations_unique_model.groupby(["uittredepunt", "ondergrondscenario"]).apply(lambda df_group: build_and_run_combined_calculations(df_group,
                                                                                                                                                                                             self.uittredepunt_collection[str(df_group.name[0])],
                                                                                                                                                                                             self.ondergrond_scenario_collection[str(df_group.name[1])])
                                                                                                                                        ).reset_index(drop=True)

        print("INFO: calculations were performed successfully")


    @property
    def results(self) -> _DataClassResults:
        """Returns a dataclass with dot-access to the results of the unique model calculations (uplift/heave/piping) and of the combined calculations."""
        return _DataClassResults(
            unique_models=self._combined_df_calculations_unique_model,
            combined=self._calculations_combined,
        )


    @property
    def _combined_df_calculations_unique_model(self) -> pd.DataFrame:
        """Merge the DataFrames of the unique model calculations (uplift/heave/piping) into a single DataFrame for convenient access.

        Returns:
            pd.DataFrame: containing the results of the unique model calculations, sorted by uittredepunt, ondergrondscenario and model type (uplift/heave/piping).
        """
        
        # Store the model type in a new column
        df_unique_model_results = pd.concat(
            [df.assign(model=key) for key, df in self._calculations_unique_models.items()],
            ignore_index=True
        )  
        
        # Sort DataFrame of all ReliabilityCalculations by model using custom order uplift, heave and piping
        df_unique_model_results["model"] = df_unique_model_results["model"].astype(CategoricalDtype(categories=["uplift", "heave", "piping"], ordered=True))
        df_unique_model_results = df_unique_model_results.sort_values(
            by=["uittredepunt", "ondergrondscenario", "model"]
        ).reset_index(drop=True)
        
        # Make sure that the columns are in a specific order for easier access
        known = ["uittredepunt", "ondergrondscenario", "model", "reliability_calculation"]
        df_unique_model_results = df_unique_model_results[known + [col for col in df_unique_model_results.columns if col not in known]]
        
        return df_unique_model_results
    
