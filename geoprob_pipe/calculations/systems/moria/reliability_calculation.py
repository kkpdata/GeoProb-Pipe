from geoprob_pipe.calculations.systems.moria.limit_state_functions import (
    system_variable_setup, calc_Z_h, calc_Z_p, calc_Z_u, calc_Z_project)
from geoprob_pipe.calculations.systems.base_objects.system_calculation import SystemCalculation
from typing import List, Dict, Union, Tuple


class MORIACalculation(SystemCalculation):
    """ Vooraf gedefinieerde System Reliability Calculation voor piping met het WBI-stijghoogtemodel. """

    def __init__(
            self,
            distributions: List[Dict],
            correlations: List[Tuple[str, str, float]] = None,
            reliability_settings: Dict[str, Union[str, float, int]] = None
    ):
        super().__init__(
            distributions=distributions, correlations=correlations, reliability_settings=reliability_settings)
        self.setup.variables_function = system_variable_setup
        self.setup.system_limit_states = [calc_Z_u, calc_Z_h, calc_Z_p]
        self.setup.project_limit_state = calc_Z_project
