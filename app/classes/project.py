from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Callable

import pandas as pd
from probabilistic_library.reliability import Settings

from app.classes.ondergrond_scenario import OndergrondScenarioCollection
from app.classes.overschrijdingsfrequentielijn import (
    OverschrijdingsfrequentielijnCollection,
)
from app.classes.reliability_calculation import ReliabilityCalculation
from app.classes.uittredepunt import UittredepuntCollection
from app.classes.vak import VakCollection
from app.classes.workspace import Workspace
from app.helper_functions.data_validation import (
    checks_input_parameters,
    checks_overview_parameters,
)
from app.helper_functions.z_functions import calc_Z_h, calc_Z_p, calc_Z_u


def _start_calculations(list_reliability_calculations: list[ReliabilityCalculation]) -> None:
    # FIXME perhaps find a better locaton for this function, since it is not really part of the Project class
    def run_reliability_calculation(reliability_calculation: ReliabilityCalculation) -> None:
        try:
            reliability_calculation.run()
        except Exception as e:
            print(f"ERROR: could not run running reliability calculation {reliability_calculation.id}: {e}")

    with ThreadPoolExecutor() as executor:
        executor.map(run_reliability_calculation, list_reliability_calculations)


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
        print("INFO: parameter data successfully loaded from 'input.xlsx'")
        
        # Initialize collections. Note that UittredepuntCollection and OndergrondscenarioCollection link the
        # instances of Uittredepunt and OndergrondScenario to the corresponding Vak instance
        self.vak_collection = VakCollection(df_vakken, self.df_overview_parameters)
        self.uittredepunt_collection = UittredepuntCollection(df_uittredepunten, self.vak_collection, self.df_overview_parameters)
        self.ondergrond_scenario_collection = OndergrondScenarioCollection(df_ondergrond_scenarios, self.vak_collection, self.df_overview_parameters)        
        self.overschrijdingsfrequentielijn_collection = OverschrijdingsfrequentielijnCollection(self.workspace.hrd_path, self.uittredepunt_collection)
        print("INFO: HRD .sqlite file successfully loaded")

        # Read calculation settings from Excel file
        self.df_settings = pd.read_excel(self.workspace.excel_path, sheet_name="Settings", index_col=0, header=0)
        print("INFO: settings successfully loaded from 'input.xlsx'")
        print(f"INFO: full list of available settings:\n{Settings().__dir__()}")

        # Build ReliabilityCalculations objects (= combinations of uittredepunten, ondergrondscenarios for each model) and run these
        # Notes:
        #   1. Due to limitations in the probabilistic_library, we cannot first set up all calculations and then run them. After setting up calculations for each model (uplift/heave/piping), we need to run them immediately before setting up the next model.
        #   2. Not all combinations of uittredepunten and ondergrondscenarios are valid, so we need a helper-loop through the vakken which holds the valid combinations
        #   3. Nested for-loops are inefficient but used on purpose since there are no heavy calculations and it's easily understandable
        def _build_and_run_calculations(model: Callable) -> list[ReliabilityCalculation]:
            list_calculations = []
            for vak in self.vak_collection.values():
                for uittredepunt in vak.uittredepunten:
                    for ondergrond_scenario in vak.ondergrond_scenarios:
                        list_calculations.append(
                            ReliabilityCalculation(
                                uittredepunt,
                                ondergrond_scenario,
                                model,
                                self.df_overview_parameters[
                                    self.df_overview_parameters["parameter_type"] == "constant"
                                ],
                                self.df_settings
                            )
                        )
            _start_calculations(list_calculations)
                        
            return list_calculations
        
        self.calculations = {
                            "uplift": _build_and_run_calculations(calc_Z_u),
                            "heave": _build_and_run_calculations(calc_Z_h),
                            "piping": _build_and_run_calculations(calc_Z_p),
                            }
        print("INFO: calculations were performed successfully")

    @property
    def results(self) -> pd.DataFrame:
        """Returns a DataFrame with the results of the calculations."""
        # Combine results from the calculations into a single DataFrame
        df_results = pd.DataFrame.from_dict(self.calculations, orient="index").T.melt(var_name="model", value_name="reliability_calculation")

        df_results["id"] = df_results["reliability_calculation"].apply(lambda x: x.id)
        df_results["converged"] = df_results["reliability_calculation"].apply(lambda x: x.is_converged)
        df_results["beta"] = df_results["reliability_calculation"].apply(lambda x: x.beta)
        df_results["alphas"] = df_results["reliability_calculation"].apply(lambda x: x.alphas)
        df_results["influence_factors"] = df_results["reliability_calculation"].apply(lambda x: x.influence_factors)
        
        return df_results
    
    
    # @property
    # def alphas(self)