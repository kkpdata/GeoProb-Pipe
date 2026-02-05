from __future__ import annotations
from geoprob_pipe.calculations.systems.base_objects.base_system_build import BaseSystemBuilder
from geoprob_pipe.calculations.systems.model4a.reliability_calculation import (
    Model4aCalculation)


class Model4aSystemBuilder(BaseSystemBuilder):

    def __init__(self,
                 geopackage_filepath: str,
                 to_run_vakken_ids: list[int]):
        super().__init__(geopackage_filepath=geopackage_filepath,
                         to_run_vakken_ids=to_run_vakken_ids)
        self.system_class = Model4aCalculation
