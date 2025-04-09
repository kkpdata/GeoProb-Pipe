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
        list_scenario_calculations = []
        self.settings = pd.read_excel(self.workspace.input.folderpath / "settings.xlsx", index_col=0, header=0)
        for model in [calc_Z_u, calc_Z_h, calc_Z_p]:
            list_scenario_calculations.append(ReliabilityCalculation(self.settings, model))
        
        # FIXME pseudocode, wachten op acties Oscar
        list_scenario_calculations = []
        for scenario in self.parameter_collection:
            for model in [calc_Z_u, calc_Z_h, calc_Z_p]:
                list_scenario_calculations.append(ReliabilityCalculation(self.settings, model, uittredepunt, scenario, vak))
        self.scenario_calculations = list_scenario_calculations
        
        # Start calculations
        # FIXME parallelize these calculations
        for scenario_calculation in self.scenario_calculations:
            self._start_calculations(scenario_calculation.reliability_project)
    
        
    # FIXME parallelize these calculations
    def _start_calculations(self, reliability_project: ReliabilityProject):
        reliability_project.run()