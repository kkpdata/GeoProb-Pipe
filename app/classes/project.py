from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd
from probabilistic_library import (
    CombineProject,
    CombinerMethod,
    CombineType,
    CompareType,
    DistributionType,
    ReliabilityMethod,
    ReliabilityProject,
    StandardNormal,
)
from probabilistic_library.reliability import Settings
from probabilistic_library.statistic import Stochast

from app.classes.ondergrond_scenario import OndergrondScenarioCollection
from app.classes.reliability_calculation import ReliabilityCalculation
from app.classes.uittredepunt import UittredepuntCollection
from app.classes.vak import VakCollection
from app.classes.workspace import Workspace
from app.helper_functions.data_validation import (
    checks_input_parameters,
    checks_overview_parameters,
)
from app.helper_functions.piping_functions import calc_Z_h, calc_Z_p, calc_Z_u


class Project():
    """ Project class """
    def __init__(self, PATH_WORKSPACE: str|Path) -> None:
        
        # Initialize Workspace object (also checks if input/output folders contain all necessary files)
        self.workspace = Workspace(PATH_WORKSPACE)
        print("\nINFO: workspace (I/O folders) successfully processed")

        # Read overview data of parameters from input Excel file (includes e.g. upper and lower bounds, type of distribution, etc.) and carry out checks
        self.df_overview_parameters = pd.read_excel(self.workspace.input.folderpath / "input.xlsx", sheet_name="Overzicht_parameters", index_col=0, header=0).rename(columns=lambda x: x.strip())
        checks_overview_parameters(self.df_overview_parameters)

        # Read input data of vakken, uittredepunten and ondergrondscenarios data from input Excel file and carry out checks.
        # Note that the df's are not set on self (Project) but are added below to VakCollection/UittredepuntCollection/OndergrondScenarioCollection
        # Strip trailing whitespace in column names. Also, unused ondergrondscenario's (ondergrondscenario_kans=Nan or ondergrondscenario_kans=0) are removed since these are not relevant
        df_vakken = pd.read_excel(self.workspace.input.folderpath / "input.xlsx", sheet_name="Vakken").rename(columns=lambda x: x.strip())
        df_uittredepunten = pd.read_excel(self.workspace.input.folderpath / "input.xlsx", sheet_name="Uittredepunten").rename(columns=lambda x: x.strip())
        df_ondergrond_scenarios = pd.read_excel(self.workspace.input.folderpath / "input.xlsx", sheet_name="Ondergrondscenarios").rename(columns=lambda x: x.strip()).dropna(subset=['ondergrondscenario_kans']).loc[lambda x: x['ondergrondscenario_kans'] != 0]
        checks_input_parameters(self.df_overview_parameters, df_vakken, df_uittredepunten, df_ondergrond_scenarios)
        print("INFO: parameter data successfully loaded from 'input.xlsx'")
        
        # Initialize collections. Note that UittredepuntCollection and OndergrondscenarioCollection link the
        # instances of Uittredepunt and OndergrondScenario to the corresponding Vak instance
        self.vak_collection = VakCollection(df_vakken, self.df_overview_parameters)
        self.uittredepunt_collection = UittredepuntCollection(df_uittredepunten, self.vak_collection, self.df_overview_parameters)
        self.ondergrond_scenario_collection = OndergrondScenarioCollection(df_ondergrond_scenarios, self.vak_collection, self.df_overview_parameters)        

        # FIXME CONSTANTEN MOETEN NOG INGELEZEN WORDEN!

        # Read calculation settings from Excel file
        self.df_settings = pd.read_excel(self.workspace.input.folderpath / "input.xlsx", sheet_name="Settings", index_col=0, header=0)
        print("INFO: settings successfully loaded from input.xlsx")
        print(f"INFO: full list of available settings:\n{Settings().__dir__()}")

        # Make combinations of uittredepunten, ondergrondscenarios and models
        # Notes:
        #   1. Not all combinations of uittredepunten and ondergrondscenarios are valid, so we need a helper loop through the vakken which holds the valid combinations
        #   2. Nested for-loops are inefficient but used on purpose since there are no heavy calculations and it's easily understandable
        self._list_reliability_calculations = []
        for vak in self.vak_collection.values():
            for uittredepunt in vak.uittredepunten:
                for ondergrond_scenario in vak.ondergrond_scenarios:
                    for model in [calc_Z_u, calc_Z_h, calc_Z_p]:
                        self._list_reliability_calculations.append(ReliabilityCalculation(uittredepunt, ondergrond_scenario, model, self.df_settings))
        
        # # Start calculations
        # self._start_calculations(self._list_reliability_calculations)
    
    
    # FIXME parallelize these calculations
    def _start_calculations(self, list_reliability_calculations: list[ReliabilityCalculation]):
        
        def run_reliability_calculation(reliability_calculation: ReliabilityCalculation):
            try:
                reliability_calculation._run()
            except Exception as e:
                print(f"ERROR: could not run running reliability calculation {reliability_calculation.name}: {e}")

        with ThreadPoolExecutor() as executor:
            executor.map(run_reliability_calculation, list_reliability_calculations)