from geoprob_pipe.calculations.system_calculations.system_base_objects.parallel_system_reliability_calculation import (
    ParallelSystemReliabilityCalculation)
from abc import ABC, abstractmethod
from typing import List, Dict, Union


class BaseSystemBuilder(ABC):

    def __init__(self):
        self.system_class = ParallelSystemReliabilityCalculation

    @abstractmethod
    def build_instances(self, **kwargs) -> List[ParallelSystemReliabilityCalculation]:
        """ This method needs to be replaced with the logic to build all
        ParallelSystemReliabilityCalculation-instances. You are obligated to use the methods
        'construct_system_variable_distributions' and 'construct_project_settings' to construct these instances.
         """
        pass

    @abstractmethod
    def construct_system_variable_distributions(self, **kwargs) -> List[Dict[str, Union[str, float, int]]]: pass

    @abstractmethod
    def construct_project_settings(self, **kwargs) -> Dict[str, Union[str, float, int]]: pass

