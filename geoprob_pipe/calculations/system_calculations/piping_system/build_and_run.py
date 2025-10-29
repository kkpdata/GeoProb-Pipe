from __future__ import annotations
from geoprob_pipe.calculations.system_calculations.piping_system.reliability_calculation import \
    PipingSystemReliabilityCalculation
from geoprob_pipe.calculations.system_calculations.piping_system.system_builder import PipingSystemBuilder
from typing import List, TYPE_CHECKING
from multiprocessing import Pool, cpu_count
from itertools import product
# noinspection PyPep8Naming
from geoprob_pipe.utils.loggers import TmpAppConsoleHandler as logger
if TYPE_CHECKING:
    from geoprob_pipe import GeoProbPipe


def _worker(build_input):
    """
    Worker function for the parallel processing executor.
    Here a single PipingSystemReliabilityCalculation instance is set up
    and run. After running the results are split off, converted to a
    dict and returned to the main process.
    """

    # Split the parameter from the input
    # (Only one argument can be send to the worker)
    vak, uittredepunt, ondergrond_scenario, df_settings, df_constants = build_input
    system_builder = PipingSystemBuilder()

    # Build the single calculation
    calc: PipingSystemReliabilityCalculation = system_builder.build_single_instance(
        vak=vak,
        uittredepunt=uittredepunt,
        ondergrond_scenario=ondergrond_scenario,
        df_settings=df_settings,
        df_constants=df_constants
        )
    calc.run()
    # Convert the results to a dict for pickeling
    result = calc.export_result()

    return result


def build_and_run_piping_system_calculations(
        geoprob_pipe: GeoProbPipe
        ) -> List[PipingSystemReliabilityCalculation]:
    logger.info("Now building and running calculations...")

    df_settings = geoprob_pipe.df_settings
    df = geoprob_pipe.input_data.df_overview_parameters
    df_constants = df[df["parameter_type"] == "constant"]

    system_builder = PipingSystemBuilder()

    # extract build parameters to setup single calculation instances
    build_inputs = []
    for vak in geoprob_pipe.input_data.vakken.values():
        uittredepunten = vak.uittredepunten
        ondergrond_scenarios = vak.ondergrond_scenarios
        for uittredepunt, ondergrond_scenario in product(uittredepunten,
                                                         ondergrond_scenarios):
            build_inputs.append((vak, uittredepunt, ondergrond_scenario,
                                 df_settings, df_constants))

    # Perform calculations
    with Pool(processes=min(len(build_inputs), cpu_count()-1)) as pool:
        results = pool.map(_worker, build_inputs)

    # Remake the calculation classes for further use in the code
    calculations = system_builder.build_instances(
        geoprob_pipe.input_data.vakken, df_settings, df_constants
        )

    # Add the results from the worker to the remade calculations
    for result, calculation in zip(results, calculations):
        calculation.import_results(result)
    return calculations
