import inspect
from collections.abc import Iterable
from typing import Any, Callable

import pandas as pd
from misc._default_values_constants import ALLOWED_DISPERSION_TYPES
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
from probabilistic_library.project import ZModel
from probabilistic_library.reliability import Settings

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
        
        # Setup ReliabilityProject
        self.reliability_project = ReliabilityProject()
        
        # Model & Variables
        # First the model (Z-function that will be run) must be set, since probabilistic_library defines the variables of a ReliabilityProject
        # based on the input args of the model function. Other args (i.e. variables from the input Excel) are not allowed, so we need to know which
        # input args the current model requires so we can add the relevant variables.
        self.reliability_project.model = self._model

        self._setup_variables(self._uittredepunt, self._ondergrond_scenario)
        
        # Constants
        # self._setup_constants()  # FIXME constants should be added
        
        # Calculation settings
        self._setup_settings(df_settings)
        
    
    def _setup_settings(self, df_settings: pd.DataFrame) -> None:

        # Setup the settings of the ReliabilityProject
        # Note: all supported settings can be found in probabilistic_library.reliability.Settings.__dir__
        for attr_name, row in df_settings.iterrows():
            if attr_name in Settings().__dir__():
                setattr(self.reliability_project.settings, attr_name, row['value'])
            else:
                raise ValueError(f"Attribute '{attr_name}' not found in SensitivitySettings class. Available attributes:\n{Settings().__dir__()}")


    def _setup_variables(self, uittredepunt: Uittredepunt, ondergrond_scenario: OndergrondScenario) -> None:
        # Setup the different variables of the ReliabilityProject
        # Note: all supported variable attributes can be found in probabilistic_library.statistic.Stochast.__dir__
        
        # Vak variables
        for var_name, var_dict in uittredepunt.vak.variables.__dict__.items():
            if var_name in inspect.signature(self._model).parameters:
                self._set_reliability_project_variable(var_name, var_dict)

        # Uittredepunt variables
        for var_name, var_dict in uittredepunt.variables.__dict__.items():
            if var_name in inspect.signature(self._model).parameters:
                self._set_reliability_project_variable(var_name, var_dict)
            
        # Ondergrondscenario variables
        for var_name, var_dict in ondergrond_scenario.variables.__dict__.items():
            if var_name in inspect.signature(self._model).parameters:
                self._set_reliability_project_variable(var_name, var_dict)
        

    def _setup_constants(self):
        raise NotImplementedError


    def _run(self):
        # Run the reliability project
        self.reliability_project.run()
    

    def _set_reliability_project_variable(self, var_name: str, var_dict: dict[str, Any]) -> None:
        self.reliability_project.variables[var_name].distribution = var_dict["distribution"]
        
        if var_dict["distribution"] == "deterministic":
            self.reliability_project.variables[var_name].mean = var_dict["value"]
        else:
            self.reliability_project.variables[var_name].mean = var_dict["mean"]
            
            if var_dict["dispersion_type"] == "_stdev":
                self.reliability_project.variables[var_name].deviation = var_dict["dispersion_value"]
            elif var_dict["dispersion_type"] == "_stdev":
                self.reliability_project.variables[var_name].variation = var_dict["dispersion_value"]
            else:
                raise ValueError(f"Disperion type '{var_dict["dispersion_type"]}' of variable '{var_name}' is not implemented. Allowed types: {ALLOWED_DISPERSION_TYPES}")
    
        if pd.notna(var_dict["lower_bound_mean"]):
            self.reliability_project.variables[var_name].minimum = var_dict["lower_bound_mean"]
            self.reliability_project.variables[var_name].maximum = var_dict["upper_bound_mean"]

    
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

