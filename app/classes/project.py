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
from app.classes.scenario_calculation import ScenarioCalculation

class Project():
    """Project class"""
    def __init__(self, PATH_WORKSPACE: str|Path) -> None:
        
        # Initialize Workspace object
        self.workspace = Workspace(PATH_WORKSPACE)
        
        # Initialize parameters_collection object
        # self.parameter_collection = ParameterCollection(self.workspace.input.folderpath)
        
        # Initialize uittredepunt, scenario and vak using data in parameters_collection
        self.uittredepunten = ...self.parameter_collection...
        self.scenario = ...self.parameter_collection...
        self.vakken = ...self.parameter_collection...
        
        # Generate ScenarioCalculation instances (combinations of uittredepunten, scenarios and vakken)
        list_scenario_calculations = []
        for scenario in self.parameter_collection:
            list_scenario_calculations.append(ScenarioCalculation(uittredepunt, scenario, vak))
        self.scenario_calculations = list_scenario_calculations
        
        # Start calculations
        # FIXME parallelize these calculations
        for scenario_calculation in self.scenario_calculations:
            self._start_calculations(scenario_calculation.reliability_project)
    
        
    # FIXME parallelize these calculations
    def _start_calculations(self, reliability_project: ReliabilityProject):
        reliability_project.run()