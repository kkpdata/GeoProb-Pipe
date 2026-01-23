from __future__ import annotations
from geoprob_pipe.calculations.system_calculations.system_base_objects.base_system_build import BaseSystemBuilder
from geoprob_pipe.calculations.system_calculations.piping_system.reliability_calculation import (
    PipingSystemReliabilityCalculation)


class PipingSystemBuilder(BaseSystemBuilder):

    def __init__(self,
                 geopackage_filepath: str,
                 to_run_vakken_ids: list[int]):
        super().__init__(geopackage_filepath=geopackage_filepath,
                         to_run_vakken_ids=to_run_vakken_ids)
        self.system_class = PipingSystemReliabilityCalculation
