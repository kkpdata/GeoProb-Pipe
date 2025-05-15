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

from app.classes.ondergrond_scenario import OndergrondScenarioCollection
from app.classes.reliability_calculation import ReliabilityCalculation
from app.classes.uittredepunt import UittredepuntCollection
from app.classes.vak import VakCollection
from app.classes.workspace import Workspace
from app.helper_functions.data_validation import (
    check_completeness_input_variables,
    check_variable_overview,
)
from app.helper_functions.piping_functions import calc_Z_h, calc_Z_p, calc_Z_u


class Project():
    """Project class"""
    def __init__(self, PATH_WORKSPACE: str|Path) -> None:
        
        # Initialize Workspace object (also checks if input/output folders contain all necessary files)
        self.workspace = Workspace(PATH_WORKSPACE)

        # Read overview of variables from Excel file (includes e.g. upper and lower bounds, type of distribution, etc.)
        self.df_variable_overview = pd.read_excel(self.workspace.input.folderpath / "input.xlsx", sheet_name="Overzicht_variabelen", index_col=0, header=0).rename(columns=lambda x: x.strip())
        check_variable_overview(self.df_variable_overview)
        print("\nOverzicht_variabelen successfully loaded from input.xlsx")
        
        # Initialize collections. Note that UittredepuntCollection and OndergrondscenarioCollection link the
        # instances of Uittredepunt and OndergrondScenario to the corresponding Vak instance
        self.vak_collection = VakCollection(self.workspace.input.folderpath / "input.xlsx", self.df_variable_overview)
        self.uittredepunt_collection = UittredepuntCollection(self.workspace.input.folderpath / "input.xlsx", self.vak_collection, self.df_variable_overview)
        self.ondergrond_scenario_collection = OndergrondScenarioCollection(self.workspace.input.folderpath / "input.xlsx", self.vak_collection, self.df_variable_overview)        
        # check_completeness_input_variables(self.df_variable_overview, self.vak_collection.df, self.uittredepunt_collection.df, self.ondergrond_scenario_collection.df)
        # print("\nVakken, Uittredepunten & Ondergrondscenarios successfully loaded from input.xlsx")

        # # Read calculation settings from Excel file
        # self.settings = pd.read_excel(self.workspace.input.folderpath / "input.xlsx", sheet_name="Settings", index_col=0, header=0)
        # print("\nSettings successfully loaded from input.xlsx")

        # # Make combinations of uittredepunten, ondergrondscenarios and models
        # # Notes:
        # #   1. Not all combinations of uittredepunten and ondergrondscenarios are valid, so we need a helper loop through the vakken which holds the valid combinations
        # #   2. Nested for-loops are inefficient but used on purpose since there are no heavy calculations and it's easily understandable
        # self._list_reliability_calculations = []
        # for vak in self.vak_collection.values():
        #     for uittredepunt in vak.uittredepunten:
        #         for ondergrond_scenario in vak.ondergrond_scenarios:
        #             for model in [calc_Z_u, calc_Z_h, calc_Z_p]:
        #                 self._list_reliability_calculations.append(ReliabilityCalculation(uittredepunt, ondergrond_scenario, model, self.settings))
        
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