from pathlib import Path

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

from app.classes.parameter_collection import ParameterCollection
from app.classes.workspace import Workspace
from app.classes.reliability_calculation import ReliabilityCalculation

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
        self.uittredepunten = ...self.parameter_collection...
        self.scenario = ...self.parameter_collection...
        self.vakken = ...self.parameter_collection...
                
        # TODO add samengestelde (afgeleide) parameters (zoals kwelweglengte) 
        self.uittredepunten.calculate_afgeleide_params()
        self.scenario.calculate_afgeleide_params()
        self.vakken.calculate_afgeleide_params()        
        #FIXME <--------------> Einde stukje Oscar

        
        # Generate ReliabilityCalculation instances (combinations of uittredepunten, scenarios and vakken)
        #FIXME
        # FIXME bedenk andere naam voor ReliabilityCalculation, dubbeling met subsoil_scenario voorkomen 
        list_scenario_calculations = []
        for scenario in self.parameter_collection:
            for model in Zu, Zh, Zp:  # Uplift, Heave, Piping
                list_scenario_calculations.append(ReliabilityCalculation(uittredepunt, scenario, vak, model))
        self.scenario_calculations = list_scenario_calculations
        
        # Start calculations
        # FIXME parallelize these calculations
        for scenario_calculation in self.scenario_calculations:
            self._start_calculations(scenario_calculation.reliability_project)
    
        
    # FIXME parallelize these calculations
    def _start_calculations(self, reliability_project: ReliabilityProject):
        reliability_project.run()