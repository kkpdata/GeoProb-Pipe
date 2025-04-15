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

from app.classes.reliability_calculation import ReliabilityCalculation
from app.classes.workspace import Workspace
from app.helper_functions.piping_functions import calc_Z_h, calc_Z_p, calc_Z_u


class Project():
    """Project class"""
    def __init__(self, PATH_WORKSPACE: str|Path) -> None:
        
        # Initialize Workspace object
        self.workspace = Workspace(PATH_WORKSPACE)

        #FIXME <--------------> Start stukje Oscar
        
        # Initialize parameters_collection object #FIXME
        # self.parameter_collection = ParameterCollection(self.workspace.input.folderpath)
        
        # TODO waar moet buitewaterstand komen?
        
        # Initialize uittredepunt, scenario and vak using data in parameters_collection
        # self.uittredepunten = ...self.parameter_collection...
        # self.scenario = ...self.parameter_collection...
        # self.vakken = ...self.parameter_collection...
                
        # # TODO add samengestelde (afgeleide) parameters (zoals kwelweglengte) 
        # self.uittredepunten.calculate_afgeleide_params()
        # self.scenario.calculate_afgeleide_params()
        # self.vakken.calculate_afgeleide_params()        
        #FIXME <--------------> Einde stukje Oscar

        
        # FIXME
        list_reliability_calculations = []
        self.settings = pd.read_excel(self.workspace.input.folderpath / "settings.xlsx", index_col=0, header=0)
        
        for uittredepunt in self.uittredepunten:
            for ondergrond_scenario in df_ondergrondscenario[row_name == uittredepunt.vak]:
                for model in [calc_Z_u, calc_Z_h, calc_Z_p]:
                    list_reliability_calculations.append(ReliabilityCalculation(self.settings, model, self.uittredepunt, self.ondergrond_scenarios))
        
        # Start calculations
        self._start_calculations(list_reliability_calculations)
    
        
    # FIXME parallelize these calculations
    def _start_calculations(self, list_reliability_calculations: list[ReliabilityCalculation]):
        
        def run_reliability_calculation(reliability_calculation: ReliabilityCalculation):
            try:
                reliability_calculation._run()
            except Exception as e:
                print(f"ERROR: could not run running reliability calculation {reliability_calculation.name}: {e}")

        with ThreadPoolExecutor() as executor:
            executor.map(run_reliability_calculation, list_reliability_calculations)