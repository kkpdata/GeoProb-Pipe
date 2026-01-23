from geoprob_pipe.calculations.system_calculations.piping_wbi.limit_state_functions import (
    system_variable_setup, calc_Z_h, calc_Z_p, calc_Z_u)
from geoprob_pipe.calculations.system_calculations.system_base_objects.parallel_system_reliability_calculation import (
    ParallelSystemReliabilityCalculation)
from typing import List, Dict, Union, Tuple


class PipingWBISystemReliabilityCalculation(ParallelSystemReliabilityCalculation):
    """ Vooraf gedefinieerde System Reliability Calculation voor piping met het WBI-stijghoogtemodel. """

    def __init__(
            self,
            system_variable_distributions: List[Dict],
            system_variable_correlations: List[Tuple[str, str, float]] = None,
            project_settings: Dict[str, Union[str, float, int]] = None
    ):

        super().__init__(
            system_variable_distributions=system_variable_distributions, project_settings=project_settings,
            system_variable_correlations=system_variable_correlations
        )
        self.given_system_variables_setup_function = system_variable_setup
        self.given_system_models = [calc_Z_u, calc_Z_h, calc_Z_p]
