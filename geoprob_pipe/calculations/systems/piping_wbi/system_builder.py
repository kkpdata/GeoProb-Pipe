from __future__ import annotations
from geoprob_pipe.calculations.systems.piping_wbi.reliability_calculation import \
    PipingWBISystemReliabilityCalculation
from geoprob_pipe.calculations.systems.base_objects.base_system_build import BaseSystemBuilder


class WBISystemBuilder(BaseSystemBuilder):

    def __init__(self,
                 geopackage_filepath: str,
                 to_run_vakken_ids: list[int]):
        super().__init__(geopackage_filepath=geopackage_filepath,
                         to_run_vakken_ids=to_run_vakken_ids)
        self.system_class = PipingWBISystemReliabilityCalculation
