from geoprob_pipe.calculations.system_calculations.piping_system.limit_state_functions import (
    limit_state_model4a, calc_Z_h, calc_Z_p, calc_Z_u)
from geoprob_pipe.calculations.system_calculations.system_base_objects.parallel_system_reliability_calculation import (
    ParallelSystemReliabilityCalculation)
from typing import List, Dict, Union


class PipingSystemReliabilityCalculation(ParallelSystemReliabilityCalculation):
    """ Pre-defined system reliability calculation for Piping.

    Usage by calling the object, inserting the variable distributions and after that calling the run-method. The
    separate limit state models (uplift, heave and piping) are already pre-defined in the class. """

    def __init__(
            self,
            system_variable_distributions: List[Dict],
            project_settings: Dict[str, Union[str, float, int]] = None
    ):
        # Mutable arguments
        if project_settings is None:
            project_settings = {}

        super().__init__(system_variable_distributions=system_variable_distributions, project_settings=project_settings)
        self.given_system_variables_setup_function = limit_state_model4a
        self.given_system_models = [calc_Z_u, calc_Z_h, calc_Z_p]
