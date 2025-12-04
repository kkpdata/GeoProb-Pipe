from __future__ import annotations
from geoprob_pipe.calculations.system_calculations.piping_wbi.reliability_calculation import \
    PipingWBISystemReliabilityCalculation
from geoprob_pipe.calculations.system_calculations.system_base_objects.base_system_build import BaseSystemBuilder
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from geoprob_pipe import GeoProbPipe


class WBISystemBuilder(BaseSystemBuilder):

    def __init__(self, geoprob_pipe: GeoProbPipe):
        super().__init__(geoprob_pipe=geoprob_pipe)
        self.system_class = PipingWBISystemReliabilityCalculation
