from probabilistic_library import DistributionType
from geoprob_pipe.calculations.limit_state_functions import (
    system_variable_setup, limit_state_example_1, limit_state_example_2)
from geoprob_pipe.calculations.system_calculations._parallel_system_reliability_calculation import (
    ParallelSystemReliabilityCalculation)
from typing import List, Dict


class PipingSystemReliabilityCalculation(ParallelSystemReliabilityCalculation):
    """ Pre-defined system reliability calculation for Piping.

    Usage by calling the object, inserting the variable distributions and after that calling the run-method. The
    separate limit state models (uplift, heave and piping) are already pre-defined in the class.

    >>> obj = PipingSystemReliabilityCalculation(
    ...     system_variable_distributions=[
    ...         {
    ...             "name": "a",
    ...             "distribution_type": DistributionType.uniform,
    ...             "minimum": -1,
    ...             "maximum": 1,
    ...         },
    ...         ...
    ...     ],
    ... )
    >>> obj.run()
    """

    def __init__(self, system_variable_distributions: List[Dict]):
        super().__init__(system_variable_distributions)
        self.system_variables_setup_function = system_variable_setup
        self.system_models = [limit_state_example_1, limit_state_example_2]
