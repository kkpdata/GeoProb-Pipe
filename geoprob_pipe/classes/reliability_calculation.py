import inspect
from abc import ABC, abstractmethod
from types import SimpleNamespace
from typing import Any, Callable

import numpy as np
import pandas as pd
from geoprob_pipe.globals import ALLOWED_DISPERSION_TYPES
from pandas import DataFrame
from probabilistic_library import CombineProject, FragilityValue, ReliabilityProject
from probabilistic_library.reliability import Settings
from probabilistic_library.utils import FrozenList

from geoprob_pipe.classes.ondergrond_scenario import OndergrondScenario
from geoprob_pipe.classes.uittredepunt import Uittredepunt
from geoprob_pipe.helper_functions.data_validation import enforce_lower_upper_bounds
from geoprob_pipe.helper_functions.parameter_functions import (
    generate_parameter_dict_for_constant,
)


class ResultsTemplate(ABC):
    @property
    def settings(self) -> SimpleNamespace:
        """Return the settings of the reliability project as a SimpleNamespace object, which includes the settings DataFrame (simple overview) and the Settings object (actually used in ReliabilityProject)."""
        return SimpleNamespace(df=self.df_settings, obj=self.reliability_project.settings)


    @property
    def variables(self) -> FrozenList:
        return self.reliability_project.variables

    
    @property
    def design_point(self):
        return self.reliability_project.design_point
    
    
    @property
    def beta(self):
        return self.design_point.reliability_index


    @property
    def alphas(self):
        return {a.identifier: a.alpha for a in self.design_point.alphas.get_list()}


    @property
    def influence_factors(self):
        return {a.identifier: a.influence_factor for a in self.design_point.alphas.get_list()}


    @property
    def is_converged(self):
        return self.design_point.is_converged



