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
from probabilistic_library.sensitivity import SensitivitySettings

from app.classes.ondergrond_scenario import OndergrondScenario
from app.classes.uittredepunt import Uittredepunt
from app.helper_functions.data_validation import is_number


class ReliabilityCalculation():
    """ReliabilityCalculation class containing calculation settings and results for 1 uittredepunt"""

    def __init__(self, uittredepunt: Uittredepunt, ondergrond_scenario: OndergrondScenario, model: Callable, df_settings: pd.DataFrame) -> None:
        
        self._id = {"uittredepunt": uittredepunt.id, "ondergrondscenario": ondergrond_scenario.id, "model": model.__name__}
        self._uittredepunt = uittredepunt
        self._ondergrond_scenario = ondergrond_scenario
        self._model = model
    
        self.reliability_project = self._setup_reliability_project(df_settings)

    
    def _setup_reliability_project(self, df_settings: pd.DataFrame) -> ReliabilityProject:
        reliability_project = ReliabilityProject()

        # Set settings attributes
        print(f"INFO: list of available settings:\n{dir(SensitivitySettings)}")
        for attr_name, row in df_settings.iterrows():
            if attr_name in dir(SensitivitySettings):
                setattr(reliability_project.settings, attr_name, row['value'])
            else:
                raise ValueError(f"Attribute {attr_name} not found in SensitivitySettings class. Available attributes:\n{dir(SensitivitySettings)}")

        # Set variable attributes
        
        # FIXME make sure that the attributes values are numbers using is_number()
        is_number(...)
        for attr_name, row in parameter_collection_single_uittredepunt.iterrows():
            setattr(reliability_project.settings, attr_name, row['value'])
        reliability_project.variables["k"].distribution = DistributionType.log_normal
        
        # project.variables["k"].mean = Uittredepunten_scenario.iloc[i]['k_WVP [m/dag]']
        # project.variables["k"].variation = Uittredepunten_scenario.iloc[i]['VC_k_WVP [-]']
        # project.variables["k"].design_quantile = 0.95
        # ...etc...
        
        return reliability_project

    def _run(self):
        # Run the reliability project
        self.reliability_project.run()
    
    def plot_fragility_curve(self):
        raise NotImplementedError()

    @property
    def id(self):
        return self._id
    
    @property
    def uittredepunt(self):
        return self._uittredepunt
    
    @property
    def ondergrond_scenario(self):
        return self._ondergrond_scenario
    
    @property
    def model(self):
        return self._model

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

