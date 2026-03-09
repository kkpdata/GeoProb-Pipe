from geoprob_pipe.calculations.systems.model4a.limit_state_functions import (
    limit_state_model4a, calc_Z_h, calc_Z_p, calc_Z_u, calc_Z_project)
from geoprob_pipe.calculations.systems.base_objects.system_calculation import SystemCalculation
from typing import List, Dict, Union, Tuple


class Model4aCalculation(SystemCalculation):
    """ Pre-defined system reliability calculation for Piping.

    Usage by calling the object, inserting the variable distributions and
    after that calling the run-method. The separate limit state models
    (uplift, heave and piping) are already pre-defined in the class.
    """

    def __init__(
            self,
            distributions: List[Dict],
            correlations: List[Tuple[str, str, float]] = None,
            reliability_settings: Dict[str, Union[str, float, int]] = None
    ):

        super().__init__(
            distributions=distributions,
            correlations=correlations,
            reliability_settings=reliability_settings)
        self.setup.variables_function = limit_state_model4a
        self.setup.system_limit_states = [calc_Z_u, calc_Z_h, calc_Z_p]
        self.setup.project_limit_state = calc_Z_project