class ReliabilityCalculation(ResultsTemplate):
    """ReliabilityCalculation class for calculations of either the uplift, heave or piping model for each unique uittredepunt-ondergrondscenario combination."""

    def __init__(self, uittredepunt: Uittredepunt, ondergrond_scenario: OndergrondScenario, model: Callable,
                 df_constants: pd.DataFrame, df_settings: pd.DataFrame) -> None:
        
        self.id = {"uittredepunt": uittredepunt.id, "ondergrondscenario": ondergrond_scenario.id, "model": model.__name__}
        self.uittredepunt = uittredepunt
        self.ondergrond_scenario = ondergrond_scenario
        self.model = model
        self.constants = df_constants
        self.df_settings = df_settings
        
        # Setup ReliabilityProject
        self.reliability_project = ReliabilityProject()
        
        # Calculation settings
        self._setup_settings(df_settings)
        
        # Model & Variables
        # First the model (Z-function that will be run) must be set, since the probabilistic_library defines the
        # variables of a ReliabilityProject based on the input args of the evaluated model function. Other args (i.e.
        # variables from the input Excel) are not allowed, so we need to know which input args the current model
        # requires so we can add the relevant variables.
        self.reliability_project.model = self.model

        # Buitenwaterstand (from Overschrijdingsfrequentielijn)
        # Special variable since it comes from Pydra (and not the input Excel file), so it is set separately        
        self._set_buitenwaterstand_overschrijdingsfrequentielijn(self.uittredepunt)
        list_assigned_parameters = ["buitenwaterstand"]  # Keep track of the parameters that were assigned to the ReliabilityProject	

        # Variables
        list_assigned_parameters += self._setup_variables(self.uittredepunt, self.ondergrond_scenario)
        
        # Constants
        list_assigned_parameters += self._setup_constants()
        
        # Make sure all variables and constants are set in the ReliabilityProject
        expected_parameters = [parameter.name for parameter in self.reliability_project.variables.get_list()]
        if set(list_assigned_parameters) != set(expected_parameters):
            raise ValueError(f"Not all input parameters expected by model '{self.model.__name__}' were set in the ReliabilityProject.\nExpected parameters: {expected_parameters}\nSet parameters: {list_assigned_variables+list_assigned_constants}\nMissing parameters: {set(expected_parameters) - set(list_assigned_variables + list_assigned_constants)}")
        

    def _setup_settings(self, df_settings: pd.DataFrame) -> None:

        # Setup the settings of the ReliabilityProject
        # Note: all supported settings can be found in probabilistic_library.reliability.Settings.__dir__
        for attr_name, row in df_settings.iterrows():
            if attr_name in Settings().__dir__():
                setattr(self.reliability_project.settings, attr_name, row['value'])
            else:
                raise ValueError(f"Attribute '{attr_name}' not found in SensitivitySettings class. Available attributes:\n{Settings().__dir__()}")


    def _setup_variables(self, uittredepunt: Uittredepunt, ondergrond_scenario: OndergrondScenario) -> list[str]:
        # Setup the different variables of the ReliabilityProject
        # Notes: before a variable is assigned it is checked whether it is a valid input parameter of the current model function.

        list_assigned_variables = []

        # FIXME code below can be optimized (repetitive tasks)
        # Vak variables
        for var_name, var_dict in uittredepunt.vak.variables.__dict__.items():
            if var_name in inspect.signature(self.model).parameters:
                enforce_lower_upper_bounds(var_dict, f"Vak ID {uittredepunt.vak.id}")
                self._set_reliability_project_variable(var_name, var_dict)
                list_assigned_variables.append(var_name)

        # Uittredepunt variables
        for var_name, var_dict in uittredepunt.variables.__dict__.items():
            if var_name in inspect.signature(self.model).parameters:
                enforce_lower_upper_bounds(var_dict, f"Uittredepunt ID {uittredepunt.id}")
                self._set_reliability_project_variable(var_name, var_dict)
                list_assigned_variables.append(var_name)
            
        # Ondergrondscenario variables
        for var_name, var_dict in ondergrond_scenario.variables.__dict__.items():
            if var_name in inspect.signature(self.model).parameters:
                enforce_lower_upper_bounds(var_dict, f"Ondergrondscenario ID {ondergrond_scenario.id}")
                self._set_reliability_project_variable(var_name, var_dict)
                list_assigned_variables.append(var_name)
        
        return list_assigned_variables

    def _setup_constants(self) -> list[str]:
        
        list_assigned_constants = []
        
        for var_name, row in self.constants.iterrows():
            if var_name in inspect.signature(self.model).parameters:
                constant_dict = generate_parameter_dict_for_constant(str(var_name), df_overview_row=row)
                enforce_lower_upper_bounds(constant_dict, "located parameter overview sheet")
                self._set_reliability_project_variable(str(var_name), var_dict=constant_dict)
            
                list_assigned_constants.append(str(var_name))
                
        return list_assigned_constants

    
    def _set_buitenwaterstand_overschrijdingsfrequentielijn(self, uittredepunt: Uittredepunt) -> None:
        # Add the overschrijdingsfrequentielijn as stochastic variable to the ReliabilityProject
        
        waterlevel = uittredepunt.overschrijdingsfrequentielijn.overschrijdingsfrequentielijn.level
        exceedance_frequency = uittredepunt.overschrijdingsfrequentielijn.overschrijdingsfrequentielijn.exceedance_frequency
        
        self.reliability_project.variables["buitenwaterstand"].distribution = "cdf_curve"

        for i in range(0, len(waterlevel)):
            fc = FragilityValue()
            fc.x = waterlevel[i]
            fc.probability_of_failure = exceedance_frequency[i]
            self.reliability_project.variables["buitenwaterstand"].fragility_values.append(fc)

        

    def _set_reliability_project_variable(self, var_name: str, var_dict: dict[str, Any]) -> None:
        # Create the Stochastic variable in the ReliabilityProject
        # Note: all supported variable attributes can be found in probabilistic_library.statistic.Stochast().__dir__()

        try:
            self.reliability_project.variables[var_name].distribution = var_dict["distribution"]
            
            if var_dict["distribution"] == "deterministic":
                self.reliability_project.variables[var_name].mean = var_dict["value"]
            else:
                self.reliability_project.variables[var_name].mean = var_dict["mean"]
                
                if var_dict["dispersion_type"] == "_stdev":
                    self.reliability_project.variables[var_name].deviation = var_dict["dispersion_value"]
                elif var_dict["dispersion_type"] == "_vc":
                    self.reliability_project.variables[var_name].variation = var_dict["dispersion_value"]
                else:
                    raise ValueError(f"Disperion type '{var_dict["dispersion_type"]}' of variable '{var_name}' is not implemented. Allowed types: {ALLOWED_DISPERSION_TYPES}")
        
            if pd.notna(var_dict["lower_bound_mean"]):
                self.reliability_project.variables[var_name].minimum = var_dict["lower_bound_mean"]
            if pd.notna(var_dict["upper_bound_mean"]):
                self.reliability_project.variables[var_name].maximum = var_dict["upper_bound_mean"]
        except AttributeError as e:
            raise AttributeError(f"Trying to set variable '{var_name}', which is not an input arg of function {self._model.__name__}. The probabilistic_library package only allows variables defined as input args of the evaluated model function.\nError message: {e}")
    
    
    def run(self):
        # Run the reliability project
        self.reliability_project.run()


class CombinedReliabilityCalculation(ResultsTemplate):
    """CombinedReliabilityCalculation class for combined calculations of the uplift/heave/piping models for each unique uittredepunt-ondergrondscenario combination."""

    def __init__(self, reliability_project: CombineProject, uittredepunt: Uittredepunt, ondergrond_scenario: OndergrondScenario) -> None:
        self.id = {"uittredepunt": uittredepunt.id, "ondergrondscenario": ondergrond_scenario.id}
        self.uittredepunt = uittredepunt
        self.ondergrond_scenario = ondergrond_scenario
        self.reliability_project = reliability_project

