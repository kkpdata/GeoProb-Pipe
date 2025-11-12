from __future__ import annotations
from typing import TYPE_CHECKING, List
from geoprob_pipe.calculations.system_calculations.system_calculation_mapper import SYSTEM_CALCULATION_MAPPER

if TYPE_CHECKING:
    from geoprob_pipe import GeoProbPipe
    from geoprob_pipe.calculations.system_calculations.system_base_objects.base_system_build import BaseSystemBuilder
    from geoprob_pipe.calculations.system_calculations.system_base_objects.parallel_system_reliability_calculation import \
        ParallelSystemReliabilityCalculation


def build_and_run_system_calculations(geoprob_pipe: GeoProbPipe) -> List[ParallelSystemReliabilityCalculation]:

    # Determine geohydrologisch model
    geohydrologisch_model = geoprob_pipe.input_data.geohydrologisch_model
    system_builder: BaseSystemBuilder = SYSTEM_CALCULATION_MAPPER[geohydrologisch_model]['system_builder'](
        geoprob_pipe=geoprob_pipe)

    print("", f"Now building calculations...")
    calculations = system_builder.build_instances()

    print("", f"Now running calculations...")
    for calc in calculations:
        calc.run()

    return calculations
