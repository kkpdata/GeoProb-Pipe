from __future__ import annotations
from geoprob_pipe.calculations.system_calculations.piping_wbi.reliability_calculation import \
    PipingWBISystemReliabilityCalculation
from geoprob_pipe.calculations.system_calculations.system_base_objects.base_system_build import BaseSystemBuilder
# from typing import TYPE_CHECKING
# if TYPE_CHECKING:
#     from geoprob_pipe import GeoProbPipe


class WBISystemBuilder(BaseSystemBuilder):

    def __init__(self,
                 geopackage_filepath: str,
                 to_run_vakken_ids: list[int]):
        super().__init__(geopackage_filepath=geopackage_filepath,
                         to_run_vakken_ids=to_run_vakken_ids)
        self.system_class = PipingWBISystemReliabilityCalculation
