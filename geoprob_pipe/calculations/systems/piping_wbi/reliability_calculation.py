from geoprob_pipe.calculations.systems.piping_wbi.limit_state_functions import (
    system_variable_setup, calc_Z_h, calc_Z_p, calc_Z_u)
from geoprob_pipe.calculations.systems.base_objects.system_calculation import (
    SystemCalculation)
from typing import List, Dict, Union, Tuple


class PipingWBISystemReliabilityCalculation(SystemCalculation):
    """ Vooraf gedefinieerde System Reliability Calculation voor piping met het WBI-stijghoogtemodel. """

    def __init__(
            self,
            system_variable_distributions: List[Dict],
            system_variable_correlations: List[Tuple[str, str, float]] = None,
            project_settings: Dict[str, Union[str, float, int]] = None
    ):

        super().__init__(
            distributions=system_variable_distributions, project_settings=project_settings,
            correlations=system_variable_correlations
        )
        self.given_variables_setup_function = system_variable_setup
        self.given_limit_states = [calc_Z_u, calc_Z_h, calc_Z_p]
