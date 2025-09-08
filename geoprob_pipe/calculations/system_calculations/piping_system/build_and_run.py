from __future__ import annotations
from geoprob_pipe.calculations.system_calculations.piping_system.reliability_calculation import \
    PipingSystemReliabilityCalculation
from geoprob_pipe.calculations.system_calculations.piping_system.system_builder import PipingSystemBuilder
from typing import List, TYPE_CHECKING
import traceback
import time
from concurrent.futures import ThreadPoolExecutor
# noinspection PyPep8Naming
from geoprob_pipe.utils.loggers import TmpAppConsoleHandler as logger
if TYPE_CHECKING:
    from geoprob_pipe import GeoProbPipe


def _run_calculation(calculation: PipingSystemReliabilityCalculation):
    try:
        calculation.run()
    except Exception as e:
        # error_msg = traceback.format_exc()
        uittredepunt_id = calculation.metadata['uittredepunt_id']
        ondergrondscenario_id = calculation.metadata['ondergrondscenario_id']
        vak_id = calculation.metadata['vak_id']
        print(f"Could not run reliability calculation: "
              f"{uittredepunt_id=}, {ondergrondscenario_id=}, {vak_id=}: "
              f"{e}, ")


def build_and_run_piping_system_calculations(self: GeoProbPipe) -> List[PipingSystemReliabilityCalculation]:
    system_builder = PipingSystemBuilder()
    df = self.input_data.df_overview_parameters
    df_constants = df[df["parameter_type"] == "constant"]

    # Build calculations
    logger.info("Now building calculations")
    calculations =  system_builder.build_instances(
        vak_collection=self.input_data.vakken,
        df_settings=self.df_settings,
        df_constants=df_constants)
    logger.info("Now finished building.")

    # Run calculations
    logger.info("Starting running calculations.")
    with ThreadPoolExecutor(max_workers=24) as executor:
        executor.map(_run_calculation, calculations)
    # for calc in calculations:
    #     calc.run()
    logger.info("Now finished running.")
    # TODO Nu Could Middel: Uitvoeren van system calculations ombouwen naar Threads.
    #  Niet direct prio omdat het eigenlijk allemaal al snel doorgerekend wordt.

    return calculations
