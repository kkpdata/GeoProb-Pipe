from typing import Callable

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


class ReliabilityCalculation():
    """ReliabilityCalculation class containing calculation settings and results for 1 uittredepunt"""

    def __init__(self, settings: pd.DataFrame, model=Callable):
        
        self.name = None
        self.uittredepunt = None
        self.scenario = None
    
        self.reliability_project = self._setup_reliability_project(settings, model)
    

    

    
    def _setup_reliability_project(self, settings: pd.DataFrame, model=Callable) -> ReliabilityProject:
        reliability_project = ReliabilityProject()

        # Set settings
        for attr_name, row in settings.iterrows():
            setattr(reliability_project.settings, attr_name, row['value'])

        # Set model (uplift, heave or piping)
        reliability_project.model = model
        
        # FIXME set variables, based on Oscar's code
        # Set variables
        # project.variables["k"].distribution = DistributionType.log_normal
        # project.variables["k"].mean = Uittredepunten_scenario.iloc[i]['k_WVP [m/dag]']
        # project.variables["k"].variation = Uittredepunten_scenario.iloc[i]['VC_k_WVP [-]']
        # project.variables["k"].design_quantile = 0.95
        # ...etc...
        return reliability_project

    
    def plot_fragility_curve(self):
        raise NotImplementedError()

    @property
    def settings(self):
        return self.reliability_project.settings

    @property
    def variables(self):
        return self.reliability_project.variables


    # FIXME add properties:
    # self.beta = None
    # self.failure_probability = None
    # self.waterlevels = None
    # self.influence_factors = None
    # self.alphas = None

class ReliabilityCalculationSet:
    """ReliabilityCalculationSet class containing multiple ReliabilityCalculation instances"""

    def __init__(self, list_scenario_calculations: list[ReliabilityCalculation]) -> None:
        self.calculations = list_scenario_calculations

