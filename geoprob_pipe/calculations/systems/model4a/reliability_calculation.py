from geoprob_pipe.calculations.systems.model4a.limit_state_functions import (
    limit_state_model4a, calc_Z_h, calc_Z_p, calc_Z_u)
from geoprob_pipe.calculations.systems.base_objects.system_calculation import (
    SystemCalculation)
from typing import List, Dict, Union, Tuple


class Model4aCalculation(SystemCalculation):
    """ Pre-defined system reliability calculation for Piping.

    Usage by calling the object, inserting the variable distributions and
    after that calling the run-method. The separate limit state models
    (uplift, heave and piping) are already pre-defined in the class.
    """

    def __init__(
            self,
            system_variable_distributions: List[Dict],
            system_variable_correlations: List[Tuple[str, str, float]] = None,
            project_settings: Dict[str, Union[str, float, int]] = None
    ):

        super().__init__(
            distributions=system_variable_distributions,
            project_settings=project_settings,
            correlations=system_variable_correlations)
        self.given_variables_setup_function = limit_state_model4a
        self.given_ls_separate = [calc_Z_u, calc_Z_h, calc_Z_p]
