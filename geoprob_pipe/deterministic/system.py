from typing import Union, Dict, Callable, List, Optional
from geoprob_pipe.calculations.system_calculations.system_base_objects.parallel_system_reliability_calculation import (
    ParallelSystemReliabilityCalculation)
from probabilistic_library import DistributionType
import inspect


class DeterministicSystemCalculation:

    def __init__(self, input_object: Union[ParallelSystemReliabilityCalculation]):
        self.input_object = input_object
        self.limit_state_results = {}
        self.system_variable_setup_result: Optional[List[float]] = None
        self._calculate_limit_states()

    def _collect_deterministic_input(self, func: Callable) -> Dict[str, float]:
        """ For now this function collects the mean values. """
        deterministic_input = {}

        # Input argument names
        signature = inspect.signature(func)
        input_argument_names = signature.parameters.keys()

        # Collect deterministic input
        for distribution in self.input_object.given_system_variable_distributions:
            if distribution['name'] not in input_argument_names:
                continue

            if distribution['distribution_type'] in [
                DistributionType.deterministic, DistributionType.normal, DistributionType.log_normal]:
                deterministic_input[distribution['name']] = distribution['mean']
            else:
                raise NotImplementedError(
                    f"DeterministicSystemCalculation does not yet anticipate a distribution type "
                    f"'{DistributionType.uniform}'. Contact the developer.")

        return deterministic_input

    def _calculate_limit_states(self):
        """ For now this method only considers ParallelSystemReliabilityCalculation, in future with other systems
        or types it should anticipate those as well. """

        # Limit state functions
        for func in self.input_object.given_system_models:
            deterministic_input = self._collect_deterministic_input(func)
            self.limit_state_results[func.__name__] = func(**deterministic_input)

        # System variable setup function (may not be provided as a Z-function)
        deterministic_input = self._collect_deterministic_input(self.input_object.given_system_variables_setup_function)
        self.system_variable_setup_result = self.input_object.given_system_variables_setup_function(
            **deterministic_input)
        print(f"{deterministic_input=}")
